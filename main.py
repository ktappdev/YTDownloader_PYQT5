from PyQt5.QtCore import QObject, QThread, pyqtSignal
import PyQt5.QtCore
from pytube import YouTube
from pytube import Search
from pytube import Playlist
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QRadioButton, QFileDialog, \
    QProgressBar, QMessageBox, QTextEdit
from PyQt5 import uic, QtGui
import os
from sys import platform
import subprocess
import func
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def run(self):
        download_location = mainuiwindow.download_location_label.text()
        """Download task"""
        if mainuiwindow.link.text() == '':
            mainuiwindow.update_label.setText("ERROR - Please enter a song name and artiste")
            return
        #################### Youtube URL detection #####################
        list_of_urls_ = func.read_urls_from_search_box(mainuiwindow.link.text())
        if list_of_urls_:
            self.progress.emit(f'Found {len(list_of_urls_)} youtube urls, Downloading...')
            for link in list_of_urls_:
                # print(link)
                down_inf = youtube_single_download(link, download_location)
                self.progress.emit(f'Downloaded - {down_inf[0]}')
            self.finished.emit()
            # End URL Detection on the single download page
            return
        if mainuiwindow.select_audio.isChecked():
            mainuiwindow.radio_button_state = "official audio"
        elif mainuiwindow.select_raw_audio.isChecked():
            mainuiwindow.radio_button_state = "raw official audio"
        elif mainuiwindow.select_clean_audio.isChecked():
            mainuiwindow.radio_button_state = "radio edit clean audio"

        ################## youtube SERACH
        txt = mainuiwindow.link.text()
        radio_button_state = mainuiwindow.radio_button_state
        video_list = []
        self.progress.emit(f'Searching for - {txt}')
        s = Search(f'{txt} {radio_button_state}')
        for obj in s.results[:2]:
            x = str(
                obj)
            video_id = x[x.rfind('=') + 1:].strip('>')
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            video_list.append(video_url)
        ############## youtube single DOWNLOAD
        yt = YouTube(video_list[0])
        if 'TTRR' in yt.title:
            yt = YouTube(video_list[1])
        self.progress.emit('Filtering songs')
        stream = yt.streams.get_audio_only()
        func.ensure_dir_exist(download_location)
        self.progress.emit('Downloading...')
        file_path = stream.download(output_path=download_location)
        download_info = [yt.title, file_path, yt.vid_info]
        self.progress.emit('Download complete')
        song_name = download_info[0]
        # song_info = download_info[2]
        try:
            # func.rename_file(file_path)
            self.progress.emit('Converting and adding tags')
            func.convert_rename_add_tags(file_path)
        except Exception as e:
            print(str(e))
        self.progress.emit(f'Downloaded - {song_name}')
        self.finished.emit()


class Worker2(QObject):  # Second Thread

    finished = pyqtSignal()
    progress_bar_multi = pyqtSignal(int)  # for Progress bar on multi page
    progress_multi = pyqtSignal(str)  # for label on multi page

    def run(self):
        try:
            download_location = mainuiwindow.download_location_label_multi.text()

            #################### Youtube URL detection and download #####################
            list_of_urls_ = func.read_urls_from_search_box(mainuiwindow.link_multi.toPlainText())
            if list_of_urls_:
                self.progress_multi.emit(f'Found {len(list_of_urls_)} youtube urls, Downloading...')
                for link in list_of_urls_:
                    down_inf = youtube_single_download(link, download_location)
                    self.progress_multi.emit(f'Downloaded - {down_inf[0]}')
                self.finished.emit()
                return
            ########## if there isn't any youtube link then its a text list ###########
            if mainuiwindow.select_audio.isChecked():
                mainuiwindow.radio_button_state = "official audio"
            elif mainuiwindow.select_raw_audio.isChecked():
                mainuiwindow.radio_button_state = "raw official audio"
            elif mainuiwindow.select_clean_audio.isChecked():
                mainuiwindow.radio_button_state = "radio edit clean audio"

            ################## youtube SERACH
            songs = mainuiwindow.link_multi.toPlainText().split("\n")
            p = round(100 / len(songs))
            video_list = []
            for song in songs:
                self.progress_multi.emit(f'Searching for - {song}')
                s = Search(f'{song} {mainuiwindow.radio_button_state}')
                for obj in s.results[:2]:
                    x = str(obj)
                    video_id = x[x.rfind('=') + 1:].strip('>')
                    video_url = f'https://www.youtube.com/watch?v={video_id}'
                    video_list.append(video_url)
                ############## DOWNLOAD

                # down_inf = youtube_single_download(video_list, download_location)
                yt = YouTube(video_list[0])
                if 'TTRR' in yt.title:
                    yt = YouTube(video_list[1])
                # yt.streams.filter(only_audio=True)
                stream = yt.streams.get_audio_only()
                self.progress_multi.emit(f'Downloading...{yt.title}')
                file_path = stream.download(output_path=download_location)
                download_info = [yt.title, file_path, yt.vid_info]
                try:
                    # func.rename_file(file_path)
                    self.progress_multi.emit('Converting, renaming and adding IDTags')
                    func.convert_rename_add_tags(file_path)
                except Exception as ex:
                    print(ex)
                self.progress_multi.emit(f'Downloaded - {download_info[0]}')
                self.progress_bar_multi.emit(mainuiwindow.progress_bar_multi.value() + p)
                self.progress_multi.emit('Download complete')
                song_name = download_info[0]
                video_list.clear()
                # song_info = download_info[2]
        except Exception as e:
            print(e)
        self.progress_multi.emit(f'All downloads complete, ready for more!')
        self.progress_bar_multi.emit(0)
        self.finished.emit()


def youtube_single_download(link, op): #Using this for links still
    if link == []:
        return
    yt = YouTube(link[0])
    if 'TTRR' in yt.title:
        yt = YouTube(link[1])
    yt.streams.filter(only_audio=True)
    stream = yt.streams.get_audio_only()
    file_path = stream.download(output_path=op)
    download_info = [yt.title, file_path, yt.vid_info]
    try:
        func.convert_rename_add_tags(file_path)
    except Exception as ex:
        print(str(e))
    return download_info


class MainUiWindow(QMainWindow):
    def __init__(self):
        super(MainUiWindow, self).__init__()
        uic.loadUi("MainUiWindow.ui", self)
        self.thread = None
        self.thread2 = None
        self.worker = None
        self.worker2 = None

        self.download_button = self.findChild(QPushButton, "download_button")
        self.update_label = self.findChild(QLabel, "update_label")
        self.update_label_multi = self.findChild(QLabel, "update_label_multi")
        self.open_folder = self.findChild(QPushButton, "open_folder")
        self.open_folder_multi = self.findChild(QPushButton, "open_folder_multi")
        self.op_input = self.findChild(QLineEdit, "op_input")
        self.link = self.findChild(QLineEdit, "link")
        self.link_multi = self.findChild(QTextEdit, "link_multi")
        self.select_audio = self.findChild(QRadioButton, "select_audio")
        self.select_raw_audio = self.findChild(QRadioButton, "select_raw_audio")
        self.select_clean_audio = self.findChild(QRadioButton, "select_clean_audio")
        self.download_list_button = self.findChild(QPushButton, "download_list_button")
        self.change_location_button = self.findChild(QPushButton, "change_location_button")
        self.change_location_button_multi = self.findChild(QPushButton, "change_location_button_multi")
        self.download_location_label = self.findChild(QLabel, "download_location_label")
        self.download_location_label_multi = self.findChild(QLabel, "download_location_label_multi")
        self.progress_bar_multi = self.findChild(QProgressBar, "progress_bar_multi")
        self.radio_button_state = "radio edit clean audio"

        # Actions
        self.link.returnPressed.connect(self.download_clicked)
        self.download_location_label.setText(f'{func.get_os_downloads_folder()}/Youtube/')
        self.download_location_label_multi.setText(f'{func.get_os_downloads_folder()}/Youtube/Multi')
        self.download_button.clicked.connect(self.download_clicked)
        self.download_list_button.clicked.connect(self.download_list_clicked)
        self.open_folder.clicked.connect(lambda: self.open_folder_clicked('single'))
        self.open_folder_multi.clicked.connect(lambda: self.open_folder_clicked('multi'))
        self.change_location_button.clicked.connect(lambda: self.download_location_picker('single'))
        self.change_location_button_multi.clicked.connect(lambda: self.download_location_picker('multi'))

    def reportProgress(self, s):
        self.update_label.setText(s)

    def reportProgress_multi(self, s):
        self.update_label_multi.setText(s)

    def report_progress_bar_multi(self, s):
        self.progress_bar_multi.setValue(s)

    def resetSearchBoxfunc(self):
        self.link.clear()

    def download_location_picker(self, lbl):
        user_location = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if lbl == 'single':
            self.download_location_label.setText(user_location)
            return user_location
        else:
            self.download_location_label_multi.setText(user_location)
            return user_location

    #########################This triggers the Worker Thread#######################
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

    #########################This triggers the Worker2 Thread#######################
    def download_list_clicked(self):
        if mainuiwindow.link_multi.toPlainText() == '':
            QMessageBox.about(self, "Error", "List is empty")
            return

        self.thread2 = QThread()

        self.worker2 = Worker2()

        self.worker2.moveToThread(self.thread2)
        print('gass')
        self.thread2.started.connect(self.worker2.run)
        self.worker2.finished.connect(self.thread2.quit)
        self.worker2.finished.connect(self.worker2.deleteLater)
        self.thread2.finished.connect(self.thread2.deleteLater)
        self.worker2.progress_multi.connect(self.reportProgress_multi)
        self.worker2.progress_bar_multi.connect(self.report_progress_bar_multi)
        print('about to start')
        self.thread2.start()
        print('after started')
        # Final resets
        self.download_list_button.setEnabled(False)
        self.link_multi.setEnabled(False)
        self.thread2.finished.connect(
            lambda: self.download_list_button.setEnabled(True)
        )
        self.thread2.finished.connect(
            lambda: self.link_multi.clear()
        )
        self.thread2.finished.connect(
            lambda: self.link_multi.setEnabled(True)
        )

    ################################################

    def open_folder_clicked(self, btn):
        if btn == 'single':
            path = self.download_location_label.text()
        else:
            path = self.download_location_label_multi.text()
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
            self.func.youtube_single_download(url)

    def download_list_of_songs_from_file(self, list_of_songs):
        print('playlist from file func ran')
        self.update_label.setText('Getting list of songs from file')
        self.update_label.setText(f'File contains {len(list_of_songs)} songs')
        for song in list_of_songs:
            self.update_label.setText(f'Currently downloading song - {song}')
            self.func.youtube_single_download(song)


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
