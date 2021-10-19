import socket
from os import getlogin
from PIL import Image
import io
import numpy as np
from random import randint
import pyautogui
from threading import Thread
import win32api as win
# PyQt5
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QPushButton, QAction, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect, Qt


print("[SERVER]: STARTED")
sock = socket.socket()
sock.bind(('192.168.31.186', 9091))  # Your Server
sock.listen()
print(sock.getsockname())
conn, addr = sock.accept()

class Dekstop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def ChangeImage(self):
        try:
            print("[SERVER]: CONNECTED: {0}!".format(addr[0]))
            screenSize = conn.recv(1024)
            print(screenSize)
            screenSize = screenSize.decode()
            self.setGeometry(QRect(pyautogui.size()[0] // 4, pyautogui.size()[1] // 4, eval(screenSize)[0] // 2, eval(screenSize)[1] // 2))
            self.setFixedSize(self.width(), self.height())
            while True:
                img_bytes = conn.recv(999999)
                self.pixmap.loadFromData(img_bytes)
                self.label.setScaledContents(True)
                self.label.resize(self.width(), self.height())
                self.label.setPixmap(self.pixmap)
                click = win.GetKeyState(0x01)
                if click < 0:
                    x, y = pyautogui.position()
                    win_x,win_y,win_width,win_height = self.frameGeometry().x(), self.frameGeometry().y(), self.frameGeometry().width(), self.frameGeometry().height()
                    if win_x<=x<=win_x+win_width and win_y<=y<=win_y+win_height:
                        x = x-win_x
                        y = y-win_y
                        positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
                        print(positionStr)
                        # command = str([click, x*2, y*2])
                        # conn.send(command.encode())
        except ConnectionResetError:
            QMessageBox.about(self, "ERROR", "[SERVER]: The remote host forcibly terminated the existing connection!")
            conn.close()

    def initUI(self):
        self.pixmap = QPixmap()
        self.label = QLabel(self)
        self.label.resize(self.width(), self.height())
        self.setWindowTitle("[SERVER] Remote Desktop: " + str(randint(99999, 999999)))
        self.setGeometry(QRect(pyautogui.size()[0] // 4, pyautogui.size()[1] // 4, 800, 400))
        self.setFixedSize(self.width(), self.height())

        self.start = Thread(target=self.ChangeImage, daemon=True)
        self.start.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Dekstop()
    ex.show()
    sys.exit(app.exec())
