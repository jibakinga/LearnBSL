# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 22:00:30 2022

@author: MinahilF
"""


import tkinter as tk #For GUI creation
from tkinter import filedialog #To allow for file selection

from CF_CreatingLandmarksDatabase import C_EditLandmarkDatabase
from CF_Widgets import C_Label, C_Button

from PIL import ImageTk, Image #To show images onto GUI


#Create interface to add, update or delete words
class C_AddWords:
    def __init__(self, root, main):
        #Database connection
        self.connection = C_EditLandmarkDatabase() #Connect to database
        self.cursor = self.connection.get_cursor() #Assign cursor to database       
        
        #Create root window
        self.root = root
        self.root.title("Edit Words") #Set window title
        self.root.config(padx = 10, pady = 10)
        
        #Create main frame for placing widgets
        self.main = main
        self.main.config(padx = 10, pady = 10)
        self.main.grid(row = 0, column = 0, sticky = "NSEW")
        
    #Get the list of words to show in the dropdown when it is empty
    def get_words_list(self):
        #Get all words that have been added to the database
        self.cursor.execute("SELECT Word FROM Words_tbl")
         
        #Get list of words    
        self.words = sorted([i[0].lower() for i in self.cursor.fetchall()]) #Unpack and sortlist of words since returned as a list of tuples (list comprehension)
        
        #Words are in lowercase
        return self.words
    #Returns array of words
    
    #Creates view word frame
    def create_view_frame(self, root):  
        #Remove widgets from grid
        self.delete_records_button.remove_from_grid()
        self.add_word_entry.grid_remove()
        self.description_entry.grid_remove()
        self.select_filepath_button.remove_from_grid()
        self.save_new_word_button.remove_from_grid()
        self.update_word_button.remove_from_grid()
        self.change_word_entry.grid_remove()
        self.add_word_entry.grid_remove()

        #Create a frame for viewing currently saved words
        root.config(text = "List of Saved Words")
        
        #Set label onto grid
        self.view_word_label.set_text("Select a word to view: \n (from list on right)")
        self.view_word_label.arrange_on_grid(0,0, sticky = "W")      
        
        #Set selected word label onto grid
        self.word_selected.set_text("") #Reset selection
        self.word_selected.arrange_on_grid(0,1)
        
        #Show saved videos number indicator onto grid
        self.extra_label.set_text("Total videos saved:")
        self.extra_label.arrange_on_grid(1, 0, sticky = "W" , columnspan = 2)
        
        #Place description label onto grid
        self.description_label.set_text("Description of sign:")
        self.description_label.arrange_on_grid(2,0, sticky = "W")
        
        #Show the word description
        self.view_description_label.set_text("") #Reset description text
        self.view_description_label.arrange_on_grid(3,0, columnspan = 2)
        
        #Label for the chosen image
        self.image_label.set_text("Image chosen:")
        self.image_label.arrange_on_grid(4,0, sticky = "W")
        
        #Show selected image onto grid 
        self.selected_image.set_image("") #Reset image selection
        self.selected_image.arrange_on_grid(5, 1)
        
        #Show filepath of the image selected
        self.selected_filepath.set_wraplength(450, "left")
        self.selected_filepath.set_font(10)
        self.selected_filepath.arrange_on_grid(5,0, sticky = "WE")        

        
    #When listbox option is selected
    def listbox_select(self, event = None):
        #Get selected word from listbox
        selected_word = self.view_list.curselection()

        #Check if any word is selected
        if selected_word: #Disabling generates event
            self.change_word_entry.config(state = "normal")    
        
            #Get word index
            index = selected_word[0] #since tuple returned
            self.current_word = self.words[index].lower() #Get currently selected word
            
            #Show selected word
            self.word_selected.set_text(self.current_word)
            self.add_word_entry.delete(0, "end")
            self.add_word_entry.insert(0,self.current_word)
            self.change_word_entry.delete(0, "end")
            self.change_word_entry.insert(0,self.current_word)      
            
            #Show word description and filepath
            self.cursor.execute(f"""SELECT VidPairs, Picture_path, Description
                                   FROM Words_tbl
                                   WHERE Word = '{self.current_word}'""")
            
            vidpairs, filepath, description = self.cursor.fetchall()[0]
            
            #Check which page it is on:
                #If it is in the view or delete page:
            if (self.main_action_frame.cget("text")) in ("List of Saved Words", "Delete Word"):
                self.delete_records_button.set_state("active")
                self.extra_label.set_text(f"Total videos saved: {vidpairs}")
            
            #Show filepath
            self.image_filepath = filepath #Set filepath
            
            if filepath: #If filepath is saved (not NONE)
                self.selected_filepath.set_text(filepath) #Show selected filepath
                
            else: #If no filepath saved
                self.selected_filepath.set_text("No image was saved")
                self.selected_image.set_image("")
            
            #Check if image exists for that filepath
            try:
                #If image exists, show image
                self.show_image(self.image_filepath)                
            except:
                #If image does not exist or cannot be found
                self.selected_image.set_image("") #Remove image shown if any
                self.selected_image.set_text("IMAGE COULD NOT BE FOUND") #Indicate that the image could not be found
        
            #Reset description box
            self.description_entry.delete("1.0", "end")
            
            #If description is saved
            if description:
                #Show description
                self.description_entry.insert("1.0",description) 
                self.view_description_label.set_text(description)
            else:
                self.view_description_label.set_text("No description saved")

    #Show word image             
    def show_image(self, filepath):
        #Show image
        height = 100 #Set image height
        
        #If filepath exists
        if str(filepath) not in ("None","") :
            
            image = Image.open(filepath) #Open image
            
            #Resize image as per aspect ratio
            aspect_ratio = image.size[0]/image.size[1] 
            image = image.resize((int(height*aspect_ratio),height), Image.ANTIALIAS)#Int since height in pixels
            
            #Show image
            self.image = ImageTk.PhotoImage(image)
            self.selected_image.set_image(self.image)
        
        else:
            self.selected_image.set_image("") #Remove image
        
    #View words
    def view_button_command(self, root):
        #Create frame to hold widgets
        self.create_view_frame(root)
        self.update_listbox() #Update with new words added
        self.view_list.config(state = "normal")
        self.selected_filepath.set_text("") #Reset filepath displayed
        
        #Reset selection
        self.view_list.selection_clear(0, tk.END)
        self.view_list.select_set(0)
        self.listbox_select()   
    
    #Create frame for add new word menu
    def create_add_frame(self, root):      
        #Remove widgets from grid
        self.extra_label.remove_from_grid()
        self.delete_records_button.remove_from_grid()
        self.word_selected.remove_from_grid()
        self.change_word_entry.grid_remove()
        self.view_description_label.remove_from_grid()
        self.update_word_button.remove_from_grid()
        
        #Set title
        root.config(text = "Add New Word")
        
        #Add word label
        self.view_word_label.set_text("Enter the word you want to add:")
        self.view_word_label.arrange_on_grid(0,0, sticky = "W")
        
        #Word entry        
        self.add_word_entry.delete(0, "end")
        self.add_word_entry.config(width = 15, font = ("Consolas", 12))
        self.add_word_entry.grid(row = 0, column = 1, padx = 10, pady = 10)
        
        #Description label        
        self.description_label.set_text("Add a description:")
        self.description_label.arrange_on_grid(1,0, sticky = "W")
                
        #Description entry
        self.description_entry.delete("1.0", "end") #Clear entry box
        self.description_entry.insert("end","")
        
        self.description_entry.config(state = "disabled") #Set state as disabled to prevent editing
        self.description_entry.config(width = 50, height = 2, font = ("Consolas", 12))
        self.description_entry.grid(row = 2, column = 0, padx = 10, pady = 10, columnspan = 2, sticky = "WE")        
        
        #Image label
        self.image_label.set_text("Select filepath for image of sign:")
        self.image_label.arrange_on_grid(3,0, sticky = "W")
        
        #Filepath select button
        self.select_filepath_button.set_text("Select file")
        self.select_filepath_button.arrange_on_grid(3,1,sticky =("WE"))

        #Set image 
        self.selected_image.set_image("")
        self.selected_image.arrange_on_grid(4, 1, columnspan = 1, rowspan = 1)
        
        #Set filepath
        self.selected_filepath.set_text("")
        self.selected_filepath.set_wraplength(450, "right")
        self.selected_filepath.set_font(10)
        self.selected_filepath.arrange_on_grid(4,0, sticky = "WE")
    
        #Save button        
        self.save_new_word_button.arrange_on_grid(5,0, sticky = "WE", columnspan=2)

    #Add words
    def add_button_command(self, root):        
        self.update_listbox() #Update with new words added
        self.view_list.config(state = "disabled") #Disable list to prevent selection
        self.selected_filepath.set_text("")
        
        self.image_filepath = None
        self.description_entry.delete("1.0", "end") #Reset description entry box
        
        self.create_add_frame(root) #Create frame (add widgets to frame)
    
    #Save word
    def save_new_word(self):
        #Get contents of description entry box
        description = self.description_entry.get("1.0", tk.END)
        
        #If there is nothing in the description box, add no description
        if description == "\n":
            description = None
            
        #Add word and details to database
        self.cursor.execute(f"""
                            INSERT INTO Words_tbl (Word, VidPairs, Picture_path, Description)
                            VALUES ('{self.current_word}', 0, '{self.image_filepath}', '{description}')
                            """)
        
        self.update_listbox() #Update listbox since new words have been added
        
        self.add_button_command(self.main_action_frame) #Reset add frame to include new word
    
    #Update listbox values
    def update_listbox(self):
        self.get_words_list() #Update word list
        self.connection.reset_auto_increment("Words_tbl", "WordID") #Reset max id if last added word has been deleted
        
        self.view_list.config(state = "normal")
        self.view_list.delete(0, tk.END)  #clear listbox

        self.view_list.insert(tk.END, *self.words) #Add new list of words
        
        self.view_list.config(state = "disabled") #Set state of listbox to disabled as default

    #Add word entry
    def validate_add_entry(self, P):
        #Get word from entry box
        #If entry box entry is in words list
        if (len(P) == 0) or (P in self.words):
            #Disable widgets
            self.save_new_word_button.set_state("disabled")
            self.description_entry.config(state = "disabled")            
            self.select_filepath_button.set_state("disabled")
        
        else:
            self.save_new_word_button.set_state("active")
            self.select_filepath_button.set_state("active")
            self.description_entry.config(state = "normal")            
            
            self.current_word = P.lower() #Set current word to the word which is entered
        return True #Allow word to be entered
    
    #Select filepath
    def select_filepath(self):
        file_types = ["*.jpg","*.jpeg","*.png","*.jfif"] #List of acceptable filetypes
        
        #Open filedialog to select file
        self.image_filepath = filedialog.askopenfilename(title = "Select image", filetypes = (("Image files", file_types),))
        
        #Show filepath and selected image
        self.selected_filepath.set_text(self.image_filepath)
        self.show_image(self.image_filepath)
        
    #Edit word button
    def modify_button_command(self,root):
        self.update_listbox() #Reset contents of listbox
        self.view_list.config(state = "normal") #Listbox active so user can select option
        self.selected_filepath.set_text("") #Reset filepath contents
        
        self.view_list.selection_clear(0, "end")
        self.description_entry.delete("1.0", "end")
        
        self.create_modify_frame(root) #Create frame
        
    #Update word
    def update_word_command(self):
        description = self.description_entry.get("1.0", tk.END) #Get description
        
        #If no description entered:
        if description == "\n":
            description = None
        
        #Get the word that the word should be changed to
        word_to_change = (self.word_selected.get_text())
        
        #Update words table with new word details
        self.cursor.execute(f"""
                            UPDATE Words_tbl 
                            SET Word = '{self.current_word}', Picture_path = '{self.image_filepath}', Description = '{description}'
                            WHERE Word = '{word_to_change}'
                            """)
  
        self.connection.commit_changes() #Save changes to database
            
        self.modify_button_command(self.main_action_frame) #Recreate frame    
        
    #Create frame for modify word
    def create_modify_frame(self, root):
        #Hide widgets from grid
        self.delete_records_button.remove_from_grid()
        self.add_word_entry.grid_remove()
        self.save_new_word_button.remove_from_grid()
        self.view_description_label.remove_from_grid()
        self.view_description_label.remove_from_grid()        

        #Create a frame for viewing currently saved words
        root.config(text = "Modify Word")
        
        #Show and align widgets
        self.view_word_label.set_text("Select the word you want to change: \n (from list on right)")
        self.view_word_label.arrange_on_grid(0,0, sticky = "W")
        
        #Add label for the alternate word to change to
        self.extra_label.set_text("Change existing word to:")
        self.extra_label.arrange_on_grid(1,0,sticky = "W")
        
        #Reset word selection
        self.word_selected.set_text("") #Clear selection
        self.word_selected.arrange_on_grid(0,1)        
        
        #Change word entry box
        self.change_word_entry.delete(0, "end") #Clear entry
        self.change_word_entry.config(state = "disabled")
        self.change_word_entry.config(width = 15, font = ("Consolas", 12))
        self.change_word_entry.grid(row = 1, column = 1, padx = 10, pady = 10)
        
        #Label for description
        self.description_label.set_text("Description of sign:")
        self.description_label.arrange_on_grid(2,0, sticky = "W")
    
        #Entrybox for description
        self.description_entry.delete("1.0", "end")
        self.description_entry.config(state = "disabled") 
        self.description_entry.config(width = 50, height = 2, font = ("Consolas", 12))
        self.description_entry.grid(row = 3, column = 0, padx = 10, pady = 10, columnspan = 2, sticky = "WE") 

        #Label for image
        self.image_label.set_text("Image chosen:")
        self.image_label.arrange_on_grid(4,0, sticky = "W")
        
        #Image selected
        self.selected_image.set_image("") #Reset selected image
        self.selected_image.arrange_on_grid(5, 1, columnspan = 1)
        
        #Filepath select button
        self.select_filepath_button.set_text("Select file")
        self.select_filepath_button.set_state("disabled") #Initial state is disabled
        self.select_filepath_button.arrange_on_grid(4,1,sticky =("WE"))
        
        #Selected filepath label
        self.selected_filepath.set_wraplength(450, "left")
        self.selected_filepath.set_font(10)
        self.selected_filepath.arrange_on_grid(5,0, sticky = "WE")    
        
        #Show button to update word
        self.update_word_button.arrange_on_grid(6,0, sticky = "WE", columnspan = 2)

    #Validate word for change in word
    def validate_change_entry(self, P):
        #If word is not null, or the selected word or saved word:
        if (len(P) == 0) or ((P != self.word_selected.get_text()) and (P in self.words)):
            self.update_word_button.set_state("disabled")
            self.description_entry.config(state = "disabled")            
            self.select_filepath_button.set_state("disabled")
        else:
            self.update_word_button.set_state("active")
            self.description_entry.config(state = "normal")            
            self.select_filepath_button.set_state("active")
            
            self.current_word = P.lower() #Set current word as word entered
        return True
    
    #Delete word command
    def delete_button_command(self, root):
        self.selected_filepath.set_text("") #Reset selected filepath
    
        self.update_listbox() #Update listbox contents
        self.view_list.config(state = "normal") #Allow options to be selected from listbox
        
        self.view_list.selection_clear(0, tk.END)  #Reset selection from listbox
        
        self.listbox_select() #Select default from listbox
        self.create_delete_frame(root) #Create delete frame
    
    #Create delete word frame
    def create_delete_frame(self,root):
        self.create_view_frame(root) #Create view frame (delete screen based on view screen)
        
        root.config(text = "Delete Word") #Set frame title
        
        self.view_word_label.set_text("Select a word to delete: \n (from list on right)")
        
        self.delete_records_button.set_state("disabled") #Initial state of delete button is disabled
        self.delete_records_button.arrange_on_grid(6, 0, columnspan = 2, sticky = "WE")
        
    #Delete record
    def delete_record_command(self):
        #Ask user whether they are sure that they want to delete it
        is_sure = tk.messagebox.askokcancel(title='Delete word', message=f"This action will delete all the data for the word: '{self.current_word}' \n Are you sure you want to continue?", icon="warning")
        
        #If they want to delete it:
        if is_sure:
            self.connection.delete_word(self.current_word) #Delete all information relating to the word
            tk.messagebox.showinfo(title = "Records deleted", message= f"All data for the word: '{self.current_word}' has been deleted.")
        
        #Recreate delete frame
        self.delete_button_command(self.main_action_frame)
    
    #Add widgets to UI
    #Create all widgets
    def add_widgets(self):
        #Set title
        add_menu_title = C_Label(self.main,"Words")
        add_menu_title.set_font(font_size = 15)
        add_menu_title.arrange_on_grid(0,0,sticky = ("WE"), columnspan = 4, padx = 10, pady = 10)
        
        #Create main frame for placing widgets
        frame = tk.Frame(self.main) 
        frame.grid(row = 2, column = 0, columnspan = 4, sticky = "NSEW")            
        
        #Create a frame for adding new words
        self.main_action_frame = tk.LabelFrame(frame) 
        self.main_action_frame.config(font=("Consolas", 10), relief = "groove", borderwidth = 3)
        self.main_action_frame.grid(row = 0, column = 0, padx = 10, pady = 10,sticky = ("WE"))
        
        #Label to show the word the user has selected
        self.view_word_label = C_Label(self.main_action_frame)
        self.word_selected = C_Label(self.main_action_frame) #Label in which actual chosen word is displayed
        self.word_selected.set_width(15)
        
        #Word description
        self.description_label = C_Label(self.main_action_frame)
        self.view_description_label = C_Label(self.main_action_frame) #Label in which actual description is shown
        self.view_description_label.set_wraplength(500, "left")
        
        #Label for sign image
        self.image_label = C_Label(self.main_action_frame)
        
        #Label to display the selected image
        self.selected_image = C_Label(self.main_action_frame)
        self.selected_filepath = C_Label(self.main_action_frame)
        
        #Entrybox to enter new word to be saved
        self.add_word_entry = tk.Entry(self.main_action_frame)
        self.add_word_entry.config(validate = "all", validatecommand = (self.add_word_entry.register(self.validate_add_entry), "%P"))
        
        #Entrybox to enter an alternate word to change current word to
        self.change_word_entry = tk.Entry(self.main_action_frame)
        self.change_word_entry.config(validate = "all", validatecommand = (self.change_word_entry.register(self.validate_change_entry), "%P"))
        
        #Textbox to enter word sign description
        self.description_entry = tk.Text(self.main_action_frame)
        
        #Button used to select filepath for image
        self.select_filepath_button = C_Button(self.main_action_frame)
        self.select_filepath_button.set_command(self.select_filepath)
        
        self.image_filepath = None #No initial filepath
        
        #Save new word into database button
        self.save_new_word_button = C_Button(self.main_action_frame, "Add word")
        self.save_new_word_button.set_command(self.save_new_word)
        
        #Extra label which is changed based on what the screen is. 
        self.extra_label = C_Label(self.main_action_frame)
        
        #Update record button (user clicks to update records)
        self.update_word_button = C_Button(self.main_action_frame, "Update word")
        self.update_word_button.set_command(self.update_word_command)
        
        #Delete records button (user clicks to delete record)
        self.delete_records_button = C_Button(self.main_action_frame, "Delete word")
        self.delete_records_button.set_command(self.delete_record_command)
        
        #View word Details (to access view screen)
        view_word_button = C_Button(self.main)
        view_word_button.set_text("View Word Details")
        view_word_button.set_state("active")
        view_word_button.set_command(lambda: self.view_button_command(self.main_action_frame)) 
        view_word_button.arrange_on_grid(1,0,sticky =("WE"))
        
        #Modify word button (to access modify screen)
        modify_word_button = C_Button(self.main)
        modify_word_button.set_text("Modify Word Details")
        modify_word_button.set_state("active")
        modify_word_button.set_command(lambda: self.modify_button_command(self.main_action_frame))
        modify_word_button.arrange_on_grid(1,1,sticky =("WE"))
            
        #Add word button (to access add screen)
        add_word_button = C_Button(self.main)
        add_word_button.set_text("Add New Word")
        add_word_button.set_state("active")
        add_word_button.set_command(lambda: self.add_button_command(self.main_action_frame)) 
        add_word_button.arrange_on_grid(1,2,sticky =("WE"))
    
        #Delete word button (to access delete screen)
        delete_word_button = C_Button(self.main)
        delete_word_button.set_text("Delete Word")
        delete_word_button.set_state("active")
        delete_word_button.set_command(lambda: self.delete_button_command(self.main_action_frame)) 
        delete_word_button.arrange_on_grid(1,3,sticky =("WE"))
           
        #Create frame to contain listbox of saved words
        saved_frame = tk.LabelFrame(frame) 
        saved_frame.config(text = "Saved words", font=("Consolas", 10), relief = "groove", borderwidth = 3)
        saved_frame.grid(row = 0, column = 1, padx = 10, pady = 10,sticky = ("WE"))
    
        #Listbox + Scrollbar  
        #Listbox
        self.view_list = tk.Listbox(saved_frame, width=30, height=15)
        self.view_list.config(selectmode="single")
        self.view_list.bind('<<ListboxSelect>>',self.listbox_select)
        
        #Get words into listbox
        self.update_listbox()
        self.view_list.pack(side = 'left',fill = 'y' , padx = 10, pady = 10)
        
        #Scrollbar
        view_scrollbar = tk.Scrollbar(saved_frame, orient="vertical", command=self.view_list.yview)
        self.view_list.config(yscrollcommand = view_scrollbar.set) #Sets scrollbar to scroll vertically
        view_scrollbar.pack(side = 'left',fill = 'y' , pady = 10)
        
        #Default option chosen when opened
        self.view_button_command(self.main_action_frame)
    
    #Add widgets onto the screen
    def run_menu(self):
        self.add_widgets()
