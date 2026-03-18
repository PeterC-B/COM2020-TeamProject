from dotenv import load_dotenv

load_dotenv()
from os import getenv

from app import create_app

app = create_app()

if __name__ == '__main__':

    host_address = getenv('HOST')
    if host_address is None:
        raise ValueError("HOST environment variable is not set.")

    backend_port = getenv('BACKEND_PORT')
    if backend_port is None:
        raise ValueError("BACKEND_PORT environment variable is not set.")
    
    if not backend_port.isdigit():
        raise ValueError("BACKEND_PORT environment variable must be a valid integer.")
    else:
        backend_port = int(backend_port)
    
    debug_mode = getenv('DEBUG')
    if debug_mode is None:
        raise ValueError("DEBUG environment variable is not set.")

    if debug_mode.lower() == 'true':
        debug_mode = True
    elif debug_mode.lower() == 'false':
        debug_mode = False
    else:
        raise ValueError("DEBUG environment variable must be 'true' or 'false'.")
    
    reloader = getenv('DEV_RELOADER')
    if reloader == 'false':
        reloader = False
    print("Starting server with the following configuration:")
    print(f"Host: {host_address}")
    print(f"Port: {backend_port}")
    print(f"Debug mode: {debug_mode}")

    app.run(host=host_address, port=backend_port, debug=debug_mode, use_reloader=False)