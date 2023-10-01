import websocket, time, argparse
from threading import Thread, Lock





def main(args):
    ws = WebSocketClient("192.168.4.1", args.trace)
    ws.connect()

    print(wait_for(ws.is_connected, True, delay=0.25, timeout=5))
    print(execute_cmd(ws, "version"))

    # while True:
    #     if crt_pkt != None:
    #         time.sleep(0.5)
    #         continue

    #     try:
    #         # Get input
    #         pkt = input("> ")
    #     except EOFError:
    #         ws.close()
    #         exit(0)
        
    #     # Exit case
    #     if pkt == "exit":
    #         ws.close()
    #         exit(0)

    #     # Send packet
    #     crt_pkt = pkt
    #     send_pkt(pkt)





class WebSocketClient:
    def __init__(self, server:str, trace:bool):
        self.server = server
        self.ws = None
        self.debug = trace
        self.connected = False
        self.__lock = Lock()
        self.__pkt_buffer = None
        
    def connect(self):
        if self.connected == True:
            return False

        if self.debug: self.ws.enableTrace()
        self.ws = websocket.WebSocketApp(f"ws://{self.server}/ws",
            on_open=self.__on_open,
            on_message=self.__on_message,
            on_error=self.__on_error,
            on_close=self.__on_close)
        
        # Start thread
        self.thread = Thread(target=self.ws.run_forever, daemon=True)
        self.thread.start()

    def is_connected(self) -> bool:
        return self.connected

    def send(self, pkt:str):
        self.ws.send(pkt)
    
    def receive(self) -> str:
        if not self.__pkt_buffer:
            return None
        with self.__lock:
            pkt = self.__pkt_buffer
            self.__pkt_buffer = None
        return pkt
    

    # WS methods
    def __on_message(self, ws, pkt:str):
        with self.__lock:
            self.__pkt_buffer = pkt

    def __on_error(self, ws, err):
        try:
            raise err
        except KeyboardInterrupt:
            self.ws.close()

    def __on_open(self, ws):
        with self.__lock:
            self.connected = True

    def __on_close(self, ws, code, msg):
        with self.__lock:
            self.connected = False
        exit(0)





def wait_for(func, expected, delay, timeout):
    rtn = None
    while (rtn := func()) != expected:
        time.sleep(delay)
        if timeout != None and (timeout := timeout - delay) < 0:
            return None
    return rtn

def execute_cmd(ws, cmd, timeout=3, delay=0.1):
    ws.send(cmd)
    rtn = None
    while type(rtn := ws.receive()) is not str:
        time.sleep(delay)
        if (timeout := timeout - delay) < 0:
            return None
    return rtn
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--trace", help="Enable WS tracing", action="store_true")
    main(parser.parse_args())