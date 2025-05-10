from flask import Flask, request, render_template
from processor import process_meeting_audio

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    audio = request.files['file']
    path = f"./uploads/{audio.filename}"
    audio.save(path)
    process_meeting_audio(path)
    return "Recap video created. Check the static folder!"

if __name__ == '__main__':
    app.run(debug=True)