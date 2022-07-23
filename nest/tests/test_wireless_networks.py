# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""Test Wireless Networks API"""

import unittest
import time
from nest import config
from nest.clean_up import delete_namespaces, delete_wlans
from nest.topology import AccessPoint, WifiStation, connect
from nest.topology.interface.wireless_interface import WirelessInterface
from nest.topology.interface.wireless_interface import (
    leave_wireless_network,
    start_adhoc_network,
)
from nest.topology.wireless_topology_map import WirelessTopologyMap
from nest.topology_map import TopologyMap

# pylint: disable=missing-docstring
# pylint: disable=too-many-instance-attributes


class TestWirelessNetworks(unittest.TestCase):
    def setUp(self):
        # Create nodes
        self.ap1 = AccessPoint("ap1")
        self.ap2 = AccessPoint("ap2")
        self.sta1 = WifiStation("sta1")
        self.sta2 = WifiStation("sta2")
        self.sta3 = WifiStation("sta3")

        config.set_value("max_wireless_interface_count", 5)

        self.ap1.set_ssid("bss1")
        self.ap2.set_ssid("bss2")
        self.ap1.set_address("10.0.0.1/24")
        self.ap2.set_address("10.0.1.1/24")

    def tearDown(self):
        delete_namespaces()
        delete_wlans()
        TopologyMap.delete_all_mapping()
        WirelessTopologyMap.delete_all_mappings()
        WirelessInterface.created_wireless_interfaces = False

    def test_bss_network(self):
        self.ap1.start()
        self.sta1.set_address("10.0.0.2/24")
        self.sta2.set_address("10.0.0.3/24")
        self.sta1.join_bss(self.ap1)
        self.sta2.join_bss("bss1")

        self.assertTrue(self.sta1.ping(self.sta2.address))
        self.assertTrue(self.ap1.ping(self.sta2.address))
        self.ap1.stop()

    def test_ibss_network(self):
        self.sta1.set_address("10.0.2.1/24")
        self.sta2.set_address("10.0.2.2/24")
        self.sta3.set_address("10.0.2.3/24")

        self.sta1.start_adhoc_network("test_ibss")
        time.sleep(5)
        self.sta2.join_adhoc_network("test_ibss")
        self.sta3.join_adhoc_network("test_ibss")
        time.sleep(5)
        self.assertTrue(self.sta1.ping(self.sta3.address))
        self.sta3.leave_wireless_network()
        self.assertFalse(self.sta1.ping(self.sta3.address))
        self.assertTrue(self.sta2.ping(self.sta1.address))
        self.sta1.leave_wireless_network()
        self.sta2.leave_wireless_network()

    def test_ibss_network_group_join(self):
        [wlan1, wlan2, wlan3] = start_adhoc_network(
            [self.sta1, self.sta2, self.sta3], "test_ibss2"
        )
        wlan1.set_address("10.0.3.1/24")
        wlan2.set_address("10.0.3.2/24")
        wlan3.set_address("10.0.3.3/24")
        time.sleep(5)
        self.assertTrue(self.sta1.ping(wlan3.address))
        self.assertTrue(self.sta2.ping(wlan3.address))
        leave_wireless_network(self.sta1)
        leave_wireless_network(self.sta2)
        leave_wireless_network(self.sta3)

    def test_ibss_wireless_topology_map(self):
        self.sta1.set_address("10.0.2.1/24")
        self.sta2.set_address("10.0.2.2/24")
        self.sta3.set_address("10.0.2.3/24")

        self.sta1.start_adhoc_network("test_ibss")
        self.sta2.join_adhoc_network("test_ibss")
        self.sta3.join_adhoc_network("test_ibss")

        self.assertEqual(len(WirelessTopologyMap.wireless_topology_map["ibss"]), 1)
        self.assertEqual(len(WirelessTopologyMap.wireless_topology_map["bss"]), 0)
        self.assertEqual(
            len(WirelessTopologyMap.wireless_topology_map["ibss"][0]["stations"]), 3
        )

        self.sta1.leave_wireless_network()
        self.assertEqual(
            len(WirelessTopologyMap.wireless_topology_map["ibss"][0]["stations"]), 2
        )
        self.assertEqual(len(WirelessTopologyMap.default_namespace_interfaces), 1)

        self.sta2.leave_wireless_network()
        self.sta3.leave_wireless_network()
        self.assertEqual(len(WirelessTopologyMap.wireless_topology_map["ibss"]), 0)

    def test_bss_wireless_topology_map(self):
        self.ap1.start()
        self.sta1.set_address("10.0.0.2/24")
        self.sta2.set_address("10.0.0.3/24")
        self.sta1.join_bss(self.ap1)
        self.sta2.join_bss("bss1")

        self.assertEqual(len(WirelessTopologyMap.wireless_topology_map["ibss"]), 0)
        self.assertEqual(len(WirelessTopologyMap.wireless_topology_map["bss"]), 1)
        self.assertEqual(
            WirelessTopologyMap.wireless_topology_map["bss"][0]["ssid"], "bss1"
        )
        self.assertEqual(
            len(WirelessTopologyMap.wireless_topology_map["bss"][0]["stations"]), 2
        )

        self.sta1.leave_wireless_network()
        self.assertEqual(
            len(WirelessTopologyMap.wireless_topology_map["bss"][0]["stations"]), 1
        )

        self.ap2.start()
        self.assertEqual(len(WirelessTopologyMap.wireless_topology_map["bss"]), 2)

        self.ap1.stop()
        self.ap2.stop()
        self.assertEqual(len(WirelessTopologyMap.wireless_topology_map["bss"]), 0)
        self.assertEqual(len(WirelessTopologyMap.default_namespace_interfaces), 3)

    def test_ess(self):
        (eth1, eth2) = connect(self.ap1, self.ap2)
        self.sta1.set_address("10.0.0.2/24")
        self.sta2.set_address("10.0.1.2/24")
        eth1.set_address("10.0.2.1/24")
        eth2.set_address("10.0.2.2/24")

        self.ap1.start()
        self.ap2.start()

        wlan_sta1 = self.sta1.join_bss(self.ap1)
        wlan_sta2 = self.sta2.join_bss(self.ap2)

        self.ap1.enable_ip_forwarding()
        self.ap2.enable_ip_forwarding()

        # Adding routing directions
        self.sta1.add_route("DEFAULT", wlan_sta1, "10.0.0.1")
        self.sta2.add_route("DEFAULT", wlan_sta2, "10.0.1.1")
        self.ap1.add_route("10.0.1.2", eth1)
        self.ap2.add_route("10.0.0.2", eth2)

        self.assertTrue(self.sta1.ping(self.sta2.address))


if __name__ == "__main__":
    unittest.main()
