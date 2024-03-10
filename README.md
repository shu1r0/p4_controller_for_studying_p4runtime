# Simple P4Runtime Controller (for studying P4Runtime)

## P4 Compile

```
docker run --rm -v $PWD:/workdir -w /workdir opennetworking/p4c:stable p4c-bm2-ss --arch v1model -o p4src/build/basic.bmv2.json --p4runtime-files p4src/build/basic.p4info.txt --Wdisable=unsupported p4src/basic.p4
```

## Run mininet

```bash
docker run --privileged --rm -it -v $PWD:/workdir -w /workdir -p50001-50030:50001-50030 --name p4mn --hostname p4mn --entrypoint "bash" opennetworking/p4mn:stable
```

```bash
simple_switch_grpc --device-id 1 -i 1@s1_h1 -i 2@s1_h2 --log-console --log-level info ./p4src/build/basic.bmv2.json -- --cpu-port 255 --grpc-server-addr 0.0.0.0:50001
```

## References
- [P4Runtimeでコントロールプレーンを開発する Python編 (1/2)](https://madomadox.hatenablog.com/entry/2022/07/02/114709)
- https://github.com/p4lang/p4runtime/tree/main/proto/p4
- https://p4.org/p4-spec/p4runtime/main/P4Runtime-Spec.html
- https://github.com/opennetworkinglab/p4mn-docker



```txt
╰─(*ﾉ･ω･)ﾉ < sudo docker run --privileged --rm -it -v /tmp/p4mn:/tmp -p50001-50030:50001-50030 --name p4mn --hostname p4mn opennetworking/p4mn:stable                                             09:03:16
[sudo] password for shu1r0: 
Unable to find image 'opennetworking/p4mn:stable' locally
stable: Pulling from opennetworking/p4mn
0e9cbea72135: Already exists 
0f3aa031e3b6: Pull complete 
96791fdf0c3c: Pull complete 
1e9778e667e5: Pull complete 
4f4fb700ef54: Pull complete 
27ba553222af: Pull complete 
Digest: sha256:782b17be5a702ffe151ec7b61e67f93f1a62af38ce26640aa984ca7bd2e147fd
Status: Downloaded newer image for opennetworking/p4mn:stable
*** Error setting resource limits. Mininet's performance may be affected.
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 
*** Adding switches:
s1 
*** Adding links:
(h1, s1) (h2, s1) 
*** Configuring hosts
h1 h2 
*** Starting controller

*** Starting 1 switches
s1 ....⚡️ simple_switch_grpc @ 50001

*** Starting CLI:
mininet> nodes   
available nodes are: 
h1 h2 s1
mininet> py print(s1)
invalid syntax (<string>, line 1)
mininet> py print(s1.__dir__())
invalid syntax (<string>, line 1)
mininet> py print("hopge")
invalid syntax (<string>, line 1)
mininet> py               
unexpected EOF while parsing (<string>, line 0)
mininet> p    
pingall       pingallfull   pingpair      pingpairfull  ports         px            py            
mininet> py s1
<ONOSBmv2Switch s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None pid=16> 
mininet> py print(s1)
invalid syntax (<string>, line 1)
mininet> py print(dir(s1))
invalid syntax (<string>, line 1)
mininet> py dir(s1)           
['IP', 'MAC', '__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_popen', 'addIntf', 'bmv2Args', 'bmv2popen', 'chassisConfig', 'chassisConfigFile', 'checkSetup', 'cleanup', 'cleanupTmpFiles', 'cmd', 'cmdPrint', 'config', 'configDefault', 'connected', 'connectionsTo', 'controlIntf', 'cpuPort', 'debugger', 'decoder', 'defaultDpid', 'defaultIntf', 'delIntf', 'deleteIntfs', 'doOnosNetcfg', 'dpid', 'dpidLen', 'dryrun', 'elogger', 'execed', 'fdToNode', 'getBmv2CmdString', 'getDeviceConfig', 'getStratumCmdString', 'grpcPort', 'grpcPortInternal', 'inNamespace', 'inToNode', 'injectPorts', 'intf', 'intfIsUp', 'intfList', 'intfNames', 'intfs', 'isSetup', 'json', 'keepaliveFile', 'killBmv2', 'lastCmd', 'lastPid', 'latitude', 'linkTo', 'listenPort', 'logfd', 'logfile', 'loglevel', 'longitude', 'master', 'mininet_exception', 'monitor', 'mountPrivateDirs', 'name', 'nameToIntf', 'netcfgfile', 'newPort', 'nextGrpcPort', 'notifications', 'onosDeviceId', 'opts', 'outToNode', 'p4DeviceId', 'params', 'pexec', 'pid', 'pipeconfId', 'pktdump', 'pollOut', 'popen', 'portBase', 'ports', 'printBmv2Log', 'privateDirs', 'read', 'readbuf', 'readline', 'sendCmd', 'sendInt', 'setARP', 'setDefaultRoute', 'setHostRoute', 'setIP', 'setMAC', 'setParam', 'setup', 'shell', 'slave', 'start', 'startShell', 'stdin', 'stdout', 'stop', 'stopped', 'targetName', 'terminate', 'thriftPort', 'unmountPrivateDirs', 'useStratum', 'valgrind', 'waitBmv2Start', 'waitExited', 'waitOutput', 'waitReadable', 'waiting', 'withGnmi', 'write']
mininet> py s1.params
{'isSwitch': True}
mininet> py s1.sw_path
'ONOSBmv2Switch' object has no attribute 'sw_path'
mininet> py s1.json   
mininet> py s1.getBmv2CmdString()
simple_switch_grpc --device-id 1 -i 1@s1-eth1 -i 2@s1-eth2 --log-console -Lwarn --no-p4 -- --cpu-port 255 --grpc-server-addr 0.0.0.0:50001
mininet> exit 
*** Stopping 0 controllers

*** Stopping 2 links
..
*** Stopping 1 switches
s1 
*** Stopping 2 hosts
h1 h2 
*** Done
completed in 312.484 seconds


(venv) ╭─shu1r0@shu1r0-ryzen-desktop /home/shu1r0/workspace/p4_env/lib/p4_controller  (master →☡)
╰─(*ﾉ･ω･)ﾉ < sudo docker run --privileged --rm -it -v /tmp/p4mn:/tmp -p50001-50030:50001-50030 --name p4mn --hostname p4mn opennetworking/p4mn:stable --entrypoint "bash"                         09:08:50
Usage: mn [options]
(type mn -h for details)

mn: error: no such option: --entrypoint
(venv) ╭─shu1r0@shu1r0-ryzen-desktop /home/shu1r0/workspace/p4_env/lib/p4_controller  (master →☡)
╰─(# ﾟДﾟ) < sudo docker run --privileged --rm -it -v /tmp/p4mn:/tmp -p50001-50030:50001-50030 --name p4mn --hostname p4mn --entrypoint opennetworking/p4mn:stable "/bin/bash"                     09:09:08
docker: invalid reference format.
See 'docker run --help'.
(venv) ╭─shu1r0@shu1r0-ryzen-desktop /home/shu1r0/workspace/p4_env/lib/p4_controller  (master →☡)
╰─(# ﾟДﾟ) < sudo docker run --privileged --rm -it -v /tmp/p4mn:/tmp -p50001-50030:50001-50030 --name p4mn --hostname p4mn --entrypoint "/bin/bash" opennetworking/p4mn:stable                     09:10:00
root@p4mn:~# s
savelog             select              service             sg                  sha384sum           shuf                snice               start-stop-daemon   sum                 sync
script              select-editor       set                 sh                  sha512sum           simple_switch_grpc  socat               stat                suspend             sysctl
scriptreplay        sensible-browser    setarch             sh.distrib          shadowconfig        skill               sort                stdbuf              swaplabel           
sdiff               sensible-editor     setsid              sha1sum             shift               slabtop             source              stty                swapoff             
sed                 sensible-pager      setterm             sha224sum           shopt               slattach            split               su                  swapon              
see                 seq                 sfdisk              sha256sum           shred               sleep               ss                  sulogin             switch_root         
root@p4mn:~# which simple_switch_grpc 
/usr/local/bin/simple_switch_grpc
root@p4mn:~# simple_switch_grpc -h
Usage: SWITCH_NAME [options] <path to JSON config file>
Options:
  -h [ --help ]               Display this help message
  -i [ --interface ] arg      <port-num>@<interface-name>: Attach network 
                              interface <interface-name> as port <port-num> at 
                              startup. Can appear multiple times
  --pcap [=arg(=.)]           Generate pcap files for interfaces. Argument is 
                              optional and is the directory where pcap files 
                              should be written. If omitted, files will be 
                              written in current directory.
  --use-files arg             Read/write packets from files (interface X 
                              corresponds to two files X_in.pcap and 
                              X_out.pcap). Argument is the time to wait (in 
                              seconds) before starting to process the packet 
                              files.
  --device-id arg             Device ID, used to identify the device in IPC 
                              messages (default 0)
  --nanolog arg               IPC socket to use for nanomsg pub/sub logs 
                              (default: no nanomsg logging
  --log-console               Enable logging on stdout
  --log-file arg              Enable logging to given file
  -L [ --log-level ] arg      Set log level, supported values are 'trace', 
                              'debug', 'info', 'warn', 'error', off'; default 
                              is 'trace'
  --log-flush                 If used with '--log-file', the logger will flush 
                              to disk after every log message
  --restore-state arg         Restore state from file
  --dump-packet-data arg      Specify how many bytes of packet data to dump 
                              upon receiving & sending a packet. We use the 
                              logger to dump the packet data, with log level 
                              'info', so make sure the log level you have set 
                              does not exclude 'info' messages; default is 0, 
                              which means that nothing is logged.
  -v [ --version ]            Display version information
  --json-version              Display max bmv2 JSON version supported in the 
                              format <major>.<minor>; all bmv2 JSON versions 
                              with the same <major> version number are also 
                              supported.
  --no-p4                     Enable the switch to start without an inout 
                              configuration
  --max-port-count arg (=512) Maximum number of interfaces that can be bound to
                              the switch; this is not an upper bound on each 
                              port number, which can be arbitrary. Depending on
                              the target, this max value may or may not be 
                              enforced.
This target also comes with its own command line parser, make sure you separate general bmv2 options from, target specific options with '--'
Target specific options:
Target options:
  --load-modules arg        Load the given .so files (comma-separated) as 
                            modules.
  --disable-swap            disable JSON swapping at runtime
  --grpc-server-addr arg    bind gRPC server to given address [default is 
                            0.0.0.0:50051]
  --cpu-port arg            set CPU port, will be used for packet-in / 
                            packet-out; do not add an interface with this port 
                            number
  --drop-port arg           choose drop port number (default is 511)
  --dp-grpc-server-addr arg use a gRPC channel to inject and receive dataplane 
                            packets; bind this gRPC server to given address, 
                            e.g. 0.0.0.0:50052

```
