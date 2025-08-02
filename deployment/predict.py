from mlflow import MlflowClient
import pandas as pd
import mlflow.pyfunc
import warnings

warnings.filterwarnings("ignore")


def load_model(model_name: str, 
               model_version: int = 1, 
               tracking_uri: str = "http://localhost:5000") -> mlflow.pyfunc.PyFuncModel:
    """
    Load the model from MLflow.
    """
    # Set the tracking URI to the MLflow server
    mlflow.set_tracking_uri(tracking_uri)

    # Load the model using its URI
    model_uri = f"models:/{model_name}/{model_version}"
    loaded_logreg_model = mlflow.pyfunc.load_model(model_uri)

    return loaded_logreg_model



def predict(model: mlflow.pyfunc.PyFuncModel,
            data: pd.DataFrame) -> pd.Series:
    """
    Make predictions using the loaded model.
    """
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Input data must be a pandas DataFrame.")
    
    # Use the model to make predictions
    predictions = model.predict(data)
    if predictions[0] == 0:
        return "Predictions: No fraud detected"
    elif predictions[0] == 1:
        return "Predictions: Fraud detected"

    

if __name__ == "__main__":
    # Example usage
    model_name = "FraudDetectionModel"
    model_version = 1
    tracking_uri = "http://localhost:5000"

    # Load the model
    loaded_model = load_model(model_name, model_version, tracking_uri)

    # Example data for prediction
    example_data = pd.DataFrame({
      "type": "CASH_OUT", 
      "amount": float(184073.5),
      "oldbalanceOrg": float(10715),
       "oldbalanceDest" : float(15750),
       "time": 16
    }, index=[0])
    # Make predictions
    predictions = predict(loaded_model, example_data)
    if predictions[0] == 0:
        print("Predictions:")
    print(predictions)