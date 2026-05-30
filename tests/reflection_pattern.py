from groq import Groq
client = Groq(api_key="xxx")

def call_llm(system: str, prompt: str) -> str:
   response = client.chat.completions.create(
       model="llama-3.3-70b-versatile", max_tokens=2048,
       messages=[
           {"role": "system", "content": system},
           {"role": "user", "content": prompt}
       ]
   )
   return response.choices[0].message.content
task = "Write a Python function that finds the second largest number in a list."


draft = call_llm(		#call API to finish first task
   system="You are a junior developer writing quickly. Skip edge cases, error handling, and docstrings.",
   prompt=task
)
print("FIRST RESULT:\n", draft)

improved = call_llm(	#evaluate the code and improve it based on the task, asking to consider edge cases and add docstrings
   system="You are a senior Python engineer. Review the code, list its problems, then rewrite it properly with edge cases and docstrings.",
   prompt=f'Task: "{task}"\n\nCode to review:\n{draft}'
)
print("=== AFTER REFLECTION:\n", improved)
