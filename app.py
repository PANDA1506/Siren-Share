from flask import Flask, render_template, request, send_file, jsonify
import os
from utils.sound_cipher import encode_text_to_wav, decode_wav_to_text, text_to_frequencies, frequencies_to_text

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['GET', 'POST'])
def encode():
    if request.method == 'POST':
        text = request.form.get('text', '')
        if not text:
            return render_template('encode.html', error='Please enter some text')
        
        # Generate WAV file
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded.wav')
        encode_text_to_wav(text, output_path)
        
        return send_file(output_path, as_attachment=True, download_name='encoded_message.wav')
    
    return render_template('encode.html')

@app.route('/decode', methods=['GET', 'POST'])
def decode():
    if request.method == 'POST':
        if 'wavfile' not in request.files:
            return render_template('decode.html', error='No file uploaded')
        
        file = request.files['wavfile']
        if file.filename == '':
            return render_template('decode.html', error='No file selected')
        
        if not file.filename.endswith('.wav'):
            return render_template('decode.html', error='Please upload a WAV file')
        
        # Save uploaded file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded.wav')
        file.save(filepath)
        
        # Decode the WAV file
        try:
            decoded_text = decode_wav_to_text(filepath)
            return render_template('decode.html', decoded_text=decoded_text)
        except Exception as e:
            return render_template('decode.html', error=f'Error decoding file: {str(e)}')
    
    return render_template('decode.html')

@app.route('/freqs', methods=['GET', 'POST'])
def freqs():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'encode':
            text = request.form.get('text', '')
            if not text:
                return render_template('freqs.html', error='Please enter some text')
            
            freq_array = text_to_frequencies(text)
            return render_template('freqs.html', freq_array=freq_array, encoded_text=text)
        
        elif action == 'decode':
            freq_str = request.form.get('frequencies', '')
            if not freq_str:
                return render_template('freqs.html', error='Please enter frequency array')
            
            try:
                # Parse the frequency array
                freq_array = [float(f.strip()) for f in freq_str.strip('[]').split(',')]
                decoded_text = frequencies_to_text(freq_array)
                return render_template('freqs.html', decoded_from_freq=decoded_text, freq_input=freq_str)
            except Exception as e:
                return render_template('freqs.html', error=f'Error parsing frequencies: {str(e)}')
    
    return render_template('freqs.html')

@app.route('/decode-client')
def decode_client():
    return render_template('decode_client.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
