# Data set https://www.kaggle.com/datasets/duongtruongbinh/manga-and-anime-dataset?select=manga.csv


# Add axis + titles on them 
# create subplots + fix multivariable one 
# Do the last visualization comment + clean up code 

# Reading in the data 
import pandas as pd 
import numpy as np 
data = "~/Documents/School/data/manga.csv"
manga_data = pd.read_csv(data)
#print(manga_data.head())
#print(manga_data.info())
# 1. Visualization of a single quantitative data variable
import plotly.graph_objects as go 
x = np.array(manga_data['Score'])
fig = go.Figure()
"""
fig.add_trace(go.Box(x=x, name='Ratings', boxpoints=False, marker_color='rgb(159, 157, 209)')) 

fig.update_layout(
    title='Rating Distribution',
    yaxis=dict(
        autorange=True,
        showgrid=False,
        zeroline=True,
        gridcolor='rgb(255, 255, 255)',
        gridwidth=1,
    ),
    paper_bgcolor='rgb(255, 255, 255)',
    plot_bgcolor='rgb(255, 255, 255)',
    showlegend=False
)
"""
# 2. Visualizaiton combining one quantitative and one qualitative data variable
# Preprocessing the 'Genres' data

manga_data['Genres'] = manga_data['Genres'].astype(str)
# Clean up each invidiual genre 
def clean_genres(genre):
    for char in ['[', ']', ' ']:
        genre = genre.replace(char, '')
    return genre

genre_data = []
for i, row in manga_data.iterrows():
    genres = row['Genres'].split(', ')
    for genre in genres:
        cleaned_genre = clean_genres(genre)
        genre_data.append({'Title': row['Title'], 'Score': row['Score'], 'Genre': cleaned_genre})
genre_data = pd.DataFrame(genre_data)
genre_data = genre_data[genre_data['Genre']!= '']
#print(genre_data.head())

genres = genre_data['Genre'].unique()
for genre in genres:
    genre_score = genre_data[genre_data['Genre']==genre]['Score']
    fig.add_trace(go.Violin(y=genre_score, name=genre))

fig.update_layout(
    yaxis=dict(
        autorange=True,
        showgrid=False,
        zeroline=True,
        gridcolor='rgb(255, 255, 255)',
        gridwidth=1),
    plot_bgcolor='rgb(255, 255, 255)')
"""
# 3. Visualization representing more than two data variables SPLIT THIS INTO TWO WITH NA VALUES
# Normalize Data for size

manga_data['Chapters'] = pd.to_numeric(manga_data['Chapters'], errors='coerce')
manga_data['Chapters'] = manga_data['Chapters'].fillna(0)

max_chp = manga_data['Chapters'].max()

manga_data['Normalized Chapters'] = manga_data['Chapters'] / max_chp * 100

manga_data['Members'] = pd.to_numeric(manga_data['Members'], errors='coerce')

# Handle NaN values if necessary (e.g., fill with 0 or drop them)
manga_data['Members'] = manga_data['Members'].fillna(0)

fig.add_trace(go.Scatter(x=manga_data['Score'], y=manga_data['Members'], mode='markers', marker = dict(size=manga_data['Normalized Chapters'], color = manga_data['Score'], colorscale='Viridis'), text=manga_data['Title']))
fig.update_layout(
    showlegend =False
)

# 4. Visualization involving two quantitative data variables
 
jitter_points = manga_data['Popularity'] + np.random.uniform(-2, 2, size=len(manga_data))
fig.add_trace(go.Scatter(
    x=jitter_points, 
    y=manga_data['Score'], 
    mode='markers',
    text=manga_data['Title'],
    hoverinfo='text+x+y'
))
fig.update_layout(title='Manga Popularity vs Score', xaxis_title='Popularity', yaxis_title='Score', plot_bgcolor='rgb(255, 255, 255)', showlegend=False)
"""
# 5. Figure containing at least three subplots 
#
#print(manga_data.info())
fig.show()
