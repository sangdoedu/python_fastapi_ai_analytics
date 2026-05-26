import json
import requests
from groq import Groq

client = Groq(api_key="your_groq_api_key")

# --- Base Tool ---
class Tool:
    name: str
    description: str
    parameters: dict

    def run(self, **kwargs) -> str:
        raise NotImplementedError

    def definition(self):
        return {"type": "function", "function": {"name": self.name, "description": self.description, "parameters": self.parameters}}

# --- Tools ---
class CryptoPriceTool(Tool):
    name = "get_crypto_price"
    description = "Get live crypto price."
    parameters = {"type": "object", "properties": {"coin_id": {"type": "string"}}, "required": ["coin_id"]}

    def run(self, coin_id):
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
                         params={"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"}).json()
        return f"{coin_id}: ${r[coin_id]['usd']:,.2f} (24h: {r[coin_id]['usd_24h_change']:.2f}%)"

class WeatherTool(Tool):
    name = "get_weather"
    description = "Get current weather for a city."
    parameters = {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}

    def run(self, city):
        geo = requests.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": city, "count": 1}).json()["results"][0]
        w = requests.get("https://api.open-meteo.com/v1/forecast",
                         params={"latitude": geo["latitude"], "longitude": geo["longitude"], "current": "temperature_2m,wind_speed_10m"}).json()["current"]
        return f"{city}: {w['temperature_2m']}°C, wind {w['wind_speed_10m']} km/h"

class ExchangeRateTool(Tool):
    name = "get_exchange_rate"
    description = "Get live currency exchange rate."
    parameters = {"type": "object", "properties": {"base": {"type": "string"}, "target": {"type": "string"}}, "required": ["base", "target"]}

    def run(self, base, target):
        rate = requests.get(f"https://open.er-api.com/v6/latest/{base.upper()}").json()["rates"][target.upper()]
        return f"1 {base.upper()} = {rate} {target.upper()}"

# --- Agent ---
class Agent:
    def __init__(self, name, role, tools=[]):
        self.name = name
        self.tools = {t.name: t for t in tools}
        self.messages = [
            {"role": "system", "content": role + "\nAlways call tools for real data. Never guess."}
        ]

    def run(self, prompt):
        print(f"\n🤖 [{self.name}]")
        self.messages.append({"role": "user", "content": prompt})

        while True:
            msg = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=1024,
                tools=[t.definition() for t in self.tools.values()] or None,
                tool_choice="auto" if self.tools else None,
                messages=self.messages
            ).choices[0].message

            if not msg.tool_calls:
                print(f"✅ {msg.content}\n{'='*60}")
                return msg.content

            self.messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": msg.tool_calls})
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                print(f"  🔧 {tc.function.name}({args})")
                result = self.tools[tc.function.name].run(**args)
                print(f"  📡 {result}")
                self.messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

# --- Pipeline ---
btc     = Agent("Crypto Agent",  "You are a crypto data agent.",   [CryptoPriceTool()]).run("Get Bitcoin price.")
weather = Agent("Weather Agent", "You are a weather agent.",        [WeatherTool()]).run("Get weather in Bangkok.")
fx      = Agent("FX Agent",      "You are a currency data agent.", [ExchangeRateTool()]).run("Get USD to THB rate.")

Agent("Analyst", "You are a financial analyst. No tools needed.").run(
    f"Should I buy Bitcoin or keep USD in Bangkok?\nData:\n- {btc}\n- {weather}\n- {fx}"
)