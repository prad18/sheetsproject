"""from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserFormSerializer
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import concurrent.futures

class BaseEventView(APIView):
    SHEET_ID = ''
    DRIVE_KEY_FILE = "D:\\Code\\kratos24\\macro-griffin-402307-b08b971175aa.json"

    def post(self, request):
        serializer = UserFormSerializer(data=request.data)
        if serializer.is_valid():
            # Save the form data
            serializer.save()

            # Handle the uploaded image
            uploaded_file = request.FILES.get('image')
            image_url = None
            if uploaded_file:
                # Process image and send to Drive/Sheets concurrently
                uploads_dir = 'uploads/'
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)

                # Save image locally
                image_path = os.path.join(uploads_dir, uploaded_file.name)
                with open(image_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # Parallelize Google Sheets update and Drive upload
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_drive = executor.submit(self.upload_to_drive, image_path)
                    
                    # Wait for Drive upload to finish and get the URL
                    image_url = future_drive.result()
                    
                    # Now send to sheets with the image URL
                    future_sheets = executor.submit(self.send_to_sheets, serializer.data, image_url)
                    future_sheets.result()  # Ensure Sheets append is completed

            # Include image URL in response if available
            data = serializer.data
            data['image_url'] = image_url

            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_to_sheets(self, data, image_url):
        credentials = service_account.Credentials.from_service_account_file(
            self.DRIVE_KEY_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)

        # Prepare data for Google Sheets, now including the image_url
        values = [[data['name'], data['email'], data['message'], image_url]]

        body = {'values': values}

        # Perform the append operation
        result = service.spreadsheets().values().append(
            spreadsheetId=self.SHEET_ID, range='Sheet1!A1',
            valueInputOption='RAW', body=body).execute()
        return result

    def upload_to_drive(self, image_path):
        credentials = service_account.Credentials.from_service_account_file(
            self.DRIVE_KEY_FILE, scopes=['https://www.googleapis.com/auth/drive.file']
        )
        drive_service = build('drive', 'v3', credentials=credentials)

        # Upload the image to Google Drive using MediaFileUpload
        file_metadata = {'name': os.path.basename(image_path)}
        media = MediaFileUpload(image_path, mimetype='image/jpeg', resumable=False)

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        file_id = file.get('id')
        media.stream().close()

        # Make the file publicly accessible
        drive_service.permissions().create(
            fileId=file_id,
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()

        # Return the public URL for the uploaded file
        image_url = f"https://drive.google.com/uc?id={file_id}"

        # Clean up local file
        try:
            os.remove(image_path)
        except PermissionError as e:
            print(f"Failed to delete {image_path}: {e}")

        return image_url


# Inherit the common functionality and assign unique Google Sheets IDs per event
class Event1(BaseEventView):
    SHEET_ID = '1oVKb6N9DIUu_H5o9j5yzwazPtWsURj8PdzU6ycg32wo'


class Event2(BaseEventView):
    SHEET_ID = '1bZnhWP-qoNhNoi5pjCFMygTgxfNDmGNZnrJR7UonBJ4'


class Event3(BaseEventView):
    SHEET_ID = '1Y1Ty3dVk8v_mmyrrrw1_WuxDDFYe2vCB6NEiJxNYLEw'"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserFormSerializer
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import concurrent.futures
from dotenv import load_dotenv
import json

# Load environment variables from .env
load_dotenv()

class BaseEventView(APIView):
    SHEET_ID = ''
    DRIVE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS")  # Load the JSON string from .env

    def post(self, request):
        serializer = UserFormSerializer(data=request.data)
        if serializer.is_valid():
            # Save the form data
            serializer.save()

            # Handle the uploaded image
            uploaded_file = request.FILES.get('image')
            image_url = None
            if uploaded_file:
                # Process image and send to Drive/Sheets concurrently
                uploads_dir = 'uploads/'
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)

                # Save image locally
                image_path = os.path.join(uploads_dir, uploaded_file.name)
                with open(image_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # Parallelize Google Sheets update and Drive upload
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_drive = executor.submit(self.upload_to_drive, image_path)
                    
                    # Wait for Drive upload to finish and get the URL
                    image_url = future_drive.result()
                    
                    # Now send to sheets with the image URL
                    future_sheets = executor.submit(self.send_to_sheets, serializer.data, image_url)
                    future_sheets.result()  # Ensure Sheets append is completed

            # Include image URL in response if available
            data = serializer.data
            data['image_url'] = image_url

            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_to_sheets(self, data, image_url):
        # Parse the JSON string into a Python dictionary
        credentials_info = json.loads(self.DRIVE_CREDENTIALS_JSON)
        
        # Create credentials object from parsed dictionary
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=credentials)

        # Prepare data for Google Sheets, now including the image_url
        values = [[data['name'], data['email'], data['message'], image_url]]

        body = {'values': values}

        # Perform the append operation
        result = service.spreadsheets().values().append(
            spreadsheetId=self.SHEET_ID, range='Sheet1!A1',
            valueInputOption='RAW', body=body).execute()
        return result

    def upload_to_drive(self, image_path):
        # Parse the JSON string into a Python dictionary
        credentials_info = json.loads(self.DRIVE_CREDENTIALS_JSON)

        # Create credentials object from parsed dictionary
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        drive_service = build('drive', 'v3', credentials=credentials)

        # Upload the image to Google Drive using MediaFileUpload
        file_metadata = {'name': os.path.basename(image_path)}
        media = MediaFileUpload(image_path, mimetype='image/jpeg', resumable=False)

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        file_id = file.get('id')
        media.stream().close()

        # Make the file publicly accessible
        drive_service.permissions().create(
            fileId=file_id,
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()

        # Return the public URL for the uploaded file
        image_url = f"https://drive.google.com/uc?id={file_id}"

        # Clean up local file
        try:
            os.remove(image_path)
        except PermissionError as e:
            print(f"Failed to delete {image_path}: {e}")

        return image_url

class Event1(BaseEventView):
    SHEET_ID = '1oVKb6N9DIUu_H5o9j5yzwazPtWsURj8PdzU6ycg32wo'


class Event2(BaseEventView):
    SHEET_ID = '1bZnhWP-qoNhNoi5pjCFMygTgxfNDmGNZnrJR7UonBJ4'


class Event3(BaseEventView):
    SHEET_ID = '1Y1Ty3dVk8v_mmyrrrw1_WuxDDFYe2vCB6NEiJxNYLEw'


"""from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserFormSerializer
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json
import os
import concurrent.futures

class BaseEventView(APIView):
    SHEET_ID = ''
    DRIVE_KEY_FILE = "D:\\Code\\kratos24\\macro-griffin-402307-b08b971175aa.json"

    def post(self, request):
        serializer = UserFormSerializer(data=request.data)
        if serializer.is_valid():
            # Save the form data
            serializer.save()

            # Handle the uploaded image
            uploaded_file = request.FILES.get('image')
            if uploaded_file:
                # Process image and send to Drive/Sheets concurrently
                uploads_dir = 'uploads/'
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)

                # Save image locally
                image_path = os.path.join(uploads_dir, uploaded_file.name)
                with open(image_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # Upload image to Google Drive and get the URL
                image_url = self.upload_to_drive(image_path)

                # Now update the data with the image URL before sending to Google Sheets
                data = serializer.data
                data['image_url'] = image_url  # Add image URL to the data

                # Send data to Google Sheets after image URL is included
                self.send_to_sheets(data)

                return Response(data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_to_sheets(self, data):
        credentials = service_account.Credentials.from_service_account_file(
            self.DRIVE_KEY_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)

        # Prepare data for Google Sheets
        values = [[data['name'], data['email'], data['message'], data.get('image_url', '')]]

        body = {'values': values}

        # Perform the append operation
        result = service.spreadsheets().values().append(
            spreadsheetId=self.SHEET_ID, range='Sheet1!A1',
            valueInputOption='RAW', body=body).execute()
        return result

    def upload_to_drive(self, image_path):
        credentials = service_account.Credentials.from_service_account_file(
            self.DRIVE_KEY_FILE, scopes=['https://www.googleapis.com/auth/drive.file']
        )
        drive_service = build('drive', 'v3', credentials=credentials)

        # Upload the image to Google Drive using MediaFileUpload
        file_metadata = {'name': os.path.basename(image_path)}
        media = MediaFileUpload(image_path, mimetype='image/jpeg', resumable=False)

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        media.stream().close()

        # Make the file publicly accessible
        drive_service.permissions().create(
            fileId=file.get('id'),
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()

        # Return the public URL for the uploaded file
        image_url = f"https://drive.google.com/uc?id={file.get('id')}"

        # Clean up local file
        try:
            os.remove(image_path)
        except PermissionError as e:
            print(f"Failed to delete {image_path}: {e}")

        return image_url


# Inherit the common functionality and assign unique Google Sheets IDs per event
class Event1(BaseEventView):
    SHEET_ID = '1oVKb6N9DIUu_H5o9j5yzwazPtWsURj8PdzU6ycg32wo'


class Event2(BaseEventView):
    SHEET_ID = '1bZnhWP-qoNhNoi5pjCFMygTgxfNDmGNZnrJR7UonBJ4'


class Event3(BaseEventView):
    SHEET_ID = '1Y1Ty3dVk8v_mmyrrrw1_WuxDDFYe2vCB6NEiJxNYLEw'"""

"""from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserFormSerializer
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import concurrent.futures
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

class BaseEventView(APIView):
    SHEET_ID = ''
    DRIVE_KEY_FILE = "D:\\Code\\kratos24\\macro-griffin-402307-b08b971175aa.json"
    _credentials = None
    _sheet_service = None
    _drive_service = None

    @classmethod
    def get_credentials(cls):
        if cls._credentials is None or not cls._credentials.valid:
            cls._credentials = service_account.Credentials.from_service_account_file(
                cls.DRIVE_KEY_FILE, 
                scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']
            )
            if cls._credentials.expired:
                cls._credentials.refresh(Request())
        return cls._credentials

    @classmethod
    def get_sheet_service(cls):
        if cls._sheet_service is None:
            cls._sheet_service = build('sheets', 'v4', credentials=cls.get_credentials(), cache_discovery=False)
        return cls._sheet_service

    @classmethod
    def get_drive_service(cls):
        if cls._drive_service is None:
            cls._drive_service = build('drive', 'v3', credentials=cls.get_credentials(), cache_discovery=False)
        return cls._drive_service

    def post(self, request):
        serializer = UserFormSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            uploaded_file = request.FILES.get('image')
            image_url = None

            if uploaded_file:
                uploads_dir = 'uploads/'
                os.makedirs(uploads_dir, exist_ok=True)
                image_path = os.path.join(uploads_dir, uploaded_file.name)
                
                with open(image_path, 'wb') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_drive = executor.submit(self.upload_to_drive, image_path)
                    future_sheets = executor.submit(self.send_to_sheets, serializer.data)
                    
                    image_url = future_drive.result()
                    sheet_result = future_sheets.result()

            data = serializer.data
            data['image_url'] = image_url
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_to_sheets(self, data):
        service = self.get_sheet_service()
        values = [[data['name'], data['email'], data['message'], data.get('image_url', '')]]
        body = {'values': values}
        
        result = service.spreadsheets().values().append(
            spreadsheetId=self.SHEET_ID, 
            range='Sheet1!A1',
            valueInputOption='RAW', 
            body=body
        ).execute()
        return result

    def upload_to_drive(self, image_path):
        drive_service = self.get_drive_service()
        file_metadata = {'name': os.path.basename(image_path)}
        media = MediaFileUpload(image_path, mimetype='image/jpeg', resumable=True)

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        file_id = file.get('id')

        media.stream().close()
        drive_service.permissions().create(
            fileId=file_id,
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()

        image_url = f"https://drive.google.com/uc?id={file_id}"

        try:
            os.remove(image_path)
        except PermissionError as e:
            print(f"Failed to delete {image_path}: {e}")

        return image_url

# Event classes remain the same
class Event1(BaseEventView):
    SHEET_ID = '1oVKb6N9DIUu_H5o9j5yzwazPtWsURj8PdzU6ycg32wo'

class Event2(BaseEventView):
    SHEET_ID = '1bZnhWP-qoNhNoi5pjCFMygTgxfNDmGNZnrJR7UonBJ4'

class Event3(BaseEventView):
    SHEET_ID = '1Y1Ty3dVk8v_mmyrrrw1_WuxDDFYe2vCB6NEiJxNYLEw'"""

