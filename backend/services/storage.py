import boto3
from botocore.exceptions import ClientError
import os
from typing import BinaryIO
import uuid

class StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_S3_BUCKET')
    
    def upload_file(self, file: BinaryIO, folder: str = "uploads") -> str:
        """Upload a file to S3 and return its URL"""
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        key = f"{folder}/{file_id}{file_extension}"
        
        try:
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                key,
                ExtraArgs={
                    'ContentType': file.content_type,
                    'ACL': 'public-read'
                }
            )
            
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
            return url
            
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            raise
    
    def delete_file(self, file_url: str) -> bool:
        """Delete a file from S3 given its URL"""
        try:
            # Extract key from URL
            key = file_url.split(f"{self.bucket_name}.s3.amazonaws.com/")[1]
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
            
        except ClientError as e:
            print(f"Error deleting file from S3: {e}")
            return False
    
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for secure file access"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            return url
            
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            raise