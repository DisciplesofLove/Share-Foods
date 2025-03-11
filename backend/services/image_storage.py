import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from typing import Optional
from decouple import config
import uuid

class ImageStorage:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=config('AWS_REGION')
        )
        self.bucket_name = config('AWS_BUCKET_NAME')
    
    async def upload_image(
        self, file: UploadFile, folder: str = "listings"
    ) -> Optional[str]:
        """
        Upload an image to S3 and return its URL.
        
        Args:
            file: The image file to upload
            folder: The folder within the bucket to store the image
            
        Returns:
            str: The URL of the uploaded image, or None if upload failed
        """
        try:
            # Generate unique filename
            file_extension = file.filename.split('.')[-1]
            filename = f"{folder}/{uuid.uuid4()}.{file_extension}"
            
            # Upload file
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                filename,
                ExtraArgs={
                    "ContentType": file.content_type,
                    "ACL": "public-read"
                }
            )
            
            # Return public URL
            return f"https://{self.bucket_name}.s3.amazonaws.com/{filename}"
        
        except ClientError as e:
            print(f"Error uploading image: {str(e)}")
            return None
        
    async def delete_image(self, image_url: str) -> bool:
        """
        Delete an image from S3.
        
        Args:
            image_url: The URL of the image to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Extract key from URL
            key = image_url.split('.com/')[-1]
            
            # Delete file
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
            
        except ClientError as e:
            print(f"Error deleting image: {str(e)}")
            return False