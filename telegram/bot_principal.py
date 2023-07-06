import telebot
from telebot import types
from listar_eventos_nao_confirmados import ClasseListarEventosNaoConfirmados
from editar_evento import EditarEvento


CHAVE_API = '6075754026:AAF2jnAxNoDXfJAaYai5nWOmnA4TFypUblU'
ID_CALENDARIO_DISPONIVEL = 'd25601d008a84d01457d05710fa71998a93bb6c5b55e0df332087b164badab73@group.calendar.google.com'
ID_CALENDARIO_CONFIRMADOS = '812bfe549dd5ab2c747bac7874a0c500103766d05ce9d03a808bc9769fbefa5b@group.calendar.google.com'
ID_CALENDARIO_NAO_CONFIRMADOS = '3a0334f8befd7aa68908f7dda72f253efb0aec7adf8edf86ee390195cb7130f3@group.calendar.google.com'

bot = telebot.TeleBot(CHAVE_API)

chat_states = {}
id_eventos_em_espera = {}


@bot.message_handler(commands=["agendar"])
def agendar(mensagem):
    listar_eventos = ClasseListarEventosNaoConfirmados()
    horarios_disponiveis = listar_eventos.formatarEventos(5.0)
    horarios_concatenados = "\n".join(
        "/{} {}".format(item['id'], item['start_datetime']) for item in horarios_disponiveis
    )
    texto = "Horários disponíveis:\n" + horarios_concatenados
    bot.send_message(mensagem.chat.id, texto)
    chat_states[mensagem.chat.id] = "esperando_selecao_horario"


@bot.message_handler(func=lambda message: message.chat.id in chat_states and chat_states[message.chat.id] == "esperando_selecao_horario")
def esperando_horario(message):
    callback_data = message.text.split()[0]
    callback_query = types.CallbackQuery(
        id="1",  # ID único para a consulta de retorno
        from_user=message.from_user,
        data=callback_data,
        chat_instance=message.chat.id,
        json_string=message.json,
    )
    callback_selecao_horario(callback_query)


@bot.message_handler(func=lambda message: message.chat.id in chat_states and chat_states[message.chat.id] == "esperando_dados")
def esperando_dados(message):
    chat_id = message.chat.id
    id_evento = id_eventos_em_espera.get(chat_id)
    if id_evento is not None:
        dados_cliente = message.text
        editar_evento(chat_id, id_evento, dados_cliente)


@bot.message_handler(commands=["encerrar"])
def cancelar(mensagem):
    bot.send_message(
        mensagem.chat.id, 'Seu atendimento está sendo encerrado.')
    bot.stop_polling()


@bot.callback_query_handler(func=lambda call: True)
def callback_selecao_horario(call):
    chat_id = call.message.chat.id if call.message else call.from_user.id
    if chat_id in chat_states and chat_states[chat_id] == "esperando_selecao_horario":
        horario_selecionado = call.data
        id_evento = horario_selecionado.split()[0][1:]
        id_eventos_em_espera[chat_id] = id_evento
        texto = "Para agendar, digite: Nome do tutor, Telefone do tutor, Nome do pet"
        bot.send_message(chat_id, texto)
        chat_states[chat_id] = "esperando_dados"
    else:
        print("Caiu no else da callback_selecao_horario....")


def editar_evento(chat_id, id_evento, dados_cliente):
    classeEditarEvento = EditarEvento()
    classeEditarEvento.moveEventoParaNovoCalendario(
        id_evento, dados_cliente, ID_CALENDARIO_CONFIRMADOS)
    texto = """Agendado!
    Seu atendimento está sendo encerrado."""
    bot.send_message(chat_id, texto)
    del id_eventos_em_espera[chat_id]
    chat_states[chat_id] = None
    bot.stop_polling()


# isso sempre é no final.....
def verificar(mensagem):
    return True


@bot.message_handler(func=verificar)
def responder(mensagem):
    texto = """Seja bem vindo! Clique na opção desejada:

    /agendar Agendar horário
    /cancelar Cancelar horário agendado
    /encerrar Encerrar atendimento
    """
    bot.send_message(mensagem.chat.id, texto)


bot.polling()
