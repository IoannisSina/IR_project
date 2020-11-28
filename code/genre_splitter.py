import pandas as pd
from ast import literal_eval


df = pd.read_csv('data/songs.csv')
df['genre'] = df.genre.apply(lambda x: literal_eval(x))
df = df.explode('genre').reset_index()

unique_genres = df.genre.unique()

for genre in list(unique_genres):
    temp_df = df[df.genre == genre].reset_index()
    del temp_df['genre']
    temp_df.to_csv('songs/' + genre + '.csv')

    temp_df.singer_ids = temp_df.singer_ids.apply(literal_eval)
    temp_df = temp_df[['singer_ids', 'popularity']].explode('singer_ids')
    temp_df = temp_df.groupby('singer_ids').mean().reset_index()

    temp_df.to_csv('artists/' + genre + '.csv')
