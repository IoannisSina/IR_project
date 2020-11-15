import pandas as pd

df = pd.read_csv('data/SpotifyFeatures.csv')
df = df.groupby('track_id').agg({'track_name':'first', 'artist_name': 'first', 'popularity': 'first', 'genre': lambda x: x.unique().tolist()})
df.to_csv('data/dataset.csv')
