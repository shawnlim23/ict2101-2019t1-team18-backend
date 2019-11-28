# ict2101-Amble-backend
Amble's backend REST API  

REST API + MariaDB database  
Using Python3 w/ Flask and pymysql

# How to Run  
## Requirements
1) Python 3+  
2) Mysql Server/MariaDB Server  

### Required Python Packages
[Flask](https://pypi.org/project/Flask/)  
[PyMySQL](https://pypi.org/project/PyMySQL/)  
or use the below code in a terminal  
`pip install -r requirements.txt`
  
## Setup
### Setting up MariaDB (Also works with MySQL)  
1) Set up a MariaDB server ([Instructions](https://www.tutorialspoint.com/mariadb/mariadb_installation.htm))  
2) Create a database in the server  
3) Run the database_init.sql and views.sql files in order. They are located in the DBStuff directory  
4) Modify the access credentials in the creds.ini under [CREDENTIALS] to point to the SQL server
  
### Setting up SMTP
1) Create a gmail account
2) Enable the "Allow Less Secure App Access" setting ([Instructions](https://support.google.com/accounts/answer/6010255))
3) Modify the access credentials in the creds.ini file under [SMTP] to access the SMTP server

### Running the Flask Server
1) Run the server by running the server.py file in python

## Enabling access
1) Ensure ports 5000(Flask server), and 3306(SQL server) are allowed through the firewall
2) For remote access, ensure those ports are also port forwarded correctly through the network gateway
An active server URL can be found in the documentation  

# Documentation
[API Documentation](https://docs.google.com/document/d/1YnJoDLhQgFwOwnHlbMjkgAQh_Wkc6BzzvwpF8y2Znd0/edit?usp=sharing)
