#!/bin/bash
python ./agendamento/cancelar_evento.py &
python ./agendamento/editar_evento.py &
python ./agendamento/listar_eventos_por_nome_cliente.py &
python ./agendamento/listar_eventos_disponiveis.py &
python ./agendamento/listar_eventos_agendados.py &
node robo.js