import pandas as pd
from game_data_fetch import get_token, api_call
from movie_show_data_fetch import (
    get_tmdb_show_data,
    get_tmdb_movie_data,
)
import tmdbsimple as tmdb

# Keys
# Movies and TV database key

k = "56b7978a58b581985e796e2e89fe8ac0"
tmdb.API_KEY = k
tmdb.REQUESTS_TIMEOUT = 5  # seconds, for both connect and read

# Game Database Keys

id = "5uw67iqnik8k47weous7kro35u4nud"
secret = "ahjonjggspq5b1uz5pqi72mv4s5dmj"
token = get_token(id, secret)


def process_data(key, id, secret, token):
    key = key
    id = id
    secret = secret

    # Make Data Frames
    movies = get_tmdb_movie_data()
    shows = get_tmdb_show_data()
    games = api_call(id, token)

    # Add Medium columns and prcoess data frames
    movies_df = pd.DataFrame(movies)
    shows_df = pd.DataFrame(shows)
    games_df = pd.DataFrame(games)

    movies_df["medium"] = "movie"
    shows_df["medium"] = "show"
    games_df["medium"] = "game"
    movies_df["rating"] = movies_df["rating"].round(1)
    shows_df["rating"] = shows_df["rating"].round(1)

    games_df.drop(
        ["id", "genres", "aggregated_rating", "critic_rating", "user_rating"],
        axis=1,
        inplace=True,
    )
    games_df["rating"] = games_df["rating"] / 10.0
    games_df["rating"].round(1)
    games_df.rename(columns={"genre_names": "genre", "name": "title"}, inplace=True)

    data = pd.concat([movies_df, shows_df, games_df], ignore_index=True)
    data = data.dropna()

    return data
