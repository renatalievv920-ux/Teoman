import os
import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler


OPENAI_URL = "https://api.openai.com/v1/responses"


def openai_request(message, image=None):
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise Exception("OPENAI_API_KEY не найден в Vercel.")

    if image:
        content = [
            {
                "type": "input_text",
                "text": message
            },
            {
                "type": "input_image",
                "image_url": image
            }
        ]

        payload = {
            "model": "gpt-5-mini",
            "instructions": (
                "Ты — Зея, личный AI-помощник. "
                "Тебя зовут Зея. "
                "Не называй себя Теоманом. "
                "Отвечай естественно и дружелюбно. "
                "Отвечай на языке пользователя. "
                "Если пользователь пишет по-русски — отвечай по-русски."
            ),
            "input": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }

    else:
        payload = {
            "model": "gpt-5-mini",
            "instructions": (
                "Ты — Зея, личный AI-помощник. "
                "Тебя зовут Зея. "
                "Никогда не называй себя Теоманом. "
                "Общайся дружелюбно, естественно и коротко. "
                "Пользователь может обращаться к тебе «бро». "
                "Отвечай на языке пользователя."
            ),
            "input": message
        }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OPENAI_URL,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key
        }
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")

        try:
            error_json = json.loads(error_body)
            error_message = (
                error_json.get("error", {}).get("message")
                or error_body
            )
        except Exception:
            error_message = error_body

        raise Exception(error_message)

    output_text = result.get("output_text")

    if output_text:
        return output_text

    # Запасной вариант, если output_text отсутствует
    for item in result.get("output", []):
        for content_item in item.get("content", []):
            if content_item.get("type") == "output_text":
                return content_item.get("text", "")

    return "Я не смогла получить ответ."


class handler(BaseHTTPRequestHandler):

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

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json(
            200,
            {"ok": True}
        )

    def do_GET(self):
        self.send_json(
            200,
            {
                "ok": True,
                "message": "Зея API работает 🤖"
            }
        )

    def do_POST(self):

        try:
            content_length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            body = self.rfile.read(
                content_length
            )

            data = json.loads(
                body.decode("utf-8")
            )

            message = str(
                data.get("message", "")
            ).strip()

            image = data.get("image")

            if not message:
                self.send_json(
                    400,
                    {
                        "error": "Сообщение пустое."
                    }
                )
                return

            answer = openai_request(
                message,
                image
            )

            self.send_json(
                200,
                {
                    "reply": answer,
                    "response": answer,
                    "message": answer
                }
            )

        except Exception as e:

            self.send_json(
                500,
                {
                    "error": "Ошибка API Зеи.",
                    "details": str(e)
                }
            )
