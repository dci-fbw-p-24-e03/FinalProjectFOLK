import os
from dotenv import load_dotenv
from groq import Groq
import json

load_dotenv()

client = Groq(api_key=os.getenv("API_KEY"))
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": "Let's play Trivial Pursuit. Ask a question about history. Give me four possible answers. Give me the correct answer. Present your response in the form of a python dictionary: {\"question\": \"...\", \"A\": \"....\", \"B\": \"...\", \"C\": \"....\", \"D\": \"...\", \"correct_answer\": \"...\"} "
        },
    ],
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=True,
    stop=None,
)

answer = ""
for chunk in completion:
    if chunk.choices[0].delta.content != None:
        answer = answer + chunk.choices[0].delta.content

answer_dictionary = json.loads(answer)

print(answer_dictionary)



