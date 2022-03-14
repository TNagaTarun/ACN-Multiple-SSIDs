# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to wireless interfaces in topology"""

import logging
import time
from nest import engine
import nest.config as config
from nest.topology.wlan import Wlan
from nest.utils.hostapd_conf import hostapd_conf
from nest.utils.wpa_supplicant_conf import wpa_supplicant_conf

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


class WirelessInterface:
    """
    An abstraction of a wireless interface.
    """

    # A static member to indicate which wireless interfaces are being used already
    used_wireless_interfaces = []

    # A static member to indicate if the required number of wireless interfaces
    # have been created in the kernel or not
    created_wireless_interfaces = False

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

    @property
    def address(self):
        """
        Getter for the IP address associated
        with the interface
        """
        return self._wlan.address

    @address.setter
    def address(self, address):
        """
        Assigns IP address to an interface

        Parameters
        ----------
        address : Address or str
            IP address to be assigned to the interface
        """
        self._wlan.address = address

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

    @property
    def name(self):
        """
        Getter for the name of the wireless interface, like 'wlan0', 'wlan1' etc.
        """
        return self._wlan.name

    @property
    def node_id(self):
        """
        Getter for the id of the node that the wireless interface is present in.
        """
        return self._wlan.node_id

    @classmethod
    def create_wireless_interfaces(cls):
        """
        Function to create wireless interfaces.
        Number of interfaces created according to the value of
        "max_wireless_interface_count" config.

        """

        count = config.get_value("max_wireless_interface_count")
        print("Count of wireless interfaces being created : ", count)
        engine.unload_hwsim()
        engine.load_hwsim(count)

        cls.used_wireless_interfaces = [0 for i in range(0, count)]
        cls.created_wireless_interfaces = True

    @classmethod
    def use_wireless_interface(cls, node_id, wlan_type, ssid, frequency=None):
        """
        A function that puts an already created wireless interface into use.
        It searches for an available wireless interface in the kernel,
        shifts it into the specified node, and sets the wireless interface up.

        Also creates a WirelessInterface object according to the passed parameters
        and returns the object.

        Parameters
        ----------
        node_id: str
            Id of the node into which the interface has to be placed.
        wlan_type: str
            Type of the wireless interface to be used, like 'managed', 'ibss', 'monitor' etc.
        ssid: str
            The SSID of the wireless network that this interface is going to be part of.
        frequency: int
            The frequency of the channel over which this interface will be communicating.

        Returns
        -------
        WirelessInterface object.
        """

        # If the wireless interfaces have not been created yet, create them first.
        if not cls.created_wireless_interfaces:
            cls.create_wireless_interfaces()

        # Finding the first unused wireless interface
        free_interface = -1
        for i in range(0, len(cls.used_wireless_interfaces)):
            if cls.used_wireless_interfaces[i] == 0:
                free_interface = i
                cls.used_wireless_interfaces[i] = 1
                break

        if free_interface == -1:
            raise ValueError(
                """Exceeded the maximum number of wireless interfaces.
                You might want to reset the 'max_wireless_interface_count' config."""
            )

        interface_name = f"wlan{free_interface}"

        # Get the MAC address of the wireless interface
        mac_address = engine.get_mac_address(interface_name)

        # Get the physical device number of the wireless interface
        phy_number = engine.get_phy_dev_number(interface_name)

        # Shift the wireles interface into the namespace
        engine.shift_wlan_to_ns(node_id, phy_number)

        # Set the wlan interface up
        engine.set_interface_mode(node_id, interface_name, "up")

        return WirelessInterface(
            interface_name, node_id, mac_address, wlan_type, ssid, frequency
        )

    def free_wireless_interface(self):
        """
        Frees the wireless interface by shifting it back to the default namespace
        and makes it available for use by other namespaces.

        Parameters
        ----------
        interface: WirelessInterface
            The object corresponding to the wireless interface that has to be freed.
        """

        # Get the physical device number of the wireless interface
        phy_number = engine.get_phy_dev_number(self.name, self.node_id)

        # Shift the wireless interface back to the default namespace
        engine.shift_wlan_to_root(self.node_id, phy_number)

        index = int(self.name[4:])
        WirelessInterface.used_wireless_interfaces[index] = 0

        # The interface is freed on the kernel,
        # but how to free the python object??

        # TODO: Have to remove the interface from the TopologyMap.


def create_ap(node, ssid, ap_config={}):
    """
    Creates a wireless interface inside the given node, and makes it an Access Point.
    Parameters
    ----------
        node: node Object
            The node object whose interface has to be made an access point
        ssid: str
            The ssid of the network to be created
        config: dict of configuration
            All the additional configurations to be added to the network
            Note: The key names have to resemble with the standard of the hostapd.conf file
    RETURNS:
        WirelessInterface: list(WirelessInterface)
            A Wireless Interface object that has been placed inside the node and made an AP.
    """

    # Creating an access point for making it an AP
    wlan = WirelessInterface.use_wireless_interface(node.id, "AP", ssid)

    # Reading the default config file and modifying the key-value pairs
    for key in hostapd_conf:
        if key in ap_config:
            hostapd_conf[key] = ap_config[key]
    hostapd_conf["ssid"] = ssid
    hostapd_conf["interface"] = wlan.name

    with open(f"hostapd_{wlan.name}.conf", "w") as file:
        for key in hostapd_conf:
            file.write(key + "=" + str(hostapd_conf[key]) + "\n")

    # Starting the access point
    engine.start_bss(wlan.name, wlan.node_id)
    return wlan


def join_bss(list_of_nodes, access_point, sta_config={}):
    """
    Makes the given list of nodes join the BSS having the given 'ap' as the Access Point.

    PARAMETERS
    ----------
        list_of_nodes: list(node)
            A list of 'Node' objects, that should join the BSS.
        ap: WirelessInterface
            The wireless interface corresponding to the node that is acting as Access Point.
        config: dict
            An optional python dictionary that holds values of various configuration parameters
            like 'key_mgmt', 'psk' etc. In its absence, default values are used.
    RETURNS:
        WirelessInterface: list(WirelessInterface)
            A list of wireless interfaces, of the same size as the input list of nodes.
            A wireless interface is created inside each node,
            and these interfaces are connected to the given AP.
    """

    # Checking if the variable is a list
    if not isinstance(list_of_nodes, list):
        list_of_nodes = [list_of_nodes]

    lines = wpa_supplicant_conf.split("\n")
    bssid = lines[1].split("=")
    bssid[1] = f"{access_point.mac_address}"
    lines[1] = "=".join(bssid)
    if "psk" in sta_config:
        password = lines[3].split("=")
        psk = sta_config["psk"]
        password[1] = f'"{psk}"'
        lines[3] = "=".join(password)
    with open(f"wpa_supplicant_{access_point.mac_address}.conf", "w") as file:
        for line in lines:
            file.write(line + "\n")

    # Adding all nodes to the network one by one
    wlans = []
    for node in list_of_nodes:
        # Creating a wireless interface in that node to connect it to the network
        wlan = WirelessInterface.use_wireless_interface(
            node.id, "managed", access_point.ssid
        )
        engine.join_bss(access_point.mac_address, wlan.name, wlan.node_id)
        wlans.append(wlan)
    return wlans


def join_adhoc_network(list_of_nodes, ssid, frequency=2412):
    """
    Makes the given list of nodes join the existing ad hoc network of the given SSID.

    PARAMETERS
    ----------
        list_of_nodes: list(node)
            A list of 'Node' objects, that should join the IBSS.
        ssid: str
            The SSID of the adhoc network to be formed
        frequency: int
            The frequency of the channel in which the nodes should operate
    RETURNS:
        WirelessInterface: list(WirelessInterface)
            A list of wireless interfaces, of the same size as the input list of nodes.
            A wireless interface is created inside each node,
            and these interfaces are made part of the existing ad hoc network.
    """

    # Checking if the variable is a list
    if not isinstance(list_of_nodes, list):
        list_of_nodes = [list_of_nodes]
    wlans = []

    # Creating wireless interfaces and adding it to the adhoc network one by one
    for node in list_of_nodes:
        wlan = WirelessInterface.use_wireless_interface(
            node.id, "ibss", ssid, frequency
        )
        engine.set_wlan_type(wlan.name, wlan.node_id, "ibss")
        engine.join_ibss(wlan.name, ssid, frequency, wlan.node_id)
        wlans.append(wlan)
    return wlans


def create_adhoc_network(list_of_nodes, ssid, frequency=2412):
    """
    Creates a adhoc network of the given SSID and makes the given list of nodes join it.

    PARAMETERS
    ----------
        list_of_nodes: list(node)
            A list of 'Node' objects, that should join the IBSS.
        ssid: str
            The SSID of the adhoc network to be formed
        frequency: int
            The frequency of the channel in which the nodes should operate
    RETURNS:
        WirelessInterface: list(WirelessInterface)
            A list of wireless interfaces, of the same size as the input list of nodes.
            A wireless interface is created inside each node,
            and these interfaces are made part of an ad hoc network.
    """

    # Check if value is a list
    if not isinstance(list_of_nodes, list):
        list_of_nodes = [list_of_nodes]
    wlans = []

    # Creating wireless interfaces and starting the adhoc network
    wlan = WirelessInterface.use_wireless_interface(
        list_of_nodes[0].id, "ibss", ssid, frequency
    )
    engine.set_wlan_type(wlan.name, wlan.node_id, "ibss")
    engine.join_ibss(wlan.name, ssid, frequency, wlan.node_id)
    wlans.append(wlan)

    # Pausing the execution of the program for a while as if two interfaces invoke the command
    # for starting an ibss with almost no delay then kernel will create two seprate ibss with
    # the same ssid and the nodes will not be able to reach each other
    time.sleep(20)
    # TODO: Find the optimum delay to be given, or find a different workaround
    # Taking upto 10 seconds for it to work correctly

    # Creating wireless interfaces and adding it to the adhoc network one by one
    for i in range(1, len(list_of_nodes)):
        wlan = WirelessInterface.use_wireless_interface(
            list_of_nodes[i].id, "ibss", ssid, frequency
        )
        engine.set_wlan_type(wlan.name, wlan.node_id, "ibss")
        engine.join_ibss(wlan.name, ssid, frequency, wlan.node_id)
        wlans.append(wlan)
    return wlans
