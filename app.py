from flask import Flask, request, jsonify, send_file
import openai
import requests
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    url = data.get('url')
    advanced = data.get('advanced', False)

    if not url:
        return "❌ No URL provided.", 400

    try:
        response = requests.get(url, timeout=5)
        content = response.text.lower()

        if not any(keyword in content for keyword in ['privacy', 'gdpr', 'data collection', 'cookie', 'personal information']):
            return "⚠️ This doesn't appear to be a privacy policy page. Please check the URL."

        if advanced:
            prompt = f"""
            Analyze the following privacy policy found at {url}. Provide a detailed breakdown of:
            - What data is collected
            - How the data is used
            - Third-party sharing details
            - Data retention policy
            - User control options
            Use clear, structured bullet points.
            """
        else:
            prompt = f"""
            Summarize the main points of the privacy policy found at {url} in 2-3 sentences.
            Focus on what data is collected and how it's used.
            """

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a privacy policy analysis assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        result_text = completion.choices[0].message.content.strip()

        return result_text

    except Exception as e:
        return f"❌ Error processing request: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True)
