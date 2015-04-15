node=$1

sudo ip netns exec $node ping -c2 qgw
sudo ip netns exec $node ping -c2 qhost1
sudo ip netns exec $node ping -c2 qhost2
sudo ip netns exec $node ping -c2 qsrv1
sudo ip netns exec $node ping -c2 qsrv2

sudo ip netns exec $node curl http://qsrv1:8124/
sudo ip netns exec $node curl http://qsrv2:8124/




