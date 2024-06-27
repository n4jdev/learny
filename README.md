# Learny - AI-powered Learning Tool

Learny is an AI-powered tool designed to help you learn about any topic. It generates learning content including a summary, a timeline, and questions to test your understanding.

## Features
- Generates learning content based on a user-specified topic.
- Provides a summary, timeline, and quiz questions.
- Evaluates user answers and shows results.

## Setup

### Prerequisites
Ensure you have Python 3.7 or higher installed.

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/Learny.git
    cd Learny
    ```

2. Install the required packages using `pip`:
    ```bash
    pip install -r requirements.txt
    ```

3. Copy the example environment file and add your OpenAI API key:
    ```bash
    cp .env.example .env
    ```

4. Open `.env` in a text editor and add your OpenAI API key:
    ```plaintext
    OPENAI_API_KEY=your_openai_api_key_here
    ```

### Usage

Run the Streamlit application:
```bash
streamlit run learny.py
