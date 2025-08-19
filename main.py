from interview_cli import InterviewAgent

if __name__ == "__main__":
    agent = InterviewAgent(model="qwen2.5:7b", voice=True)  # voice=True => TTS on, push-to-talk on
    agent.run()
