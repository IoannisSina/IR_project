import requests
import pandas as pd
from pandarallel import pandarallel
from ast import literal_eval
import API_keys

api_url = 'https://api.genius.com/artists/'
headers = {'Authorization': API_keys.genius_key }


def search_genius(x):

    try:
        r = requests.get(api_url + str(x.artist_id), headers=headers)
        result = r.json()['response']['artist']

        x['name'] = result['name']
        x['alternate_names'] = result['alternate_names']
        x['description'] = result['description'] != None
        x['facebook_name'] = result['facebook_name']
        x['twitter_name'] = result['twitter_name']
        x['instagram_name'] = result['instagram_name']
        x['followers_count'] = result['followers_count']
        x['url'] = result['url']
        x['is_verified'] = result['is_verified']
        x['user'] = result['user'] != None

    except requests.exceptions.RequestException as e:
        print(e)
        pass

    return x


if __name__ == '__main__':

    ids = []
    pandarallel.initialize()

    df = pd.read_csv('data/songs.csv')

    artist_ids = [literal_eval(s) for s in df['singer_ids'].tolist() + df['producer_ids'].tolist() + df['songwriter_ids'].tolist()]
    artist_ids = [item for sublist in artist_ids for item in sublist]
    artist_ids = set(artist_ids)

    df = pd.DataFrame(list(artist_ids), columns=['artist_id'])

    df = df.parallel_apply(search_genius, axis=1)
    df.to_csv('data/artists.csv')
