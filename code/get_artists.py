import requests
import pandas as pd
from pandarallel import pandarallel
from ast import literal_eval
import API_keys
from bs4 import BeautifulSoup
import re

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
        if result['facebook_name']:
            x['facebook_likes'] = get_facebook_likes(result['facebook_name'])
        # if result['instagram_name']:
        #     x['instagram_likes'] = get_instagram_likes(result['instagram_name'])


    except requests.exceptions.RequestException as e:
        print(e)
        pass

    return x


def get_facebook_likes(fb_name=None):
    r = requests.get(url='https://www.facebook.com/' + fb_name)
    try:
        return int(re.search(r'Αρέσει σε ((\d+)(\.(\d+))*)', r.text).group(1).replace('.', ''))
    except:
        return None


def get_instagram_followers(insta_name=None):
    r = requests.get(url='https://www.instagram.com/' + insta_name)
    x = re.search(r'((\d+)((\.|,)\d+))?(k|m)? Followers', r.text).groups()

    if x[-1]:
        m = {'k': 3, 'm': 6}
        return int(float(x[0]) * (10 ** m[x[-1]]))
    else:
        return x[0].replace(',','')


if __name__ == '__main__':

    ids = []
    pandarallel.initialize()

    df = pd.read_csv('data/songs.csv')

    df.singer_ids = df.singer_ids.apply(literal_eval)
    df = df[['singer_ids', 'popularity']].explode('singer_ids')
    df = df.groupby('singer_ids').mean().reset_index()
    df.columns = ['artist_id', 'popularity']

    df = df.parallel_apply(search_genius, axis=1)
    df.to_csv('data/artists.csv')
