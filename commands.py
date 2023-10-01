


managed = {
    "ram",
    "run",
    "settings",
    "status",
    "mem",
    "format",
    "ls",
    "help",
}

unmanaged = ["create", "remove", "cat", "rename", "write", "stream", "close", "read", "stop", "set", "reset", "version"]



# MAX FILENAME LEN = 30




class Commands:
    def run(malw, args:list):
        if malw.running:
            malw.execute("stop "+args[1])
        malw.execute("run "+args[1])
        malw.running = args
    
    def exit(malw, args:list):
        malw.disconnect()
        exit(0)
