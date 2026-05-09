import os
import datetime
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.config import GOOGLE_CREDENTIALS_PATH, TIMEZONE

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    creds = None
    base_dir = os.path.dirname(os.path.abspath(GOOGLE_CREDENTIALS_PATH))
    if base_dir == '':
        base_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(base_dir, 'token.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            except RefreshError:
                if os.path.exists(token_path):
                    os.remove(token_path)
                raise Exception("Sessão expirada. Por favor, faça login novamente na interface.")
        else:
            raise Exception("Não autenticado. Por favor, faça login na interface do Streamlit.")
            
    service = build('calendar', 'v3', credentials=creds)
    return service

def add_event_to_calendar(task: dict):
    try:
        service = get_calendar_service()
    except Exception as e:
        print(f"Erro ao obter serviço do calendário: {e}")
        return None
    
    title = task.get('title', 'Anotação Extraída')
    description = task.get('description', '')
    date_str = task.get('date')
    time_str = task.get('time')
    
    event_body = {
        'summary': title,
        'description': description,
    }
    
    if date_str and time_str:
        try:
            start_datetime_str = f"{date_str}T{time_str}:00"
            start_dt = datetime.datetime.strptime(start_datetime_str, "%Y-%m-%dT%H:%M:%S")
            end_dt = start_dt + datetime.timedelta(hours=1)
            
            event_body['start'] = {'dateTime': start_dt.isoformat(), 'timeZone': TIMEZONE}
            event_body['end'] = {'dateTime': end_dt.isoformat(), 'timeZone': TIMEZONE}
        except ValueError:
            # Se a hora ou data estiver mal formatada, tenta usar apenas a data
            time_str = None 

    if not (date_str and time_str):
        if date_str:
            try:
                event_body['start'] = {'date': date_str, 'timeZone': TIMEZONE}
                start_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                end_dt = start_dt + datetime.timedelta(days=1)
                event_body['end'] = {'date': end_dt.strftime("%Y-%m-%d"), 'timeZone': TIMEZONE}
            except ValueError:
                date_str = None

    if not date_str:
        today = datetime.datetime.now()
        tomorrow = today + datetime.timedelta(days=1)
        event_body['start'] = {'date': today.strftime("%Y-%m-%d"), 'timeZone': TIMEZONE}
        event_body['end'] = {'date': tomorrow.strftime("%Y-%m-%d"), 'timeZone': TIMEZONE}

    try:
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        return event.get('htmlLink')
    except HttpError as error:
        print(f"Erro na API do Google Calendar ao inserir '{title}': {error}")
        return None
    except Exception as e:
        print(f"Erro inesperado ao inserir evento '{title}': {e}")
        return None
