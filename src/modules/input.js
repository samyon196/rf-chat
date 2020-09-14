const bus = require('./bus');
const stdin = process.openStdin();
stdin.on('data', (data) => {
    data = data.toString().trim();
    //console.log('Got: ' + data);
    bus.emit('inputEventSamyon', data);
});