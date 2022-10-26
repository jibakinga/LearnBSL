# -*- coding: utf-8 -*-
"""
Created on Thu Dec 30 20:30:03 2021

@author: MinahilF
"""

import tkinter as tk #For GUI creation
from tkinter import ttk #GUI entryboxes

from threading import Thread #Allows multiprocessing

from CF_Widgets import C_Label, C_Button
from CF_TrainModelCode import C_TrainModel

class C_TrainingMenu:
    def __init__(self, root, main):
        #Create root window
        self.root = root
        self.root.title("Train Model") #Set window title
        self.main = main #Frame in which all other widgets will be contained
        
    def add_widgets(self):
        #Set title
        train_menu_title = C_Label(self.main,"Train Model")
        train_menu_title.set_font(font_size = 15)
        train_menu_title.arrange_on_grid(0,0,sticky = ("WE"), columnspan = 3, padx = 10, pady = 10) 
        
        #Total number of frames entry label
        frame_no_label = C_Label(self.main,"No. of frames per video: 30")
        frame_no_label.arrange_on_grid(1,0,sticky = ("WE"), columnspan = 3, padx = 10, pady = 10) 
        
        #Set number of k_folds
        k_fold_label = C_Label(self.main,"Number of train checks:")
        k_fold_label.arrange_on_grid(2,0,sticky = ("WE"), padx = 10, pady = 10)
        
        #Get number of k_folds (max(10))
        ##Combobox -> subclass of entry widget
        self.k_fold_drop = ttk.Combobox(self.main)
        self.k_fold_drop.config(value = [number+1 for number in range(1,10)]) #Standard combobox with acceptable number of folds
  
        self.k_fold_drop.config(state = "readonly") #Prevents user from entering values not in the combobox dropdown
        self.k_fold_drop.current(0) #Default selection is the first one
        self.k_fold_drop.config(width = 10, height = 5) #Where height is the number of rows high that the pop-down list of values will be displayed
        self.k_fold_drop.config(font=("Consolas", 12))
        self.k_fold_drop.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = "WE", columnspan = 2)
        
        ## Train model button
        self.train_button = C_Button(self.main)
        self.train_button.set_text("Train model")
        self.train_button.set_command(self.train_model) #Link train model button to train_model function
        self.train_button.set_state("active")
        self.train_button.arrange_on_grid(3,0,sticky =("WE"), columnspan = 3, rowspan = 2, padx = 10, pady = 10)
        
        #Training progress label    
        self.training_progress_label = C_Label(self.main,"Progress:")
        self.train_check_label = C_Label(self.main,"Current train check in progress:")
        self.train_check_no = C_Label(self.main,"1")
        
        self.percent_done_label = C_Label(self.main,"0%") #Start at 0
        
        #Training progressbar
        self.progress_bar = ttk.Progressbar(self.main, orient="horizontal", mode= "determinate", length=300)
        
    def train_model(self):
        #Prompt user to ask whether training should start or not
        ok_to_train  = tk.messagebox.askyesno("Start training", "Model training may take a while. Continue? \n (Leaving this screen will stop training)")
        
        if ok_to_train:
            #Start training            
            self.train_button.set_state("disabled")
            self.k_fold_drop.config(state = "disabled")
            self.train_button.remove_from_grid()
            
            #Arrange widgets onto grid
            self.training_progress_label.arrange_on_grid(row = 3, column = 0, padx = 10, pady = 10, sticky = "W")
            self.train_check_label.arrange_on_grid(row = 3, column = 1, padx = 10, pady = 10)
            self.train_check_no.arrange_on_grid(row = 3, column = 2, padx = 10, pady = 10)
            self.percent_done_label.arrange_on_grid(row = 4, column = 2, columnspan = 1, sticky = "W")
            self.progress_bar.grid(row = 4, column = 0, padx = 10, pady = 10, columnspan = 2, sticky = "WE")

            train_model = C_TrainModel(k_fold_splits=int(self.k_fold_drop.get())) #Train model object
                
            #Train model in background
            Thread(target = lambda: train_model.train(self.progress_bar, self.percent_done_label, self.train_check_no), daemon = True).start() #Train model in bg

    
    #Add widgets onto interface
    def run_menu(self):
        self.add_widgets()