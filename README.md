# mobile-money-fraud-detection

## Overview
This project delivers a microservice for mobile money operators across Africa to identify and block fraudulent transactions in real-time. As mobile money services have become a primary solution for financial inclusion in many African regions, this system helps protect users who may have limited knowledge of cybersecurity from sophisticated fraud tactics.

## Objectives
1. Automate the training data pipeline
2. Deploy a microservice with API endpoints

## Data description 

This project utilizes the [Synthetic Financial Datasets For Fraud Detection](https://www.kaggle.com/datasets/ealaxi/paysim1/data) from Kaggle. The dataset simulates mobile money transactions based on a sample of real transactions extracted from financial logs from a mobile money service implemented in an African country.

## Training workflow 

This workflow automates the end-to-end process for mobile money fraud detection using three main steps:

- `run_preprocessing` : 
Downloads the dataset from Kaggle and applies essential data transformations, including filtering and cleaning. This step prepares the data for model training.

- `run_training`:
Trains a machine learning model on the processed data. The training step includes hyperparameter tuning and evaluation on a test set.

- `get_best_model` : 
Selects and registers the best model based on the highest average F1 score on the test data. The chosen model is then stored in the MLflow Model Registry for future use.

Each step is orchestrated using Prefect and MLflow, ensuring reproducibility and traceability of experiments.

Note: It is imperative to have a Kaggle account to download the dataset.

### Tools & Technologies

- `Makefile`: Task automation and standardization 
- `Prefect`: Workflow orchestration
- `MLflow`: Experiment tracking and model registry
- `LocalStack S3`: Local S3-compatible storage
- `SQLite`: Lightweight database
- `Pipenv`: Python dependency management


### How to Run the Training Workflow

1. **Complete your Kaggle credentials**
    First, install Pipenv and ensure you are using Python 3.12.   
    `pip install pipenv`

   At the top of the `Makefile`, fill in your Kaggle username and password:
   ```makefile
   KAGGLE_USERNAME = your_kaggle_username
   KAGGLE_PASSWORD = your_kaggle_key
   ```

2. **Start the training workflow**

   In your terminal, run:
   ```bash
   make start-training
   ```


   This command will:
   - Start LocalStack and install dependencies
   - Download and preprocess the dataset
   - Train the model
   - Register the best model in MLflow

### Monitoring

You can monitor the training workflow in real time:
- **MLflow UI**: Track experiments, metrics, and models at [http://localhost:5000](http://localhost:5000)
- **Prefect UI**: Visualize and manage workflow execution at [http://localhost:4200](http://localhost:4200)


## Microservice prediction flow 

The microservice exposes a `/predict` endpoint using FastAPI. When a transaction is submitted:

- The request payload is validated using a `Pydantic model (Transaction)`.
- The transaction data is formatted and passed to the prediction function.
- The pre-trained fraud detection model (loaded at startup) generates a prediction.
- The API returns whether the transaction is fraudulent or not.

### Deployment

To execute, it is important to specify the `RUN_ID` of the model contained in the model registry at the header of the Makefile

```bash
 RUN_ID=your_model_run_id
```

Currently there is a bug: the run ID is not the same for training and S3. Therefore, to get a valid RUN ID, you must enter `make ls-objects`


```bash
To extract the correct RUN_ID, look for the string after "m-" in the "Key" field from the output of make ls-objects.
example: 
         {
            "Key": "1/models/m-314f3f443a5441b5b6523bc01e748b4a/artifacts/MLmodel",
            "LastModified": "2025-08-05T10:44:12.000Z",
            "ETag": "\"7f22c7b78675df831b34276dde1b7f67\"",
            "ChecksumAlgorithm": [
                "CRC32"
            ],
            "ChecksumType": "FULL_OBJECT",
            "Size": 1259,
            "StorageClass": "STANDARD",
            "Owner": {
                "DisplayName": "webfile",
                "ID": "75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a"
            }
        }
 RUN_ID = 314f3f443a5441b5b6523bc01e748b4a
```



Then, run the FastAPI application:

```bash
make start-app
```

You can test the API interactively using FastAPI's built-in documentation at [http://localhost:8000/docs](http://localhost:8000/docs).


```bash

# Sample data
{
  "type": "CASH_OUT",
  "amount": 184073.5,
  "oldbalanceOrg": 10715,
  "oldbalanceDest": 15750,
  "time": 16

}
```
## Limitations

- Monitoring feature is not yet implemented. However, the system automatically records all requests and responses in a CSV file. This data can be analyzed afterward using EvidentlyAI to evaluate model performance and drift.

- Unit tests have not been established at this stage of the project.