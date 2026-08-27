import os
import json
import urllib.request
import urllib.error

from http.server import BaseHTTPRequestHandler


OPENAI_URL = "https://api.openai.com/v1/responses"


def ask_openai(message, image=None):
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise Exception("OPENAI_API_KEY не найден в Vercel.")


    content = [
        {
            "type": "input_text",
            "text": message
        }
    ]


    # Если пользователь отправил изображение
    if image:
        content.append(
            {
                "type": "input_image",
                "image_url": image
            }
        )


    payload = {
        "model": "gpt-5-mini",

        "instructions": """
Ты — Зея 🤖, личный AI-помощник пользователя.

Отвечай на русском языке, если пользователь пишет по-русски.

Будь дружелюбной, умной и понятной.
Помогай с программированием, учёбой, повседневными задачами,
анализом изображений и другими вопросами.

Не говори, что ты настоящий человек.
Если не знаешь ответ — честно скажи об этом.
""",

        "input": [
            {
                "role": "user",
                "content": content
            }
        ],

        "max_output_tokens": 1000
    }


    data = json.dumps(payload).encode("utf-8")


    request = urllib.request.Request(
        OPENAI_URL,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )


    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8")

        try:
            error_json = json.loads(error_body)
            error_message = error_json.get("error", {}).get(
                "message",
                error_body
            )
        except Exception:
            error_message = error_body

        raise Exception(
            f"OpenAI API ошибка {error.code}: {error_message}"
        )

    except Exception as error:
        raise Exception(
            f"Ошибка соединения с OpenAI: {str(error)}"
        )


    # Responses API возвращает готовый текст в output_text
    answer = result.get("output_text")

    if not answer:
        raise Exception("OpenAI не вернул текстовый ответ.")

    return answer


class handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        response = json.dumps(
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

        self.wfile.write(response)


    def do_OPTIONS(self):
        self.send_response(204)

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


    def do_POST(self):

        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            data = json.loads(
                body.decode("utf-8")
            )


            message = data.get("message", "").strip()
            image = data.get("image")


            if not message and not image:
                self.send_json(
                    400,
                    {
                        "ok": False,
                        "error": "Сообщение пустое."
                    }
                )
                return


            if not message:
                message = "Проанализируй это изображение."


            answer = ask_openai(
                message,
                image
            )


            self.send_json(
                200,
                {
                    "ok": True,
                    "answer": answer
                }
            )


        except json.JSONDecodeError:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Неверный JSON."
                }
            )


        except Exception as error:
            self.send_json(
                500,
                {
                    "ok": False,
                    "error": str(error)
                }
            )
