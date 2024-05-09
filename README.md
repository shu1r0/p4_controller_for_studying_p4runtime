# Simple P4Runtime Controller (for studying P4Runtime)

## P4 Compile

```bash
docker run --rm -v $PWD:/workdir -w /workdir opennetworking/p4c:stable p4c-bm2-ss --arch v1model -o p4src/build/basic.bmv2.json --p4runtime-files p4src/build/basic.p4info.txt --Wdisable=unsupported p4src/basic.p4
```

## Run mininet

```bash
docker run --privileged --rm -it -v $PWD:/workdir -w /workdir -p50001-50030:50001-50030 --name p4mn --hostname p4mn --entrypoint "bash" opennetworking/p4mn:stable
```

```bash
root@p4mn:/workdir# python mininet_lib/simple_net.py
```

```bash
mininet> p1 simple_switch_grpc --device-id 1 -i 1@p1_h1 -i 2@p1_h2 --log-console --log-level info ./p4src/build/basic.bmv2.json -- --cpu-port 255 --grpc-server-addr 0.0.0.0:50001 &
```

## References
- [P4Runtimeでコントロールプレーンを開発する Python編 (1/2)](https://madomadox.hatenablog.com/entry/2022/07/02/114709)
- https://github.com/p4lang/p4runtime/tree/main/proto/p4
- https://p4.org/p4-spec/p4runtime/main/P4Runtime-Spec.html
- https://github.com/opennetworkinglab/p4mn-docker


