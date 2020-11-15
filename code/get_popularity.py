import csv
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_popularity(artist_id):

    url = 'https://api.spotify.com/v1/artists/' + artist_id
    headers = {'Authorization': 'Bearer +++'}

    try:
        r = requests.get(url, headers=headers)
        artist = r.json()
        followers = artist['followers']['total']
        genres = artist['genres']
        popularity = artist['popularity']
        name = artist['name']
        return artist_id, name, followers, genres, popularity
    except Exception as e:
        print(e)


if __name__ == '__main__':

    file = csv.reader(open('data/artist-uris.csv.csv', 'r', encoding='utf-8'), delimiter=',')
    artists = []
    threads = []

    counter = 0

    with ThreadPoolExecutor(max_workers=20) as executor:
        for line in file:
            artist_id = line[-1].split(':')[-1]
            threads.append(executor.submit(get_popularity, artist_id))

    for task in as_completed(threads):
        artist_id, name, followers, genres, popularity = task.result()
        artists.append([name, artist_id, followers, genres, popularity])

    with open("data/output.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(artists)
