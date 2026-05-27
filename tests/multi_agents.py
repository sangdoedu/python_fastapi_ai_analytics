def get_crypto_price(coin_id):
    r = requests.get("https://api.coingecko.com/api/v3/simple/price",
                     params={"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"}).json()
    return f"{coin_id}: ${r[coin_id]['usd']:,.2f} (24h: {r[coin_id]['usd_24h_change']:.2f}%)"
def get_weather(city):
    geo = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                       params={"name": city, "count": 1}).json()["results"][0]
    w = requests.get("https://api.open-meteo.com/v1/forecast",
                     params={"latitude": geo["latitude"], "longitude": geo["longitude"],
                             "current": "temperature_2m,wind_speed_10m"}).json()["current"]
    return f"{city}: {w['temperature_2m']}°C, wind {w['wind_speed_10m']} km/h"
def get_exchange_rate(base, target):
    rate = requests.get(f"https://open.er-api.com/v6/latest/{base.upper()}").json()["rates"][target.upper()]
    return f"1 {base.upper()} = {rate} {target.upper()}"

TOOLS = {"get_crypto_price": get_crypto_price, "get_weather": get_weather, "get_exchange_rate": get_exchange_rate}
TOOL_DEFS = [
    {"type": "function", "function": {"name": "get_crypto_price", "description": "Get live crypto price.",
     "parameters": {"type": "object", "properties": {"coin_id": {"type": "string"}}, "required": ["coin_id"]}}},
    {"type": "function", "function": {"name": "get_weather", "description": "Get current weather for a city.",
     "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
    {"type": "function", "function": {"name": "get_exchange_rate", "description": "Get live currency exchange rate.",
     "parameters": {"type": "object", "properties": {"base": {"type": "string"}, "target": {"type": "string"}}, "required": ["base", "target"]}}},
]

import json
import requests
from groq import Groq

client = Groq(api_key="xxx")

def chat(messages):
    while True:
        msg = client.chat.completions.create(
            model="llama-3.3-70b-versatile", max_tokens=1024,
            tools=TOOL_DEFS,
            tool_choice="auto",
            parallel_tool_calls=False,
            messages=messages
        ).choices[0].message
        if not msg.tool_calls:
            return msg.content
        print(f"Assistant: {msg.tool_calls}")
        messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": msg.tool_calls})
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            result = TOOLS[tc.function.name](**args)
            print(f"{tc.function.name}({args}) → {result}")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

# --- Single agent, any question ---
user_question = input("Ask anything: ")

answer = chat([
    {"role": "system", "content": "You are a helpful assistant with access to live crypto, weather, and currency tools. Use them whenever needed to answer the user's question."},
    {"role": "user",   "content": user_question}
])

print("\nFinal answer:", answer)