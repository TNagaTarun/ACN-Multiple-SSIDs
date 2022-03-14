# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to wireless devices in topology"""

import logging
from nest import engine
from nest.topology.device import Device
import nest.global_variables as g_var
from .address import Address

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


class Wlan(Device):
    """
    This is a wireless device, used in wireless interfaces.

    Attributes
    ----------
    node_id : str
        id of the Node to  which this Interface belongs
    address : str/Address
        IP address assigned to this interface
    type : str
        The type of the interface, for example, 'managed', 'AP', 'ibss', etc.
    ssid : str
        The Service Set Identifier (SSID) of the wireless network to which this interface belongs.
    frequency : int
        The channel frequency (MHz) at which the interface communicates.
    mac_address : str
        The 48-bit MAC address of the wireless interface.

    """

    def __init__(self, name, node_id, mac_address, wlan_type, ssid, frequency):
        """
        Constructor of Wlan

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

        super().__init__(name, node_id)
        self._address = None
        self._type = wlan_type
        self._ssid = ssid
        self._frequency = frequency
        self._mac_address = mac_address

    @property
    def address(self):
        """
        Getter for the IP address associated
        with the interface
        """
        return self._address

    @address.setter
    def address(self, address):
        """
        Assigns IP address to an interface

        Parameters
        ----------
        address : Address or str
            IP address to be assigned to the interface
        """
        if isinstance(address, str):
            address = Address(address)

        if self.node_id is not None:
            engine.assign_ip(self.node_id, self.name, address.get_addr())
            self._address = address
        else:
            # TODO: Create our own error class
            raise NotImplementedError(
                "You should assign the interface to node or router before assigning address to it."
            )

        # Global variable to check if address is ipv6 or not for DAD check
        if address.is_ipv6() is True:
            g_var.IS_IPV6 = True

    @property
    def mac_address(self):
        """
        Getter for the MAC address of the wireless interface.
        """
        return self._mac_address

    @property
    def type(self):
        """
        Getter for the type of the wireless interface
        """
        return self._type

    @property
    def frequency(self):
        """
        Getter for the frequency in MHz of the wireless interface
        """
        return self._frequency

    @property
    def ssid(self):
        """
        Getter for the SSID that the wireless interface is part of
        """
        return self._ssid

    @property
    def name(self):
        """
        Getter for the name of the wireless interface, like 'wlan0', 'wlan1' etc.
        """
        return super().name

    @property
    def node_id(self):
        """
        Getter for the id of the node that the wireless interface is present in.
        """
        return super().node_id
