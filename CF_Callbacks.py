# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 15:07:48 2021

@author: MinahilF
"""

#import tensorflow as tf
from tensorflow.keras.callbacks import Callback #To use for model training callbacks
import numpy as np #To initialise loss value


#REFERENCE: https://keras.io/guides/writing_your_own_callbacks/

class C_Callbacks(Callback):
    def __init__(self, total_epochs, progress_bar, percent_done_label, validation_ratio = 0.2, patience = 50):
        super().__init__() #Initialise callbacks class from tkinter for use of methods such as self.method.*
        
        self.lowest_loss = np.Inf #Initialize the best loss as infinity since all losses calculated will be less than infinity
        
        self.best_accuracy = 0 #Initialise the best accuracy as 0 since all accuracies calculated will be more than this
        
        self.best_weights = None #Weights of best model
        
        self.total_epochs = total_epochs #Total epochs the model is trained for
        
        self.patience = patience #The number of epochs to wait before stopping training since accuracy has reached standstill
        self.epochs_passed = 0 #Number of epochs passed since accuracy hasnt changed
        self.prev_accuracy = 0 #Accuracy of previous epoch
        
        self.progress_bar = progress_bar #Change the progress bar to indicate progress being made
        self.percent_done_label = percent_done_label #Show progress of model in %
        
    def on_train_begin(self, logs=None):
        self.progress_bar["value"] = 0 #Reset progressbar to 0 after each train cycle
        self.percent_done_label.set_text(f"{int(self.progress_bar['value'])}%") #Set progressbar label to the percent value


    def on_train_end(self, logs=None):
        self.model.set_weights(self.best_weights) #Set current model weights to weights with best accuracy
        
    def on_epoch_end(self, epoch, logs=None):

        loss = logs.get("loss") #Get current loss
        accuracy = logs.get("categorical_accuracy") #Get current accuracy

        #If loss is lower and current accuracy is equal to or more than current, then get new weights (since better model)
        if loss < self.lowest_loss and accuracy >= self.best_accuracy:
                self.lowest_loss = loss #Reset lowest loss to new loss
                self.best_accuracy = accuracy #Reset best accuracy to new accuracy
                self.best_weights = self.model.get_weights() #Save the best model weights (these would be those with the highest accuracy and lowest loss)
                
        #Check if minimum reached
        #If current accuracy doesnt change much from the previous value for 'x' epochs, then end training
        if round(accuracy,2) == self.prev_accuracy:
            self.epochs_passed +=1
        else:
            self.epochs_passed = 0
            
        #If best accuracy is more than 97% and loss is less than 10% 
        ##Or accuracy has reached a standstill
        ###Then end training
        if (self.best_accuracy > 0.90 and self.lowest_loss < 0.15) or (self.epochs_passed >= self.patience):
            self.model.stop_training = True            
            
        #Set accuracy of previous epoch to compare with current epoch            
        self.prev_accuracy = round(accuracy,2)    
            
        #Increment progressbar percentage values as a percentage of total epochs
        self.progress_bar["value"] += 100/self.total_epochs
        self.percent_done_label.set_text(f"{int(self.progress_bar['value'])}%")

        