# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

class WirelessTopologyMap:
    """
    Stores the list of all wireless networks created, and the interfaces which are part of them
    """

    wireless_topology_map = {"bss": [], "ibss": []}

    @staticmethod
    def create_ibss(ssid):
        """
        Add an IBSS to the wireless topology map. 

        Parameters
        ----------
        ssid : str
            SSID of the IBSS to add.
        """

        ibss_networks = WirelessTopologyMap.get_ibss_networks()

        ibss_networks.append({"ssid": ssid, "stations": []})

    @staticmethod
    def add_station_to_ibss(ssid, wlan):
        """
        Add a station to an IBSS

        Parameters
        ----------
        ssid : str
            SSID of the IBSS to which the station is to be added.
        wlan : WirelessInterface
            The wireless interface to be added into the IBSS        
        """

        ibss_networks = WirelessTopologyMap.get_ibss_networks()
        for ibss in ibss_networks:
            if ibss["ssid"] == ssid:
                ibss["stations"].append(wlan)
                break

    @staticmethod
    def create_bss(ssid, ap):
        """
        Add a new BSS to the wireless topology map.

        Parameters
        ----------
        ssid : str
            SSID of the BSS to add.
        ap : WirelessInterface
            The interface that is acting as access point for the BSS
        """

        bss_networks = WirelessTopologyMap.get_bss_networks()
        bss_networks.append({"ssid": ssid, "ap": ap, "stations": []})

    @staticmethod
    def add_station_to_bss(ap, wlan):
        """
        Add a station to a BSS

        Parameters
        ----------
        ap : str
            The name of the access point to which the station is to be added.
        wlan : WirelessInterface
            The wireless interface to be added into the BSS
        """

        bss_networks = WirelessTopologyMap.get_bss_networks()
        for bss in bss_networks:
            if bss["ap"].node_id == ap:
                bss["stations"].append(wlan)
                break

    @staticmethod
    def remove_station_from_ibss(wlan):
        """
        Remove a station from an IBSS

        Parameters
        ----------
        wlan : WirelessInterface
            The wireless interface to be removed from the IBSS
        """
        ibss_networks = WirelessTopologyMap.get_ibss_networks()
        for ibss in ibss_networks:
            if wlan in ibss["stations"]:
                ibss["stations"].remove(wlan)
                # Remove the IBSS if no more stations are present
                if len(ibss["stations"]) == 0:
                    WirelessTopologyMap.remove_ibss(ibss["ssid"])
                break


    @staticmethod
    def remove_station_from_bss(wlan):
        """
        Remove a station from a BSS

        Parameters
        ----------
        wlan : WirelessInterface
            The wireless interface to be removed from the BSS
        """
        bss_networks = WirelessTopologyMap.get_bss_networks()

        for bss in bss_networks:
            if wlan in bss["stations"]:
                bss["stations"].remove(wlan)
                break


    @staticmethod
    def remove_ibss(ssid):
        """
        Remove an IBSS from the topology

        Parameters
        ----------
        ssid : str
            SSID of the IBSS to be removed
        """
        ibss_networks = WirelessTopologyMap.get_ibss_networks()
        for ibss in ibss_networks:
            if ibss["ssid"] == ssid:
                ibss_networks.remove(ibss)
                break
        

    @staticmethod
    def remove_bss(ap):
        """
        Remove a BSS from the topology

        Parameters
        ----------
        ap : WirelessInterface
            The access point of the BSS to be removed
        """
        bss_networks = WirelessTopologyMap.get_bss_networks()
        for bss in bss_networks:
            if bss["ap"] == ap:
                bss_networks.remove(bss)
                break

    @staticmethod
    def return_ap(ssid):
        """
        Checks if a BSS of the given SSID exists, and if it does, return it AP.

        Parameters
        ----------
        ssid : str
            The SSID of the BSS

        Returns
        -------
        The WirelessInterface object corresponding to the AP of the BSS.
        'None' if no BSS of the given SSID exists
        """
        bss_networks = WirelessTopologyMap.get_bss_networks()
        for bss in bss_networks:
            if bss["ssid"] == ssid:
                return bss["ap"]

        return None

    @staticmethod
    def ibss_exists(ssid):
        """
        To check if an IBSS with the given SSID exists

        Parameters
        ----------
        ssid : str
            The SSID of the IBSS to be searched
        """
        ibss_networks = WirelessTopologyMap.get_ibss_networks()
        for ibss in ibss_networks:
            if ibss["ssid"] == ssid:
                return True

        return False
    
    @staticmethod
    def is_ap(node_id):
        """
        To check if the given node is an AP

        Parameters
        ----------
        node_id : str
            The name of the node to check

        Returns
        -------
        boolean - True if the given node is an AP of a BSS, false otherwise
        WirelessInterface - The object corresponding to the AP if True, None otherwise
        """
        bss_networks = WirelessTopologyMap.get_bss_networks()
        for bss in bss_networks:
            if bss["ap"].node_id == node_id:
                return True, bss["ap"]
        return False, None

    @staticmethod
    def is_bss_station(node_id):
        """
        To check if the given node is a BSS station

        Parameters
        ----------
        node_id : str
            The name of the node to check

        Returns
        -------
        boolean - True if the given node is part of a BSS, false otherwise
        WirelessInterface - The object corresponding to the station if True, None otherwise
        """
        bss_networks = WirelessTopologyMap.get_bss_networks()
        for bss in bss_networks:
            for wlan in bss["stations"]:
                if wlan.node_id == node_id:
                    return True, wlan
        return False, None

    @staticmethod
    def is_ibss_station(node_id):
        """
        To check if the given node is an IBSS station

        Parameters
        ----------
        node_id : str
            The name of the node to check

        Returns
        -------
        boolean - True if the given node is part of an IBSS, false otherwise
        WirelessInterface - The object corresponding to the station if True, None otherwise
        """
        ibss_networks = WirelessTopologyMap.get_ibss_networks()
        for ibss in ibss_networks:
            for wlan in ibss["stations"]:
                if wlan.node_id == node_id:
                    return True, wlan
        return False, None

    @staticmethod
    def is_part_of_network(node_id):
        """
        Check if the given node is part of any wireless network.

        Parameters
        ----------
        node_id : str
            The name of the node to check

        Returns
        -------
        boolean - True if the given node is part of a wireless network, false otherwise
        """
        if WirelessTopologyMap.is_ap(node_id)[0]:
            return True

        elif WirelessTopologyMap.is_bss_station(node_id)[0]:
            return True

        elif WirelessTopologyMap.is_ibss_station(node_id)[0]:
            return True

        return False
        
    @staticmethod
    def get_bss_stations(ap):
        """
        Returns a list of all the BSS stations connected to the given AP

        Parameters
        ----------
        ap : WirelessInterface
            name of the access point

        Returns
        -------
        WirelessInterface[] : A list of WirelessInterface objects 
        corresponding to the stations in the BSS having the given AP
        """
        bss_networks = WirelessTopologyMap.get_bss_networks()
        for bss in bss_networks:
            if bss["ap"] == ap:
                return bss["stations"]

    @staticmethod
    def get_ibss_networks():
        """
        Get all the IBSS networks in the topology.
        """

        return WirelessTopologyMap.wireless_topology_map["ibss"]

    @staticmethod
    def get_bss_networks():
        """
        Get all the BSS networks in the topology.
        """

        return WirelessTopologyMap.wireless_topology_map["bss"]