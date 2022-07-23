import time
from nest.topology import *
import nest.config as config

##############################
# Emulating wireless networks
##############################

# This program emulates wireless networks in NeST by building a topology
# consisting of one Basic Service Set (BSS)
# and an Independent Basic Service Set (IBSS) / Ad Hoc Network

# Configure the maximum number of wireless interfaces that will be used in the topology.
# It is 10 by default.
config.set_value("max_wireless_interface_count", 4)

### Demonstrating BSS ###

# Define an AccessPoint `ap`, and set its SSID and IP address
ap = AccessPoint("ap")
ap.set_ssid("MyBssNetwork")
ap.set_address("10.0.0.1/24")

# Activate the AP
ap.start()

# Define a Wifi Station `sta1`, and set its IP address
sta1 = WifiStation("sta1")
sta1.set_address("10.0.0.2/24")

# Make the station join the BSS associated with ap
sta1.join_bss(ap)
time.sleep(2)

# Testing the topology, by pinging
ap.ping(sta1.address)

### Demonstrating IBSS / Ad-Hoc Network ###

# Define 2 Wifi Stations, `sta2` and `sta3`, and set their IP addresses
sta2 = WifiStation("sta2")
sta3 = WifiStation("sta3")
sta2.set_address("10.0.1.1/24")
sta3.set_address("10.0.1.2/24")

# Make `sta2` start an ad-hoc network and make `sta3` join it
sta2.start_adhoc_network("MyAdHocNetwork")
sta3.join_adhoc_network("MyAdHocNetwork")
time.sleep(5)

# Testing the topology, by pinging
sta2.ping(sta3.address)
