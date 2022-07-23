"""
The default wpa_supplicant configurations that are used when a
wireless interface is made to join a BSS.
"""

WPA_SUPPLICANT_CONF = """network={
    bssid=02:00:00:00:00:00
    key_mgmt=WPA-PSK
    psk="123456789a"
}"""
