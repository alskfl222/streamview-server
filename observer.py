import os
import sys
import traceback
import json
import websocket
import pytchat
# from dotenv import load_dotenv
from message import ObserverMessage

# load_dotenv()

# WS_SERVER = os.getenv("WS_SERVER_CLOUD") if os.getenv(
#     "PY_ENV") == "production" else os.getenv("WS_SERVER_LOCAL")
WS_SERVER = "ws://127.0.0.1:8000/ws"


class Observer():
    def __init__(self, stream_id):
        print(f"STREAM_ID : {stream_id}")
        print()
        self.chat = pytchat.create(video_id=stream_id)
        self.commands = {
            '캐릭터': 'charactor'
        }
        self.message = ObserverMessage(WS_SERVER)

    def handle_chat(self, chat):
        args = chat.split(' ')
        command = args[0][1:]
        if args[0].startswith("!") and command in self.commands.keys():
            return command, args[1:]
        return None, None

    def run(self):
        print('OBSERVER START')
        while self.chat.is_alive():
            try:
                data = self.chat.get()
                items = data.items
                for item in items:
                    # print(
                    #     f"{item.datetime} : {item.author.name} [{item.author.isChatOwner}] - {item.message}")
                    command, args = self.handle_chat(item.message)
                    if command:
                        self.message.send_ws(
                            user=item.author.name, args=args)
            except:
                traceback.print_exc()
                print("BREAK")
                self.chat.terminate()
                break


if __name__ == '__main__':
    try:
        stream_id = sys.argv[1]
    except:
        print('error stream_id')
        sys.exit(0)
    try:
        observer = Observer(stream_id)
        observer.run()
    except:
        traceback.print_exc()
        sys.exit(0)
