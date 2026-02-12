# COM2020 - TeamProject

## Team Name: Ctrl-Alt-Elite

## Team members and contributions:

### Charlotte Beardsall
#### Role: Project Lead

Responsibilites:
 - Creating the scrum board
 - Organising group responsibilities and things to do
 - Managing the team
 - Creating the ERD
 - Creating the location and mission progress models
 - Compiling the meeting minutes into a document
 - Creating the risk register document

### Max Chambers
#### Role: Technical Lead

Responsibilites:
 - Organising the team with technical aspects and bringing the code together
 - Started with finding OSMNx for creating and fetching maps for use
 - Creating the edges, nodes, missions and user account database models
 - Creating functions to run the algorithms created by James
 - Adding the coding documentation to the report
 - Creating helper functions to link the front and back-ends together
 - Finalised the scoring / weighting algorithms for routing

### Peter Compton-Burnett
#### Role: Software Engineer

Responsibilites:
 - Creating the VueJS app for the front-end
 - Helping to link the back-end code into the front-end
 - Creating the Docker container and helping implement the database
 - Initialising the front-end code
 - Created the file structure and organised the files into it

### James Ellis
#### Role: Routing Algorithms and Testing

Responsibilites:
 - Created the routing algorithms for use
   - Yens
   - Dijkstra
   - A-Star
 - Helped create the scoring / weighting algorithms
 - Created 111 automated testing algorithms for the back-end
 - Created a confusion matrix for the testing suite
 - Created endpoints
 - 

### Sophie Barrell
#### Role: UI / UX Designer

Responsibilites:
 - Created the initial website design aesthetics
 - Created the demo slides
   - The Problem
   - Our Solution
   - How it works
   - Major Risks
   - Plans for sprint 2
 - Explored Tailwind CSS for possible use in our program
 - Writing CSS files for use on the front-end

### Hayley Gray
#### Role: Documentation and Communication

Responsibilites:
 - Created the report
   - Executive Summary
   - Prioritised Requirements
   - Evaluation evidence
   - Sprint 2 Plan
 - Communicating with the team to help get everything sorted
 - Created the Ethical and Legal Considerations document
 
### Eleanor Breheny
#### Role: Development / Operations Engineer

Responsibilites:
 - Create the initial mission needed for sprint 1
 - Using Amazon Web Services (AWS) to get a deployable version
   - Created an AWS instance for deploying our website
   - Compiled our project into AWS to be deployed by it

## File Structure:

## Breakdown of each main project part
### Contents:
1. [Algorithms](#algorithms)
2. [Routing](#routing)
3. [Database](#database)
4. [Scoring / Weighting](#scoring--weighting)
5. [Deployment](#deployment)

### Shortest Path Algorithms:
#### Assignees: James
We decided to use some standard routing algorithms to calculate the shortest paths between the two selected points. James was tasked with looking into this and he chose: Yen's Algorithm, Dijkstra's Algorithm and A-Star Algorithm. These were implemented as follows:

- Dijkstra's Algorithm
  - Dijkstra's algorithm uses weights based on factors (like length of the edge, safety, greenery etc.) to calculate the shortest path using a breadth-first format.
- Yen's Algorithm
  - Yen's algorithm uses our Dijkstra's shortest path algorithm as well as a heuristic function to calculate k shortest paths (k in our case would be 3).
- A-Star Algorithm
  - The A-Star (A*) algorithm also uses a heuristic function to combine the best aspects of Dijkstra's algorithm, while including the best parts of a greedy best-first search.

In light of this, James chose to only use Yen's algorithm for sprint 1, as it allows for the creation of 3 shortest routes without having to run the function multiple times.

### Routing:
#### Assignees: Max, James
Max started off with looking at OpenSteetMap Networks (OSMnx) which allowed us to create a map view and download all of the edges and nodes for our chosen spot into CSV files for future use. It also allows us to find all of the nearby features that are needed for our scoring, including:

 - Lighting
 - Places you can drink in
 - Greenery
 - The distance of each edge
 - The amenities that act as our key nodes to go to and from

OSMnx also allows us to generate the geometry for each edge and node, which is useful for generating our map data inside our website.

Eventually we just use OSMnx to generate the necessary files for our project, and don't use it for anything else.

### Database: 
#### Assignees: Max, Peter, Charlotte
Peter started this off by creating a Docker container using Postgres SQL to store our information in, which can be hosted using AWS so would be ideal for our project. Charlotte then created an Entity Relationship Diagram for our data tables and planned out the relationships. Peter initially created the nodes and edges tables using Flask SQL. Max then finished off the edges and nodes table, and created the missions model. Charlotte then completed the mission_progress and location models with appropriate relationships as per her ERD.

Max then tested the SQL with Docker implementation and made sure the models worked well.

### Scoring / Weighting:
#### Assignees: James, Max


### Deployment
#### Assignees: Eleanor, Peter

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