from typing import TypedDict, Any, Tuple, List, Optional
from logging import Logger, getLogger, DEBUG, StreamHandler
from queue import Queue
import grpc
import google.protobuf.text_format

from p4.config.v1 import p4info_pb2
from p4.v1 import p4runtime_pb2, p4runtime_pb2_grpc


class Action(TypedDict, total=False):
    action_id: int
    params: List[Tuple[int, bytes]]  # list of (param_id, value)


class FieldMatch(TypedDict, total=False):
    # ref: https://github.com/p4lang/p4runtime/blob/main/proto/p4/v1/p4runtime.proto#L229
    field_id: int
    match_type: p4runtime_pb2.FieldMatch.Exact | p4runtime_pb2.FieldMatch.Ternary | p4runtime_pb2.FieldMatch.LPM | p4runtime_pb2.FieldMatch.Range | p4runtime_pb2.FieldMatch.Optional | Any
    value: bytes  # Exact/Ternary/LPM/Optional
    mask: bytes  # Ternary
    prefix_len: int  # LPM
    low: bytes  # Range
    high: bytes  # Range


class TableEntry(TypedDict, total=False):
    update_type: int
    table_id: int
    match: List[FieldMatch]
    is_default_action: bool
    action: Action
    priority: int


def build_table_entry(entry: TableEntry):
    table_entry = p4runtime_pb2.TableEntry()
    table_entry.table_id = entry["table_id"]
    table_entry.is_default_action = entry.get("is_default_action", False)
    table_entry.priority = entry.get("priority", 0)

    action = table_entry.action.action
    action.action_id = entry["action"]["action_id"]
    for action_param in entry["action"].get("params", []):
        param = action.params.add()
        param.param_id = action_param[0]
        param.value = action_param[1]

    for m in entry.get("match", []):
        match_type = m["match_type"]
        field_match = table_entry.match.add()
        field_match.field_id = m["field_id"]
        if match_type == p4runtime_pb2.FieldMatch.Exact:
            field_match.exact.value = m["value"]
        elif match_type == p4runtime_pb2.FieldMatch.Ternary:
            field_match.ternary.value = m["value"]
            field_match.ternary.mask = m["mask"]
        elif match_type == p4runtime_pb2.FieldMatch.LPM:
            field_match.lpm.value = m["value"]
            field_match.lpm.prefix_len = m["prefix_len"]
        elif match_type == p4runtime_pb2.FieldMatch.Range:
            field_match.range.low = m["low"]
            field_match.range.high = m["high"]
        elif match_type == p4runtime_pb2.FieldMatch.Optional:
            field_match.optional.value = m["value"]
        else:
            raise Exception("%s is unknown match type." % str(match_type))

    return table_entry


class P4RuntimeClient:

    def __init__(self, ip: str, port: str, device_id: int, p4info_txt: str, p4device_json: str, election_id_high: int,
                 election_id_low: int, logger: Logger = None):
        self.ip = ip
        self.port = port
        self.device_id = device_id

        self.p4info = p4info_pb2.P4Info()
        with open(p4info_txt, "r") as f:
            google.protobuf.text_format.Merge(f.read(), self.p4info)
        with open(p4device_json, "rb") as f:
            self.device_config = f.read()

        # Election ID (上位64ビット)
        self.election_id_high = election_id_high
        # Election ID (下位64ビット)
        self.election_id_low = election_id_low

        self.logger = logger

        self.channel = None
        self.stub = None

        self.stream_replies = None
        self.req_queue = Queue()

    def establish_stream_channel(self):
        self.channel = grpc.insecure_channel(self.ip + ":" + self.port)
        self.stub = p4runtime_pb2_grpc.P4RuntimeStub(self.channel)

        self.stream_replies = self.stub.StreamChannel(iter(self.req_queue.get, None))

    def close_stream_channel(self):
        self.stream_replies.cancel()

    def master_arbitration_update(self):
        req = p4runtime_pb2.StreamMessageRequest()
        req.arbitration.device_id = self.device_id
        req.arbitration.election_id.high = self.election_id_high
        req.arbitration.election_id.low = self.election_id_low

        self.logger.debug("MasterArbitrationUpdate[Request]: %s" % str(req))
        self.req_queue.put(req)
        for rep in self.stream_replies:
            self.logger.debug("MasterArbitrationUpdate[Reply]: %s" % str(rep))
            return rep

    def set_pipeline_config_forward(self):
        req = p4runtime_pb2.SetForwardingPipelineConfigRequest()
        req.election_id.high = self.election_id_high
        req.election_id.low = self.election_id_low
        req.device_id = self.device_id

        req.config.p4info.CopyFrom(self.p4info)
        req.config.p4_device_config = self.device_config
        req.config.cookie.cookie = 1
        req.action = p4runtime_pb2.SetForwardingPipelineConfigRequest.VERIFY_AND_COMMIT
        self.logger.debug("SetPipelineConfigForward[Request]: %s" % str(req))
        rep = self.stub.SetForwardingPipelineConfig(req)
        self.logger.debug("SetPipelineConfigForward[Reply]: %s" % str(rep))
        return rep

    def get_pipeline_config_forward(self):
        req = p4runtime_pb2.GetForwardingPipelineConfigRequest()
        req.device_id = self.device_id
        self.logger.debug("GetPipelineConfigForward[Request]: %s" % str(req))
        rep = self.stub.GetForwardingPipelineConfig(req)
        self.logger.debug("GetPipelineConfigForward[Reply]: %s" % str(rep))
        return rep

    def write_table_entries(self, table_entries: List[TableEntry]):
        req = p4runtime_pb2.WriteRequest()
        req.device_id = self.device_id
        req.election_id.high = self.election_id_high
        req.election_id.low = self.election_id_low
        for entry in table_entries:
            update = req.updates.add()
            update.type = entry.get("update_type", p4runtime_pb2.Update.INSERT)
            table_entry = build_table_entry(entry)
            update.entity.table_entry.CopyFrom(table_entry)
        self.logger.debug("WriteTableEntries [Request]: %s" % str(req))
        rep = self.stub.Write(req)
        self.logger.debug("WriteTableEntries [Reply]: %s" % str(rep))

    def read_table_entries(self, table_id=0):
        req = p4runtime_pb2.ReadRequest()
        req.device_id = self.device_id
        entity = req.entities.add()
        table_entry = entity.table_entry
        table_entry.table_id = table_id

        self.logger.debug("ReadTableEntries [Request]: %s" % str(req))
        for rep in self.stub.Read(req):
            self.logger.debug("ReadTableEntries [Rep]: %s" % str(rep))
            yield rep

    def read_counters(self, counter_id=0, index=0):
        req = p4runtime_pb2.ReadRequest()
        req.device_id = self.device_id
        entity = req.entities.add()
        counter_entry = entity.counter_entry
        counter_entry.counter_id = counter_id
        counter_entry.index.index = index

        self.logger.debug("ReadCounters [Request]: %s" % str(req))
        for rep in self.stub.Read(req):
            self.logger.debug("ReadCounters [Reply]: %s" % str(rep))
            yield rep

    # def write_pre_entry(self, pre_entry):
    #     req = p4runtime_pb2.WriteRequest()
    #     req.device_id = self.device_id
    #     req.election_id.high = self.election_id_high
    #     req.election_id.low = self.election_id_low
    #     update = req.updates.add()
    #     update.type = p4runtime_pb2.Update.INSERT
    #     update.entity.packet_replication_engine_entry.CopyFrom(pre_entry)
    #     self.stub.Write(req)


if __name__ == "__main__":
    logger = getLogger(__name__)
    logger.setLevel(DEBUG)
    logger.addHandler(StreamHandler())
    client = P4RuntimeClient(
        ip="127.0.0.1",
        port="50001",
        device_id=1,
        p4info_txt="./p4src/build/basic.p4info.txt",
        p4device_json="./p4src/build/basic.bmv2.json",
        election_id_high=0,
        election_id_low=1,
        logger=logger
    )
    client.establish_stream_channel()
    client.master_arbitration_update()
    client.set_pipeline_config_forward()
    conf = client.get_pipeline_config_forward()
    print(conf)
    client.close_stream_channel()
