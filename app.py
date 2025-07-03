from flask import Flask, request, jsonify, render_template
import os
from openai import OpenAI
from dotenv import load_dotenv
import fitz  # PyMuPDF for PDF text extraction

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# Analyze resume pasted as text
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    resume_text = data.get('resume')

    if not resume_text:
        return jsonify({'error': 'No resume text provided'}), 400

    prompt = generate_prompt(resume_text)

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI career coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        result = response.choices[0].message.content
        return jsonify({'result': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Analyze uploaded PDF resume
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF file uploaded'}), 400

    pdf_file = request.files['pdf']

    try:
        # Extract text from uploaded PDF using PyMuPDF
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        extracted_text = ""
        for page in doc:
            extracted_text += page.get_text()

        if not extracted_text.strip():
            return jsonify({'error': 'No readable text found in PDF.'}), 400

        prompt = generate_prompt(extracted_text)

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI career coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        result = response.choices[0].message.content
        return jsonify({'result': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Reusable prompt builder
def generate_prompt(profile_text):
    return f"""
You are an AI-powered career coach with expertise in resume evaluation, job role mapping, and behavioral interview preparation.

Analyze the following candidate profile and provide:
1. A summary of the candidate's key strengths and expertise.
2. Three ideal job roles or industries that suit this candidate.
3. Three targeted behavioral or technical interview questions for the selected role.
4. For each question, provide a model answer and constructive feedback for the candidate to improve.
5. One tip to improve their resume based on modern hiring standards.

Candidate Profile:
{profile_text}
"""

if __name__ == '__main__':
    app.run(debug=True)
