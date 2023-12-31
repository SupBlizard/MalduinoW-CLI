import math


# files = ["create", "remove", "rename", "write", "stream", "close", "read"]

# settings:
# settings, set, reset


MAX_FILENAME_LEN = 30




class Cmds:
    def __init__(self, malw):
        self.malw = malw
        self.MAX_WIDTH = 105

        # Store a list of custom methods
        self.available = [method for method in dir(self) if not method.startswith("__")]
    
    def mem(self, args=""):
        BAR_WIDTH = 50
        mem_str = self.malw.execute("mem").splitlines()
        total, used, free = int(mem_str[0].split(" ", 1)[0]), int(mem_str[1].split(" ", 1)[0]), int(mem_str[2].split(" ", 1)[0])
        percentage = math.ceil(used/(total/100))

        bar = f"[{('|'*math.ceil(percentage/(100/BAR_WIDTH))).ljust(BAR_WIDTH, '-')}] ({percentage}%)"
        return f"<{used} bytes used>  ".ljust(24)+bar+f"  <{free} bytes free>".rjust(self.MAX_WIDTH-len(bar)-24)
    

    def format(self, args=""):
        print("This action will begin formatting SPIFFS and disconnect the Malduino W")
        confirm = input("Are you sure you want to proceed ? [y/n]: ").lower()
        if confirm in ["yes", "y"]:
            self.malw.send("format")
            print("\nFormatting SPIFFS ...")
            self.exit()
        elif confirm in ["no", "n"]:
            return "Aborted"
        else: return "Invalid option, aborting"


    def run(self, args=""):
        self.malw.execute("stop")
        self.malw.execute("run "+args)
        return f"Running {args}"
    

    def ls(self, args=""):
        files = parse_file_list(self.malw.execute("ls"))
        file_list = f"{len(files['list'])} Script(s) saved, {files['size']} bytes in total.\n"
        for file in files["list"]: file_list+=f"/{file[0].ljust(self.MAX_WIDTH-19)} | {file[1].ljust(7)} byte(s)\n"
        return file_list
    

    def cat(self, filename=""):
        if not filename.strip():
            return "Missing filename."
        
        # Open file stream
        self.malw.execute("close")
        self.malw.execute("stop " + filename)
        self.malw.execute("stream " + filename)
        
        # Read stream
        content = ""
        while True:
            if (pkt := self.malw.execute("read")) == "> END": break
            content += pkt
        self.malw.execute("close")

        if not content:
            self.malw.execute("remove " + filename)
            return f'File {filename} not found'
        return (" "+args+" ").center(self.MAX_WIDTH, "-")+"\n"+content+"\n"+"-"*self.MAX_WIDTH
    

    def help(self, args=""):
        # TODO: Print additional utillity commands
        return self.malw.execute("help")


        
    # =========================================
    #             Utillity commands
    # =========================================
    def exit(self, args=""):
        self.malw.disconnect()
        self.malw.thread.join()
        exit(0)





def parse_file_list(fl:str):
    file_list, size = [], 0
    for file in fl.strip().splitlines():
        sep_idx = file.rindex(" ")
        file_list.append([file[1:sep_idx], file[sep_idx+1:]])
        size += int(file[sep_idx+1:])
    return {"list":file_list,"size":size}