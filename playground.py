import asyncio
import certifi
import os
import traceback
import websockets
from helpers import parse_message_prompt, handle_identification_question, handle_computation_question, handle_resume_summary_cache, handle_resume_summary, handle_verification, handle_wikipedia
import json

os.environ['SSL_CERT_FILE'] = certifi.where()

def handler(message):
    prompt, question_type = parse_message_prompt(message)
    if question_type == "identification":
        frequency = handle_identification_question(prompt)
        return json.dumps({"type": "enter_digits", "digits": frequency})
    elif question_type == "computation":
        result = handle_computation_question(prompt)
        return json.dumps({"type": "enter_digits", "digits": result})
    elif question_type == "resume_summarizer":
        result = handle_resume_summary_cache(prompt)
        return json.dumps({"type": "speak_text", "text": result})
    elif question_type == "wikipedia_fetch":
        result = handle_wikipedia(prompt)
        return json.dumps({"type": "speak_text", "text": result})
    elif question_type == "verification":
        result = handle_verification(prompt)
        return json.dumps({"type": "speak_text", "text": result})
    return json.dumps({"type": "send_message", "message": prompt})

async def connect_to_wss(uri, handler):
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")

            async for message in websocket:
                print(f"< Message & Question Type: {parse_message_prompt(message)}")
                reply = handler(message)
                if reply is not None:
                    await websocket.send(reply)
                    print(f"> Sent: {reply}")

    except Exception as e:
        print(f"Connection failed: {type(e).__name__}: {e}")
        print()
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(connect_to_wss('wss://neonhealth.software/agent-puzzle/challenge', handler))