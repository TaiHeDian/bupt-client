"""
Title: fun.py
Author: 吴烨辰
LastEditors: 高迎新
"""
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

    save_data(new_data, filename)
    print(data_deque)
    return data_deque


def time_name():
    """
    为 CSV 数据生成基于时间戳的文件名

    Returns
    -------
    str
        文件名格式 './YYYY-MM-DD HH.MM.SS.csv'
    """
    return f"./{datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S')}.csv"


def save_data(data, filename):
    data = np.array(data).reshape(-1, 1)
    try:
        np.savetxt(filename, data, delimiter=',', fmt='%g')
    except Exception as e:
        print(f'保存数据到{filename}时出错: {str(e)}')


def moving_average(data, window_size):
    """
    计算移动平均值

    Parameters
    ----------
    data : array_like
        输入数据数组
    window_size : int
        移动窗口大小

    Returns
    -------
    ndarray
        平滑后的数据数组
    """
    window = np.ones(window_size) / window_size
    return np.convolve(data, window, mode='same')


def wifi_connect(ssid='ESP32', password='123456789', max_retries=3):
    """
    连接到Wi-Fi网络

    Parameters
    ----------
    ssid : str, optional
        网络名称 (默认: 'ESP32')
    password : str, optional
        网络密码 (默认: '123456789') 
    max_retries : int, optional
        最大重试连接次数 (默认: 3)

    Returns
    -------
    bool
        连接成功返回True，失败返回False
    """
    try:
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        iface.disconnect()  # Ensure disconnected from any network
        
        # Configure network profile
        profile = pywifi.Profile()
        profile.ssid = ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = password
        
        # Remove existing profiles and add new one
        iface.remove_all_network_profiles()
        tmp_profile = iface.add_network_profile(profile)
        
        # Try connecting with retries
        for _ in range(max_retries):
            iface.connect(tmp_profile)
            if iface.status() == const.IFACE_CONNECTED:
                return True
        
        return False
        
    except Exception as e:
        print(f"Wi-Fi连接失败: {e}")
        return False
