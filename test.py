import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Win(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 200, 400, 400)
        self.setWindowTitle('QMessageBox的使用')

        self.btn1 = QPushButton(self)
        self.btn1.setText('弹出消息对话框')
        self.btn1.clicked.connect(self.show1)

        self.btn2 = QPushButton(self)
        self.btn2.setText('弹出提问对话框')
        self.btn2.clicked.connect(self.show2)

        self.btn3 = QPushButton(self)
        self.btn3.setText('弹出警告对话框')
        self.btn3.clicked.connect(self.show3)

        self.btn4 = QPushButton(self)
        self.btn4.setText('弹出严重错误对话框')
        self.btn4.clicked.connect(self.show4)

        self.btn5 = QPushButton(self)
        self.btn5.setText('弹出关于对话框')
        self.btn5.clicked.connect(self.show5)

        layout = QVBoxLayout()
        layout.addWidget(self.btn1)
        layout.addWidget(self.btn2)
        layout.addWidget(self.btn3)
        layout.addWidget(self.btn4)
        layout.addWidget(self.btn5)
        self.setLayout(layout)

    def show1(self):
        reply = QMessageBox.information(self,"消息对话框","消息对话框正文",QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
        print(reply)
    def show2(self):
        reply = QMessageBox.question(self,"提问对话框","提问对话框正文",QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
        print(reply)
    def show3(self):
        reply = QMessageBox.warning(self,"警告对话框","警告对话框正文",QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
        print(reply)
    def show4(self):
        reply = QMessageBox.critical(self,"严重错误对话框","严重错误对话框正文",QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
        print(reply)
    def show5(self):
        reply = QMessageBox.about(self,"关于对话框","关于对话框正文")
        print(reply)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Win()
    form.show()
    sys.exit(app.exec_())

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Win(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 200, 400, 400)
        self.setWindowTitle('QMessageBox的使用')

        self.btn1 = QPushButton(self)
        self.btn1.setText('弹出消息对话框')
        self.btn1.clicked.connect(self.show1)

        self.btn2 = QPushButton(self)
        self.btn2.setText('弹出提问对话框')
        self.btn2.clicked.connect(self.show2)

        self.btn3 = QPushButton(self)
        self.btn3.setText('弹出警告对话框')
        self.btn3.clicked.connect(self.show3)

        self.btn4 = QPushButton(self)
        self.btn4.setText('弹出严重错误对话框')
        self.btn4.clicked.connect(self.show4)

        self.btn5 = QPushButton(self)
        self.btn5.setText('弹出关于对话框')
        self.btn5.clicked.connect(self.show5)

        layout = QVBoxLayout()
        layout.addWidget(self.btn1)
        layout.addWidget(self.btn2)
        layout.addWidget(self.btn3)
        layout.addWidget(self.btn4)
        layout.addWidget(self.btn5)
        self.setLayout(layout)

    def show1(self):
        reply = QMessageBox.information(self,"消息对话框","消息对话框正文",QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
        print(reply)
    def show2(self):
        reply = QMessageBox.question(self,"提问对话框","提问对话框正文",QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
        print(reply)
    def show3(self):
        reply = QMessageBox.warning(self,"警告对话框","警告对话框正文",QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
        print(reply)
    def show4(self):
        reply = QMessageBox.critical(self,"严重错误对话框","严重错误对话框正文",QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
        print(reply)
    def show5(self):
        reply = QMessageBox.about(self,"关于对话框","关于对话框正文")
        print(reply)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Win()
    form.show()
    sys.exit(app.exec_())

