const io = require('socket.io');
const settings = require('./../../settings.json')
const uiServer = io.listen(settings.ports.ui);
console.log('[-socket] ui-socket listening on ' + settings.ports.ui);
const bus = require('./bus');
let uiSocket = null;
const {exec} = require("child_process");

exec("start chrome http://localhost:8080", (error, stdout, stderr) => {});
console.log('[process] chrome process spawned');
uiServer.on('connection', (socket) => {
    console.log('[-socket] chrome connected to ui-socket');
    uiSocket = socket;
    uiSocket.on('disconnect', () => {
        uiSocket = null;
        console.log('[-socket] chrome disconnected from ui-socket');
        bus.emit('uiDisconnect');
    });
    
    uiSocket.on('messages', (data) => {
        console.log('[-socket] << message from ui');
        bus.emit('messageFromUi', data);
        uiSocket.emit('messages', data);
    })
        
    bus.emit('uiConnect');
});

sendMessageToUi = function(message, systemMsg) {
    console.log('[-socket] >> message to ui');
    uiSocket.emit('messages', {txt: message, systemMsg: systemMsg});
};

module.exports = sendMessageToUi;

