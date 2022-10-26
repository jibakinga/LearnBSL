# -*- coding: utf-8 -*-
"""
Created on Sat Dec 18 20:19:53 2021

@author: MinahilF
"""

from mysql import connector #Imports sql connector
import os
from dotenv import load_dotenv #Access env file


#Load environment variables
load_dotenv()

#Object to create database
class C_LandmarksDatabase:

    
    def __init__(self):
        #Create database connection
        
        ##Database details
        self.host = os.getenv("MYSQL_HOST")
        self.username = os.getenv("MYSQL_USERNAME")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.database = "landmarks_database"
        
        self.db_connection = connector.connect(host=self.host,
                                               user=self.username, 
                                               password= self.password)
        
        #Create a database cursor object
        self.db_cursor = self.db_connection.cursor()
        
        
    #Creates database called landmark_database
    def create_database(self):
        try:
            #Create database if doesn't exist
            ##Database is called "landmarks_database"
            ###SQL COMMAND
            create_db = f'''CREATE DATABASE IF NOT EXISTS {self.database}''' 
            self.db_cursor.execute(create_db)     
             
        except:
            print("ERROR: Database could not be created")
            
        finally:
            #Close cursor and connection. Otherwise they'd be out of sync.
            self.db_cursor.close()
            self.db_connection.close()    


    #Create tables within database
    def create_tables(self):
        try:
            #Creates connection to database
            self.db_connection = connector.connect(host= self.host,
                                                user= self.username,
                                                password=self.password,
                                                database = self.database
                                                )
            
            
            #Create a database cursor object
            self.db_cursor = self.db_connection.cursor(buffered = True) #(buffered = True)
            
            #Create tables within the database
            
            ###Word 50 means that a max of 50 letters/digits can be stored 
            ####SQL COMMAND
            create_tbl_words = '''
                                CREATE TABLE Words_tbl (
                                                        WordID INT NOT NULL AUTO_INCREMENT,
                                                        Word VARCHAR (50) NOT NULL,
                                                        VidPairs SMALLINT NOT NULL, 
                                                        Picture_path VARCHAR (250),
                                                        Description VARCHAR (250),
                                                        PRIMARY KEY (WordID)
                                                        )''' 
            
            self.db_cursor.execute(create_tbl_words)
            
            ##Create all other tables
            ###Primary key is a composite key which is made of WordID, VidNo, and FrameNo
            ###WordID is a foriegn key
            ####All other columns are for the coordinates corresponding to the attributes
            
            #Tables to be added to the database + no. of coords for each attribute
            table_details = {"Face_X_tbl":468, 
                             "Face_Y_tbl":468, 
                             "Face_Z_tbl":468, 
                             "Pose_X_tbl":33, 
                             "Pose_Y_tbl":33, 
                             "Pose_Z_tbl":33,
                             "Pose_Vis_tbl":33,
                             "RH_X_tbl":21,
                             "RH_Y_tbl":21,
                             "RH_Z_tbl":21,
                             "LH_X_tbl":21,
                             "LH_Y_tbl":21,
                             "LH_Z_tbl":21}
            
            for table_name in table_details: #Loop through list of table names
                
                #Create tables with the standard primary keys as those are the same for all tables
                create_tbl = f'''CREATE TABLE {table_name} (
                                                                        WordID INT NOT NULL,
                                                                        VidNo INT NOT NULL,
                                                                        FrameNo INT NOT NULL,
                                                                        FOREIGN KEY (WordID) REFERENCES                 Words_tbl(WordID) ON DELETE CASCADE,
                                                                        PRIMARY KEY (WordID,VidNo,FrameNo)
                                                                    )''' 
                self.db_cursor.execute(create_tbl)
                
                #Add the number of columns since number of columns varies.
                ##No. of columns is the corresponding value to the table name in the dictionary
                for col_no in range (table_details[table_name]):
                        add_cols = f'''ALTER TABLE {table_name} ADD Coord{(col_no+1)} FLOAT NOT NULL'''
                        self.db_cursor.execute(add_cols)

        except:
            print("ERROR: Tables could not be created")

    
    #Adds records to words table
    def add_rec_words(self):
        try:
            words = ("a", "thankyou") #List of words that will be detected initially

            for word in words:  #For each word
                #Add records to the word table
                
                ##SQL COMMAND
                add_rec = '''
                            INSERT INTO Words_tbl (Word,VidPairs)
                            VALUES (%s,%s)
                            '''
                self.db_cursor.execute(add_rec,(word.lower(),0,)) #Add lowercase words to prevent distinguishment between same words of different cases
            self.db_connection.commit() #Save changes
    
        except:
            print("ERROR: Records could not be added")
        
        finally:
            #Close cursor and connection. Otherwise they'd be out of sync.
            self.db_cursor.close()
            self.db_connection.close()  

class C_EditLandmarkDatabase:
    def __init__(self):
        
        self.host = os.getenv("MYSQL_HOST")
        self.username = os.getenv("MYSQL_USERNAME")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.database = "landmarks_database"
        
        #Creates connection to database
        self.db_connection = connector.connect(host= self.host,
                                               user= self.username,
                                               password=self.password,
                                               database = self.database
                                            )
        
        #Create a database cursor object
        self.db_cursor = self.db_connection.cursor() 
        
    #Get list of all landmark tables in database
    def get_tables(self):
        self.db_cursor.execute("SHOW TABLES")
        results = self.db_cursor.fetchall() 
    
        #Gets tuple of tables in the database (since constant) and removes the words_tbl result
        return tuple([result[0] for result in results if result[0] != "words_tbl"])
        
    
    #Reset auto increment field
    def reset_auto_increment(self, table, auto_increment_field):
        #Get max auto increment number (in the situation where the max was deleted or all words were deleted)
        self.db_cursor.execute(f"SELECT MAX({auto_increment_field}) FROM {table}")
        
        max_ID = self.db_cursor.fetchall()[0][0]
        
        #Reset auto increment value to next greatest ID
        self.db_cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = {max_ID +1 if max_ID else 1}")
        
    #Delete word and corresponding details
    def delete_word(self, word):
        self.db_cursor.execute(f"DELETE FROM Words_tbl WHERE Word = '{word}'")
        self.commit_changes() # save changes
    
    #Returns a cursor connection in case cursor connection closed
    def get_cursor(self):
        return self.db_connection.cursor(buffered = True)
    
    #Save changes
    def commit_changes(self):
        self.db_connection.commit()
    
    #Close connection to database
    def close_connection(self):
        #Close connection
        self.db_cursor.close()
        self.db_connection.close()
        return


#Create database and tables
def create_database():
    database = C_LandmarksDatabase()
    database.create_database()
    database.create_tables()
    database.add_rec_words()
    
