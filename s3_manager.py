#!/usr/bin/env python3
"""
AWS S3 Manager for RAG-Enhanced Workflow Optimization System

This module provides comprehensive S3 integration for:
- RAG dataset storage and retrieval
- Analysis results persistence
- Workflow diagram storage
- Configuration management

Demonstrates complete AWS cloud architecture: Bedrock + S3
"""

import boto3
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from botocore.exceptions import ClientError, NoCredentialsError
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class S3Manager:
    """
    Comprehensive S3 manager for workflow optimization system.
    Handles all cloud storage operations with proper error handling and caching.
    """
    
    def __init__(self, bucket_name: str = None, region: str = "eu-west-2", enable_cache: bool = True):
        """
        Initialize S3 manager with cloud storage capabilities.
        
        Args:
            bucket_name: S3 bucket name (default: workflow-optimization-system)
            region: AWS region (default: eu-west-2 for Bedrock compatibility)
            enable_cache: Enable local caching for performance
        """
        self.bucket_name = bucket_name or "workflow-optimization-system"
        self.region = region
        self.enable_cache = enable_cache
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client('s3', region_name=region)
            logger.info(f"S3 client initialized for region: {region}")
        except NoCredentialsError:
            logger.error("AWS credentials not configured. Please run 'aws configure'")
            raise
        except Exception as e:
            logger.error(f"S3 client initialization failed: {str(e)}")
            raise
        
        # Local cache directory
        if enable_cache:
            self.cache_dir = os.path.join(tempfile.gettempdir(), "workflow_system_cache")
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Cache directory: {self.cache_dir}")
        
        # S3 bucket structure
        self.bucket_structure = {
            "datasets": "datasets/",
            "analysis_results": "analysis_results/",
            "diagrams": "diagrams/",
            "configurations": "configurations/",
            "current_workflows": "diagrams/current_workflows/",
            "optimized_workflows": "diagrams/optimized_workflows/"
        }
        
        logger.info(f" S3 Manager initialized for bucket: {self.bucket_name}")
    
    def ensure_bucket_exists(self) -> bool:
        """
        Create S3 bucket if it doesn't exist.
        
        Returns:
            bool: True if bucket exists or was created successfully
        """
        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' already exists")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    if self.region == 'us-east-1':
                        # us-east-1 doesn't need LocationConstraint
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    
                    logger.info(f"Created S3 bucket: {self.bucket_name}")
                    return True
                    
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {str(create_error)}")
                    return False
            else:
                logger.error(f"Error checking bucket: {str(e)}")
                return False
        
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return False
    
    def upload_json_data(self, data: Dict[str, Any], s3_key: str, 
                        content_type: str = "application/json") -> bool:
        """
        Upload JSON data to S3 with proper formatting.
        
        Args:
            data: Dictionary to upload as JSON
            s3_key: S3 object key (path)
            content_type: Content type for the object
            
        Returns:
            bool: True if upload successful
        """
        try:
            json_string = json.dumps(data, indent=2, default=str)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_string,
                ContentType=content_type,
                ServerSideEncryption='AES256'
            )
            
            logger.info(f"Uploaded JSON to S3: s3://{self.bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload JSON to S3: {str(e)}")
            return False
    
    def download_json_data(self, s3_key: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Download JSON data from S3 with caching support.
        
        Args:
            s3_key: S3 object key (path)
            use_cache: Whether to use local cache
            
        Returns:
            Dict containing JSON data or None if failed
        """
        # Check cache first
        cache_path = None
        if self.enable_cache and use_cache:
            cache_path = os.path.join(self.cache_dir, s3_key.replace('/', '_'))
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'r') as f:
                        data = json.load(f)
                    logger.info(f"Loaded from cache: {s3_key}")
                    return data
                except Exception as e:
                    logger.warning(f"⚠Cache read failed: {str(e)}")
        
        # Download from S3
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            content = response['Body'].read().decode('utf-8')
            data = json.loads(content)
            
            # Cache the data
            if self.enable_cache and use_cache and cache_path:
                try:
                    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                    with open(cache_path, 'w') as f:
                        json.dump(data, f, indent=2, default=str)
                    logger.info(f"Cached data: {s3_key}")
                except Exception as e:
                    logger.warning(f"⚠Cache write failed: {str(e)}")
            
            logger.info(f"Downloaded from S3: s3://{self.bucket_name}/{s3_key}")
            return data
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                logger.warning(f"⚠File not found in S3: {s3_key}")
            else:
                logger.error(f"S3 download error: {str(e)}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to download JSON from S3: {str(e)}")
            return None
    
    def upload_file(self, local_path: str, s3_key: str, content_type: str = None) -> bool:
        """
        Upload a file to S3.
        
        Args:
            local_path: Local file path
            s3_key: S3 object key (path)
            content_type: MIME type (auto-detected if None)
            
        Returns:
            bool: True if upload successful
        """
        try:
            # Auto-detect content type
            if content_type is None:
                if s3_key.endswith('.png'):
                    content_type = 'image/png'
                elif s3_key.endswith('.jpg') or s3_key.endswith('.jpeg'):
                    content_type = 'image/jpeg'
                elif s3_key.endswith('.json'):
                    content_type = 'application/json'
                else:
                    content_type = 'binary/octet-stream'
            
            with open(local_path, 'rb') as f:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=f,
                    ContentType=content_type,
                    ServerSideEncryption='AES256'
                )
            
            logger.info(f"Uploaded file to S3: {local_path} → s3://{self.bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            return False
    
    def download_file(self, s3_key: str, local_path: str) -> bool:
        """
        Download a file from S3.
        
        Args:
            s3_key: S3 object key (path)
            local_path: Local destination path
            
        Returns:
            bool: True if download successful
        """
        try:
            # Ensure local directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            logger.info(f"Downloaded file from S3: s3://{self.bucket_name}/{s3_key} → {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download file from S3: {str(e)}")
            return False
    
    def store_analysis_result(self, result: Dict[str, Any], workflow_title: str) -> str:
        """
        Store workflow analysis result in S3 with organized naming.
        
        Args:
            result: Analysis result dictionary
            workflow_title: Name of the workflow analyzed
            
        Returns:
            str: S3 key where result was stored
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in workflow_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_').lower()
        
        date_folder = datetime.now().strftime("%Y-%m-%d")
        s3_key = f"{self.bucket_structure['analysis_results']}{date_folder}/analysis_{safe_title}_{timestamp}.json"
        
        # Add metadata to result
        enhanced_result = {
            "metadata": {
                "workflow_title": workflow_title,
                "analysis_timestamp": datetime.now().isoformat(),
                "system_version": "1.0.0",
                "s3_location": f"s3://{self.bucket_name}/{s3_key}"
            },
            "analysis_data": result
        }
        
        if self.upload_json_data(enhanced_result, s3_key):
            logger.info(f"Analysis result stored: {workflow_title}")
            return s3_key
        else:
            raise Exception("Failed to store analysis result in S3")
    
    def store_diagram(self, local_diagram_path: str, diagram_type: str, workflow_title: str) -> str:
        """
        Store workflow diagram in S3 with organized structure.
        
        Args:
            local_diagram_path: Local path to diagram file
            diagram_type: 'current' or 'optimized'
            workflow_title: Name of the workflow
            
        Returns:
            str: S3 key where diagram was stored
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in workflow_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_').lower()
        
        if diagram_type == 'current':
            s3_key = f"{self.bucket_structure['current_workflows']}{safe_title}_current_{timestamp}.png"
        elif diagram_type == 'optimized':
            s3_key = f"{self.bucket_structure['optimized_workflows']}{safe_title}_optimized_{timestamp}.png"
        else:
            s3_key = f"{self.bucket_structure['diagrams']}{safe_title}_{diagram_type}_{timestamp}.png"
        
        if self.upload_file(local_diagram_path, s3_key):
            logger.info(f"Diagram stored: {diagram_type} workflow for {workflow_title}")
            return s3_key
        else:
            raise Exception("Failed to store diagram in S3")
    
    def get_s3_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for S3 object access.
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds
            
        Returns:
            str: Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return f"s3://{self.bucket_name}/{s3_key}"
    
    def list_analysis_results(self, date_filter: str = None) -> List[Dict[str, Any]]:
        """
        List stored analysis results with metadata.
        
        Args:
            date_filter: Date filter in YYYY-MM-DD format
            
        Returns:
            List of analysis result metadata
        """
        try:
            prefix = self.bucket_structure['analysis_results']
            if date_filter:
                prefix += f"{date_filter}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            results = []
            for obj in response.get('Contents', []):
                results.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': self.get_s3_url(obj['Key'])
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to list analysis results: {str(e)}")
            return []
    
    def initialize_rag_datasets(self, local_bpi_data_path: str, local_benchmarks_path: str) -> Tuple[bool, bool]:
        """
        Upload RAG datasets to S3 for cloud-based operation.
        
        Args:
            local_bpi_data_path: Local path to BPI RAG data
            local_benchmarks_path: Local path to research benchmarks
            
        Returns:
            Tuple[bool, bool]: (BPI upload success, benchmarks upload success)
        """
        bpi_success = False
        benchmarks_success = False
        
        # Upload BPI RAG data
        try:
            if os.path.exists(local_bpi_data_path):
                with open(local_bpi_data_path, 'r') as f:
                    bpi_data = json.load(f)
                
                s3_key = f"{self.bucket_structure['datasets']}bpi_rag_data.json"
                bpi_success = self.upload_json_data(bpi_data, s3_key)
                
                if bpi_success:
                    logger.info(f"BPI RAG data uploaded: {len(bpi_data.get('patterns', []))} patterns")
        except Exception as e:
            logger.error(f"Failed to upload BPI data: {str(e)}")
        
        # Upload research benchmarks
        try:
            if os.path.exists(local_benchmarks_path):
                with open(local_benchmarks_path, 'r') as f:
                    benchmarks_data = json.load(f)
                
                s3_key = f"{self.bucket_structure['datasets']}research_benchmarks.json"
                benchmarks_success = self.upload_json_data(benchmarks_data, s3_key)
                
                if benchmarks_success:
                    logger.info(f"Research benchmarks uploaded: {len(benchmarks_data)} categories")
        except Exception as e:
            logger.error(f"Failed to upload benchmarks: {str(e)}")
        
        return bpi_success, benchmarks_success
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive S3 system status.
        
        Returns:
            Dictionary containing system status information
        """
        status = {
            "bucket_name": self.bucket_name,
            "region": self.region,
            "cache_enabled": self.enable_cache,
            "bucket_exists": False,
            "datasets": {},
            "storage_usage": {},
            "recent_analyses": 0
        }
        
        try:
            # Check bucket existence
            status["bucket_exists"] = self.ensure_bucket_exists()
            
            if status["bucket_exists"]:
                # Check datasets
                for dataset in ["bpi_rag_data.json", "research_benchmarks.json"]:
                    s3_key = f"{self.bucket_structure['datasets']}{dataset}"
                    try:
                        response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
                        status["datasets"][dataset] = {
                            "exists": True,
                            "size": response['ContentLength'],
                            "last_modified": response['LastModified'].isoformat()
                        }
                    except:
                        status["datasets"][dataset] = {"exists": False}
                
                # Get recent analyses count
                today = datetime.now().strftime("%Y-%m-%d")
                recent_results = self.list_analysis_results(today)
                status["recent_analyses"] = len(recent_results)
        
        except Exception as e:
            logger.error(f"Failed to get system status: {str(e)}")
        
        return status

def main():
    """
    Test S3 manager functionality.
    """
    print("Testing S3 Manager...")
    
    try:
        # Initialize S3 manager
        s3_manager = S3Manager()
        
        # Ensure bucket exists
        if not s3_manager.ensure_bucket_exists():
            print("Failed to create/access S3 bucket")
            return
        
        # Get system status
        status = s3_manager.get_system_status()
        print("S3 System Status:")
        print(json.dumps(status, indent=2, default=str))
        
        print("S3 Manager test completed successfully!")
        
    except Exception as e:
        print(f"S3 Manager test failed: {str(e)}")

if __name__ == "__main__":
    main()