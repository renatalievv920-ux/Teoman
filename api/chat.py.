import os
import json
from http.server import BaseHTTPRequestHandler
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


class handler(BaseHTTPRequestHandler):

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
                    json.dumps({
                        "error": "Пустое сообщение"
                    }).encode()
                )

                return

            response = client.responses.create(
                model="gpt-5-mini",
                instructions=(
                    "Тебя зовут Теоман. "
                    "Ты дружелюбный личный ИИ-помощник. "
                    "Отвечай на русском языке, "
                    "естественно и понятно."
                ),
                input=message
            )

            answer = response.output_text

            result = {
                "answer": answer
            }

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps(
                    result,
                    ensure_ascii=False
                ).encode("utf-8")
            )

        except Exception as e:

            self.send_response(500)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps({
                    "error": str(e)
                }).encode()
            )
