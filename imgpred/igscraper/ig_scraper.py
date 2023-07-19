import instaloader
import uuid
import requests
from azure.storage.blob import BlobServiceClient, ContainerClient

def scrape_instagram_and_upload_to_blob(username, password):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=scrapeddataforapp;AccountKey=PlqU9/MzDy5yF9Si4xhLoGTk7jTg1XkR2V0IAQOSPkR+JTDYz1VByxUcSqd/WAj/ZW8wI9SDiZnv+ASt2IxVsw==;EndpointSuffix=core.windows.net"
    container_name = "igscrapedata"
    L = instaloader.Instaloader()

    def check_duplicate_image(container_client, date_time_str):
        blobs = container_client.list_blobs()
        for blob in blobs:
            if blob.name[:19] == date_time_str[:19]:
                return True
        return False

    def upload_image_to_blob_storage(connection_string, container_name, image_url, posted_date):
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Generate a unique blob name by appending a timestamp and a UUID
        unique_blob_name = f"{posted_date}_{str(uuid.uuid4())}.jpg"

        # Check if the blob with the same name (first 19 characters) already exists
        if not check_duplicate_image(container_client, unique_blob_name):
            # If the blob does not exist, upload the image
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                blob_client = container_client.upload_blob(name=unique_blob_name, data=response.content)
                print(f"Uploaded image {unique_blob_name} to Azure Blob Storage.")
            else:
                print(f"Error while downloading image: HTTP status code {response.status_code}")
        else:
            print(f"Image with timestamp {unique_blob_name[:19]} already exists. Skipping upload.")

    try:
        L.login(username, password)
        profile = instaloader.Profile.from_username(L.context, username)
        posts = profile.get_posts()
        for post in posts:
            posted_date = post.date.strftime("%Y-%m-%d %H:%M:%S")
            image_url = post.url
            upload_image_to_blob_storage(connection_string, container_name, image_url, posted_date)
            for comment in post.get_comments():
                print("comment username: " + comment.owner.username)
                print("comment text: " + comment.text)
                print("comment date : " + str(comment.created_at_utc))
            print("\n\n")
    except instaloader.exceptions.ProfileNotExistsException as e:
        print(f"Profile '{username}' does not exist.")
    except instaloader.exceptions.PrivateProfileNotFollowedException as e:
        print(f"Profile '{username}' is private, and you are not following it.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
