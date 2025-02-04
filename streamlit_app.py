import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from pyproj import Transformer
from pyproj import CRS 
import geopandas as gpd
import matplotlib.pyplot as plt
import openpyxl
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Michigan Senate Districts and Voting Precincts Maps",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Filter out warnings (optional)
st.set_option('deprecation.showPyplotGlobalUse', False)

# Cache the data loading functions
@st.cache_data
def load_shapefile(shapefile_path):
    return gpd.read_file(shapefile_path)

# Load shapefiles with caching
gdf_linden = load_shapefile("6bc519b009f35b3311fc5009945479fb.shp")
gdf_crane = load_shapefile("c074a222edfd3dc6822d0a8e844b8d3f.shp")
gdf1_crane = load_shapefile("gdf1_crane.shp")
gdf1_linden = load_shapefile("gdf1_linden.shp")

# Set colors
gdf_linden['color'] = '#514585'
gdf_crane['color'] = '#800000'

# First map (gdf_linden)
fig2 = px.choropleth_mapbox(gdf_linden, 
                            geojson=gdf_linden.geometry.__geo_interface__,
                            locations=gdf_linden.index,
                            mapbox_style="carto-positron",
                            zoom=5,
                            hover_name="DISTRICTNO",
                            custom_data=["DISTRICTNO"], 
                            color=gdf_linden['color'],
                            color_discrete_map={'#514585':'#B078CA', '#800000':'#B078CA'},
                            center={"lat": gdf_linden.centroid.y.mean(), "lon": gdf_linden.centroid.x.mean()},
                            opacity=0.5,
                           )

# Second map (gdf_crane)
fig1 = px.choropleth_mapbox(gdf_crane, 
                            geojson=gdf_crane.geometry.__geo_interface__,
                            locations=gdf_crane.index,
                            mapbox_style="carto-positron",
                            zoom=5,
                            hover_name="DISTRICTNO",
                            custom_data=["DISTRICTNO"], 
                            color=gdf_crane['color'],
                            color_discrete_map={'#514585':'#B078CA', '#800000':'#B078CA'},
                            center={"lat": gdf_crane.centroid.y.mean(), "lon": gdf_crane.centroid.x.mean()},
                            opacity=0.5,
                           )

# Extract data from figures
choropleth_data1 = list(fig1.data)
choropleth_data2 = list(fig2.data)

# Define your Mapbox access token
mapbox_access_token = 'pk.eyJ1IjoiY2JlbnNvMTgyMiIsImEiOiJjbHdoenNleTcwMXljMmpwa25xb29mM2FvIn0.oUFcXxBLN4G4FIM2TG8mtg'

# Scattermapbox data
scattermapbox_data = [
    go.Scattermapbox(),
    go.Scattermapbox()
]

# Layout
layout = go.Layout(
    mapbox=dict(
        accesstoken=mapbox_access_token,
        domain={'x': [0, 0.4], 'y': [0, 1]},
        bearing=0,
        center=dict(
            lat=gdf_crane.centroid.y.mean(),
            lon=gdf_crane.centroid.x.mean()
        ),
        pitch=0,
        zoom=5,
        style='outdoors'
    ),
    mapbox2=dict(
        accesstoken=mapbox_access_token,
        domain={'x': [0.6, 1.0], 'y': [0, 1]},
        bearing=0,
        center=dict(
            lat=gdf_linden.centroid.y.mean(),
            lon=gdf_linden.centroid.x.mean()
        ),
        pitch=0,
        zoom=5,
        style='outdoors'
    )
)

# Create the figure
fig = go.Figure(data=scattermapbox_data + choropleth_data2, layout=layout)

for trace in choropleth_data1:
    trace['subplot'] = 'mapbox2'
    fig.add_trace(trace)

click_script = """
selected_points = fig.data[0].selectedpoints;
new_color1 = ['#636efa'] * len(fig.data[0].z); // Default color for all districts on mapbox subplot
new_color2 = ['#636efa'] * len(fig.data[1].z); // Default color for all districts on mapbox2 subplot

if (selected_points.length > 0) {
    selected_points.forEach(function(point) {
        new_color1[point] = '#ef553b'; // Change color upon click for mapbox subplot
        new_color2[point] = '#ef553b'; // Change color upon click for mapbox2 subplot
    });

    // Synchronize selected points between subplots
    fig.data[1].selectedpoints = selected_points;
}

fig.data[0].marker.color = new_color1;
fig.data[1].marker.color = new_color2;
"""

fig.update_layout(
    clickmode='event+select',
    mapbox={
        "layers": [
            {
                "source": gdf_linden["geometry"].__geo_interface__,
                "type": "line",
                "color": "black",
                "line": {
                    "width": 3.5
                }
            }
        ]
    },
    mapbox2={
        "layers": [
            {
                "source": gdf_crane["geometry"].__geo_interface__,
                "type": "line",
                "color": "black",
                "line": {
                    "width": 3.5
                }
            }
        ]
    }
)

fig.update_traces(
    hovertemplate="<b>State Senate District: %{customdata[0]}</b><extra></extra>"
)

fig.update_layout(
    autosize=False,
    height=700,
    margin=dict(
        l=50,
        r=50,
        b=50,
        t=50,
        pad=4
    ),
    paper_bgcolor="#F4EBD9",
)

fig.update_layout(showlegend=False)

fig3 = fig

# Third and fourth maps with gdf1_linden and gdf1_crane
fig2 = px.choropleth_mapbox(gdf1_linden, 
                            geojson=gdf1_linden.geometry.__geo_interface__,
                            locations=gdf1_linden.index,
                            mapbox_style="carto-positron",
                            zoom=5,
                            hover_name="DISTRICTNO",
                            hover_data=["Precinct_L", "DISTRICTNO", "PRECINCTID"],
                            color=gdf1_linden['color'],
                            color_discrete_map={'#514585':'#8390FA', '#800000':'#800000'},
                            center={"lat": gdf1_linden.centroid.y.mean(), "lon": gdf1_linden.centroid.x.mean()},
                            opacity=0.5,
                           )

fig1 = px.choropleth_mapbox(gdf1_crane, 
                            geojson=gdf1_crane.geometry.__geo_interface__,
                            locations=gdf1_crane.index,
                            mapbox_style="carto-positron",
                            zoom=5,
                            hover_name="DISTRICTNO",
                            hover_data=["Precinct_L", "DISTRICTNO", "PRECINCTID"],
                            color=gdf1_crane['color'],
                            color_discrete_map={'#514585':'#8390FA', '#800000':'#7B3EB8'},
                            center={"lat": gdf1_crane.centroid.y.mean(), "lon": gdf1_crane.centroid.x.mean()},
                            opacity=0.5,
                           )

choropleth_data1 = list(fig1.data)
choropleth_data2 = list(fig2.data)

layout = go.Layout(
    mapbox=dict(
        accesstoken=mapbox_access_token,
        domain={'x': [0, 0.4], 'y': [0, 1]},
        bearing=0,
        center=dict(
            lat=gdf1_crane.centroid.y.mean(),
            lon=gdf1_crane.centroid.x.mean()
        ),
        pitch=0,
        zoom=5,
        style='outdoors'
    ),
    mapbox2=dict(
        accesstoken=mapbox_access_token,
        domain={'x': [0.6, 1.0], 'y': [0, 1]},
        bearing=0,
        center=dict(
            lat=gdf1_linden.centroid.y.mean(),
            lon=gdf1_linden.centroid.x.mean()
        ),
        pitch=0,
        zoom=5,
        style='outdoors'
    )
)

fig = go.Figure(data=scattermapbox_data + choropleth_data2, layout=layout)

for trace in choropleth_data1:
    trace['subplot'] = 'mapbox2'
    fig.add_trace(trace)

click_script = """
selected_points = fig.data[0].selectedpoints;
new_color1 = ['#636efa'] * len(fig.data[0].z); // Default color for all districts on mapbox subplot
new_color2 = ['#636efa'] * len(fig.data[1].z); // Default color for all districts on mapbox2 subplot

if (selected_points.length > 0) {
    selected_points.forEach(function(point) {
        new_color1[point] = '#ef553b'; // Change color upon click for mapbox subplot
        new_color2[point] = '#ef553b'; // Change color upon click for mapbox2 subplot
    });

    // Synchronize selected points between subplots
    fig.data[1].selectedpoints = selected_points;
}

fig.data[0].marker.color = new_color1;
fig.data[1].marker.color = new_color2;
"""

fig.update_layout(
    clickmode='event+select',
    mapbox={
        "layers": [
            {
                "source": gdf_linden["geometry"].__geo_interface__,
                "type": "line",
                "color": "black",
                "line": {
                    "width": 3.5
                }
            }
        ]
    },
    mapbox2={
        "layers": [
            {
                "source": gdf_crane["geometry"].__geo_interface__,
                "type": "line",
                "color": "black",
                "line": {
                    "width": 3.5
                }
            }
        ]
    }
)

fig.update_traces(
    hovertemplate="<b>Precinct Name: %{customdata[0]}</b><br>State House District: %{customdata[1]}<br>Precinct ID: %{customdata[2]}<extra></extra>"
)

fig.update_layout(
    autosize=False,
    height=700,
    margin=dict(
        l=50,
        r=50,
        b=50,
        t=50,
        pad=4
    ),
    paper_bgcolor="#F4EBD9",
)

fig.update_layout(showlegend=False)

# Define tabs
tabs = ["Map", "Excel Data"]
active_tab = st.sidebar.radio("Select Tab", tabs)

# Render Plot tab
if active_tab == "Map":
    st.markdown("<h1 style='text-align: center; color:#373F51;'>Michigan State Senate Districts</h1><br>", unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color:#B078CA; font-size:36px;'>Linden District Boundaries and Crane District Boundaries</h1>", unsafe_allow_html=True)

    st.plotly_chart(fig3, use_container_width=True, height=1200)
    container = st.container(border=True)
    container.write("The 2022 Linden State Senate District boundaries are pictured on the left map. The proposed 2024 Crane State Senate District Boundaries are pictured on the right map. The majority of the boundary changes occurred in the Metro Detroit area. Both maps are interactive, containing zoom and selection features.")
    st.markdown("<h1 style='text-align: center; color:#B078CA; font-size:36px;'>Linden District Boundaries and Crane District Boundaries Against Voting Precincts</h1>", unsafe_allow_html=True)
    
    st.plotly_chart(fig, use_container_width=True, height=1200)
    container = st.container(border=True)
    container.write("The 2022 Linden State Senate District boundaries are pictured on the left map. The proposed 2024 Crane State Senate District Boundaries are pictured on the right map. The majority of the boundary changes occurred in the Metro Detroit area. Both maps are interactive, containing zoom and selection features. The 2022 voting precincts are mapped as well, and the precincts that changed Senate Districts are highlighted in purple on the Crane map.")

# Render Data tab
elif active_tab == "Excel Data":
    @st.cache_data
    def load_dataframe(file_path):
        return pd.read_excel(file_path)
    
    df_option = st.selectbox(
        "Select a dataframe",
        ("Linden District Boundaries", "Crane District Boundaries", "Precincts that Changed Districts")
    )
    
    # Load the selected dataframe
    if df_option == "Linden District Boundaries":
        df = load_dataframe("gdf1_linden2.xlsx")
    elif df_option == "Crane District Boundaries":
        df = load_dataframe("gdf1_crane2.xlsx")
    else:
        df = load_dataframe("Crane_Linden_District_Changes.xlsx")
    
    # Display the selected dataframe
    st.dataframe(df, width=1000, height=500)
