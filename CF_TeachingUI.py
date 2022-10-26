# -*- coding: utf-8 -*-
"""
Created on Mon Jan  3 23:59:59 2022

@author: MinahilF
"""


import cv2 #For image and video processing
import numpy as np #For array processing
import random #To generate a random shuffle of a list

import os #To get directory path

from threading import Thread#Allows multiprocessing

#For GUI creation
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

from tensorflow.keras.utils import to_categorical #Encode words chosen for application

from CF_CreatingLandmarksDatabase import C_EditLandmarkDatabase
from CF_HolisticModel import C_holistic_model
from CF_Widgets import C_Label
from CF_TrainModelCode import C_LSTM

#Class creates user interface
class C_TeachingWidgets:
    def __init__(self, root, main, no_of_frames):
        #Database connection
        self.connection = C_EditLandmarkDatabase() #Connect to database
        self.cursor = self.connection.get_cursor() #Assign cursor to database

        #Create root window
        self.root = root
        self.root.title("Learn BSL") #Set window title
       
        #Create main frame for placing widgets
        self.main = main
        self.main.config(padx = 10, pady = 10)
        self.main.grid(row = 0, column = 0, sticky = "NSEW")
        
        #Set no_of_frames
        self.no_of_frames = no_of_frames
        self.video = []

    #Get the list of words to show in the dropdown when it is empty
    def get_words_list(self):
        #Get all words that have been added to the database
        self.cursor.execute("SELECT Word FROM Words_tbl")
         
        #Get list of words    
        self.words = ([i[0].lower() for i in self.cursor.fetchall()]) #Unpack and sortlist of words since returned as a list of tuples

        #Words are in lowercase
        return self.words
        #Returns array of words
     
    #Select a word to sign
    def get_word(self):
        random.shuffle(self.words) #Shuffle list of words
        self.current_word = self.words[0] #Select first word from list of words
        
        self.word_to_sign.set_text(f"{self.current_word.upper()}")
        
        #Get word details
        self.cursor.execute(f"""SELECT WordID, Picture_path, Description FROM Words_tbl
                            WHERE Word = '{self.current_word}'""")
                            
        results = self.cursor.fetchall()
    
        #Unpack results        
        wordID, filepath, description = results[0][0], results[0][1], results[0][2]
        
        #Show image
        height = 150 
        
        #Show details onto screen
        if str(filepath) not in ["None", ""]:
             image = Image.open(filepath) #Open image at filepath
             aspect_ratio = image.size[0]/image.size[1] #Get image aspect ratio
             image = image.resize((int(height*aspect_ratio),height), Image.ANTIALIAS)#Int since height in pixels

             self.new_image = ImageTk.PhotoImage(image)
             self.word_to_sign_image.set_image(self.new_image) #Set label image to the image read
             self.word_to_sign.set_text(None) #Reset word
        
        else:
             self.word_to_sign_image.set_image("") #Erase image previously shown
             self.word_to_sign_image.set_text("No image available") #Show alt text

        if str(description) != "None": #If description saved
            self.word_description.set_text(description) #Show description
        else:
            self.word_description.set_text("No description available") #Alt description text
            
        self.wordID = wordID #Set word ID to if of chosen word
    
    #Create and add labels to main window   
    def add_widgets(self):
        #Set title
        teach_title = C_Label(self.main,"LEARN BSL")
        teach_title.set_font(font_size = 40)
        teach_title.arrange_on_grid(0,0,sticky = ("WE"), columnspan = 3) 
    
        #Create a frame for the word selection
        word_to_sign_frame = tk.LabelFrame(self.main) 
        word_to_sign_frame.config(text = "Word to Sign", font=("Consolas", 10), relief = "groove", borderwidth = 3)
        word_to_sign_frame.grid(row = 1, column = 0, padx = 10, pady = 10,sticky = ("WE"), columnspan = 2)
        
        ##LABELS
        
        ###Word to sign label
        word_label = C_Label(word_to_sign_frame,"Sign this word:")
        word_label.arrange_on_grid(0,0)    
        
        #Chosen word to be signed
        self.word_to_sign = C_Label(word_to_sign_frame)
        self.word_to_sign.set_font(16, bold = True, fg_colour = "#FF0000")
        self.word_to_sign.arrange_on_grid(0, 1, padx = 10, pady = 10, sticky = "WE")

        #Image for sign + Description        
        self.word_to_sign_image = C_Label(word_to_sign_frame)
        self.word_to_sign_image.arrange_on_grid(1, 0, padx = 10, pady = 10, sticky = "WE", columnspan = 2)
        
        #Description of chosen word
        self.word_description = C_Label(word_to_sign_frame)
        self.word_description.set_wraplength(500, "left")
        self.word_description.arrange_on_grid(2, 0, padx = 10, pady = 10, sticky = "WE", columnspan = 2)
        
        #Create a frame for the feedback that will be given
        feedback_frame = tk.LabelFrame(self.main) 
        feedback_frame.config(text = "Feedback", font=("Consolas", 10),  relief = "groove", borderwidth = 3)
        feedback_frame.grid(row = 2, column = 0, padx = 10, pady = 10,sticky = ("WE"), columnspan = 2)     
    
        #Label showing whether the sign was recognised or not
        feedback_label = C_Label(feedback_frame)
        feedback_label.set_text("Result:")
        feedback_label.arrange_on_grid(1, 0)
        
        #Output regaring whether sign was performed correctly or not
        self.feedback_output_text = C_Label(feedback_frame)
        self.feedback_output_text.set_font(14, bold = True, fg_colour = "#00A300")
        self.feedback_output_text.arrange_on_grid(1, 1)
            
        #Video feed label
        self.video_feed_label = tk.Label(self.main)
        self.video_feed_label.grid(row = 1 , column = 2, rowspan = 5, padx = 10, pady = 10) 
        
        #Progressbar to let user know that threshold is achieved
        self.progress_bar = ttk.Progressbar(feedback_frame, orient="horizontal", mode= "determinate", length=300)
        self.progress_bar.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10, sticky = "WE")
        
        #Get list of saved words
        self.words =  self.get_words_list()
        self.get_word() #Get word to sign

    def get_video_feed_label(self):
        return self.video_feed_label
        #Returns the video feed label (the label where the frames will be shown)
    
    def get_progress_bar(self):
        return self.progress_bar #Returns the progressbar widget
    
    #Get the wordID of the word selected in the combobox
    def get_wordID(self):
        self.cursor.execute(f"SELECT WordID FROM Words_tbl WHERE Word = {self.word}")
        wordID = self.cursor.fetchall()[0][0]
        return wordID
        #Returns the wordID of the word selected
            
    def get_cursor(self): #Return cursor
        return self.cursor
    
    def get_current_word(self):
        return self.current_word #Return current word being signed
    
    def set_feedback_label(self,feedback):
        self.feedback_output_text.set_text(feedback) #Set the feedback label value
    
    def get_root(self):
        return self.root #Get the root widget


class C_LoadModel:
    def __init__(self, no_of_frames):
        self.no_of_frames = no_of_frames
        
    def get_output_shape(self):
        #Database connection
        connection = C_EditLandmarkDatabase() #Connect to database
        cursor = connection.get_cursor() #Assign cursor to database
        
        #Get all words that have been added to the database
        cursor.execute("SELECT WordID FROM Face_x_tbl")
         
        #Get list of words    
        self.wordIDs = ([i[0] for i in set(cursor.fetchall())]) #Unpack and sortlist of words since returned as a list of tuples (list comprehension)
        
        print(self.wordIDs)
        
        cat_y = to_categorical(self.wordIDs).astype(int) #Get one hot encoded labels
                
        self.output_shape = np.array(cat_y[0]).shape #Get the shape of the output required from the model
        self.output_shape = self.output_shape[0]
        
        connection.close_connection() #Close connection to database

    #Get the saved model
    def get_AI(self):
        self.get_output_shape() #Get output shape of model
        AI = C_LSTM(self.no_of_frames, self.output_shape) #Create model object
        model = AI.get_model() #Get model
        
        current_file_path = os.getcwd() #Get current working directory
        file_path = os.path.join(current_file_path, r"model.h5") 

        model.load_weights(file_path) #Load model weights from the filepath

        return model
    
    #get dictionary of each word and its wordID
    def get_dict(self):
        #Database connection
        connection = C_EditLandmarkDatabase() #Connect to database
        cursor = connection.get_cursor() #Assign cursor to database
        
        #Get all words that have been added to the database
        cursor.execute("""SELECT WordID, Word 
                           FROM Words_tbl""")
         
        #Get list of words    
        word_dictionary = {i[0]:i[1] for i in set(cursor.fetchall())} #Unpack and sortlist of words since returned as a list of tuples
        
        connection.close_connection() #Close database connection
        
        return word_dictionary

            
#Video feed object
class C_VideoFeed:
    def __init__(self,no_of_frames, vid_frame_label, progress_bar):
        self.no_of_frames = no_of_frames #No of frames is passed in
        self.frame_no = 0 #Initial frame number set to 0

        self.video = [] #List for video landmarks
        
        self.vid_frame_label = vid_frame_label #Video frame

        self.cap = cv2.VideoCapture(0)  #Capture video frames from camera 0
        
        LSTM_model = C_LoadModel(self.no_of_frames) #Create model object
        self.AI = LSTM_model.get_AI() #Get model
    
        self.word_dict = LSTM_model.get_dict() #Get dictionary of words and wordIDs
        
        self.no_of_times_correct = 0 #Checks the number of times the sign was correctly done to ensure that the sign itself was recognised and it wasnt an anomaly

        self.reinforcement_comments = ("Good job!", "You did it!", "That was perfect!", "You're learning fast!", "Keep it up!", "Just right!")
        
        self.progress_bar = progress_bar #Progressbar to indicate the sign is being correctly recognised
        
        self.threshold = 15 #Threshold corresponding to the number of frames for which the sign should be recognised correctly
        
    #Save frame landmarks to database
    def get_landmarks_array(self, results):    
        
        main_landmarks = [] #List of frame landmarks

        #Append landmarks to arrays to be saved
        def append_to_landmark_arrays(x, y, z, result):
            x.extend([result.x])
            y.extend([result.y])
            z.extend([result.z])
            #return x,y,z
            
        #Get array of face landmarks   
        x_landmarks, y_landmarks, z_landmarks = [],[],[]
        
        if results.face_landmarks:
        #If face landmarks are present then:
                
            #For each landmark in the face results
                #Appends landmark coordinates (468,) to landmarks list 
            
            for result in results.face_landmarks.landmark:
                append_to_landmark_arrays(x_landmarks, y_landmarks, z_landmarks, result) #Append results to existing axis landmark arrays
                
        else:
        #If face landmarks absent
            x_landmarks = [0] * 468 #No landmarks so array of 0's is added
            y_landmarks, z_landmarks = x_landmarks.copy(), x_landmarks.copy()
            
        main_landmarks.extend(x_landmarks)
        main_landmarks.extend(y_landmarks)
        main_landmarks.extend(z_landmarks)

        #Get array of right hand landmarks
        
        x_landmarks, y_landmarks, z_landmarks = [],[],[]
        
        #Since mirrored, left hand landmarks = real right hand landmarks
        if results.left_hand_landmarks:
        #If left hand landmarks are present then
            
            #For each landmark in left hand results 
                #Appends landmark coordinates (21,) to landmarks list
            
            for result in results.left_hand_landmarks.landmark:
                append_to_landmark_arrays(x_landmarks, y_landmarks, z_landmarks, result) #Append results to existing axis landmark arrays
        else:
        #If left hand landmarks absent
            x_landmarks = [0] * 21 #No landmarks so array of 0's is added
            y_landmarks, z_landmarks = x_landmarks.copy(), x_landmarks.copy()
        
        #List of shape (24,) is returned
        
        #Add records to tables
        main_landmarks.extend(x_landmarks)
        main_landmarks.extend(y_landmarks)
        main_landmarks.extend(z_landmarks)
        
        #Get array of pose landmarks        
        x_landmarks, y_landmarks, z_landmarks, vis_landmarks = [],[],[],[]
        
        if results.pose_landmarks:
        #If pose landmarks are present then        
            #For each landmark in the pose results 
                #Appends landmark coordinates (33,) to landmarks list 
            for result in results.pose_landmarks.landmark:
                append_to_landmark_arrays(x_landmarks, y_landmarks, z_landmarks, result) #Append results to existing axis landmark arrays
                vis_landmarks.extend([result.visibility])
               
        else:
        #If pose landmarks absent
            x_landmarks = [0] * 33  #No landmarks so array of 0's is added
            y_landmarks, z_landmarks, vis_landmarks = x_landmarks.copy(), x_landmarks.copy(), x_landmarks.copy()
        
        #List of shape (36,) is returned -> this is the record to be added
            
        #Add records to tables
        main_landmarks.extend(x_landmarks)
        main_landmarks.extend(y_landmarks)
        main_landmarks.extend(z_landmarks)
        main_landmarks.extend(vis_landmarks)
              
        #Get array of left hand landmarks 
        x_landmarks, y_landmarks, z_landmarks = [],[],[]
        
        
        #Since mirrored, right hand landmarks = real left hand landmarks
        if results.right_hand_landmarks:
        #If right hand landmarks are present then
            
            #For each landmark in right hand results 
                #Appends landmark coordinates (21,) to landmarks list
            
            for result in results.right_hand_landmarks.landmark:
                append_to_landmark_arrays(x_landmarks, y_landmarks, z_landmarks, result) #Append results to existing axis landmark arrays
                
        else:
        #If right hand landmarks absent
            x_landmarks = [0] * 21 #No landmarks so array of 0's is added
            y_landmarks, z_landmarks = x_landmarks.copy(), x_landmarks.copy()
        
        #List of shape (24,) is returned
        
        #Add records to tables
        main_landmarks.extend(x_landmarks)
        main_landmarks.extend(y_landmarks)
        main_landmarks.extend(z_landmarks)

        return main_landmarks
       
          
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
            
            #Append landmarks from current frame to video landmarks
            self.video.append(self.get_landmarks_array(results))            
            
            #Get the latest number of frames recorded
            self.video = self.video[-self.no_of_frames:] 
            
            #If frame number is equal to number of frames: (Recording complete)            
            if len(self.video) == self.no_of_frames:
            
                pred = self.AI.predict(np.expand_dims(self.video, axis=0))

                if pred[0][np.argmax(pred, axis = 1)] > 0.60:
                    #Get index of the most probable output
                    predicted_word = np.argmax(pred, axis=1) 
                    word = self.word_dict.get(predicted_word[0]) #Get predicted word
                    
                    #If word predicted is the same as the one user was asked to sign
                    if word == widgets.get_current_word(): 
                        #Add to the number of times the sign was recognised correctly
                        self.no_of_times_correct +=1 
                        
                        self.progress_bar["value"] += 100/self.threshold #Increment progressbar
                        
                    #If the number of times the sign was recognised correctly has reached threshold value
                    if self.no_of_times_correct >= self.threshold:
                        #Tell user they are right
                        label = random.choice(self.reinforcement_comments)#Choose random comment
                        widgets.set_feedback_label(label) #Show feedback
                        self.no_of_times_correct = 0 #Reset counter
                        self.progress_bar["value"] = 0 #Reset progress bar
                        
                        tk.messagebox.showinfo("Next word", "You did it! Keep going...") #Show message to user
                        
                        widgets.get_word() #Get another word for user to sign from words list
                        
                    else:
                        widgets.set_feedback_label("Try again!")
                    
                else:
                    self.no_of_times_correct = 0
                    self.progress_bar["value"] = 0
                    widgets.set_feedback_label("Try again!")
                
            self.vid_frame_label.after(50, lambda: self.show_feed(widgets))   
            #New frame after 50 ms


#GENERATE TEACHING UI
class C_TeachingUI:
    def __init__(self, no_of_frames = 30):
        self.no_of_frames = no_of_frames #Number of frames in one video
    
    def execute(self, root, main):
        #Create widgets
        teaching_widgets = C_TeachingWidgets(root, main, self.no_of_frames)
        teaching_widgets.add_widgets()
        
        vid_frame_label = teaching_widgets.get_video_feed_label() #Get video frame and root widget
        progress_bar = teaching_widgets.get_progress_bar() #Get progressbar widget
        
        #Create video feed object
        video_feed = C_VideoFeed(self.no_of_frames, vid_frame_label, progress_bar)
        
        #Start background process of showing video frames
        Thread(target = lambda: video_feed.show_feed(teaching_widgets), daemon = True).start()
