import streamlit as st
import streamlit as st
import pickle
import pandas as pd
import numpy as np
import requests
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer


def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(
        movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path


# Load pickle files
movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movie_dict)

count_vector = CountVectorizer(max_features=5000, stop_words='english')
vector = count_vector.fit_transform(movies['tags']).toarray()
similarity = cosine_similarity(vector)

try:
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    print("File not found. Please check the path to 'movies_list.pkl'.")
except Exception as e:
    print(f"An error occurred: {e}")
# similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recomendation System')


def recommended(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distance = similarity[movie_index]
    movie_list = sorted(list(enumerate(distance)),
                        reverse=True, key=lambda x: x[1])[1:6]

    recomended_movie = []
    recomended_movie_poster = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id

        # fetch poster from API
        recomended_movie.append(movies.iloc[i[0]].title)
        recomended_movie_poster.append(fetch_poster(movie_id))
    return recomended_movie, recomended_movie_poster


selected_movie_name = st.selectbox(
    "Select The Movie", movies['title'].values)

# st.button("Reset", type="primary")
if st.button("Recomend"):
    names, posters = recommended(selected_movie_name)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])

    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])
