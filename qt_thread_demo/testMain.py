# coding: utf-8

# refer: https://muyuuuu.github.io/2021/02/05/PyQt5-QThread/

#导入程序运行必须模块
import sys
#PyQt5中使用的基本控件都在PyQt5.QtWidgets模块中
import time

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
#导入designer工具生成的login模块
from test import Ui_MainWindow

class MyMainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        # self.pushButton.clicked.connect(self.onClick)
        self.pushButton.clicked.connect(self.onClick)
        self.worker = myThread()
        self.worker.signal_out.connect(self.display)


    def onClick(self):
        # self.textBrowser.append('1')
        self.worker.start()
        # thread.signal_out.connect(self.display)

    def display(self, value):
        # QApplication.processEvents()
        self.textBrowser.append(value)

class myThread(QThread):
    signal_out = pyqtSignal(str)
    def __init__(self):
        super(myThread, self).__init__()
        self.working = True
        self.finished.connect(self.finish)


    def finish(self):
        print('finish')
        self.working = False

    def run(self):
        print('i am running')
        i = 0
        while self.working:
            self.sleep(1)
            i = i + 1
            print(i)
            self.signal_out.emit(f'{i}')
            if i == 10:
                self.working = False

if __name__ == "__main__":
    #固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
    app = QApplication(sys.argv)
    #初始化
    myWin = MyMainForm()
    #将窗口控件显示在屏幕上
    myWin.show()
    #程序运行，sys.exit方法确保程序完整退出。
    sys.exit(app.exec_())
