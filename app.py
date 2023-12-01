import pickle
import glob
import streamlit as st
import pandas as pd
from collections import defaultdict
import geopandas as gpd
import plotly.express as px
from streamlit_plotly_events import plotly_events

st.title('Social Media Privacy Laws in the Francophone World')

pickled_responses = glob.glob('./data/*.p')

with open(pickled_responses[0], 'rb') as f:
        child_0 = pickle.load(f)

with open(pickled_responses[1], 'rb') as f:
        parent = pickle.load(f)

with open(pickled_responses[2], 'rb') as f:
        child_1 = pickle.load(f)

def get_logit_dicts(response):
    return [dict(sorted(dict(zip(s['labels'], s['scores'])).items())) for s in response]

parent_select = st.selectbox("Pick parent code", parent[0]['labels'])

if parent_select == 'Personelle':
    child_select = st.selectbox("Pick child code", child_0[0]['labels'])
    children = child_0
else:
    child_select = st.selectbox("Pick child code", child_1[0]['labels'])
    children = child_1

sents = pd.read_csv('sents.csv').rename(columns={'Unnamed: 0':'org_idx'})
df = pd.read_csv('./data/all_countries_desc_stats_full_laws.csv').dropna().reset_index()

def find_country(response):
    country_idx = sents.loc[sents['law'] == response['sequence']]['org_idx'].iloc[0]
    response['country'] = df.iloc[country_idx]['Country']
    return response

def count_labels(child_select, children):
    counts = defaultdict(int)
    for child in children:
        child = find_country(child)
        if child['labels'][0] == child_select:
            counts[child['country']] += 1
    counts = dict(counts)
    for country in list(set(df.Country) ^ set(counts)):
        counts[country] = 0
    count_df = pd.Series(counts).reset_index().rename(columns={'index':'Country', 0:'count'})
    count_df['normalized_count'] = count_df.reset_index().apply(lambda x: x['count']/sents.org_idx.value_counts()[x['index']], axis=1)
    return count_df

count_df = count_labels(child_select, children)
select_df = df.copy()
select_df = select_df.merge(count_df, on='Country')

new_name = {"Cote d'Ivoire":"Ivory Coast", 'Democratic Republic of Congo':"Democratic Republic of the Congo", 'Congo, Republic of':"Republic of Congo"}
select_df["Country"] = select_df["Country"].replace(new_name)
polys = gpd.read_file("./geodata/countries.geojson")
map_df = polys.loc[polys.ADMIN.isin(select_df.Country)].reset_index(drop=True)
map_df.to_crs(epsg=4326, inplace=True)
map_df = map_df.sort_values(by="ADMIN", ascending=True)

merged = map_df.merge(select_df, left_on='ADMIN', right_on='Country', how='inner')
map_df.set_index('ADMIN', inplace=True)

fig = px.choropleth_mapbox(merged, 
                           geojson=map_df['geometry'],
                           locations=map_df.index,
                           color=merged['normalized_count'],
                           mapbox_style="open-street-map",
                           center={'lat':30, 'lon':0},
                           zoom=1,
                           opacity=1,
                           color_continuous_scale="Viridis"
                           )

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
selected = plotly_events(fig)

if len(selected) > 0:
    selected_idx = selected[0]['pointNumber'] 

    tagged_sentences = []
    for child in children:
        child = find_country(child)
        if (child['labels'][0] == child_select) and (child['country'] == df.iloc[selected_idx]['Country']):
            tagged_sentences.append(child['sequence'])
    
    st.write(f"#### Sections of {df.iloc[selected_idx]['Country']}'s Social Media Privacy laws, concerning *{child_select}*:")
    st.divider()
    for sent in tagged_sentences:
        st.write(sent)
        st.divider()