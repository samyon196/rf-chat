import numpy as np
import pylab as pl
import scipy.signal.signaltools as sigtool
import scipy.signal as signal
from numpy.random import sample
from scipy.io.wavfile import write
from scipy.io import wavfile
import binascii
import sys
import time
subdir = "audio"

# the following variables setup the system
Fc = 16000  # simulate a carrier frequency of 1kHz
Fbit = 50  # simulated bitrate of data
Fdev = 1000  # frequency deviation, make higher than bitrate
N = 64  # how many bits to send
A = 1  # transmitted signal amplitude
Fs = 44100  # sampling frequency for the simulator, must be higher than twice the carrier frequency
A_n = 0.10  # noise peak amplitude

def frombits(bits):
    chars = []
    for b in range(int(len(bits) / 8)):
        byte = bits[b*8:(b+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)

def str2bits(text):
    bitArr = []
    strLst = list(text)
    strLst = [ord(c) for c in strLst]
    for i in strLst:
        for j in list("{0:08b}".format(i)):
            bitArr.append(int(j))
    #print(bitArr)
    return bitArr

def modulate2fsk(text):
    # the following variables setup the system
    Fc = 1000  # simulate a carrier frequency of 1kHz
    Fbit = 50  # simulated bitrate of data
    Fdev = 500  # frequency deviation, make higher than bitrate
    N = 64  # how many bits to send
    A = 1  # transmitted signal amplitude
    Fs = 44100  # sampling frequency for the simulator, must be higher than twice the carrier frequency
    A_n = 0.10  # noise peak amplitude
    N_prntbits = 10  # number of bits to print in plots
    preemble=[1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]
    data_in = [0,0,0,0,1,1,1,1,1,1,1,1,1,1]+preemble+str2bits(text)
    N = len(data_in)
    t = np.arange(0, float(N) / float(Fbit), (1 / float(Fs)), dtype=np.float)
    m = np.zeros(0).astype(float)
    for bit in data_in:
        if bit == 0:
            m = np.hstack((m, np.multiply(np.ones(int(Fs / Fbit)), Fc + Fdev)))
        else:
            m = np.hstack((m, np.multiply(np.ones(int(Fs / Fbit)), Fc - Fdev)))
    y = np.zeros(0)
    y = A * np.cos(2 * np.pi * np.multiply(m, t))
    y=np.int16(y * 32767)
    timeNow=time.time()
    write("./" + subdir + "/out_" + str(int(timeNow))+".wav", Fs, y)
    return "./" + subdir + "/out_" + str(int(timeNow))+".wav"

def demodulate2fsk(fileName):
    preemble = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    fs, y = wavfile.read(fileName)
    y_diff = np.diff(y, 1)
    y_env = np.abs(sigtool.hilbert(y_diff))
    h = signal.firwin(numtaps=100, cutoff=Fbit * 2, nyq=Fs / 2)
    y_filtered = signal.lfilter(h, 1.0, y_env)
    mean = np.mean(y_filtered)
    rx_data = []
    sampled_signal = y_filtered[int(Fs / Fbit / 2):len(y_filtered):int(Fs / Fbit)]
    for bit in sampled_signal:
        if bit > mean:
            rx_data.append(0)
        else:
            rx_data.append(1)
    for i in range(len(rx_data)-24):
        if(rx_data[i:i+24]==preemble):
            indexStart=i+24
            break
    rx_data=rx_data[indexStart:]
    return frombits(rx_data)

def main():
    try:
        args=sys.argv
        if(args[1] == "modulate"):
            fileName=modulate2fsk(args[2])
            print(fileName)
        elif(args[1] == "demodulate"):
            text=demodulate2fsk(args[2])
            print(text)
    except:
        print('[modem] Error was found')


main()