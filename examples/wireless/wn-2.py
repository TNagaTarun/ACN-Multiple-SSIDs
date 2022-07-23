import time
from nest.topology import *
import nest.config as config

##############################
# Emulating wireless networks, with reusing of wireless interfaces
##############################

# Define 3 namespaces
n1 = Node("n1")
n2 = Node("n2")
n3 = Node("n3")

# Configure the maximum number of wireless interfaces that will be used in the topology.
# It is 10 by default.
config.set_value("max_wireless_interface_count", 3)

# Demonstrating BSS, by making node n1 as the AP
# and making node n2 join as a station
ap = create_ap(n1, "MyBSS", {})
ap.set_address("10.0.0.1/24")
[sta] = join_bss(n2, "MyBSS")
sta.set_address("10.0.0.2/24")
time.sleep(2)

# The topologies can be tested by pinging the nodes from each other
n1.ping(sta.address)

# Demostrating an ad hoc network between n2 and n3
# n2, which was part of a BSS, will be made to leave the BSS
[wlan2] = start_adhoc_network(n3, "MyAdHocNetwork", 2412)
[wlan1] = join_adhoc_network(n2, "MyAdHocNetwork", 2412)
wlan1.set_address("10.0.1.1/24")
wlan2.set_address("10.0.1.2/24")
time.sleep(5)

# The topologies can be tested by pinging the nodes from each other
n3.ping(wlan1.address)

# Demostrating an ad hoc network between n1 and n3
# n1, which was an access point of a BSS, will be made to leave the BSS
[wlan3, wlan4] = start_adhoc_network([n1, n3], "MySecondAdHocNetwork", 2412)
wlan3.set_address("10.0.2.1/24")
wlan4.set_address("10.0.2.2/24")
time.sleep(5)

# The topologies can be tested by pinging the nodes from each other
n3.ping(wlan3.address)
