# summarizer.py
# Builds a Markdown summary + a JSON block and also writes summary.json.

import json
import re
import time
from typing import Dict, Tuple
from ollama_client import OllamaClient


class Summarizer:
    """Create human-readable summary + structured JSON via LLM."""
    def __init__(self, model: str = "qwen2.5:7b"):
        self.client = OllamaClient(model=model)

    def summarize_markdown_and_json(self, answers: Dict[str, str]) -> Tuple[str, dict]:
        """
        Returns (combined_markdown_and_json_text, parsed_json).
        Also writes summary.json to disk if JSON can be parsed.
        """
        system = (
            "You are an admissions interview summarizer. "
            "Write concise English. First output a short Markdown summary (<=120 words). "
            "Then output ONLY one fenced code block with a JSON object using keys: "
            "name, background, motivation, experience, goals_short, goals_long, readiness, interest_level."
        )
        user = (
            "Use these answers to produce the summary and JSON.\n"
            f"{json.dumps(answers, ensure_ascii=False)}\n"
            "For interest_level use an integer 1-5. JSON must be valid."
        )

        text = self.client.chat([
            {"role": "system", "content": system},
            {"role": "user",   "content": user}
        ])

        # Try to extract the JSON part from a fenced block or raw braces
        parsed = {}
        try:
            block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S).group(1)
        except Exception:
            # fallback: take the widest {...} in the text
            m1 = text.find("{")
            m2 = text.rfind("}")
            block = text[m1:m2+1] if (m1 != -1 and m2 != -1) else ""

        if block:
            try:
                parsed = json.loads(block)
            except Exception:
                parsed = {}

        # Write standalone JSON if available
        if parsed:
            with open("summary.json", "w", encoding="utf-8") as jf:
                json.dump(parsed, jf, indent=2, ensure_ascii=False)

        # Also append full record into session.jsonl (done by caller too, but keep here as utility)
        with open("session.jsonl", "a", encoding="utf-8") as f:
            record = {
                "created_at": time.time(),
                "model": self.client.model,
                "answers": answers,
                "summary_md_and_json": text,
                "summary_json": parsed
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return text, parsed
