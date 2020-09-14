const io = require('socket.io');
const settings = require('./../../settings.json')
const driverServer = io.listen(settings.ports.driver);
console.log('[-socket] driver-socket listening on ' + settings.ports.driver);
const bus = require('./bus');
let driverSocket = null;

const spawn = require("child_process").spawn; 
spawn('python',["./src/dsp/driver.py", settings.ports.arduino, settings.ports.driver]); 
console.log('[process] driver process spawned');
driverServer.on('connection', (socket) => {
    console.log('[-socket] driver process connected to driver-socket');
    driverSocket = socket;
    driverSocket.on('disconnect', () => {
        uiSocket = null;
        console.log('[-socket] driver process disconnected from driver-socket');
        bus.emit('driverDisconnect');
    });
    
    driverSocket.on('interrupt', (data) => {
        console.log('[-socket] << interrupt from driver');
        bus.emit('messageFromDriver', data);
    })
        
    bus.emit('driverConnect');
});

sendMessageToDriver = function(fileName) {
    console.log('[-socket] >> tx request to driver');
    driverSocket.emit('transmit', fileName);
};

module.exports = sendMessageToDriver;

