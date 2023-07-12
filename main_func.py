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
from notion.client import NotionClient

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
logger = logging.getLogger("httpx").setLevel(logging.WARNING)


load_dotenv()  # take environment variables from .env.
openai.api_key = os.getenv("OPENAI_API_KEY")
notion_token = os.getenv("NOTION_TOKEN")
database_url = os.getenv("DATABASE_URL")

# Membuat objek lampu dengan alamat IP, email, dan password
l530 = PyL530.L530("192.168.0.23", "rorezxez@gmail.com", "tyutyu12T")
# Melakukan handshake dan login
l530.handshake()
l530.login()

@openaifunc
def turn_on():
    """get the lamp to turn on"""
    l530.turnOn()
    return "Turned on the light."

@openaifunc
def turn_off():
    """get the lamp to turn off"""
    l530.turnOff()
    return "Turned off the light."

@openaifunc
def set_brightness(percentage: int) -> str:
    """set the brightness of the lamp"""
    l530.setBrightness(percentage)
    return f"Set the brightness to {percentage}%."


@openaifunc
def set_color(hue: int, saturation: int) -> str:
    """set the color of the lamp"""
    l530.setColor(hue, saturation)
    return f"Set the color to hue {hue} and saturation {saturation}."



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

    return messages

#NOTION
def connect_to_notion(token):
    # Menginisiasi koneksi ke Notion
    client = NotionClient(token_v2=token)
    return client
def get_notion_database(client, database_url):
    # Mengambil database Notion berdasarkan URL-nya
    db = client.get_collection_view(database_url)
    return db
@openaifunc
@openaifunc
def add_reminder_to_notion(reminder):
    """ini adalah funsi untuk menambahkan reminder pada database notion
        @param reminder adalah task=reminder dan date=tanggal
    """
    # Menginisiasi koneksi ke Notion
    client = NotionClient(token_v2=notion_token)
    # Mengambil database Notion berdasarkan URL-nya
    db = client.get_collection_view(database_url)
    
    # Membuat baris baru di database Notion
    row = db.collection.add_row()
    # Menambahkan reminder ke baris baru
    row.task = reminder['task']  # Menggunakan 'task' sebagai nama
    row.date = reminder['date']  # Menggunakan 'date' sebagai tanggal
    return "Reminder has been added."

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
    messages = send_message({"role": "user", "content": prompt}, messages                           
                            )

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
        # if chatgpt doesn't respond with a function call, ask user for input
        return message["content"]

    # save last response for the while loop
    message = messages[-1]

    return message["content"]
