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

        # Keywords for traffic light scoring
        keywords = [
            'privacy', 'gdpr', 'data collection', 'third-party',
            'cookies', 'tracking', 'opt-out', 'personal information',
            'data sharing', 'location', 'data retention', 'user data'
        ]

        keyword_mentions = 0
        for word in keywords:
            keyword_mentions += len(re.findall(word, content))

        # Rule-based findings
        findings = []

        if re.search(r'share.*data.*with', content):
            findings.append("⚠️ This site may share your data with third parties.")

        if re.search(r'retain data for|store data for|keep.*data for', content):
            findings.append("🗄️ This site discusses how long your data is stored.")

        if re.search(r'track.*location|location data', content):
            findings.append("📍 This site may track your location.")

        if re.search(r'cookies|tracking', content):
            findings.append("🍪 This site uses cookies or tracking technologies.")

        if re.search(r'you can opt out|opt[- ]?out|to disable|manage your preferences', content):
            findings.append("🔓 This site appears to offer opt-out options for users.")

        if not findings:
            findings.append("ℹ️ No specific privacy practices detected, but some privacy-related terms were found.")

        # Try to extract opt-out instructions
        opt_out_instructions = None
        opt_out_patterns = [
            r'you can opt out.*?\.',
            r'to opt[- ]?out.*?\.',
            r'to disable.*?\.',
            r'opt[- ]?out by.*?\.',
            r'to manage your preferences.*?\.'
        ]

        for pattern in opt_out_patterns:
            match = re.search(pattern, content)
            if match:
                opt_out_instructions = match.group(0).strip()
                break

        # Traffic Light System
        if keyword_mentions < 10:
            traffic_light = "🟢 Low Data Collection Risk"
        elif keyword_mentions < 30:
            traffic_light = "🟡 Moderate Data Collection Risk"
        else:
            traffic_light = "🔴 High Data Collection / Tracking Detected"

        # Build HTML output
        output = f"""
<h2>{traffic_light}</h2>

<h3>🔍 Summary of Detected Practices:</h3>
<ul>
"""

        for finding in findings:
            output += f"<li>{finding}</li>\n"

        output += "</ul>"

        if opt_out_instructions:
            output += f"""
<h3>🔓 Opt-Out Instructions:</h3>
<p>{opt_out_instructions}</p>
"""

        output += f"""
<p><strong>Total privacy-related keywords found:</strong> {keyword_mentions}</p>
"""

        return jsonify({"result": output})

    except Exception as e:
        return jsonify({"result": f"❌ Error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run()
