# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest import config
from nest.topology import *

# This program emulates an Extended Service Set (ESS) with two Basic Service Sets (BSS).
# There are 2 access points ap1 and ap2, that are connected through a veth pair.
# sta1 is a wi-fi station connected to ap1, and sta2 is a wi-fi station connected to ap2.
# Five ping packets are sent from sta1 to sta2,
# and the success/failure of these packets is reported.

# Configure the maximum number of wireless interfaces that will be used in the topology.
# It is 10 by default.
config.set_value("max_wireless_interface_count", 4)

# Create 4 hosts, ap1, ap2, sta1 and sta2
ap1 = AccessPoint("ap1")
ap2 = AccessPoint("ap2")
sta1 = WifiStation("sta1")
sta2 = WifiStation("sta2")

# Connecting a virtual ethernet cable between ap1 and ap2
(eth1, eth2) = connect(ap1, ap2)

# Assign IP addresses according to subnets
ap1.set_address("10.0.0.1/24")
ap2.set_address("10.0.1.1/24")
sta1.set_address("10.0.0.2/24")
sta2.set_address("10.0.1.2/24")
eth1.set_address("10.0.2.1/24")
eth2.set_address("10.0.2.2/24")

# Assigning SSIDs and activating access points at ap1 and ap2
ap1.set_ssid("ExampleESS")
ap2.set_ssid("ExampleESS")
wlan_ap1 = ap1.start()
wlan_ap2 = ap2.start()

# Make sta1 and sta2 join the respective BSS networks
wlan_sta1 = sta1.join_bss(ap1)
wlan_sta2 = sta2.join_bss(ap2)

# Enabling IP forwarding in ap1 and ap2
ap1.enable_ip_forwarding()
ap2.enable_ip_forwarding()

# Adding routing directions
sta1.add_route("DEFAULT", wlan_sta1, "10.0.0.1")
sta2.add_route("DEFAULT", wlan_sta2, "10.0.1.1")
ap1.add_route("10.0.1.2", eth1)
ap2.add_route("10.0.0.2", eth2)

# Ping from sta1 to sta2
sta1.ping(sta2.address)
