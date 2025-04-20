from openai import  OpenAI , models
from env import openai_api
from asgiref.sync import sync_to_async

client = OpenAI(api_key=openai_api)


@sync_to_async
def ProcessText(message_list):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=message_list
            )
        return True ,completion.choices[0].message.content
    except Exception as e:
        return False, str(e)