


managed = {
    "cat",
    "ram",
    "run",
    "settings",
    "status",
    "mem",
    "format",
    "ls",
    "help",
}

unmanaged = ["create", "remove", "rename", "write", "stream", "close", "read", "stop", "set", "reset", "version"]



MAX_FILENAME_LEN = 30




class Commands:
    def run(malw, args:list):
        if malw.running:
            malw.execute("stop "+args[1])
        malw.running = args
        return malw.execute("run "+args[1])
    
    def ls(malw, args:list):
        files = process_file_list(malw.execute("ls"))
        print(f"{len(files['list'])} Script(s) saved, {files['size']} bytes in total.")
        for file in files["list"]: print(f"/{file[0].ljust(MAX_FILENAME_LEN)} | {file[1].ljust(7)} byte(s)")
    



    # =========================================
    #             Custom commands
    # =========================================
    def exit(malw, args:list):
        malw.disconnect()
        exit(0)






def process_file_list(fl:str):
    file_list, size = [], 0
    for file in fl.strip().split("\n"):
        sep_idx = file.rindex(" ")
        file_list.append([file[1:sep_idx], file[sep_idx+1:]])
        size += int(file[sep_idx+1:])
    return {"list":file_list,"size":size}