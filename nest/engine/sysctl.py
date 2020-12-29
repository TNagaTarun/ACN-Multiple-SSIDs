# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Sysctl commands"""

from .exec import exec_subprocess

def en_ip_forwarding(ns_name, ipv6=False):
    """
    Enables ip forwarding in a namespace. Used for routers

    Parameters
    ----------
    ns_name : str
        namespace name
    """
    if ipv6:
        exec_subprocess(f'ip netns exec {ns_name} sysctl -w net.ipv6.conf.all.forwarding=1')
    else:
        exec_subprocess(f'ip netns exec {ns_name} sysctl -w net.ipv4.ip_forward=1')

def disable_dad(ns_name, int_name):
    """
    Disables DAD at nodes for IPv6 Addressing

    Parameters
    ----------
    ns_name : str
        namespace name
    int_name : str
        interface name
    """
    exec_subprocess(f'ip netns exec {ns_name} sysctl -w net.ipv6.conf.{int_name}.accept_dad=0')

def configure_kernel_param(ns_name, prefix, param, value):
    """
    Configure kernel parameters using sysctl

    Parameters
    ----------
    ns_name : str
        name of the namespace
    prefix : str
        path for the sysctl command
    param : str
        kernel parameter to be configured
    value : str
        value of the parameter
    """
    exec_subprocess(f'ip netns exec {ns_name} sysctl -q -w {prefix}{param}={value}')


def read_kernel_param(ns_name, prefix, param):
    """
    Read kernel parameters using sysctl

    Parameters
    ----------
    ns_name : str
        name of the namespace
    prefix : str
        path for the sysctl command
    param : str
        kernel parameter to be read

    Returns
    -------
    str
        value of the `param`
    """
    value = exec_subprocess(f'ip netns exec {ns_name} sysctl -n {prefix}{param}', output=True)
    return value.rstrip('\n')
