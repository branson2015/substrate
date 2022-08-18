from flask import Flask, render_template, request
from flask_socketio import SocketIO
import logging
import sys
import os
import signal

from utils import *

#logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def commands(server):
    @server.app.route('/start', methods=['POST'])
    def start():
        if server.substrate_pid is not None:
            return

        data = request.json
        tool = data['tool']
        execPath = tool
        p = subprocess.Popen(execPath)
        server.substrate_pid = p.pid

    @server.app.route('/restart')
    def restart():
        shutdown()
        start()
    
    @server.app.route('/shutdown')
    def shutdown():
        if server.substrate_pid:
            os.kill(server.substrate_pid, signal.SIGTERM) #or signal.SIGKILL 

    @server.app.route('/scale')
    def scale():
        pass

class Server:
    def __init__(self):
        template_dir = os.path.abspath('../templates')
        self.app = Flask(__name__, template_folder=template_dir)
        self.app.config['SECRET_KEY'] = 'secret'
        self.socketio = SocketIO()
        self.socketio.init_app(self.app)
        self.substrate_pid = None
    
    def run(self, *args, **kwargs):
        return self.socketio.run(self.app, *args, **kwargs)

    def add(self, callback, *args, **kwargs):
        callback(self, *args, **kwargs)

def main():
    required_vars = {
        'REMOTE_ARB_DEBUG': 'True',                 # debug flag for arbitration server
        'REMOTE_HOST'     : None,                   # which host we will host on
        'REMOTE_ARB_PORT' : None,                   # which port we will host on
    }


    #remove me
    required_vars['REMOTE_HOST'] = '127.0.0.1'
    required_vars['REMOTE_ARB_PORT'] = '8031'



    needed_vars = check_environment_variables(required_vars)
    if len(needed_vars) != 0:
        print("Required Environment Variables unset")
        print("Set the following Environment Variables: ")
        print(needed_vars)
        return
    
    host = os.environ['REMOTE_HOST']
    port = os.environ['REMOTE_ARB_PORT']
    debug = os.environ['REMOTE_ARB_DEBUG']

    server = Server()
    server.add(socketio_pty, '/pty2')
    server.add(commands)
    server.add(routes)
    server.run(host=host, port=int(port), debug=True if debug == 'True' else False)

if __name__ == "__main__":
    main()
