import sys
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QStackedWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QRadioButton
import os
import yt_downloader
from sys import platform
import subprocess
from pathlib import Path
import func
import ssl
ssl._create_default_https_context = ssl._create_unverified_context  # important used to make internet coms legit - windows issue

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
        self.download_list_button = self.findChild(QPushButton, "download_list_button")

        # Actions
        self.download_button.clicked.connect(lambda: self.download_clicked())
        # self.open_folder.clicked.connect(lambda: self.action())

    def download_clicked(self):
        if self.link.text() == '':
            self.update_label.setText("ERROR - Please enter a song name and artiste")
            return
        self.update_label.setText('Searching...')
        default_loc = func.get_os() + '/Youtube/'  # Default folder
        if self.op_input.text() == '':
            download_info = yt_downloader.youtube_single_download(yt_downloader.searchtube(self.link.text()), default_loc)
        else:
            user_location = default_loc + self.op_input.text()
            download_info = yt_downloader.youtube_single_download(yt_downloader.searchtube(self.link.text()),
                                                                  user_location)
        self.update_label.setText(download_info[0])
        file_path = download_info[1]
        song_info = download_info[2]



        # if self.select_audio.isChecked():
        #     self.update_label.setText("just audio")
        # elif self.select_raw_audio.isChecked():
        #     self.update_label.setText("raw audio")
        # elif self.select_clean_audio.isChecked():
        #     self.update_label.setText("clean audio")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainuiwindow = MainUiWindow()
    widget = QStackedWidget()
    widget.addWidget(mainuiwindow)
    widget.setFixedHeight(450)
    widget.setFixedWidth(550)
    widget.show()
    try:
        sys.exit(app.exec())
    except Exception as e:
        print(e)
