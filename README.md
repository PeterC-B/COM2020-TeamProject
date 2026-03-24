# COM2020 - TeamProject

## Team Name: Ctrl-Alt-Elite

## Team members and contributions:

### Charlotte Beardsall
#### Role: Project Lead

Responsibilites:
 - Created and managed the scrum board
 - Organised group meetings twice a week
 - Managed the teams responsibilities
 - Assigned tasks to group members based on individual stregths and availability
 - Created the ERD
 - Created the location, mission progress, and user account models for the database
 - Compiled the meeting minutes into a document
 - Created the risk register document
 - Created edit / create mission view

### Max Chambers
#### Role: Technical Lead

Responsibilites:
 - Organised the team with technical aspects and bringing the code together
 - Started with finding OSMNx for creating and fetching maps for use
 - Created the edges, nodes, missions and user account database models
 - Created functions to run the algorithms created by James
 - Added the coding documentation to the report
 - Created helper functions to link the front and back-ends together
 - Finalised the scoring / weighting algorithms for routing
 - Added features to improve functionality:  
    - Map auto-centres on chosen location
    - Able to select a route and other routes are greyed out
    - Added pop-up box to show the context of edges
 - Linked leaderboard to database
 - Created handover pack: deployment & operations, maintenance & troubleshooting

### Peter Compton-Burnett
#### Role: Software Engineer

Responsibilites:
 - Created the VueJS app for the front-end
 - Helped to link the back-end code into the front-end
 - Created the Docker container and helping implement the database
 - Initialised the front-end code
 - Created the file structure and organised the files into it
 - Created handover pack: deployment & operations, maintenance & troubleshooting
 - Created analytics views with export functions across the system

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
 - Created forgotten password view and functionality
 - Added 200 pre-seeded route queries
 - Optimised area selection
 - Created handover pack: deployment & operations, maintenance & troubleshooting

### Sophie Barrell
#### Role: UI / UX Designer

Responsibilites:
 - Created the initial website design aesthetics
 - Created the demo slides:
   - The Problem
   - Our Solution
   - How it works
   - Major Risks
   - Plans for sprint 2
 - Explored Tailwind CSS for possible use in our program
 - Wrote CSS files for use on the front-end 
 - Created the final slides:
   - Recap of the problem
   - What we delivered in sprint 2
   - Demonstration of product
   - Deployment handover docs
   - Evaluation
   - Next steps


### Hayley Gray
#### Role: Documentation and Communication

Responsibilites:
 - Wrote the Sprint 1 report
   - Executive summary
   - Prioritised requirements
   - Evaluation evidence
   - Sprint 2 Plan
 - Communicated with the team to help get everything sorted
 - Created the Ethical and Legal Considerations document
 - Wrote the Sprint 2 final report
   - Executive summary
   - Problem framing and project requirements
   - Requirements and success criteria
   - System architecture and design
   - Algorithm design
   - Prototype implementation and analytics 
   - Ethics, legal, and licencing considerations
   - Testing evidence
   - Final evaluation
 
### Eleanor Breheny
#### Role: Development / Operations Engineer

Responsibilites:
 - Create the initial mission needed for sprint 1
 - Using Amazon Web Services (AWS) to get a deployable version
   - Created an AWS instance for deploying our website
   - Compiled our project into AWS to be deployed by it
 - Wrote tests for the front-end


<br>

## File Structure:

## Breakdown of each main project part
### Contents:
1. [Algorithms](#algorithms)
2. [Routing](#routing)
3. [Database](#database)
4. [Scoring / Weighting](#scoring--weighting)
5. [Deployment](#deployment)

---

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

<br>

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

<br>

### Database: 
#### Assignees: Max, Peter, Charlotte
Peter started this off by creating a Docker container using Postgres SQL to store our information in, which can be hosted using AWS so would be ideal for our project. Charlotte then created an Entity Relationship Diagram for our data tables and planned out the relationships. Peter initially created the nodes and edges tables using Flask SQL. Max then finished off the edges and nodes table, and created the missions model. Charlotte then completed the mission_progress and location models with appropriate relationships as per her ERD.

Max then tested the SQL with Docker implementation and made sure the models worked well.

<br>

### Scoring / Weighting:
#### Assignees: James, Max
We started by coming up with the indicators that we would use for the for the routing weights:
1. Proximity to green spaces
2. Proximity to places you can drink
3. Whether the edges are lit or not
4. Distance of the node
5. Surface quality of each node

<br>

We then grouped these into the 3 route preferences that the user can adjust using sliders on the route selection page:
1. Safety
   - Lighting
   - Proximity to places you can drink
2. Greenery
   - Proximity to green spaces
3. Speed
   - Time
   - Surface quality
  
<br>
For each map load, the weights are calculated based on the indicators and the weight that the user gives to each of the sliders. This is then multiplied by the distance of the edges which calculates the new weights.

<br>

### Deployment
#### Assignees: Eleanor, Peter
Eleanor was originally put in charge of creating the AWS deployment. However, as more and more was needed to be added, Peter assisted her as he had prior knowledge of the skills needed.

We use an S3 bucket for statically serving the frontend, which primarily uses VueJS, alongside an EC2 Linux instance, for the backend and database.

### DISCLAIMER:
Any crime or criminal data that may have been inferred by this project is 100% fake and has been fabricated to add a sense of realism for this project only.
