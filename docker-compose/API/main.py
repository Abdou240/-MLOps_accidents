from typing import Union, Any
import joblib
import pandas as pd

from fastapi import FastAPI, Body, Request

app = FastAPI()

loaded_model = joblib.load("../src/models/trained_model.joblib")

# Admin endpoints

@app.post("/admin/model/retrain")
def retrain_model(years=5):
	# TODO Send request to the model container to trigger retraining no n years of recent data

@app.get("/admin/model/stats")
def stats_model():
	# TODO Get model performance metrics, request from the model container

@app.get("/admin/model/predict")
async def predict_model(request: Request):
	# Request a specific prediction from the model using json
	features = await request.json()
	input_df = pd.DataFrame([features])
	# TODO pull model from model container instead
	prediction = loaded_model.predict(input_df)
	return {'predictions': [x.item() for x in list(prediction)]}

@app.get("/admin/users/list")
def users_list():
	# TODO query database container to get list of superusers

@app.post("/admin/users/add")
def users_add(user):
	# TODO send update request to DB container

@app.post("/admin/users/remove")
def users_remove(user):
	# TODO send remove request to DB container

@app.post("/admin/users/update")
def users_update(user):
	# TODO send update request to update a specific user


# Superuser endpoints

@app.get("/superusers/gen_stats")
def gen_stats():
	# TODO query DB to get general stats on dataset

@app.get("/superusers/stats_query")
def stats_query():
	# TODO query DB for spefic stats using SQL query


# General users endpoints

@app.get("/gen_user/risky_locations")
def risky_locations(top=10):
	# TODO return top 10 risky locations after querying the model with loads of predictions

@app.get("/gen_user/query_location")
def query_location(location):
	# TODO return info on riskyness of this location by querying model container with loads of predictions about this location