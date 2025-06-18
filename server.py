import requests
import openai
from flask import Flask, request, jsonify

GOOGLE_SHEET_WEBHOOK = "https://script.google.com/macros/s/AKfycbzOCJq7Qy1gSxUvxJDzB5XWutGL09d8q_96QagIIwGc_GOxYprE323ZRqDga6NrmZ7j/exec"
OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

def get_products_from_sheets(query):
    try:
        params = {"query": query}
        response = requests.get(GOOGLE_SHEET_WEBHOOK, params=params, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
        else:
            print("Ошибка Google Sheets:", response.status_code, response.text)
            return ""
    except Exception as e:
        print("Ошибка при обращении к Google Sheets:", e)
        return ""

def ask_gpt(user_message, products):
    prompt = (
        "Ниже приведён разговор с помощником ИИ, использующим WhatsApp. "
        "Помощник услужливый, умный, дружелюбный и всегда старается помочь клиенту подобрать подходящий товар. Наш адрес: Акан-Серы 31А. Работаем с 11 до 19.\n\n"
        "Вот список всех товаров магазина:\n"
        f"{products}\n\n"
        "Если клиент спрашивает о товаре, ищи не только точные совпадения, но и похожие по смыслу. "
        "Если не нашёл точного совпадения — предложи похожие товары. "
        "Если не понял запрос — уточни у клиента. "
        "В ответе используй дружелюбный и профессиональный стиль.\n\n"
        f"Вопрос клиента: {user_message}\n2::"
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI error:", e)
        return "Ошибка при обращении к ИИ. Попробуйте позже."

@app.route("/", methods=["POST"])
def autoresponder_webhook():
    data = request.json
    user_message = data.get("message", "")
    products = get_products_from_sheets(user_message)
    answer = ask_gpt(user_message, products)
    # Возвращаем массив ответов (можно один)
    return jsonify({"replies": [answer]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
