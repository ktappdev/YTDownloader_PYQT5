import re
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import PyQt5.QtCore
from pytube import YouTube
from pytube import Search
from pytube import Playlist
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QRadioButton, QFileDialog, \
    QProgressBar, QMessageBox
from PyQt5 import uic, QtGui
import os
from sys import platform
import subprocess
import func
import ssl

ssl._create_default_https_context = ssl._create_unverified_context  # important used to make internet coms legit - windows issue


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def run(self):
        download_location = mainuiwindow.download_location_label.text()[19:]
        """Download task"""
        if mainuiwindow.link.text() == '':
            mainuiwindow.update_label.setText("ERROR - Please enter a song name and artiste")
            return
        #################### Youtube URL detection #####################
        list_of_urls_ = read_urls_from_search_box(mainuiwindow.link.text())
        if list_of_urls_:
            self.progress.emit(f'Found {len(list_of_urls_)} youtube urls, Downloading...')
            for link in list_of_urls_:
                # print(link)
                down_inf = youtube_single_download(link, download_location)
                self.progress.emit(f'Downloaded - {down_inf[0]}')
            self.finished.emit()
            return

        if mainuiwindow.select_audio.isChecked():
            mainuiwindow.radio_button_state = "official audio"
        elif mainuiwindow.select_raw_audio.isChecked():
            mainuiwindow.radio_button_state = "raw official audio"
        elif mainuiwindow.select_clean_audio.isChecked():
            mainuiwindow.radio_button_state = "radio edit clean audio"

        ################## SERACH
        txt = mainuiwindow.link.text()
        radio_button_state = mainuiwindow.radio_button_state
        video_list = []
        self.progress.emit(f'Searching for - {txt}')
        s = Search(f'{txt} {radio_button_state}')
        for obj in s.results:
            x = str(
                obj)  # in the future see if theyy have an easier way to use these youtube obj in search results. I doubt what i'm doing is the easy way lol
            video_id = x[x.rfind('=') + 1:].strip('>')
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            video_list.append(video_url)

        ############## DOWNLOAD
        yt = YouTube(video_list[0])
        if 'TTRR' in yt.title:
            yt = YouTube(video_list[1])
        self.progress.emit('Filtering songs')
        # yt.streams.filter(only_audio=True)
        # stream = yt.streams.get_by_itag(251)
        stream = yt.streams.get_audio_only()
        func.ensure_dir_exist(download_location)
        self.progress.emit('Downloading...')
        file_path = stream.download(output_path=download_location)
        download_info = [yt.title, file_path, yt.vid_info]
        self.progress.emit('Download complete')
        file_path = download_info[1]
        song_info = download_info[2]
        try:
            func.rename_file(file_path)  # remove the word downloaded 11 characters, its the title so i add mp4
        except Exception as e:
            print(str(e))
        self.progress.emit(f'Downloaded - {download_info[0]}')
        self.finished.emit()


def youtube_single_download(link, op):
    if link == []:
        return
    yt = YouTube(
        link)  # not sure whay i does remove this indexing thing but i suspect its for thwee playlisting to work... after 2 weeks im lost when the program gcrashes lol i need to handle this better asap
    # print(f'single download func debug 2 {yt}')
    yt.streams.filter(only_audio=True)
    stream = yt.streams.get_audio_only()
    file_path = stream.download(output_path=op)
    download_info = [yt.title, file_path, yt.vid_info]
    try:
        func.rename_file(file_path)  # remove the word downloaded 11 characters, its the title so i add mp4
    except Exception as ex:
        print(str(e))
    return download_info


def read_urls_from_search_box(search_box_contents):
    REXP2 = r'(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?'
    list_of_urls = []
    try:
        url = re.findall(REXP2, search_box_contents)
        # print(url)
        if not url:  # check if the current list is empty. this is insane to me right now lol, compared to how i was gonna check
            return []
        else:
            for vid_code in url:
                list_of_urls.append(f'https://www.youtube.com/watch?v={vid_code}')
    except Exception as e:
        print(e)
    print(list_of_urls)
    return list_of_urls


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
        self.link.returnPressed.connect(self.download_clicked)
        self.select_audio = self.findChild(QRadioButton, "select_audio")
        self.select_raw_audio = self.findChild(QRadioButton, "select_raw_audio")
        self.select_clean_audio = self.findChild(QRadioButton, "select_clean_audio")
        self.download_list_button = self.findChild(QPushButton, "download_list_button")
        self.change_location_button = self.findChild(QPushButton, "change_location_button")
        self.download_location_label = self.findChild(QLabel, "download_location_label")
        self.radio_button_state = "radio edit clean audio"

        # Actions
        self.download_location_label.setText(f'Download Location: {func.get_os_downloads_folder()}/Youtube/')
        self.download_button.clicked.connect(self.download_clicked)
        self.open_folder.clicked.connect(self.open_folder_clicked)
        self.download_list_button.clicked.connect(self.open_folder_clicked)
        self.change_location_button.clicked.connect(self.download_location_picker)

    def reportProgress(self, s):
        self.update_label.setText(s)

    def resetSearchBoxfunc(self):
        print('clear box')
        self.link.clear()

    def download_location_picker(self):
        user_location = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.download_location_label.setText(f'Download Location: {user_location}')
        return user_location

    ################################################
    def download_clicked(self):
        if mainuiwindow.link.text() == '':
            QMessageBox.about(self, "Error", "Please enter song and artiste name")
            return

        self.thread = QThread()

        self.worker = Worker()

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.thread.start()

        # Final resets
        self.download_button.setEnabled(False)
        self.link.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.download_button.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.link.clear()
        )
        self.thread.finished.connect(
            lambda: self.link.setEnabled(True)
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
        self.update_label.setText(f'File contains {len(list_of_songs)} songs')
        for song in list_of_songs:
            self.update_label.setText(f'Currently downloading song - {song}')
            self.youtube_single_download(song)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainuiwindow = MainUiWindow()
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("icon.ico"), QtGui.QIcon.Selected, QtGui.QIcon.On)
    mainuiwindow.setWindowIcon(icon)
    mainuiwindow.setFixedWidth(624)
    mainuiwindow.setFixedHeight(360)
    mainuiwindow.show()
    try:
        sys.exit(app.exec())
    except Exception as e:
        print(e)
