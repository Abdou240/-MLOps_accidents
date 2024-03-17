import requests

runs = ['f439c730d3794df08de67c18d02ad1d6',
        '7f767bc02a17493e95921b6f2bcebcf0',
        'f8c4776c3c4042c0b8d099dcc8d23eb2']

for run in runs:
    end_pont='2.0/mlflow/runs/get'
    params = {'run_id':run}

    response = requests.get(
        'http://0.0.0.0:8000/api/'+end_pont,
        headers={"Content-Type":'application/json'},
        params=params
    )
    #print(response.text)
    experiment_details = response.json()
    #print('\n\n', run)
    #print(experiment_details)
    run_name = experiment_details['run']['info']['run_name']
    print('\n\nRun name', run_name)
    print('Run id', run)
    print('\nMetrics')
    metrics = experiment_details['run']['data']['metrics']
    for x in metrics:
        #print(x)
        name = x['key']
        print(f'{name}=', x['value'])
    print('\nParams')
    params = experiment_details['run']['data']['params']
    for x in params:
        name = x['key']
        print(f'{name}=', x['value'])


url = 'http://0.0.0.0:8000/api/2.0/mlflow/experiments/search'
r = requests.get(url, params= {'max_results':5})
print(r.text)
experiments = None
if r.status_code == 200:
    experiment_id = experiments = r.json()["experiments"][0]['experiment_id']
    print(experiments)


# url = 'http://0.0.0.0:8000/api/2.0/mlflow/runs/search'
# r = requests.post(url, headers={"Content-Type":'application/json'},
#                   params={'experiment_id':experiment_id, 'filter':'*'})
# print(r.text)
# experiments = None
# # if r.status_code == 200:
# #     experiments = r.json()["experiments"]
# #     print(experiments)


response = requests.get(
    'http://localhost:8050/status'
)
print(response.text)

params = {'n_estimators':40, 'max_depth':8}

response = requests.post(
    'http://localhost:8050/retrain',
    json=params
)
print(response.text)