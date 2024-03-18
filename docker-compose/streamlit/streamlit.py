import streamlit as st
import requests
import pandas as pd

navigation = ['Project Presentations', 'API Endpoints']
menu = st.sidebar.expander('Menu')

nav = menu.radio('Menu', navigation, label_visibility='collapsed')
endpoint = user = method = ''
if nav == 'API Endpoints':
	col1, col2 = st.sidebar.columns([1,8])
	users = ['/admin', '/superuser', '/gen_user', '/status']
	endpoints = {'/status': ['/api', '/model', '/database'], '/admin': ['/model', '/users'], '/gen_user': ['/query_location', '/risky_locations'], '/superuser': ['/gen_stats', '/stats_query']}
	user = col2.radio('users', users, label_visibility='collapsed')
	if st.button('Create table'):
		res = requests.get('http://database:9090/create_table')
	if st.button('Add Users'):
		res = requests.get('http://database:9090/init_users')

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
		if user in ['/admin', '/superuser']:
			auth = {}
			auth['username'] = col2.text_input('Username', key='/admin_username')
			auth['password'] = col2.text_input('Password', key='/admin_password')
	st.divider()
	if user != '':
		with st.container(height=60):
			endpoint = st.radio(f'{user} endpoints:', endpoints[user], horizontal=True, label_visibility='collapsed')

	if user == '/admin':
		def dataframe_with_selections(df):
			df_with_selections = df.copy()
			df_with_selections.insert(0, "Select", False)

			# Get dataframe row-selections from user with st.data_editor
			edited_df = st.data_editor(
				df_with_selections,
				hide_index=True,
				column_config={"Select": st.column_config.CheckboxColumn(required=True)},
				disabled=df.columns,
			)

			# Filter the dataframe using the temporary column, then drop the column
			selected_rows = edited_df[edited_df.Select]
			return selected_rows.drop('Select', axis=1)

		if endpoint == '/users':
			res = requests.get(f'http://api:8090{user}{endpoint}/list', json={'auth': auth})
			if res.status_code == 404:
				st.warning(res.json()['detail'], icon="⚠️")
			else:
				st.subheader('Query Response')
				users = pd.DataFrame(res.json())
				selection = dataframe_with_selections(users).reset_index(drop=True)
				query = {}
				if len(selection) == 0:
					c1, c2, c3 = st.columns(3)
					query['new_username'] = c1.text_input('Username', key='/admin/users_username')
					query['new_password'] = c2.text_input('Password', key='/admin/users_password')
					query['new_permission'] = c3.selectbox('Permission', ['Admin', 'Superuser'])
					if query['new_username'] in users['username']:
						st.warning('Username already in use', icon="⚠️")
					else:
						if st.button('Add User'):
							res = requests.post(f'http://api:8090{user}/users/add', json={'auth': auth, 'query': query})
							if res.status_code != 200:
								st.warning(res.json()['detail'])
							else:
								st.rerun()

				if len(selection) == 1:
					c1, c2, c3 = st.columns(3)
					query['new_username'] = c1.text_input('Username', key='/admin/users_username', value=selection.loc[0, 'username'])
					query['new_password'] = c2.text_input('Password', key='/admin/users_password', value=selection.loc[0, 'password'])
					query['new_permission'] = c3.selectbox('Permission', ['Admin', 'Superuser'], index=(0 if selection.loc[0, 'permission'] == 'Admin' else 1))
					if query['new_username'] in users['username']:
						st.warning('Username already in use', icon="⚠️")
					else:
						if st.button('Update User'):
							query['target_username'] = selection.loc[0, 'username']
							res = requests.post(f'http://api:8090{user}/users/update', json={'auth': auth, 'query': query})
							st.rerun()


				if len(selection) >= 1:
					if st.button(f'Delete {len(selection)} ' + ('Users' if len(selection) > 1 else 'User')):
						query['target_username'] = list(selection['username'].values())
						res = requests.post(f'http://api:8090{user}/users/remove', json={'auth': auth, 'query': query})
						st.rerun()


	
	

	if user == '/superuser':
		if endpoint == '/gen_stats':
			search = st.button('get')
			if search:
				res = requests.get(f'http://api:8090{user}{endpoint}', json={'auth': auth})
				if res.status_code == 404:
					st.warning(res.json()['detail'], icon="⚠️")
				else:
					st.subheader('General Stats')
					st.write(res.json())

		if endpoint == '/stats_query':
			query = st.text_input('SQL Query', value='')
			search = st.button('Search')
			if search:
				res = requests.get(f'http://api:8090{user}{endpoint}', json={'auth': auth, 'query': query})
				if res.status_code == 404:
					st.warning(res.json()['detail'], icon="⚠️")
				else:
					st.subheader('Query Response')
					st.write(res.json())

	if user == '/gen_user':
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
					with st.container(height=300):
						for com, risk in zip(res_com, res['predictions']):
							c = st.container()
							col1, col2 = c.columns([2, 8])
							col1.write(com)
							progress = PredProgress(risk, col2)
		
	if user == '/status':
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
			