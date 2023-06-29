# voice-changer

The purpose of this project is to change the sound of an audio file.

### This project consists of 3 parts:

- Change the user voice (sola Algorithm + pitch-shifting)
- Change the pitch of user voice
- Implement an online voice change algorithm

### Getting Started

To get started with this project, you will need to have:

* Python 3.11
* Numpy
* Wave
* Pyaudio

### Change the user voice (sola Algorithm + pitch-shifting)

In the first phase, we intend to take the audio file from the first speaker, change the speaker voice, and save the new
file. There are different ways to do this. One of the ways to change the sound is to change the pitch of the voice. This
is done by shifting the pitch using special techniques such as pitch Synchronous Over Lap-Add. There is another way.
Using the Synchronous Over Lap-Add algorithm or `SOLA`.

This algorithm for changing the sound consists of three parts:

- Separate the input signals evenly
- Shift separated signals
- Connect the separated parts

###### part one

In this algorithm, we divide the signal by as many as 2048 after that divide each chunk into 4 parts.

```
data_1 = data[0::4]
data_2 = data[1::4]
data_3 = data[2::4]
data_4 = data[3::4]
```

Then we take Fourier transform from the separated parts using fft().

```
data_1_fourier = np.fft.fft(data_1)
data_2_fourier = np.fft.fft(data_2)
data_3_fourier = np.fft.fft(data_3)
data_4_fourier = np.fft.fft(data_4)
```

After we convert, we have to shift each of the separated sections by value of 50, to do this we use roll function
that gives the rotating shift.

```
data_1_fourier = np.roll(data_1_fourier, SHIFT)
data_2_fourier = np.roll(data_2_fourier, SHIFT)
data_3_fourier = np.roll(data_3_fourier, SHIFT)
data_4_fourier = np.roll(data_4_fourier, SHIFT)
```

Now we have to connect the separated parts and create a new audio file. To do this, we must first align the beginning
and end of each part to create less noise. For this reason, we set the beginning and end of each section equal to the
average frequency of each chunk.

```
data_fourier = np.fft.rfft(data)
mean_freq = np.mean(data_fourier)

data_1_fourier[:SHIFT]  = mean_freq 
data_1_fourier[-SHIFT:] = mean_freq
data_2_fourier[:SHIFT]  = mean_freq
data_2_fourier[-SHIFT:] = mean_freq
data_3_fourier[:SHIFT]  = mean_freq 
data_3_fourier[-SHIFT:] = mean_freq
data_4_fourier[:SHIFT]  = mean_freq
data_4_fourier[-SHIFT:] = mean_freq
```

Now we need to reverse the Fourier transform from the generated frequencies, using ifft.
Because the answer of our inverse Fourier transform is not a real number, we must convert them to real numbers.

```
data_1_new = np.fft.ifft(data_1_fourier)
data_2_new = np.fft.ifft(data_2_fourier)
data_3_new = np.fft.ifft(data_3_fourier)
data_4_new = np.fft.ifft(data_4_fourier)

data_1_new = np.real(data_1_new)
data_2_new = np.real(data_2_new)
data_3_new = np.real(data_3_new)
data_4_new = np.real(data_4_new)
```

Finally, connect the separated parts

```
    new_data = np.column_stack((data_1_new, data_2_new, data_3_new, data_4_new)).ravel().astype(
            np.int16)  
    output.writeframes(new_data)
```

### Change the pitch of user voice

Like other algorithms we first get the voice from user. but here as we mention it before we want to change the voice
base on changing the pitch of user voice.
If we increase the pitch of a person's voice, it will sound higher in frequency and
generally more "squeaky" or "childlike" and vice versa if we decrease the pitch of a person's voice, it will sound lower
in frequency and generally more "deep" or "masculine".

So we for doing this we first need user input :

```pycon
while True:
    try:
        # Getting the amount of the pitch shift from user ->
        pitch_shift = int(
            input("Enter the desired pitch shift in Hz (positive to increase, negative to decrease): "))
        break
    except ValueError:
        print("Invalid input. Please enter an integer value.")
```

Main function of algorithm is `modify_pitch`, we pass 4 value to this
function, `string filename & String output_filename & Int pitch_shift & Int rate=44100`.
The sample rate of the audio file is 44100 by default.

We will open the input WAV file (filename that we get as input of function) in binary read mode and reads all the audio
frames from it. It converts these binary audio frames into a NumPy array of 16-bit integers.

```pycon
    wf = wave.open(filename, "rb")  # rb -> Binary read mode: output -> Numpy Array.
    n_frames = wf.getnframes()
    audio_data = wf.readframes(n_frames)

    # Converting the binary audio data from the WAV file into a NumPy array of 16-bit integers ->
    audio_data = np.frombuffer(audio_data, dtype=np.int16)
    wf.close()
```

Next step in the code, is applying the Fast Fourier Transform (FFT) to the audio data. This is a mathematical
operation that converts the audio data into a frequency domain representation. The code then shifts the frequencies of
the audio by the specified amount of semitones. It does this by multiplying the frequency of each audio sample by a
factor that corresponds to the desired pitch shift. This is done in the frequency domain.

```pycon

    audio_fft = rfft(audio_data)  # fft for real-value signal
    n = len(audio_fft)
    shifted_fft = np.zeros(n, dtype=complex)
    shift = int(n * pitch_shift / rate)
    for i in range(n):
        shifted_fft[(i + shift) % n] = audio_fft[i]  # Shifting the value of audio.
```

The formula(`shift = int(n * pitch_shift / rate)`) for calculating the shift variable is based on the relationship
between the desired pitch shift, the length
of the FFT array, and the sample rate.
When we apply the FFT to an audio signal, we convert it from the time domain to the frequency domain. This means that
the audio signal is represented as a series of frequency components. To modify the pitch of the audio signal, we need to
shift these frequency components up or down.
The amount of frequency shift required to achieve a particular pitch shift depends on the length of the FFT array and
the sample rate. This is because the FFT output is a series of frequency bins that represent the signal's frequency
content. The frequency of each bin is proportional to the sample rate and depends on the length of the FFT array.
To calculate the required frequency shift in terms of FFT bins, we need to multiply the desired pitch shift (in
semitones) by a factor that takes into account the length of the FFT array and the sample rate. This factor is
calculated by dividing the pitch shift by the sample rate and then multiplying the result by the length of the FFT
array. The resulting value is rounded down to the nearest integer using the int() function, since FFT bins must be
integers.
In the code, n represents the length of the FFT array, pitch_shift is the desired pitch shift in semitones, and rate is
the sample rate of the audio signal.

When we shift the sound in the frequency domain by modifying the FFT data, we are actually changing the relative
amplitudes of the different frequency components that make up the sound. This results in a change in the perceived pitch
of the sound, even though we are not changing the actual values of the audio samples themselves.
In the frequency domain, the audio signal is represented as a series of frequency components, where each component has a
specific frequency and amplitude. The magnitude of each frequency component represents the strength or amplitude of that
frequency in the sound. By shifting the frequencies of these components up or down, we are effectively changing the
relative amplitudes of the different frequency components in the sound.
For example, if we want to shift the pitch of a sound upwards, we need to shift the frequency components of the sound
upwards. This means that we need to increase the amplitudes of the higher frequency components relative to the lower
frequency components. This change in relative amplitudes results in a higher perceived pitch for the sound.
Similarly, if we want to shift the pitch of a sound downwards, we need to shift the frequency components of the sound
downwards. This means that we need to increase the amplitudes of the lower frequency components relative to the higher
frequency components. This change in relative amplitudes results in a lower perceived pitch for the sound.
Therefore, by modifying the FFT data and shifting the frequencies of the frequency components, we can effectively change
the perceived pitch of the sound without changing the actual values of the audio samples themselves.

In the end we just to need find the inverse fft and make the output file :

```pycon
    modified_audio_data = irfft(shifted_fft).astype(np.int16)  # Inverse fft.
    wf = wave.open(output_filename, "wb")  # wb -> binary Write mode.
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(rate)
    wf.writeframes(modified_audio_data.tobytes())
    wf.close()
```

### Implement an online voice change algorithm

In this phase, the method of changing the sound is the same as the previous phase and does not change,
but for the voice recording section, it is different from the previous phase. In this phase, we put the `stream.read()`
function in a loop and call it, then use the voice.

```
while True:
    data = stream.read(CHUNK) 
    data = np.array(wave.struct.unpack("%dh" % (len(data) / 2),
                                       data))  
    .                                   
    .
    .
```
