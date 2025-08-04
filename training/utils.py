import boto3

# Create an S3 client
s3_client = boto3.client('s3')

# Define bucket and object details
bucket_name = 'your-s3-bucket-name'
object_key = 'path/to/your/object.txt'
data_to_upload = b'This is the content of the S3 object.' # Data must be bytes

def upload_to_s3(
        object_key, 
        data_to_upload,
        bucket_name="fraud-detection-data"):
# Upload the object
    try:
        response = s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=data_to_upload
        )
        print(f"Object '{object_key}' uploaded successfully to '{bucket_name}'.")
        print(response)
    except Exception as e:
        print(f"Error uploading object: {e}")