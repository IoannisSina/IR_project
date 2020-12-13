import requests
import pandas as pd
from pandarallel import pandarallel
import API_keys
import time

api_search_url = 'https://api.genius.com/search?q='
api_songs_url = 'https://api.genius.com/songs/'

headers = { 'Authorization': API_keys.genius_key }

def search_genius(x):

    try:
        r = requests.get(api_search_url + x.track_name + ' ' + x.artist_name, headers=headers)
        result = r.json()['response']['hits'][0]['result']

        genius_track_id = result['id']

        r = requests.get(api_songs_url + str(genius_track_id), headers=headers)
        song = r.json()['response']['song']

        for dictionary in song['media']:
            provider = dictionary['provider']
            if provider != 'spotify':
                x[provider] = dictionary['url']

        x['songwriter_ids'] = [dictionary['id'] for dictionary in song['writer_artists']]
        x['producer_ids'] = [dictionary['id'] for dictionary in song['producer_artists']]

        x['genius_track_id'] = genius_track_id
        x['annotation_count'] = result['annotation_count']
        x['pyongs'] = result['pyongs_count']
        x['lyrics_owner_id'] = result['lyrics_owner_id']
        x['hot'] = result['stats']['hot']
        x['pageviews'] = result['stats']['pageviews'] if 'pageviews' in result['stats'] else None

        artist_name = result['primary_artist']['name']

        if '&' in artist_name:
            singer_ids = []
            names = [name.strip() for name in artist_name.split('&')]
            for name in names:
                r = requests.get(api_search_url + name, headers=headers)
                hits = r.json()['response']['hits']
                for hit in hits:
                    if hit['result']['primary_artist']['name'] == name:
                        singer_ids.append(hit['result']['primary_artist']['id'])
                        break
            
            x['singer_ids'] = singer_ids
        else:
            x['singer_ids'] = [result['primary_artist']['id'] if 'id' in result['primary_artist'] else None]

        print('OK')
    except Exception as e:
        print(e)
        pass

    return x


if __name__ == '__main__':

    pandarallel.initialize(nb_workers=32)

    df = pd.read_csv('data/dataset.csv')
    df = df.sort_values('popularity', ascending=False)

    start = time.time()
    df = df.parallel_apply(search_genius, axis=1)
    end = time.time()
    print(end - start)

    df = df.fillna(0)
    for collumn in ['annotation_count', 'genius_track_id', 'pyongs', 'pageviews', 'lyrics_owner_id']:
        df[collumn] = df[collumn].astype(int)

    df.to_csv('data/songs.csv')
