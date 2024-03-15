import tmdbsimple as tmdb

# Get API data


def fetch_movie_genre_mappings():
    genres = tmdb.Genres()
    movie_genres = genres.movie_list()
    return {genre["id"]: genre["name"] for genre in movie_genres["genres"]}


def fetch_tv_genre_mappings():
    genres = tmdb.Genres()
    tv_genres = genres.tv_list()
    return {genre["id"]: genre["name"] for genre in tv_genres["genres"]}


def get_tmdb_show_data():
    genre_mappings = fetch_tv_genre_mappings()
    # tmdb.API_KEY = key
    # tmdb.REQUESTS_TIMEOUT = 5  # seconds, for both connect and read
    shows = tmdb.TV()
    popular_shows = shows.popular()
    show_list = []
    for page in range(1, 16):  # Example: Fetch first 4 pages
        popular_shows = shows.popular(page=page)
        for show in popular_shows["results"]:
            genres = [
                genre_mappings.get(genre_id)
                for genre_id in show["genre_ids"]
                if genre_id in genre_mappings
            ]
            show_data = {
                "title": show["name"],
                "rating": show["vote_average"],
                "genre": genres,
            }
            show_list.append(show_data)
    return show_list


def get_tmdb_movie_data():
    genre_mappings = fetch_movie_genre_mappings()
    # tmdb.API_KEY = key
    # tmdb.REQUESTS_TIMEOUT = 5  # seconds, for both connect and read
    movies = tmdb.Movies()
    popular_movies = movies.popular()
    movie_list = []

    for page in range(1, 16):
        popular_movies = movies.popular(page=page)
        # print(f"Fetched {len(popular_movies['results'])} movies from page {page}")

        for movie in popular_movies["results"]:
            genres = [
                genre_mappings.get(genre_id)
                for genre_id in movie["genre_ids"]
                if genre_id in genre_mappings
            ]
            movie_data = {
                "title": movie["title"],
                "rating": movie["vote_average"],
                "genre": genres,
            }
            movie_list.append(movie_data)
    return movie_list
