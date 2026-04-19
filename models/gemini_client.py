from google import genai
import os
import time


def call_gemini(prompt: str) -> str:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    last_error = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            last_error = e
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                # Extract retry delay if present, else back off 30s
                import re
                match = re.search(r"retryDelay.*?(\d+)s", msg)
                wait = int(match.group(1)) + 2 if match else 30
                if attempt < 2:
                    time.sleep(wait)
                    continue
            raise
    raise last_error
