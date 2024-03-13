import streamlit as st
import requests
import csv

navigation = ['Project Presentations', 'API Endpoints']

nav = st.sidebar.radio('Menu', navigation)
endpoint = user = method = ''
if nav == 'API Endpoints':
	col1, col2 = st.sidebar.columns([1,8])
	users = ['/admin', '/superusers', '/gen_user', '/status']
	endpoints = {'/status': ['/api', '/model', '/database'], '/admin': {'/model': ['/retrain', '/stats', '/predict'], '/users': ['/list', '/add', '/remove', '/update']}, '/gen_user': ['/query_location', '/risky_locations'], '/superusers': ['/gen_stats', '/stats_query']}
	user = col2.radio('users', users, label_visibility='collapsed')

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
		def __init__(self, pred, obj=st):
			self.color = ['green', 'orange', 'red', 'gray'][pred]
			self.txt = ['Safe', 'Risky', 'Very Risky', 'Deadly'][pred]
			self.progress = (pred + 1) * 25 - 1
			
			self.bar = obj.progress(self.progress, text=f'Risk is predicted at: :{self.color}[{self.txt}]')

	file = open("./com.csv", "r")
	s = file.read()
	c = s.split('\n')
	r = [row.split(',') for row in c]
	r.remove([''])
	coms_label = [x[9] for x in r[1:]]
	coms_code = [x[1] for x in r[1:]]
	file.close()

	# Defining header for each user
	with st.container(height=200, border=False):
		col1, col2 = st.columns([3, 5])
		col1.header(f'{user} endpoints')
		if user in ['/admin', '/superusers']:
			username = col2.text_input('Username')
			password = col2.text_input('Password')
	st.divider()
	if user == '/admin':
		with st.container(height=60):
			endpoint = st.radio(f'{user} endpoints:', endpoints[user].keys(), horizontal=True, label_visibility='collapsed')
		with st.container(height=60):
			method = st.radio(f'{user} methods:', endpoints[user][endpoint], horizontal=True, label_visibility='collapsed')
		endpoint += method
	elif user != '':
		with st.container(height=60):
			endpoint = st.radio(f'{user} endpoints:', endpoints[user], horizontal=True, label_visibility='collapsed')

	if endpoint == '/api':
		try:
			res = requests.get(f'http://api:8090{user}{endpoint}')
			res = res.json()
		except:
			st.warning('API connection issues', icon="⚠️")
		else:
			st.success('API is ready to go!', icon="✅")
		

	if endpoint == '/model':
		try:
			res = requests.get(f'http://api:8090{user}{endpoint}')
			res = res.json()
		except:
			st.warning('Model still warming up...', icon="⚠️")
		else:
			st.success('Model is all fired up!', icon="✅")

	if endpoint == '/database':
		try:
			res = requests.get(f'http://api:8090{user}{endpoint}')
			res = res.json()
		except:
			st.warning('Database still under construction', icon="⚠️")
		else:
			st.success('Database is cookin\'!', icon="✅")
		

	if endpoint == '/query_location':
		
		col1, col2, col3, col4, col5 = st.columns(5)
		feat1 = col1.selectbox('User Category', list(feats['catu'].keys()))
		feat2 = col2.number_input('User Age', min_value=0, max_value=120, value=20)
		feat3 = col3.selectbox('Lighting Conditions', list(feats['lum'].keys()))
		feat4 = col4.selectbox('Municipality', coms_label)
		feat5 = col5.selectbox('Atmospheric Conditions', list(feats['atm'].keys()))
		features = {'catu': feats['catu'][feat1], 'victim_age': feat2, 'lum': feats['lum'][feat3], 'com': coms_code[coms_label.index(feat4)], 'atm': feats['atm'][feat5]}
		search = st.button('Search')
		if search:
			try:
				res = requests.get(f'http://api:8090{user}{endpoint}', json=features)
				res = res.json()
			except:
				st.warning('Model still warming up...', icon="⚠️")
			else:
				st.write(res)
			
		

	if endpoint == '/risky_locations':
		col1, col2, col3, col4 = st.columns(4)
		feat1 = col1.selectbox('User Category', list(feats['catu'].keys()))
		feat2 = col2.number_input('User Age', min_value=0, max_value=120, value=20)
		feat3 = col3.selectbox('Lighting Conditions', list(feats['lum'].keys()))
		feat4 = col4.selectbox('Atmospheric Conditions', list(feats['atm'].keys()))
		features = {'catu': feats['catu'][feat1], 'victim_age': feat2, 'lum': feats['lum'][feat3], 'atm': feats['atm'][feat4]}
		top_loc = st.number_input('Top n locations', min_value=1, max_value=100, value=10)
		search = st.button('Search')
		if search:
			try:
				res = requests.get(f'http://api:8090{user}{endpoint}', json={'features': features, 'top_loc': top_loc})
				res = res.json()
			except:
				st.warning('Model still warming up...', icon="⚠️")
			else:
				res_com = res['locations']
				res_com = [coms_label[coms_code.index('0'*(5 - len(com)) + str(com))] for com in res_com]
				for com, risk in zip(res_com, res['predictions']):
					c = st.container()
					col1, col2 = c.columns([2, 8])
					col1.write(com)
					progress = PredProgress(risk, col2)

	if endpoint == '/stats_query':
		query = st.text_input('SQL Query', value='')
		search = st.button('Search')
		if search:
			try:
				res = requests.get(f'http://api:8090{user}{endpoint}', json=query)
				res = res.json()
			except:
				st.warning('DB not connected yet...', icon="⚠️")
			else:
				st.subheader('Query Response')
				st.write(res)