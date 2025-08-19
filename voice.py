# voice.py
# Reliable TTS on macOS: prefer 'say', fallback to pyttsx3.

import subprocess

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

USE_MAC_SAY = True   # prefer macOS 'say' for reliability
_tts = None

def tts_say(text: str):
    """Speak text reliably. Prefer macOS 'say', fallback to pyttsx3."""
    print(f"AI: {text}")

    # 1) Try macOS 'say'
    if USE_MAC_SAY:
        try:
            # -r 190: speaking rate; adjust to taste
            subprocess.run(["say", "-r", "190", text], check=True)
            return
        except Exception:
            pass  # fall back to pyttsx3

    # 2) Fallback: pyttsx3
    if pyttsx3 is None:
        return  # no engine available
    global _tts
    try:
        if _tts is None:
            _tts = pyttsx3.init()
            _tts.setProperty("rate", 180)
        _tts.say(text)
        _tts.runAndWait()
    except Exception:
        # give up silently
        return
