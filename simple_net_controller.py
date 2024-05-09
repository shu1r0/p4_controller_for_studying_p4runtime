import argparse
import binascii
import socket
from time import sleep
from logging import StreamHandler, DEBUG, getLogger
from typing import List

from p4.v1 import p4runtime_pb2

from p4controller.p4runtime_client import P4RuntimeClient, TableEntry


def get_args():
    """get args from command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="p4 switch address")
    parser.add_argument("--port", default="50001", help="p4 switch port")
    parser.add_argument("--device_id", default=1, help="p4 device id")
    parser.add_argument("--p4info_txt", default="./p4src/build/basic.p4info.txt", help="p4info file")
    parser.add_argument("--p4device_json", default="./p4src/build/basic.bmv2.json", help="p4 device json file")
    parser.add_argument("--election_id_high", default=0, help="Election ID (High)")
    parser.add_argument("--election_id_low", default=1, help="Election ID (Low)")

    args = parser.parse_args()
    return args


def new_p4runtime_client():
    args = get_args()
    logger = getLogger(__name__)
    logger.setLevel(DEBUG)
    logger.addHandler(StreamHandler())
    client = P4RuntimeClient(
        ip=args.ip,
        port=args.port,
        device_id=args.device_id,
        p4info_txt=args.p4info_txt,
        p4device_json=args.p4device_json,
        election_id_high=args.election_id_high,
        election_id_low=args.election_id_low,
        logger=logger
    )
    return client


if __name__ == "__main__":
    client = new_p4runtime_client()
    client.establish_stream_channel()
    client.master_arbitration_update()
    client.set_pipeline_config_forward()
    conf = client.get_pipeline_config_forward()
    # print(conf)

    # 書き込むテーブルエントリ．各IDはp4infoから取得
    table_entries: List[TableEntry] = [
        {
            "update_type": p4runtime_pb2.Update.MODIFY,
            "table_id": 33574068,  # MyIngress.ipv4_lpm
            "is_default_action": True,
            "action": {
                "action_id": 16805608,  # MyIngress.drop
            }
        }, {
            "update_type": p4runtime_pb2.Update.INSERT,
            "table_id": 33574068,  # MyIngress.ipv4_lpm
            "match": [
                {
                    "field_id": 1,  # hdr.ipv4.dstAddr
                    "match_type": p4runtime_pb2.FieldMatch.LPM,
                    "value": socket.inet_aton("192.168.1.1"),
                    "prefix_len": 32,
                }
            ],
            "action": {
                "action_id": 16799317,  # MyIngress.ipv4_forward
                "params": [
                    (1, binascii.unhexlify("08:00:00:00:00:01".replace(':', ''))),  # (dstAddr, "08:00:00:00:00:01")
                    (2, (1).to_bytes(2, "big"))  # (port, 1)
                ]
            }
        }, {
            "update_type": p4runtime_pb2.Update.INSERT,
            "table_id": 33574068,  # MyIngress.ipv4_lpm
            "match": [
                {
                    "field_id": 1,  # hdr.ipv4.dstAddr
                    "match_type": p4runtime_pb2.FieldMatch.LPM,
                    "value": socket.inet_aton("192.168.2.2"),
                    "prefix_len": 32,
                }
            ],
            "action": {
                "action_id": 16799317,  # MyIngress.ipv4_forward
                "params": [
                    (1, binascii.unhexlify("08:00:00:00:00:02".replace(':', ''))),  # (dstAddr, "08:00:00:00:00:02")
                    (2, (2).to_bytes(2, "big"))  # (port, 2)
                ]
            }
        },
    ]
    client.write_table_entries(table_entries)

    tables = client.read_table_entries()
    for table in tables:
        print(str(table))

    client.close_stream_channel()
