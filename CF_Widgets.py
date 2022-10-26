# -*- coding: utf-8 -*-
"""
Created on Sat Dec 18 20:35:34 2021

@author: MinahilF
"""

#Import appropriate required libraries
import tkinter as tk #To create GUI elements

#Widget superclass
##Contains methods common to buttons and labels
class C_Widget:
    def __init__(self, widget):
        self.widget = widget #Sets the current widget to be edited
        self.widget.config(font=("Consolas", 12)) #Default font and font size set

    #Arrange the widget onto the grid
    ##Variables set as default if no custom values given
    def arrange_on_grid(self,row,column, padx = 10, pady = 10, sticky = None, columnspan = None, rowspan = None):
        #Aligns widget onto the grid
        self.widget.grid(row = row, column = column, padx = padx, pady = pady, sticky = sticky, columnspan = columnspan)
            
    #Set widget font
    def set_font(self,font_size, font = "Consolas",fg_colour = None, bold = False):
        #Default is not bold, but if bold is given as true, the text is made bold
         self.widget.config(font=(font, font_size, "bold" if bold else "normal"), fg = fg_colour) 
        
    #Set widget text
    def set_text(self, text):
        self.widget.config(text = text)
        
    #Set button width
    def set_width(self, width):
        self.widget.config(width = width)  
        
    #Remove widget from grid
    def remove_from_grid(self):
        self.widget.grid_remove()
       
#Create label widget
class C_Label(C_Widget):
    #Inherits methods from widget class
    
    #Initialise widget
    def __init__(self, root, text = None):
        self.label = tk.Label(root,text = text)
        super().__init__(self.label)
    
    #Set wrap length for label
    def set_wraplength(self, wraplength, justify):
        self.label.config(wraplength = wraplength, justify = justify)
     
    #Set label image
    def set_image(self, image):
        self.label.config(image = image)
        
    #Get label text
    def get_text(self):
        return self.label.cget("text")
        
#Create button widget
class C_Button(C_Widget):
    def __init__(self, root, text = None, function = None):
        #Button is set to disabled as default
        self.button = tk.Button(root, text = text, command = function, state = "disabled") #Disabled by default
        super().__init__(self.button)
       
    #Set button background colour
    def bg_col(self, bg_colour):
        self.button.config(bg = bg_colour)

    #Set button state (active/disabled)
    def set_state(self, state):
        self.button.config(state = state)
        
    #Assigns the command to the button
    def set_command(self,command):
        self.button.config(command = command)
        
        
