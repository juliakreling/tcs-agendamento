
const wppconnect = require('@wppconnect-team/wppconnect');
const { error } = require('console');
const http = require('http');

const id_calendario_disponivel = 'd25601d008a84d01457d05710fa71998a93bb6c5b55e0df332087b164badab73'
const id_calendario_confirmados = '812bfe549dd5ab2c747bac7874a0c500103766d05ce9d03a808bc9769fbefa5b'
const id_calendario_nao_confirmados = '3a0334f8befd7aa68908f7dda72f253efb0aec7adf8edf86ee390195cb7130f3'

var userStages = [];
var id_eventos_em_espera = {};

wppconnect.create({
    session: 'whatsbot',
    autoClose: false,
    puppeteerOptions: { args: ['--no-sandbox'] }
})
    .then((client) =>
        client.onMessage((message) => {
            stages(client, message);
        }))
    .catch((error) =>
        console.log(error));


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

function formatarEventos(jsonData) {
    let mensagemFormatada = 'Escolha um horário por ID:\n\n';
    for (let i = 0; i < jsonData.length; i++) {
        const evento = jsonData[i];
        const eventoFormatado = `${evento.start_datetime} - ${evento.summary} - ${evento.id}\n`;
        mensagemFormatada += eventoFormatado;
    }
    return mensagemFormatada;
}

function listarEventosDisponiveis(parametro) {
    return new Promise((resolve, reject) => {
        http.get(`http://localhost:5000/listar_eventos_disponiveis/${parametro}`, (response) => {
            let data = '';

            response.on('data', (chunk) => {
                data += chunk;
            });

            response.on('end', () => {
                console.log("Resposta do servidor: ", data);
                const jsonData = JSON.parse(data);
                resolve(jsonData);
            });

        }).on('error', (error) => {
            reject(error);
        });
    });
}

function listarEventosPorNomeCliente(parametro){
    return new Promise((resolve, reject) => {
        http.get(`http://127.0.0.1:5002/listar_eventos_nome_cliente/${parametro}`, (response) => {
            let data = '';

            response.on('data', (chunk) => {
                data += chunk;
            });

            response.on('end', () => {
                console.log("Resposta do servidor: ", data);
                const jsonData = JSON.parse(data);
                resolve(jsonData);
            });

        }).on('error', (error) => {
            reject(error);
        });
    });
}

function editar_evento(message, id_evento, dados_cliente){
    return new Promise((resolve, reject) => {
        http.get(`http://localhost:5001/editar_evento/${id_evento}/${dados_cliente}`, (response) => {
            let data = '';

            response.on('data', (chunk) => {
                data += chunk;
            });

            response.on('end', () => {
                console.log("Resposta do servidor: ", data);
                const jsonData = JSON.parse(data);
                if (jsonData.message === "Evento editado com sucesso!"){
                    delete id_eventos_em_espera[message.from];
                    resolve(jsonData);
                } else {
                    reject("Erro ao editar o evento");
                }
            });

        }).on('error', (error) => {
            reject(error);
        });
    });
}

function cancelar_evento(id_evento){
    return new Promise((resolve, reject) => {
        http.get(`http://127.0.0.1:5003/cancelar_evento/${id_evento}`, (response) => {
            let data = '';

            response.on('data', (chunk) => {
                data += chunk;
            });

            response.on('end', () => {
                console.log("Resposta do servidor: ", data);
                const jsonData = JSON.parse(data);
                if (jsonData.message === "Evento cancelado com sucesso!"){
                    resolve(jsonData.message);
                } else {
                    reject("Erro ao editar o evento");
                }
            });

        }).on('error', (error) => {
            reject(error);
        });
    });
}


async function stages(client, message) {
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
            listarEventosDisponiveis(floatDays)
                .then(jsonData => {
                    const mensagemFormatada = formatarEventos(jsonData);
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
                    console.log('DELETE id_eventos_em_espera  == ', id_eventos_em_espera[message.from]);
                    const texto = "Agendado!\nSeu atendimento está sendo encerrado.";
                    sendWppMessage(client, message.from, texto);
                    userStages[message.from] = 'default';
                })
                .catch(error => {
                    console.error("Erro ao agendar o evento", error);
                    const texto = "Erro ao agendar evento.";
                    sendWppMessage(client, message.from, texto);
                    userStages[message.from] = 'default';
                })
            }
            break;

        case 'cancelarHorario':
            await sendWppMessage(client, message.from, 'Para cancelar um horário digite seu nome completo.');
            userStages[message.from] = 'aguardandoNomeCompletoCancelamento';
            break;

        case 'aguardandoNomeCompletoCancelamento':
            const nomeCompleto = message.body;
            listarEventosPorNomeCliente(nomeCompleto)
            .then(jsonData => {
                const mensagemFormatada = formatarEventos(jsonData);
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
                const texto = "Cancelado!\nSeu atendimento está sendo encerrado.";
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
            sendWppMessage(client, message.from, 'Atendimento encerrado.');
            userStages[message.from] = 'default';
            break;

        default:
            console.log('userStages no default == ', userStages[message.from]);
            await sendWppMessage(client, message.from, 'Seja bem-vindo! Escolha a opção desejada: \n*1* - Agendar horário\n*2* - Cancelar horário agendado\n*3* - Encerrar Atendimento');
            switch (message.body) {
                case '1':
                    userStages[message.from] = 'agendarHorario';
                    break;
                case '2':
                    userStages[message.from] = 'cancelarHorario';
                    break;
                case '3':
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