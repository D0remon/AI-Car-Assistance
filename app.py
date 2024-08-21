import json
import nltk
import pyttsx3
from googletrans import Translator
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from flask import Flask, request, render_template, jsonify
import threading

# Initialize the Flask application
app = Flask(__name__)

# Initialize the Google Translator
translator = Translator()

# Function to speak text
def speak(text, lang):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if lang in voice.languages:
            engine.setProperty('voice', voice.id)
            break
    engine.say(text)
    engine.runAndWait()
    engine.stop()

# Function to translate text
def translate_text(text, dest_language):
    translation = translator.translate(text, dest=dest_language)
    return translation.text

# Download necessary NLTK data files
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Load the car manual data
with open('car_manual.json', 'r') as f:
    car_manual_data = json.load(f)

# Function to preprocess text
def preprocess(text):
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word.isalpha()]
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens

# Function to find the best matching response
def get_response(user_input):
    user_tokens = preprocess(user_input)
    best_match = None
    max_overlap = 0
    for question, answer in car_manual_data.items():
        question_tokens = preprocess(question)
        overlap = len(set(user_tokens) & set(question_tokens))
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = answer
    return best_match if best_match else "Sorry, I don't have an answer for that question."

# Define the Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def handle_get_response():
    user_input = request.form['user_input']
    language = request.form['language']
    response = get_response(user_input)
    translated_response = translate_text(response, language)
    
    # Use a separate thread for TTS to avoid blocking the main thread
    tts_thread = threading.Thread(target=speak, args=(translated_response, language))
    tts_thread.start()
    
    return jsonify({'response': translated_response})

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)
