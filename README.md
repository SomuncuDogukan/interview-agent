# AI Interview Agent

This project is an AI-powered interview agent that simulates a job interview.  
It asks predefined questions, listens to the user's answers via voice or text, and generates a final summary in both Markdown and JSON formats.

## Features
- Speech-to-text with `speechrecognition` and `pyaudio`
- Text-to-speech with `pyttsx3`
- Communication with Ollama API using `requests`
- Summarization of answers with `summarizer.py`
- Logging of sessions into `session.jsonl` and structured output in `summary.json`

## Installation
Clone the repository and install dependencies:

```bash
pip install -r requirements.txt

On macOS, you may need to install portaudio before installing pyaudio:

brew install portaudio
pip install pyaudio

Usage
Run the main script:

python main.py

ou will be prompted with interview questions.
Press Enter to start and stop voice recording, or type your answer manually.
At the end, the system generates a structured summary.
Output
Console: shows live Q&A and summary
session.jsonl: stores all runs with timestamp and answers
summary.json: stores extracted JSON summary
Project Structure

.
├── main.py             # Entry point
├── interview_cli.py    # Interview logic
├── ollama_client.py    # API client for Ollama
├── summarizer.py       # Summary generator
├── voice.py            # Voice input/output
├── requirements.txt    # Dependencies
├── session.jsonl       # Log of sessions
└── summary.json        # Structured summary

Author
Dogukan Somuncu
Prepared for the AI Engineering - Pathway 2 (AI Agent for Onboarding) assignment.