import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['institutions', 'positions', 'experiences', 'skills','feedback', 'users']
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row
    
    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        # create array of sql files sorted by dependency
        sql_files = [
            'institutions.sql',
            'positions.sql',
            'experiences.sql',
            'skills.sql',
            'feedback.sql',
            'users.sql'
        ]

        # create array of sql files sorted by dependency
        csv_files = [
            'institutions.csv',
            'positions.csv',
            'experiences.csv',
            'skills.csv'
        ]

        tables  = ['institutions', 'positions', 'experiences', 'skills','feedback', 'users'] 
        if purge:
            for table in tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")

        # Loop through array and execute each file to create tables
        for sql_file in sql_files:
            # open joined pathname file
            with open(os.path.join(data_path, 'create_tables', sql_file), 'r') as file:
                sql_script = file.read()
                self.query(sql_script)

        for csv_file in csv_files:
            table = csv_file.split('/')[-1].split('.')[0]
            with open(os.path.join(data_path, 'initial_data', csv_file), 'r') as file:
                reader = csv.DictReader(file)
                columns = reader.fieldnames
                
                # Transform each row dictionary to a list of values in the order of columns
                data = [[None if row.get(col) == 'NULL' else row.get(col, None) for col in columns] for row in reader]
                
                # Insert rows into the table
                self.insertRows(table, columns, data)

        self.getResumeData()        


    def insertRows(self, table='table', columns=['x', 'y'], parameters=[['v11', 'v12'], ['v21', 'v22']]):
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        # Create Insert query string
        query = f'INSERT INTO {table} ({columns_str}) VALUES ({placeholders})'
        
        for param in parameters:
            if len(param) != len(columns):
                # Mismatched column count
                continue
            
            param_tuple = tuple(value if value is not None else None for value in param)
            try:
                self.query(query, param_tuple)
            except mysql.connector.errors.ProgrammingError as e:
                # Insertion error
                print(f"Failed to insert {param_tuple} into {table}. Error: {e}")


    def getResumeData(self):
        # Fetch data from each table in dependency order
        institutions_data = self.query("SELECT * FROM institutions")
        positions_data = self.query("SELECT * FROM positions")
        experiences_data = self.query("SELECT * FROM experiences")
        skills_data = self.query("SELECT * FROM skills")

        # Organize into hierarchical layers. Convert skills data into a nested dictionary by experience_id
        skills_by_experience = {}
        for skill in skills_data:
            experience_id = skill['experience_id']
            if experience_id not in skills_by_experience:
                skills_by_experience[experience_id] = {}
            skills_by_experience[experience_id][skill['skill_id']] = {
                'name': skill['name'],
                'skill_level': skill['skill_level']
            }

        # Organize experiences with nested skills by position_id
        experiences_by_position = {}
        for experience in experiences_data:
            position_id = experience['position_id']
            experience_id = experience['experience_id']
            if position_id not in experiences_by_position:
                experiences_by_position[position_id] = {}
            experiences_by_position[position_id][experience_id] = {
                'name': experience['name'],
                'description': experience['description'],
                'hyperlink': experience['hyperlink'],
                'start_date': experience['start_date'] if experience['start_date'] else None,
                'end_date': experience['end_date'] if experience['end_date'] else None,
                'skills': skills_by_experience.get(experience_id, {})  # Nested skills
            }

        # Organize positions with nested experiences by inst_id
        positions_by_institution = {}
        for position in positions_data:
            inst_id = position['inst_id']
            position_id = position['position_id']
            if inst_id not in positions_by_institution:
                positions_by_institution[inst_id] = {}
            positions_by_institution[inst_id][position_id] = {
                'title': position['title'],
                'responsibilities': position['responsibilities'],
                'start_date': position['start_date'] if position['start_date'] else None,
                'end_date': position['end_date'] if position['end_date'] else None,
                'experiences': experiences_by_position.get(position_id, {})  # Nested experiences
            }

        # Organize institutions with nested positions
        result = {}
        for institution in institutions_data:
            inst_id = institution['inst_id']
            result[inst_id] = {
                'type': institution['type'],
                'name': institution['name'],
                'department': institution['department'],
                'address': institution['address'],
                'city': institution['city'],
                'state': institution['state'],
                'zip': institution['zip'],
                'positions': positions_by_institution.get(inst_id, {})  # Nested positions
            }

        return result

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password', role='user'):
        # Check if the email already exists
        existing_user = self.query("SELECT * FROM users WHERE email = %s", (email,))
        if existing_user:
            return {'success': 0, 'message': 'User already exists'}
        if '@' not in email:
            return {'success': 0, 'message': '`${email}` missing an @'}

        # Encrypt the password
        encrypted_password = self.onewayEncrypt(password)

        # Insert the new user into the database
        try:
            self.query(
                "INSERT INTO users (role, email, password) VALUES (%s, %s, %s)",
                (role, email, encrypted_password)
            )
            return {'success': 1, 'message': 'User created successfully'}
        except Exception as e:
            return {'success': 0, 'message': f'Error creating user: {e}'}

    def authenticate(self, email='me@email.com', password='password'):
        # Encrypt the provided password
        encrypted_password = self.onewayEncrypt(password)

        # Check if the user exists with the matching email and encrypted password
        user = self.query(
            "SELECT * FROM users WHERE email = %s AND password = %s",
            (email, encrypted_password)
        )
        
        if user:
            return {'success': 1, 'message': 'Authentication successful', 'user': user[0]}
        else:
            return {'success': 0, 'message': 'Invalid email or password'}

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message