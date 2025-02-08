import os
from dotenv import load_dotenv
from groq import Groq
import json
from random import shuffle

load_dotenv()


def main():
    # Get a question about the the specified topic excluding the not_questions
    # as well as four possible answers shuffled randomly and the correct answer in a single dictionary.
    question = get_question(
        topic="python programming language",
        not_questions=[
            "What is the print function in Python used for?",
            "What is the purpose of the __new__ method in Python classes?",
        ],
        difficulty="normal",
    )
    print(question)


def get_question(
    topic: str = "anything", not_questions: list[str] = [], difficulty: str = "normal"
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
    content += f"Do not ask any of these questions: {dont_ask}.\n"
    content += "Give me four possible answers A, B, C and D. Give me the correct answer."
    content += "Present your response in the form of a python dictionary:"
    content += '{"question": "...", "A": "....", "B": "...", "C": "....", "D": "...", "correct_answer": "..."}'

    # Connect to the Groq API
    client = Groq(api_key=os.getenv("API_KEY"))

    # Get the question and answers from the Groq API
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"{content}",
            },
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
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

    # Shuffle the answers randomly
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
    mapping_answers = dict(zip(["A", "B", "C", "D"], answers))

    # Get the correct answer and map it to the shuffled answers
    correct_answer = question["correct_answer"]
    correct_answer = mapping_answers[correct_answer]

    # Create a new dictionary with the shuffled answers
    shuffled_dict = {
        "question": question["question"],
        "A": question[mapping_answers["A"]],
        "B": question[mapping_answers["B"]],
        "C": question[mapping_answers["C"]],
        "D": question[mapping_answers["D"]],
        "correct_answer": correct_answer,
    }

    return shuffled_dict


if __name__ == "__main__":
    main()
