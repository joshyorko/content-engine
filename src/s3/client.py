from dataclasses import dataclass
import boto3
from botocore.client import Config

@dataclass
class S3Client:
    """
    client = S3Client(
        aws_access_key_id="...",
        aws_secret_access_key="...",
        endpoint_url="...",
        public_endpoint_url="...",  # Optional: URL for presigned URLs accessible from browser
        default_bucket_name="...",
    ).client
    """
    aws_access_key_id: str
    aws_secret_access_key: str
    endpoint_url: str 
    default_bucket_name: str
    public_endpoint_url: str | None = None  # Optional, falls back to endpoint_url

    def __post_init__(self):
        # Validate required parameters
        if not self.aws_access_key_id:
            raise ValueError("aws_access_key_id is required")
        if not self.aws_secret_access_key:
            raise ValueError("aws_secret_access_key is required")
        if not self.endpoint_url:
            raise ValueError("endpoint_url is required")
        if not self.default_bucket_name:
            raise ValueError("default_bucket_name is required")
        
        self.client = self.create_s3_client()

    def create_s3_client(self):
        """
        Create and return a boto3 S3 client
        """
        try:
            return boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                endpoint_url=self.endpoint_url,
                config=Config(signature_version='s3v4')
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create S3 client: {e}")
    
    def generate_presigned_url_with_public_endpoint(self, operation, params, expires_in=3600):
        """
        Generate a presigned URL using the public endpoint URL for browser access
        """
        if not self.public_endpoint_url:
            # Fall back to regular presigned URL if no public endpoint is set
            return self.client.generate_presigned_url(operation, Params=params, ExpiresIn=expires_in)
        
        # Create a temporary client with the public endpoint for presigned URL generation
        try:
            public_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                endpoint_url=self.public_endpoint_url,
                config=Config(signature_version='s3v4')
            )
            return public_client.generate_presigned_url(operation, Params=params, ExpiresIn=expires_in)
        except Exception as e:
            # Fall back to regular client if public client fails
            print(f"Public endpoint presigned URL generation failed, falling back: {e}")
            return self.client.generate_presigned_url(operation, Params=params, ExpiresIn=expires_in)

    # def list_objects(self):
    # self.client.get_paginator()
    # return