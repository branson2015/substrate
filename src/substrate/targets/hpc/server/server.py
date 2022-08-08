import argparse
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import logging
import sys

import requests
import asyncio
import threading

def create_app(config_filename=None):
    #flask app
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    app = Flask(__name__)

    if config_filename:
        app.config.from_pyfile(config_filename)
    app.config['SECRET_KEY'] = 'secret'

    @app.route('/')
    def root():
        return render_template('index.html')

    #socketio events
    socketio = SocketIO(app)

    @socketio.on('ssh-start')
    def handle_ssh_start(msg):
        emit('ssh-ready', None, broadcast=True)
        #TODO: do proxy

    @socketio.on('message')
    def handle_message(message):
        logging.debug(f'message: {message}')

    @socketio.on('connect')
    def handle_connect(message):
        logging.debug('User Connected')

    return app, socketio


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
    print('handling errorrrrr')
    return e

@nothrow(requests.exceptions.RequestException, handler)
def safeGet(*args, **kwargs):
    return requests.get(*args, **kwargs)



async def poll_ssh(host, port, timeout=1):
    res = requests.get(f'http://{host}:{port}')
    count = 1 
    while not res.ok:
        print(count)
        if count >= 10:
            return (False, res)
        await asyncio.sleep(timeout)
        res = requests.get(f'{host}:{port}')
        count += 1
    return (True, res)


def ssh_established_callback(future):
    result = future.result()
    success = result[0]
    res = result[1]
    print(f'remote ssh {"connected" if success else "not connected"}')



def cli():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--host', type=str, default='127.0.0.1')
    parser.add_argument('-p', '--port', type=int, default=8028)
    parser.add_argument('-d', '--debug', action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()
    return vars(args)

async def run_server(host, port, debug):
    app, socketio = create_app()
    socketio.run(app, host=host, port=port, debug=debug)

async def main(host, port, debug):
    loop = asyncio.get_running_loop()
    
    ssh_task = loop.create_task(poll_ssh(host, port))
    ssh_task.add_done_callback(ssh_established_callback)

    server_task = loop.create_task(run_server(host, port, debug))

if __name__ == "__main__":
    args = cli()
    asyncio.run(main(**args))
