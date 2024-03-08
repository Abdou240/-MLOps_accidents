import streamlit as st
import requests

endpoints = ['/status', '/model_status', '/query_location']

endpoint = st.sidebar.radio('endpoints', endpoints)

feats = {
	'catu': {
		'Driver': 0, 
		'Passenger': 1,
		'Pedestrian': 3
	},
	'lum': {
		'Day': 0,
		'Night': 1
	},
	'atm': {
		'Normal': 0,
		'Rain/Storm': 1,
		'Snow/Hail': 2,
		'Fog/Smoke': 3
	}
}

if endpoint == '/status':
	res = requests.get(f'http://api:8000{endpoint}')
	res.json()

if endpoint == '/model_status':
	res = requests.get(f'http://api:8000{endpoint}')
	res.json()

if endpoint == '/query_location':
	col1, col2, col3, col4, col5 = st.columns(5)
	feat1 = col1.selectbox('User Category', list(feats['catu'].keys()))
	feat2 = col2.number_input('User Age', min_value=0, max_value=120, value=20)
	feat3 = col3.selectbox('Lighting Conditions', list(feats['lum'].keys()))
	feat4 = col4.number_input('Municipality', min_value=0, max_value=10000)
	feat5 = col5.selectbox('Atmospheric Conditions', list(feats['atm'].keys()))
	features = {'catu': feats['catu'][feat1], 'age': feat2, 'lum': feats['lum'][feat3], 'com': feat4, 'atm': feats['atm'][feat5]}
	search = st.button('Search')
	res = None
	if search:
		res = requests.get(f'http://api:8000{endpoint}', json=features)
		search = False
	if res:
		res.json()