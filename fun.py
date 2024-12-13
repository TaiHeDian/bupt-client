import csv
import datetime
from collections import deque
import struct
import pywifi
from matplotlib import pyplot as plt
from pywifi import const
import numpy as np

font = {
    'family': 'serif',
    'weight': 'normal',
    'rotation': '0',
    'size': 16}
data_deque = deque(maxlen=5000)
count = 10
new_data = [0 for i in range(count)]


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


def draw_matplotlib(array, ax, fig):
    ax.set_ylabel('kPa', fontdict=font, loc='top', x=100)
    ax.plot(array)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.cla()


def draw_pyqtgraph(array, plot):
    plot.plot().setData(array, pen='r')


def time_name():
    now = datetime.datetime.now()
    now_str = str(now)
    now_str = now_str.replace(':', '.')
    now_str = now_str[:18]
    fp = './' + f'''{now_str}.csv'''
    return fp


def save(data, filename):
    data = list(map((lambda x: [x]), data))

    try:
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
    except Exception as e:
        print(f'保存数据到{filename}时出错: {str(e)}')


def moving_average(interval, windowsize):
    window = np.ones(int(windowsize)) / float(windowsize)
    re = np.convolve(interval, window, 'same')
    return re


def wifi_connect():
    SSID = 'ESP32'
    password = '123456789'
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.disconnect()
    profile = pywifi.Profile()
    profile.ssid = SSID
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
