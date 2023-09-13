from django.core.files.uploadedfile import SimpleUploadedFile
from google.cloud import storage


def upload_file_to_google_bucket(destination_file_name, bucket_name, file):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_file_name)
    blob.upload_from_file(file_obj=file, rewind=True)


def download_file_from_google_bucket(file_cloud_directory, bucket_name, target_file_name, content_type):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.get_blob(file_cloud_directory)
    file_bytes = blob.download_as_bytes()
    file_to_store_download = SimpleUploadedFile(target_file_name, file_bytes, content_type=content_type)
    return file_to_store_download
