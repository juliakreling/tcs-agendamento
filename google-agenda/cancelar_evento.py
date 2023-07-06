from __future__ import print_function
import os.path
from flask import Flask, jsonify
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# SEMPRE QUE MODIFICAR ESSE SCOPES PRECISA DELETAR O ARQUIVO token.json
SCOPES = ['https://www.googleapis.com/auth/calendar']
ID_CALENDARIO_DISPONIVEL = 'd25601d008a84d01457d05710fa71998a93bb6c5b55e0df332087b164badab73@group.calendar.google.com'
ID_CALENDARIO_CONFIRMADOS = '812bfe549dd5ab2c747bac7874a0c500103766d05ce9d03a808bc9769fbefa5b@group.calendar.google.com'


class CancelarEvento():

    def cancelaEvento(self, idEvento: str):
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
            try:
                event = service.events().get(calendarId=ID_CALENDARIO_CONFIRMADOS,
                                             eventId=idEvento).execute()
                id_calendario_deletar = ID_CALENDARIO_CONFIRMADOS
            except:
                event = service.events().get(calendarId=ID_CALENDARIO_NAO_CONFIRMADOS,
                                             eventId=idEvento).execute()
                id_calendario_deletar = ID_CALENDARIO_NAO_CONFIRMADOS

            atualSummary = event['summary']
            dividirSummary = atualSummary.split("-", 1)
            primeiraParte = dividirSummary[0]

            novo_event = {
                'summary': str(primeiraParte),
                'start': event['start'],
                'end': event['end'],
            }

            service.events().delete(calendarId=id_calendario_deletar, eventId=idEvento).execute()
            service.events().insert(calendarId=ID_CALENDARIO_DISPONIVEL, body=novo_event).execute()

        except HttpError as error:
            print('Ocorreu um erro: %s' % error)


editar_eventos = CancelarEvento()
app = Flask(__name__)


@app.route('/cancelar_evento/<string:id_evento>', methods=['GET'])
def editar_evento(id_evento):
    editar_eventos.cancelaEvento(id_evento)
    return jsonify({"message": "Evento cancelado com sucesso!"})


if __name__ == '__main__':
    app.run(port=5003)


# http://127.0.0.1:5003/cancelar_evento/4ni4gfbcrbc4lempmhendod8g1
