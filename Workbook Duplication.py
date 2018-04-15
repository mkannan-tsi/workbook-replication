from tableaudocumentapi import Workbook
from tableaudocumentapi import Datasource
from tableaudocumentapi import Connection
import MySQLdb
import tableauserverclient as TSC
import time

###Retrieving lookup table###
uniqueField = []
schema = []
db_username = []
db_password = []
server_username = []
counter = 0

###Getting details about the duplication###
db = MySQLdb.connect(host="server",    
                     user="username",         
                     passwd="password",  
                     db="dbname")       
cur = db.cursor()
cur.execute("SELECT uniqueField, schema, DB_Username, DB_Password, Server_Username FROM tablename")

for row in cur.fetchall():
    uniqueField.append (row[0])
    schema.append (row[1])
    db_username.append (row[2])
    db_password.append (row[3])
    server_username.append (row[4])
    counter = counter+1
db.close()


###Creating duplicate copies of workbooks###
sourceWB = Workbook('Base.twbx')
sourceDS = Datasource.from_file('Base.tdsx')

for i in range (0,len(uniqueField)):
	for x in sourceWB.datasources:
		for j in x.connections:
	 		j.dbname = schema[i]
	 		j.username = db_username[i]
	for j in sourceDS.connections:
		j.dbname = schema[i]
		j.username = db_username[i]
	#Saving the workbook and datasource
	Workbook.save_as (sourceWB, uniqueField[i]+'.twbx')
	Datasource.save_as (sourceDS, uniqueField[i]+'.tdsx')

###Creating sites, projects and users if they don't exist, and publishing the workbooks###
server = TSC.Server('server')
tableau_auth = TSC.TableauAuth('username', 'password')

with server.auth.sign_in(tableau_auth):
    all_sites, pagination_item = server.sites.get()

site_check = 0
for i in range (0, len(uniqueField)):
	###Ignoring process if site already exists###
	for site in all_sites:
		if site.name == uniqueField[i]:
			site_check = 1
			break

	###Creating site and user###
	if site_check == 0:
		with server.auth.sign_in(tableau_auth):
			new_site = TSC.SiteItem(name=uniqueField[i], content_url=uniqueField[i].replace(" ", ""))
			server.sites.create(new_site)
		time.sleep (0.5)	
		with server.auth.sign_in(tableau_auth):
		    all_sites, pagination_item = server.sites.get()
		for site in all_sites:
			if site.name == uniqueField[i]:
				tableau_auth.site_id = site.content_url
				break
		with server.auth.sign_in(tableau_auth):
		    user = TSC.UserItem(server_username[i],'SiteAdministrator')
		    user = server.users.add(user)
		    user = server.users.update(user, 'password')

        #Getting the default project and publishing workbook and datasource###
        project_id = ''
        time.sleep (1)
        with server.auth.sign_in(tableau_auth):
	        all_projects, pagination_item = server.projects.get()
	        for project in all_projects:

	        	if project.name == 'Default':
	        		project_id = project.id

    	new_workbook = TSC.WorkbookItem(project_id)
    	new_datasource = TSC.DatasourceItem(project_id)
    	credentials = TSC.ConnectionCredentials (db_username[i], db_password[i], embed=True)

    	with server.auth.sign_in(tableau_auth):
    		server.datasources.publish(new_datasource, uniqueField[i] + ".tdsx", TSC.Server.PublishMode.Overwrite, credentials)
    		server.workbooks.publish(new_workbook, uniqueField[i] + ".twbx", TSC.Server.PublishMode.Overwrite, credentials)

	site_check = 0		
	

# print "The workbook connections have been updated. Please open the newly created workbook to test."