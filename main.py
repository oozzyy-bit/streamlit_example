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

st.header("Bölgelere göre boşluluk-doluluk oranı?")

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
    .availability_365.mean().plot.bar(rot=0).set(title="Average availability by neighborhood group",
        xlabel="Neighborhood group", ylabel="Avg. availability (in no. of days)")
st.pyplot()

st.header("Properties by number of reviews")
st.write("Enter a range of numbers in the sidebar to view properties whose review count falls in that range.")
minimum = st.sidebar.number_input("Minimum", min_value=0)
maximum = st.sidebar.number_input("Maximum", min_value=0, value=5)
if minimum > maximum:
    st.error("Please enter a valid range")
else:
    df.query("@minimum<=number_of_reviews<=@maximum").sort_values("number_of_reviews", ascending=False)\
        .head(50)[["name", "number_of_reviews", "neighbourhood", "host_name", "room_type", "price"]]

st.write("486 is the highest number of reviews and two properties have it. Both are in the East Elmhurst \
    neighborhood and are private rooms with prices $65 and $45. \
    In general, listings with >400 reviews are priced below $100. \
    A few are between $100 and $200, and only one is priced above $200.")
st.header("Images")
pics = {
    "Cat": "https://cdn.pixabay.com/photo/2016/09/24/22/20/cat-1692702_960_720.jpg",
    "Puppy": "https://cdn.pixabay.com/photo/2019/03/15/19/19/puppy-4057786_960_720.jpg",
    "Sci-fi city": "https://storage.needpix.com/rsynced_images/science-fiction-2971848_1280.jpg"
}
pic = st.selectbox("Picture choices", list(pics.keys()), 0)
st.image(pics[pic], use_column_width=True, caption=pics[pic])

st.markdown("## Party time!")
st.write("Yay! You're done with this tutorial of Streamlit. Click below to celebrate.")
btn = st.button("Celebrate!")
if btn:
    st.balloons()