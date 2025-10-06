import numpy as np
import wave
import struct

# Configuration
SAMPLE_RATE = 44100
DURATION_PER_CHAR = 0.2  # seconds per character
BASE_FREQUENCY = 500  # Hz
FREQ_STEP = 50  # Hz per ASCII value

def char_to_frequency(char):
    """Convert a character to its corresponding frequency."""
    ascii_val = ord(char)
    return BASE_FREQUENCY + (ascii_val * FREQ_STEP)

def frequency_to_char(freq):
    """Convert a frequency back to its character."""
    ascii_val = round((freq - BASE_FREQUENCY) / FREQ_STEP)
    if 0 <= ascii_val <= 127:
        return chr(ascii_val)
    return '?'

def encode_text_to_wav(text, output_path):
    """Encode text into a WAV file with frequency-mapped audio."""
    samples = []
    
    for char in text:
        freq = char_to_frequency(char)
        duration = DURATION_PER_CHAR
        num_samples = int(SAMPLE_RATE * duration)
        
        # Generate sine wave for this frequency
        t = np.linspace(0, duration, num_samples, False)
        wave_data = np.sin(2 * np.pi * freq * t)
        samples.extend(wave_data)
    
    # Convert to 16-bit PCM
    samples = np.array(samples)
    samples = np.int16(samples * 32767)
    
    # Write WAV file
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(samples.tobytes())

def decode_wav_to_text(wav_path):
    """Decode a WAV file back to text using FFT."""
    with wave.open(wav_path, 'r') as wav_file:
        sample_rate = wav_file.getframerate()
        num_frames = wav_file.getnframes()
        audio_data = wav_file.readframes(num_frames)
        
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        audio_array = audio_array.astype(np.float32) / 32767.0
    
    # Calculate chunk size
    chunk_size = int(sample_rate * DURATION_PER_CHAR)
    decoded_text = []
    
    # Process each chunk
    num_chunks = len(audio_array) // chunk_size
    for i in range(num_chunks):
        start = i * chunk_size
        end = start + chunk_size
        chunk = audio_array[start:end]
        
        # Perform FFT
        fft = np.fft.fft(chunk)
        freqs = np.fft.fftfreq(len(chunk), 1/sample_rate)
        
        # Find dominant frequency (positive frequencies only)
        positive_freqs = freqs[:len(freqs)//2]
        positive_fft = np.abs(fft[:len(fft)//2])
        
        # Get the frequency with maximum magnitude
        dominant_idx = np.argmax(positive_fft)
        dominant_freq = abs(positive_freqs[dominant_idx])
        
        # Convert frequency back to character
        char = frequency_to_char(dominant_freq)
        decoded_text.append(char)
    
    return ''.join(decoded_text)

def text_to_frequencies(text):
    """Convert text to an array of frequencies."""
    return [char_to_frequency(char) for char in text]

def frequencies_to_text(freq_array):
    """Convert an array of frequencies back to text."""
    return ''.join([frequency_to_char(freq) for freq in freq_array])