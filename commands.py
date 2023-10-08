


# misc = {
#     "run",
#     "status",
#     "mem",
#     "format",
#     "help",
#     "stop",
#     "version"
# }

# files = ["create", "remove", "rename", "write", "stream", "close", "read", "ls"]

# settings:
# settings, set, reset


MAX_FILENAME_LEN = 30




class Cmds:
    def __init__(self, malw):
        self.malw = malw

        # Store a list of custom methods
        self.available = [method for method in dir(self) if not method.startswith("__")]
    


    def run(self, args=""):
        self.malw.execute("stop")
        self.malw.execute("run "+args)
        return f"Running {args}"
    
    def ls(self, args=""):
        files = parse_file_list(self.malw.execute("ls"))
        file_list = f"{len(files['list'])} Script(s) saved, {files['size']} bytes in total.\n"
        for file in files["list"]: file_list+=f"/{file[0].ljust(MAX_FILENAME_LEN)} | {file[1].ljust(7)} byte(s)\n"
        return file_list
    

    def cat(self, args=""):
        timeout, delay = 500, 50
        file_content = ""

        if not args.strip(): return "Missing filename."
            
        filename = '"/'+args+'"'
        self.malw.execute("close")
        self.malw.execute("stop " + filename)
        self.malw.execute("stream " + filename)
        
        # Read stream
        while True:
            if (pkt := self.malw.execute("read")) == "> END": break
            file_content += pkt
        self.malw.execute("close")
        
        return (" "+args+" ").center(100, "-")+"\n"+file_content+"\n"+"-"*100

        
    # =========================================
    #             Utillity commands
    # =========================================
    def exit(self, args=""):
        self.malw.disconnect()
        self.malw.thread.join()
        exit(0)





def parse_file_list(fl:str):
    file_list, size = [], 0
    for file in fl.strip().split("\n"):
        sep_idx = file.rindex(" ")
        file_list.append([file[1:sep_idx], file[sep_idx+1:]])
        size += int(file[sep_idx+1:])
    return {"list":file_list,"size":size}