"""
This script assumes that the witness files from the noir program are in the folder this script is executed in.

WHAT DOES THIS SCRIPT DO!
1. Read the witness files from the artifacts folder.
2. Smooth their evaluations to be within the audible evaluation domain.
3. Perform an FFT on the evaluations to get the frequency-domain signal.
4. Perform an inverse FFT on the positive frequencies to get the time-domain signal.
5. Normalize the inverse FFT result to fit within the range of -32768 to 32767. (16-bit signed integer for the .wav format)
6. Construct a wavetable over the normalized signal.

The wavetables are saved as .wav files which can be dragged into your wavetable synthesizer of choice. (e.g. Serum, Vital, etc.)
"""

import numpy as np
import math, wave, array
from scipy.interpolate import BarycentricInterpolator

def create_wavetable(name):

    print(f"Creating wavetable for {name}")

    witness_string = ""
    with open(f"./artifacts/{name}", "r") as file:
        witness_string = file.read()

    BIT_32 = 2**14;
    # Split the hex string into separate hex values
    hex_values = [witness_string[i:i+64] for i in range(0, len(witness_string), 64)]
    # Convert the hex values to integers
    y_val = [int(hex_value, 16) for hex_value in hex_values]
    y_val = [value % BIT_32 for value in y_val]
    y_val = [math.log2(value) if value != 0 else 0 for value in y_val]

    # Perform FFT to get the frequency-domain signal
    fft_result = np.fft.fft(y_val)

    # Only take the positive frequencies (first half)
    positive_fft_result = fft_result[:len(fft_result)//2]

    # Perform inverse FFT to get the time-domain signal from positive frequencies
    fft_result = np.fft.ifft(positive_fft_result)

    # Normalize the inverse FFT result to fit within the range of -32768 to 32767
    fft_result_real = np.real(fft_result)
    min_val = np.min(fft_result_real)
    max_val = np.max(fft_result_real)

    # Scale fft_result_real to the range -32768 to 32767
    scaled_fft_result = 65535 * (fft_result_real - min_val) / (max_val - min_val) - 32768

    # # Ensure the values are within the correct range (optional, for safety)
    # scaled_fft_result = np.clip(scaled_fft_result, -32768, 32767)

    # Settings
    data = array.array('h')  # signed short integer (-32768 to 32767) data
    sampleRate = 44100       # of samples per second (standard)
    numChan    = 1           # of channels (1: mono, 2: stereo)
    dataSize   = 2           # 2 bytes from signed short integers (bit depth = 16)
    numSamples = 1024        # of samples per waveform
    numWaves   = 32          # of waveforms in wavetable
    pi         = math.pi     # the constant pi

    # Define wavetable as function of time 0 <= t < 1
    # and interpolation parameter 0 <= x < 1
    def waves(t, x):
        # Use the normalized inverse FFT result
        index = int(x * numSamples + t)
        return scaled_fft_result[index % len(scaled_fft_result)]

    # Loop through waveforms in wavetable
    for waveIndex in range(numWaves):
        # x = waveIndex / numWaves
        
        # Loop through samples in waveform
        for sampleIndex in range(numSamples):
            # t = sampleIndex / numSamples
            
            # Append new sample to array
            sample = waves(sampleIndex, waveIndex)
            data.append(int(sample))
            
    # Generate .wav file
    f = wave.open(f'{name}_wavetable.wav', 'w')
    f.setparams((numChan, dataSize, sampleRate, numSamples * numWaves, "NONE", "Uncompressed"))
    f.writeframes(data.tobytes())
    f.close()

# File name to read evaluations from
files = [
    "w_1_lagrange","w_2_lagrange", "w_3_lagrange", "w_4_lagrange",
    "q_1_lagrange",  "q_2_lagrange", "q_3_lagrange", "q_4_lagrange", "q_c_lagrange", 
    "q_aux_lagrange", "q_c_lagrange",  "q_aux_lagrange", "q_arith_lagrange", "q_sort_lagrange", "q_elliptic_lagrange",
]
for file in files:
    create_wavetable(file)
