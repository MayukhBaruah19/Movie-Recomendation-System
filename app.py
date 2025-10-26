import streamlit as st
import pickle
import pandas as pd
import requests
import time
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer


# Fetch movie poster from TMDb

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    """
    Fetches the movie poster URL from TMDb API.
    Includes retries, error handling, and a fallback image.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"

    for attempt in range(3):  # Try up to 3 times
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses
            data = response.json()

            poster_path = data.get('poster_path')
            if not poster_path:
                return "https://via.placeholder.com/500x750?text=No+Poster+Available"

            return f"https://image.tmdb.org/t/p/w500/{poster_path}"

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}: Error fetching poster for ID {movie_id} -> {e}")
            time.sleep(1.5)  # Wait before retrying

    # If all retries fail, return placeholder
    return "https://via.placeholder.com/500x750?text=Poster+Unavailable"



# Load movie data and similarity matrix
try:
    movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movie_dict)
except Exception as e:
    st.error(f"Error loading movie_dict.pkl: {e}")
    st.stop()

try:
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("File 'similarity.pkl' not found. Please check the file path.")
    st.stop()
except Exception as e:
    st.error(f"Error loading similarity file: {e}")
    st.stop()



# Recommend movies
def recommend(movie):
    """
    Given a movie title, returns top 5 similar movies and their posters.
    """
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)

        # Fetch poster safely
        poster_url = fetch_poster(movie_id)
        recommended_posters.append(poster_url)

    return recommended_movies, recommended_posters



# Streamlit UI
st.title("🎬 Movie Recommendation System")

selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:", movies['title'].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
