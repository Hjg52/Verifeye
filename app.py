from flask import Flask, request, jsonify, send_from_directory
import requests
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

        keywords = [
            'privacy', 'gdpr', 'data collection', 'third-party',
            'cookies', 'tracking', 'opt-out', 'personal information',
            'data sharing', 'location', 'data retention', 'user data'
        ]

        found_keywords = []
        total_mentions = 0

        for word in keywords:
            count = len(re.findall(word, content))
            if count > 0:
                found_keywords.append((word, count))
                total_mentions += count

        if not found_keywords:
            return jsonify({"result": "⚠️ This doesn't appear to be a privacy policy page or contains very few privacy-related terms."})

        found_keywords.sort(key=lambda x: x[1], reverse=True)

        # Generate readable summary
        summary = "🔍 Analysis Result:\n\n"

        for word, count in found_keywords:
            summary += f"- The term '{word}' appears {count} time(s).\n"

        if total_mentions < 10:
            traffic_light = "🟢 Low Data Collection Risk"
        elif total_mentions < 30:
            traffic_light = "🟡 Moderate Data Collection Risk"
        else:
            traffic_light = "🔴 High Data Collection / Tracking Detected"

        final_output = f"{traffic_light}\n\nThis site mentions key privacy-related terms a total of {total_mentions} time(s).\n\n{summary}"

        return jsonify({"result": final_output})

    except Exception as e:
        return jsonify({"result": f"❌ Error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run()
