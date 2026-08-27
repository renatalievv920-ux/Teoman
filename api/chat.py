import os
import json
import urllib.request
import urllib.error

from http.server import BaseHTTPRequestHandler


OPENAI_URL = "https://api.openai.com/v1/chat/completions"

MODEL = "gpt-5.6"


def ask_openai(message, image=None):

    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise Exception(
            "OPENAI_API_KEY не найден в настройках Vercel."
        )


    # -----------------------------
    # ТОЛЬКО ТЕКСТ
    # -----------------------------

    if not image:

        messages = [
            {
                "role": "system",
                "content": (
                    "Ты — Зея, личный AI-помощник. "
                    "Твоё имя только Зея. "
                    "Никогда не называй себя Теоманом. "
                    "Отвечай понятно, дружелюбно и по делу."
                )
            },
            {
                "role": "user",
                "content": message
            }
        ]


    # -----------------------------
    # ТЕКСТ + ФОТО
    # -----------------------------

    else:

        messages = [
            {
                "role": "system",
                "content": (
                    "Ты — Зея, личный AI-помощник. "
                    "Твоё имя только Зея. "
                    "Никогда не называй себя Теоманом. "
                    "Ты умеешь анализировать фотографии. "
                    "Опиши пользователю, что изображено на фотографии, "
                    "и отвечай на его вопрос по изображению."
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image
                        }
                    }
                ]
            }
        ]


    payload = {
        "model": MODEL,
        "messages": messages
    }


    data = json.dumps(
        payload,
        ensure_ascii=False
    ).encode("utf-8")


    request = urllib.request.Request(
        OPENAI_URL,
        data=data,
        method="POST"
    )


    request.add_header(
        "Authorization",
        "Bearer " + api_key
    )

    request.add_header(
        "Content-Type",
        "application/json"
    )


    try:

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

            result = json.loads(raw)


    except urllib.error.HTTPError as e:

        error_body = e.read().decode(
            "utf-8",
            errors="replace"
        )

        raise Exception(
            "OpenAI API " +
            str(e.code) +
            ": " +
            error_body
        )


    except Exception as e:

        raise Exception(
            "Ошибка подключения к OpenAI: " +
            str(e)
        )


    # -----------------------------
    # ПОЛУЧАЕМ ТЕКСТ
    # -----------------------------

    try:

        answer = (
            result
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content")
        )

    except Exception:

        answer = None


    if isinstance(answer, list):

        parts = []

        for item in answer:

            if isinstance(item, dict):

                text = item.get("text")

                if text:
                    parts.append(
                        str(text)
                    )

        answer = "\n".join(parts)


    if not answer:

        raise Exception(
            "OpenAI не вернул текстовый ответ. "
            "Ответ API: " +
            json.dumps(
                result,
                ensure_ascii=False
            )
        )


    return str(answer).strip()



class handler(BaseHTTPRequestHandler):


    # =====================================
    # CORS
    # =====================================

    def send_cors(self):

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


    # =====================================
    # JSON RESPONSE
    # =====================================

    def send_json(
        self,
        status,
        data
    ):

        body = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")


        self.send_response(status)


        self.send_cors()


        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )


        self.send_header(
            "Content-Length",
            str(len(body))
        )


        self.end_headers()


        self.wfile.write(body)


    # =====================================
    # OPTIONS
    # =====================================

    def do_OPTIONS(self):

        self.send_json(
            200,
            {
                "ok": True
            }
        )


    # =====================================
    # GET
    # =====================================

    def do_GET(self):

        self.send_json(
            200,
            {
                "ok": True,
                "message": "Зея API работает 🤖"
            }
        )


    # =====================================
    # POST
    # =====================================

    def do_POST(self):

        try:

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )


            if content_length <= 0:

                self.send_json(
                    400,
                    {
                        "ok": False,
                        "error": "Пустой запрос."
                    }
                )

                return


            body = self.rfile.read(
                content_length
            )


            data = json.loads(
                body.decode("utf-8")
            )


            message = str(
                data.get(
                    "message",
                    ""
                )
            ).strip()


            image = data.get(
                "image"
            )


            # -----------------------------
            # ПРОВЕРКА
            # -----------------------------

            if not message:

                message = (
                    "Проанализируй изображение."
                    if image
                    else ""
                )


            if not message and not image:

                self.send_json(
                    400,
                    {
                        "ok": False,
                        "error": "Сообщение пустое."
                    }
                )

                return


            # -----------------------------
            # ПРОВЕРКА ФОТО
            # -----------------------------

            if image:

                if not isinstance(
                    image,
                    str
                ):

                    self.send_json(
                        400,
                        {
                            "ok": False,
                            "error":
                                "Неверный формат изображения."
                        }
                    )

                    return


                if not image.startswith(
                    "data:image/"
                ):

                    self.send_json(
                        400,
                        {
                            "ok": False,
                            "error":
                                "Изображение должно быть Base64 data URL."
                        }
                    )

                    return


            # -----------------------------
            # OPENAI
            # -----------------------------

            answer = ask_openai(
                message,
                image
            )


            # -----------------------------
            # УСПЕХ
            # -----------------------------

            self.send_json(
                200,
                {
                    "ok": True,
                    "reply": answer,
                    "response": answer,
                    "message": answer
                }
            )


        except json.JSONDecodeError:

            self.send_json(
                400,
                {
                    "ok": False,
                    "error":
                        "Сервер получил неправильный JSON."
                }
            )


        except Exception as e:

            self.send_json(
                500,
                {
                    "ok": False,
                    "error": str(e)
                }
            )
