# weather_app.py

import requests
import streamlit as st

API_key = '4254316d1ccf131f81e76d7ec009f94c'


def get_weather(api_key, city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    response = requests.get(base_url, params=params)
    weather_data = response.json()

    return weather_data


def get_custom_images():
    # Define a dictionary mapping weather descriptions to image URLs
    custom_images = {
        "moderate rain": "clear_sky.jpg",
        # "clear sky": "clear_sky.jpg",
        # "few clouds": "https://example.com/few_clouds_image.jpg",
        # "scattered clouds": "https://example.com/scattered_clouds_image.jpg",
        # "broken clouds": "clouds.png",
        # "shower rain": "https://example.com/shower_rain_image.jpg",
        # "rain": "https://example.com/rain_image.jpg",
        # # "moderate rain": "https://example.com/moderate_rain_image.jpg",
        # "thunderstorm": "https://example.com/thunderstorm_image.jpg",
        # "snow": "https://example.com/snow_image.jpg",
        # "mist": "https://example.com/mist_image.jpg"
    }
    return custom_images


def main():
    st.title("Weather App")

    # Get user input
    city = st.text_input("Enter the city name:", "London")
    api_key = API_key

    if st.button("Get Weather"):
        # Fetch weather data
        try:
            weather_data = get_weather(api_key, city)

            # Display weather information
            st.subheader(f"Weather Information for {city}")
            # st.write(f"**City:** {city}")
            st.write(f"**Temperature:** {weather_data['main']['temp']} °C")
            st.write(f"**Description:** {weather_data['weather'][0]['description']}")

            st.write(f"**Humidity:** {weather_data['main']['humidity']} %")
            st.write(f"**Wind Speed:** {weather_data['wind']['speed']} km/h")
            st.write(f"**Clouds:** {weather_data['clouds']['all']} %")
            st.write(f"**Pressure:** {weather_data['main']['pressure']} hPa")
            st.write(f"**Visibility:** {weather_data['visibility']} m")
            st.write(f"**Sunrise:** {weather_data['sys']['sunrise']} UTC")
            st.write(f"**Sunset:** {weather_data['sys']['sunset']} UTC")
            st.write(f"**Timezone:** {weather_data['timezone']} s")

            # Display weather images based on weather description
            # icon_url = f"http://openweathermap.org/img/wn/{weather_data['weather'][0]['icon']}.png"
            # st.image(icon_url, caption=weather_data['weather'][0]['description'], use_column_width=True)
            custom_images = get_custom_images()

            # Display custom weather image
            weather_description = weather_data['weather'][0]['description'].lower()

            if weather_description in custom_images:
                st.image(custom_images[weather_description], caption=weather_description, use_column_width=True)

            else:
                st.warning("Custom image not available for this weather description.")

        except Exception as e:
            st.error(f"Error fetching weather data: {e}")


if __name__ == "__main__":
    main()