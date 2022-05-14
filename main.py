import sys
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QStackedWidget, QMainWindow, QPushButton, QLabel


class MainUiWindow(QMainWindow):
    def __init__(self):
        super(MainUiWindow, self).__init__()
        uic.loadUi("MainUiWindow.ui", self)
        self.download_button = self.findChild(QPushButton, "download_button")
        self.open_folder = self.findChild(QPushButton, "open_folder")
        self.updates_label = self.findChild(QLabel, "updates_label")


        self.download_button.clicked.connect(lambda: self.action())

    def action(self):
        self.updates_label.setText("clicked")

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