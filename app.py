import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import urllib.parse

# MySQL connection configuration
mysql_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Mysql@1997!',
    'database': 'airbnb',
}

# URL-encode the password
encoded_password = urllib.parse.quote_plus(mysql_config['password'])

# Create a SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{mysql_config['user']}:{encoded_password}@{mysql_config['host']}/{mysql_config['database']}")

# Function to retrieve data from MySQL
@st.cache_data
def fetch_data(query):
    with engine.connect() as connection:
        data = pd.read_sql(query, connection)
    return data

# Fetch data
listings_data = fetch_data("SELECT * FROM Listings")
hosts_data = fetch_data("SELECT * FROM Hosts")
amenities_data = fetch_data("SELECT * FROM Amenities")
reviews_data = fetch_data("SELECT * FROM Reviews")

# Apply custom CSS for background color and layout
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f0f5;
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit App
st.title("Airbnb Listings Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
country_filter = st.sidebar.multiselect("Select Country", options=listings_data['Country'].unique())
if country_filter:
    listings_data = listings_data[listings_data['Country'].isin(country_filter)]

price_range = st.sidebar.slider("Select Price Range", int(listings_data['Price'].min()), int(listings_data['Price'].max()), (int(listings_data['Price'].min()), int(listings_data['Price'].max())))
listings_data = listings_data[(listings_data['Price'] >= price_range[0]) & (listings_data['Price'] <= price_range[1])]

# Main content
st.header("Listings Data Overview")
st.dataframe(listings_data)

# Visualizations
st.header("Visualizations")

# Listings by Country
st.subheader("Listings by Country")
listings_by_country = listings_data['Country'].value_counts().reset_index()
listings_by_country.columns = ['Country', 'Count']
fig = px.bar(listings_by_country, x='Country', y='Count', title="Listings by Country")
st.plotly_chart(fig, use_container_width=True)

# Average Price by Country
st.subheader("Average Price by Country")
avg_price_by_country = listings_data.groupby('Country')['Price'].mean().reset_index()
fig = px.bar(avg_price_by_country, x='Country', y='Price', title="Average Price by Country")
st.plotly_chart(fig, use_container_width=True)

# Listings by Property Type
st.subheader("Listings by Property Type")
listings_by_property_type = listings_data['Property_Type'].value_counts().reset_index()
listings_by_property_type.columns = ['Property_Type', 'Count']
fig = px.bar(listings_by_property_type, x='Property_Type', y='Count', title="Listings by Property Type")
st.plotly_chart(fig, use_container_width=True)

# Average Review Score by Property Type
st.subheader("Average Review Score by Property Type")
avg_review_score_by_property_type = listings_data.groupby('Property_Type')['Review_Score'].mean().reset_index()
fig = px.bar(avg_review_score_by_property_type, x='Property_Type', y='Review_Score', title="Average Review Score by Property Type")
st.plotly_chart(fig, use_container_width=True)

# Average Availability by Country
st.subheader("Average Availability by Country")
avg_availability_by_country = listings_data.groupby('Country')['Availability_365'].mean().reset_index()
fig = px.bar(avg_availability_by_country, x='Country', y='Availability_365', title="Average Availability by Country")
st.plotly_chart(fig, use_container_width=True)

# Top Amenities
st.subheader("Top Amenities")
top_amenities = amenities_data['Amenity'].value_counts().reset_index().head(10)
top_amenities.columns = ['Amenity', 'Count']
fig = px.bar(top_amenities, x='Amenity', y='Count', title="Top Amenities")
st.plotly_chart(fig, use_container_width=True)

# Reviews Distribution
st.subheader("Reviews Distribution")
fig = px.histogram(reviews_data, x='Review_Score', title="Reviews Distribution")
st.plotly_chart(fig, use_container_width=True)

# Specific coordinates to highlight (e.g., a specific Airbnb listing)
highlighted_coordinates = {
    "Latitude": 37.7749,
    "Longitude": -122.4194,
    "Name": "Highlighted Listing",
    "Country": "USA",
    "Price": 200
}

# Convert to DataFrame
highlighted_df = pd.DataFrame([highlighted_coordinates])

# Interactive Map with highlighted point
st.subheader("Listings Map with Highlighted Point")
fig = px.scatter_mapbox(listings_data, lat="Latitude", lon="Longitude", hover_name="Name",
                        hover_data=["Country", "Price"], zoom=3, height=300)

# Add highlighted point
fig.add_scattermapbox(
    lat=highlighted_df["Latitude"],
    lon=highlighted_df["Longitude"],
    mode='markers',
    marker=dict(size=14, color='red'),
    name=highlighted_df["Name"].iloc[0]
)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)

# 3D Listings Map
st.subheader("3D Listings Map")
fig_3d = px.scatter_3d(listings_data, x='Longitude', y='Latitude', z='Price',
                       color='Country', hover_name='Name', hover_data=['Country', 'Price'],
                       title="3D Listings Map")
fig_3d.update_layout(scene=dict(
    xaxis_title='Longitude',
    yaxis_title='Latitude',
    zaxis_title='Price'
))
st.plotly_chart(fig_3d, use_container_width=True)

# Download Data Button
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

csv = convert_df(listings_data)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='listings_data.csv',
    mime='text/csv',
)


