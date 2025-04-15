from flask import Flask, request, jsonify, send_from_directory
import openai
import requests
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json(force=True)
    url = data.get('url')
    advanced = data.get('advanced', False)

    if not url:
        return jsonify({"result": "❌ No URL provided."}), 400

    try:
        response = requests.get(url, timeout=5)
        content = response.text.lower()

        if not any(keyword in content for keyword in ['privacy', 'gdpr', 'data collection', 'cookie', 'personal information']):
            return jsonify({"result": "⚠️ This doesn't appear to be a privacy policy page. Please check the URL."})

        prompt = f"Summarize the main points of the privacy policy at {url}."
        if advanced:
            prompt = f"""
            Analyze the privacy policy found at {url}. Provide a detailed breakdown of:
            - What data is collected
            - How it is used
            - Third-party sharing
            - Data retention
            - User controls
            """

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a privacy policy analysis assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        result_text = completion.choices[0].message.content.strip()
        return jsonify({"result": result_text})

    except Exception as e:
        return jsonify({"result": f"❌ Error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run()
