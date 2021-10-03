import pyaudio
import numpy as np
import wave
import time

CHUNK = 2048
RATE = 32000
FORMAT = pyaudio.paInt16
CHANNEL = 1
SHIFT = 50

""" recording """
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK)

print("start recording...")
print("talk...")

while True:
    data = stream.read(CHUNK)  # read each chunk
    data = np.array(wave.struct.unpack("%dh" % (len(data) / 2),
                                       data))  # data that is writen has twice size of chunk and we just want half of it

    data_fourier = np.fft.rfft(data)
    mean_freq = np.mean(data_fourier)
    data_1 = data[0::4]     # devide each chunck into 4 parts
    data_2 = data[1::4]
    data_3 = data[2::4]
    data_4 = data[3::4]

    data_1_fourier = np.fft.fft(data_1)
    data_2_fourier = np.fft.fft(data_2)
    data_3_fourier = np.fft.fft(data_3)
    data_4_fourier = np.fft.fft(data_4)

    data_1_fourier = np.roll(data_1_fourier, SHIFT)     # shift each part
    data_2_fourier = np.roll(data_2_fourier, SHIFT)
    data_3_fourier = np.roll(data_3_fourier, SHIFT)
    data_4_fourier = np.roll(data_4_fourier, SHIFT)

    data_1_fourier[:SHIFT] = mean_freq   # set head & tail of each chunk equal to avoid noise
    data_1_fourier[-SHIFT:] = mean_freq
    data_2_fourier[:SHIFT] = mean_freq
    data_2_fourier[-SHIFT:] = mean_freq
    data_3_fourier[:SHIFT] = mean_freq
    data_3_fourier[-SHIFT:] = mean_freq
    data_4_fourier[:SHIFT] = mean_freq
    data_4_fourier[-SHIFT:] = mean_freq

    data_1_new = np.fft.ifft(data_1_fourier)
    data_2_new = np.fft.ifft(data_2_fourier)
    data_3_new = np.fft.ifft(data_3_fourier)
    data_4_new = np.fft.ifft(data_4_fourier)

    data_1_new = np.real(data_1_new)
    data_2_new = np.real(data_2_new)
    data_3_new = np.real(data_3_new)
    data_4_new = np.real(data_4_new)

    new_data = np.column_stack((data_1_new, data_2_new, data_3_new, data_4_new)).ravel().astype(np.int16)  # reasemble parts together

    time.sleep(0.02055)   # this is used for avoiding eco

    output = wave.struct.pack("%dh" % (len(new_data)), *list(new_data))  # pack array into a raw file
    stream.write(output)
