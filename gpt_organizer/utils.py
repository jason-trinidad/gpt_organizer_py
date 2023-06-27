from typing import List


def compose_message_history(history: List[str]) -> str:
    message_history_str = ""
    if history:
        for i, message in enumerate(history):
            if i % 2 != 0:
                message_history_str += f"\nHuman: {message}"
            else:
                message_history_str += f"\nAI: {message}"

    return message_history_str
