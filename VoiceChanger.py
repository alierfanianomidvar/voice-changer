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

