import sys
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QStackedWidget, QMainWindow, QPushButton, QLabel, QLineEdit, \
    QRadioButton


class MainUiWindow(QMainWindow):
    def __init__(self):
        super(MainUiWindow, self).__init__()
        uic.loadUi("MainUiWindow.ui", self)
        self.download_button = self.findChild(QPushButton, "download_button")
        self.open_folder = self.findChild(QPushButton, "open_folder")
        self.update_label = self.findChild(QLabel, "update_label")
        self.op_input = self.findChild(QLineEdit, "op_input")
        self.link = self.findChild(QLineEdit, "link")
        self.select_clean_audio = self.findChild(QRadioButton, "select_clean_audio")
        self.select_audio = self.findChild(QRadioButton, "select_audio")
        self.select_raw_audio = self.findChild(QRadioButton, "select_raw_audio")


        self.download_button.clicked.connect(lambda: self.action())


    def action(self):
        if self.select_audio.isChecked():
            self.update_label.setText("just audio")
        elif self.select_raw_audio.isChecked():
            self.update_label.setText("raw audio")
        elif self.select_clean_audio.isChecked():
            self.update_label.setText("clean audio")


app = QApplication(sys.argv)

mainuiwindow = MainUiWindow()
widget = QStackedWidget()
widget.addWidget(mainuiwindow)
widget.setFixedHeight(400)
widget.setFixedWidth(550)
widget.show()
try:
    sys.exit(app.exec_())
except Exception as e:
    print(e)