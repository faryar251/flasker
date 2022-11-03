# # needs to be run just once 

# import mysql.connector

# mydb = mysql.connector.connect(
#     host='localhost',
#     user='root',
#     passwd=whatever_password
# )

# cur = mydb.cursor()

# query1 = 'CREATE DATABASE IF NOT EXISTS our_users'
# query2 = 'SHOW DATABASES'
# cur.execute(query1)
# cur.execute(query2)

# for db in cur:
#     print(db)


