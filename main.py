import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib
import matplotlib.pyplot as plt

@st.cache
def get_data():
    return pd.read_csv("http://data.insideairbnb.com/turkey/marmara/istanbul/2020-12-31/visualisations/listings.csv")

df = get_data()
st.title("Streamlit-Airbnb Data Ananizi")
st.dataframe(df.head())


st.header("En pahalı günlük kiralar?")
st.subheader(">=200")
st.map(df.query("price>=200")[["latitude", "longitude"]].dropna(how="any"))

st.subheader("İlk 10 satır")
st.write(df.query("price>=200").sort_values("price", ascending=False).head(10))

st.subheader("Seçili kolonlar ile ilk 10 satır")
defaultcols = ["name", "host_name", "neighbourhood", "room_type", "price"]
cols = st.multiselect("Columns", df.columns.tolist(), default=defaultcols)
st.dataframe(df[cols].head(10))

st.header("Oda tipine göre ortalama Günlük Fiyatlar")
st.write("Statik tablo gösterimi.")
st.table(df.groupby("room_type").price.mean().reset_index()\
    .round(2).sort_values("price", ascending=False)\
    .assign(avg_price=lambda x: x.pop("price").apply(lambda y: "%.2f" % y)))

st.header("En çok ilanı olan ev sahibi.")
listingcounts = df.host_id.value_counts()
top_host_1 = df.query('host_id==@listingcounts.index[0]')
top_host_2 = df.query('host_id==@listingcounts.index[1]')
st.write(f"""**{top_host_1.iloc[0].host_name}**, {listingcounts.iloc[0]} ilan ile birinci sırada.
**{top_host_2.iloc[1].host_name}**, {listingcounts.iloc[1]} ilan ile ikinci sırada.
Aşağıda JSON formatında bu 2 ev sahibinin rastgele seçilmiş bir ilanlarının bilgileri mevcut. [`st.json`](https://streamlit.io/docs/api.html#streamlit.json).""")

st.json({top_host_1.iloc[0].host_name: top_host_1\
    [["name", "neighbourhood", "room_type", "minimum_nights", "price"]]\
        .sample(2, random_state=4).to_dict(orient="records"),
        top_host_2.iloc[0].host_name: top_host_2\
    [["name", "neighbourhood", "room_type", "minimum_nights", "price"]]\
        .sample(2, random_state=4).to_dict(orient="records")})

st.header("Kiraların dağılımı nasıl?")

values = st.sidebar.slider("Fiyat Aralığı", float(df.price.min()), float(df.price.clip(upper=1000.).max()), (50., 300.))
f = px.histogram(df.query(f"price.between{values}"), x="price", nbins=15, title="Fiyat Dağılımı")
f.update_xaxes(title="Fiyat")
f.update_yaxes(title="İlan Sayısı")
st.plotly_chart(f)

st.header("Bölgelere göre boş oda oranı?")

neighborhood = st.radio("Bölgeler listesi:", df.neighbourhood.unique())
show_exp = st.checkbox("Pahalı olanlarıda göster.")
show_exp = " and price<200" if not show_exp else ""

@st.cache
def get_availability(show_exp, neighborhood):
    return df.query(f"""neighbourhood_group==@neighborhood{show_exp}\
        and availability_365>0""").availability_365.describe(\
            percentiles=[.1, .25, .5, .75, .9, .99]).to_frame().T

st.table(get_availability(show_exp, neighborhood))


df.query("availability_365>0").groupby("neighbourhood_group")\
    .availability_365.mean().plot.bar(rot=0).set(title="Bölgelerin Ortalama Boş Oda Sayısı.",
        xlabel="Bölge ismi", ylabel="Ortalama Boş Oda Sayısı")
st.pyplot()

st.header("İlan bazında yorum sayısı.")
st.write("Sol tarafran bir aralık seçin.")
minimum = st.sidebar.number_input("Minimum", min_value=0)
maximum = st.sidebar.number_input("Maximum", min_value=0, value=5)
if minimum > maximum:
    st.error("Lütfen mantıklı bir aralık girin!")
else:
    df.query("@minimum<=number_of_reviews<=@maximum").sort_values("number_of_reviews", ascending=False)\
        .head(50)[["name", "number_of_reviews", "neighbourhood", "host_name", "room_type", "price"]]


btn = st.button("Sakın Bana Basma!")
if btn:
    st.balloons()