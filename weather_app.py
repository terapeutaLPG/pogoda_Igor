import requests
from pprint import pprint
# streamlit
# pandas
# seaborn
# matplotlib
# requests
import streamlit as st
import pandas as pd
from datetime import datetime
import time
import seaborn as sns



import matplotlib.pyplot as plt

API_KEY = '4254316d1ccf131f81e76d7ec009f94c'


def add_progress_bar():
    widget_container = st.empty()
    progress_bar = widget_container.progress(0)

    for i in range(100):
        progress_bar.progress(i + 1)
        time.sleep(0.01)

    if progress_bar.progress(100):
        widget_container.empty()


def get_weather_info(api_key, city_name):
    parameters = {
        'q': city_name,
        'appid': api_key,
        "units": "metric"

    }

    try:

        if 'weather_data' not in st.session_state or st.session_state.current_city != st.session_state.city_history[-1]:

            response = requests.get('https://api.openweathermap.org/data/2.5/forecast', parameters)

            weather_data = response.json()

            if weather_data['cod'] != '200':
                raise ValueError

            st.session_state.weather_data = weather_data['list']

            add_progress_bar()
            return weather_data['list']
        else:

            return st.session_state.weather_data

    except ValueError as error:
        st.write('Takie miasto nie istnieje w bazie danych')
        st.write(error)


def display_history(city_history):
    st.subheader('Historia wyszukiwania')

    for search_city in city_history:
        st.write(f"- {search_city}")


def add_city_history(provided_city):
    st.session_state.city_history.append(provided_city)


def convert_data_to_dataframe(hourly_forecast_data, which_day=None):
    st.subheader("Prognoza godzinowa na 4 dni (Co godzinę)")

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

    lst = []

    hours = []

    for row in df['dt_txt']:
        row = str(row)

        row = row.split('-')

        day, hour = row[2].split(' ')

        hours.append(hour.split(':')[0])

        lst.append(day)

    df['day'] = lst
    df['hour'] = hours

    # df.to_csv('tabela.csv')

    if which_day is not None:
        df = df[df['day'] == which_day]
    return df


def display_temp_line_chart(df):
    chart_data = df[["temp", "temp_min", "temp_max", "day"]]

    chart_data = chart_data.groupby('day').agg(Avg_temp=('temp', 'mean')).reset_index().rename(columns=
                                                                                               {'day': 'Dzien',
                                                                                                'Avg_temp': 'Srednia_temperatura'})

    st.subheader('Średnia temperatura danego dnia')

    st.line_chart(data=chart_data, x='Dzien', y='Srednia_temperatura', use_container_width=True)


def display_customized_line_chart(df, selected_column, pl_choice):
    chart_data = df[[selected_column, "day"]]

    chart_data = chart_data.groupby('day').agg(Avg_choice=(selected_column, 'mean')).reset_index().rename(columns=
    {
        'day': 'Dzien',
        'Avg_choice': pl_choice})

    st.subheader(f'Średnia {pl_choice} danego dnia')

    fig, ax = plt.subplots()

    sns.lineplot(data=chart_data, x='Dzien', y=pl_choice, ax=ax)

    st.pyplot(fig)


def display_customized_line_hour_chart(df, selected_column, pl_choice):
    chart_data = df[[selected_column, "hour"]]

    chart_data = chart_data.rename(columns=
    {
        'hour': 'Godzina',
        selected_column: pl_choice})

    st.subheader(f'Średnia {pl_choice} w danej godzinie')

    fig, ax = plt.subplots()

    sns.lineplot(data=chart_data, x='Godzina', y=pl_choice, ax=ax)

    st.pyplot(fig)


def get_current_day_name():
    dt = datetime.now()

    day_name = dt.strftime('%A')

    week_days = {
        'Monday': 'Poniedziałek',
        'Tuesday': 'Wtorek',
        'Wednesday': 'Środa',
        'Thursday': 'Czwartek',
        'Friday': 'Piątek',
        'Saturday': 'Sobota',
        'Sunday': 'Niedziela'
    }

    day_names = []

    week_days_keys = list(week_days.keys())

    for idx, key in enumerate(week_days_keys):
        if key == day_name:
            day_names.append(week_days[key])
            for i in range(1, 4):
                day_names.append(week_days[week_days_keys[idx + i]])

    return day_names


def get_current_day_numerical():
    dt = datetime.now()

    day_of_month = dt.day

    return [day_of_month + idx for idx in range(4)]


def set_selected_day(btn_key):
    st.session_state.selected_day = True
    st.session_state.button_pressed = btn_key


def reset_selected_day():
    st.session_state.selected_day = False
    st.session_state.button_pressed = None


def show_weather_buttons():
    btn_cols = st.columns(5)

    day_names = get_current_day_name()

    days_numerical = get_current_day_numerical()

    for idx, col in enumerate(btn_cols):

        if idx < len(btn_cols) - 1:
            btn_key = f'button_day_{days_numerical[idx]}'
            col.button(day_names[idx], key=btn_key, on_click=set_selected_day, args=[btn_key])
        else:
            col.button('Reset', key='reset_button', on_click=lambda: reset_selected_day())


def select_customized_plot(df):
    polish_choices = ['Temperatura', 'Temperatura minimalna', 'Temperatura maksymalna',
                      'Temperatura odczuwalna', 'Ciśnienie', 'Wilgotność', 'Zachmurzenie',
                      'Widoczność', 'Prędkość wiatru']
    with st.expander('Wykresy'):
        choice = st.selectbox('Wybierz kolumnę',
                              options=polish_choices)

        if choice:
            english_choices = ['temp', 'temp_min', 'temp_max', 'feels_like', 'pressure', 'humidity',
                               'clouds',
                               'visibility', 'speed']

            choice = english_choices[polish_choices.index(choice)]
            display_customized_line_chart(df, choice,
                                          polish_choices[english_choices.index(choice)])

            display_boxplot(df, choice,
                            polish_choices[english_choices.index(choice)])


def display_pairplot(df):
    columns_to_visualize = ['temp', 'temp_min', 'temp_max', 'feels_like', 'day']
    try:

        g = sns.pairplot(df[columns_to_visualize], hue='day')
        fig = plt.gcf()
        ax = plt.gca()

        # Display the plot in Streamlit
        st.pyplot(fig)

    except Exception as e:
        st.write(e)


def display_boxplot(df, selected_column, pl_choice):
    fig, ax = plt.subplots()
    df = df.copy().rename(columns={'day': 'Dzien', selected_column: pl_choice})
    sns.boxplot(data=df, x="Dzien", y=pl_choice, ax=ax, fill=False)

    st.pyplot(fig)


def display_catplot(df):
    df = df.copy().rename(columns={'day': 'Dzien'})

    fig, ax = plt.subplots()

    data_melted = pd.melt(df[['Dzien', 'temp_min', 'temp_max', 'temp']], id_vars='Dzien', var_name='Temperature',
                          value_name='Values')

    sns.barplot(x='Dzien', y='Values', hue='Temperature', data=data_melted)

    ax.set_xlabel('Dni')
    ax.set_ylabel('Temperatura')
    ax.set_title('Porównanie temperatury maksymalnej, minimalnej i średniej')
    ax.legend()

    st.pyplot(fig)


def show_general_plots(df):
    if st.session_state.selected_day is True:
        return
    display_temp_line_chart(df)

    display_pairplot(df)
    display_catplot(df)
    select_customized_plot(df)


def select_customized_hour_plot(df):
    polish_choices = ['Temperatura', 'Temperatura minimalna', 'Temperatura maksymalna',
                      'Temperatura odczuwalna', 'Ciśnienie', 'Wilgotność', 'Zachmurzenie',
                      'Widoczność', 'Prędkość wiatru']
    with st.expander('Wykresy'):
        choice = st.selectbox('Wybierz kolumnę',
                              options=polish_choices)

        if choice:
            english_choices = ['temp', 'temp_min', 'temp_max', 'feels_like', 'pressure', 'humidity',
                               'clouds',
                               'visibility', 'speed']

            choice = english_choices[polish_choices.index(choice)]
            display_customized_line_hour_chart(df, choice,
                                               polish_choices[english_choices.index(choice)])


def show_general_hour_plots(df):
    if st.session_state.selected_day is False:
        return

    select_customized_hour_plot(df)


def show_weather_hour_info(df, selected_which_day):
    if not st.session_state.selected_day:
        return
    st.subheader('Zobacz godzinną pogodę dla wybranego dnia')
    val = st.slider('Wybierz godzinę', min_value=0, max_value=21, step=3, key='hour_slider')

    df = df[df['hour'].astype('int64') == int(val)]
    df = df.query('day == @selected_which_day')

    if df.shape[0] <= 0:
        st.write('Brak danych dla wybranej godziny')
        return
    temp_cols = st.columns(4)

    temp_cols[0].metric(label='Temperatura', value=df['temp'].values[0], delta=df['temp_kf'].values[0])

    temp_cols[1].metric(label='Temperatura odczuwalna', value=df['feels_like'].values[0], delta=df['temp_kf'].values[0])

    # Show minimal and maximal temperature
    temp_cols[2].metric(label='Temperatura minimalna', value=df['temp_min'].values[0], delta=df['temp_kf'].values[0])

    temp_cols[3].metric(label='Temperatura maksymalna', value=df['temp_max'].values[0], delta=df['temp_kf'].values[0])

    # show humidity, vibisility and pressure

    humidity_cols = st.columns(8)

    humidity_cols[0].metric(label='Wilgotność', value=df['humidity'].values[0])

    # Add some humidity icon
    humidity_cols[1].image('humidity.png', width=20)

    st.metric(label='Widoczność', value=df['visibility'].values[0])

    st.metric(label='Ciśnienie', value=df['pressure'].values[0])

    # show wind speed

    st.metric(label='Prędkość wiatru', value=df['speed'].values[0])

    # show clouds

    st.metric(label='Zachmurzenie', value=df['clouds'].values[0])

    # show weather description

    st.metric(label='Opis pogody', value=df['description'].values[0])

    # show weather icon

    st.image(f"http://openweathermap.org/img/wn/{df['icon'].values[0]}.png")


st.title('Aplikacja pogodowa 🌡️')

city = st.text_input("Wpisz miasto:", "Wroclaw", key='current_city')

st.button('Znajdź pogodę', on_click=lambda: get_weather_info(API_KEY, city))


if 'selected_day' not in st.session_state:
    st.session_state.selected_day = False
if 'button_pressed' not in st.session_state:
    st.session_state.button_pressed = None

try:

    if 'weather_data' in st.session_state:

        which_day = None

        if st.session_state.button_pressed is not None:
            which_day = st.session_state.button_pressed.split('_')[-1]
            # which = 18
        hourly_forecast_df = convert_data_to_dataframe(st.session_state.weather_data, which_day=which_day)

        show_weather_buttons()

        show_general_plots(hourly_forecast_df)

        show_general_hour_plots(hourly_forecast_df)

        show_weather_hour_info(hourly_forecast_df, which_day)

        if 'city_history' not in st.session_state:
            st.session_state.city_history = []

        if len(st.session_state.city_history) == 0 or st.session_state.current_city != st.session_state.city_history[
            -1]:
            add_city_history(city)
        display_history(st.session_state.city_history)


except KeyError:
    st.write('Nie ma takiego miasta')
except Exception as error:
    st.write(error)