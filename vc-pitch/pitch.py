import pyaudio
import wave
import numpy as np
from scipy.fft import rfft, irfft
import matplotlib.pyplot as plt



def record_audio(
        filename,
        duration=5,
        rate=44100,
        channels=1,
        chunk=1024,
        format=pyaudio.paInt16):
    p = pyaudio.PyAudio()

    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    print(f"Recording for {duration} seconds...")

    frames = []

    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print("Done recording.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b"".join(frames))
    wf.close()


def modify_pitch(
        filename,
        output_filename,
        pitch_shift,
        rate=44100):
    wf = wave.open(filename, "rb")  # rb -> Binary read mode: output -> Numpy Array.
    n_frames = wf.getnframes()
    audio_data = wf.readframes(n_frames)

    # Converting the binary audio data from the WAV file into a NumPy array of 16-bit integers ->
    audio_data = np.frombuffer(audio_data, dtype=np.int16)
    wf.close()

    #audio_fft = rfft(audio_data)  # fft for real-value signal
    audio_fft = np.fft.rfft(audio_data)  # fft for real-value signal
    n = len(audio_fft)
    shifted_fft = np.zeros(n, dtype=complex)
    shift = int(n * pitch_shift / rate)

    time = np.arange(len(audio_data)) / rate
    # Plot the original Voice
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    axs[0, 0].plot(time, audio_data)
    axs[0, 0].set_title("Original Audio")
    axs[0, 0].set_xlabel("Time (s)")
    axs[0, 0].set_ylabel("Amplitude")

    freqs = np.fft.rfftfreq(len(audio_data), 1 / rate)
    freq_range = (freqs > 0) & (freqs < 2000)  # Only plot frequencies up to 2000 Hz
    axs[0, 1].plot(freqs[freq_range], np.abs(audio_fft)[freq_range])
    axs[0, 1].set_title("Original FFT")
    axs[0, 1].set_xlabel("Frequency (Hz)")
    axs[0, 1].set_ylabel("Magnitude")

    print("data :", audio_data[1])
    for i in range(n):
        print(i, "move to -> ", (i + shift) % n)
        shifted_fft[(i + shift) % n] = audio_fft[i]  # Shifting the value of audio.

    modified_audio_data = irfft(shifted_fft).astype(np.int16)  # Inverse fft.

    print("modified_audio_data:", modified_audio_data[1])

    # Plot the modified Voice
    axs[1, 0].plot(time, modified_audio_data)
    axs[1, 0].set_title("Modified Audio")
    axs[1, 0].set_xlabel("Time (s)")
    axs[1, 0].set_ylabel("Amplitude")

    residual_signal = modified_audio_data - audio_data
    axs[1, 1].plot(time, residual_signal)
    axs[1, 1].set_title("Residual Signal")
    axs[1, 1].set_xlabel("Time (s)")
    axs[1, 1].set_ylabel("Amplitude")
    plt.tight_layout()
    plt.show()

    #filtered_audio_data = apply_lowpass_filter(modified_audio_data, rate)

    wf = wave.open(output_filename, "wb")  # wb -> binary Write mode.
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(rate)
    wf.writeframes(modified_audio_data.tobytes())
    wf.close()


def start():
    # Output file name ->
    input_filename = "recorded_audio_3.wav"
    output_filename = "modified_audio_3.wav"

    # Recording the user voice and save it with the name tf ->
    record_audio(input_filename)

    while True:
        try:
            # Getting the amount of the pitch shift from user ->
            pitch_shift = int(
                input("Enter the desired pitch shift in Hz (positive to increase, negative to decrease): "))
            break
        except ValueError:
            print("Invalid input. Please enter an integer value.")

    # Changing the pitch function ->
    modify_pitch(input_filename, output_filename, pitch_shift)
    print(f"Modified audio saved as {output_filename}")


if __name__ == "__main__":
    start()
