import socket
from os import getlogin
from PIL import Image, ImageQt, ImageChops
import io
import numpy as np
from random import randint
import pyautogui
from pynput import mouse, keyboard
from threading import Thread
import time
import win32api as win
import math
# PyQt5
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QPushButton, QAction, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect, Qt

print("[SERVER]: STARTED")
sock = socket.socket()
ADDR = '192.168.31.186'
sock.bind((ADDR, 9091))
sock.listen()
conn, addr = sock.accept()

scale_x, scale_y = 2, 2


class Dekstop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def ScreenSharing(self):
        try:
            print("[SERVER]: CONNECTED: {0}!".format(addr[0]))
            screenSize = conn.recv(1024)
            print(screenSize)
            screenSize = screenSize.decode()
            self.setGeometry(QRect(pyautogui.size()[0] // 4, pyautogui.size()[1] // 4, eval(screenSize)[0] // scale_x,
                                   eval(screenSize)[1] // scale_y))
            self.setFixedSize(self.width(), self.height())

            self.controlling = Thread(target=self.Controlling, args=(conn,), daemon=True)
            self.controlling.start()
            while True:
                img_bytes = conn.recv(999999)
                self.pixmap.loadFromData(img_bytes)
                self.label.setScaledContents(True)
                self.label.resize(self.width(), self.height())
                self.label.setPixmap(self.pixmap)
        except ConnectionResetError:
            QMessageBox.about(self, "ERROR", "[SERVER]: The remote host forcibly terminated the existing connection!")
            conn.close()

    def Controlling(self, conn):
        new_conn = socket.socket()
        new_conn.bind((ADDR, 9092))
        new_conn.listen()
        conn, addr = new_conn.accept()

        def on_move(x, y):
            win_x, win_y = self.frameGeometry().x() + (
                        self.frameGeometry().width() - self.label.width()), self.frameGeometry().y() + (
                                       self.frameGeometry().height() - self.label.height())
            win_width, win_height = self.label.width(), self.label.height()
            if win_x <= x <= win_x + win_width and win_y <= y <= win_y + win_height:
                x = x - win_x
                y = y - win_y
                command = str(['MOVE', x * scale_x, y * scale_y])
                conn.send(command.encode())
                conn.recv(256)
            # print('Pointer moved to {0}'.format((x, y)))

        def on_click(x, y, button, pressed):
            win_x, win_y = self.frameGeometry().x() + (
                        self.frameGeometry().width() - self.label.width()), self.frameGeometry().y() + (
                                       self.frameGeometry().height() - self.label.height())
            win_width, win_height = self.label.width(), self.label.height()
            if win_x <= x <= win_x + win_width and win_y <= y <= win_y + win_height:
                command = str(['CLICK' if pressed else 'RELEASE', str(button)])
                conn.send(command.encode())
                print(command)
                conn.recv(256)
            # print('{0} at {1} {2}'.format('Pressed' if pressed else 'Released',(x, y), button))

        def on_scroll(x, y, dx, dy):
            win_x, win_y = self.frameGeometry().x() + (
                        self.frameGeometry().width() - self.label.width()), self.frameGeometry().y() + (
                                       self.frameGeometry().height() - self.label.height())
            win_width, win_height = self.label.width(), self.label.height()
            if win_x <= x <= win_x + win_width and win_y <= y <= win_y + win_height:
                command = str(['SCROLL', 'DOWN' if dy < 0 else 'UP'])
                conn.send(command.encode())
                conn.recv(256)
            # print('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up',(x, y)))

        listener = mouse.Listener(on_move=on_move, on_click=on_click)
        listener.start()

        def on_press(key):
            ms = mouse.Controller()
            x,y = ms.position
            win_x, win_y = self.frameGeometry().x() + (
                    self.frameGeometry().width() - self.label.width()), self.frameGeometry().y() + (
                                   self.frameGeometry().height() - self.label.height())
            win_width, win_height = self.label.width(), self.label.height()
            if win_x <= x <= win_x + win_width and win_y <= y <= win_y + win_height:
                command = str(['KEY', str(key)])
                conn.send(command.encode())
                conn.recv(256)

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    def initUI(self):
        self.pixmap = QPixmap()
        self.label = QLabel(self)
        self.label.resize(self.width(), self.height())
        self.setWindowTitle("[SERVER] Remote Desktop: " + str(randint(99999, 999999)))
        self.screenSharing = Thread(target=self.ScreenSharing, daemon=True)
        self.screenSharing.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Dekstop()
    ex.show()
    sys.exit(app.exec())
