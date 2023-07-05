from __future__ import print_function
import math
import os.path
from flask import Flask, jsonify
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
            fim = inicio + timedelta(days=math.floor(qtde_dias))
            fim_fim_fim = fim - timedelta(days=1.0)
            # Converte as datas em formato RFC3339
            time_min = inicio.isoformat() + 'T' + agora.strftime('%H:%M:%S') + 'Z'
            time_max = fim_fim_fim.isoformat() + 'T23:59:59Z'

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
                        event['start']['dateTime']
                    )
                    lista_eventos.append(objeto_evento)
                page_token = events.get('nextPageToken')
                if not page_token:
                    break
            return lista_eventos
        except HttpError as error:
            print('Ocorreu um erro: %s' % error)

    def formatarEventosConfirmados(self, qtde_dias: float) -> list:
        nao_formatados = self.listarEventosConfirmados(qtde_dias)
        lista_formatada = []
        for evento in nao_formatados:
            inicio = datetime.strptime(
                evento.start_datetime, f"%Y-%m-%dT%H:%M:%S%z")
            inicio_formatado = inicio.strftime(f"%d-%m-%Y %H:%M")
            evento_formatado = {
                'id': evento.id,
                'summary': evento.summary,
                'start_datetime': inicio_formatado
            }
            lista_formatada.append(evento_formatado)
        print("LISTA EVENTOS confirmados!!! ", lista_formatada)
        return lista_formatada


class Evento:
    def __init__(self, id, summary, start_datetime):
        self.id = id
        self.summary = summary
        self.start_datetime = start_datetime


listar_eventos = ClasseListarEventosConfirmados()
app = Flask(__name__)


@app.route('/listar_eventos_confirmados', methods=['GET'])
def obter_eventos():
    eventos_formatados = listar_eventos.formatarEventosConfirmados(2.0)
    return jsonify(eventos_formatados)


if __name__ == '__main__':
    app.run()
