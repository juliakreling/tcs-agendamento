from __future__ import print_function
from flask import Flask, jsonify
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import os.path


# SEMPRE QUE MODIFICAR ESSE SCOPES PRECISA DELETAR O ARQUIVO token.json
SCOPES = ['https://www.googleapis.com/auth/calendar']
ID_CALENDARIO_NAO_CONFIRMADOS = '3a0334f8befd7aa68908f7dda72f253efb0aec7adf8edf86ee390195cb7130f3@group.calendar.google.com'


class Evento:
    def __init__(self, id, summary, start_datetime):
        self.id = id
        self.summary = summary
        self.start_datetime = start_datetime


class ClasseListarEventosNaoConfirmados():
    def listarEventosNaoConfirmados(self, qtde_dias: float) -> list:
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
                    calendarId=ID_CALENDARIO_NAO_CONFIRMADOS,
                    timeMin=time_min,
                    timeMax=time_max,
                    pageToken=page_token
                ).execute()
                for event in events['items']:
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
        except HttpError as error:
            print('Ocorreu um erro: %s' % error)

    def formatarEventos(self, qtde_dias: float) -> list:
        nao_formatados = self.listarEventosNaoConfirmados(qtde_dias)
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


listar_eventos = ClasseListarEventosNaoConfirmados()
app = Flask(__name__)


@app.route('/listar_eventos_nao_confirmados', methods=['GET'])
def obter_eventos():
    qtde_dias = 3
    eventos_formatados = listar_eventos.formatarEventos(qtde_dias)
    return jsonify(eventos_formatados)

 # peggou esse evento da onde? [{"id":"hmrlkt8276r40dil56bao8bsa0","start_datetime":"26-05-2023 11:00"}]
if __name__ == '__main__':
    app.run()
