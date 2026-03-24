import http.server
import socketserver
import json
import subprocess
import os
import webbrowser
from threading import Timer

PORT = 8000

class CodexHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        
        if self.path == '/cast':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            code = data.get('code', '')
            user_inputs = data.get('inputs', '')

            if not code.strip():
                self._send_response({"status": "curse", "message": "Miss! No scroll equipped."})
                return

            temp_file = "temp_incantation.scroll"
            with open(temp_file, 'w') as f:
                f.write(code)

            try:
                #call the actual compiler engine
                result = subprocess.run(
                    ['python', '-m', 'src.main', temp_file],
                    input=user_inputs,
                    capture_output=True,
                    text=True
                )

                if os.path.exists(temp_file):
                    os.remove(temp_file)

                if result.returncode != 0:
                    self._send_response({"status": "curse", "message": result.stderr or result.stdout})
                else:
                    self._send_response({"status": "success", "message": result.stdout})

            except Exception as e:
                self._send_response({"status": "curse", "message": f"Critical Failure: {str(e)}"})
        else:
            # If it's not a POST to /cast, return a 404
            self.send_response(404)
            self.end_headers()

    def _send_response(self, response_dict):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_dict).encode('utf-8'))

def open_browser():
    # Automatically opens your default web browser to the UI
    webbrowser.open_new(f"http://127.0.0.1:{PORT}/index.html")

if __name__ == "__main__":
    if not os.path.exists('index.html'):
        print("💀 Curse: Cannot find index.html in the current directory.")
        exit(1)

    #delay the browser opening for 1 second so the server can start
    Timer(1.25, open_browser).start()

    with socketserver.TCPServer(("", PORT), CodexHandler) as httpd:
        print(f"🔮 The Oracle is listening on port {PORT}...")
        print("Press Ctrl+C to close the Codex.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down the Codex...")