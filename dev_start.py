import subprocess
import time
import webbrowser
import signal
import sys

backend_process = None
frontend_process = None

def run_command(command, cwd=None):
    """Run a command as a subprocess."""
    return subprocess.Popen(
        command,
        cwd=cwd,
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr
    )


def wait_for_db():
    """Wait for Docker container health."""
    print("Waiting for database to become healthy...")

    while True:
        result = subprocess.run(
            "docker inspect --format='{{.State.Health.Status}}' com2020-dev-db",
            shell=True,
            capture_output=True,
            text=True
        )

        if "healthy" in result.stdout:
            print("Database is healthy.")
            break

        time.sleep(2)


def main():
    global backend_process, frontend_process

    # Catch Ctrl+C
    signal.signal(signal.SIGINT, handle_signal)

    
    print("Starting Docker...")
    subprocess.run("docker compose up -d", shell=True, check=True, cwd="server")

    wait_for_db()

    print("Starting backend server...")
    backend = run_command("py -m server.run")
    
    time.sleep(5)

    print("Starting frontend...")
    frontend = run_command("npm run dev", cwd="client")

    time.sleep(3)
    webbrowser.open("http://localhost:5173")

    print("Development environment started.")

    backend.wait()
    frontend.wait()

def stop():
    print("\nStopping development environment...")

    global backend_process, frontend_process

    # Stop backend
    if backend_process:
        backend_process.terminate()
        backend_process.wait()

    # Stop frontend
    if frontend_process:
        frontend_process.terminate()
        frontend_process.wait()

    # Stop docker
    subprocess.run(
        "docker compose down",
        shell=True,
        cwd="server"
    )

    print("Everything stopped.")
    sys.exit(0)


def handle_signal(sig, frame):
    stop()


if __name__ == "__main__":
    main()