from nest.topology import *
import nest.config as config

##############################
# Emulating wireless networks
##############################

# Define 2 namespaces
config.set_value("assign_random_names", False)
config.set_value("delete_namespaces_on_termination", False)
n1 = Node("n1")
n2 = Node("n2")
n3 = Node("n3")
n4 = Node("n4")

# Configure the maximum number of wireless interfaces that will be used in the topology.
# It is 10 by default.
config.set_value("max_wireless_interface_count", 4)

# Demonstrating BSS, by making node n1 as the AP
# and making node n2 join as a station
ap = create_ap(n1, "MyBSS", {})
ap.address = "10.0.0.1/24"
[sta] = join_bss(n2, ap)
sta.address = "10.0.0.2/24"

# Demonstrating an ad-hoc network, using nodes n3 and n4
[wlan1, wlan2] = create_adhoc_network([n3, n4], "MyAdHocNetwork", 2412)
wlan1.address = "10.0.1.1/24"
wlan2.address = "10.0.1.2/24"
time.sleep(5)

# The topologies can be tested by pinging the nodes from each other
n3.ping(wlan2.address)
n1.ping(sta.address)
