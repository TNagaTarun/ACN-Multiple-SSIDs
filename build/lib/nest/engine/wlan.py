# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Wireless Interface management"""

from .exec import exec_subprocess, exec_async_commands


def load_hwsim(count):
    """
    Creates specified number of wireless interfaces in the linux kernel,
    by loading the mac80211_hwsim module.

    Parameters
    ----------
    count : int
        Number of wireless interfaces to be created.
    """

    exec_subprocess(f"modprobe mac80211_hwsim radios={count}")


def unload_hwsim():
    """
    Unloads the mac80211_hwsim module,
    deletes all the wireless interfaces in the kernel.
    """

    exec_subprocess("modprobe -r mac80211_hwsim")


def get_phy_dev_number(interface_name, node_name=None):
    """
    Returns the physical device number corresponding to the wireless interface.

    Parameters
    ----------
    interface_name: str
        Name of the wireless interface.
    node_name: str/None
        Name of the network namespace contaning the wireless interface.
        `None` if it is in the default namespace.
    """

    if node_name is None:
        output = exec_subprocess(f"iw dev {interface_name} info", output=True)
    else:
        output = exec_subprocess(
            f"ip netns exec {node_name} iw dev {interface_name} info", output=True
        )

    # The above linux command gives various information about the interface
    # And the physical device number is present alongside an attribute called 'wiphy'
    output_split = output.split()
    phy_number = int(output_split[output_split.index("wiphy") + 1])
    return phy_number


def get_mac_address(interface_name):
    """
    Returns the MAC address of the wireless interface.

    Parameters
    ----------
    interface_name: str
        Name of the wireless interface.
    """

    output = exec_subprocess(f"iw dev {interface_name} info", output=True)
    # The above linux command gives various information about the interface
    # And the MAC address is present alongside an attribute called 'addr'
    output_split = output.split()
    mac_address = output_split[output_split.index("addr") + 1]
    return mac_address


def shift_wlan_to_ns(node_name, phy_number):
    """
    Shifts the specified wireless interface into the specified node.

    Parameters
    ----------
    node_name: str
        Name of the network namespace.
    phy_number: int
        Physical device number corresponding to the wireless interface.
    """

    exec_subprocess(f"iw phy phy{phy_number} set netns name {node_name}")


def shift_wlan_to_root(node_name, phy_number):
    """
    Shifts the specified wireless interface from the specified node to the default namespace.

    Parameters
    ----------
    node_name: str
        Name of the network namespace.
    phy_number: int
        Physical device number corresponding to the wireless interface.
    """

    exec_subprocess(f"ip netns exec {node_name} iw phy phy{phy_number} set netns 1")


def start_bss(interface_name, node_name):
    """
    Starts  bss from the specified node using the hostapd module

    Parameters
    ----------
    interface_name: str
        Name of the the interface where the BSS has to be initilized
    node_name: str
        Name of the network namespace.
    """

    exec_async_commands(
        f"ip netns exec {node_name} hostapd hostapd_{interface_name}.conf"
    )


def join_bss(bssid, interface_name, node_name):
    """
    Connects the node to the given bss network using the wpa_supplicant module

    Parameters
    ----------
    interface_name: str
        Name of the the interface which is joining the bss
    bssid: str
        MAC address of the interface to which this node is connecting
    node_name: str
        Name of the network namespace.
    """

    exec_async_commands(
        f"ip netns exec {node_name} wpa_supplicant -i {interface_name} -c wpa_supplicant_{bssid}.conf"  # pylint: disable=line-too-long
    )


def join_ibss(interface_name, ssid, frequency, node_name):
    """
    Adds the given interface to the ad_hoc netwrok

    Parameters
    ----------
    interface_name: str
        Name of the interface which is joining the bss
    ssid: str
        ssid of the interface to which this node is connecting
    frequency: int
        frequency of the ibss network
    node_name: str
        Name of the network namespace.
    """

    exec_subprocess(
        f"ip netns exec {node_name} iw dev {interface_name} ibss join {ssid} {frequency}"
    )


def leave_ibss(interface_name, node_name):
    """
    Makes the given wireless interface leave its ad hoc network.

    Parameters
    ----------
    interface_name: str
        Name of the interface which is leaving its IBSS
    node_name: str
        Name of the network namespace containing the interface
    """

    exec_subprocess(f"ip netns exec {node_name} iw dev {interface_name} ibss leave")


def set_wlan_type(interface_name, node_name, wlan_type):
    """
    Sets the `type` of the given wireless interface.

    Parameters
    ----------
    interface_name: str
        Name of the interface whose type is to be set
    node_name: str
        Name of the network namespace containing the interface
    wlan_type: str
        The type to be set for the wireless interface
    """

    exec_subprocess(
        f"ip netns exec {node_name} iw dev {interface_name} set type {wlan_type}"
    )
