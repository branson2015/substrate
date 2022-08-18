from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
import logging
import sys
from datetime import datetime
import subprocess
import requests
import os

from utils import *

#logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def passthrough_handler(e):
    return e

def nothrow(exception=Exception, callback=passthrough_handler):
    def outer(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception as e:
                if callback:
                    return callback(e)
                else:
                    return None
        return inner
    return outer

def handler(e):
    return None

@nothrow(requests.exceptions.RequestException, handler)
def safeGet(*args, **kwargs):
    return requests.get(*args, **kwargs)

def dhms_from_seconds(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return (days, hours, minutes, seconds)

def poll_connect_time(server):
    while True:
        if server.cluster_connected:
            return
        #TODO: make this script plugin-able to support different job systems
        cmd = f"sbatch --test-only -A {os.environ['ACCOUNT']} -N {os.environ['NODES']} -t {os.environ['TIME']} test.slurm"
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        time = result.split()[6].decode('utf-8')
        then = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
        now = datetime.now()
        diff = then - now
        days, hours, minutes, seconds = dhms_from_seconds(diff.seconds)

        timestr = ''
        if days > 7:
            timestr = 'More than 7 days'
        else:
            timestr += f'{days} days ' if days > 0 else ''
            timestr += f'{hours}:{minutes}:{seconds}'
        
        server.socketio.emit('cluster_estimate', {"output": timestr})
        server.socketio.sleep(1)

def poll_cluster(server):
    while True:
        res = safeGet(f'http://{os.environ["REMOTE_HOST"]}:{os.environ["INTERMEDIATE_APP_PORT"]}')
        if res is not None:
            print('Cluster connected!')
            server.set_cluster_connected()
            return
        server.socketio.sleep(5)

        

def routes(server):
    @server.app.route('/')
    def root():
        return render_template('index.html')

    @server.app.route('/terminal')
    def terminal():
        return render_template('terminal.html', data={'pty': '/pty2'})

    @server.app.route('/command', methods=['GET'])
    def server_command():
        args = request.args
        command = args.get('command')
        ret = True
        match command:
            case 'kill':
                print('killing server...')
                #TODO
            case 'spawn':
                print('spawning new server...')
                #TODO
            case _:
                ret = False
        return {'executed': ret}
    
    @server.app.route('/cluster_connected', methods=['GET'])
    def cluster_connected():
        server.set_cluster_connected()

    @server.app.route('/cluster_disconnected', methods=['GET'])
    def cluster_disconnected():
        server.set_cluster_disconnected()

    @server.app.route('/cluster_down', methods=['GET'])
    def cluster_down():
        return render_template('cluster_down.html')

class Server:
    def __init__(self):
        template_dir = os.path.abspath('../templates')
        self.app = Flask(__name__, template_folder=template_dir)
        self.app.config['SECRET_KEY'] = 'secret'
        self.socketio = SocketIO()
        self.socketio.init_app(self.app)
        self.cluster_connected = False
    
    def run(self, *args, **kwargs):
        return self.socketio.run(self.app, *args, **kwargs)

    def start_background_task(self, callback, *args, **kwargs):
        self.socketio.start_background_task(callback, self, *args, **kwargs)

    def set_cluster_connected(self):
        if self.cluster_connected == True:
            return
        self.cluster_connected = True
        self.socketio.emit('cluster_connected', None, broadcast=True)
        # set up pty2 routes
        # server.add(socketio_pty, '/pty1')
    
    def set_cluster_disconnected(self):
        if self.cluster_connected == False:
            return
        self.cluster_connected = False
        self.socketio.emit('cluster_disconnected', None, broadcast=True)
        # destroy pty2 routes
        # server.remove(socketio_pty, '/pty1')

    def add(self, callback, *args, **kwargs):
        callback(self, *args, **kwargs)

def main():    
    required_vars = {
        'ACCOUNT'               : None,             # -A flag       (will be moved to plugin)
        'GPU'                   : None,             # -p gpu flag   (will be moved to plugin)
        'TIME'                  : None,             # -t flag       (will be moved to plugin)
        'NODES'                 : None,             # -N flag       (will be moved to plugin)
        'INTERMEDIATE_ARB_DEBUG': 'True',             # debug flag for arbitration server
        'INTERMEDIATE_HOST'     : '127.0.0.1',      # which host we will host on
        'INTERMEDIATE_ARB_PORT' : '8029',             # which port we will host on
        'REMOTE_HOST'           : '127.0.0.1',      # which host the cluster will be on
        'INTERMEDIATE_APP_PORT' : '8028',             # which port the cluster will be on
    }
    
    needed_vars = check_environment_variables(required_vars)
    if len(needed_vars) != 0:
        print("Required Environment Variables unset")
        print("Set the following Environment Variables: ")
        print(needed_vars)
        return
    
    host = os.environ['INTERMEDIATE_HOST']
    port = os.environ['INTERMEDIATE_ARB_PORT']
    debug = os.environ['INTERMEDIATE_ARB_DEBUG']

    server = Server()
    
    server.add(routes)
    server.add(socketio_pty, '/pty1')

    #server.start_background_task(poll_connect_time)
    #server.start_background_task(poll_cluster)

    server.run(host=host, port=int(port), debug=True if debug == 'True' else False)

if __name__ == "__main__":
    main()
