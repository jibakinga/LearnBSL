# -*- coding: utf-8 -*-
"""
Created on Sat Dec 18 20:21:45 2021

@author: MinahilF
"""

import mediapipe as mp #For hand recognition models
import cv2 #For image and video processing


class C_holistic_model
    
    
    def get_landmarks(self):
        #Convert the BGR image to RGB.
        image <- Convert image from BGR to RGB
           
        image <- flag as non-writeable #Image -> NOT Writeable
        
        results <- get landmarks from image #Get landmarks from the processed image
    
        image <- flag as writeable  #Image -> Writeable
        
        return results
        ##returns landmark_array