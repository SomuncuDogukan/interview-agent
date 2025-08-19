# interview_cli.py
# Push-to-talk interview: press Enter to record; robust STT; rephrase; full logging.

import time, json
from typing import List, Dict
import speech_recognition as sr

from ollama_client import OllamaClient
from summarizer import Summarizer
from voice import tts_say  # pyttsx3 (optionally with macOS 'say' fallback)
# Optional Whisper STT (uncomment if you have it in voice.py):
# from voice import stt_listen_whisper

# Toggle: use Whisper offline STT instead of Google Web (needs voice.stt_listen_whisper)
USE_WHISPER = False   # set True to use Whisper
WHISPER_SECONDS = 10  # recording length for Whisper


class InterviewAgent:
    """Ask 5 Qs, capture answers, re-ask if unclear, log with timestamps, summarize (Markdown+JSON)."""

    def __init__(self, model: str = "qwen2.5:7b", voice: bool = True):
        self.client = OllamaClient(model=model)
        self.summarizer = Summarizer(model=model)
        self.voice = voice
        self.turns: List[Dict] = []        # [{ts, role, text}]
        self.answers: Dict[str, str] = {}  # collected answers

        # STT recognizer tuning (Google Web engine)
        self.rec = sr.Recognizer()
        self.rec.dynamic_energy_threshold = True
        self.rec.pause_threshold = 0.9
        self.timeout = 12
        self.phrase_time_limit = 18

        # Assignment-required questions
        self.questions = [
            ("name_background", "What is your full name and your background?"),
            ("motivation",      "Why are you interested in joining the program?"),
            ("experience",      "What’s your experience with data science or AI?"),
            ("goals",           "What are your short-term and long-term goals?"),
            ("readiness",       "Are you ready to start immediately? If not, when?")
        ]

    # --- helpers --------------------------------------------------------------

    def _say(self, text: str):
        """Speak/print and log."""
        if self.voice:
            tts_say(text)
        else:
            print(f"AI: {text}")
        self.turns.append({"ts": time.time(), "role": "agent", "text": text})

    def _type_or_speak(self) -> str:
        """
        User can type, or press Enter to speak.
        Two STT attempts; then force typing.
        """
        typed = input("> Type your answer (or press Enter to speak): ").strip()
        if typed:
            self.turns.append({"ts": time.time(), "role": "user", "text": typed})
            return typed

        # push-to-talk path
        for attempt in range(2):
            said = self._p2t_once()
            if len(said.split()) >= 2:
                self.turns.append({"ts": time.time(), "role": "user", "text": said})
                return said
            self._say("I couldn't catch that. Please try again.")

        typed2 = input("> Please type your answer: ").strip()
        self.turns.append({"ts": time.time(), "role": "user", "text": typed2})
        return typed2

    def _p2t_once(self) -> str:
        """One push-to-talk attempt using Google Web or Whisper."""
        input("\n🎤 Press Enter to start recording...")
        if USE_WHISPER:
            # Offline STT (needs voice.stt_listen_whisper)
            try:
                # from voice import stt_listen_whisper  # ensure imported if you set USE_WHISPER=True
                text = stt_listen_whisper(seconds=WHISPER_SECONDS, model_name="small")
                return (text or "").strip()
            except Exception:
                print("⚠️ Whisper STT not available; falling back to Google Web.")
                # fall through to Google path

        # Google Web path
        with sr.Microphone() as source:
            try:
                self.rec.adjust_for_ambient_noise(source, duration=1.2)
            except Exception:
                pass
            print("Listening... speak now.")
            try:
                audio = self.rec.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit
                )
            except sr.WaitTimeoutError:
                print("⚠️ No speech detected.")
                return ""
        try:
            text = self.rec.recognize_google(audio)  # requires internet
            print("You said:", text)
            return text.strip()
        except sr.UnknownValueError:
            print("⚠️ Could not understand audio.")
            return ""
        except sr.RequestError:
            print("⚠️ Speech service not available (check internet).")
            return ""

    def _rephrase(self, question: str) -> str:
        """Ask LLM to rephrase once."""
        return self.client.chat([
            {"role": "system", "content": "Rephrase the interview question clearly in one sentence."},
            {"role": "user",   "content": question}
        ])

    # --- main flow ------------------------------------------------------------

    def run(self):
        self._say("Welcome to the AI Interview Agent!")
        for key, q in self.questions:
            self._say(q)
            time.sleep(0.8)  # let TTS finish; reduce echo into mic
            ans = self._type_or_speak()

            if len(ans.split()) < 2:
                rp = self._rephrase(q)
                self._say(f"Let me rephrase: {rp}")
                time.sleep(0.6)
                ans = self._type_or_speak()

            self.answers[key] = ans

        # Build summary (Markdown + JSON)
        combined_text, json_obj = self.summarizer.summarize_markdown_and_json(self.answers)
        self._say("Here is the interview summary.")

        # Persist session
        record = {
            "created_at": time.time(),
            "model": self.client.model,
            "turns": self.turns,
            "answers": self.answers,
            "summary_md_and_json": combined_text,
            "summary_json": json_obj
        }
        with open("session.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        print("\n----- SUMMARY (Markdown + JSON) -----\n")
        print(combined_text)
        print("\nSaved to session.jsonl (and summary.json)")
