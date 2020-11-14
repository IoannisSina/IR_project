import requests
import pandas as pd
from pandarallel import pandarallel
import API_keys

api_url = 'https://api.genius.com/search?q='
headers = {'Authorization': API_keys.genius_key }
def search_genius(x):

    try:
        r = requests.get(api_url + x.track_name + ' ' + x.artist_name, headers=headers)
        result = r.json()['response']['hits'][0]['result']

        x['annotation_count'] = result['annotation_count']
        x['song_id'] = result['id']
        x['pyongs'] = result['pyongs_count']
        x['lyrics_owner_id'] = result['lyrics_owner_id']
        x['hot'] = result['stats']['hot']
        x['pageviews'] = result['stats']['pageviews'] if 'pageviews' in result['stats'] else None

        artist_name = result['primary_artist']['name']

        if '&' in artist_name:
            artist_ids = []
            names = [name.strip() for name in artist_name.split('&')]
            for name in names:
                r = requests.get(api_url + name, headers=headers)
                hits = r.json()['response']['hits']
                for hit in hits:
                    if hit['result']['primary_artist']['name'] == name:
                        artist_ids.append(hit['result']['primary_artist']['id'])
                        break
            
            x['artist_ids'] = artist_ids
            return x

        x['artist_ids'] = [result['primary_artist']['id'] if 'id' in result['primary_artist'] else None]

    except requests.exceptions.RequestException as e:
        # print(e)
        pass

    return x


if __name__ == '__main__':

    pandarallel.initialize()

    df = pd.read_csv('dataset.csv')
    df = df.sort_values('popularity', ascending=False)
    df = df.head(100)

    df = df.parallel_apply(search_genius, axis=1)

    df = df.fillna(0)
    for collumn in ['annotation_count', 'song_id', 'pyongs', 'pageviews', 'lyrics_owner_id']:
        df[collumn] = df[collumn].astype(int)

    df.to_csv('songs.csv')
