const wppconnect = require('@wppconnect-team/wppconnect');
const { error } = require('console');
const http = require('http');
const cron = require('node-cron');

var userStages = [];
var id_eventos_em_espera = {};

const {
    enviarMensagem,
    formatar_eventos,
    listar_eventos_disponiveis,
    listar_eventos_por_nome_cliente,
    editar_evento,
    cancelar_evento,
    listar_eventos_agendados,
    formatar_eventos_agendados
} = require('./funcoes');

const texto_inicial = 'Seja bem-vindo! Escolha a opção desejada:\n\
*1* - Agendar horário\n\
*2* - Listar seus agendamentos\n\
*3* - Cancelar horário agendado\n\
*4* - Encerrar Atendimento\n\
\n\n*Por favor, esteja ciente de que, ao continuar o atendimento, precisaremos dos seus \
dados pessoais para agendar o horário. Além disso, \
você está ciente que receberá mensagens de confirmação e lembrete \
de agendamentos futuros no WhatsApp.*';


wppconnect.create({
    session: 'whatsbot-responder',
    autoClose: false,
    puppeteerOptions: { args: ['--no-sandbox'] }
})
.then(async (client) => {
    client.onStateChange((state) => {
        console.log('State changed: ', state);
        if(state === 'CONNECTED') {
            cron.schedule('*/20 * * * *', function(){
                enviarLembretes(client);
            });
        }
    });

    client.onMessage((message) => {
        estagios_chatbot(client, message);
    });
})
.catch((error) => {
    console.error('Failed to create client: ', error);
});


async function enviarLembretes(client) {
    let dados = await formatar_eventos_agendados();
    console.log("DADOS antes de passar pra json === ", dados)
    let agendamentos = dados.trim().split('\n'); 
    console.log("ENVIAR LEMBRETES == agendamentos == ", agendamentos);

    for (let agendamento of agendamentos) {
        console.log("Dentro do loop: ", agendamento);
        let agendamento_parts = agendamento.split(' - ');

        let data_hora = agendamento_parts[0];
        let summary_parts = agendamento_parts[1].split(',');
        let id = agendamento_parts[2];

        let servico_cliente = summary_parts[0].split('-');
        let servico = servico_cliente[0].trim();
        let nome_cliente = servico_cliente[1].trim();

        let telefone = summary_parts[1].trim();
        let nome_pet = summary_parts[2].trim();

        console.log('servico: ', servico)
        console.log('nome_cliente: ', nome_cliente)
        console.log('telefone: ', telefone)
        console.log('nome_pet: ', nome_pet)
        console.log('data_hora: ', data_hora)
        
        let mensagem = `Olá ${nome_cliente}, esse é um lembrete do seu agendamento para ${servico} no dia ${data_hora}, para o pet ${nome_pet}.`;

        try {
            result = await client.sendText(telefone + '@c.us', mensagem);
            console.log('Result: ', result);
        } catch (error) {
            console.error('Failed to send message: ', error);
        }
    }
}


function sendWppMessage(client, sendTo, text) {
    return new Promise((resolve, reject) =>{
        client
        .sendText(sendTo, text)
        .then((result) => {
            resolve(result); 
        })
        .catch((erro) => {
            console.error('ERRO: ', erro);
        });
    });
}


async function estagios_chatbot(client, message) {
    let stage = userStages[message.from];
    if (!stage) {
        stage = 'default';
        userStages[message.from] = stage;
    }

    console.log('userStages no início --', userStages[message.from]);

    switch (stage) {
        case 'agendarHorario':
            await sendWppMessage(client, message.from, 'Você gostaria de visualizar os horários disponíveis dentro de quantos dias?\n*1* dia\n*3* dias\n*7* dias');
            userStages[message.from] = 'aguardandoDiasAgendamento';
            break;

        case 'aguardandoDiasAgendamento':
            const days = message.body;
            const floatDays = parseFloat(days).toFixed(1);
            listar_eventos_disponiveis(floatDays)
                .then(jsonData => {
                    const mensagemFormatada = formatar_eventos(jsonData);
                    sendWppMessage(client, message.from, mensagemFormatada);
                    userStages[message.from] = 'escolhaHorarioAgendamento';
                })
                .catch(error => {
                    console.error('Ocorreu um erro ao fazer a solicitação:', error);
                });
            break;

        case 'escolhaHorarioAgendamento':
            const horarioEscolhido = message.body;
            id_eventos_em_espera[message.from] = horarioEscolhido;
            console.log('id_eventos_em_espera no escolhaHorarioAgendamento == ', id_eventos_em_espera[message.from]);
            await sendWppMessage(client, message.from, 'Para agendar, digite: \nNome completo do responsável\nTelefone do responsável\nNome do pet\nRaça do pet\nPorte do pet (pequeno, médio ou grande)')
            userStages[message.from] = 'esperandoDadosAgendamento';
            break;

        case 'esperandoDadosAgendamento':
            let id_evento = id_eventos_em_espera[message.from];
            if(id_evento){
                const dadosCliente = message.body;
                editar_evento(message.from, id_evento, dadosCliente)
                .then(jsonData => {
                    delete id_eventos_em_espera[message.from];
                    console.log('DELETE id_eventos_em_espera  == ', id_eventos_em_espera[message.from]);
                    const texto = "Agendado!\nSe precisar de algo a mais estou a disposição.";
                    sendWppMessage(client, message.from, texto);
                    userStages[message.from] = 'default';
                })
                .catch(error => {
                    console.error("Erro ao agendar o evento", error);
                    userStages[message.from] = 'default';
                })
            }
            break;

        case 'listarAgendamentos':
            await sendWppMessage(client, message.from, 'Para listar seus horários digite seu nome completo.');
            userStages[message.from] = 'aguardandoNomeCompletoListagemAgendamentos';
            break;
        
        case 'aguardandoNomeCompletoListagemAgendamentos':
            const nomeCompletoListagem = message.body;
            sendWppMessage(client, message.from, 'Seus agendamentos futuros:');
            listar_eventos_por_nome_cliente(nomeCompletoListagem)
            .then(jsonData => {
                const mensagemFormatadaListagem = formatar_eventos(jsonData);
                sendWppMessage(client, message.from, mensagemFormatadaListagem);
                sendWppMessage(client, message.from, 'Se precisar de algo a mais estou a disposição.');
                userStages[message.from] = 'default';
            })
            .catch(error => {
                console.error('Ocorreu um erro ao fazer a solicitação:', error);
            });
            break;
        
        case 'cancelarHorario':
            await sendWppMessage(client, message.from, 'Para cancelar um horário digite seu nome completo.');
            userStages[message.from] = 'aguardandoNomeCompletoCancelamento';
            break;

        case 'aguardandoNomeCompletoCancelamento':
            const nomeCompleto = message.body;
            listar_eventos_por_nome_cliente(nomeCompleto)
            .then(jsonData => {
                const mensagemFormatada = formatar_eventos(jsonData);
                sendWppMessage(client, message.from, mensagemFormatada);
                userStages[message.from] = 'escolhaHorarioCancelamento';
            })
            .catch(error => {
                console.error('Ocorreu um erro ao fazer a solicitação:', error);
            });                
            break;
        
        case 'escolhaHorarioCancelamento':
            const horarioCancelamento = message.body;
            cancelar_evento(horarioCancelamento)
            .then(jsonData => {
                const texto = "Cancelado!\nSeu atendimento está sendo encerrado.\nSe precisar de algo a mais estou a disposição.";
                sendWppMessage(client, message.from, texto);
                userStages[message.from] = 'default';
            })
            .catch(error => {
                console.error("Erro ao cancelar o evento", error);
                const texto = "Erro ao cancelar evento.";
                sendWppMessage(client, message.from, texto);
                userStages[message.from] = 'default';
            })
            break;

        case 'encerrarAtendimento':
            sendWppMessage(client, message.from, 'Atendimento encerrado. Mande uma mensagem quando quiser novo atendimento.');
            userStages[message.from] = 'default';
            break;

        default:
            console.log('userStages no default == ', userStages[message.from]);
            await sendWppMessage(client, message.from, texto_inicial);
            switch (message.body) {
                case '1':
                    userStages[message.from] = 'agendarHorario';
                    break;
                case '2':
                    userStages[message.from] = 'listarAgendamentos';
                    break;
                case '3':
                    userStages[message.from] = 'cancelarHorario';
                    break;
                case '4':
                    userStages[message.from] = 'encerrarAtendimento';
                    break;
                default:
                    console.log('NAO PODE CAIR AQUI, OQ FACO????');
                    break;
            }
            break;
    }
    
    console.log('userStages no final == ', userStages[message.from]);
}