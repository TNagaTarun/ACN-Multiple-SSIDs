# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""API related to creation of a wireless station in a wireless network topology"""

import logging

from nest.topology.access_point import AccessPoint
from nest.topology.node import Node
from nest.topology.wireless_interface import WirelessInterface
from nest.topology.wireless_interface import create_adhoc_network, join_adhoc_network, join_bss

logger = logging.getLogger(__name__)


class WifiStation(Node):
    """
    Abstraction for a wireless station,
    that may join a Basic Service Set (BSS) or an Ad-Hoc network.

    Attributes
    ----------
    name: str
        User given name for the station.
    ssid: str
            The SSID of the wireless network associated with the wifi station
    type: str
        Whether the wifi station is part of a `bss` or an `ibss`
    active: boolean
        Whether the wifi station is active i.e, part of an active wireless network or not
    address: str or Address
        The IP address of the Wifi Station.
    """

    def __init__(self, name):
        """
        Create a wireless station with given `name` inside a 'Node'.

        Parameters
        ----------
        name: str
            The name of the wifi station to be created
        """
        super().__init__(name)
        self._ssid = ""
        self._type = ""
        self._active = False
        self._address = ""

    @property
    def ssid(self):
        """
        Getter for the SSID of the wireless network 
        associated with the wifi station
        """
        return self._ssid
    
    @property
    def address(self):
        """
        Getter for the IP address associated
        with the wifi station
        """
        return self._address

    @address.setter
    def address(self, address):
        """
        Assigns IP address to the access point

        Parameters
        ----------
        address : Address or str
            IP address to be assigned to the interface
        """
        self._address = address

    def set_address(self, address):
        """
        Assigns IP address to the access point

        Parameters
        ----------
        address : Address or str
            IP address to be assigned to the interface
        """
        self._address = address

    def join_bss(self, ap: AccessPoint, configs={}):
        """
        Function for the wifi station to join a BSS network, specified by the given AP

        PARAMETERS
        ----------
        ap: AccessPoint
            The access point whose network the station should join
        configs: dict
            An optional python dictionary that holds values of various configuration parameters
            like 'key_mgmt', 'psk' etc. In its absence, default values are used.

        RETURNS
        -------
        WirelessInterface 
            Returns the Wireless Interface object that is installed in the Wifi Station.
            This object may be used for setting IP address to the AP, and for routing purposes.
        """

        if not ap.active:
            raise ValueError("The Access Point that you have specified is not active.")

        if self._address == "":
            raise ValueError(f"IP address of the station {self.id} is not set.")

        [self._sta_wlan] = join_bss(self, ap, configs)

        self._sta_wlan.address = self._address
        self._ssid = ap.ssid 
        self._active = True
        self._type = "bss"

        return self._sta_wlan

    def start_adhoc_network(self, ssid, frequency=2412):
        """
        Function for the wifi station to start an Ad Hoc network
        with the given SSID and frequency.

        PARAMETERS
        ----------
        ssid: str
            The SSID of the adhoc network to be formed
        frequency: int
            The frequency of the channel in which the network should operate

        RETURNS
        -------
        WirelessInterface 
            Returns the Wireless Interface object that is installed in the Wifi Station.
            This object may be used for setting IP address to the AP, and for routing purposes.
        """

        if self._address == "":
            raise ValueError(f"IP address of the station {self.id} is not set.")

        [self._sta_wlan] = create_adhoc_network(self, ssid, frequency)
        self._sta_wlan.address = self._address
        self._ssid = ssid 
        self._active = True
        self._type = "bss"

        return self._sta_wlan

    def join_adhoc_network(self, ssid, frequency=2412):
        """
        Function for the wifi station to join an Ad Hoc network
        with the given SSID and frequency.

        PARAMETERS
        ----------
        ssid: str
            The SSID of the adhoc network to be formed
        frequency: int
            The frequency of the channel in which the network should operate

        RETURNS
        -------
        WirelessInterface 
            Returns the Wireless Interface object that is installed in the Wifi Station.
            This object may be used for setting IP address to the AP, and for routing purposes.
        """

        if self._address == "":
            raise ValueError(f"IP address of the station {self.id} is not set.")

        [self._sta_wlan] = join_adhoc_network(self, ssid, frequency)
        self._sta_wlan.address = self._address
        self._ssid = ssid 
        self._active = True
        self._type = "ibss"

        return self._sta_wlan
        

    def leave_network(self):
        """
        Function for the wifi station to leave the wireless network that it is part of.
        """

        if not self._active:
            raise ValueError("The wifi station is not part of any wireless network.")

        WirelessInterface.leave_network(self.id)
        self._ssid = ""
        self._active = False
        self._type = ""