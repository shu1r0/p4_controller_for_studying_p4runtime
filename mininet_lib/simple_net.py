from mininet.cli import CLI
from mininet.net import Mininet
from mininet.log import setLogLevel


def setup_topo():
    net = Mininet()
    h1 = net.addHost("h1", ip="192.168.0.1/24", mac="00:00:00:00:00:00:01")
    h2 = net.addHost("h2", ip="192.168.0.2/24", mac="00:00:00:00:00:00:02")
    s1 = net.addHost("s1", ip=None, inNamespace=False)

    net.addLink(h1, s1, intfName1="h1_s1", intfName2="s1_h1")
    net.addLink(h2, s1, intfName1="h2_s1", intfName2="s1_h2")

    return net


if __name__ == "__main__":
    setLogLevel("debug")
    net = setup_topo()
    net.start()
    CLI(net)
    net.stop()
