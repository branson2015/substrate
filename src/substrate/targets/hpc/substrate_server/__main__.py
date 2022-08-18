import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--server')
    args, _ = parser.parse_known_args()
    server = args.server

    if server == 'intermediate':
        from mediator_server.server import main as mediator_main
        mediator_main()
    elif server == 'remote':
        from remote_server.server import main as remote_main
        remote_main()