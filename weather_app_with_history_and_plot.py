import numpy as np
import requests
from pprint import pprint
import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns

API_KEY = '4254316d1ccf131f81e76d7ec009f94c'


# Funkcja djaca info na 4 dni

@st.cache_data
def get_hourly_forecast(api_key, city_name):
    parameters = {
        'q': city_name,
        'appid': api_key,
        "units": "metric"
    }
    response = requests.get('https://api.openweathermap.org/data/2.5/forecast', parameters)

    weather_data = response.json()
    # pprint(weather_data)

    # st.write(weather_data)

    st.session_state.weather_data = weather_data['list']


# Funkcja dajaca wynik historii
def add_to_history(search_history, city_in_history):
    if city_in_history not in search_history:
        search_history.append(city_in_history)


# Funkcja by zobazyc historie
def display_search_history(search_history):
    st.subheader("Search History")
    for search_city in search_history:
        st.write(f"- {search_city}")


@st.cache_data
def convert_data_to_dataframe(hourly_forecast_data):
    st.subheader("Hourly Forecast for 4 days (Every hour)")

    main_metrics = {
        "temp": [],
        "feels_like": [],
        "temp_min": [],
        "temp_max": [],
        "pressure": [],
        "sea_level": [],
        "grnd_level": [],
        "humidity": [],
        "temp_kf": []
    }

    weather_metrics = {
        "id": [],
        "main": [],
        "description": [],
        "icon": [],

    }

    wind_metrics = {
        "speed": [],
        "deg": [],
        "gust": []
    }

    time_metrics = {
        "dt": [],
        "dt_txt": []
    }

    clouds_and_visibility = {
        "clouds": [],
        "visibility": []
    }
    for entry in hourly_forecast_data:
        main = entry['main']

        weather = entry['weather'][0]

        wind = entry['wind']

        for key in main_metrics.keys():
            main_metrics[key].append(main.get(key, "None"))

        for key in weather_metrics.keys():
            weather_metrics[key].append(weather.get(key, "None"))

        for key in wind_metrics.keys():
            wind_metrics[key].append(wind.get(key, "None"))

        clouds = entry['clouds'].get('all', "None")

        clouds_and_visibility['clouds'].append(clouds)

        visibility = entry.get('visibility', "None")

        clouds_and_visibility["visibility"].append(visibility)

        dt = entry["dt"]

        time_metrics["dt"].append(dt)

        dt_txt = entry["dt_txt"]

        time_metrics["dt_txt"].append(dt_txt)

    merged_weather_data = {**main_metrics, **weather_metrics, **wind_metrics, **time_metrics, **clouds_and_visibility}

    df = pd.DataFrame(merged_weather_data)

    df['dt_txt'] = pd.to_datetime(df['dt_txt'])

    return df


def display_hist_chart(feature, df):
    try:

        fig, ax = plt.subplots()

        sns.histplot(x=feature, data=df, ax=ax)

        st.pyplot(fig)
        st.write('test')
    except Exception as e:
        st.write(e)


def display_charts(df: pd.DataFrame):
    st.write(hourly_df.head(15))

    output = st.selectbox(label="Wybierz wskazniki", options=df.columns)

    display_hist_chart(output, df)


# Streamlit App
st.title('Aplikacja pogodowa')

# Get the search history from session state, initialize if not exists
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Text input for city
city = st.text_input("Wpisz miasto:", "Wroclaw")

# Button to search for weather
hourly_df = None

if st.button('Znajdz pogode'):
    try:
        get_hourly_forecast(API_KEY, city)

        # Add the city to the search history
        add_to_history(st.session_state.search_history, city)

        # Display search history
        display_search_history(st.session_state.search_history)

        # Display hourly forecast chart (every 4 hours) using Altair as a bar chart
        hourly_df = convert_data_to_dataframe(st.session_state.weather_data)








    except Exception as e:
        st.write(e)

if hourly_df is not None:
    display_charts(hourly_df)