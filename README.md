# workbook-replication
In a scenario where packaged analysis needs to be replicated for multiple customers, this solution helps you to achieve the requirement using Tableau's Document API and REST API.


The script operates in the following manner -
1. It takes in a list of all the clients, associated schema name, associated database username, associated password, and associated site admin name that a workbook needs to be replicated for.


2. For each client, the following takes place for the base workbook and data-source (using the Document API)
  - The database schema name is modified for the current client
  - The database username is modified for the current client
  - A new copy of the workbook and data-source is created


3. For each client, the following takes place (using the REST API)
- A new site is created
- A new site administrator is created
- The workbook and data-source are published to that specific site (into the Default project), with embedded database password
