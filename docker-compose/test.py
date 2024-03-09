import requests

# features = {'catu': 0, 'victim_age': 10, 'lum': 0, 'com': 77317, 'atm': 0}
# res = requests.post('http://10.5.0.3:8000/gen_user/query_location', json=features)
try:
	res = requests.get('http://api:8000/status')
	print(res.json())
except requests.exceptions.ConnectionError as con_err:
    print(f"connection issue：{con_err}")

