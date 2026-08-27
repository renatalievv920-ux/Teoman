import os
import json
import base64
from http.server import BaseHTTPRequestHandler
from openai import OpenAI


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

            api_key = os.environ.get(
                "OPENAI_API_KEY"
            )

            if not api_key:

                self.send_json(
                    500,
                    {
                        "error":
                        "OPENAI_API_KEY не найден."
                    }
                )

                return


            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )


            raw_body = self.rfile.read(
                content_length
            )


            data = json.loads(
                raw_body.decode("utf-8")
            )


            message = (
                data.get(
                    "message",
                    ""
                )
                .strip()
            )


            image = data.get(
                "image"
            )


            if not message:

                self.send_json(
                    400,
                    {
                        "error":
                        "Сообщение пустое."
                    }
                )

                return


            client = OpenAI(
                api_key=api_key
            )


            # =========================
            # ОБЫЧНЫЙ ЧАТ
            # =========================

            if not image:

                response = client.responses.create(

                    model="gpt-5-mini",

                    instructions="""
Ты — Зея, личный AI-помощник.

Твоё имя — Зея.
Не называй себя Теоманом.

Общайся дружелюбно, естественно
и по возможности коротко.

Пользователь может обращаться
к тебе «бро».

Отвечай на языке пользователя.
Если пользователь пишет по-русски —
отвечай по-русски.

Ты можешь помогать с кодом,
идеями, переводами, планированием
и обычными вопросами.
""",

                    input=message
                )


                answer = (
                    response.output_text
                    or "Я не смогла ответить."
                )


            # =========================
            # АНАЛИЗ ФОТО
            # =========================

            else:

                # Проверяем, что это
                # действительно Data URL

                if "," not in image:

                    self.send_json(
                        400,
                        {
                            "error":
                            "Неверный формат изображения."
                        }
                    )

                    return


                image_url = image


                response = client.responses.create(

                    model="gpt-5-mini",

                    instructions="""
Ты — Зея.

Пользователь отправил тебе
фотографию.

Внимательно проанализируй
изображение и ответь на русском языке.

Опиши:
- что находится на фото;
- людей и предметы, если они есть;
- текст, который можно прочитать;
- важные детали;
- что происходит на изображении.

Не выдумывай детали, которых
невозможно увидеть.
""",

                    input=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": message
                                },
                                {
                                    "type": "input_image",
                                    "image_url": image_url
                                }
                            ]
                        }
                    ]
                )


                answer = (
                    response.output_text
                    or "Я не смогла описать это фото."
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
                    "error":
                    "Ошибка API Зеи.",
                    "details":
                    str(e)
                }
            )
