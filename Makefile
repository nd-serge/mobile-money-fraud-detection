.EXPORT_ALL_VARIABLES:
AWS_ACCESS_KEY_ID = test
AWS_SECRET_ACCESS_KEY = test
AWS_DEFAULT_REGION = us-east-1
MLFLOW_S3_ENDPOINT_URL = http://localhost:4566
RUN_ID = a81abb34aad04690898a55fb8a497171 #Change this value
TRAINING_BUCKET = fraud-detection-training
BACKEND_STORE = sqlite:///fraud-detection.db
KAGGLE_USERNAME = # Complete your Kaggle username
KAGGLE_PASSWORD = # Complete your Kaggle password
IP_LOCAL_STACK = http://localstack-main:4566

ls-bucket:
	@echo "Creating S3 bucket for MLflow artifacts..."
	cd deployment && \
	pipenv run aws --endpoint-url=$(MLFLOW_S3_ENDPOINT_URL) s3api list-buckets

ls-objects: localstack
	@echo "Listing objects in S3 bucket..."
	cd deployment && \
	pipenv run aws --endpoint-url=$(MLFLOW_S3_ENDPOINT_URL) s3api list-objects --bucket $(TRAINING_BUCKET) 
localstack:
	@echo "Starting LocalStack..."
	docker compose -f deployment/docker-compose.yaml up -d
mlflow:
	cd training && \
	pipenv run mlflow server  --backend-store-uri $(BACKEND_STORE) --artifacts-destination s3://$(TRAINING_BUCKET)

install-deps:
	@echo "Installing dependencies..."
	pip install pipenv
	cd training && \
	pipenv install

start-training: localstack install-deps
	@echo "Export fake environment variables and run MLflow & Prefect servers..."
	cd training && \
	pipenv run mlflow server --host 0.0.0.0 --backend-store-uri $(BACKEND_STORE) --artifacts-destination s3://$(TRAINING_BUCKET) > mlflow.log 2>&1 &
	cd training && \
	pipenv run prefect server start > prefect.log 2>&1 &
	cd training && \
	pipenv run python training_pip.py  $(KAGGLE_USERNAME)  $(KAGGLE_PASSWORD)
	@echo "Training servers started."

start-app: localstack
	cd deployment && \
	docker build -t my-app .
	docker run --network deployment_localstack-network -e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
           -e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
           -e MLFLOW_S3_ENDPOINT_URL=$(IP_LOCAL_STACK) \
           -e RUN_ID=$(RUN_ID) \
           -p 8000:8000 \
           my-app