import requests


def get_token(client_id, client_secret):
    url = "https://id.twitch.tv/oauth2/token"
    body = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }
    response = requests.post(url, data=body)
    return response.json().get("access_token")


def genre_mappings(client_id, access_token):
    url = "https://api.igdb.com/v4/genres"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    body = "fields name; limit 300;"  # Modify as needed
    response = requests.post(url, headers=headers, data=body)
    genres = response.json()
    return {genre["id"]: genre["name"] for genre in genres}


def get_game_data(client_id, access_token, genre_mappings):
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    # Include both user and critic ratings in the fields
    body = "fields name,genres,rating,aggregated_rating; sort rating desc; limit 300;"  # Modify as needed
    response = requests.post(url, headers=headers, data=body)
    games = response.json()

    for game in games:
        if "genres" in game:
            game["genre_names"] = [
                genre_mappings.get(genre_id)
                for genre_id in game["genres"]
                if genre_id in genre_mappings
            ]
        # Keep ratings as they are without rounding
        if "rating" in game:
            game["user_rating"] = game["rating"]
        if "aggregated_rating" in game:
            game["critic_rating"] = game["aggregated_rating"]

    return games


# Example Usage
client_id = "5uw67iqnik8k47weous7kro35u4nud"
client_secret = "ahjonjggspq5b1uz5pqi72mv4s5dmj"
access_token = get_token(client_id, client_secret)


def api_call(id, token):
    if access_token:
        genres = genre_mappings(id, token)
        games = get_game_data(id, token, genres)
        # print(games)
        return games
    else:
        print("Failed to get access token")
