from socket import *
from PIL import ImageGrab, Image, ImageChops
import io
import numpy as np
from random import randint
import time
import pyautogui
from threading import Thread
import sys
import win32api as win
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QPushButton, QAction, QMessageBox, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect, Qt


class Desktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def StartThread(self):
        self.start.start()

    def ChangeImage(self):
        try:
            if len(self.ip.text()) != 0 and len(self.port.text()):
                sock = socket()
                print(self.ip.text(), int(self.port.text()))
                sock.connect((self.ip.text(), int(self.port.text()))) # 192.168.31.229 9091
                screenSize = (win.GetSystemMetrics(0),win.GetSystemMetrics(1))
                sock.send(str(screenSize).encode())
                time.sleep(0.1)
                self.controling = Thread(target=self.MouseAndKeyboardController, args=(sock,), daemon=True)
                self.controling.start()
                img = ImageGrab.grab()
                prev_img = img
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                sock.send(img_bytes.getvalue())
                while True:
                    img = ImageGrab.grab()
                    diff = ImageChops.difference(prev_img, img)
                    if diff.getbbox():
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='PNG')
                        sock.send(img_bytes.getvalue())
                        prev_img = img
                sock.close()
        except Exception as e:
            print(e)
            print("DISCONNECTED")
            sock.close()

    def MouseAndKeyboardController(self, conn):
        new_conn = socket()
        new_conn.connect((self.ip.text(), 9092))
        while True:
            command = new_conn.recv(256).decode()
            try:
                pos = eval(command)
            except TypeError:
                pass
            except SyntaxError:
                pass
            else:
                pyautogui.moveTo(pos)
                new_conn.send(("got it").encode())


    def initUI(self):
        self.pixmap = QPixmap()
        self.label = QLabel(self)
        self.label.resize(self.width(), self.height())
        self.setGeometry(QRect(pyautogui.size()[0] // 4, pyautogui.size()[1] // 4, 400, 90))
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle("[CLIENT] Remote Desktop: " + str(randint(99999, 999999)))
        self.start = Thread(target=self.ChangeImage, daemon=True)
        self.btn = QPushButton(self)
        self.btn.move(5, 55)
        self.btn.resize(390, 30)
        self.btn.setText("Start Demo")
        self.btn.clicked.connect(self.StartThread)
        self.ip = QLineEdit(self)
        self.ip.move(5, 5)
        self.ip.resize(390, 20)
        self.ip.setPlaceholderText("IP")
        self.port = QLineEdit(self)
        self.port.move(5, 30)
        self.port.resize(390, 20)
        self.port.setPlaceholderText("PORT")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Desktop()
    ex.show()
    sys.exit(app.exec())
