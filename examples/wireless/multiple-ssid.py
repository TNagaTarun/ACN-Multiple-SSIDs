import time
from nest.topology import *
import nest.config as config
from nest.topology.wireless_topology_map import WirelessTopologyMap

##############################
# Emulating wireless networks
##############################

# This program emulates wireless networks in NeST by building a topology
# consisting of one Basic Service Set (BSS)
# with multiple-SSIDs

# Configure the maximum number of wireless interfaces that will be used in the topology.
# It is 10 by default.
config.set_value("max_wireless_interface_count", 4)

### Demonstrating BSS ###

# Define an AccessPoint `ap`, and set its SSIDs IPs
ap = AccessPoint("ap")
ap.set_ssid("SSID1")
ap.set_address("10.0.0.1/24")
ap.start()

vap = VirtualAccessPoint(ap,"vap1")
vap.set_ssid("SSID2")
vap.set_address("10.0.0.3/24")
# print(ap._ap_wl_int.node_id)
# Activate the AP
print(vap.ssid)
vap.start()
# Define a Wifi Station `sta1`, and set its IP address
sta1 = WifiStation("sta1")
sta1.set_address("10.0.0.2/24")
print(ap._ap_wl_int.node_id)
print(vap._ap_vl_int.node_id)
# Make the station join the BSS associated with ap
sta1.join_bss_virtual("SSID2")
time.sleep(2)
bss_networks = WirelessTopologyMap.get_bss_networks()
print(bss_networks)
# Testing the topology, by pinging
ap.ping(sta1.address)

