import subprocess
import time
import webbrowser
import os
import sys

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


if __name__ == "__main__":
    main()