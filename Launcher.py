import sys
import os
import main
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QWidget, QFileDialog, QScrollArea, QListWidget

class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Project\Main.ui', self)
        self.setWindowTitle('Эщкерп пром Карков')
        self.pixmap = QPixmap('Project\EFT.jpg')
        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)

        self.pushButton.clicked.connect(self.run)
        self.label.setGeometry(30, 30, 770, 461)
        self.label.resize(730, 430)

    def run(self):
        main.main()
        sys.exit()

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())