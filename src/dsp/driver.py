import serial
import time
from threading import Thread, Lock
import wave
import pyaudio
import numpy as np
import os
import sys
#import scipy
import socketio

mutex = Lock()
sio = socketio.Client()

arduino=serial.Serial()
arduino.port = sys.argv[1]
arduino.baudrate=9600
arduino.timeout=.1
arduino.open()

FORMAT = pyaudio.paInt16
CHANNELS =1
WAVE_OUTPUT_FILENAME = "file.wav"
CHUNK = 2**11
RATE = 44100
flagPTT=0
flagData=0

dataLst=[]
p=pyaudio.PyAudio()
stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
              frames_per_buffer=CHUNK)

def send_PTT(arduino, PTT_value):
    time.sleep(0.05)
    arduino.write((str(PTT_value)+'\n').encode())

def play_music(filename):

    # Set chunk size of 1024 samples per data frame
    chunk = 1024

    # Open the sound file
    wf = wave.open(filename, 'rb')

    # Create an interface to PortAudio
    p = pyaudio.PyAudio()

    # Open a .Stream object to write the WAV file to
    # 'output = True' indicates that the sound will be played rather than recorded
    stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

    # Read data in chunks
    data = wf.readframes(chunk)

    # Play the sound by writing the audio data to the stream
    while data != b'':
        stream.write(data)
        data = wf.readframes(chunk)

    # Close and terminate the stream
    stream.close()
    p.terminate()

def mic_listener():
    while (True):
        i=0
        flagData = 0
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
        dataLst.clear()
        while (True):  # go for a few seconds
            i += 1
            databits = stream.read(CHUNK)
            # ~~~ time stamp
            t = time.time()

            WAVE_OUTPUT_FILENAME = ("./audio/in_" + str(t) + ".wav")
            # print(databits)
            data = np.fromstring(databits, dtype=np.int16)
            peak = np.average(np.abs(data)) * 2
            #print("%04d %05d" % (i, peak))

            if (peak > 1500 and flagData == 0):
                flagData = 1
                dataLst.append(databits)

            elif (flagData == 1 and peak < 1500):
                flagData = 0
                #print(len(dataLst))
                waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
                waveFile.setnchannels(CHANNELS)
                waveFile.setsampwidth(p.get_sample_size(FORMAT))
                waveFile.setframerate(RATE)
                waveFile.writeframes(b''.join(dataLst))
                waveFile.close()
                #print("end of recording")
                #print(len(dataLst))
                break
            elif (flagData == 1):
                dataLst.append(databits)

        stream.stop_stream()
        stream.close()
        p.terminate()
        # ~~~~ checking if the file is too small
        if (len(dataLst) < 4):
            os.remove(WAVE_OUTPUT_FILENAME)
        else:
            sio.emit('interrupt', WAVE_OUTPUT_FILENAME)
            print(WAVE_OUTPUT_FILENAME)

@sio.event
def connect():
    #print('Connection is OK')
    1+1

@sio.event
def disconnect():
    #print('Connection closed')
    1+1

@sio.event #need to send the file i got
def transmit(fileName):
    fileName = fileName.rstrip()
    print("Request to tx filename " + fileName)
    mutex.acquire()
    # fileName = '1584433430.5190217.wav'
    send_PTT(arduino, 1)
    print("PTT on")
    time.sleep(2)
    #print('Transmitting now: ' + fileName)
    print("Playing your music")
    play_music(fileName)
    print("PTT off")
    send_PTT(arduino, 2)
    mutex.release()
    #print('Transmited')

sio.connect('http://localhost:' + sys.argv[2])
print('Started on driver daaa')
#sio.emit('interrupt', './audio/out_1584466833.wav')
mic_listen_thread = Thread(target = mic_listener)
mic_listen_thread.start()  #calling the fuction when needed

sio.wait()
