from socket import *
from PIL import ImageGrab, Image, ImageChops
import io
import numpy as np
from random import randint
import time
import pyautogui
from pynput import mouse ,keyboard
from pynput.mouse import Button
from pynput.keyboard import Key

from threading import Thread
import sys
import win32api as win
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QPushButton, QAction, QMessageBox, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect, Qt

ADDR = '192.168.31.186'
class Desktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def StartThread(self):
        self.start.start()

    def ChangeImage(self):
        try:
            # if len(self.ip.text()) != 0 and len(self.port.text()):
            sock = socket()
            #     print(self.ip.text(), int(self.port.text()))
            #     sock.connect((self.ip.text(), int(self.port.text()))) # 192.168.31.229 9091
            sock.connect((ADDR, 9091))
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
        new_conn.connect((ADDR, 9092))
        ms = mouse.Controller()
        kb = keyboard.Controller()
        while True:
            msg = new_conn.recv(256).decode()
            try:
                command = eval(msg)
            except Exception as e:
                print(e)
                pass
            else:
                if command[0] == "CLICK":
                    button = command[1]
                    ms.press(Button.left if button.find('left') else Button.right)
                    new_conn.send(("got it").encode())
                    msg = new_conn.recv(256).decode()
                    try:
                        command = eval(msg)
                    except Exception as e:
                        print(e)
                    else:
                        command = eval(msg)
                        while command[0] != "RELEASE":
                            if command[0] == 'MOVE':
                                ms.position = (command[1],command[2])
                            new_conn.send(("got it").encode())
                            msg = new_conn.recv(256).decode()
                            try:
                                command = eval(msg)
                            except Exception as e:
                                print(e)
                        ms.release(Button.left if button.find('left') else Button.right)
                elif command[0] == 'MOVE':
                    ms.position = (command[1],command[2])
                elif command[0] == 'KEY':
                    kb.press(eval(command[1]))
                    kb.release(eval(command[1]))
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
        # self.ip = QLineEdit(self)
        # self.ip.move(5, 5)
        # self.ip.resize(390, 20)
        # self.ip.setPlaceholderText("IP")
        # self.port = QLineEdit(self)
        # self.port.move(5, 30)
        # self.port.resize(390, 20)
        # self.port.setPlaceholderText("PORT")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Desktop()
    ex.show()
    sys.exit(app.exec())
