from data_processing import process_data
from game_data_fetch import get_token
import tmdbsimple as tmdb
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from scipy.spatial import distance
import ast  # tokenization
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib import cm
# Keys
# Movies and TV database key

k = "56b7978a58b581985e796e2e89fe8ac0"
tmdb.API_KEY = k
tmdb.REQUESTS_TIMEOUT = 5  # seconds, for both connect and read

# Game Database Keys

id = "5uw67iqnik8k47weous7kro35u4nud"
secret = "ahjonjggspq5b1uz5pqi72mv4s5dmj"
token = get_token(id, secret)

data = process_data(k, id, secret, token)
data.to_csv("final_test_rec.csv", index=False)

print(len(data))


def safe_literal_eval(s):
    try:
        # Try to evaluate as a Python literal
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        # If error, return the original string
        return s


# Apply this function to the 'genre' column
data["genre"] = data["genre"].apply(safe_literal_eval)
# ensure that each entry in 'genre' is a list
# If an entry is not a list, wrap it in a list
data["genre"] = data["genre"].apply(lambda x: x if isinstance(x, list) else [x])
# One-hot encoding for 'genre'
genre_df = data["genre"].explode().str.get_dummies().groupby(level=0).sum()
# One-hot encoding for 'medium'
medium_df = pd.get_dummies(data["medium"])
# Combine these with the 'rating' column
features_df = pd.concat([data[["rating"]], genre_df, medium_df], axis=1)
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features_df)


def weighted_distance(point_a, point_b):
    # Define the weight inside the function
    rating_weight = 2
    medium_weight = 5

    # Assuming the rating is the first feature
    rating_dist = (point_a[0] - point_b[0]) ** 2 * rating_weight
    medium_dist = distance.euclidean(point_a[-3:], point_b[-3:]) * medium_weight
    other_features_dist = distance.euclidean(point_a[1:-3], point_b[1:-3])
    return rating_dist + other_features_dist + medium_dist


knn = NearestNeighbors(n_neighbors=7, metric=weighted_distance)
knn.fit(features_scaled)


genres = sorted(set(genre for sublist in data["genre"] for genre in sublist))


def get_user_profile(genres, preference):
    user_profile = [preference["rating"]] + [
        1 if genre in preference["liked_genres"] else 0 for genre in genres
    ]
    user_profile += preference["medium_preference"]
    return user_profile


# Example user preference
user_preference = {
    "rating": 8.5,
    "liked_genres": ["Action", "Adventure", "Fantasy", "RPG"],
    "medium_preference": [1, 0, 0],  # 1 for movie, 0 for show and game
}


def create_scaled_user_profile(user_preference, genres, scaler):
    user_profile = (
        [user_preference["rating"]]
        + [1 if genre in user_preference["liked_genres"] else 0 for genre in genres]
        + user_preference["medium_preference"]
    )

    # Scale the user profile in the same way as the training data
    user_profile_scaled = scaler.transform([user_profile])
    return user_profile_scaled[0]


user_profile_scaled = create_scaled_user_profile(user_preference, genres, scaler)
distances, indices = knn.kneighbors([user_profile_scaled], n_neighbors=20)
recommended_items = data.iloc[indices[0]]


def is_user_preference_weak(preference):
    # Example criteria: weak preference if no genre is specified, or all medium preferences are neutral
    no_genre_preference = not preference["liked_genres"]
    neutral_medium_preference = all(m == 0 for m in preference["medium_preference"])
    return no_genre_preference or neutral_medium_preference


def get_exploratory_recommendations(data, n_recommendations=10):
    # Select a random sample of items for a broader exploration
    random_sample = data.sample(n=n_recommendations * 2)

    # Prioritize diversity: Aim for a mix of genres, mediums, and possibly novelty
    diverse_items = []
    seen_genres = set()
    seen_mediums = set()

    for _, row in random_sample.iterrows():
        if len(diverse_items) >= n_recommendations:
            break
        genre = tuple(row["genre"])  # Convert list to tuple for set operations
        medium = row["medium"]

        # Check if this item adds diversity
        if genre not in seen_genres or medium not in seen_mediums:
            diverse_items.append(row)
            seen_genres.add(genre)
            seen_mediums.add(medium)

    return pd.DataFrame(diverse_items)


def get_diverse_recommendations(
    knn_model, user_profile_scaled, data, n_recommendations=10, max_per_medium=3
):
    distances, indices = knn_model.kneighbors(
        [user_profile_scaled], n_neighbors=n_recommendations * 20
    )
    recommended_items = data.iloc[indices[0]]
    diverse_recommendations = []
    medium_count = {"movie": 0, "show": 0, "game": 0}

    for index, row in recommended_items.iterrows():
        medium = row["medium"]
        if medium_count[medium] < max_per_medium:
            diverse_recommendations.append(row)
            medium_count[medium] += 1

        if not genres:
            continue

        if len(diverse_recommendations) >= n_recommendations:
            break

    return pd.DataFrame(diverse_recommendations)


# Determine if the user preference is weak
if is_user_preference_weak(user_preference):
    # Get exploratory recommendations for non-specific preferences
    recommendations = get_exploratory_recommendations(data, n_recommendations=10)
    # Print Recommended Items
    print(
        f"For Neutral User Preferences of: Rating >= {user_preference['rating']}, Genres: {', '.join(user_preference['liked_genres'])}, Type: {'Movie' if user_preference['medium_preference'][0] else 'Show/Game'}"
    )
    print("Neutal Recommended Items:")
    print(recommendations[["title", "genre", "rating", "medium"]])

else:
    # Get diverse recommendations for specific preferences
    diverse_recommendations = get_diverse_recommendations(
        knn,
        user_profile_scaled,
        data,
        n_recommendations=10,
        max_per_medium=3,
    )
    highly_rated_recommended_items = diverse_recommendations[
        diverse_recommendations["rating"] >= 8.0
    ]
    highly_rated_recommended_items.sort_values(
        by="rating", ascending=False, inplace=True
    )
    final_recommendations = highly_rated_recommended_items.head(10)
    recommendations = final_recommendations
    print(
        f"For User Preferences Based On: Rating >= {user_preference['rating']}, Genres: {', '.join(user_preference['liked_genres'])}, Type: {'Movie' if user_preference['medium_preference'][0] else 'Show/Game'}"
    )
    print("Recommended Items:")
    print(recommendations[["title", "genre", "rating", "medium"]])


# Visualizations


# Neutral user profile
neutral_user_preference = {
    "rating": 5.0,  # Neutral rating
    "liked_genres": [],  # No specific genre
    "medium_preference": [0, 0, 0],  # No medium preference
}
neutral_user_profile = create_scaled_user_profile(
    neutral_user_preference, genres, scaler
)
neutral_recommendations = get_exploratory_recommendations(data, n_recommendations=10)

# User with preferences
preferred_user_preference = {
    "rating": 9.0,  # High rating preference
    "liked_genres": ["Action", "Adventure"],  # Specific genres
    "medium_preference": [1, 0, 0],  # Preference for movies
}
preferred_user_profile = create_scaled_user_profile(
    preferred_user_preference, genres, scaler
)
distances, indices = knn.kneighbors([preferred_user_profile], n_neighbors=20)
preferred_recommendations = data.iloc[indices[0]].head(10)


pca = PCA(n_components=2)
reduced_features = pca.fit_transform(features_scaled)


preferred_recommendations.reset_index(drop=True, inplace=True)

# Get indices for neutral and preferred recommendations
neutral_indices = neutral_recommendations.index
preferred_indices = preferred_recommendations.index

# Prepare the indices for highest-rated show, movie, and game
highest_rated_show = (
    recommendations[recommendations["medium"] == "show"]
    .sort_values(by="rating", ascending=False)
    .head(1)
)
highest_rated_movie = (
    recommendations[recommendations["medium"] == "movie"]
    .sort_values(by="rating", ascending=False)
    .head(1)
)
highest_rated_game = (
    recommendations[recommendations["medium"] == "game"]
    .sort_values(by="rating", ascending=False)
    .head(1)
)


def annotate_recommended_points(indices, reduced_features, data, ax, max):
    count = 0
    for idx in indices:
        if idx >= len(data) or count >= max:
            continue
        item = data.iloc[idx]
        annotation_text = f"{item['title']}\nMedium: {item['medium']}\nGenre: {', '.join(item['genre'])}"
        ax.annotate(
            annotation_text,
            (reduced_features[idx, 0], reduced_features[idx, 1]),
            textcoords="offset points",
            xytext=(-50, 10),
            ha="left",
            va="bottom",
            fontsize=6,
            arrowprops=dict(arrowstyle="->", color="black"),
        )
        count += 1


fig = plt.figure(figsize=(18, 16))  # Adjust figsize as needed
gs = GridSpec(2, 2, figure=fig)
cmap = cm.get_cmap("Set2")


# Overall plot with all items and highlighted recommendations
ax0 = fig.add_subplot(gs[:, 0])
ax0.scatter(
    reduced_features[:, 0],
    reduced_features[:, 1],
    color=cmap(2),
    alpha=0.5,
    label="All Items",
)
ax0.scatter(
    reduced_features[neutral_indices, 0],
    reduced_features[neutral_indices, 1],
    color=cmap(1),
    label="Neutral User Recs",
)
ax0.scatter(
    reduced_features[preferred_indices, 0],
    reduced_features[preferred_indices, 1],
    color=cmap(0),
    label="Preferred User Recs",
)
ax0.set_xlabel("PCA Feature 1")
ax0.set_ylabel("PCA Feature 2")
ax0.set_title("All Items and Recommendation Clusters")
ax0.legend()

# Neutral user recommendations plot
ax1 = fig.add_subplot(gs[0, 1])
ax1.scatter(
    reduced_features[neutral_indices, 0],
    reduced_features[neutral_indices, 1],
    color=cmap(1),
    label="Neutral User Recs",
    s=50,
)
annotate_recommended_points(neutral_indices, reduced_features, data, ax1, max=1)
ax1.set_xlabel("")
ax1.set_ylabel("")
ax1.set_xticklabels([])
ax1.set_yticklabels([])
ax1.set_title("User Neutral Prefrence Recommendations")
ax1.legend()

# Preferred user recommendations plot
ax2 = fig.add_subplot(gs[1, 1])
ax2.scatter(
    reduced_features[preferred_indices, 0],
    reduced_features[preferred_indices, 1],
    color=cmap(0),
    label="User Preference Recs",
    s=50,
)
annotate_recommended_points(preferred_indices, reduced_features, data, ax2, max=1)
ax2.set_xlabel("")
ax2.set_ylabel("")
ax2.set_xticklabels([])
ax2.set_yticklabels([])
ax2.set_title("User Prefrence Recommendations")
ax2.legend()

plt.tight_layout()
plt.show()
