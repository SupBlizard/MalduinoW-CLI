import websocket, time, argparse
from threading import Thread, Lock

from commands import Commands

SERVER_IP = "192.168.4.1"


def main(args):
    malw = WebSocketClient(SERVER_IP, args.debug)
    malw.connect()

    # Await connection to be established and initialise
    if not wait_for(malw.is_connected, True, delay=0.25, timeout=5):
        malw.disconnect()
        raise websocket.WebSocketTimeoutException("Failed to establish connection")
    else: malw.execute("close")

    print(" Connection Established ".center(100, "="))
    print("Firmware " + malw.execute("version"))
    print(malw.execute("mem"))
    print(malw.execute("ls"))

    # Load available commands
    cmds = [method for method in dir(Commands) if not method.startswith("__")]
    
    while True:
        try:
            # Get input
            cmd = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            malw.disconnect()
            break
        
        # Check if the command has custom handling
        if (cmd_name := cmd.split(" ", maxsplit=1)[0]) in cmds:
            getattr(Commands, cmd_name)(malw, cmd)
 
        # Send and listen
        resp = malw.execute(cmd)
        print(resp)
    



def wait_for(func, expected, delay, timeout):
    rtn = None
    while (rtn := func()) != expected:
        time.sleep(delay)
        if timeout != None and (timeout := timeout - delay) < 0:
            return None
    return rtn


class WebSocketClient:
    def __init__(self, server:str, debug:bool):
        self.server = server
        self.debug = debug
        self.connected = False
        self.running = None

        self.__ws = None
        self.__lock = Lock()
        self.__pkt_buffer = []
        
    def connect(self):
        if self.connected == True:
            return False

        if self.debug: self.__ws.enableTrace()
        self.__ws = websocket.WebSocketApp(f"ws://{self.server}/ws",
            on_open=self.__on_open,
            on_message=self.__on_message,
            on_error=self.__on_error,
            on_close=self.__on_close)

        # Start thread
        self.thread = Thread(target=self.__ws.run_forever, daemon=True)
        self.thread.start()
    
    def disconnect(self):
        self.__ws.close()

    def is_connected(self) -> bool:
        return self.connected
    
    def send(self, pkt:str):
        self.__ws.send(pkt)
    
    def listen(self) -> str:
        if len(self.__pkt_buffer) == 0:
            return None
        with self.__lock:
            pkt = self.__pkt_buffer[0]
            self.__pkt_buffer = []
        return pkt
    
    def execute(self, cmd:str, delay=0.1, timeout=5) -> str:
        self.send(cmd+"\n")
        while time.sleep(delay) == None: # (identical to "while True" but calls sleep)
            if type(resp := self.listen()) is str:
                return resp
            elif (timeout := timeout - delay) < 0:
                raise websocket.WebSocketTimeoutException("Command timed out")
    

    # WS methods
    def __on_message(self, ws, pkt:str):
        with self.__lock:
            self.__pkt_buffer.append(pkt)

    def __on_error(self, ws, err):
        try:
            raise err
        except KeyboardInterrupt:
            self.__ws.close()

    def __on_open(self, ws):
        with self.__lock:
            self.connected = True

    def __on_close(self, ws, code, msg):
        with self.__lock:
            self.connected = False
        print("\n"+" Disconnected ".center(100, "="))
        exit(0)



    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="Enable WS tracing", action="store_true")
    args = parser.parse_args()

    try:   main(args)
    except websocket.WebSocketException as e:
        if args.debug == True: print(e, end="\n\n")
        else: raise e