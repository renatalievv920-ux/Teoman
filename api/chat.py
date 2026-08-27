import os
import json
from http.server import BaseHTTPRequestHandler
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


class Handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS"
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )
        self.end_headers()

        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json(200, {"ok": True})

    def do_POST(self):

        try:
            length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(length)

            data = json.loads(body.decode("utf-8"))

            message = data.get("message", "").strip()

            if not message:
                self.send_json(
                    400,
                    {
                        "error": "Сообщение пустое"
                    }
                )
                return

            response = client.responses.create(
                model="gpt-5-mini",
                instructions=(
                    "Тебя зовут Теоман. "
                    "Ты дружелюбный личный ИИ-помощник. "
                    "Отвечай на русском языке. "
                    "Обращайся к пользователю дружелюбно. "
                    "Отвечай понятно и не слишком длинно."
                ),
                input=message
            )

            answer = response.output_text

            self.send_json(
                200,
                {
                    "reply": answer
                }
            )

        except Exception as e:

            self.send_json(
                500,
                {
                    "error": str(e)
                }
            )


if __name__ == "__main__":

    from http.server import HTTPServer

    port = int(
        os.environ.get("PORT", 8000)
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        Handler
    )

    print(
        f"Теоман запущен на порту {port}"
    )

    server.serve_forever()
