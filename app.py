@app.route('/fetch-emails')
def fetch_emails():
    mock_messages = [fake_message]
    parsed = [parse_message(m) for m in mock_messages]
    return jsonify(parsed)