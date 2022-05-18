from concurrent.futures import ThreadPoolExecutor

from PyQt5.QtCore import QObject, QThread, pyqtSignal
import PyQt5.QtCore
from pytube import YouTube
from pytube import Search
from pytube import Playlist
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QRadioButton, QFileDialog, \
    QProgressBar
# from PyQt5.QtWidgets import *
from PyQt5 import uic, QtGui
import os
from sys import platform
import subprocess
import func
import ssl

ssl._create_default_https_context = ssl._create_unverified_context  # important used to make internet coms legit - windows issue

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        """Download task"""
        if mainuiwindow.link.text() == '':
            mainuiwindow.update_label.setText("ERROR - Please enter a song name and artiste")
            return

        if mainuiwindow.select_audio.isChecked():
            mainuiwindow.radio_button_state = "official audio"
        elif mainuiwindow.select_raw_audio.isChecked():
            mainuiwindow.radio_button_state = "raw official audio"
        elif mainuiwindow.select_clean_audio.isChecked():
            mainuiwindow.radio_button_state = "radio edit clean audio"
        # mainuiwindow.update_label.setText('Searching....')
        # default_loc = func.get_os_downloads_folder() + '/Youtube/'  # Default folder
        download_location = mainuiwindow.download_location_label.text()[19:]
        print('just before download')
        download_info = mainuiwindow.youtube_single_download(mainuiwindow.searchtube(mainuiwindow.link.text(), mainuiwindow.radio_button_state),
                                                     download_location)
        # mainuiwindow.update_label.setText(download_info[0])
        file_path = download_info[1]
        song_info = download_info[2]
        print('before rename')
        try:
            func.rename_file(file_path)  # remove the word downloaded 11 characters, its the title so i add mp4

        except Exception as e:
            print(str(e))

        mainuiwindow.link.setText("")
        mainuiwindow.download_button.disabled = False

        self.finished.emit()



class MainUiWindow(QMainWindow):
    def __init__(self):
        super(MainUiWindow, self).__init__()

        self.thread = None
        self.worker = None
        uic.loadUi("MainUiWindow.ui", self)
        self.download_button = self.findChild(QPushButton, "download_button")
        self.update_label = self.findChild(QLabel, "update_label")
        self.open_folder = self.findChild(QPushButton, "open_folder")
        self.op_input = self.findChild(QLineEdit, "op_input")
        self.link = self.findChild(QLineEdit, "link")
        self.progress_bar = self.findChild(QProgressBar, 'progressBar')
        self.select_audio = self.findChild(QRadioButton, "select_audio")
        self.select_raw_audio = self.findChild(QRadioButton, "select_raw_audio")
        self.select_clean_audio = self.findChild(QRadioButton, "select_clean_audio")
        self.download_list_button = self.findChild(QPushButton, "download_list_button")
        self.change_location_button = self.findChild(QPushButton, "change_location_button")
        self.download_location_label = self.findChild(QLabel, "download_location_label")
        self.radio_button_state = "radio edit clean audio"


        # Actions
        self.download_location_label.setText(f'Download Location: {func.get_os_downloads_folder()}\\Youtube\\')
        self.download_button.clicked.connect(self.download_clicked)
        # self.download_button.clicked.connect(self.download_thread.start) # I'm greatnessss
        self.open_folder.clicked.connect(self.open_folder_clicked)
        self.download_list_button.clicked.connect(self.open_folder_clicked)
        self.change_location_button.clicked.connect(self.download_location_picker)

    def reportProgress(self, n):
        self.update_label.setText('stuff')

    ################################################
    def download_clicked(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()

        # Final resets
        self.download_button.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.download_button.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.update_label.setText("Long-Running Step: 0")
        )
    ################################################

    def open_folder_clicked(self):
        path = self.download_location_label.text()[19:]
        if platform == "win32":
            try:
                os.startfile(path)
            except Exception as e:
                print(e)

        elif platform == "darwin":
            try:
                subprocess.Popen(["open", path])
            except Exception as e:
                print(e)
        else:
            try:
                print(platform)
                subprocess.Popen(["xdg-open", path])
            except Exception as e:
                print(e)

    def download_list_clicked(self):
        try:
            list_of_songs = func.get_songs_from_text('listofsongs.txt')
            self.update_label.setText("text file found...")
        except Exception as e:
            self.update_label.setText(str(e))

        radio_button_state = "radio edit clean audio"
        if self.select_audio.isChecked():
            radio_button_state = "official audio"
        elif self.select_raw_audio.isChecked():
            radio_button_state = "raw official audio"
        elif self.select_clean_audio.isChecked():
            radio_button_state = "radio edit clean audio"

        self.update_label.setText('Searching...')
        default_loc = func.get_os_downloads_folder() + '/Youtube/'  # Default folder
        if self.op_input.text() == '':
            download_info = self.youtube_single_download(
                self.searchtube(self.link.text(), radio_button_state), default_loc)
        else:
            user_location = default_loc + self.op_input.text()
            download_info = self.youtube_single_download(
                self.searchtube(self.link.text(), radio_button_state),
                user_location)
        self.update_label.setText(download_info[0])
        file_path = download_info[1]
        song_info = download_info[2]
        try:
            self.update_label.setText('converting...')
            func.rename_file(file_path)  # remove the word downloaded 11 characters, its the title so i add mp4
            self.update_label.setText('converted...')
        except Exception as e:
            self.update_label.setText(e)

        self.link.setText("")

        # *************************** YOUTUBE STUFF *************************

    def youtube_single_download(self, link, op):
        if not link:
            self.update_label.setText('Error - no song specified or song downloaded already')
            return
        print('single download func ran')
        yt = YouTube(link[0])
        # print(f'single download func debug 2 {yt}')
        yt.streams.filter(only_audio=True)
        self.update_label.setText('Starting download...')
        stream = yt.streams.get_by_itag(140)
        func.ensure_dir_exist(op)
        file_path = stream.download(output_path=op)
        self.update_label.setText('Download complete')
        info_list = [yt.title, file_path, yt.vid_info]
        print('download finished')
        return info_list

    def searchtube(self, txt, radio_button_state):
        if txt == '':
            return []
        print('search func ran')
        self.update_label.setText('Searching for your song...')
        video_list = []
        s = Search(f'{txt} {radio_button_state}')
        for obj in s.results:
            x = str(
                obj)  # in the future see if theyy have an easier way to use these youtube obj in search results. I doubt what i'm doing is the easy way lol
            video_id = x[x.rfind('=') + 1:].strip('>')
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            video_list.append(video_url)
            self.update_label.setText('getting list of matching audio')
        self.update_label.setText('Search complete - Starting download')
        return video_list

    def download_youtube_playlist(self):
        print('playlist func ran')
        pl = input('Paste playlist here >')
        playlist = Playlist(pl)
        print('*' * 40)
        print(f'Playlist contains {len(playlist)} items')
        print('*' * 40)
        for url in playlist[:3]:
            self.youtube_single_download(url)

    def download_list_of_songs_from_file(self, list_of_songs):
        print('playlist from file func ran')
        self.update_label.setText('Getting list of songs from file')
        # playlist = Playlist(pl)
        # print('*' * 40)
        self.update_label.setText(f'File contains {len(list_of_songs)} songs')
        # print('*' * 40)
        for song in list_of_songs:
            self.update_label.setText(f'Currently downloading song - {song}')
            self.youtube_single_download(song)

    def download_location_picker(self):
        user_location = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.download_location_label.setText(f'Download Location: {user_location}')
        return user_location


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainuiwindow = MainUiWindow()

    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("icon.ico"), QtGui.QIcon.Selected, QtGui.QIcon.On)
    mainuiwindow.setWindowIcon(icon)

    mainuiwindow.setFixedWidth(491)
    mainuiwindow.setFixedHeight(386)
    mainuiwindow.show()

    try:
        sys.exit(app.exec())
    except Exception as e:
        print(e)
