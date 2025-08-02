import mlflow
import click
import numpy as np
import pandas as pd
import pickle
import os

from prefect import task, flow
from sklearn.pipeline import make_pipeline
from category_encoders.one_hot import OneHotEncoder

from sklearn.linear_model import LogisticRegression
from imblearn.metrics import classification_report_imbalanced
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score


EXPERIMENT_NAME = "fraud detection"

@task(log_prints=True)
def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)

@task(log_prints=True)
def tracking_runs(C: list, solvers: list, X_samp, y_samp, X_test, y_test, target_names, dataset, testdata):
    print("Starting tracking runs...")
    best_f1 = 0.91
    for c in C:
        for solver in solvers:
            with mlflow.start_run():
                #log dataset 
                mlflow.log_input(dataset, context="training")
                mlflow.log_input(testdata, context="test")
                try:
                    model = make_pipeline(
                            OneHotEncoder(use_cat_names=True),
                            LogisticRegression(
                                random_state=42,
                                solver=solver,
                                n_jobs=2,
                                C=c
                            ))

                    model.fit(X_samp, y_samp)
                    print("Training is finished")
                    y_pred = model.predict(X_samp)
                    f1 = round(f1_score(y_pred=y_pred, y_true=y_samp), 2)
                    acc = round(accuracy_score(y_pred=y_pred, y_true=y_samp), 2)
                    recall = round(recall_score(y_pred=y_pred, y_true=y_samp),2)
                    precision = round(precision_score(y_pred=y_pred, y_true=y_samp),2)
                    training_metrics = {
                        "accuracy_training": acc,
                        "recall_training": recall,
                        "f1_score_training": f1,
                        "precision_training": precision
                    }
                    print(training_metrics)

                    y_pred_test = model.predict(X_test)
                    class_report = classification_report_imbalanced(
                        y_pred=y_pred_test, 
                        y_true=y_test,
                        target_names=target_names, 
                        output_dict=True)

                    test_metrics = {
                        "avg_precision_test": round(class_report["avg_pre"], 2),
                        "avg_recall_test": round(class_report["avg_rec"], 2),
                        "avg_f1_score_test": round(class_report["avg_f1"], 2)
                    }
                    print(test_metrics)
                    mlflow.log_metrics(test_metrics)
                    mlflow.log_metrics(training_metrics)
                    mlflow.log_params(
                        {"C":c,"solver":solver})
                    print("metrics and parameters have been logged")

                    if f1 >= best_f1:
                        best_f1 = f1
                            # Log model
                        mlflow.sklearn.log_model(model, name="model", input_example=X_samp.sample(4))
                        print("The best model has been saved!")
                except Exception as e :
                    print(e)
                    continue

@task(log_prints=True)
def training_setup(datapath, experiment_name, tracking_uri="http://localhost:5000"):
    """
    Setup the training environment.
    """
    # Set the experiment name
    print("Setting up MLflow experiment:", experiment_name)
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

    # Load the preprocessed data
    print("Loading preprocessed data from:", datapath)
    X_train, y_train = load_pickle(os.path.join(datapath, "train.pkl"))
    X_test,y_test = load_pickle(os.path.join(datapath, "test.pkl"))
    print("Data loaded. Shapes:", X_train.shape, y_train.shape, X_test.shape, y_test.shape)

    return X_train, y_train, X_test, y_test

@flow(name="run_training")
def run_training(datapath, experiment_name, tracking_uri):
    """
    Main function to run the training process.
    """
    # Load data
    X_samp, y_samp, X_test, y_test = training_setup(datapath, experiment_name, tracking_uri)

    # Define target names
    target_names = ["Not Fraud", "Fraud"]

    # Define solvers and C values
    solvers = ["sag", "saga"]
    C = np.linspace(0.5, 5, 2)
  
    raw_data = X_samp.copy()
    raw_data["target"] = y_samp

    test_data = X_test.copy()
    test_data["target"] = y_test

    dataset = mlflow.data.from_pandas(raw_data, name="train data")
    testdata = mlflow.data.from_pandas(test_data,  name="test data")

    # Start tracking runs
    tracking_runs(C, solvers, X_samp, y_samp, X_test, y_test, target_names, dataset, testdata)
    
if __name__ == "__main__":
    #user should enter data path 
    run_training()
   



