# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""API related to wireless devices in topology"""

import logging
from nest import config
from nest.topology.device import Device

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

        # The `id` of a wlan Device must be same as its `name`.
        # This is achieved when the "asssign_random_names" config is set to False
        assign_random_names = config.get_value("assign_random_names")
        if assign_random_names:
            config.set_value("assign_random_names", False)
        super().__init__(name, node_id)
        if assign_random_names:
            config.set_value("assign_random_names", True)

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
        return super().get_address()

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

    @type.setter
    def type(self, type):  # pylint: disable=redefined-builtin
        """
        Setter for the type of the wireless interface
        """
        self._type = type

    @frequency.setter
    def frequency(self, freq):
        """
        Setter for the frequency in MHz of the wireless interface
        """
        self._frequency = freq

    @ssid.setter
    def ssid(self, ssid):
        """
        Setter for the SSID that the wireless interface is part of
        """
        self._ssid = ssid
