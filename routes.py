
from flask import Flask, request, Response, jsonify
from datetime import datetime

from utils import generate_random_string

app = Flask(__name__)


@app.route('/whoami', methods=['GET'])
def whoami():
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown Browser')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    response = {
        "client_ip": client_ip,
        "browser": user_agent,
        "current_server_time": current_time
    }
    return response, 200


@app.route('/source_code', methods=['GET'])
def source_code():
    try:
        with open(__file__, 'r', encoding='utf-8') as file:
            source = file.read()
    except Exception as e:
        return {"error": "Unable to read source code", "details": str(e)}, 500

    return Response(source, mimetype='text/plain')


@app.route('/random', methods=['GET'])
def random_string():
    try:
        length = request.args.get('length', default=8, type=int)
        specials = request.args.get('specials', default=0, type=int)
        digits = request.args.get('digits', default=0, type=int)

        if not (1 <= length <= 100):
            return jsonify({"error": "Invalid 'length'. Must be between 1 and 100."}), 400
        if specials not in (0, 1):
            return jsonify({"error": "Invalid 'specials'. Must be 0 or 1."}), 400
        if digits not in (0, 1):
            return jsonify({"error": "Invalid 'digits'. Must be 0 or 1."}), 400

        result = generate_random_string(length, specials == 1, digits == 1)
        return jsonify({"random_string": result})
    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
