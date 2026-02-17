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

## Flask Migrate commands:

To setup a fresh database to have the correct tables
'flask db upgrade'

To create a new migration when a table has been altered or created
'flask db migrate -m "Message here"'

## Deployment on EC2 commands

Stop & Remove everything INCLUDING ALL DATA
'docker compose -f docker-compose.prod.yml down -v'

Rebuild the containers from scratch
'docker compose -f docker-compose.prod.yml build --no-cache'

Start the new containers
'docker compose -f docker-compose.prod.yml up -d'

Verify everything is running
'docker compose -f docker-compose.prod.yml ps'

Swap to the server/ directory and then fun 'flask db upgrade'

2 Docker containers:

- One runs the backend using gunicorn to serve the Flask API
- One runs the postgresql server which hosts the database

## Frontend deployment

On desktop:
'npm run build'

Use scp to copy the dist/ contents over to the EC2 instance
'scp -i "C:\Users\{USERNAME}\.ssh\id_ed25519" -r dist/\* ubuntu@18.133.229.114:/var/www/frontend/'

Move from temp to frontend
sudo mv ~/temp/\* /var/www/frontend/

Change owner of /var/www/frontend folder and files to www-data
'sudo chown -R www-data:www-data /var/www/frontend'

Add permissions
'sudo find /var/www/frontend -type d -exec chmod 755 {} \;'
'sudo find /var/www/frontend -type f -exec chmod 644 {} \;'

Test nginx
sudo nginx -t

Reload nginx
sudo systemctl reload nginx

Trace backend logs:
docker compose -f docker-compose.prod.yml logs -f backend

curl -i -X POST http://127.0.0.1:8000/api/user/login
