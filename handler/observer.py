import datetime

def observer_handler(server, websocket, json_data):
    check_message = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} : {json_data}"
    print(f"[HANDLER]\t: {check_message}")
    
