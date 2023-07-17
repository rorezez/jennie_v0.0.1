#!/usr/bin/env python3
from openai_decorator.openai_decorator import openaifunc, get_openai_funcs
import openai
import os
import sys
import json
from dotenv import load_dotenv
from PyP100 import PyL530
import logging
import memory
from dateutil.parser import parse
from datetime import datetime
from notion_client import Client


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
logger = logging.getLogger("httpx").setLevel(logging.WARNING)


load_dotenv()  # take environment variables from .env.
openai.api_key = os.getenv("OPENAI_API_KEY")





@openaifunc
def get_current_datetime():
    """Return the current date and time."""
    now = datetime.now()
    return now.isoformat()


# ChatGPT API Function
def send_message(message, messages):
    # add user message to message list
    messages.append(message)

    try:
        # send prompt to chatgpt
        response = openai.ChatCompletion.create(
            # model="gpt-4-0613",
            model="gpt-4-0613",
            messages=messages,
            functions=get_openai_funcs(),
            function_call="auto",
        )
    except openai.error.AuthenticationError:
        print("AuthenticationError: Check your API-key")
        sys.exit(1)

    # add response to message list
    messages.append(response["choices"][0]["message"])
    # print the response in JSON format
    print(json.dumps(response, indent=4))

    return messages

#NOTION

@openaifunc
def add_reminder(reminder: str, date: str):
    """fungsi ini di gunakan untuk menambah reminder ke dalam notion
        @param reminder: ini adalah nama dari agenda yang akan di buat
        @param date : adalah tanggal dari agenda itu dalam format date_time.isoformat()
    """
    # Convert the date string to a datetime object
    date_time = parse(date)
    notion_key = os.getenv('NOTION_KEY')
    database_id = os.getenv('DATABASE_ID')
     # Create the Notion client
    notion = Client(auth=notion_key)

    try:
        # Create a new page in the database
        page = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "reminder": {
                    "title": [
                        {
                            "text": {
                                "content": reminder
                            }
                        }
                    ]
                },
                "date": {
                    "date": {
                        "start": date_time.isoformat(),
                    }
                },
            }
        )
        return f"Reminder berhasil ditambahkan dengan ID: {page.get('id')}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Maaf, terjadi kesalahan saat menambahkan pengingat Anda."
    

# MAIN FUNCTION
def run_conversation(prompt, messages=[]):
    # add system prompt to chatgpt messages
    prompt_id = 'default_prompt'
    prompt_text = memory.get_prompt(prompt_id)
    messages.append({
        "role": "system",
        "content": prompt_text
    })
    # add user prompt to chatgpt messages
    messages = send_message({"role": "user", "content": prompt}, messages)

    while True:
        # get chatgpt response
        message = messages[-1]

        if message.get("function_call"):
            # get function name and arguments
            function_name = message["function_call"]["name"]
            arguments = json.loads(message["function_call"]["arguments"])

            # call function dangerously
            function_response = globals()[function_name](**arguments)
            
            # send function result to chatgpt
            messages = send_message(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                },
                messages,
            )
        else:
            # if chatgpt doesn't respond with a function call, return message
            return message["content"]

        # save last response for the while loop
        message = messages[-1]
