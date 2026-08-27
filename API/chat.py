import os
import json
from http.server import BaseHTTPRequestHandler
from openai import OpenAI


def send_json(handler, status, data):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")

    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        send_json(self, 200, {"ok": True})

    def do_GET(self):
        send_json(self, 200, {
            "ok": True,
            "message": "Теоман онлайн 🤖"
        })

    def do_POST(self):
        try:
            api_key = os.environ.get("OPENAI_API_KEY")

            if not api_key:
                send_json(self, 500, {
                    "error": "OPENAI_API_KEY не найден в Vercel"
                })
                return

            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length)

            try:
                data = json.loads(raw_body.decode("utf-8"))
            except Exception:
                send_json(self, 400, {
                    "error": "Неверный JSON"
                })
                return

            message = data.get("message")

            if not message:
                messages = data.get("messages", [])

                if messages:
                    message = messages[-1].get("content", "")

            if not message:
                send_json(self, 400, {
                    "error": "Сообщение пустое"
                })
                return

            client = OpenAI(api_key=api_key)

            response = client.responses.create(
                model="gpt-5-mini",
                instructions="""
Ты — Теоман, личный ИИ-помощник.

Общайся по-русски, дружелюбно и естественно.
Обращайся к пользователю как к бро, когда это уместно.

Можно использовать нецензурные слова, если пользователь сам общается
в таком стиле или прямо просит материться. Не надо вставлять мат в каждое
сообщение — используй его естественно и только когда это подходит ситуации.

Отвечай понятно, без лишней официальности.
Если пользователь просит помощь с кодом — помогай пошагово.
""",
                input=message
            )

            answer = response.output_text

            send_json(self, 200, {
                "reply": answer,
                "response": answer,
                "message": answer
            })

        except Exception as e:
            send_json(self, 500, {
                "error": "Ошибка сервера",
                "details": str(e)
            })
