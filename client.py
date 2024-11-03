"""
Title: client.py
Author: 吴烨辰
LastEditors: 高迎新
"""
import sys
import re
import csv
import socket
import subprocess

import psutil
import numpy as np
import pyqtgraph as pg

from collections import deque

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication

from fun import time_name, receive_data, moving_average
from Ui import UiDialog

PORT = 9000
BUFF = 1024
COUNT = 500
cmd = 'netsh wlan show interfaces'
the_mac = 'ec-62-60-fe-81-98'


class Mine(UiDialog, QMainWindow):

    def __init__(self=None, parent=None):
        super(Mine, self).__init__(parent)

        # Network related
        self.host = ''
        self.client = None
        self.enable = False

        # Timer related
        self.timer = None
        self.receive_timer = None

        # Plot related
        self.plot_plt = None
        self.layout = None

        # Data related
        self.data_list = [np.random.uniform(1, 500) for _ in range(COUNT)]
        self.array = deque(maxlen=COUNT)
        self.new_data = deque()
        self.filename: str = ""

        # UI setup
        self.setup_ui(self)
        self.setCentralWidget(self.main_container)

        # Button connections
        self.start_button.clicked.connect(self.fun_pushbutton_start)
        self.stop_button.clicked.connect(self.fun_pushbutton_close)
        self.data_button.clicked.connect(self.fun_pushbutton_data)
        self.connect_button.clicked.connect(self.fun_pushbutton_link)

        # Initial setup
        self.set_plot()

    def fun_pushbutton_start(self):
        self.enable = True
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.enable:
            self.filename = time_name()
            print(self.enable)
            self.client.connect((self.host, PORT))
            self.textEdit.setText('开启中')
            self.start()
        else:
            self.textEdit.setText('请先连接正确的设备')
        print(self.enable)

    def fun_pushbutton_close(self):
        self.enable = False
        self.client.close()
        self.receive_timer.stop()
        self.textEdit.setText('已关闭')

    def fun_pushbutton_data(self):
        with open(self.filename, 'r') as f:
            reader = csv.reader(f)
            data_list = [float(row[0]) for row in reader if row]

        all_plt = pg.plot()
        all_plt.setXRange(0, 2000)
        all_plt.showGrid(x=True, y=True)
        all_plt.plot(data_list, pen='w')

    def fun_pushbutton_link(self):
        output = subprocess.check_output(cmd, shell=True).decode('gbk')
        ssid = re.search('SSID\\s+:\\s(.+)', output)
        ssid = ssid.group(1)[:-1]
        print(ssid)
        if ssid == 'wyc':
            self.textEdit.setText('连接中，请稍后')
            self.textEdit.repaint()
            text_ip = self.textEdit_2.toPlainText()
            print(text_ip.isspace())
            self.host = text_ip
            self.textEdit.setText(f'''连接设备IP:{self.host}''')
        else:
            self.textEdit.setText(f'''请连接正确的wifi,当前{ssid}''')

    def start(self):
        self.receive_timer = QtCore.QTimer(self)
        self.receive_timer.timeout.connect(self.pyqtgraph_start)
        self.receive_timer.start(9)

    def set_plot(self):
        pg.setConfigOptions(antialias=True)
        self.layout = QtWidgets.QGridLayout(self.plot_widget)
        self.plot_plt = pg.PlotWidget(self.plot_widget)
        self.plot_plt.showGrid(x=True, y=True)
        self.plot_plt.setLabel('left', '压力值(KPa)')
        self.layout.addWidget(self.plot_plt)

    def timer_start(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.random)
        self.timer.start(1000)

    def get_cpu_info(self):
        cpu = '%0.2f' % psutil.cpu_percent(interval=1)
        self.data_list.append(float(cpu))
        print(float(cpu))
        self.plot_plt.plot().setData(self.data_list, pen='g')

    def random(self):
        num = np.random.uniform(1, 500)
        self.data_list[0:] = self.data_list[1:]
        self.data_list.append(num)
        self.array.append(num)
        self.plot_plt.clearPlots()
        self.plot_plt.plot().setData(self.array, pen='g')

    def pyqtgraph_start(self):
        self.array = receive_data(self.client, self.filename)
        self.array = moving_average(self.array, 20)
        self.plot_plt.setXRange(0, 5000)
        self.plot_plt.clearPlots()
        self.plot_plt.plot().setData(self.array, pen='w')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Mine()
    window.show()
    sys.exit(app.exec())
