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
from UI import UiDialog

PORT = 9000
BUFF = 1024
COUNT = 500
cmd = 'netsh wlan show interfaces'
the_mac = 'ec-62-60-fe-81-98'


class Mine(UiDialog, QMainWindow):

    def __init__(self=None, parent=None):
        super(Mine, self).__init__(parent)

        self.data_list = [np.random.uniform(1, 500) for _ in range(COUNT)]
        self.filename = ""
        self.array = deque(maxlen=COUNT)
        self.new_data = deque()
        self.setup_ui(self)
        self.setCentralWidget(self.main_widget)
        self.enable = False
        self.pushButton_start.clicked.connect(self.fun_pushbutton_start)
        self.pushButton_close.clicked.connect(self.fun_pushbutton_close)
        self.pushButton_data.clicked.connect(self.fun_pushbutton_data)
        self.pushButton_link.clicked.connect(self.fun_pushbutton_link)
        self.set_plot()
        self.check_link = False

    def fun_pushbutton_start(self):
        global client
        self.enable = True
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.enable:
            self.filename = time_name()
            print(self.enable)
            client.connect((HOST, PORT))
            self.textEdit.setText('开启中')
            self.start(client)
        else:
            self.textEdit.setText('请先连接正确的设备')
        print(self.enable)

    def fun_pushbutton_close(self):
        self.enable = False
        client.close()
        self.receive_timer.stop()
        self.textEdit.setText('已关闭')

    def fun_pushbutton_data(self):
        with open(self.filename, 'r') as f:
            reader = csv.reader(f)
            list_data = list(reader)
            f.close()
        for i in range(len(list_data)):
            list_data[i] = float(list_data[i][0])

        all_plt = pg.plot()
        all_plt.setXRange(0, 2000)
        all_plt.showGrid(x=True, y=True)
        all_plt.plot(list_data, pen='w')

    def fun_pushbutton_link(self):
        global HOST
        output = subprocess.check_output(cmd, shell=True).decode('gbk')
        ssid = re.search('SSID\\s+:\\s(.+)', output)
        ssid = ssid.group(1)[:-1]
        print(ssid)
        if ssid == 'wyc':
            self.textEdit.setText('连接中，请稍后')
            self.textEdit.repaint()
            text_ip = self.textEdit_2.toPlainText()
            print(text_ip.isspace())
            HOST = text_ip
            self.textEdit.setText(f'''连接设备IP:{HOST}''')
        else:
            self.textEdit.setText(f'''请连接正确的wifi,当前{ssid}''')

    def start(self, client):
        # while self.enable:
        #     try:
        #         array = receive_data(client)
        #         # draw_matplotlib(array,self.ax,self.fig)
        #
        #         print(self.enable)
        #
        #     except Exception as e:
        #         client.connect((HOST, PORT))
        #         print(e)

        self.receive_timer = QtCore.QTimer(self)
        self.receive_timer.timeout.connect(self.pyqtgraph_start)
        self.receive_timer.start(9)

    def set_plot(self):
        # # 创建画布
        # self.fig=plt.figure()
        #
        # self.canvas=FigureCanvasQTAgg(self.fig)
        # # 画布放进widget组件，设定位置
        # self.vlayout=QVBoxLayout()
        # self.vlayout.addWidget(self.canvas)
        # self.widget.setLayout(self.vlayout)
        # #初始化matplotlib显示区域
        # self.ax=self.fig.add_subplot(111)

        pg.setConfigOptions(antialias=True)
        self.layout = QtWidgets.QGridLayout(self.widget_plot)
        self.plot_plt = pg.PlotWidget(self.widget_plot)
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
        self.array = receive_data(client, self.filename)
        self.array = moving_average(self.array, 20)
        self.plot_plt.setXRange(0, 5000)
        self.plot_plt.clearPlots()
        self.plot_plt.plot().setData(self.array, pen='w')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Mine()
    window.show()
    sys.exit(app.exec())
