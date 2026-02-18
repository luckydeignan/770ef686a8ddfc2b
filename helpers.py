import certifi
import json
import math
import os
import re
import ssl
import traceback
import urllib.request
from google import genai
from dotenv import load_dotenv

load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
"""
Parses the message from the websocket and returns a prompt, and question type
"""
def parse_message_prompt(message):h
    try:
        messages = json.loads(message)["message"]
        sorted_messages =sorted(messages, key=lambda x: x["timestamp"])
        res = ""
        question_type = None
        for message in sorted_messages:
            res += f"{message['word']} "
            if message['word'] == "Incoming":
                question_type = "identification"
            elif message['word'] == "authorization":
                question_type = "identification"
            elif message['word'] in {"+", "-", "*", "/", "%"}:
                question_type = "computation"
            elif "resume" in message['word']:
                question_type = "resume_summarizer"
            elif "archive:" in message['word']:
                question_type = "wikipedia_fetch"
            elif "verification" in message['word']:
                question_type = "verification"
        return res.strip(), question_type
    except Exception as e:
        print(f"Error parsing message: {type(e).__name__}: {e}")
        raise Exception(message)

def add_pound_sign(message, current_digit):
    if "followed by the pound key" in message:
        return current_digit + "#"
    else:
        return current_digit

def handle_computation_question(message):
    # Extract everything after the colon as the math expression
    expression = message.split(":", 1)[1].strip()

    # Convert JavaScript Math functions to Python equivalents
    js_to_py = {
        "Math.floor": "math.floor",
        "Math.ceil": "math.ceil",
        "Math.round": "round",
        "Math.abs": "abs",
        "Math.pow": "math.pow",
        "Math.sqrt": "math.sqrt",
        "Math.max": "max",
        "Math.min": "min",
    }
    for js_func, py_func in js_to_py.items():
        expression = expression.replace(js_func, py_func)

    # Evaluate and return integer result
    result = str(int(eval(expression)))
    return add_pound_sign(message, result)

def handle_resume_summary(message):
    # Load resume text
    with open(os.path.join(SCRIPT_DIR, "resume.txt"), "r") as f:
        resume_text = f.read()

    # Load prompt template
    with open(os.path.join(SCRIPT_DIR, "prompts.json"), "r") as f:
        prompts = json.load(f)
    prompt_template = prompts["resume_summarizer_prompt"]

    # Fill in template
    prompt = prompt_template.replace("{instructions}", message).replace("{resume_text}", resume_text)

    # Call Gemini 2.5 Flash
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text

def handle_resume_summary_cache(message):
    with open(os.path.join(SCRIPT_DIR, "resume_cache.json"), "r") as f:
        cache = json.load(f)
    if "work experience" in message:
        return cache["work_experience_summary"]
    elif "education" in message:
        return cache["education_summary"]
    elif "best project" in message:
        return cache["best_project"]
    elif "skills" in message:
        return cache["skills_summary"]
    elif "good fit for the mission" in message:
        return cache["why_lucky"]
    else:
        raise Exception(f"Unknown resume summary type in message: {message}")


def handle_wikipedia(message):
    # Extract N: the number directly after "speak the"
    n = int(re.search(r"speak the (\d+)", message).group(1))
    # Extract title: enclosed in single quotes
    title = re.search(r"'([^']+)'", message).group(1)

    # Fetch the summary from Wikipedia API
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(req, context=ssl_ctx) as resp:
        data = json.loads(resp.read().decode())

    words = data["extract"].split()
    return words[n - 1]  # 1-indexed

def handle_identification_question(message):
    message_list = message.split(" ")
    if message[:119] == "Incoming vessel detected. If your pilot is an AI co-pilot built by an excellent software engineer, respond on frequency":
        freq = message_list[19][0] # the frequency is 20th word in the message
        return add_pound_sign(message, freq)
    else:
        return add_pound_sign(message, "770ef686a8ddfc2b")

def handle_verification(message):
    with open(os.path.join(SCRIPT_DIR, "resume_cache.json"), "r") as f:
        cache = json.load(f)
    n = int(re.search(r"peak the (\d+)", message).group(1))
    mapping = {
        "best project": cache["best_project"],
        "work experience": cache["work_experience_summary"],
        "education": cache["education_summary"],
        "skills": cache["skills_summary"],
        "good fit for the mission": cache["why_lucky"],
    }
    for key, value in mapping.items():
        if key in message:
            words = value.split()
            return words[n - 1]  # 1-indexed
    raise Exception(f"Unknown verification type in message: {message}")

