import click
from prefect import flow
from train import run_training
from preprocess_data import run_process

#mlflow client search best experiments
import mlflow
from mlflow import MlflowClient

# Define the MLflow client
client = MlflowClient()

#seek the best model based on metrics and put it in the model registry
@task(log_prints=True, name="get_best_model")
def get_best_model(experiment_name):
    """
    Get the best model from the MLflow experiment based on F1 score.
    """
    current_experiment=dict(mlflow.get_experiment_by_name(experiment_name))
    experiment_id=current_experiment['experiment_id']

    runs = client.search_runs([experiment_id], filter_string="metrics.avg_f1_score_test >= 0.92", order_by=["metrics.avg_f1_score_test desc"])
    
    if runs:
        best_run = runs[0]
        print(f"Best run ID: {best_run.info.run_id}, F1 Score: {best_run.data.metrics['avg_f1_score_test']}")
        
        run_id = best_run.info.run_id
        model_uri = f"runs:/{run_id}/model"
        model_name = "FraudDetectionModel"
        mlflow.register_model(model_uri, model_name)
        client.set_model_version_tag(name=model_name, version=1, key="Prod", value=True) 
        return 
    else:
        print("No suitable model found.")
        return None



@click.command()
@click.argument('kaggle_username')
@click.argument('kaggle_key')
@click.option('--experiment_name', type=str, default="Fraud Detection Experiment", help="Name of the MLflow experiment")
@click.option('--datapath', type=str, default="data/PS_20174392719_1491204439457_log.csv", help="PaySim1 dataset")
@click.option('--tracking_uri', type=str, default="http://localhost:5000", help="MLflow tracking URI")
@click.option('--dest_path', type=str, default ="data/processed", help="Destination path for processed data")
@flow(name="training_workflow")
def training_workflow(
    kaggle_username, 
    kaggle_key, datapath, 
    dest_path, 
    experiment_name, 
    tracking_uri):
    """
    Main workflow to run the training and preprocessing.
    """
    # Run preprocessing
    run_process(kaggle_username, kaggle_key, datapath, dest_path)
    # Run training
    run_training(datapath=dest_path, experiment_name=experiment_name, tracking_uri=tracking_uri)
    # Get the best model
    get_best_model(experiment_name=experiment_name)

if __name__ == "__main__":
    # User should enter data path
    training_workflow()