import os 
import pandas as pd
import pickle
from imblearn.over_sampling import SMOTENC
from sklearn.model_selection import train_test_split
from prefect import flow, task
import subprocess

@task
def dump_pickle(obj, filename: str) -> None:
    with open(filename, "wb") as f_out:
        return pickle.dump(obj, f_out)

@task
def download_dataset(kaggle_username, kaggle_key):
    os.environ['KAGGLE_USERNAME'] = kaggle_username
    os.environ['KAGGLE_KEY'] = kaggle_key # key from the json file
    os.makedirs("data", exist_ok=True)
    subprocess.run(["kaggle", "datasets", "download", "-d", "ealaxi/paysim1", "--path", "data", "--unzip"])


@task    
def wrangle(filepath) -> pd.DataFrame:
    print("data wrangling started")
    df = pd.read_csv(filepath)
    print("data loaded", df.shape)

    # remove leak features
    cols = []
    cols.append("newbalanceOrig")
    cols.append("newbalanceDest")

    #dectection system result
    cols.append("isFlaggedFraud")

    #Select only transaction's type where there is a fraud
    trans_types = ["CASH_OUT", "TRANSFER"]
    df = df[df["type"].isin(trans_types)]

    #keep only type of customers M or C
    df["nameOrig"] = df["nameOrig"].str[0]
    df["nameDest"] = df["nameDest"].str[0]

    # Transaction's hour
    df["time"] = df["step"].apply(lambda step: (step - 1) % 24 + 1)
    cols.append("step")

    #filter amount between 10th and 90th percentile
    q10 = df.amount.quantile(0.1)
    q90 = df.amount.quantile(0.9)
    df = df[df["amount"].between(q10, q90)]

    #Filter oldbalanceOrg
    df = df[df.oldbalanceOrg > 0]
    q10 = df.oldbalanceOrg.quantile(0.1)
    q90 = df.oldbalanceOrg.quantile(0.9)
    df = df[df["oldbalanceOrg"].between(q10, q90)]

    #Filter oldbalanceDest
    q10 = df.oldbalanceDest.quantile(0.1)
    q90 = df.oldbalanceDest.quantile(0.9)
    df = df[df["oldbalanceDest"].between(q10, q90)]

    #Drop features with low dimensionality
    cols.append("nameOrig")
    cols.append("nameDest")

    # drop columns
    df.drop(columns=cols, inplace=True)
    return df

@task
def preprocess_data(df, target="isFraud") -> tuple:
    """
    Preprocess the data for training.  
    """
    print("Preprocessing data...")
    # Ensure the target column exists
    X = df.drop(columns=[target])
    y = df[target]


    X_train,X_test,y_train,y_test = train_test_split(X, y, test_size=0.2, random_state=2000)
        
    #OverSampling Data using SMOTENC method
    X_samp, y_samp = SMOTENC(categorical_features=[0], random_state=42).fit_resample(X_train, y_train)

    return X_samp, y_samp, X_test, y_test


@flow(name="run_preprocess_data")
def run_preprocessing(
    kaggle_username, 
    kaggle_key, 
    datapath, 
    dest_path="data/processed"):
    
    """
    Run the preprocessing and return the processed DataFrame.
    """
    print("Downloading dataset from Kaggle...")
    # Download dataset from Kaggle
    if datapath is not None:
        if os.path.isfile(datapath):
            print(f"Dataset already exists at {datapath}. Skipping download.")
        else:
            download_dataset(
                kaggle_username=kaggle_username, 
                kaggle_key=kaggle_key
            )

    print("Dataset downloaded. Starting data wrangling...")    
    df = wrangle(datapath)
    
    print("wrangled df", df.shape)  

    print("Preprocessing data...") 
    # Preprocess the data
    X_samp, y_samp, X_test, y_test = preprocess_data(df)

    os.makedirs(dest_path, exist_ok=True)

    dump_pickle((X_samp, y_samp), os.path.join(dest_path, "train.pkl"))
    dump_pickle((X_test, y_test), os.path.join(dest_path, "test.pkl"))
    print("Data preprocessing completed and saved to disk.")