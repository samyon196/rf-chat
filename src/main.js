const bus = require('./modules/bus');
const sendMessageToUi = require('./modules/ui');
const sendMessageToDriver = require('./modules/driver');
require('./modules/input');

const express = require('express');
const app = express();
const cors = require('cors');
const settings = require('./../settings.json');
const port = settings.ports.static;

bus.on('messageFromUi', (data) => {
    const spawn = require("child_process").spawn; 
    const process = spawn('python',["./src/dsp/modem.py", "modulate", data.txt]); 
    process.stdout.on('data', function(result) { 
        //console.log('Response from5 py: ' + result.toString());
        // with this result, (filename)
        // go to the driver and tell him to send it out
        sendMessageToDriver(result.toString())

    });
})

bus.on('messageFromDriver', (fileName) => {
    // Use filename and tell python process to demod:
    const spawn = require("child_process").spawn; 
    const process = spawn('python',["./src/dsp/modem.py", "demodulate", fileName]); 
    process.stdout.on('data', function(result) { 
        console.log('Response from py: ' + result.toString());
        // Use the string and send to ... GUI
        sendMessageToUi(result.toString(), false);
    });
});

/* remove after driver is ready */
bus.on('inputEventSamyon', (data) => {
    const spawn = require("child_process").spawn; 
    const process = spawn('python',["./src/dsp/modem.py", "demodulate", data]); 
    process.stdout.on('data', function(result) { 
        if(result.toString().startsWith('[modem] Error was found')) {
            console.log('[--modem] Error was found');
            return;
        }
        sendMessageToUi(result.toString(), false);
    });
});

app.use(express.static(__dirname + '/public'))
app.use(cors());
app.get('/', (req, res) => res.send('Hello world'));
app.listen(port, () => console.log('[-static] server is running'));