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
from django.http import HttpResponse

# Load environment variables from .env
load_dotenv()

def index(request):
    return HttpResponse("Welcome to the homepage")


class BaseEventView(APIView):
    SHEET_ID = ''
    DRIVE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS")

    def post(self, request):
        serializer = UserFormSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            uploaded_file = request.FILES.get('image')
            image_url = None
            if uploaded_file:
                uploads_dir = 'uploads/'
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)
                image_path = os.path.join(uploads_dir, uploaded_file.name)
                with open(image_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_drive = executor.submit(self.upload_to_drive, image_path)
                    image_url = future_drive.result()
                    future_sheets = executor.submit(self.send_to_sheets, serializer.data, image_url)
                    future_sheets.result()
            data = serializer.data
            data['image_url'] = image_url
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_to_sheets(self, data, image_url):
        credentials_info = json.loads(self.DRIVE_CREDENTIALS_JSON)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)

        team_name = data['team_name']
        team_leader = data['team_leader']
        leader_contact = data['leader_contact']
        email = data['email']
        
        members = [
            {"name": team_leader, "contact": leader_contact},
            {"name": data.get('member1', ''), "contact": data.get('member1_contact', '')},
            {"name": data.get('member2', ''), "contact": data.get('member2_contact', '')},
            {"name": data.get('member3', ''), "contact": data.get('member3_contact', '')},
            {"name": data.get('member4', ''), "contact": data.get('member4_contact', '')}
        ]
        members = [member for member in members if member['name']]

        values = [
            ['', '', '', '', ''],
            [team_name, members[0]['name'], members[0]['contact'], email, image_url]
        ]
        values.extend([['' for _ in range(5)] for _ in range(len(members) - 1)])
        for i, member in enumerate(members[1:], start=1):
            values[i + 1][1] = member['name']
            values[i + 1][2] = member['contact']

        body = {'values': values}
        result = service.spreadsheets().values().append(
            spreadsheetId=self.SHEET_ID, range='Sheet1!A1',
            valueInputOption='RAW', insertDataOption='INSERT_ROWS', body=body).execute()

        start_row = result.get('updates').get('updatedRange').split('!')[1]
        start_row_num = int(start_row[1:].split(':')[0])
        end_row_num = start_row_num + len(values) - 1

        requests = [
            {
                "mergeCells": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": start_row_num,
                        "endRowIndex": end_row_num,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1
                    },
                    "mergeType": "MERGE_ALL"
                }
            },
            {
                "mergeCells": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": start_row_num,
                        "endRowIndex": end_row_num,
                        "startColumnIndex": 3,
                        "endColumnIndex": 4
                    },
                    "mergeType": "MERGE_ALL"
                }
            },
            {
                "mergeCells": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": start_row_num,
                        "endRowIndex": end_row_num,
                        "startColumnIndex": 4,
                        "endColumnIndex": 5
                    },
                    "mergeType": "MERGE_ALL"
                }
            }
        ]

        batch_update_request = {'requests': requests}
        service.spreadsheets().batchUpdate(
            spreadsheetId=self.SHEET_ID,
            body=batch_update_request
        ).execute()

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
