import json
import resend
import requests
from groq import Groq

client = Groq(api_key="xxx")    #groq.com
resend.api_key = "xxx"      #resend.com
NEWSDATA_API_KEY = "xxx"    #newsdata.io

# --- Plain functions (not tools) ---
def search_news(query: str) -> str:
    res = requests.get("https://newsdata.io/api/1/news",
                       params={"apikey": NEWSDATA_API_KEY, "q": query, "language": "en"}).json()
    articles = res.get("results", [])[:3]
    return "\n".join([f"- {a['title']}: {(a.get('description') or '')[:100]}" for a in articles])

def get_gold_price() -> str:
    # metals-api free alternative via gold-api.com
    res = requests.get("https://www.goldapi.io/api/XAU/USD",
                       headers={"x-access-token": "goldapi-demo"}).json()
    price = res.get("price")
    if price:
        return f"Gold spot price: ${price:.2f} USD/oz"
    
    # fallback: use a hardcoded recent price if API fails
    return "Gold spot price: ~$3,300 USD/oz (approximate, live API unavailable)"

def send_email(to: str, subject: str, body: str) -> str:
    resend.Emails.send({"from": "onboarding@resend.dev", "to": [to], "subject": subject, "html": body})
    return f"Email sent to {to}"

# --- Only send_email is a tool ---
TOOL_DEFS = [
    {"type": "function", "function": {
        "name": "send_email",
        "description": "Send an email to a recipient.",
        "parameters": {
            "type": "object",
            "properties": {
                "to":      {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string", "description": "Email subject line"},
                "body":    {"type": "string", "description": "Email body in HTML format"}
            },
            "required": ["to", "subject", "body"]
        }
    }},
]

def chat(system: str, prompt: str, use_tools: bool = False) -> str:
    print(f"\n🤖 {system.split('.')[0]}")
    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": prompt}
    ]
    while True:
        kwargs = dict(
            model="openai/gpt-oss-120b",
            max_tokens=1024,
            messages=messages
        )
        if use_tools:
            kwargs["tools"] = TOOL_DEFS
            kwargs["tool_choice"] = "auto"
            kwargs["parallel_tool_calls"] = False

        msg = client.chat.completions.create(**kwargs).choices[0].message

        if not msg.tool_calls:
            print(f"✅ {msg.content[:200]}...")
            return msg.content[:500]

        messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": msg.tool_calls})
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            print(f"  🔧 {tc.function.name}({args})")
            result = send_email(**args)
            print(f"  📡 {result}")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

# --- Fetch data ONCE ---
print("📡 Fetching data...")
news      = search_news("gold market news today")
goldprice = get_gold_price()
print(f"  News: {news[:100]}...")
print(f"  Price: {goldprice}")

# --- Agents: pure reasoning, no tools ---
summary    = chat("You are a summarizer. Summarize into 3 bullet points.",
                  f"Summarize:\n{news}")

trend      = chat("You are a market analyst. Analyze the market trend.",
                  f"Gold price: {goldprice}\nNews:\n{news}\n\nAnalyze the trend.")

prediction = chat("You are a financial forecaster. Give a brief prediction.",
                  f"Gold price: {goldprice}\nTrend:\n{trend[:300]}\n\nPredict next month in 100 words.")

# --- Email agent: only one that needs a tool ---
chat("You are an email agent. Send a market report by email.",
     f"Send email to your_email_in_resend@gmail.com subject 'Gold Market Report'.\n"
     f"News: {summary[:300]}\nTrend: {trend[:300]}\nPrediction: {prediction[:300]}",
     use_tools=True)

print("\n🏁 Done!")