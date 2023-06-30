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
ID_CALENDARIO_DISPONIVEL = 'd25601d008a84d01457d05710fa71998a93bb6c5b55e0df332087b164badab73@group.calendar.google.com'


class ClasseListarEventosDisponiveis():

    def listarEventosDisponiveis(self, qtde_dias: float) -> list:
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
                    calendarId=ID_CALENDARIO_DISPONIVEL,
                    timeMin=time_min,
                    timeMax=time_max,
                    pageToken=page_token
                ).execute()
                for event in events['items']:
                    if 'start' in event and 'dateTime' in event['start']:
                        objeto_evento = Evento(
                            event['id'],
                            event['summary'],
                            event['start']['dateTime']
                        )
                        lista_eventos.append(objeto_evento)
                page_token = events.get('nextPageToken')
                if not page_token:
                    break
            return lista_eventos
        except Exception as e:
            print("Ocorreu um erro ao listar os eventos:", str(e))

    def formatarEventosDisponiveis(self, qtde_dias: float) -> list:
        nao_formatados = self.listarEventosDisponiveis(qtde_dias)
        lista_formatada = []
        for evento in nao_formatados:
            inicio = datetime.strptime(
                evento.start_datetime, f"%Y-%m-%dT%H:%M:%S%z")
            inicio_formatado = inicio.strftime(f"%d-%m-%Y %H:%M")
            evento_formatado = {
                'id': evento.id,
                'start_datetime': inicio_formatado,
            }
            lista_formatada.append(evento_formatado)
        return lista_formatada


class Evento:
    def __init__(self, id, summary, start_datetime):
        self.id = id
        self.summary = summary
        self.start_datetime = start_datetime


# lista = ClasseListarEventosDisponiveis()
# eventos_formatados = lista.listarEventosDisponiveis(2.0)
# # print("eventos_formatados:  ", eventos_formatados)
# # eventos_formatados = lista.formatarEventosDisponiveis(1)
# for evento in eventos_formatados:
#     inicio = datetime.strptime(evento.start_datetime, f"%Y-%m-%dT%H:%M:%S%z")
#     inicio_formatado = inicio.strftime(f"%d-%m-%Y %H:%M")
#     print()
#     print("ID: ", evento.id)
#     print("titulo: ", evento.summary)
#     print("Início: ", inicio_formatado)
#     print()
