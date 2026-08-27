import os
import json
from http.server import BaseHTTPRequestHandler
from openai import OpenAI


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
            "Access-Control-Allow-Headers",
            "Content-Type"
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS"
        )
        self.end_headers()

        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json(200, {"ok": True})

    def do_POST(self):

        try:
            length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(length)

            data = json.loads(body)

            message = str(
                data.get("message", "")
            ).strip()

            if not message:
                self.send_json(
                    400,
                    {
                        "error":
                        "Сообщение пустое"
                    }
                )
                return

            api_key = os.environ.get(
                "OPENAI_API_KEY"
            )

            if not api_key:
                self.send_json(
                    500,
                    {
                        "error":
                        "OPENAI_API_KEY не настроен в Vercel"
                    }
                )
                return

            client = OpenAI(
                api_key=api_key
            )

            response = client.responses.create(
                model="gpt-5-mini",
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

            print(
                "Ошибка API:",
                repr(e)
            )

            self.send_json(
                500,
                {
                    "error":
                    "Ошибка сервера",
                    "details":
                    str(e)
                }
            )
