import struct
import datetime

from collections import deque

import pywifi
import numpy as np
from pywifi import const

font = {
    'family': 'serif',
    'weight': 'normal',
    'rotation': '0',
    'size': 16}
data_deque = deque(maxlen=5000)
count = 10
new_data = [0] * count


def receive_data(client, filename):
    receive = client.recv(2 * count)
    for i in range(count):
        unpack_data = struct.unpack('H', receive[i * 2:i * 2 + 2])[0]
        force_value = ((1 - unpack_data / 4095) * 3.3 / 10000) * 2.8889 * 1000000 + 17.0411
        data_deque.append(force_value)
        new_data[i] = force_value

    save(new_data, filename)
    print(data_deque)
    return data_deque


def time_name():
    now = datetime.datetime.now()
    now_str = str(now)
    now_str = now_str.replace(':', '.')
    now_str = now_str[:18]
    fp = 'output/' + f'''{now_str}.csv'''
    return fp


def save(data, filename):
    data = np.array(data).reshape(-1, 1)
    np.savetxt(filename, data, delimiter=',', fmt='%g')


def moving_average(interval, window_size):
    window = np.ones(int(window_size)) / float(window_size)
    re = np.convolve(interval, window, 'same')
    return re


def wifi_connect():
    ssid = 'ESP32'
    password = '123456789'
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.disconnect()
    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = password
    iface.remove_all_network_profiles()
    tmp_profile = iface.add_network_profile(profile)
    iface.connect(tmp_profile)
    iface.disconnect()
    iface.connect(tmp_profile)
    return iface.status() == const.IFACE_CONNECTED
