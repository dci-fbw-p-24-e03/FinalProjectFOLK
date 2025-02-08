import os
from dotenv import load_dotenv
from groq import Groq
import json

load_dotenv()

def main():
    question = get_question("history", 
                            ["Who was the first president of the United States?", 
                             'The ancient city of Pompeii was destroyed by the eruption of which volcano in 79 AD?',
                             'The Rosetta Stone, which helped decipher ancient Egyptian hieroglyphs, was discovered in which year?']
                            )
    print(question)


def get_question(topic: str, not_questions: list[str]) -> dict:
    """Get Trivial Pursuit Question and answers.

    Args:
        topic (str): Topic of the question.
        not_questions (list[str]): List of questions that should not be asked.

    Returns:
        dict: Dictionary with the question and possible answers as well as the correct answer.
        {'question': ..., 
        'A': ..., 
        'B': ..., 
        'C': ..., 
        'D': ..., 
        'correct_answer': ...}
        """
        
    # Create a string with all the questions that should not be asked
    dont_ask = ""
    for not_question in not_questions:
        dont_ask = dont_ask + f"\"{not_question}\", "
    
    # Connect to the Groq API
    client = Groq(api_key=os.getenv("API_KEY"))
    
    # Get the question and answers from the Groq API
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"Let's play Trivial Pursuit. Do not ask: {dont_ask}. Ask a question about {topic}. Give me four possible answers. Give me the correct answer. Present your response in the form of a python dictionary: {{\"question\": \"...\", \"A\": \"....\", \"B\": \"...\", \"C\": \"....\", \"D\": \"...\", \"correct_answer\": \"...\"}} "
            },
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    # Get the answer from the completion as a string
    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content != None:
            answer = answer + chunk.choices[0].delta.content

    # Convert the answer from a string to a dictionary
    answer_dictionary = json.loads(answer)

    # Check if the question is in the list of questions that should not be asked
    if answer_dictionary["question"] in not_questions:
        return get_question(topic, not_questions)
    else:
        return answer_dictionary

if __name__ == "__main__":
    main()
