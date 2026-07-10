from dotenv import load_dotenv
import os

load_dotenv()

print("KEY FOUND:", bool(os.getenv("OPENAI_API_KEY")))

key = os.getenv("OPENAI_API_KEY")

if key:
    print("FIRST 10 CHARS:", key[:10])