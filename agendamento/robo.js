// from listar_eventos_nao_confirmados import ClasseListarEventosNaoConfirmados
import ClasseListarEventosNaoConfirmados from listar_eventos_nao_confirmados

const wppconnect = require('@wppconnect-team/wppconnect');

var userStages = [];

wppconnect.create({
    session: 'whatsbot',
    autoClose: false,
    puppeteerOptions: { args: ['--no-sandbox'] }
})
    .then((client) =>
        client.onMessage((message) => {
            console.log('Mensagem digitada pelo usuário: ' + message.body);
            stages(client, message);
        }))
    .catch((error) =>
        console.log(error));


function stages(client, message) {
    stage = userStages[message.from];
    switch (stage) {
        case 'agendarHorario':
            //listar_eventos = ClasseListarEventosNaoConfirmados()
            // USAR FLASK PRA FAZER ISSOOO!
           
            userStages[message.from] = 'CPF';
            break;
        case 'cancelarHorario':
            const cpf = message.body;
            sendWppMessage(client, message.from, 'Obrigada por informar seu CPF: ' + cpf);
            sendWppMessage(client, message.from, 'Fim');
            userStages[message.from] = 'Fim';
            break;
        case 'encerrarAtendimento':
            sendWppMessage(client, message.from, 'Atendimento encerrado.');
            break;
        default:
            // console.log('*Usuário atual* from:' + message.from);
            sendWppMessage(client, message.from, 'Seja bem vindo! Escolha a opção desejada: \n1 - Agendar horário\n2 - Cancelar horário agendado\n3 - Encerrar Atendimento');
            switch(message.body){
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
                    sendWppMessage(client, message.from, 'Opção inválida!');
            }
    }
}


function sendWppMessage(client, sendTo, text) {
    client
        .sendText(sendTo, text)
        .then((result) => {
            // console.log('SUCESSO: ', result); 
        })
        .catch((erro) => {
            console.error('ERRO: ', erro);
        });
}