# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""API related to wireless interfaces in topology"""

import logging
import time
from nest import engine
from nest import config
from nest.topology.device.wlan import Wlan
from nest.topology.interface.base_interface import BaseInterface
from nest.topology_map import TopologyMap
from nest.utils.hostapd_conf import hostapd_conf
from nest.utils.wpa_supplicant_conf import WPA_SUPPLICANT_CONF as wpa_supplicant_conf
from nest.topology.wireless_topology_map import WirelessTopologyMap

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments
# pylint: disable=logging-fstring-interpolation
# pylint: disable=consider-using-dict-items


class VirtualInterface(BaseInterface):
    """
    An abstraction of a wireless interface.
    """

    # A static member to indicate which wireless interfaces are being used already
    used_virtual_wireless_interfaces = 0
    mac_devices = config.get_value("max_wireless_interface_count")

    def __init__(self, name, node_id, mac_address, wlan_type, ssid, frequency=None):
        """
        Constructor of WirelessInterface

        Parameters
        ----------
        name : str
            Name of the wireless interface
        node_id : str
            Id of the node that the interface belongs to
        mac_address : str
            The 48-bit MAC address of the wireless interface.
        wlan_type : str
            The type of the interface, for example, 'managed', 'AP', 'ibss', etc.
        ssid : str
            The SSID of the wireless network to which this interface belongs.
        frequency : int
            The channel frequency (MHz) at which the interface communicates.
        """

        self._wlan = Wlan(name, node_id, mac_address, wlan_type, ssid, frequency)

        super().__init__(name, self._wlan)

    @property
    def mac_address(self):
        """
        Getter for the MAC address of the wireless interface.
        """
        return self._wlan.mac_address

    @property
    def type(self):
        """
        Getter for the type of the wireless interface
        """
        return self._wlan.type

    @property
    def frequency(self):
        """
        Getter for the frequency in MHz of the wireless interface
        """
        return self._wlan.frequency

    @property
    def ssid(self):
        """
        Getter for the SSID that the wireless interface is part of
        """
        return self._wlan.ssid

    @ssid.setter
    def ssid(self, ssid):
        """
        Setter for the SSID of the wireless network that the interface is part of.

        Parameters
        ----------
        ssid: str
            The SSID to be set.
        """
        self._wlan.ssid = ssid

    @frequency.setter
    def frequency(self, freq):
        """
        Setter for the frequency of the wireless network that the interface is part of.

        Parameters
        ----------
        freq: int
            The frequency to be set, in MHz.
        """
        self._wlan.frequency = freq

    @type.setter
    def type(self, type):  # pylint: disable=redefined-builtin
        """
        Setter for the type of the interface.

        Parameters
        ----------
        type: str
            The type to be set.
        """
        self._wlan.type = type

    @classmethod
    def create_virtual_wireless_interface(cls):
        """
        Function to create wireless interfaces.
        Number of interfaces created according to the value of
        "max_wireless_interface_count" config.
        """
        cls.used_virtual_wireless_interfaces += 1
        cls.mac_devices += 1

    @classmethod
    def use_virtual_wireless_interface(cls, ap, wlan_type, ssid, frequency=None):
       
        free_interface = cls.used_virtual_wireless_interfaces
        mac_address = f"02:00:00:00:00:{cls.mac_devices}"
        cls.create_virtual_wireless_interface()

        if free_interface >= 99:
            raise ValueError(
                """Exceeded the maximum number of virtual wireless interfaces."""
            )

        interface_name = f"{ap._ap_wl_int.id}_{free_interface}"
        
        # Shift the wireles interface into the namespace
        engine.set_virtual_interface(ap._ap_wl_int.node_id, ap._ap_wl_int.id , interface_name, "__ap")

        engine.assign_mac_address(ap._ap_wl_int.node_id , interface_name, mac_address)

        # Set the wlan interface up
        engine.set_interface_mode(ap._ap_wl_int.node_id, interface_name, "up")

        # If a WirelessInterface object corresponding to this wlan already exists, then reuse it.
        # if interface_name in WirelessTopologyMap.default_namespace_interfaces:
        #     wl_int = WirelessTopologyMap.default_namespace_interfaces[interface_name]
        #     wl_int.node_id = node_id
        #     wl_int.type = wlan_type
        #     wl_int.ssid = ssid
        #     wl_int.frequency = frequency
        #     del WirelessTopologyMap.default_namespace_interfaces[interface_name]
        #     return wl_int

        return VirtualInterface(
            interface_name, ap._ap_wl_int.node_id, mac_address, wlan_type , ssid, frequency
        )

#     def free_wireless_interface(self):
#         """
#         Frees the wireless interface by shifting it back to the default namespace
#         and makes it available for use by other namespaces.
#         """

#         # Get the physical device number of the wireless interface
#         phy_number = engine.get_phy_dev_number(self.id, self.node_id)

#         # Shift the wireless interface back to the default namespace
#         engine.shift_wlan_to_root(self.node_id, phy_number)

#         index = int(self.id[4:])
#         WirelessInterface.used_wireless_interfaces[index] = 0

#         # Move the wlan from its namespace to the default namespace in the topology map
#         TopologyMap.move_device(self.node_id, None, self.id)
#         WirelessTopologyMap.move_to_def_namespace(self)

#     def delete_vap(self, node_name):
#         """
#         Stops this interface from acting as an Access Point.
#         This results in dissolution of the entire BSS that it was part of.

#         Parameters
#         ----------
#         node_name: str
#             The name of the node in which the wireless interface is present.
#         """

#         # Check if the passed interface is an AP
#         if not WirelessTopologyMap.is_ap(self.node_id):
#             raise ValueError(f"Namespace {node_name} is not an Access Point.")

#         # Remove all the stations of this BSS.
#         logger.info(f"Disconnecting Access Point in node {node_name}.")
#         logger.info(
#             "Since you are removing an AP, all its stations will also get disconnected."
#         )
#         stations = WirelessTopologyMap.get_bss_stations(self)
#         for station in stations:
#             station.leave_bss(station.node_id)

#         engine.set_wlan_type(self.id, self.node_id, "managed")
#         WirelessTopologyMap.remove_bss(self)
#         self.free_wireless_interface()

#     def leave_bss(self, node_name):
#         """
#         Makes the interface leave the BSS that it is part of.

#         Parameters
#         ----------
#         node_name: str
#             The name of the node in which the wireless interface is present.
#         """
#         if not WirelessTopologyMap.is_bss_station(self.node_id):
#             raise ValueError(f"Namespace {node_name} is not a BSS station.")
#         WirelessTopologyMap.remove_station_from_bss(self)
#         self.free_wireless_interface()

#     def leave_ibss(self, node_name):
#         """
#         Makes the interface leave the IBSS that it is part of.

#         Parameters
#         ----------
#         node_name: str
#             The name of the node in which the wireless interface is present.
#         """
#         if not WirelessTopologyMap.is_ibss_station(self.node_id):
#             raise ValueError(f"Namespace {node_name} is not an IBSS station.")
#         engine.leave_ibss(self.id, self.node_id)
#         WirelessTopologyMap.remove_station_from_ibss(self)
#         self.free_wireless_interface()


# def check_network_and_leave(node):
#     """
#     Check if the given node is part of a wireless network, and if yes, leave that network.

#     Parameters
#     ----------
#     node: Node
#         The Node object
#     """
#     if WirelessTopologyMap.is_part_of_network(node.id):
#         logger.info(
#             f"The namespace {node.name} is already part of a wireless network, "
#             "and so will be made to leave that network."
#         )
#         leave_wireless_network(node)


# def leave_wireless_network(node):
#     """
#     Make this interface leave the wireless network that it is part of.
#     The interface could be an AP, a BSS station or an Ad hoc network station.

#     Parameters
#     ----------
#     node: Node
#         The Node object
#     """

#     is_ap, interface = WirelessTopologyMap.is_ap(node.id)
#     if is_ap:
#         interface.delete_ap(node.name)
#         return

#     is_bss_station, interface = WirelessTopologyMap.is_bss_station(node.id)
#     if is_bss_station:
#         interface.leave_bss(node.name)
#         logger.info(f"Node {node.name} leaving its BSS.")
#         return

#     is_ibss_station, interface = WirelessTopologyMap.is_ibss_station(node.id)
#     if is_ibss_station:
#         interface.leave_ibss(node.name)
#         logger.info(f"Node {node.name} leaving its ad hoc network.")
#         return

#     raise ValueError(
#         f"Namespace with name {node.name} isn't part of a wireless network"
#     )

# BSS can be joined by either passing the access_point (node) object, or by passing SSID
# pylint: disable=too-many-locals
def join_bss(
    node, access_point, sta_config={}
):  # pylint: disable=dangerous-default-value
    """
    Makes the given list of nodes join the BSS having the given 'ap' as the Access Point.

    PARAMETERS
    ----------
        list_of_nodes: list(node)
            A list of 'Node' objects, that should join the BSS.
        access_point: Node / str
            The node that is acting as Access Point, or the SSID of the BSS to be joined
        config: dict
            An optional python dictionary that holds values of various configuration parameters
            like 'key_mgmt', 'psk' etc. In its absence, default values are used.

    RETURNS
    -------
        WirelessInterface: list(WirelessInterface)
            A list of wireless interfaces, of the same size as the input list of nodes.
            A wireless interface is created inside each node,
            and these interfaces are connected to the given AP.
    """

    # Suppose the access point parameter is passed as a string, indicating the ssid of the network
    ssid_passed = isinstance(access_point, str)
    if ssid_passed:
        ssid = access_point
        access_point = WirelessTopologyMap.return_ap(ssid)
        if access_point is None:
            raise ValueError(f"No BSS found with the SSID {ssid}")
        ap_interface = access_point

    else:
        is_ap, ap_interface = WirelessTopologyMap.is_ap(access_point.id)
        if not is_ap:
            raise ValueError(
                f"The specified node {access_point.name} is not an Access Point."
            )

    # Checking if the variable is a list
    # if not isinstance(list_of_nodes, list):
    #     list_of_nodes = [list_of_nodes]

    # Building the wpa_supplicant conf file
    lines = wpa_supplicant_conf.split("\n")
    bssid = lines[1].split("=")
    bssid[1] = f"{ap_interface.mac_address}"
    lines[1] = "=".join(bssid)
    if "psk" in sta_config:
        password = lines[3].split("=")
        psk = sta_config["psk"]
        password[1] = f'"{psk}"'
        lines[3] = "=".join(password)
    with open(f"wpa_supplicant_{ap_interface.mac_address}.conf", "w") as file:
        for line in lines:
            file.write(line + "\n")

    # Adding all nodes to the network one by one
    # wlans = []
    # for node in list_of_nodes:
        # Creating a wireless interface in that node to connect it to the network
    check_network_and_leave(node)
    wlan = WirelessInterface.use_wireless_interface(
        node.id, "managed", ap_interface.ssid
    )
    engine.join_bss(ap_interface.mac_address, wlan.id, wlan.node_id)
    # wlans.append(wlan)
    WirelessTopologyMap.add_station_to_bss(ap_interface.node_id, wlan)

    if ssid_passed:
        logger.info(f"Node {node.name} has joined the BSS {ssid}.")
    else:
        logger.info(
            f"Node {node.name} has joined the BSS of node {access_point.name}."
        )

    time.sleep(2)
    return wlan





# TODO: Kill the hostapd and wpa_supplicant processes at the end of the program


def create_vap(node,ap, ssid, ap_config={}):  

    vlan = VirtualInterface.use_virtual_wireless_interface(ap,"VAP",ssid)

    # Reading the default config file and modifying the key-value pairs
    for key in hostapd_conf:
        if key in ap_config:
            hostapd_conf[key] = ap_config[key]
    hostapd_conf["ssid"] = ssid
    hostapd_conf["interface"] = vlan.id

    with open(f"hostapd_{vlan.id}.conf", "w") as file:
        for key in hostapd_conf:
            file.write(key + "=" + str(hostapd_conf[key]) + "\n")

    # Starting the access point
    engine.start_bss(vlan.id, vlan.node_id)

    # Adding the BSS into the wireless topology map
    WirelessTopologyMap.create_bss(ssid, vlan)

    logger.info(f"Starting Access Point in namespace {node.name}.")

    return vlan