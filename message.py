import traceback
import json
import websocket
from datetime import datetime, timezone


class Message():
    def __init__(self, ws_server, sender):
        self.ws_server = ws_server
        self.sender = sender

    def get_timestring(self):
        return datetime.now(timezone.utc).isoformat().split('+')[0]

    def send_ws(self, user, type, **kwargs):
        try:
            ws = websocket.WebSocket()
            ws.connect(self.ws_server)
            export_dict = {
                "sender": self.sender,
                "user": user,
                "time": self.get_timestring(),
                "type": type,
                "data": kwargs,

            }
            export_json = json.dumps(export_dict, ensure_ascii=False)
            ws.send(export_json)
            ws.close()
        except:
            return traceback.format_exc()


class ObserverMessage(Message):
    def __init__(self, ws_server):
        super().__init__(ws_server, "observer")
