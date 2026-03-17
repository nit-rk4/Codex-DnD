# app.py
from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os

app = Flask(__name__)

# Serve the Retro D&D Frontend
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# The API endpoint that connects to your compiler
@app.route('/cast', methods=['POST'])
def cast_spell():
    data = request.json
    code = data.get('code', '')
    user_inputs = data.get('inputs', '') # Catch the inputs from the web

    if not code:
        return jsonify({"status": "curse", "message": "Miss! No scroll equipped."})

    temp_file = "temp_incantation.scroll"
    with open(temp_file, 'w') as f:
        f.write(code)

    try:
        # We pass the `input=user_inputs` argument here!
        # This acts exactly like someone typing the answers and pressing Enter.
        result = subprocess.run(
            ['python', '-m', 'src.main', temp_file],
            input=user_inputs, 
            capture_output=True,
            text=True
        )

        if os.path.exists(temp_file):
            os.remove(temp_file)

        if result.returncode != 0:
            return jsonify({"status": "curse", "message": result.stderr or result.stdout})
        else:
            return jsonify({"status": "success", "message": result.stdout})

    except Exception as e:
        return jsonify({"status": "curse", "message": f"Server Error: {str(e)}"})

if __name__ == '__main__':
    print("🔮 The Oracle is listening on http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)