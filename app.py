from flask import Flask, request, jsonify, send_from_directory
import requests
from collections import Counter
import re

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

    if not url:
        return jsonify({"result": "❌ No URL provided."}), 400

    try:
        response = requests.get(url, timeout=5)
        content = response.text.lower()

        # Check for privacy keywords
        keywords = [
            'privacy', 'gdpr', 'data collection', 'third-party',
            'cookies', 'tracking', 'opt-out', 'personal information',
            'data sharing', 'location', 'data retention', 'user data'
        ]

        found_keywords = []

        for word in keywords:
            count = len(re.findall(word, content))
            if count > 0:
                found_keywords.append((word, count))

        if not found_keywords:
            return jsonify({"result": "⚠️ This doesn't appear to be a privacy policy page or contains very few privacy-related terms."})

        found_keywords.sort(key=lambda x: x[1], reverse=True)

        summary = "🔍 Keyword Analysis:\n\n"
        summary += "This page contains the following privacy-related terms:\n\n"

        for word, count in found_keywords:
            summary += f"- {word}: {count} occurrence(s)\n"

        return jsonify({"result": summary})

    except Exception as e:
        return jsonify({"result": f"❌ Error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run()
