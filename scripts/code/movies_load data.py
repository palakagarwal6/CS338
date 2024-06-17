import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def select_file():
    Tk().withdraw()  
    file_path = askopenfilename()  
    return file_path


file_path = select_file()
df = pd.read_csv(file_path, encoding='utf-8')  


df.columns = df.columns.str.strip()


df.rename(columns={
    'id': 'movie_id',
    'title': 'title',
    'overview': 'overview',
    'status': 'status',
    'release_date': 'release_date',
    'adult': 'adult',
    'video': 'video',
    'runtime': 'runtime',
    'vote_average': 'vote_average',
    'vote_count': 'vote_count'
}, inplace=True)


df = df[['movie_id', 'title', 'overview', 'status', 'release_date', 'adult', 'video', 'runtime', 'vote_average', 'vote_count']]


df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce').dt.date


df['title'].fillna('No Title', inplace=True)
df['overview'].fillna('No Overview', inplace=True)
df['status'].fillna('Released', inplace=True)
df['release_date'].fillna(pd.NaT, inplace=True)
df['adult'].fillna('False', inplace=True)
df['video'].fillna('False', inplace=True)
df['runtime'].fillna(0, inplace=True)
df['vote_average'].fillna(0.0, inplace=True)
df['vote_count'].fillna(0, inplace=True)


df['adult'] = df['adult'].astype(str)
df['video'] = df['video'].astype(str)


movies_metadata1 = 'movies_metadata2.csv' 
df.to_csv(movies_metadata1, index=False, encoding='utf-8') 

print(f'CSV file saved as {movies_metadata1}')
