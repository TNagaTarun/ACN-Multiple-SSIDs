# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *

# This program emulates an Extended Service Set (ESS) with two Basic Service Sets (BSS).
# There are 2 access points ap1 and ap2, that are connected through a veth pair.
# sta1 is a wi-fi station connected to ap1, and sta2 is a wi-fi station connected to ap2.
# Five ping packets are sent from sta1 to sta2, 
# and the success/failure of these packets is reported.

# Create 4 hosts, ap1, ap2, sta1 and sta2
ap1 = Node('ap1')
ap2 = Node('ap2')
sta1 = Node('sta1')
sta2 = Node('sta2')

# Connecting a virtual ethernet cable between ap1 and ap2
(eth1, eth2) = connect(ap1, ap2)

# Creating access points at ap1 and ap2
wlan_ap1 = create_ap(ap1, "ExampleESS")
wlan_ap2 = create_ap(ap2, "ExampleESS")

# make sta1 and sta2 join the respective BSS networks
[wlan_sta1] = join_bss(sta1, wlan_ap1)
[wlan_sta2] = join_bss(sta2, wlan_ap2)

# Assign IP addresses according to subnets
wlan_ap1.address = '10.0.0.1/24'
wlan_ap2.address = '10.0.1.1/24'
wlan_sta1.address = '10.0.0.2/24'
wlan_sta2.address = '10.0.1.2/24'
eth1.address = '10.0.2.1/24'
eth2.address = '10.0.2.2/24'

# Enabling IP forwarding in ap1 and ap2
ap1.enable_ip_forwarding()
ap2.enable_ip_forwarding()

# Adding routing directions
# TODO: Need to change the input validator of add_route 
# for the second parameter to accept topology.WirelessInterface objects also.
sta1.add_route('DEFAULT', wlan_sta1, '10.0.0.1')
sta2.add_route('DEFAULT', wlan_sta2, '10.0.1.1')
ap1.add_route('10.0.1.2', eth1)
ap2.add_route('10.0.0.2', eth2)

# Ping from sta1 to sta2
sta1.ping('10.0.1.2')

