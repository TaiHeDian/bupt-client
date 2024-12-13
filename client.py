from socket import *
from fun import *
from UI import *
import sys
from PyQt5.QtWidgets import QMainWindow
import pyqtgraph as pg
from PyQt5 import QtCore
import psutil
import traceback
from get_ip import *
import re

PORT = 9000
BUFSIZ = 1024
count = 500
cmd = 'netsh wlan show interfaces'
the_mac = 'ec-62-60-fe-81-98'


class mine(Ui_Dialog, QMainWindow):

    def __init__(self):
        super(mine, self).__init__()
        self.data_list = [np.random.uniform(1, 500) for i in range(500)]
        self.filename = str()
        self.array = deque(maxlen=500)
        self.new_data = deque()
        self.setupUi(self)
        self.setCentralWidget(self.main_widget)
        self.enable = False
        self.start_button.clicked.connect(self.fun_pushbutton)
        self.stop_button.clicked.connect(self.fun_pushbutton_close)
        self.data_button.clicked.connect(self.fun_pushbutton_2)
        self.connect_button.clicked.connect(self.fun_pushbutton_checklink)
        self.set_plot()
        self.checklink = False

    def fun_pushbutton(self):
        global client
        self.enable = True
        client = socket.socket(AF_INET, SOCK_STREAM)
        if self.enable == True:
            self.filename = time_name()

            try:
                print(self.enable)
                client.connect((HOST, PORT))
                self.status_field.setText('开启中')
                self.start(client)
            except Exception as e:
                self.status_field.setText('连接失败')
                print(e)


        self.status_field.setText('请先连接正确的设备')
        print(self.enable)

    def fun_pushbutton_close(self):
        self.enable = False

        try:
            client.close()
            self.receive_timer.stop()
            self.status_field.setText('已关闭')
        except Exception as e:
            self.status_field.setText('已关闭')
            print(e)


    def fun_pushbutton_2(self):
        pass
        # TODO: Open data folder

    def fun_pushbutton_checklink(self):
        global HOST
        output = subprocess.check_output(cmd, shell=True).decode('gbk')
        ssid = re.search('SSID\\s+:\\s(.+)', output)
        ssid = ssid.group(1)[:-1]
        print(ssid)
        if ssid == 'wyc':
            self.status_field.setText('连接中，请稍后')
            self.status_field.repaint()
            text_ip = self.input_field.toPlainText()
            print(text_ip.isspace())
            HOST = text_ip
            self.status_field.setText(f'''连接设备IP:{HOST}''')
        else:
            self.status_field.setText(f'''请连接正确的wifi,当前{ssid}''')

    def start(self, client):
        '''
        while self.enable==True:
            try:
                array=receive_data(client)
                # draw_matplotlib(array,self.ax,self.fig)

                print(self.enable)

            except Exception as e:
                client.connect((HOST, PORT))
                print(e)
        '''
        self.receive_timer = QtCore.QTimer(self)
        self.receive_timer.timeout.connect(self.pyqtgraph_start)
        self.receive_timer.start(9)

    def set_plot(self):
        '''

        # 创建画布
        self.fig=plt.figure()

        self.canvas=FigureCanvasQTAgg(self.fig)
        # 画布放进widget组件，设定位置
        self.vlayout=QVBoxLayout()
        self.vlayout.addWidget(self.canvas)
        self.widget.setLayout(self.vlayout)
        #初始化matplotlib显示区域
        self.ax=self.fig.add_subplot(111)
        '''
        pg.setConfigOptions(leftButtonPan=True, antialias=True)
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

        try:
            cpu = '%0.2f' % psutil.cpu_percent(interval=1)
            self.data_list.append(float(cpu))
            print(float(cpu))
            self.plot_plt.plot().setData(self.data_list, pen='g')
        except Exception as e:
            print(traceback.print_exc())


    def random(self):
        num = np.random.uniform(1, 500)
        self.data_list[0:] = self.data_list[1:]
        self.data_list.append(num)
        self.array.append(num)
        self.plot_plt.clearPlots()
        self.plot_plt.plot().setData(self.array, pen='g')

    def pyqtgraph_start(self):

        try:
            self.array = receive_data(client, self.filename)
            self.array = moving_average(self.array, 20)
            self.plot_plt.setXRange(0, 5000)
            self.plot_plt.clearPlots()
            self.plot_plt.plot().setData(self.array, pen='w')
        except Exception as e:
            print(e)


app = QtWidgets.QApplication(sys.argv)
dialog = mine()
dialog.show()
sys.exit(app.exec_())
