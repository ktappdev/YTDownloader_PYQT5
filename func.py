import os
import sys
import yt_downloader
from sys import platform
import subprocess
from pathlib import Path


def resource_path(
        relative_path):  # This function gets the absolute pathe of what ever you feed it, just so there is no location issue
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def rename_file(
        song_path):  # This is my ver own rename function, not sure if this is how everyong does it but it works for me
    # print(song_path)
    new_file = song_path.replace('.mp4', '.mp3')  # A simple replace
    os.rename(song_path, new_file)


def get_os():
    if platform == "linux" or platform == "linux2":
        return str(os.path.join(Path.home(), "Downloads"))
    elif platform == "darwin":
        return str(os.path.join(Path.home(), "Downloads"))
    elif platform == "win32":
        return str(os.path.expanduser("~\\Desktop"))
    else:
        print('err')


# class BoxLayoutUI(BoxLayout):
#     link = ObjectProperty(None)
#     op_input = ObjectProperty(None)
#     update_label = ObjectProperty(None)
#     download_button = ObjectProperty(None)
#     main_canv_image = resource_path('bg.png')
#     yt_logo = resource_path('ytlogo.png')

    def download_button_action(self):
        self.download_button.disabled = True
        # os_download_location = get_os()
        # print(desktop)
        if self.link.text == '':
            self.update_label.text = 'ERROR - Please enter a song name and artiste'
            return
        self.update_label.text = 'Searching...'

        default_loc = get_os() + '/Youtube/'  # Default folder
        if self.op_input.text == '':
            download_info = yt_downloader.youtube_single_download(yt_downloader.searchtube(self.link.text), default_loc)
        else:
            user_location = default_loc + self.op_input.text
            download_info = yt_downloader.youtube_single_download(yt_downloader.searchtube(self.link.text),
                                                                  user_location)

        self.update_label.text, file_path, song_info = download_info
        # print(song_info)
        try:
            rename_file(file_path)  # remove the word downloaded 11 characters, its the title so i add mp4
        except Exception as e:
            print(str(e))

        self.link.text = ''
        self.download_button.disabled = False

    def open_folder(self):
        # desktop = os.path.expanduser("~\\Desktop\\")
        # print(desktop)
        default_loc = get_os() + '/Youtube/'
        # print(default_loc)
        if self.op_input.text == '':
            path = default_loc
        else:
            path = default_loc + self.op_input.text

        if platform == "windows":
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


if __name__ == "__main__":
    pass
