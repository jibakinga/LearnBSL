# -*- coding: utf-8 -*-
"""
Created on Fri Dec 24 01:54:59 2021

@author: MinahilF
"""

#Import required libraries and classes
from CF_CreatingLandmarksDatabase import C_EditLandmarkDatabase 
from CF_Callbacks import C_Callbacks

import os #To save final model
import numpy as np #Array manipulation

from tensorflow.keras.utils import to_categorical #Encode words chosen for application
from tensorflow.keras.models import Sequential #LSTM model
from tensorflow.keras.layers import LSTM, Dense #Dense and LSTM layers for LSTM model

from sklearn.model_selection import StratifiedKFold #To split data into folds for training
from sklearn.metrics import accuracy_score #To judge performance of model

#Create data generator class
class C_DataGenerator:
    def __init__(self, no_of_frames):
        #Database connection
        self.connection = C_EditLandmarkDatabase() #Connect to database
        self.cursor = self.connection.get_cursor() #Assign cursor to database
        self.tables = self.connection.get_tables() #Get all tables in the landmarks database
        self.no_of_frames = no_of_frames #Get the number of frames to be recorded
       
    def get_dataset(self):
        self.cursor = self.connection.get_cursor() #Assign cursor to database

        #Get list of all [WordIDs, Video Numbers] currently saved        
        self.cursor.execute("SELECT WordID, VidNo FROM Face_x_tbl")
         
        #Returns tuples of the format ("WordID", VidNo)
        results = self.cursor.fetchall()
        
        data = [] #Create array for all saved Word IDs and video numbers

        for result in set(results): #Set is used to remove duplicate results
            data.append(list(result)) #Add result to list of results

        self.cursor.close() #Close cursor
        
        return data 
        ##Returns a list of all saved records in the format [[WordID, VidNo],[WordID, VidNo],...]
    
    #Gets landmark arrays
    ##Can be used for both test and train datasets
    def data_landmarks(self, data):
        X, y = [],[] #Define landmark arrays -> X is Landmarks, y is Labels
        
        for WordID, VidNo in data:

                vid_landmarks = [] #Landmarks of each video -> Stores landmarks in a list of lists of frame landmarks
                    
                #Loop through each frame
                for frame in range(self.no_of_frames):
                    
                    frame_landmarks = [] #Create list of frame landmarks
                    
                    #Loop through each table
                    for table in self.tables:
                        self.cursor = self.connection.get_cursor() #Assign cursor to database
                            
                        #Select all records which correspond to the wordID and the particular video
                        command = (f"""
                                     SELECT * FROM {table}
                                     WHERE (WordID = {WordID}) AND (VidNo = {VidNo}) AND (FrameNo = {frame})""")
                        
                        self.cursor.execute(command)
                        
                        results = self.cursor.fetchall()
                        
                        #Append landmarks to frame landmarks
                        for result in results:
                            frame_landmarks.extend(list(result[3:])) #[3:] used to only get landmarks (and not wordID, vidno and frameno (cols 1,2,3)), converted to list since tuple is returned from results
                            
                        self.cursor.close()

                    # frame_landmarks is a list of shape (1662,) corresponding to the 1662 key points stored
                    vid_landmarks.append(frame_landmarks) #Creates a list of frame coordinates from one video
                
                #Append video landmarks to X and y lists
                X.append(vid_landmarks) #Append video landmarks to X array
                y.extend([str(WordID)]) #Extended because append appends arrays not values

        return np.array(X) , y
        #Returns landmarks as a numpy array (X) and labels (y)
        
        
##Build LSTM model 
class C_LSTM:
    def __init__(self, no_of_frames, output_shape):
        self.no_of_frames = no_of_frames #Get number of frames
        self.output_shape = output_shape #Get output shape of output from model
        
    
    #Create LSTM model
    def get_model(self):
        input_shape = (self.no_of_frames, 1662)  #Variable frame_no, fixed number of key points
        
        #Create sequential model
        model = Sequential()
        
        #Add LSTM layers
        model.add(LSTM(name = "LSTM_Layer_1", units = 64, return_sequences=True, activation = "relu", input_shape = input_shape)) 
        model.add(LSTM(name = "LSTM_Layer_2", units = 128, activation = "relu", return_sequences=True))
        model.add(LSTM(name = "LSTM_Layer_3", units = 64, activation = "relu", return_sequences=False))

        #Add dense layers
        model.add(Dense(units = 64,activation="relu")) #Activation is relu because better back propagation 
        model.add(Dense(units = 32,activation="relu")) 
        model.add(Dense(units = 32 ,activation="relu")) 
        
        #Final dense layer
        model.add(Dense(self.output_shape, activation="softmax")) #Softmax returns probability 

        #Compile model 
        model.compile(optimizer="Adam",loss = "categorical_crossentropy",metrics  = ["categorical_accuracy"])
        
        return model 
        #Returns LSTM model


class C_TrainModel:
    def __init__(self, no_of_frames = 30, k_fold_splits = 10, total_epochs = 2000):
        self.no_of_frames = no_of_frames #Get number of frames
        self.k_fold_splits = k_fold_splits #Get number of folds to make
        self.total_epochs = total_epochs #Get the total number of epochs to train the model for
        
    def train(self, progress_bar, percent_done_label, train_check_no): #The parameters passed are to change progressbar status
        
        #Get a list of WordID, VidNo of all data stored
        data_gen = C_DataGenerator(self.no_of_frames)
        all_data = data_gen.get_dataset() #Get all data
        #all_data is in the format [[WordID 1, VidNo 1], [WordID 2, VidNo 2], ... ]

        X, y = data_gen.data_landmarks(all_data) #Get landmarks and labels for all data
        
        #Create kFold object (Shuffle is done to make sure the data is not clustered)
        cross_val_folds = StratifiedKFold(n_splits = self.k_fold_splits, shuffle = True)
        
        cat_y = to_categorical(y).astype(int) #Get one hot encoded labels
                
        output_shape = np.array(cat_y[0]).shape #Get the shape of the output required from the model
        
        total_epochs = self.total_epochs #Define total number of epochs 
        
        AI = C_LSTM(self.no_of_frames, output_shape[0]) #Create model object
        self.model_details = {"accuracy":[],"weights":[]} #Create dictionary of accuracies for each of the model runs and their corresponding weights
        #Use best accuracy and corresponding weights for final model
        
        split_no = 0 #Current kFold split number
        
        #Loop model 'x' times to get best accuracy values over 'x' folds
        for train, test in cross_val_folds.split(X,y):
            
            #Change current split number in UI
            split_no+=1
            train_check_no.set_text(f"{split_no}")
            
            #Reset X_train and y_train for each iteration based on IDs chosen in fold
            X_train = []
            y_train = []
            
            #For each index in the train divide, append landmarks to X_train and y_train
            for index in train:
                X_train.append(X[index])
                y_train.append(cat_y[index])
        
            model = AI.get_model() #Get LSTM
            
            #fit model
            model.fit(
                        np.array(X_train),
                        np.array(y_train),
                        epochs=total_epochs,
                        verbose=0,
                        callbacks=[C_Callbacks(total_epochs, progress_bar, percent_done_label)]
                      )   #Callbacks to callbacks class to get accuracy and loss values and change progressbar
            
            #Get accuracy score by testing on test set
            X_test = []
            y_test = []
            
            #For each index in the test divide, append landmarks to X_test and y_test
            for index in test:
                X_test.append(X[index])
                y_test.append(cat_y[index]) #Get categorical labels
            
            predictions = model.predict(np.array(X_test)) #Get model predictions
            predictions = np.argmax(predictions, axis=1) #Get index of the most probable output
            
            #Get actual labels
            actual = [np.argmax(label, axis=0) for label in y_test]    
            
            #Append accuracy score to model dict
            self.model_details["accuracy"].append(accuracy_score(actual,predictions))
            
            #Append weight score to model dict
            self.model_details["weights"].append(model.get_weights())
        
        best_model = np.argmax(self.model_details["accuracy"]) #Get argument of maximum accuracy
        
        best_accuracy = self.model_details["accuracy"][best_model] #Get accuracy of best model
        
        best_weights = self.model_details["weights"][best_model] #Get weights of best model
        
        model.set_weights(best_weights) #Set current model weights to the best weights from the model
        
        #Append accuracy and words to model database
        current_file_path = os.getcwd() #Get current directory
        file_path = os.path.join(current_file_path, r"model.h5")
        
        #Save model weights
        model.save_weights(file_path)
        
        #Remove progressbar from grid once training done
        progress_bar.grid_remove()
        
        #Show accuracy
        percent_done_label.set_text(f"Model trained with accuracy: {best_accuracy*100: .2f}%")
        percent_done_label.arrange_on_grid(4, 0, columnspan=2, sticky = "WE")