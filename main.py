from flask import Flask, render_template, request, jsonify
from utils.ai_generator import generate_content, classify_content

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    initial_title = data.get('initial_title', '')
    initial_idea = data.get('initial_idea', '')
    feedback = data.get('feedback', [])

    generated_content = generate_content(initial_title, initial_idea, feedback)
    classified_content = classify_content(generated_content)

    return jsonify(classified_content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
