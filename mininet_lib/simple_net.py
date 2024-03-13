from mininet.cli import CLI
from mininet.net import Mininet
from mininet.log import setLogLevel


def run_topo():
    net = Mininet()
    
    h1 = net.addHost("h1", ip="192.168.1.1/24", mac="08:00:00:00:00:01")
    h2 = net.addHost("h2", ip="192.168.2.2/24", mac="08:00:00:00:00:02")
    p1 = net.addHost("p1", ip=None, inNamespace=False)

    net.addLink(h1, p1, intfName1="h1_p1", intfName2="p1_h1")
    net.addLink(h2, p1, intfName1="h2_p1", intfName2="p1_h2")

    net.start()

    h1.cmdPrint("ip route add default via 192.168.1.254 dev h1_p1")
    h1.cmdPrint("arp -i h1_p1 -s 192.168.1.254 08:00:00:00:01:00")
    h2.cmdPrint("ip route add default via 192.168.2.254 dev h2_p1")
    h2.cmdPrint("arp -i h2_p1 -s 192.168.2.254 08:00:00:00:02:00")

    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run_topo()
