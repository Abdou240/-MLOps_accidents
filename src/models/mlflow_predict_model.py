
import joblib
import pandas as pd
import sys
import json

# Load your saved model
loaded_model = joblib.load("./src/models/trained_model.joblib")

def predict_model(features):
    input_df = pd.DataFrame([features])
    print(input_df)
    prediction = loaded_model.predict(input_df)
    return prediction

def get_feature_values_manually(feature_names):
    features = {}
    for feature_name in feature_names:
        feature_value = float(input(f"Enter value for {feature_name}: "))
        features[feature_name] = feature_value
    return features

if __name__ == "__main__":
    print(len(sys.argv))
    if len(sys.argv) == 2:
        json_file = sys.argv[1]
        with open(json_file, 'r') as file:
            features = json.load(file)

        json_file='./src/models/test_features_mlflow.json'
        with open(json_file, 'r') as file:
            mlflow_features = json.load(file)

        # print('features', features)
        # columns = ["place", "catu", "sexe", "secu1", "year_acc", "victim_age", "catv", "obsm", "motor",
        #             "catr", "circ", "surf", "situ", "vma", "jour", "mois", "lum", "dep", "com", "agg_", 
        #             "int", "atm", "col", "lat", "long", "hour", "nb_victim", "nb_vehicules"]
        # print('columns', len(columns))
        # data = [features[x] for x in columns]
        # print('data', len(data))
        # mlflow_features = {"columns": columns,
        #                     "data": [[1, 1, 1, 1.0, 2021, 25.0, 2.0, 2.0, 1.0, 4, 2.0, 2.0, 1.0, 50.0, 8, 12, 5, 1, 1053, 2, 2, 1.0, 3.0, 46.19561, 5.22192, 22, 2, 2], [10, 3, 1, 0.0, 2021, 60.0, 2.0, 1.0, 1.0, 3, 2.0, 1.0, 1.0, 50.0, 7, 12, 5, 77, 77317, 2, 1, 0.0, 6.0, 48.607146, 2.890515, 17, 2, 1], [1, 1, 1, 2.0, 2021, 47.0, 1.0, 0.0, 1.0, 7, 2.0, 1.0, 1.0, 50.0, 1, 4, 1, 69, 69034, 2, 3, 0.0, 6.0, 45.7997253517, 4.8768031597, 16, 1, 1]]}
        # x = [1, 1, 1, 1.0, 2021, 25.0, 2.0, 2.0, 1.0, 4, 2.0, 2.0, 1.0, 50.0, 8, 12, 5, 1, 1053, 2, 2, 1.0, 3.0, 46.19561, 5.22192, 22, 2, 2]
        # print('x', len(x))

        # mlflow_features = x
        #input()
        #mlflow_features = pd.read_json("/home/ortegamo/Daniel/Personal/jobsuche/courses/MLops/final_project/MLOps_accidents/mlruns/950173504043555393/a98bbbd5944749cb86a4bd234a57ae60/artifacts/rf_car_accidents/input_example.json")
        

        #print('mlflow_features', mlflow_features)

        import mlflow
        logged_model = 'runs:/a98bbbd5944749cb86a4bd234a57ae60/rf_car_accidents'

        # Load model as a PyFuncModel.
        loaded_model_mlflow = mlflow.pyfunc.load_model(logged_model)

        # Predict on a Pandas DataFrame.
        #df = pd.DataFrame(data=mlflow_features["data"], columns=mlflow_features["columns"])
        #df = pd.DataFrame(**mlflow_features)
        import numpy as np
        #df = {}
        #for k, v in zip(columns, x):
        #    df[k] = v if type(v) == int else float(v)
            
        #df['victim_age'] = np.float32(df['victim_age'])
        #print(df['victim_age'])
        input_df = pd.DataFrame([mlflow_features])
        print(input_df)
        x = loaded_model_mlflow.predict(input_df)
        print('MLflow prediction', x)

    else:
        X_train = pd.read_csv("data/preprocessed/X_train.csv")
        feature_names = X_train.columns.tolist()
        features = get_feature_values_manually(feature_names)

    result = predict_model(features)
    print(f"prediction : {result[0]}")