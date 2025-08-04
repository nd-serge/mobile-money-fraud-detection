import pandas as pd
import mlflow.pyfunc
import warnings
import os.path
from mlflow.artifacts import download_artifacts
import mlflow
import os


warnings.filterwarnings("ignore")



def load_model():
    """
    Load the model from MLflow.
    """

    try:

        print("Downloading model artifacts...")

        path = f"s3://fraud-detection-training/1/models/m-{os.environ["RUN_ID"]}/artifacts"
        model_path = download_artifacts(path)
        print(f"Model artifacts downloaded to: {model_path}")

        print("Loading model...")
        loaded_logreg_model = mlflow.pyfunc.load_model(model_path)
        print("Model loaded successfully.")

        return loaded_logreg_model
    except Exception as e:
        print(f"Error loading model: {e}")


def predict(data: dict, model) -> str:
    """
    Make predictions using the loaded model.
    """
    file_path = "predictions.csv"
    
    # Use the model to make predictions
    df = pd.DataFrame(data, index=[0], columns=["type", "amount", "oldbalanceOrg", "oldbalanceDest", "time"])

    predictions = model.predict(df)
    df["prediction"] = predictions[0]

    #if file exists, append to it; otherwise, create a new file
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, mode='w', header=True, index=False)    
    # Return the predictions
    if predictions[0] == 0:
        return "Predictions: No fraud detected"
    elif predictions[0] == 1:
        return "Predictions: Fraud detected"
