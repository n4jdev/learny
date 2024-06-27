import os
import json
import re
from openai import OpenAI
import streamlit as st
from streamlit_timeline import timeline
from difflib import SequenceMatcher

# Initialize OpenAI client with API key
client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Function to generate learning content
def generate_learning_content(topic: str):
    prompt = f"""
    You are an AI assistant, and your task is to generate learning content based on a given topic. The response must be a well-structured JSON object and must contain no other text or commentary outside the JSON format.

    The JSON format should include:
    - title: The title of the content.
    - summary: A long summary of the topic, not the quiz.
    - questions: A list of 10 questions, where each question is an object containing:
      - question: The question text.
      - type: The type of question, either "multiple-choice", "checkbox", "dropdown", "true-false", or "short-answer".
      - options: The options for multiple-choice; checkbox, or dropdown questions (if applicable).
      - correct: The correct answer (or answers for checkbox).
      - explanation: Explanation of the correct answer.

    - timeline: A timeline of major events related to the topic, formatted for TimelineJS.

    Here is an example JSON structure for your reference:

    ```json
    {{
      "title": "Example Learning Title",
      "summary": "This is a brief summary of the learning topic.",
      "questions": [
        {{
          "question": "What is the capital of France?",
          "type": "multiple-choice",
          "options": ["Paris", "London", "Rome", "Berlin"],
          "correct": "Paris",
          "explanation": "Paris is the capital and largest city of France."
        }},
        {{
          "question": "What is 2 + 2?",
          "type": "short-answer",
          "correct": "4",
          "explanation": "2 + 2 equals 4."
        }},
        {{
          "question": "Select all prime numbers.",
          "type": "checkbox",
          "options": ["2", "3", "4", "5"],
          "correct": ["2", "3", "5"],
          "explanation": "2, 3, and 5 are prime numbers."
        }},
        {{
          "question": "Select a fruit.",
          "type": "dropdown",
          "options": ["Apple", "Carrot", "Potato", "Tomato"],
          "correct": "Apple",
          "explanation": "Apple is a type of fruit, while the others are vegetables."
        }},
        {{
          "question": "True or False: The sky is green.",
          "type": "true-false",
          "correct": "False",
          "explanation": "The sky appears blue due to the scattering of sunlight."
        }}
      ],
      "timeline": {{
        "events": [
          {{
            "start_date": {{ "year": "2020" }},
            "text": {{
              "headline": "Example Event 1",
              "text": "Description of example event 1."
            }}
          }},
          {{
            "start_date": {{ "year": "2021" }},
            "text": {{
              "headline": "Example Event 2",
              "text": "Description of example event 2."
            }}
          }}
        ]
      }}
    }}
    ```

    Generate learning content on the following topic, and provide the response only in the JSON format specified above. Ensure the number of questions is 10.

    Topic: {topic}
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]

def normalized_answer(answer):
    """Normalize the answer for case and whitespace differences."""
    return re.sub(r'\s+', ' ', answer).strip().lower()

def is_similar(a, b, threshold=0.85):
    """Check if two answers are similar using a similarity threshold."""
    return SequenceMatcher(None, a, b).ratio() > threshold

def evaluate_quiz(answers, quiz_data):
    total_correct = 0
    results = []

    for i, question in enumerate(quiz_data["questions"]):
        correct = False
        user_answer = answers.get(f'q{i}', '')

        if question["type"] in ["multiple-choice", "dropdown", "true-false"]:
            correct = normalized_answer(user_answer) == normalized_answer(question["correct"])
        elif question["type"] == "short-answer":
            correct = is_similar(normalized_answer(user_answer), normalized_answer(question["correct"]))
        elif question["type"] == "checkbox":
            correct = set(normalized_answer(opt) for opt in user_answer) == set(normalized_answer(opt) for opt in question["correct"])

        total_correct += correct
        results.append({'question': question, 'correct': correct, 'user_answer': user_answer})

    return total_correct, results

# Initialize session_state variables
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None

if 'answers' not in st.session_state:
    st.session_state.answers = {}

if 'completed' not in st.session_state:
    st.session_state.completed = False

if 'current_question' not in st.session_state:
    st.session_state.current_question = 0

# Streamlit UI
st.title("Learny")
st.write("Learny is an AI-powered tool designed to help you learn about any topic.")
st.markdown("---")
st.header("Learn")
learning_topic = st.text_input("What do you want to learn about?")
submit_button = st.button("Submit")

st.markdown("---")
st.header("About this tool")
st.write("Learny is an AI-powered tool designed to help you learn about any topic. Simply enter a topic, and Learny will generate content including a summary, a timeline, and questions to test your understanding.")

if submit_button and learning_topic:
    try:
        with st.spinner('Generating learning content...'):
            learning_json = generate_learning_content(learning_topic)
            st.session_state.quiz_data = json.loads(learning_json)
        # The data is now loaded
        st.session_state.answers = {}
        st.session_state.completed = False
        st.session_state.current_question = 0
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Render Learning Content
if st.session_state.quiz_data:
    quiz_data = st.session_state.quiz_data
    st.header("Summary")
    st.write(quiz_data["summary"])

    # Timeline Section
    st.header("Timeline")
    try:
        timeline_data = quiz_data["timeline"]
        timeline(timeline_data, height=800)
    except KeyError:
        st.write("No timeline data available.")

    st.markdown("---")
    with st.expander(quiz_data["title"], expanded=True):
        answers = st.session_state.answers
        current_question_index = st.session_state.current_question

        if current_question_index < len(quiz_data["questions"]):
            question = quiz_data["questions"][current_question_index]
            st.subheader(f"Question {current_question_index + 1}")

            if question.get("type") == "multiple-choice":
                st.session_state.answers[f'q{current_question_index}'] = st.radio(f"{question['question']}", question.get("options"), key=f'q{current_question_index}')
            elif question.get("type") == "short-answer":
                st.session_state.answers[f'q{current_question_index}'] = st.text_input(f"{question['question']}", key=f'q{current_question_index}')
            elif question.get("type") == "checkbox":
                st.session_state.answers[f'q{current_question_index}'] = st.multiselect(f"{question['question']}", question.get("options"), key=f'q{current_question_index}')
            elif question.get("type") == "dropdown":
                st.session_state.answers[f'q{current_question_index}'] = st.selectbox(f"{question['question']}", question.get("options"), key=f'q{current_question_index}')
            elif question.get("type") == "true-false":
                st.session_state.answers[f'q{current_question_index}'] = st.radio(f"{question['question']}", ["True", "False"], key=f'q{current_question_index}')

            next_button = st.button("Next", key=f'next_{current_question_index}')
            if next_button:
                if (
                    st.session_state.answers.get(f'q{current_question_index}') is not None and
                    (isinstance(st.session_state.answers[f'q{current_question_index}'], list) and len(st.session_state.answers[f'q{current_question_index}']) > 0 or
                     not isinstance(st.session_state.answers[f'q{current_question_index}'], list) and st.session_state.answers[f'q{current_question_index}'] != '')
                ):
                    st.session_state.current_question += 1

        else:
            st.session_state.completed = True

# Display Quiz Results
if st.session_state.completed:
    total_correct, results = evaluate_quiz(st.session_state.answers, st.session_state.quiz_data)

    correct_answers = sum([result['correct'] for result in results])
    st.header(f"{correct_answers}/{len(quiz_data['questions'])}")

    for i, result in enumerate(results):
        st.subheader(f"Question {i + 1}")
        st.markdown(f"{result['question']['question']}")
        if result['correct']:
            st.success(f"{result['user_answer']}")
        else:
            st.error(f"{result['user_answer']}")
            st.info(f"{result['question']['correct']}")
        st.markdown(f"{result['question']['explanation']}")
        st.markdown("---")
