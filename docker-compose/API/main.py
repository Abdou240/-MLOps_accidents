from typing import Union, Any
import joblib
import csv
import requests

from fastapi import FastAPI, Body, Request

app = FastAPI()
file = open("./com.csv", "r")
s = file.read()
c = s.split('\n')
r = [row.split(',') for row in c]
r.remove([''])
locations = [x[1] for x in r[1:] if x[1].isdigit()]
file.close()

# loaded_model = joblib.load("../src/models/trained_model.joblib")

# Admin endpoints

def auth(user, username, password):
	query = f'SELECT * FROM user_tab WHERE username=\'{username}\' AND password=\'{password}\''
	res = requests.post('http://database:9090/data', json={'query': query})
	res = res.json()
	if len(res) == 0:
		raise ValueError('User does not exist')
	elif res[0]['permission'].lower() != user:
		raise ValueError('Incorrect Permissions')

# @app.post("/admin/model/retrain")
# def retrain_model(years=5):
	# TODO Send request to the model container to trigger retraining no n years of recent data

# @app.get("/admin/model/stats")
# def stats_model():
	# TODO Get model performance metrics, request from the model container

# @app.get("/admin/model/predict")
# async def predict_model(request: Request):
# 	# Request a specific prediction from the model using json
# 	features = await request.json()
# 	input_df = pd.DataFrame([features])
# 	# TODO pull model from model container instead
# 	prediction = loaded_model.predict(input_df)
# 	return {'predictions': [x.item() for x in list(prediction)]}

# @app.get("/admin/users/list")
# def users_list():
	# TODO query database container to get list of superusers

# @app.post("/admin/users/add")
# def users_add(user):
	# TODO send update request to DB container

# @app.post("/admin/users/remove")
# def users_remove(user):
	# TODO send remove request to DB container

# @app.post("/admin/users/update")
# def users_update(user):
	# TODO send update request to update a specific user


# Superuser endpoints

@app.get("/superusers/gen_stats")
async def gen_stats(request: Request):
	query = await request.json()
	try:
		auth('superuser', query['username'], query['password'])
	except ValueError as err:
		raise err
	else:
		try:
			gen_query = 'SELECT COUNT(catu) FROM dataset'
			res = requests.post('http://database:9090/data', json={'query': gen_query})
			res = res.json()
		except:
			raise ConnectionError('Database not responding')
		else:	
			return res
	# TODO query DB to get general stats on dataset

@app.get("/superusers/stats_query")
async def stats_query(request: Request):
	query = await request.json()
	try:
		auth('superuser', query['username'], query['password'])
	except ValueError as err:
		raise err
	else:
		try:
			res = requests.post('http://database:9090/data', json={'query': query['query']})
			res = res.json()
		except:
			raise ConnectionError('Database not responding')
		else:	
			return res


# General users endpoints

@app.get("/gen_user/risky_locations")
async def risky_locations(request: Request):
	features = await request.json()
	feature_list = [dict({'com': mun}, **features['features']) for mun in locations]
	try:
		res = requests.post('http://model:8080/invocations', json={'dataframe_records': feature_list})
		res = res.json()
	except:
		raise ConnectionError('Model not responding')
	else:					
		pred = res['predictions']
		idx = sorted(range(len(pred)), key=lambda i: pred[i])[-(features['top_loc']):]
		return {'locations': [locations[i] for i in idx], 'predictions': [pred[i] for i in idx]}

@app.get("/gen_user/query_location")
async def query_location(request: Request):
	features = await request.json()
	try:
		res = requests.post('http://model:8080/invocations', json={'dataframe_records': [features]})
		res = res.json()
	except:
		raise ConnectionError('Model not responding')
	else:
		pred = res['predictions'][0]
		return pred
	# TODO return info on riskyness of this location by querying model container with loads of predictions about this location

@app.get("/status/api")
def test():
	return True

@app.get("/status/model")
def test():
	features = {'catu': 0, 'victim_age': 10, 'lum': 0, 'com': 77317, 'atm': 0}
	try:
		res = requests.post('http://model:8080/invocations', json={'dataframe_records': [features]})
		res = res.json()
	except:
		raise ConnectionError('Model not responding')
	else:
		return True
	
@app.get("/status/database")
def test():
	try:
		res = requests.get('http://database:9090/data_test')
		if res.status_code != 200:
			raise ConnectionError('Database not responding')
	except:
		raise ConnectionError('Database not responding')
	else:
		return True
