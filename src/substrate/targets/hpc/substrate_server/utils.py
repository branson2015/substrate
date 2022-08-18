import subprocess
import pty
import os
import fcntl
import struct
import termios
import select

def set_winsize(fd, row, col, xpix=0, ypix=0):
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

def read_and_forward_pty_output(server, ns):
    max_read_bytes = 1024 * 20
    while True:
        server.socketio.sleep(0.01)
        if server.app.config[f'{ns}_fd']:    
            timeout_sec = 0
            (data_ready, _, _) = select.select([server.app.config[f'{ns}_fd']], [], [], timeout_sec)
            if data_ready:
                output = os.read(server.app.config[f'{ns}_fd'], max_read_bytes).decode()
                server.socketio.emit("pty-output", {"output": output}, namespace=ns)

def socketio_pty(server, ns):
    server.app.config[f'{ns}_child_pid'] = None
    server.app.config[f'{ns}_fd'] = None

    @server.socketio.on('connect', namespace=ns)
    def handle_pty_connect(message):   
        if server.app.config[f'{ns}_child_pid'] != None:             # already started child process, don't start another
            return
        (child_pid, fd) = pty.fork()                                 # create child process attached to a pty we can read from and write to
        if child_pid == 0:                                           # this is the child process fork. anything printed here will show up in the pty, including the output of this subprocess
            subprocess.run(os.environ['SHELL'])                                                    
        else:                                                        # this is the parent process fork.
            server.app.config[f'{ns}_fd'] = fd 
            server.app.config[f'{ns}_child_pid'] = child_pid
            set_winsize(fd, 50, 50)
            server.socketio.start_background_task(read_and_forward_pty_output, server, ns)
    
    @server.socketio.on("pty-input", namespace=ns)
    def pty_input(data):
        if server.app.config[f'{ns}_fd']:
            os.write(server.app.config[f'{ns}_fd'], data["input"].encode())
        
    @server.socketio.on("resize", namespace=ns)
    def resize(data):
        if server.app.config[f'{ns}_fd']:
            set_winsize(server.app.config[f'{ns}_fd'], data["rows"], data["cols"])

def check_environment_variable(var, default):
    try:
        os.environ[var]
        return True
    except KeyError as e:
        if default is not None:
            os.environ[var] = default
            return True
        else:
            return False

def check_environment_variables(required_vars):
    needed = []
    for var, default in required_vars.items():
        if not check_environment_variable(var, default):
            needed.append(var)
    return needed    