import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

CREDS = st.secrets['gsp_secrets']['my_project_settings']
KWS = {
    "Personelle":[
        "Securité",
        "Dignité",
        "Individuelle",
        "Sauvegarde",
        "Sûreté",
        "Liberté",
        "droits fondamentaux",
        "protection",
        "Droit à l'information", 
        "Droit d'être informé",
        "plainte"
    ],
    "Administrative":[
        "Indenmité",
        "Entreprise",
        "Établissement",
        "Institution",
        "Exception",
        "Sauvegarde",
        "publique",
        "obligation",
        "surveillance", 
        "gouvernement",
        "organisation",
        "entité"
    ]
}

st.title("Law Navigation")

name = st.text_input("Input your name (make sure it's the same each time)")

@st.cache_resource
def load_data():
    return pd.read_csv('./data/all_countries_desc_stats_full_laws.csv').dropna().reset_index(), pd.read_csv('sents.csv').rename(columns={'Unnamed: 0':'org_idx'})
df, sents = load_data()

@st.cache_resource
def load_google_sheet():
    gc = gspread.service_account_from_dict(CREDS)
    gc = gspread.service_account_from_dict(CREDS)
    return gc.open('francophone-social-media-coding').sheet1 # gmail account
fb = load_google_sheet()

country_choice = st.selectbox("Pick a country", df.Country)
country_idx = df[df['Country'] == country_choice.strip()].index.item()
law_sents = sents[sents.org_idx == country_idx].law
st.divider()

for i, sent in enumerate(law_sents):
    st.write(sent)
    parent = st.selectbox('Pick parent code', KWS.keys(), key=i)
    child = st.selectbox('Pick child code', KWS[parent], key=f"{i}_c")
    notes = st.text_area('Add any notes or observations', key=f'n_{i}')
    if st.button('Submit to sheet', key=f"{i}_b"):
        fb.append_row([name, country_choice, sent, parent, child, notes])
    st.divider()