from __future__ import print_function
import math
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
ID_CALENDARIO_DISPONIVEL = 'd25601d008a84d01457d05710fa71998a93bb6c5b55e0df332087b164badab73@group.calendar.google.com'
ID_CALENDARIO_CONFIRMADOS = '812bfe549dd5ab2c747bac7874a0c500103766d05ce9d03a808bc9769fbefa5b@group.calendar.google.com'
ID_CALENDARIO_NAO_CONFIRMADOS = '3a0334f8befd7aa68908f7dda72f253efb0aec7adf8edf86ee390195cb7130f3@group.calendar.google.com'


class ClasseListarEventosPorNomeCliente():

    def listarEventosPorNomeCliente(self, nome_completo, id_calendario) -> list:
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
            # Define o intervalo de tempo para a consulta como 30 dias
            inicio = agora.date()
            fim = inicio + timedelta(days=math.floor(30))
            fim_fim_fim = fim - timedelta(days=1.0)
            # Converte as datas em formato RFC3339
            time_min = inicio.isoformat() + 'T' + agora.strftime('%H:%M:%S') + 'Z'
            time_max = fim_fim_fim.isoformat() + 'T23:59:59Z'

            nome_editado = nome_completo.lower()
            page_token = None
            while True:
                pegando_eventos = service.events().list(
                    calendarId=id_calendario,
                    timeMin=time_min,
                    timeMax=time_max,
                    pageToken=page_token
                ).execute()
                for evento in pegando_eventos['items']:
                    if 'summary' in evento:
                        if nome_editado in evento['summary'].lower():
                            objeto_evento = Evento(
                                evento['id'],
                                evento['summary'],
                                evento['start']['dateTime']
                            )
                            lista_eventos.append(objeto_evento)
                page_token = pegando_eventos.get('nextPageToken')
                if not page_token:
                    break

            return lista_eventos
        except HttpError as error:
            print('Ocorreu um erro: %s' % error)

    def formatarEventosDisponiveis(self, nome_completo) -> list:
        nao_confirmados = self.listarEventosPorNomeCliente(
            nome_completo, ID_CALENDARIO_NAO_CONFIRMADOS
        )
        confirmados = self.listarEventosPorNomeCliente(
            nome_completo, ID_CALENDARIO_CONFIRMADOS
        )
        lista_total_nao_formatada = nao_confirmados + confirmados
        lista_formatada = []
        for evento in lista_total_nao_formatada:
            inicio = datetime.strptime(
                evento.start_datetime, f"%Y-%m-%dT%H:%M:%S%z")
            inicio_formatado = inicio.strftime(f"%d-%m-%Y %H:%M")
            evento_formatado = {
                'id': evento.id,
                'summary': evento.summary,
                'start_datetime': inicio_formatado
            }
            lista_formatada.append(evento_formatado)
        print("LISTA EVENTOS DO USUARIO ===  ", lista_formatada)
        return lista_formatada


class Evento:
    def __init__(self, id, summary, start_datetime):
        self.id = id
        self.summary = summary
        self.start_datetime = start_datetime


listar_eventos = ClasseListarEventosPorNomeCliente()
app = Flask(__name__)


@app.route('/listar_eventos_nome_cliente/<string:parametro>', methods=['GET'])
def obter_eventos(parametro):
    eventos_formatados = listar_eventos.formatarEventosDisponiveis(parametro)
    return jsonify(eventos_formatados)


if __name__ == '__main__':
    app.run(port=5002)


# http://127.0.0.1:5002/listar_eventos_nome_cliente/
