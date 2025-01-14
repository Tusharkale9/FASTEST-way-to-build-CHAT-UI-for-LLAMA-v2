import os

import gradio as gr
from text_generation import Client


PROMPT = """<s>[INST] <<SYS>>
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
<</SYS>>

"""

LLAMA_70B = os.environ.get("LLAMA_70B", "http://localhost:3000")
CLIENT = Client(base_url=LLAMA_70B)

PARAMETERS = {
    "temperature": 0.9,
    "top_p": 0.95,
    "repetition_penalty": 1.2,
    "top_k": 50,
    "truncate": 1000,
    "max_new_tokens": 1024,
    "seed": 42,
    "stop_sequences": ["</s>"],
}


def format_message(message, history, memory_limit=5):
    # always keep len(history) <= memory_limit
    if len(history) > memory_limit:
        history = history[-memory_limit:]

    if len(history) == 0:
        return PROMPT + f"{message} [/INST]"

    formatted_message = PROMPT + f"{history[0][0]} [/INST] {history[0][1]} </s>"

    # Handle conversation history
    for user_msg, model_answer in history[1:]:
        formatted_message += f"<s>[INST] {user_msg} [/INST] {model_answer} </s>"

    # Handle the current message
    formatted_message += f"<s>[INST] {message} [/INST]"

    return formatted_message


def predict(message, history):
    query = format_message(message, history)
    text = ""
    for response in CLIENT.generate_stream(query, **PARAMETERS):
        if not response.token.special:
            text += response.token.text
            yield text


gr.ChatInterface(predict).queue().launch()
