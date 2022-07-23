"""
The default hostapd configurations that are used when a
wireless interface is made a wifi access point.
"""

hostapd_conf = {
    "interface": "wlan0",
    "ssid": "simplewifi",
    "wds_sta": 1,
    "hw_mode": "g",
    "channel": 10,
    "ieee80211d": 1,
    "country_code": "IN",
    "ieee80211n": 1,
    "auth_algs": 1,
    "wpa": 2,
    "wpa_key_mgmt": "WPA-PSK",
    "rsn_pairwise": "CCMP",
    "wpa_passphrase": "123456789a",
}
