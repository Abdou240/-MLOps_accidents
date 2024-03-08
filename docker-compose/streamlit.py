import streamlit as st
import requests

endpoints = ['/status', '/model_status', '/gen_user/query_location', '/gen_user/risky_locations']

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

class PredProgress:
	def __init__(self, pred):
		self.color = ['green', 'yellow', 'red', 'black'][pred]
		self.txt = ['Safe', 'Risky', 'Very Risky', 'Deadly'][pred]
		self.progress = (pred + 1) * 25 - 1
		self.risk = st.subheader('Risk is predicted at:')
		self.bar = st.progress(self.progress, text=self.txt)

if endpoint == '/status':
	res = requests.get(f'http://api:80{endpoint}')
	st.write(res.json())

if endpoint == '/model_status':
	res = requests.get(f'http://api:80{endpoint}')
	colors = ['green', 'yellow', 'red', 'black']
	pred = res.json()

	st.markdown(
    f"""
    <style>
        .stProgress > div > div > div > div {{
			background-color: {colors[pred]};
		}}
    </style>""",
    unsafe_allow_html=True,
	)
	progress = PredProgress(pred)

if endpoint == '/gen_user/query_location':
	col1, col2, col3, col4, col5 = st.columns(5)
	feat1 = col1.selectbox('User Category', list(feats['catu'].keys()))
	feat2 = col2.number_input('User Age', min_value=0, max_value=120, value=20)
	feat3 = col3.selectbox('Lighting Conditions', list(feats['lum'].keys()))
	feat4 = col4.number_input('Municipality', min_value=0, max_value=100000)
	feat5 = col5.selectbox('Atmospheric Conditions', list(feats['atm'].keys()))
	features = {'catu': feats['catu'][feat1], 'victim_age': feat2, 'lum': feats['lum'][feat3], 'com': feat4, 'atm': feats['atm'][feat5]}
	search = st.button('Search')
	res = None
	if search:
		res = requests.get(f'http://api:80{endpoint}', json=features)
	if res:
		st.write(res.json())

if endpoint == '/gen_user/risky_locations':
	col1, col2, col3, col4 = st.columns(4)
	feat1 = col1.selectbox('User Category', list(feats['catu'].keys()))
	feat2 = col2.number_input('User Age', min_value=0, max_value=120, value=20)
	feat3 = col3.selectbox('Lighting Conditions', list(feats['lum'].keys()))
	feat4 = col4.selectbox('Atmospheric Conditions', list(feats['atm'].keys()))
	features = {'catu': feats['catu'][feat1], 'victim_age': feat2, 'lum': feats['lum'][feat3], 'atm': feats['atm'][feat4]}
	search = st.button('Search')
	res = None
	if search:
		res = requests.get(f'http://api:80{endpoint}', json=features)
	if res:
		st.write(res.json())