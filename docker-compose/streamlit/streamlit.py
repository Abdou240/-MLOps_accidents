import streamlit as st
import requests
import pandas as pd

navigation = ['Project Presentations', 'API Endpoints']
menu = st.sidebar.expander('Menu')

nav = menu.radio('Menu', navigation, label_visibility='collapsed')
endpoint = user = section = ''

if nav == 'Project Presentations':

	sections = ['1 - Introduction', '2 - Containerization', '3 - Continuos Integration', '4 - Future work']
	col1, col2 = menu.columns([1,8])
	section = col2.radio('sections', sections, label_visibility='collapsed')

	st.markdown('''
	<style>
	[data-testid="stMarkdownContainer"] ul{
		list-style-position: inside;
	}
	</style>
	''', unsafe_allow_html=True)


	if section == '1 - Introduction':
		st.title('1 - Introduction')
		st.header('Context and Objectives')
		st.markdown(
		"""
		What problem should the application address?
		- In case of a car accident, how severe it could be for a user given the current conditions
		"""
		)
		st.markdown(
		"""
		Who is the app sponsor?
		- Local government of the municipalities
		"""
		)
		st.markdown(
		"""
		Who will be the user of the application?
		- Public entities / local population
		"""
		)
		st.markdown(
		"""
		Who will be the application administrator?
		- A government entity - E.g. Civil defense
		"""
		)
		st.markdown(
		"""
		Objective
		- Develop a system that predicts the severity of a car accident given some features
		- The system is built by containerized microservices
		"""
		)
		st.divider()
		st.header('Implementation Overview')
		st.markdown(
		"""
		Technologies used:
		- Model from scikit learn - Random Forest Classifier - Multiclass
		- PostgreSQL for hosting the DB
		- FastAPI for custom APIs
		- Streamlit for UI
		"""
		)
		st.image('diagram.png')

	if section == '2 - Containerization':
		st.title('2 - Containerization')
		st.image('containers.png')
		st.divider()
		st.header('FastAPI PostgreSQL database API')
		st.markdown(
		"""
		- Database Overview: Utilizes a PostgreSQL database for streamlined storage of clean, preprocessed data in a single table.
		- Table Structure Creation: Focuses on developing the table's layout, specifying data types and fields for comprehensive data organization.
		- Model Requests: Enables the retrieval of specific data sets for model-driven analytics upon request.
		- Appending New Data: Details the methodology for admin users to incorporate new data, highlighting the importance of maintaining data integrity.
		- Query Execution: Describes the ability to execute intricate queries and provide insights, such as pinpointing demographic-specific risk areas under certain weather conditions.
		- User Table Definition: Establishes a User Table to ensure secure data access and manipulation by verified users.
		- User Table Update: Expands functionalities for authorized admin users to update, add, or delete user information, enhancing control over access rights.

		"""
		)
		st.divider()
		st.header('FastAPI model training API')
		st.markdown(
		"""
		Receives model training requests with hyperparameters
		- Reads model code from shared volume
		- Requests data from DB container
		- Retrains the model and saves it in the volume
		"""
		)
		st.divider()
		st.header('MLflow server API')
		st.markdown(
		"""
		Provides metrics from pretrained models
		- Reads metrics from the shared volume
		- Uses Python API
		Provides MLflow server’s web interface for visualization
		"""
		)
		st.divider()
		st.header('MLflow model server')
		st.markdown(
		"""
		The model making predictions
		- Is saved and retrieved from Docker-hub
		- MLflow models is used to make predictions
		"""
		)
		st.divider()
		st.header('FastAPI manager API')
		st.markdown(
		"""
		- Central API to receive requests from frontend
		- Reworks and redirects front end requests to appropriate microservice
		- Return data in appropriate format for frontend to use
		- Users must authenticate to access certain endpoints (Admin, Superuser)
		"""
		)
		st.divider()
		st.header('Streamlit web app')
		st.markdown(
		"""
		- Frontend for UI
		- This is how the model is used and administered
		"""
		)

	if section == '3 - Continuos Integration':
		st.title('3 - Continuos Integration')
		st.header('Workflow')
		st.markdown(
		"""
		- Runs all containers (Docker-compose)
		- Makes requests for all containers
		"""
		)

	if section == '4 - Future work':
		st.title('4 - Future work')
		st.header('Mechanism to place new data is missing')
		st.markdown(
		"""
		- The mechanism to update the DB is ready
		- The mechanism to retrain models is ready
		"""
		)
		st.divider()
		st.header('Update the best performing data is missing')
		st.markdown(
		"""
		- The serving model is currently on docker-hub
		"""
		)

if nav == 'API Endpoints':
	col1, col2 = menu.columns([1,8])
	users = ['/admin', '/superuser', '/gen_user', '/status']
	endpoints = {'/status': ['/api', '/model', '/database'], '/admin': ['/model', '/users'], '/gen_user': ['/query_location', '/risky_locations'], '/superuser': ['/gen_stats', '/stats_query']}
	user = col2.radio('users', users, label_visibility='collapsed')
	# if st.button('Create table'):
	# 	res = requests.get('http://database:9090/create_table')
	# if st.button('Add Users'):
	# 	res = requests.get('http://database:9090/init_users')

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
			st.markdown(f"""
			<style>
			.stProgress .st-bo {{
				background-color: {self.color};
			}}
			</style>
			""", unsafe_allow_html=True)
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
					query['target_username'] = c1.text_input('Username', key='/admin/users_username')
					query['target_password'] = c2.text_input('Password', key='/admin/users_password')
					query['target_permission'] = c3.selectbox('Permission', ['Admin', 'Superuser'])
					if query['target_username'] in users['username']:
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
					query['target_username'] = c1.text_input('Username', key='/admin/users_username', value=selection.loc[0, 'username'])
					query['target_password'] = c2.text_input('Password', key='/admin/users_password', value=selection.loc[0, 'password'])
					query['target_permission'] = c3.selectbox('Permission', ['Admin', 'Superuser'], index=(0 if selection.loc[0, 'permission'] == 'Admin' else 1))
					if query['target_username'] in users['username']:
						st.warning('Username already in use', icon="⚠️")
					else:
						if st.button('Update User'):
							query['current_username'] = selection.loc[0, 'username']
							res = requests.post(f'http://api:8090{user}/users/update', json={'auth': auth, 'query': query})
							st.rerun()


				if len(selection) >= 1:
					if st.button(f'Delete {len(selection)} ' + ('Users' if len(selection) > 1 else 'User')):
						query['current_username'] = list(selection['username'].values)
						res = requests.post(f'http://api:8090{user}/users/remove', json={'auth': auth, 'query': query})
						st.rerun()

		if endpoint == '/model':
			with st.spinner('Pulling model stats...'):
				col1, col2 = st.columns([5, 1])
				col1.subheader('Random Forest Classifier')
				if col2.button('retrain'):
					with st.spinner('Training model...'):
						res = requests.post(f'http://api:8090{user}{endpoint}/retrain', json={'auth': auth})
					if res.status_code != 200:
						st.warning(res.json()['detail'], icon="⚠️")
					else:
						st.success('Model retrained successfully!', icon="✅")
				res = requests.get(f'http://api:8090{user}{endpoint}/stats', json={'auth': auth})
				if res.status_code != 200:
					st.warning(res.json()['detail'], icon="⚠️")
				else:
					for key in res.json():
						run = res.json()[key]
						with st.expander(f'{key}'):
							params, metrics = st.tabs(['Parameters', 'Metrics'])
							with params:
								data = {k: [val] for k, val in zip(run['params'].keys(), run['params'].values())}
								df = pd.DataFrame(data)
								st.dataframe(df)
							with metrics:
								data = {k: [val] for k, val in zip(run['metrics'].keys(), run['metrics'].values())}
								df = pd.DataFrame(data)
								st.dataframe(df)
	
	

	if user == '/superuser':
		if endpoint == '/gen_stats':
			search = st.button('Get Stats')
			with st.spinner('Fishing for stats...'):
				if search:
					res = requests.get(f'http://api:8090{user}{endpoint}', json={'auth': auth})
					if res.status_code != 200:
						st.warning(res.json()['detail'])
					else:
						st.subheader('Table: dataset')
						df = pd.DataFrame(res.json().values(), index=res.json().keys())
						st.write(df)

		if endpoint == '/stats_query':
			query = st.text_input('SQL Query', value='')
			search = st.button('Search')
			if search:
				res = requests.get(f'http://api:8090{user}{endpoint}', json={'auth': auth, 'query': query})
				if res.status_code != 200:
					st.warning(res.json()['detail'])
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
			feat5 = col5.selectbox('Atmos. Conditions', list(feats['atm'].keys()))
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
			feat4 = col4.selectbox('Atmos. Conditions', list(feats['atm'].keys()))
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
			