# -*- coding: utf-8 -*-
"""
Created on Sat Dec 18 20:37:53 2021

@author: MinahilF
"""

import cv2 #For image and video processing
import numpy as np #For array manipulation

from threading import Thread#Allows multiprocessing

#For GUI creation
import tkinter as tk 
from tkinter import ttk
from PIL import ImageTk, Image

from CF_CreatingLandmarksDatabase import C_EditLandmarkDatabase
from CF_HolisticModel import C_holistic_model
from CF_Widgets import C_Label, C_Button

#Class creates user interface
class C_TrainingWidgets:
    def __init__(self, root, main, no_of_frames):
        #Database connection
        self.connection = C_EditLandmarkDatabase() #Connect to database
        self.cursor = self.connection.get_cursor() #Assign cursor to database
        
        #Gets tuple of tables in the database (since constant) and removes the words_tbl result
        self.tables = self.connection.get_tables()
            
        #Create root window
        self.root = root
        self.root.title("Training Video Collection") #Set window title
        
        #Create main frame for placing widgets
        self.main = main
        self.main.config(padx = 10, pady = 10)
        self.main.grid(row = 0, column = 0, sticky = "NSEW")
        
        #Set no_of_frames
        self.no_of_frames = no_of_frames
        
        #Set next video number
        self.vid_no = 1
        
        #Indicate whether recording is in progress
        self.record = False
           
    #Defines the function that should take place within the combobox
    def word_combo(self, event = None, word = None):
        if word: #If word is given
            self.word = word #If "<word>" is typed in, set word to the word typed in (if it is part of the added words)
        else: #Otherwise if word is selected, set word to the word selected
            self.word = self.word_drop.get() #Get the selected word from Combobox
        
        #Get the number of videos saved for the chosen word
        self.cursor.execute(f"""SELECT VidPairs
                               FROM Words_tbl
                               WHERE Words_tbl.Word = '{self.word}'""")
                               
        results = self.cursor.fetchall()
        
        #If the number of videos is 0, then:
        if results[0][0] == 0:
            self.delete_vids_entry.config(state = "disabled") #Deactivate delete record number entry (since no vids exist)
        else:
            self.delete_vids_entry.config(state = "normal") #Activate delete record number entry to allow deletion (since vids exist)
            #Activate delete recording button
            self.delete_rec_button.set_state("active") 
        
        self.vid_no = results[0][0] + 1 #Set video number of the video to be saved to current max video number +1
        
        #Set the video number label
        self.current_vid_no_label.set_text(f"{self.vid_no}") 
        
        #Activate the start recording button
        self.start_rec_button.set_state("active")
        
    #Get filtered popup menu  
    def get_popup(self):
        current = self.word_drop.get() #Get the current value in the popup
        
        #Get the list of values which start with the string typed in
        self.word_drop.config(values = [word for word in self.words if word.startswith(current)])
    
    #Check whether the word typed is in the added words as it is being typed
    def is_in_list(self, P):
        if P.lower() in self.words: #If in added words, then:
            self.start_rec_button.set_state("active") #Activate record button
            self.word_combo(word = P) #To allow current video number to be changed if the word is valid
            
        #If word is not in the list of added words
        else:
            #Since word not added (hence invalid)
            self.start_rec_button.set_state("disabled") #Disable record button
            self.delete_vids_entry.config(state = "disabled") #Dectivate delete record number entry
            self.delete_rec_button.set_state("disabled") #Disable delete rec button
        
        return True #True to allow the user to continue typing
    #Returns true
    
    #Get the list of words to show in the dropdown when it is empty
    def get_words_list(self):
        #Get all words that have been added to the database
        self.cursor.execute("SELECT Word FROM Words_tbl")
         
        #Get list of words    
        self.words = sorted([i[0].lower() for i in self.cursor.fetchall()]) #Unpack and sortlist of words since returned as a list of tuples (list comprehension)
        # ^ is used in the scenario where youre giving the option to add more words and train model
        #Words are in lowercase
        return self.words
    #Returns array of words 
     
    #Validate entry widget for number of videos to delete
    def vids_to_delete_validate(self,S, P):
        #If is a number and less than max vids, or empty
        if (S.isnumeric()) and (int(P)<self.vid_no):
            self.delete_rec_button.set_state("active") #Activate delete record button
            return True
        else:
            #If not number:
            self.delete_rec_button.set_state("disabled") #Disable button to record
            
            if (P ==""): #If the user wants to erase what they have entered
                return True
            
            #Indicate that number entered should be a number less than max videos
            tk.messagebox.showinfo(title = "Invalid entry",message = f"The number of videos to be deleted should be a number and be less than the total number of videos saved ({self.vid_no})")
            
            return False #To prevent the number from being entered
    
    #Create and add labels to main window   
    def add_widgets(self):
        #Set title
        train_title = C_Label(self.main,"Training Dataset Collection")
        train_title.set_font(font_size = 40)
        train_title.arrange_on_grid(0,0,sticky = ("WE"), columnspan = 3) 
    
        #Create a frame for the word selection
        word_frame = tk.LabelFrame(self.main) 
        word_frame.config(text = "Word selection", font=("Consolas", 10), relief = "groove", borderwidth = 3)
        word_frame.grid(row = 1, column = 0, padx = 10, pady = 10,sticky = ("WE"), columnspan = 2)
        
        #Set entry options
        
        ##LABELS
        ###Word entry label
        word_label = C_Label(word_frame,"Select word to enter:")
        word_label.arrange_on_grid(0,0)    
        
        #Create dropdown menu for list of words        
        self.word_drop = ttk.Combobox(word_frame)
        self.word_drop.config(value = self.get_words_list()) #Standard combobox with words in alphabetical order
        
        ##Combobox -> subclass of entry widget
        ##Validate entry to check the word entered every time (%P returns the value in the box after each key is pressed)
        self.word_drop.config(validate = "all", validatecommand = (self.word_drop.register(self.is_in_list), "%P")) #Validate combobox entry
        self.word_drop.config(postcommand = self.get_popup) #Menu is changed every time the dropdown is run
        self.word_drop.bind("<<ComboboxSelected>>",self.word_combo) #Run word_combo after a selection is made
        self.word_drop.config(state = "active") 
        
        self.word_drop.config(width = 25, height = 5) #Where height is the number of rows high that the pop-down list of values will be displayed
        self.word_drop.config(font=("Consolas", 12))
        self.word_drop.grid(row = 0,  padx = 10, pady = 10, column = 1, sticky = "WE")
       
        ###Current video number    
        #Video number label
        current_vid_label = C_Label(word_frame)
        current_vid_label.set_text("Current video number:")
        current_vid_label.arrange_on_grid(1, 0)
        
        #Create label for the video number of the video currently being recorded
        self.current_vid_no_label = C_Label(word_frame)
        self.current_vid_no_label.arrange_on_grid(1, 1)
        
        ##Show how many frames are recorded per video
        frame_no_label = C_Label(word_frame, (f"{self.no_of_frames} frames are recorded per video"))
        frame_no_label.arrange_on_grid(2,0,  columnspan = 3, sticky = "WE")
    
        #Create a frame for the video deletion
        delete_frame = tk.LabelFrame(self.main) 
        delete_frame.config(text = "Delete recorded videos", font=("Consolas", 10),  relief = "groove", borderwidth = 3)
        delete_frame.grid(row = 2, column = 0, padx = 10, pady = 10,sticky = ("WE"), columnspan = 2)     
    
        #Idicate how many videos to delete
        delete_vids_label = C_Label(delete_frame)
        delete_vids_label.set_text("Choose the number of videos to be deleted:")
        delete_vids_label.arrange_on_grid(0, 0, sticky = ("WE"))
        
        #NOTE: The latest recorded videos will be deleted.
        delete_vid_note_label = C_Label(delete_frame)
        delete_vid_note_label.set_text("The latest recorded videos will be deleted")
        delete_vid_note_label.set_font(11)
        delete_vid_note_label .arrange_on_grid(row = 1 , column = 0, padx = 10, pady = 10, columnspan = 2)    
    
        #Number entry
        self.delete_vids_entry = tk.Entry(delete_frame)
        self.delete_vids_entry.config(width = 6, font = ("Consolas", 12))
        #Only accept numbers
        self.delete_vids_entry.config(validate = "key", validatecommand = (self.delete_vids_entry.register(self.vids_to_delete_validate), "%S", "%P"))
        self.delete_vids_entry.config(state = "disabled")
        self.delete_vids_entry.grid(row = 0, column = 1, padx = 10, pady = 10)
    
        #Video feed label
        #Video feed frames
        self.video_feed_label = tk.Label(self.main)
        self.video_feed_label.grid(row = 1 , column = 2, rowspan = 4, padx = 10, pady = 10)
        
        #Show if its recording or not
        self.is_recording_label = C_Label(self.main) #Is it currently recording?
        self.is_recording_label.set_text("RECORDING NOW")
        self.is_recording_label.set_font(font_size = 20, fg_colour = "#D3D3D3") #Light grey in colour
        self.is_recording_label.arrange_on_grid(row = 4 , column = 0, padx = 10, pady = 10)
        
        #Current frame number being recorded:
        self.current_frame_no_label = C_Label(self.main)
        self.current_frame_no_label.set_text("Current frame number: 01")
        self.current_frame_no_label.set_font(font_size = 15, fg_colour = "#D3D3D3") #Light grey in colour
        self.current_frame_no_label.arrange_on_grid(row = 4 , column = 1, padx = 10, pady = 10)        
         
        #Buttons
        ##Delete button
        self.delete_rec_button = C_Button(delete_frame)
        self.delete_rec_button.set_text("Delete recordings")
        self.delete_rec_button.set_command(self.delete_recording) #Link delete record button to delete_recording function
        self.delete_rec_button.arrange_on_grid(2,0,sticky =("WE"), columnspan = 2)

        
        ## Start rec button
        self.start_rec_button = C_Button(self.main)
        self.start_rec_button.set_text("Start recording")
        self.start_rec_button.set_command(self.start_recording) #Link start record button to start_recording function

        self.start_rec_button.arrange_on_grid(3,0,sticky =("WE"), columnspan = 2)
    
    #Delete recording
    def delete_recording(self):
        no_to_delete = int(self.delete_vids_entry.get()) #Get the number of records that should be deleted
        #Ask whether to delete or not
        delete = tk.messagebox.askokcancel(title = "Delete records?", message = f"{no_to_delete} recording(s) will be deleted for the word '{self.word}'", icon = "warning")
        #If they choose to delete then:
        if delete:
            #For each table
            for table in self.tables:
                #Delete records with video numbers in the range ((vid_no-1)*2 to ((vid_no-1 - number_to_delete) *2 +1)) -> The +1 is there since it is inclusive ->  The *2 is there since 2 vids per recording -> Vid_no -1 since vid number = max vid_no + 1
                delete_SQL = f"""DELETE {table}.* FROM {table}
                            JOIN words_tbl 
                            ON Words_tbl.WordID = {table}.WordID
                            AND (Words_tbl.Word = '{self.word}') 
                            AND ({table}.VidNo BETWEEN  {(2*self.vid_no - 2*no_to_delete -1)} AND {((self.vid_no - 1)*2)} )"""
                
                self.cursor.execute(delete_SQL)
            
            #Update video numbers
            self.cursor.execute(f"""UPDATE Words_tbl
                                SET VidPairs = {(self.vid_no-1-no_to_delete)}
                                WHERE Word = '{self.word}'""")
            
                    
            self.connection.commit_changes()
                
            #Indicate that records have been deleted
            tk.messagebox.showinfo(title = "Information", message = f"{no_to_delete} recording(s) deleted for the word: '{self.word}'")
        
        #Reset entry box
        self.delete_vids_entry.delete(0, tk.END) #Clear contents of entry box
        self.word_combo() #To change video number shown
    
    #Start recording
    def start_recording(self):
        self.record = True #Set recording to true
        
        #Turn the "IS RECORDING" value to red and bold
        self.is_recording_label.set_font(font_size = 20, fg_colour = "#FF0000", bold = True)
        #Set the current frame number being recorded to black
        self.current_frame_no_label.set_font(font_size = 15, fg_colour = "#000000")

        #Deactivate record button
        self.start_rec_button.set_state("disabled")        
        #Deactivate combobox
        self.word_drop.config(state = "disabled")
        
        self.delete_vids_entry.config(state = "disabled") #Deactivate delete record number entry
        self.delete_rec_button.set_state("disabled") #Disable button to record
        
    #Save recording
    def save_rec(self):
        #Prompt user to ask whether the recording should be saved or not
        ok_to_save  = tk.messagebox.askyesno("Save recording", "Recording complete. Save recording?")
        
        #If they say yes to saving it:
        if ok_to_save == True:
            
            self.cursor.execute(f"""UPDATE Words_tbl
                                SET VidPairs = {(self.vid_no)}
                                WHERE Word = '{self.word}'""")
            
            self.connection.commit_changes() #Save changes
            
            tk.messagebox.showinfo("Save status", "The recording has been saved") #Indicate that the recording was saved
        
        #If they say no
        else:
            tk.messagebox.showinfo("Save status", "The recording has been discarded") #Indicate that the recording was discarded
        
        self.connection.close_connection() #This would be done by closing the connection
            
        #Reset database connection
        self.connection = C_EditLandmarkDatabase() #Restart database connection
        self.cursor = self.connection.get_cursor() #Recreate cursor
        
        self.start_rec_button.set_state("active") #Reactivate record button
        self.word_drop.config(state = "active") #Set combobox to active so value can be changed/selected
        self.word_combo() #To change video number shown
           
    def get_recording_frame_no_label(self):
        return self.is_recording_label ,self.current_frame_no_label
        #Returns is_recording_label , current_frame_no_label
        
    def get_video_feed_label(self):
        return self.video_feed_label
        #Returns the video feed label (the label where the frames will be shown)
    
    #Get the wordID of the word selected in the combobox
    def get_wordID(self):
        self.cursor.execute(f"SELECT WordID FROM Words_tbl WHERE Word = '{self.word}'")
        wordID = self.cursor.fetchall()[0][0]
        return wordID
        #Returns the wordID of the word selected
    
    def get_vid_no(self):
        return self.vid_no
        #Returns the number of the next video to be saved
    
    def get_record_var(self):
        return self.record
        #Returns the variable indicating whether the it is currently recording or not
    
    def set_record_var(self, value):
        self.record = value
        #Set currently recording variable to true/false
    
    def get_cursor(self): #Return cursor
        return self.cursor

#Video feed object
class C_VideoFeed:
    def __init__(self,no_of_frames, vid_frame_label):
        self.no_of_frames = no_of_frames #No of frames is passed in
        self.frame_no = 0 #Initial frame number set to 0
        
        self.vid_frame_label = vid_frame_label #Video frame

        self.cap = cv2.VideoCapture(0)  #Capture video frames from camera 0
    
    #Release camera
    def release_capture(self):
        self.cap.release() #Unbind camera
          
    #Adds records to the respective table
    def add_rec(self, table, coords):
        #SQL COMMAND
        ##Record should be in string format since SQL command is a string
        ###Record should be a tuple since record data should be provided in tuple format
        
        #Execute SQL
        self.cursor.execute(f"INSERT INTO {table} VALUES {tuple(coords)}")

    #Save frame landmarks to database
    def save_landmarks_to_db(self, results, word, vid_no, frame_no):    
        #Initialise landmarks for each axis (x, y and z) with primary key values - same for x y and z
        def axis_landmark_arrays(cursor, wordID, vid_no, frame_no):
            x = np.array([wordID,vid_no,frame_no]) #list to store face x, y and z landmarks respectively
            #Duplicate x to make y and z
            y, z = x.copy(), x.copy()
            
            return x, y, z
        ##returns landmark arrrays in the order (x_landmarks, y_landmarks, z_landmarks)
        
        #Append landmarks to arrays to be saved
        def append_to_landmark_arrays(x, y, z, result):
            x = np.append(x,np.array(result.x))
            y = np.append(y,np.array(result.y))
            z = np.append(z,np.array(result.z))
            return x,y,z
            
        #Get array of face landmarks   
        x_landmarks, y_landmarks, z_landmarks = axis_landmark_arrays(self.cursor, word, vid_no, frame_no) #Initialise axis landmark arrays
        
        if results.face_landmarks:
        #If face landmarks are present then:
                
            #For each landmark in the face results
                #Appends landmark coordinates (468,) to landmarks list 
            
            for result in results.face_landmarks.landmark:
                x_landmarks, y_landmarks, z_landmarks = append_to_landmark_arrays(x_landmarks, y_landmarks, z_landmarks, result) #Append results to existing axis landmark arrays
                
        else:
        #If face landmarks absent
            x_landmarks = np.append(x_landmarks,np.zeros(468)) #No landmarks so array of 0's is added
            y_landmarks, z_landmarks = x_landmarks.copy(), x_landmarks.copy()
            
        #List of shape (471,) is returned -> this is the record to be added
            
        #Add records to tables    
        self.add_rec("Face_X_tbl",x_landmarks)
        self.add_rec("Face_Y_tbl",y_landmarks)
        self.add_rec("Face_Z_tbl",z_landmarks)
          
        #Get array of pose landmarks
        x_landmarks, y_landmarks, z_landmarks = axis_landmark_arrays(self.cursor, word, vid_no, frame_no)  #Initialise axis landmark arrays
        vis_landmarks = x_landmarks.copy() #Visibility array primary key is the same as that of x asis array
        
        if results.pose_landmarks:
        #If pose landmarks are present then        
            #For each landmark in the pose results 
                #Appends landmark coordinates (33,) to landmarks list 
            for result in results.pose_landmarks.landmark:
                x_landmarks, y_landmarks, z_landmarks = append_to_landmark_arrays(x_landmarks, y_landmarks, z_landmarks, result) #Append results to existing axis landmark arrays
                vis_landmarks = np.append(vis_landmarks,np.array(result.visibility))
               
        else:
        #If pose landmarks absent
            x_landmarks = np.append(x_landmarks,np.zeros(33)) #No landmarks so array of 0's is added
            y_landmarks, z_landmarks, vis_landmarks = x_landmarks.copy(), x_landmarks.copy(), x_landmarks.copy()
        
        #List of shape (36,) is returned -> this is the record to be added
            
        #Add records to tables
        self.add_rec("Pose_X_tbl",x_landmarks)
        self.add_rec("Pose_Y_tbl",y_landmarks)
        self.add_rec("Pose_Z_tbl",z_landmarks)
        self.add_rec("Pose_Vis_tbl",vis_landmarks)    
          
        #Get array of left hand landmarks
        
        x_landmarks, y_landmarks, z_landmarks = axis_landmark_arrays(self.cursor, word, vid_no, frame_no)  #Initialise axis landmark arrays
        
        #Since mirrored, right hand landmarks = real left hand landmarks
        if results.right_hand_landmarks:
        #If right hand landmarks are present then
            
            #For each landmark in right hand results 
                #Appends landmark coordinates (21,) to landmarks list
            
            for result in results.right_hand_landmarks.landmark:
                x_landmarks, y_landmarks, z_landmarks = append_to_landmark_arrays(x_landmarks, y_landmarks, z_landmarks, result) #Append results to existing axis landmark arrays
                
        else:
        #If right hand landmarks absent
            x_landmarks = np.append(x_landmarks,np.zeros(21)) #No landmarks so array of 0's is added
            y_landmarks, z_landmarks = x_landmarks.copy(), x_landmarks.copy()
        
        #List of shape (24,) is returned
        
        #Add records to tables
        self.add_rec("RH_X_tbl",x_landmarks)
        self.add_rec("RH_Y_tbl",y_landmarks)
        self.add_rec("RH_Z_tbl",z_landmarks)
          
        #Get array of right hand landmarks
        
        x_landmarks, y_landmarks, z_landmarks = axis_landmark_arrays(self.cursor, word, vid_no, frame_no)  #Initialise axis landmark arrays
       
        #Since mirrored, left hand landmarks = real right hand landmarks
        if results.left_hand_landmarks:
        #If left hand landmarks are present then
            
            #For each landmark in left hand results 
                #Appends landmark coordinates (21,) to landmarks list
            
            for result in results.left_hand_landmarks.landmark:
                x_landmarks, y_landmarks, z_landmarks = append_to_landmark_arrays(x_landmarks, y_landmarks, z_landmarks, result) #Append results to existing axis landmark arrays
   
        else:
        #If left hand landmarks absent
            x_landmarks = np.append(x_landmarks,np.zeros(21)) #No landmarks so array of 0's is added
            y_landmarks, z_landmarks = x_landmarks.copy(), x_landmarks.copy()
        
        #List of shape (24,) is returned
        
        #Add records to tables
        self.add_rec("LH_X_tbl",x_landmarks)
        self.add_rec("LH_Y_tbl",y_landmarks)
        self.add_rec("LH_Z_tbl",z_landmarks)    
   
    
    #Show camera feed with landmarks displayed onto the window
    def show_feed(self, widgets):
        #Show webcam feed
        ##Read camera input
        ##Success - > Frame read or not ("_" here)
        ##Frame -> Image returned in BGR ("video_frame" here)
        success, video_frame = self.cap.read()
        
        self.cursor = widgets.get_cursor() #Get cursor object
        
        if success: #If frame recorded
            #Flip video frame
            video_frame = cv2.flip(video_frame, 1) #For a selfie view
            
            #Get landmarks
            model = C_holistic_model(video_frame) #Make model object
            
            results = model.get_landmarks() #Get landmarks 
                            
            #Show landmarks onto video
            ##Reflected frame used for a selfie view
            video_frame = model.show_landmarks(results) #Display landmarks onto image
            
            frame = Image.fromarray(video_frame) #Video_frame returned from cv2 is a numpy array. This function converts it from numpy array to a CASA image which can be processed by tkinter
            frame = ImageTk.PhotoImage(image=frame)
            self.vid_frame_label.configure(image=frame) #Change frame on the feed label in the main window
            self.vid_frame_label.frame = frame
            
            #Gets the is_recording indicator, and the current frame being recorded label
            is_recording_label, current_frame_no_label = widgets.get_recording_frame_no_label()

            #If frame number is equal to number of frames: (Recording complete)
            if self.frame_no == self.no_of_frames:
                widgets.save_rec() #Ask to save recording
            
                #Reset labels to neutral
                current_frame_no_label.set_font(font_size =  15, fg_colour = "#D3D3D3") 
                is_recording_label.set_font(font_size = 20, fg_colour = "#D3D3D3")
                
            #If recording (and recording in progress):
            if widgets.get_record_var() and (self.frame_no != self.no_of_frames):
                
                current_frame_no_label.set_text(f"Current frame number: {self.frame_no+1:02d}") #Makes sure frame number is displayed in 2 digits to keep it uniform
                
                #Save landmarks from current frame into database
                ###Vid number *2 since 2 videos recorded each time
                self.save_landmarks_to_db(results, widgets.get_wordID(), widgets.get_vid_no()*2, self.frame_no)
                
                #SAVE MIRROR GESTURES AS WELL
                #Flip video frame
                video_frame = cv2.flip(video_frame, 1)
                results = model.get_landmarks() #Get landmarks 
                #Vid number *2 - 1 since odd numbers left out so saved there
                self.save_landmarks_to_db(results, widgets.get_wordID(), widgets.get_vid_no()*2-1, self.frame_no)#Save landmarks from flipped frame into database
                
                self.frame_no +=1 #Increment frame number
            
            #If not recording:
            else:
                self.frame_no = 0 #Reset current frame number
                widgets.set_record_var(False) #Set currently recording to false
                
            self.vid_frame_label.after(50, lambda: self.show_feed(widgets))#New frame after 50 ms 


#GENERATE TRAINING UI
class C_TrainingUI:
    def __init__(self, no_of_frames = 30):
        self.no_of_frames = no_of_frames #Number of frames in one video
    
    def execute(self, root, main):
        #Create widgets
        training_widgets = C_TrainingWidgets(root, main, self.no_of_frames)
        training_widgets.add_widgets()
        vid_frame_label = training_widgets.get_video_feed_label() #Get video frame and root widget
        video_feed = C_VideoFeed(self.no_of_frames, vid_frame_label)#Create video feed object
        
        #Start background process of showing video frames
        Thread(target = lambda: video_feed.show_feed(training_widgets), daemon = True).start()