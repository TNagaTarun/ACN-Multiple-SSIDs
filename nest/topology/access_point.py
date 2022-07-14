# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""API related to access point creation in a wireless network topology"""

import logging

from nest.topology.node import Node
from nest.topology.interface.wireless_interface import create_ap

logger = logging.getLogger(__name__)


class AccessPoint(Node):
    """
    Abstraction for a wireless access point.

    Attributes
    ----------
    name: str
        User given name for the AP.
    ssid: str
        The SSID of the BSS associated with the AP.
    configs: dict
        A dictionary holding the hostapd parameters for configuring the Access Point.
    address: str or Address
        The IP address of the Access Point.
    """

    def __init__(self, name):
        """
        Create a wireless access point with given `name` inside a 'Node'.

        Parameters
        ----------
        name: str
            The name of the access point to be created
        """
        super().__init__(name)
        self._ssid = "MyBSS"
        self._configs = {}
        self._address = ""
        self._ap_wl_int = None

    @property
    def ssid(self):
        """
        Getter for the SSID of the BSS network
        associated with the Access Point
        """
        return self._ssid

    @property
    def configs(self):
        """
        Getter for the hostapd configs
        associated with the Access Point
        """
        return self._configs

    @property
    def address(self):
        """
        Getter for the IP address associated
        with the access point
        """
        return self._address

    def set_ssid(self, ssid):
        """
        To set the SSID of the BSS network.

        Parameters
        ----------
        ssid: str
            The SSID to be set for the BSS network
        """
        self._ssid = ssid

    def set_configs(self, configs):
        """
        To set the hostapd configs for the Access Point

        Parameters
        ----------
        configs: dict
            A dictionary holding the hostapd configs for the Access Point
        """
        self._configs = configs

    def set_address(self, address):
        """
        Assigns IP address to the access point

        Parameters
        ----------
        address : Address or str
            IP address to be assigned to the interface
        """
        self._address = address
        if self._ap_wl_int is not None:
            self._ap_wl_int.set_address(address)

    def start(self):
        """
        Installs a wireless interface in the Access Point, activates the access point
        and starts a BSS network, into which other wifi stations can connect.

        Returns
        -------
        WirelessInterface
            Returns the Wireless Interface object that is installed in the Access Point.
            This object may be used for setting IP address to the AP, and for routing purposes.
        """

        self._ap_wl_int = create_ap(self, self._ssid, self._configs)
        if self._address != "":
            self._ap_wl_int.set_address(self._address)

        return self._ap_wl_int

    def stop(self):
        """
        The node stops acting as an Access Point,
        and the BSS network associated with it gets dissolved.
        """

        self._ap_wl_int.delete_ap(self.name)
