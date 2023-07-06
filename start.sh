#!/bin/bash
python google-agenda/cancelar_evento.py &
python google-agenda/editar_evento.py &
python google-agenda/listar_eventos_por_nome_cliente.py &
python google-agenda/listar_eventos_disponiveis.py &
python google-agenda/listar_eventos_agendados.py &
node chatbot/robo.js