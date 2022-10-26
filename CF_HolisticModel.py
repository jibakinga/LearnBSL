# -*- coding: utf-8 -*-
"""
Created on Sat Dec 18 20:21:45 2021

@author: MinahilF
"""

#Image is set as non writeable to pass by reference to improve performance.'''
#Landmark specs then connection specs
#Colour codes need to be in RGB since image is fed through RGB

#Import appropriate libraries
import mediapipe as mp #For hand recognition models
import cv2 #For image and video processing

class C_holistic_model:
    #Initialise model
    mp_holistic = mp.solutions.holistic #Creates a holistic model object 
    model = mp_holistic.Holistic(min_detection_confidence=0.6, min_tracking_confidence=0.1)
    
    def __init__(self, video_frame):
        self.mp_drawing = mp.solutions.drawing_utils #Provides drawing utilities for drawing connections within the image
        self.image = video_frame
     
    def get_landmarks(self):
        #Convert the BGR image to RGB.
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.image.flags.writeable = False #Image -> NOT Writeable 
        results = C_holistic_model.model.process(self.image) #Get landmarks from the processed image
        self.image.flags.writeable = True #Image -> Writeable
        return results
        ##Returns landmark_array

    #Show holistic landmarks
    def show_landmarks(self,results):  
        #Draw Face Landmarks onto frame
        self.mp_drawing.draw_landmarks(self.image, results.face_landmarks, 
                                      C_holistic_model.mp_holistic.FACEMESH_CONTOURS,
                                      #Landmark specs
                                      self.mp_drawing.DrawingSpec(
                                                                color=(153, 255, 255), 
                                                                thickness=1, 
                                                                circle_radius=1),
                                      #Connection specs                 
                                      self.mp_drawing.DrawingSpec(
                                                                color=(102, 255, 255), 
                                                                thickness=1, 
                                                                circle_radius=1)
                                      )
        
        #Draw Left Hand Landmarks
        self.mp_drawing.draw_landmarks(
                                      self.image, 
                                      results.left_hand_landmarks, 
                                      C_holistic_model.mp_holistic.HAND_CONNECTIONS,
                                      #Landmark specs
                                      self.mp_drawing.DrawingSpec(color=(255, 255, 102), 
                                                                  thickness=1, 
                                                                  circle_radius=1),         
                                      #Connection specs                 
                                      self.mp_drawing.DrawingSpec(
                                                                color=(255, 255, 51), 
                                                                thickness=2, 
                                                                circle_radius=1)
                                      ) 
        
        #Draw Right Hand Landmarks
        self.mp_drawing.draw_landmarks(
                                      self.image, 
                                      results.right_hand_landmarks, 
                                      C_holistic_model.mp_holistic.HAND_CONNECTIONS,
                                      #Landmark specs
                                      self.mp_drawing.DrawingSpec(
                                                                color=(255, 255, 102), 
                                                                thickness=1, 
                                                                circle_radius=1),
                                      #Connection specs             
                                      self.mp_drawing.DrawingSpec(
                                                                color=(255, 255, 51), 
                                                                thickness=2, 
                                                                circle_radius=1)
                                      )
        
        #Draw Pose Landmarks
        self.mp_drawing.draw_landmarks(
                                      self.image, 
                                      results.pose_landmarks, 
                                      C_holistic_model.mp_holistic.POSE_CONNECTIONS,
                                      #Landmark specs
                                      self.mp_drawing.DrawingSpec(
                                                                color=(255, 255, 255), 
                                                                thickness=2, 
                                                                circle_radius=1),
                                      #Connection specs                
                                      self.mp_drawing.DrawingSpec(
                                                                color=(192,192,192), 
                                                                thickness=2, 
                                                                circle_radius=1)
                                      )
        return self.image
    ##returns frame with landmarks drawn on
