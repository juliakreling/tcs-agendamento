const http = require('http');

function enviarMensagem(client, numero, mensagem) {
    client.sendText(numero, mensagem)
        .then((result) => {
            console.log('Mensagem enviada com sucesso:', result);
        })
        .catch((error) => {
            console.error('Erro ao enviar mensagem:', error);
        });
}


function formatar_eventos(jsonData) {
    let mensagemFormatada = 'Horários:\n\n';
    for (let i = 0; i < jsonData.length; i++) {
        const evento = jsonData[i];
        const eventoFormatado = `${evento.start_datetime} - ${evento.summary} - ${evento.id}\n`;
        mensagemFormatada += eventoFormatado;
    }
    return mensagemFormatada;
}

function listar_eventos_disponiveis(parametro) {
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

function listar_eventos_por_nome_cliente(parametro){
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
                    // delete id_eventos_em_espera[message.from];
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


function listar_eventos_agendados(){
    return new Promise((resolve, reject) => {
        http.get(`http://localhost:5004/listar_eventos_agendados/2.0`, (response) => {
            let data = '';

            response.on('data', (chunk) => {
                data += chunk;
            });

            response.on('end', () => {
                console.log("Resposta do servidor: ", data);
                console.log("Tipo de dados: ", typeof data);
                try {
                    const jsonData = JSON.parse(data);
                    resolve(jsonData);
                } catch (error) {
                    console.log("Erro ao analisar JSON: ", error);
                    console.log("Dados que causaram o erro: ", data);
                    reject(new Error("Não foi possível analisar a resposta como JSON: " + data));
                }
            });

        }).on('error', (error) => {
            reject(error);
        });
    });
}


async function formatar_eventos_agendados() {
    try {
        let dados = await listar_eventos_agendados();
        let mensagemFormatada = '';
        for (let i = 0; i < dados.length; i++) {
            const evento = dados[i];
            const eventoFormatado = `${evento.start_datetime} - ${evento.summary} - ${evento.id}\n`;
            mensagemFormatada += eventoFormatado;
        }
        console.log("mensagem json formatada== ", mensagemFormatada)
        return mensagemFormatada;
    } catch (error) {
        console.error("Erro ao formatar os eventos agendados: ", error);
    }
}


module.exports = {
    enviarMensagem,
    formatar_eventos,
    listar_eventos_disponiveis,
    listar_eventos_agendados,
    listar_eventos_por_nome_cliente,
    editar_evento,
    cancelar_evento,
    formatar_eventos_agendados
  };