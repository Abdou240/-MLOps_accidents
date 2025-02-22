def check_model_api_status():
    import requests
    # Port of model api is 8050
    # In orchestration change localhost to model_api
    response = requests.get(
        'http://localhost:8050/status'
    )
    print(response.text)


def retrain_model():
    import requests
    # Define different number of estimators or max_depth
    params = {'n_estimators':40, 'max_depth':15}
    # Port of model api is 8050
    # In orchestration change localhost to model_api
    response = requests.post(
        'http://localhost:8050/retrain',
        json=params
    )
    print(response.text)


def get_runs_metrics():
    import mlflow
    # Port of mlflow is 8000
    # In orchestration change 0.0.0.0 to mlflow

    MLFLOW_TRACKING_URI = "http://0.0.0.0:8000"

    # Set the MLflow tracking URI if it's not set already
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)  # Replace with your MLflow server URI

    # List all runs using mlflow.search_runs()
    runs = mlflow.search_runs(search_all_experiments=True)
    for run in runs.iterrows():
        run_id = run[1]['run_id']
        experiment_id = run[1]['experiment_id']
        
        # Get run details using mlflow.get_run()
        run_details = mlflow.get_run(run_id)
        # print(run_details)
        
        # Extract metrics
        run_name = run_details.data.tags['mlflow.runName']
        params=run_details.data.params
        metrics = run_details.data.metrics        
        
        print('\n',run_name)
        print('\t', 'Params:', params)
        print('\t', 'Metrics: ', metrics)
        


if __name__ == "__main__":
    check_model_api_status()
    retrain_model()
    get_runs_metrics()
