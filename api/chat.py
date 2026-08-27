import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            data = json.loads(body)
            message = data.get("message", "").strip()

            if not message:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()

                self.wfile.write(
                    json.dumps(
                        {"error": "Сообщение пустое"},
                        ensure_ascii=False
                    ).encode()
                )
                return

            response = client.responses.create(
                model="gpt-5-mini",
                input=message
            )

            answer = response.output_text

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(
                json.dumps(
                    {"reply": answer},
                    ensure_ascii=False
                ).encode()
            )

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(
                json.dumps(
                    {"error": str(e)},
                    ensure_ascii=False
                ).encode()
            )


port = int(os.environ.get("PORT", 8000))

server = HTTPServer(("0.0.0.0", port), Handler)

print(f"Сервер запущен на порту {port}")

server.serve_forever()
