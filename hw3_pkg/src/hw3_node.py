#!/usr/bin/env python
import cv2
import numpy as np
import rospy
import os
import math
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from Turtle import *
list = []

def find_path(path):
    """
        Function to find the opencv contours 
        - open image
        - convert to grayscale
        - apply treshholding
        - find the contours
        :param path: path to image
        :type string: string of the path
        :return contours: array of opencv contours
    """
    package_path = os.path.dirname(os.path.abspath(__file__))
    data_file_path = os.path.join(package_path, path)
    print(data_file_path)
    # Read the image
    image = cv2.imread(data_file_path)
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply a threshold to the grayscale image
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # Find the contours in the binary image
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def contour_to_accessible_format(contours):
        collection_points = []
        collection_segments = []
        collection_groups = []
        """
        Function to convert the opencv contours to accessible data format
        - Collection of x,y coordinates is a point
        - Collection of points is a segment
        - Collection of segments is a group
        - Collection of groups is a contour
        :param contours: Extracted contours from the image
        :type contours: opencv contours
        """
        print(int((len(contours))/2))
        for i in range(int((len(contours))/2)):  # For all the contours
            if len(contours[i]) > 10:  # If they have more than 10 points
                for j in range(len(contours[i])):  # Find the x,y coordinates of all the points
                    x_cord = (contours[i][j][0][0] * 11) / 500  # Convert points within (11, 11) i.e. size of turtle-sim
                    y_cord = (contours[i][j][0][1] * 11) / 500

                    # Save these coordinates in a list named collection_points and subtract y from 11 to make upright
                    # image
                    collection_points.append((x_cord, y_cord))

                # Collect all line segments in collection_segments list
                collection_segments.append(collection_points)
                collection_points = []

            # Collect all groups in collection_groups list
            collection_groups.append(collection_segments)

        # Collection of all contours in contours
        contours = collection_segments

        # Total number of contours
        numbers = len(contours)+2
        print(numbers)
        # Reset and code flow
        collection_segments = []
        return contours, numbers
def spawn_source(contours, numbers):
        global list
        """
        Spawn multiple turtles on the first point of each contour
        """
          
        rospy.loginfo("Spawning an army of turtles to sketch your image")
        for i in range(numbers):
            
            list.append(Turtle(i + 1))
            if i == 0:
                
                list[0].set_pen(0)
                list[0].teleport(11*contours[i][0][0][0]/500, 11-11*contours[i][0][0][1]/500, 0.0)
                
            else:
                list[i].spawn(11*contours[i][0][0][0]/500, 11-11*contours[i][0][0][1]/500, 0.0)
        return list

def trace(list, contours, numbers):
        """
        Function to trace the contours using sequential programming
        """
        # Take x,y coord. of next point in contour and teleport turtle to that point(for one contour at a time)
        for j in range(numbers):
            for k in range(len(contours[j])):
                list[j].teleport(11*contours[j][k][0][0]/500, 11-11*contours[j][k][0][1]/500, 0.0)
            list[j].teleport(11*contours[j][0][0][0]/500, 11-11*contours[j][0][0][1]/500, 0.0)
                
def kill_destination(list, numbers):
        """
        Remove the turtles from simulation at the end of sketching
        """
        for i in range(numbers):
            list[i].kill_turtle()      
if __name__ == '__main__':
    try:
        # find contours in the image
        contours  = find_path('technion.jpg')
        # check which countours to draw
        countours, numbers = contour_to_accessible_format(contours)
        # spawn the army of turtles at the beginning of each path
        list = spawn_source(contours, numbers)
        #trace the path with each turtle
        trace(list, contours, numbers)
        #remove the turtles
        kill_destination(list, numbers)
    except rospy.ROSInterruptException:
        pass

