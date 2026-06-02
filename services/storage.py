import shutil
import os

from azure.storage.blob import BlobServiceClient

# Replace with your Azure details

CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
CONTAINER_NAME = "app-package-func-docgen-knp-38ebd6d"

blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

def upload_file(file_path, blob_name):
    with open(file_path, "rb") as data:
        container_client.upload_blob(name=blob_name, data=data, overwrite=True)


# ZIP THE REPOSITORY
def zip_repo(folder_path, zip_name="repo.zip"):
    shutil.make_archive(zip_name.replace(".zip", ""), 'zip', folder_path)
    return zip_name
