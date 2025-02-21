import os
from dotenv import load_dotenv
from groq import Groq
import json
from random import shuffle


def main():
    pass


def get_question(
    topic: str = "anything",
    not_questions: list[str] = [],
    difficulty: str = "normal",
) -> dict[str, str]:
    """Get Trivial Pursuit Question and answers.

    Args:
        topic (str): Topic of the question.
        not_questions (list[str]): List of questions that should not be asked.
        difficulty (str): Difficulty of the question. Options are "simple", "normal" and "difficult".

    Returns:
        dict: Dictionary with the question and possible answers as well as the correct answer.\n
        {'question': ..., \n
        'A': ...,\n
        'B': ...,\n
        'C': ...,\n
        'D': ...,\n
        'correct_answer': '...'}
    """

    # Create a string of all the questions that should not be asked
    dont_ask = ", ".join(not_questions)

    # Create a string with the content of the message to the Groq API
    content = "Let's play Trivial Pursuit. There are simple, normal and difficult questions.\n"
    content += f"Ask a {difficulty} question about {topic}.\n"
    #content += "The maximum number of characters of the question is 100."
    content += f"Do not ask any of these questions or similar questions: {dont_ask}.\n"
    content += "Give me four possible answers A, B, C and D. Give me the correct answer."
    #content += "The answers should not be longer than 20 characters."
    content += "Present your response in the form of a python dictionary:"
    content += '{"question": "...", "A": "....", "B": "...", "C": "....", "D": "...", "correct_answer": "..."}'

    # Get Api key from .env file  and connect to the Groq API
    load_dotenv()
    client = Groq(api_key=os.getenv("API_KEY"))

    # Get the question and answers from the Groq API
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": content,
            },
        ],
        temperature=2,
        max_completion_tokens=1024,
        top_p=0.1,
        stream=True,
        stop=None,
    )

    # Turn the answer from the completion into a single string
    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content != None:
            answer += chunk.choices[0].delta.content

    # Convert the answer from a string to a dictionary
    answer_dictionary = json.loads(answer)
    print("answer_dictionary: ", answer_dictionary)

    if answer_dictionary["question"] != 'None':
        answer_dictionary = shuffle_answers(answer_dictionary)

    # Check whether the question is in the list of questions that should not be asked
    if answer_dictionary["question"] in not_questions:
        return get_question(topic, not_questions)
    else:
        return answer_dictionary


def shuffle_answers(question: dict[str, str]) -> dict[str, str]:
    """Shuffle the answers of a question.

    Args:
        question (dict[str, str]): dict: Dictionary with the question and possible answers as well as the correct answer.\n
        {'question': ..., \n
        'A': ...,\n
        'B': ...,\n
        'C': ...,\n
        'D': ...,\n
        'correct_answer': '...'}

    Returns:
        dict[str, str]: The same dictionary as the input but with the answers A, B, C, D randomly shuffled.
    """

    # Shuffle the answers randomly. Shuffle directly modifies the answers list.
    answers = ["A", "B", "C", "D"]
    shuffle(answers)

    # map the shuffled answers to the original answers. Turn the zipped iterable into a dictionary.
    mapping_answers = dict(zip(answers, ["A", "B", "C", "D"]))

    # Get the correct answer and map it to the shuffled answers
    correct_answer = question["correct_answer"]
    correct_answer = mapping_answers[correct_answer]
    # Create a new dictionary with the shuffled answers
    shuffled_dict = {
        "question": question["question"],
        "A": question[answers[0]],
        "B": question[answers[1]],
        "C": question[answers[2]],
        "D": question[answers[3]],
        "correct_answer": correct_answer,
    }

    return shuffled_dict

def get_explanations(wrong_questions: list[dict[str, str]]) -> dict[str, str]:
    """
    Given a list of dictionaries with keys "question" and "correct_answer",
    queries the Groq API to return a JSON dictionary mapping each question to a short explanation.
    If the API returns an empty response or decoding fails, returns an empty dictionary.
    """
    # Safety: If there are no wrong questions, return empty dict immediately.
    if not wrong_questions:
        print("No wrong questions provided; returning empty explanations.")
        return {}

    # Build the prompt for the API
    prompt = (
        "For the following questions and their correct answers, provide a short explanation "
        "of why the correct answer is correct.\n\n"
    )
    for item in wrong_questions:
        prompt += f"Question: {item['question']}\nCorrect Answer: {item['correct_answer']}\n\n"
    prompt += "Return your response as a JSON dictionary where the keys are the questions and the values are the explanations."

    # Load the API key and initialize the Groq client
    load_dotenv()
    client = Groq(api_key=os.getenv("API_KEY"))

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=2,
            max_completion_tokens=1024,
            top_p=0.1,
            stream=True,
            stop=None,
        )
    except Exception as e:
        print("Error during API call:", e)
        return {}

    # Assemble the streamed output into a single string
    answer = ""
    try:
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                answer += chunk.choices[0].delta.content
    except Exception as e:
        print("Error during streaming the response:", e)
        return {}

    # Check if the answer is empty or only whitespace
    # Check if the answer is empty or only whitespace
    if not answer.strip():
        print("Empty answer received from API.")
        return {item["question"]: "No explanation available." for item in wrong_questions}

    # Remove markdown code fences if present
    if answer.strip().startswith("```json"):
        lines = answer.strip().splitlines()
        answer = "\n".join(lines[1:-1])  # Remove the first and last lines

    # Attempt to decode the JSON response.
    try:
        result = json.loads(answer)
        if not isinstance(result, dict):
            raise ValueError("Result is not a dictionary")
        return result
    except Exception as e:
        print("Error decoding JSON:", e, "Raw answer:", answer)
        return {item["question"]: "No explanation available." for item in wrong_questions}

    # Attempt to decode the JSON response
    try:
        result = json.loads(answer)
        return result
    except json.JSONDecodeError as e:
        print("JSON decode error:", e, "Raw answer:", answer)
        return {}




if __name__ == "__main__":
    main()
