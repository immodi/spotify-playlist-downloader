import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from tkinter import *
from tkinter import filedialog
from threading import Thread
import glob
import os
from os import system
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


title = ''
selected_a_folder = False
selected_dir = "./"
pathToSave = "%(" + selected_dir + ")s%"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument("--headless")

id = 'a664e292dd94406cbca496b6f4ada586'
secret = '58ed3db92fa5467ca9d76487ba573316'

values = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .+=-")

ALL_FILES = glob.glob('*.webm')

client_credentials_manager = SpotifyClientCredentials(client_id=id, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)



def titleCase(s):
    '''
    A function to convert the given song name to title case.
    The default function in Python convert the words 'the', 'and', 'of', etc.
    And I find that annoying
    '''

    l = s.split()
    str = l[0][0].upper() + l[0][1:]

    for word in l[1:]:
        if word not in ['in', 'the', 'for', 'of', 'a', 'at', 'an', 'is', 'and']:
            str += ' ' + word[0].upper() + word[1:]
        else:
            str += ' ' + word

    return str


def getVidID(song, URL, ignore_playlist=False):
    '''
    This function gets the ID of the Video you have to download.
    '''
    global title
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    search = song + ' lyrics'
    searchQuery = '+'.join(search.split())
    searchURL = URL + searchQuery
    driver.get(searchURL)
    delay = 3  # seconds
    try:
        link = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'video-title')))
        link.click()
    except TimeoutError:
        print("Loading took too much time!")
    searchURL = driver.current_url
    title = str(driver.title)
    driver.close()
    return searchURL
    # returns None for invalid YouTube url


def doStuff(song):
    global title, selected_dir
    print("Downloading " + titleCase(song))
    URL = 'https://www.youtube.com/results?search_query='
    link = getVidID(song, URL)
    system("youtube-dl --ffmpeg-location " + '"' + "ffmpeg" + '" ' + "-f bestaudio[ext=webm]/bestaudio -x --audio-format mp3 --output \"" + pathToSave + "(" + "title" + ")" + "s" + ".%(ext)s" + '" ' + link)
    # print("youtube-dl --ffmpeg-location " + '"' + "ffmpeg" + '" ' + "-f bestaudio[ext=webm]/bestaudio -x --audio-format mp3 --output \"" + pathToSave + "(" + "title" + ")" + "s" + ".%(ext)s" + '" ' + link)
    songs = glob.glob("NA*")
    for i in songs:
        os.rename(i, i[2:])
        os.rename(i[2:], selected_dir + "/" + i[2:])
    text = "Downloaded " + titleCase(song) + "\n"
    return text


def call_playlist(creator, playlist_id):
    # step1

    playlist_features_list = ["artist", "album", "track_name", "track_id", "danceability", "energy", "key", "loudness",
                              "mode", "speechiness", "instrumentalness", "liveness", "valence", "tempo", "duration_ms",
                              "time_signature"]

    playlist_df = pd.DataFrame(columns=playlist_features_list)

    # step2

    playlist = sp.user_playlist_tracks(creator, playlist_id)["items"]
    for track in playlist:
        # Create empty dict
        playlist_features = {}
        # Get metadata
        playlist_features["artist"] = track["track"]["album"]["artists"][0]["name"]
        playlist_features["album"] = track["track"]["album"]["name"]
        playlist_features["track_name"] = track["track"]["name"]
        playlist_features["track_id"] = track["track"]["id"]

        # Get audio features
        audio_features = sp.audio_features(playlist_features["track_id"])[0]
        for feature in playlist_features_list[4:]:
            playlist_features[feature] = audio_features[feature]

        # Concat the dfs
        track_df = pd.DataFrame(playlist_features, index=[0])
        playlist_df = pd.concat([playlist_df, track_df], ignore_index=True)
    # Step 3
    return playlist_df


def remover(my_string=""):
    for item in my_string:
        if item not in values:
            my_string = my_string.replace(item, "")
    return my_string


def start(log, link):
    global selected_dir, selected_a_folder
    if not selected_a_folder:
        try:
            path = os.path.join('./', 'select-a-folder-next-time')
            os.mkdir(path)
            selected_dir = path
        except OSError:
            pass
    else: pass
    playlist = call_playlist("spotify", str(link))
    playlist_songs = playlist["artist"] + " " + playlist["track_name"]
    song_names = playlist_songs.to_numpy()
    for i in song_names:
        try:
            log.insert(1.0, doStuff(i))
        except FileExistsError:
            continue


def gui():
    window = Tk()
    width = 720
    height = 620

    window.iconbitmap("spotify_icon.ico")
    window.title('Spotify Downloader')
    window.geometry(str(str(width) + 'x' + str(height)))
    window.configure(bg='black')

    play_list_link = Text(window, height=1, width=50, font=('Cairo Regular', 12), bg='black', fg='white')
    play_list_link.place(x=width / 5, y=height / 8)

    download_button = Button(window, height=1, width=14, text='Download', font=('Cairo Regular', 10), bg='black',
                             fg='white', command=lambda: main(log, play_list_link, download_button, window, height))  # start(log, play_list_link.get("1.0", 'end-1c'))
    download_button.place(x=width / 2.3, y=height / 4)

    log = Text(window, height=10, width=80, font=('Cairo Regular', 10), bg='black', fg='white', cursor='arrow')
    log.bind("<Key>", lambda a: "break")
    log.place(x=width / 7, y=height / 2 - 50)

    change_download_dir_button = Button(window, height=1, width=14, text='Select Folder', font=('Cairo Regular', 10), bg='black',
                                        fg='white', command=lambda: ask_directory(window, height))  # start(log, play_list_link.get("1.0", 'end-1c'))
    change_download_dir_button.place(x=width - 120, y=height - 50)

    window.mainloop()


def main(log, play_list_link, download_button, window, height):
    play_list_link.bind("<Key>", lambda a: "break")
    play_list_link.config(cursor='arrow')
    changeState(download_button)

    th1 = Thread(target=start, args=(log, get_playlist_id(play_list_link.get("1.0", 'end-1c'))))
    th1.daemon = True
    th1.start()

    th2 = Thread(target=timer, args=(window, height))
    th2.daemon = True
    th2.start()


def timer(window, height):
    timer_log = Text(window, height=1, width=5, font=('Cairo Regular', 12), bg='black', fg='white', cursor='arrow')
    timer_log.bind("<Key>", lambda a: "break")
    timer_log.tag_configure("center", justify='center')
    timer_log.tag_add("center", 1.0, "end")
    timer_log.place(x=20, y=height - 45)
    x = 0
    while True:
        time.sleep(1)
        timer_log.delete('1.0', END)
        timer_log.insert(1.0, f'{x}')
        x += 1


def ask_directory(window, height):
    global selected_dir, selected_a_folder
    selected_a_folder = True
    folder_selected = filedialog.askdirectory()
    selected_dir = str(folder_selected)
    selected_dir_display = Text(window, height=1, width=70, font=('Cairo Regular', 10), bg='black', fg='white', cursor='arrow')
    selected_dir_display.bind("<Key>", lambda a: "break")
    selected_dir_display.delete('1.0', END)
    selected_dir_display.insert(1.0, selected_dir)
    selected_dir_display.place(x=90, y=height - 42)


def get_playlist_id(text):
    text_new = str(text).split('?')[0][34:]
    return text_new


def changeState(btn1):
    if btn1['state'] == NORMAL: btn1['state'] = DISABLED
    else: btn1['state'] = NORMAL


if __name__ == '__main__':
    Thread(target=gui).start()

# start("7dyygRNkq3QUB0EliWthu6")
