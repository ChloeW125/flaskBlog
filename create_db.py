# #Create database

# #Connect to database via connector
# import mysql.connector

# mydb = mysql.connector.connect(
#     #What what we want to connect to (the local host because that is where the database is sitting)
#     host="localhost",
#     user="root",
#     passwd="56y32888",
#     )

# #Cursor is a robot that will do commands in the database for you
# #Make the cursor create a database called "our_users"
# my_cursor = mydb.cursor()
# my_cursor.execute("CREATE DATABASE our_users")

# #Display the database
# my_cursor.execute("SHOW DATABASES")
# for db in my_cursor:
#     print(db)