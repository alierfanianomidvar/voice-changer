import pyaudio
import wave
import numpy as np
from scipy.io import wavfile
from scipy import signal

CHUNK = 2048
RATE = 32000
FORMAT = pyaudio.paInt16
CHANNEL = 1
TIME = 5
SAVE = "saveVoiceNew.wav"
OUTPUT = "change_voice_New_2.wav"
SHIFT = 50

## for enhancing the voice qulity \
low_cut = 50
high_cut = 8000
cut_off_freq = 100

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
    data_1 = data[0::4]  # divide each chunk into 4 parts
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

    data_1_new = np.fft.ifft(data_1_fourier)  # inverse fft.
    data_2_new = np.fft.ifft(data_2_fourier)
    data_3_new = np.fft.ifft(data_3_fourier)
    data_4_new = np.fft.ifft(data_4_fourier)

    data_1_new = np.real(data_1_new)
    data_2_new = np.real(data_2_new)
    data_3_new = np.real(data_3_new)
    data_4_new = np.real(data_4_new)

    new_data = np.column_stack((data_1_new, data_2_new, data_3_new, data_4_new)).ravel().astype(
        np.int16)  # resemble parts together
    output.writeframes(new_data)

    #####

    sample_rate, sound_data = wavfile.read(OUTPUT)
    sound_data = sound_data / 32767.0

    b, a = signal.butter(4, [low_cut / (sample_rate / 2), high_cut / (sample_rate / 2)], btype='band')
    sound_filtered = signal.filtfilt(b, a, sound_data)

    # Apply FFT to filtered sound data
    sound_fft = np.fft.fft(sound_filtered)

    # Apply high-pass filter to remove low-frequency noise
    fft_size = len(sound_fft)
    sound_fft[:int((fft_size + 1) * cut_off_freq / sample_rate)] = 0

    # Inverse FFT to get enhanced sound signal
    sound_enhanced = np.real(np.fft.ifft(sound_fft))

    # Scale the enhanced sound signal back to the original range
    sound_enhanced = np.int16(sound_enhanced / np.max(np.abs(sound_enhanced)) * 32767)

    # Write the enhanced sound signal to a file
    wavfile.write("change_voice_new.wav", sample_rate, sound_enhanced)

output.close()
save.close()
print("check output.wav ")
