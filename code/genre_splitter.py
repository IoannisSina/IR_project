import pandas as pd
from ast import literal_eval


df = pd.read_csv('data/songs.csv', index_col=0)
df['genre'] = df.genre.apply(lambda x: literal_eval(x))
df = df.explode('genre').reset_index(drop=True)

unique_genres = df.genre.unique()

for genre in list(unique_genres):
    temp_df = df[df.genre == genre].reset_index(drop=True)
    del temp_df['genre']
    temp_df.to_csv('songs/' + genre + '.csv')

    temp_df.singer_ids = temp_df.singer_ids.apply(literal_eval)
    temp_df = temp_df[['singer_ids', 'songwriter_ids', 'popularity']].explode('singer_ids')
    temp_df = temp_df.groupby('singer_ids').mean()#.reset_index(drop=True)

    temp_df.sort_values('popularity', inplace=True, ascending=False)
    temp_df['is_popular'] = pd.Series()
    temp_df.iloc[:int(len(temp_df)*.2), temp_df.columns.get_loc('is_popular')] = 1
    temp_df.iloc[int(len(temp_df)*.2):, temp_df.columns.get_loc('is_popular')] = 0


    temp_df.to_csv('artists/' + genre + '.csv')
