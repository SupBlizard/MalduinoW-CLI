import websocket, time, argparse
from threading import Thread

malW_server = "192.168.4.1"
crt_pkt = None


def on_open(ws):
    print(f" Connection Started ".center(62, "-"))

    # Start input daemon
    Thread(target=input_thread, args=[ws], daemon=True).start()

def on_message(ws, pkt:str):
    global crt_pkt
    print(pkt)
    crt_pkt = None

def on_error(ws, err):
    try:
        raise err
    except KeyboardInterrupt:
        ws.close()

def on_close(ws, code, msg):
    print(f" Connection Closed ".center(62, "-"))
    exit(0)




# Take input from user
def input_thread(ws):
    global crt_pkt
    while True:
        if crt_pkt != None:
            time.sleep(0.5)
            continue

        try:
            # Get input
            pkt = input("> ")
        except EOFError:
            ws.close()
            exit(0)
        
        # Exit case
        if pkt == "exit":
            ws.close()
            exit(0)

        # Send packet
        crt_pkt = pkt
        send_pkt(pkt)
            

def send_pkt(pkt):
    ws.send(pkt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--trace", help="Enable WS tracing", action="store_true")
    args = parser.parse_args()

    if args.trace: websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"ws://{malW_server}/ws",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)
    ws.run_forever()