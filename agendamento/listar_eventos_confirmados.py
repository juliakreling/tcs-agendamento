from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timezone, timedelta


# SEMPRE QUE MODIFICAR ESSE SCOPES PRECISA DELETAR O ARQUIVO token.json
SCOPES = ['https://www.googleapis.com/auth/calendar']
ID_CALENDARIO_CONFIRMADOS = '812bfe549dd5ab2c747bac7874a0c500103766d05ce9d03a808bc9769fbefa5b@group.calendar.google.com'


class ClasseListarEventosConfirmados():

    def listarEventosConfirmados(self, qtde_dias: float) -> list:
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
            lista_eventos = []

            # Obtém a data atual
            agora = datetime.utcnow()
            # Define o intervalo de tempo para a consulta
            inicio = agora.date()
            fim = inicio + timedelta(days=qtde_dias)
            # Converte as datas em formato RFC3339
            time_min = inicio.isoformat() + 'T00:00:00Z'
            time_max = fim.isoformat() + 'T00:00:00Z'
            page_token = None

            while True:
                events = service.events().list(
                    calendarId=ID_CALENDARIO_CONFIRMADOS,
                    timeMin=time_min,
                    timeMax=time_max,
                    pageToken=page_token
                ).execute()
                for event in events['items']:
                    objeto_evento = Evento(
                        event['id'],
                        event['summary'],
                        event['start']['dateTime'],
                        event['end']['dateTime']
                    )
                    lista_eventos.append(objeto_evento)
                page_token = events.get('nextPageToken')
                if not page_token:
                    break
            return lista_eventos
        except Exception as e:
            print("Ocorreu um erro ao listar os eventos:", str(e))


class Evento:
    def __init__(self, id, summary, start_datetime, end_datetime):
        self.id = id
        self.summary = summary
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime


lista = ClasseListarEventosConfirmados()
eventos = lista.listarEventosConfirmados(3.0)
for evento in eventos:
    # inicio = datetime.strptime(evento.start_datetime, f"%Y-%m-%dT%H:%M:%S%z")
    # fim = datetime.strptime(evento.end_datetime, f"%Y-%m-%dT%H:%M:%S%z")
    # inicio_formatado = inicio.strftime(f"%d-%m-%Y %H:%M")
    # fim_formatado = fim.strftime(f"%d-%m-%Y %H:%M")
    print()
    print("ID: ", evento.id)
    print("Título: ", evento.summary)
    print("Início: ", evento.start_datetime)
    # print("Fim: ", evento.end_datetime)
    print()
