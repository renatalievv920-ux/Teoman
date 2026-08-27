import os
from http.server import BaseHTTPRequestHandler
import json
from openai import OpenAI


class handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json(200, {"ok": True})

    def do_POST(self):
        try:
            api_key = os.environ.get("OPENAI_API_KEY")

            if not api_key:
                self.send_json(500, {
                    "error": "OPENAI_API_KEY не найден в Vercel"
                })
                return

            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length)

            data = json.loads(raw_body.decode("utf-8"))

            message = data.get("message", "").strip()

            if not message:
                self.send_json(400, {
                    "error": "Сообщение пустое"
                })
                return

            client = OpenAI(api_key=api_key)

            response = client.responses.create(
                model="gpt-5-mini",
                instructions="""
Ты — Зея, личный AI-помощник пользователя.

Общайся на русском языке, дружелюбно и естественно.
Можешь обращаться к пользователю как «бро».
Отвечай понятно и по делу.
Если пользователь просит помощь с кодом — помогай пошагово.
Не говори, что ты Теоман. Твоё имя — Зея.
""",
                input=message
            )

            answer = response.output_text

            self.send_json(200, {
                "reply": answer,
                "response": answer,
                "message": answer
            })

        except Exception as e:
            self.send_json(500, {
                "error": "Ошибка сервера",
                "details": str(e)
            })
