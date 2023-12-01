import streamlit as st
import plotly.express as px
import pandas as pd
import geopandas as gpd

new_name = {"Cote d'Ivoire":"Ivory Coast", 'Democratic Republic of Congo':"Democratic Republic of the Congo", 'Congo, Republic of':"Republic of Congo"}
map_data = pd.read_csv('./data/all_countries_desc_stats_full_laws.csv')[["Country", "Country Population"]].fillna(0)
map_data["Country"] = map_data["Country"].replace(new_name)
polys = gpd.read_file("./geodata/countries.geojson")
map_df = polys.loc[polys.ADMIN.isin(map_data.Country)].reset_index(drop=True)
map_df.to_crs(epsg=4326, inplace=True)
map_df = map_df.sort_values(by="ADMIN", ascending=True)

merged = map_df.merge(map_data, left_on='ADMIN', right_on='Country', how='inner')
map_df.set_index('ADMIN', inplace=True)

fig = px.choropleth_mapbox(map_df, 
                           geojson=map_df['geometry'],
                           locations=map_df.index,
                           color=merged['Country Population'],
                           mapbox_style="open-street-map",
                           center={'lat':30, 'lon':0},
                           zoom=1,
                           opacity=1,
                           )

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)