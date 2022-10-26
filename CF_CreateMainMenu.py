# -*- coding: utf-8 -*-
"""
Created on Sat Jan  1 01:45:50 2022

@author: MinahilF
"""

#For GUI creation
import tkinter as tk

from CF_Widgets import C_Label, C_Button
from CF_TrainingMenu import C_TrainingMenu
from CF_TeachingUI import C_TeachingUI
from CF_WordsMenu import C_AddWords
from CF_TrainingUI import C_TrainingUI

class C_MainMenu:
    def __init__(self):
        
        #Create root window
        self.root = tk.Tk()
        self.root.title("Learn BSL") #Set window title
        
        self.root.config(padx = 10, pady = 10)
        self.root.resizable(width=False, height=False) #Do not allow window to be resized
#        self.root.attributes("-fullscreen", True)
        
        #Set window icon
        icon = tk.PhotoImage(file="Icon.png") 
        self.root.iconphoto(True,icon) #True means icon is applied to all future top levels (other windows created?)
         
        self.main_frame = tk.LabelFrame(self.root) 
        
        self.main_frame.pack()
        
        self.main = tk.LabelFrame(self.main_frame) 
        self.main.grid(row = 0, column = 0, sticky = ("WE"))
        
        self.back_button = C_Button(self.main_frame)
        self.back_button.set_text("BACK TO MAIN MENU")
        self.back_button.set_command(self.back_to_main) #Link train model button to train_model function
        self.back_button.set_state("active")
    
    #Frame to allow page change
    def reset_frame(self):
        self.main.destroy()
        self.main = tk.LabelFrame(self.main_frame) 
        self.main.grid(row = 0, column = 0, sticky = ("WE"))
        
    def add_widgets(self):
        #Set title
        main_menu_title = C_Label(self.main,"Learn BSL")
        main_menu_title.set_font(font_size = 35)
        main_menu_title.arrange_on_grid(0,0,sticky = ("WE"), columnspan = 3) 
        
        ## Start learning button
        self.learn_button = C_Button(self.main)
        self.learn_button.set_text("Start learning")
        self.learn_button.set_command(self.start_teaching_ui) #Link train model button to train_model function
        self.learn_button.set_state("active")
        self.learn_button.arrange_on_grid(1,1,sticky =("WE"))
        
        ## Train model button
        self.train_button = C_Button(self.main)
        self.train_button.set_text("Train model")
        self.train_button.set_command(self.start_training_menu) #Link train model button to train_model function
        self.train_button.set_state("active")
        self.train_button.arrange_on_grid(2,1,sticky =("WE"))       
        
        ## Add training videos button
        self.add_vids_button = C_Button(self.main)
        self.add_vids_button.set_text("Add training videos")
        self.add_vids_button.set_command(self.start_training_ui) #Link train model button to train_model function
        self.add_vids_button.set_state("active")
        self.add_vids_button.arrange_on_grid(3,1,sticky =("WE"))
        
        self.edit_words_button = C_Button(self.main)
        self.edit_words_button.set_text("Edit saved words")
        self.edit_words_button.set_command(self.start_words_menu) #Link train model button to train_model function
        self.edit_words_button.set_state("active")
        self.edit_words_button.arrange_on_grid(4,1,sticky =("WE"))

    #Return to main menu
    def back_to_main(self):
        self.reset_frame()
        self.root.title("Learn BSL") #Set window title
        self.back_button.remove_from_grid()
        self.add_widgets()
        
    #Go to learning screen
    def start_teaching_ui(self):
        self.reset_frame()
        teaching_ui = C_TeachingUI()
        self.back_button.arrange_on_grid(1,0,sticky =("WE"))
        teaching_ui.execute(self.root, self.main)
    
    #Go to training menu
    def start_training_menu(self):
        self.reset_frame()
        training_menu = C_TrainingMenu(self.root, self.main)
        self.back_button.arrange_on_grid(1,0,sticky =("WE"))
        training_menu.run_menu()

    #Go to words menu
    def start_words_menu(self):
        self.reset_frame()
        words_menu = C_AddWords(self.root, self.main)
        self.back_button.arrange_on_grid(1,0,sticky =("WE"))
        words_menu.run_menu()
    
    #Go to add words screen
    def start_training_ui(self):
        self.reset_frame()
        training_ui = C_TrainingUI()
        self.back_button.arrange_on_grid(1,0,sticky =("WE"))
        training_ui.execute(self.root, self.main)
    
    #Start 
    def run_menu(self):
        self.root.mainloop()


def Main():        
    x = C_MainMenu()
    x.add_widgets()
    x.run_menu()

if __name__ == "__main__":
    Main()