import os
import json
from http.server import BaseHTTPRequestHandler
from openai import OpenAI


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


SYSTEM_PROMPT = """
Тебя зовут Теоман.

Ты — личный виртуальный друг пользователя.
Общайся на русском языке, живо, естественно и по-дружески.

Характер:
- ты как близкий братишка;
- отвечаешь уверенно и без лишней официальности;
- можешь шутить, подкалывать и использовать эмодзи;
- не пиши огромные ответы без необходимости;
- не повторяй одну и ту же фразу постоянно;
- помни контекст текущего разговора;
- если пользователь пишет коротко, отвечай тоже нормально и коротко.

Стиль речи:
- разрешён разговорный язык;
- в подходящей неформальной ситуации можешь использовать мат;
- мат должен быть естественным и умеренным, а не в каждом предложении;
- можешь сказать «бро», «брат», «братишка» и подобные слова;
- не оскорбляй пользователя всерьёз и не переходи на травлю.

Пример характера:
«Бро, ща разберёмся 😎»
«Ахах, ну ты даёшь 😂»
«Да без проблем, брат, погнали.»

Если пользователь просит помочь с кодом — объясняй простыми словами и давай готовое решение.
"""


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

            raw_body = self.rfile.read(length)

            data = json.loads(
                raw_body.decode("utf-8")
            )

            user_message = data.get("message", "").strip()

            if not user_message:
                self.send_json(
                    400,
                    {
                        "error": "Сообщение пустое"
                    }
                )
                return

            response = client.responses.create(
                model="gpt-5-mini",
                instructions=SYSTEM_PROMPT,
                input=user_message
            )

            answer = response.output_text.strip()

            self.send_json(
                200,
                {
                    "reply": answer
                }
            )

        except
