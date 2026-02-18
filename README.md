# 770ef686a8ddfc2b
Neon Health Coding Challenge. 

Main file to run is playground.py

## Process
In the beginning, I designed the high-level system of the various functions I was going to implement (handler, parser, specific_handlers for each question_type). The general process in implementing each of these functions was very iterative. I handled one question type (identification, computation, etc) at a time, and the implementation of my function was based on the logged requests from the websocket during this process.

Upon analyzing the request format for each question type, I developed the handlers for that specific task. The current solution is very "hacky", with hardcoded values that are used as checks (or response outputs in some cases). Though this is obviously not very good practice for general code, I noticed all the requests had the exact same format so I decided to take advantage of this. 

## Use of LLMs
I designed the specifications and design of each of the functions used in this pipeline, as well as the logic all but one (connect_to_wss()) of the implementations. I used an LLM to write the actual lines of code, with the inputs being my specifications for the functions. The LLMs only designed one function at a time, and I intentially did not expose the LLM to the greater context of the problem so that I would have to design and understand the overall system and logic within each of the functions.

## Note on Gemini API Call
Code currently has some extranneous functions that call Gemini for the resume summarizer. Once I realized I can just cache the responses I stopped using these to avoid timing out, but left these functions in there to show evolution of the program.

## Finally
I very much resonate with the system's response as to why I am a good fit, worth checking out imo.
