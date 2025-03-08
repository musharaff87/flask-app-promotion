# youtube_service.py
import os
import shutil
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import tempfile
import time

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CREDENTIALS_FILE = "youtube_credentials.json"

def authenticate_youtube():
    """Authenticate with YouTube API, reusing credentials if available."""
    credentials = None

    if os.path.exists(CREDENTIALS_FILE):
        credentials = Credentials.from_authorized_user_file(CREDENTIALS_FILE, SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret_2.json", SCOPES)
            credentials = flow.run_local_server(port=8080)
            with open(CREDENTIALS_FILE, 'w') as creds_file:
                creds_file.write(credentials.to_json())

    return build("youtube", "v3", credentials=credentials)

def upload_to_youtube(video_file, video_id, title, description, tags, category_id, publish_time_str):
    """Upload a video to YouTube."""
    try:
        if not all([video_id, title, description, tags, publish_time_str]):
            raise ValueError("Missing required parameters")

        try:
            publish_time = datetime.fromisoformat(publish_time_str)
        except ValueError:
            raise ValueError("Invalid publish_time format")

        # Save the uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        video_path = os.path.join(temp_dir, video_file.filename)
        video_file.save(video_path)

        title = title + " #shorts"
        youtube = authenticate_youtube()
        ist_offset = timedelta(hours=5, minutes=30)
        publish_time = publish_time - ist_offset  # Convert IST to UTC

        request_body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": "private",
                "license": "youtube",
                "publishAt": publish_time.isoformat(),
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")
        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%.")

        print("Upload Complete!")

        time.sleep(5)

        # Clean up temporary file
        try:
            shutil.rmtree(temp_dir)
            print(f"Temporary directory {temp_dir} removed.")
        except Exception as e:
            print(f"Failed to remove temporary directory: {e}")

        return {"message": "Upload Complete!", "response": response}

    except Exception as e:
        print(f"Error in upload: {e}")
        raise


if __name__ == "__main__":
    authenticate_youtube()