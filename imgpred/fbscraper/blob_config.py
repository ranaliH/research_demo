from azure.storage.blob import BlobServiceClient


def get_blob_service_client():
    blob_service_connection_string = "DefaultEndpointsProtocol=https;AccountName=scrapeddataforapp;AccountKey=PlqU9/MzDy5yF9Si4xhLoGTk7jTg1XkR2V0IAQOSPkR+JTDYz1VByxUcSqd/WAj/ZW8wI9SDiZnv+ASt2IxVsw==;EndpointSuffix=core.windows.net"
    return BlobServiceClient.from_connection_string(blob_service_connection_string)


def create_container(container_name):
    blob_service_client = get_blob_service_client()
    container_client = blob_service_client.get_container_client(container_name)
    container_client.create_container()
