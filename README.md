# COM2020-TeamProject

## Local Setup for Dev Database on Windows:

- Uses WSL and Docker to run a PostgreSQL server
- Open Powershell as Administrator
- Run 'wsl --status'
- If it is installed it shows the default version, or if it is not found then we will install it:

Run the following to install WSL (You may be told to restart your PC during the process):

- wsl --install
- Ubuntu will open after reboot and then you can create your linux username and password eg. 'John', 'Test123'
- To ensure WSL 2 is enabled run - 'wsl --set-default-version 2'
- Run 'wsl --status' and it should say Default Version: 2

Run the following to install Docker:

- Download Docker Desktop for Windows
- During the install enable 'Use WSL 2 instaed of Hyper-V'
- Finish the install and reboot if prompted
- Open Docker Desktop to start the service (Don't worry about logging in)
- Open Docker Desktop -> Settings -> Resources -> WSL Integration
- Enable 'Enable integration with my default WSL distro'
- Click Apply & Restart

Verify Docker and WSL working:

- Open PowerShell:
- Run 'docker version'
- Then run 'docker run hello-world' - This should give you a welcome message

## Docker Commands:

Start the container:
'docker compose up -d dev_db'

Stop the container but keep the data:
'docker compose down'

Stop the container + delete all data (full reset)
'docker compose down -v'

Connect with psql inside the container:
'docker exec -it com2020-dev-db psql -U postgres -d com20200_dev'
