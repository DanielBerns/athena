import os
from pathlib import Path

from webclient import (
    get_auth_headers,
    get_messages,
    clear_messages,
    publish_post,
    publish_picture,
)

import random

sequence = [v for v in range(42)]

def get_random_sequence(length):
    numbers = random.sample(sequence, 6)
    content = ','.join([str(nn) for nn in numbers])
    return "{" + content + "}"

import pdb

def main():
    AGENT_IDENTIFIER = os.environ.get("ATHENA_AGENT") or "random"    
    CLEAR_MESSAGES_switch = os.environ.get("CLEAR_MESSAGES") or "NO"
    CLEAR_MESSAGES = CLEAR_MESSAGES_switch == "YES"

    log_switches = Path("~", "Info", "athena", "switches.md").expanduser()  
    with open(log_switches, "w") as target:
        target.write(f"AGENT_IDENTIFIER {AGENT_IDENTIFIER:s}\n"
                     f"CLEAR_MESSAGES {CLEAR_MESSAGES}\n"
                    )

    auth_headers = get_auth_headers(AGENT_IDENTIFIER)
    if auth_headers:
        for message in get_messages(auth_headers):
            print("message_id", message["id"])
            sender_id = message["sender_id"]
            content = message["content"]
            print("content\n", content)
        if CLEAR_MESSAGES:
            print("start clearing messages")
            clear_messages(auth_headers)
            print("done clearing messages")
        for nn in range(15):
            content = get_random_sequence(6)
            publish_post(auth_headers, content) 


if __name__ == "__main__":
    main()
