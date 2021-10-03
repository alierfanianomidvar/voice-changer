import pyaudio
import wave
import numpy as np

CHUNK = 2048
RATE = 32000
FORMAT = pyaudio.paInt16
CHANNEL = 1
TIME = 5
SAVE = "saveVoice.wav"
OUTPUT = "output.wav"
SHIFT = 50


""" recording """
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("start recording ...")
data = []

for i in range(0, int(RATE / CHUNK * TIME)):
    tmp = stream.read(CHUNK)
    data.append(tmp)

print("finish recording...")

stream.stop_stream()
stream.close()
audio.terminate()

output = wave.open(SAVE, 'wb')
output.setnchannels(CHANNEL)
output.setsampwidth(audio.get_sample_size(FORMAT))
output.setframerate(RATE)
output.writeframes(b''.join(data))
output.close()

""" changing """
print("start changing ...")

save = wave.open(SAVE, "r")
save.getparams()

info = list(save.getparams())  # set same parameters for output audio
info[3] = 0
output = wave.open(OUTPUT, "w")
output.setparams(info)

newRate = RATE // 10
count = save.getnframes() // newRate  # devide data into chunks
for i in range(count):
    data = np.frombuffer(save.readframes(newRate), dtype=np.int16) * 3  # increase quality of voice
    data_fourier = np.fft.rfft(data)
    mean_freq = np.mean(data_fourier)
    data_1 = data[0::4]  # divide each chunck into 4 parts
    data_2 = data[1::4]
    data_3 = data[2::4]
    data_4 = data[3::4]

    data_1_fourier = np.fft.fft(data_1)
    data_2_fourier = np.fft.fft(data_2)
    data_3_fourier = np.fft.fft(data_3)
    data_4_fourier = np.fft.fft(data_4)

    data_1_fourier = np.roll(data_1_fourier, SHIFT)  # shift each part
    data_2_fourier = np.roll(data_2_fourier, SHIFT)
    data_3_fourier = np.roll(data_3_fourier, SHIFT)
    data_4_fourier = np.roll(data_4_fourier, SHIFT)

    data_1_fourier[:SHIFT] = mean_freq  # set head & tail of each chunk equal to avoid noise
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

    new_data = np.column_stack((data_1_new, data_2_new, data_3_new, data_4_new)).ravel().astype(
        np.int16)  # reasemble parts together
    output.writeframes(new_data)

output.close()
save.close()
print("check output.wav ")
