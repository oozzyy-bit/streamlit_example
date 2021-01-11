import pandas as pd
import streamlit as st
import plotly.express as px

@st.cache
def get_data():
    url = "http://data.insideairbnb.com/united-states/ny/new-york-city/2019-09-12/visualisations/listings.csv"
    return pd.read_csv(url)
df = get_data()

st.title("Streamlit NYC Airbnb Deneme")
st.markdown("Airbnb datası üzerinde oynanmaya çalışılacak.")

st.dataframe(df.head())

cols = ["name", "host_name", "neighbourhood", "room_type", "price"]
st_ms = st.multiselect("Columns", df.columns.tolist(), default=cols)