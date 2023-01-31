import mysql.connector

# Enter your db password
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "",
)

my_cursor = mydb.cursor()

# Change database name to whatever you want or keep the same
my_cursor.execute("CREATE DATABASE social")


