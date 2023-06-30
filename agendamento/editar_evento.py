from __future__ import print_function
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
ID_CALENDARIO_NAO_CONFIRMADOS = '3a0334f8befd7aa68908f7dda72f253efb0aec7adf8edf86ee390195cb7130f3@group.calendar.google.com'


class EditarEvento():

    def moveEventoParaNovoCalendario(self, idEvento: str, descricao: str, idCalendarioNovo: str):
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
            event = service.events().get(calendarId=ID_CALENDARIO_NAO_CONFIRMADOS,
                                         eventId=idEvento).execute()

            novo_event = {
                'summary': event['summary'],
                'description': descricao,
                'start': event['start'],
                'end': event['end'],
                # Incluir outros detalhes do evento, se necessário
            }

            service.events().delete(calendarId=ID_CALENDARIO_NAO_CONFIRMADOS,
                                    eventId=idEvento).execute()

            inserted_event = service.events().insert(
                calendarId=idCalendarioNovo, body=novo_event).execute()

            novo_id_evento = inserted_event['id']
            # print("novo id: ", novo_id_evento)

        except HttpError as error:
            print('Ocorreu um erro: %s' % error)

    def editaEventoDisponivel(self, idEvento: str, descricao: str, idCalendarioNovo: str):
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
            event = service.events().get(calendarId=ID_CALENDARIO_DISPONIVEL,
                                         eventId=idEvento).execute()

            event['description'] = descricao
            event['calendarId'] = idCalendarioNovo

            updated_event = service.events().update(
                calendarId=idCalendarioNovo, eventId=idEvento, body=event).execute()

            # print(updated_event['updated'])

        except HttpError as error:
            print('Ocorreu um erro: %s' % error)


# editaEvento = EditarEvento()
# editar = editaEvento.moveEventoParaNovoCalendario(
#     '1sfinqfq3u877coqe08kkvd0ps',
#     'laeveeeeeee',
#     ID_CALENDARIO_NAO_CONFIRMADOS
# )
