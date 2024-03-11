from typing import Union, Any
import joblib
import csv
import requests

from fastapi import FastAPI, Body, Request

app = FastAPI()
file = open("./unique_loc.csv", "r")
locations = [x[1] for x in list(csv.reader(file, delimiter=","))]
del locations[0]
file.close()
# loaded_model = joblib.load("../src/models/trained_model.joblib")

# Admin endpoints

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

# @app.get("/superusers/gen_stats")
# def gen_stats():
	# TODO query DB to get general stats on dataset

# @app.get("/superusers/stats_query")
# def stats_query():
	# TODO query DB for spefic stats using SQL query


# General users endpoints

@app.get("/gen_user/risky_locations")
async def risky_locations(request: Request):
	features = await request.json()
	feature_list = [dict({'com': mun}, **features) for mun in locations]
	res = requests.post('http://model:8080/invocations', 
						json={'dataframe_records': feature_list},
						headers={"Content-Type": "application/json"})						
	pred = res.json()['predictions']
	idx = sorted(range(len(pred)), key=lambda i: pred[i])[-10:]
	return {'locations': [locations[i] for i in idx], 'predictions': [pred[i] for i in idx]}
	# TODO return top 10 risky locations after querying the model with loads of predictions

@app.get("/gen_user/query_location")
async def query_location(request: Request):
	features = await request.json()
	res = requests.post('http://model:8080/invocations', 
						json={'dataframe_records': [features]},
						headers={"Content-Type": "application/json"})
	pred = res.json()['predictions'][0]
	return pred
	# TODO return info on riskyness of this location by querying model container with loads of predictions about this location

@app.get("/status")
def test():
	print('here')
	return {'test':'Active'}

@app.get("/model_status")
async def test():
	features = {'catu': 0, 'victim_age': 10, 'lum': 0, 'com': 77317, 'atm': 0}
	
	res = requests.post('http://model:8080/invocations',  
						json={'dataframe_records': [features]},
						 headers={"Content-Type": "application/json"})
	#print(res.text)
	#print(res.json())
	# res = requests.get('http://model:8080/health')
	# # f'http://api:8090{endpoint}'
	# print(res, dir(res))
	# print(res.ok)
	# print(res.json())
	# print(res.text)
	# print(res.status_code)
	# if res.status_code == 200:
	# 	return {'Model Status':'Model is running'}
	return {'predictions':res.json()['predictions']}