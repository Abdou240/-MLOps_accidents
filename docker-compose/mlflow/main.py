from typing import Union, Any
import joblib
import csv
import requests

from fastapi import FastAPI, Body, Request, HTTPException
from src.models.train_model import train_model

app = FastAPI()

@app.get("/status")
def test():
    return True


@app.post("/retrain")
async def users_list(request: Request):
    params = await request.json()
    print(params)
    print(type(params))

    param_names = ['n_estimators', 'max_depth']

    # Checking if all input params are valid
    for k in params:
        if k not in param_names:
            raise HTTPException(status_code=404, detail=f'Parameter {k} not valid')
    
    # Checking if all required params are in 
    for k in param_names:
        if k not in params:
            raise HTTPException(status_code=404, detail=f'Parameter {k} not found')

    try:
        run_name = train_model(in_params=params)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=f'{err}')
           
    
    return {'message':f'Model was trained with run name {run_name}'}
    