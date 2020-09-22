#Natapol Thamwiwat 6030806121

import streamlit as st
import pandas as pd
import numpy as np
import folium as fo
from streamlit_folium import folium_static
import geopandas as gp
import altair as alt
import pydeck as pdk
#define name
st.title('Density Pick-up Information in Bangkok')
st.markdown(
"""
This is the information of picking-up user in Bangkok,
Please select date and time

""")

date_selected = st.sidebar.selectbox('Choose date 2019/01/',['01','02','03','04','05'])

#import data
DATE_TIME = 'timestart'
if date_selected =='01':
    DATA_URL = ("https://raw.githubusercontent.com/NatapolTha/streamlit/master/20190101.csv")
elif date_selected =='02':
    DATA_URL = ("https://raw.githubusercontent.com/NatapolTha/streamlit/master/20190102.csv")
elif date_selected =='03':
    DATA_URL = ("https://raw.githubusercontent.com/NatapolTha/streamlit/master/20190103.csv")
elif date_selected =='04':
    DATA_URL = ("https://raw.githubusercontent.com/NatapolTha/streamlit/master/20190104.csv")
elif date_selected =='05':
    DATA_URL = ("https://raw.githubusercontent.com/NatapolTha/streamlit/master/20190105.csv")
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, error_bad_lines=False)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_TIME] = pd.to_datetime(data[DATE_TIME])
    return data
data = load_data(70000)

#slidebar and data
hour = st.slider("Hour to look at", 0, 23, 0, 3)
data = data[data[DATE_TIME].dt.hour == hour]
crs = "EPSG:4326"
geometry = gp.points_from_xy(data.lonstartl,data.latstartl)
geo_data  = gp.GeoDataFrame(data,crs=crs,geometry=geometry)

#create map
st.subheader('Map @ %i:00' %hour)
lon = 100.523186
lat = 13.736717
station_map = fo.Map(
	location = [lat, lon], 
	zoom_start = 12)

latitudes = list(data.latstartl)
longitudes = list(data.lonstartl)
time = list(data.timestart)
labels = list(data.n)

#pop up
for lat, lng, t, label in zip(latitudes, longitudes, time, labels):
      if data.timestart[label].hour==hour and data.timestart[label].year!=2018:
        fo.Marker(
                    location = [lat, lng],
                    popup = label,
                    icon = fo.Icon(color='black', icon='heart')
        ).add_to(station_map)
folium_static(station_map)

#create data
st.subheader("Geo data between %i:00 and %i:00" % (hour, (hour + 3) % 24))
midpoint = (np.average(data["latstartl"]), np.average(data["lonstartl"]))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 8,
        "pitch": 30,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data,
            get_position=["lonstartl", "latstartl"],
            radius=90,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
        ),
    ],
))

#graph
st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 1))
]
hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "pickups": hist})
st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=['minute', 'pickups']
    ), use_container_width=True)
if st.checkbox("Show raw data", False):
    st.subheader("Raw data by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
    st.write(data)
