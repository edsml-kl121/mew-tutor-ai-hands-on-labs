import os
import numpy as np
import pandas as pd
import logging
import json

logging.basicConfig(level=logging.INFO)
cwd = os.path.abspath(os.path.dirname(__file__))

import os
import xgboost as xgb
from google.cloud import storage
import joblib

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "coastal-cell-299117-d12449e33b59.json"

def load_model():
    """
    Load the pre-trained XGBoost regression model from Google Cloud Storage using joblib.
    Returns:
        model: The loaded model using joblib.
    """
    # Define the path to the model
    bucket_name = "prompt-tutor-us-central"
    model_filename = "xgb_regression_model_bike.pkl"
    local_model_path = os.path.abspath(model_filename)

    # Download the model from GCS to the local file
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(model_filename)
    blob.download_to_filename(local_model_path)

    # Load the model using joblib
    model = joblib.load(local_model_path)
    
    return model

def formatting(prediction):
    """Round the prediction to the nearest integer."""
    return np.around(prediction, 0) 

# def predict(instances):
#     """Make predictions for a list of instances"""    
#     model = load_model()    
#     predictions = []
#     for instance in instances:
#         df = pd.DataFrame.from_dict([json.loads(instance)])
#         prediction = model.predict(df)
#         prediction = formatting(prediction)
#         predictions.append(prediction[0])
        
#     return predictions


def predict(instances):
    """Make predictions for a list of instances"""    
    model = load_model()    
    predictions = []
    
    for instance in instances:
        # Convert the dictionary directly to a pandas DataFrame
        df = pd.DataFrame([instance])
        
        # Convert the DataFrame to an XGBoost DMatrix
        dmatrix = xgb.DMatrix(df)
        
        # Make the prediction
        prediction = model.predict(dmatrix)
        
        # Formatting the prediction (if needed)
        formatted_prediction = formatting(prediction)
        
        # Append the formatted prediction
        predictions.append(formatted_prediction[0])
        
    return predictions