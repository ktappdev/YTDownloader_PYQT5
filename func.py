import os
import sys
from sys import platform
from pathlib import Path
import re


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
    return list_of_urls

    # def resource_path(relative_path):  # This function gets the absolute pathe of what ever you feed it, just so there is no location issue
    #     if hasattr(sys, '_MEIPASS'):
    #         return os.path.join(sys._MEIPASS, relative_path)
    #     return os.path.join(os.path.abspath("."), relative_path)


def ensure_dir_exist(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def rename_file(song_path):
    new_file = song_path.replace('.mp4', '.mp3')
    if '.webm' in song_path:
        new_file = song_path.replace('.webm', '.mp3')  # A simple replace
    os.rename(song_path, new_file)
    return new_file


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
