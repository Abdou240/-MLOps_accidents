from typing import Union, Any
import joblib
import csv
import requests

from fastapi import FastAPI, Body, Request, HTTPException

app = FastAPI()
file = open("./com.csv", "r")
s = file.read()
c = s.split('\n')
r = [row.split(',') for row in c]
r.remove([''])
locations = [x[1] for x in r[1:] if x[1].isdigit()]
file.close()


# Admin endpoints

def auth(user, auth):
	query = f"SELECT * FROM user_tab WHERE username='{auth['username']}'"
	res = requests.post('http://database:9090/data', json={'query': query})
	res = res.json()
	if len(res) == 0:
		raise ValueError('User does not exist')
	elif res[0]['password'] != auth['password']:
		raise ValueError('Incorrect password')
	elif res[0]['permission'].lower() != user:
		raise ValueError('Incorrect Permissions')

@app.post("/admin/model/retrain")
async def retrain_model(request: Request):
	query = await request.json()
	params={'n_estimators':40, 'max_depth':8}
	try:
		auth('admin', query['auth'])
	except ValueError as err:
		raise HTTPException(status_code=404, detail=f'{err}')
	else:
		res = requests.post('http://model_api:8050/retrain', json=params)
		return 'Success'

# @app.get("/admin/model/stats")
# def stats_model():
	# TODO Get model performance metrics, request from the model container


@app.get("/admin/users/list")
async def users_list(request: Request):
	query = await request.json()
	try:
		auth('admin', query['auth'])
	except ValueError as err:
		raise HTTPException(status_code=404, detail=f'{err}')
	else:
		try:
			gen_query = 'SELECT * FROM user_tab'
			res = requests.post('http://database:9090/data', json={'query': gen_query})
			res = res.json()
		except:
			raise HTTPException(status_code=404, detail='Database not responding')
		else:	
			return res
	

# Query structure for user modification:
# {
# 	'auth': {
# 		'username': 'test',
# 		'password': 'test',
# 	},
# 	'query': {
# 		'action': ['add', 'modify', 'delete'],
# 		'target_username': 'test' or ['test1', 'test2'],
# 		'new_username': 'test',
# 		'new_password': 'test',
# 		'new_permission': 'test'
# 	}
# }

@app.post("/admin/users/add")
async def users_add(request: Request):
	query = await request.json()
	try:
		auth('admin', query['auth'])
	except ValueError as err:
		raise HTTPException(status_code=404, detail=f'{err}')
	else:
		try:
			query['query']['action'] = 'add'
			res = requests.post('http://database:9090/admin/manage_users', json=query['query'])
			res = res.json()
		except:
			raise HTTPException(status_code=404, detail='Database not responding')
		else:	
			return res
	

@app.post("/admin/users/remove")
async def users_remove(request: Request):
	query = await request.json()
	try:
		auth('admin', query['auth'])
	except ValueError as err:
		raise HTTPException(status_code=404, detail=f'{err}')
	else:
		query['query']['action'] = 'delete'
		users = query['query']['target_username']
		for user in users:
			try:
				query['query']['target_username'] = user
				res = requests.post('http://database:9090/admin/manage_users', json=query['query'])
				res = res.json()
				
			except:
				raise HTTPException(status_code=404, detail='Database not responding')
		return True	
	

@app.post("/admin/users/update")
async def users_update(request: Request):
	query = await request.json()
	try:
		auth('admin', query['auth'])
	except ValueError as err:
		raise HTTPException(status_code=404, detail=f'{err}')
	else:
		try:
			query['query']['action'] = 'modify'
			res = requests.post('http://database:9090/admin/manage_users', json=query['query'])
			res = res.json()
		except:
			raise HTTPException(status_code=404, detail='Database not responding')
		else:
			return res
	


# Superuser endpoints

@app.get("/superuser/gen_stats")
async def gen_stats(request: Request):
	query = await request.json()
	try:
		auth('superuser', query['auth'])
	except ValueError as err:
		raise HTTPException(status_code=404, detail=f'{err}')
	else:
		try:
			gen_query = 'SELECT COUNT(catu) FROM dataset'
			res = requests.post('http://database:9090/data', json={'query': gen_query})
			res = res.json()
		except:
			raise HTTPException(status_code=404, detail='Database not responding')
		else:	
			return res
	# TODO query DB to get general stats on dataset

@app.get("/superuser/stats_query")
async def stats_query(request: Request):
	query = await request.json()
	try:
		auth('superuser', query['auth'])
	except ValueError as err:
		raise HTTPException(status_code=404, detail=f'{err}')
	else:
		try:
			res = requests.post('http://database:9090/data', json={'query': query['query']})
			res = res.json()
		except:
			raise HTTPException(status_code=404, detail='Database not responding')
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
