import csv




def csv_operations(csv_file):
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        header = next(reader)  # gets the first line / skips
        artist_name_index = header.index('Artist Name(s)')
        song_name_index = header.index('Track Name')
        album_name_index = header.index('Album Name')
        genre_index = header.index('Artist Genres')
        album_release_date_index = header.index('Album Release Date')
        energy_index = header.index('Energy')
        mode_index = header.index('Mode')
        tempo_index = header.index('Tempo')
        for song in reader:
            print(song[artist_name_index], song[song_name_index])

