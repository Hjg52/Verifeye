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

def generate_local_summary(content):
    important_sentences = []
    sentences = re.split(r'(?<=[.!?])\s+', content)

    keywords = [
        'data collection', 'third-party', 'cookies', 'tracking',
        'opt-out', 'personal information', 'location', 'retention',
        'share your data', 'we collect', 'we use', 'delete your data',
        'sell your data', 'store your data'
    ]

    header_like = re.compile(r'^[a-z\s]{3,30}$')  # Looks like lowercase section header

    for sentence in sentences:
        sentence = sentence.strip()

        # Skip empty or header-like short phrases (e.g. "use of cookies")
        if header_like.match(sentence) and not sentence.endswith('.'):
            continue

        if any(keyword in sentence for keyword in keywords):
            if sentence.endswith(('.', '!', '?')) and 30 < len(sentence) < 300:
                # Capitalize first letter & ensure it ends with a period
                sentence = sentence[0].upper() + sentence[1:]
                if not sentence.endswith('.'):
                    sentence += '.'
                important_sentences.append(sentence)

        if len(important_sentences) >= 5:
            break

    if not important_sentences:
        return "<h3>📝 Summary of Policy:</h3><p>No clear summary could be generated from this page.</p>"

    summary = "<h3>📝 Summary of Policy:</h3><ul>"
    for s in important_sentences:
        summary += f"<li>{s}</li>\n"
    summary += "</ul>"

    return summary


@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json(force=True)
    url = data.get('url')
    advanced = data.get('advanced', False)  # From frontend toggle

    if not url:
        return jsonify({"result": "❌ No URL provided."}), 400

    try:
        response = requests.get(url, timeout=5)
        content = response.text.lower()

        # Keyword detection for traffic light system
        keywords = [
            'privacy', 'gdpr', 'data collection', 'third-party',
            'cookies', 'tracking', 'opt-out', 'personal information',
            'data sharing', 'location', 'data retention', 'user data'
        ]

        keyword_mentions = sum(len(re.findall(word, content)) for word in keywords)

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

        # Opt-out instructions detection
        opt_out_instructions = None
        opt_out_patterns = [
            r'(you can opt out.*?\.{1,3})',
            r'(to opt[- ]?out.*?\.{1,3})',
            r'(to disable.*?\.{1,3})',
            r'(opt[- ]?out by.*?\.{1,3})',
            r'(to manage your preferences.*?\.{1,3})'
        ]

        for pattern in opt_out_patterns:
            match = re.search(pattern, content)
            if match:
                start = max(match.start() - 100, 0)
                end = min(match.end() + 100, len(content))
                opt_out_instructions = content[start:end].strip()
                break

        if opt_out_instructions and len(opt_out_instructions) < 50:
            opt_out_instructions = "Opt-out instructions were mentioned, but no clear steps were found. Look for an account settings page or privacy settings on the site."

        # Traffic Light Scoring
        if keyword_mentions < 10:
            traffic_light = "🟢 Low Data Collection Risk"
        elif keyword_mentions < 30:
            traffic_light = "🟡 Moderate Data Collection Risk"
        else:
            traffic_light = "🔴 High Data Collection / Tracking Detected"

        # Build output
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

        if advanced:
            output += generate_local_summary(content)

        output += f"""
<p><strong>Total privacy-related keywords found:</strong> {keyword_mentions}</p>
"""

        return jsonify({"result": output})

    except Exception as e:
        return jsonify({"result": f"❌ Error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run()
