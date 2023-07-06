from __future__ import print_function
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# SEMPRE QUE MODIFICAR ESSE SCOPES PRECISA DELETAR O ARQUIVO token.json
SCOPES = ['https://www.googleapis.com/auth/calendar']
ID_CALENDARIO_DISPONIVEL = 'd25601d008a84d01457d05710fa71998a93bb6c5b55e0df332087b164badab73@group.calendar.google.com'
ID_CALENDARIO_CONFIRMADOS = '812bfe549dd5ab2c747bac7874a0c500103766d05ce9d03a808bc9769fbefa5b@group.calendar.google.com'


class NovoEvento():

    def novoEvento(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('calendar', 'v3', credentials=creds)
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

            print('Criando um evento novo....')
            event = {
                'summary': 'banho',
                'location': 'blumenau',
                'description': 'um evento de teste pela API doisss',
                'start': {
                    'dateTime': '2023-05-23T08:00:00',
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': '2023-05-23T08:30:00',
                    'timeZone': 'America/Sao_Paulo',
                },
                'reminders': {
                    'useDefault': False
                },
            }
            event = service.events().insert(
                calendarId=ID_CALENDARIO_DISPONIVEL, body=event).execute()
            print('Evento criado: %s' % (event.get('summary')))
            print()
            print('Próximos 5 eventos:')
            events_result = service.events().list(calendarId=ID_CALENDARIO_DISPONIVEL, timeMin=now,
                                                  maxResults=5, singleEvents=True,
                                                  orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('sem proximos eventos encontrados.')
                return

            for event in events:
                start = event['start'].get(
                    'dateTime', event['start'].get('date'))
                print(start, event['summary'])

        except HttpError as error:
            print('Ocorreu um erro: %s' % error)


novo = NovoEvento()
novo.novoEvento()
