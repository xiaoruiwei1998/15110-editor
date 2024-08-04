import environ
from openai import OpenAI
from student.repository import ConversationRepository

env = environ.Env()
environ.Env.read_env()
OPENAI_KEY = env('OPENAI_KEY')

def completion(conversation, system_message, user_message):

    # Generate new conversation or load conversation log
    if not conversation["conversation_log"]:
        messages=[
            {"role": "system", "content": f"{system_message}"},
            {"role": "user", "content": f"{user_message}"},
        ]
    else:
        messages = conversation["conversation_log"]
        messages.append({"role": "user", "content": f"{user_message}"})

    # Acquire GPT-4 response
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    # Post response processing
    agent_response = response.choices[0].message.content
    messages.append({"role": "assistant", "content": f"{agent_response}"})
    ConversationRepository.update_conversation(conversation["_id"], {"conversation_log": messages})
    return agent_response

def get_response(conversation, system_message, user_message):
    response = completion(conversation, system_message, user_message)
    if not response: response = "Sorry for the invconvenience. Currently having difficulties. Please try again later."
    return response

def get_completion(system_message: str, user_message: str) -> str:    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]
    )
    return response.choices[0].message.content