# voice-changer
The purpose of this project is to change the sound of an audio file.

####This project consists of two parts:
- Change the speaker's voice 
- Implement an online voice change algorithm

####Change the speaker's voice
In the first phase, we intend to take the audio file from the first speaker, change the speaker voice, and save the new file. There are different ways to do this. One of the ways to change the sound is to change the pitch of the voice. This is done by shifting the pitch using special techniques such as pitch Synchronous Over Lap-Add. There is another way. Using the Synchronous Over Lap-Add algorithm or SOLA that we will use SOLA in this project.

This algorithm for changing the sound consists of three parts:
- Separate the input signals evenly
- Shift separated signals
- Connect the separated parts

######part one
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
Now we need to reverse the Fourier transform from the generated frequencies, using  ifft.
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