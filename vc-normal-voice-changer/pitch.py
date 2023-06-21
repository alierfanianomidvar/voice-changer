import pyaudio
import wave
import numpy as np
from scipy.fft import rfft, irfft


def record_audio(filename, duration=5, rate=44100, channels=1, chunk=1024, format=pyaudio.paInt16):
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


def modify_pitch(filename, output_filename, pitch_shift, rate=44100):
    wf = wave.open(filename, "rb")
    n_frames = wf.getnframes()
    audio_data = wf.readframes(n_frames)
    audio_data = np.frombuffer(audio_data, dtype=np.int16)
    wf.close()

    audio_fft = rfft(audio_data)
    n = len(audio_fft)
    shifted_fft = np.zeros(n, dtype=complex)
    shift = int(n * pitch_shift / rate)

    for i in range(n):
        shifted_fft[(i + shift) % n] = audio_fft[i]

    modified_audio_data = irfft(shifted_fft).astype(np.int16)

    wf = wave.open(output_filename, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(rate)
    wf.writeframes(modified_audio_data.tobytes())
    wf.close()


def main():

    # Output file name ->
    input_filename = "recorded_audio_3.wav"
    output_filename = "modified_audio_3.wav"

    record_audio(input_filename)

    while True:
        try:
            pitch_shift = int(
                input("Enter the desired pitch shift in Hz (positive to increase, negative to decrease): "))
            break
        except ValueError:
            print("Invalid input. Please enter an integer value.")

    modify_pitch(input_filename, output_filename, pitch_shift)
    print(f"Modified audio saved as {output_filename}")


if __name__ == "__main__":
    main()
