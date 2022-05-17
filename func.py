import os
import sys
from sys import platform
from pathlib import Path


def resource_path(
        relative_path):  # This function gets the absolute pathe of what ever you feed it, just so there is no location issue
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def ensure_dir_exist(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def rename_file(
        song_path):  # This is my ver own rename function, not sure if this is how everyong does it but it works for me
    # print(song_path)
    new_file = song_path.replace('.mp4', '.mp3')  # A simple replace
    os.rename(song_path, new_file)


def get_os_downloads_folder():
    if platform == "linux" or platform == "linux2":
        return str(os.path.join(Path.home(), "Downloads"))
    elif platform == "darwin":
        return str(os.path.join(Path.home(), "Downloads"))
    elif platform == "win32":
        return str(os.path.expanduser("~\\Downloads"))
    else:
        print('err')


def get_songs_from_text(txt):
    with open(txt) as fp:
        Lines = fp.readlines()
        return Lines



if __name__ == "__main__":
    pass
