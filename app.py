# import the necessary packages
import datetime

class FPS:

    #This class reads FPS            
	def __init__(self):
		# store the start time, end time, and total number of frames
		# that were examined between the start and end intervals
		self._start = None
		self._end = None
		self._numFrames = 0
	def start(self):
		# start the timer
		self._start = datetime.datetime.now()
		return self
	def stop(self):
		# stop the timer
		self._end = datetime.datetime.now()
	def update(self):
		# increment the total number of frames examined during the
		# start and end intervals
		self._numFrames += 1
	def elapsed(self):
		# return the total number of seconds between the start and
		# end interval
		return (self._end - self._start).total_seconds()
	def fps(self):
		# compute the (approximate) frames per second
		return self._numFrames / self.elapsed()



# import the necessary packages
from threading import Thread
import cv2
class WebcamVideoStream:
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

# NOW the core
# import the necessary packages
# from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS
from collections import deque
import argparse
import imutils
import cv2
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=100,
	help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
	help="Whether or not frames should be displayed")
args = vars(ap.parse_args())


green_lower  = (0, 128, 154)
green_upper = (70, 255, 255)

pen_radius = 8

# These Variables are required by the detection part
buffer = 20
pts = deque(maxlen=buffer)
tracker_point_color = (255,0,0)
tracker_circle_color = (0,0,255)
tracker_tail_color = (0,255,0)

source = 'http'
#this list variable has all the color codes in bgr form
colors = [  
    (0,0,255),    #red
    (0,255,0),    #green
    (255,0,0)     #blue
]
#fotage from webcam.
# Comment the next line to channel video fotage through webcam
#source = 0

#give some time to cam to start. 2 seconds is somewhat enough. But this is not required in case of web fotage.
# time.sleep(2.0)

# Variables for color selection
# the current_color variable is a int type variable that ,in the whole program, can take values of 0,1,2 each reffering to its specified color below
current_color = 0     #default 0 for red
pen_radius  = 10        #default
MarksHistory = [[],[],[]]       #this variable has all the history of pen marks( locations where the pointer has bee detected).
# This is a multi dimesional Variable, each new element in this variable is new type of pen.
# 
# example [
#            [ [*This will contain all the red pixel location*],[*This will contaion all the green pixel locations*],[*And so on.*],[] ]
#               ]
#   Full map of the array: red -> 0, green ->1, blue -> 2;
# 


DrawingPaused=False     # this is a flag variable that tells us if the user wants to draw to the screen or not. (YES->False/NO->True)


source = 'http://192.168.29.244:8080/video'
source = 0

def runMe():
    current_color = 0
    pen_radius = 1
    DrawingPaused = False
    MarksHistory = [[],[],[]]
    # created a *threaded* video stream, allow the camera sensor to warmup,
    # and start the FPS counter
    print("[INFO] sampling THREADED frames from webcam...")
    vs = WebcamVideoStream(src=source).start()
    fps = FPS().start()
    # loop over some frames...this time using the threaded stream
    while True:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        frame = vs.read()
        frame = imutils.resize(frame, width=400)

        #reading the frame
        frame = vs.read()
        frame = cv2.flip(frame,1)
        frame = imutils.resize(frame, width=600)            #resize the window to make it small. width can be changed height adjust itsel accordingly
        blurred = cv2.GaussianBlur(frame, (11,11), 0)       #Bluring the image
        #converting in hsv.
        hsv = cv2.cvtColor(blurred,cv2.COLOR_BGR2HSV)
        #getting the mask ready.
        mask = cv2.inRange(hsv, green_lower, green_upper)
        mask = cv2.erode(mask, None, 5)
        mask = cv2.dilate(mask, None, 5)

        #finding contours..
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        # output = frame.copy()
        center = None
        radius = 325.116455078125           #this is a hard coded value, as some cameras take much more time to stabalize the video stream so for that time the program has a default value of the countor radius instaed of throwing an error
        if len(cnts)>0:
            # getting the x,y location of the tracked point in the current frame
            c = max(cnts, key=cv2.contourArea)
            ((x,y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M['m10']/M['m00']), int(M['m01']/M['m00']))       #this variable has the value

            if radius > 5:
                #Uncomment the below line if you want to have a outer circle around the pointer
                #cv2.circle(frame, (int(x), int(y)), int(radius), tracker_circle_color, 2)   
                cv2.circle(frame, center, 5, tracker_point_color, -1)   #inner Point
                #now we will add the points x and y info to the marks list
                """
                    Now the main logic steps in!
                    the center variable in line 75 has the x,y location of the pointer in current frame
                    we take this location and append it to MarksList variable. Since it is a 2 dimensional array (each dimension reffering to the locations of a specific color, it has)
                    Now the current_color variable decides wether to append the location marks (if DrawingPaused is False) in MarksList[0] i.e red color, or MarksList[1] i.e green color, or MarksList[2] i.e blue color
                    or if DrawingPaused if True, then skip the appending process altogether.

                """
                if not DrawingPaused:
                    MarksHistory[current_color].append(center)

                # print(MarksHistory[-1])
                # Now We will make a small red coloured circle in these points
            """
                Now we start painting the colors on the canvas .
                Since we have all the points / history locations that the pointer has ever been on (& the user intented to paint) in the MarksList variable and they are also 
                color coded, totally depending upon in which sub-dimension element array they were append to. as if some point was appended to MarksList[1] then this point was painted in green(1) color
                Same procedure goes for red(0) & blue(2)
                Now we run a for-loop for each element in MarksHistory , each time this loop runs it gives 'Points' a new sub-dimensional array (that ofcourse refers to a set of points of a color).
                This array is again run through a for-loop to get its unique points , then these points are painted to the screen. the color is decided by Number of iteration of the outer loop and counted
                using the counter 'fl' the value of this counter with colors[] gives the exact color required to paint to the screen.
            """
        fl = -1
        for Points in MarksHistory:
            fl+=1
            for locations in Points:
                clr = colors[fl]
                cv2.circle(frame, locations, pen_radius, clr, -1)
        
        #showing results
        # cv2.imshow("Original", frame)
        cv2.imshow("Mask", mask)
        cv2.imshow("Tracked", frame)
        k = cv2.waitKey(10)
        # print(k)
        if k == 27:
            # Key code 27 is for ESC key to exit the program.
            break
        if k == 8:
            # clear the canvas 
            MarksHistory = [[],[],[]]
        # Now starting color selection using keyboard keys
        # COLOR     KEYS
        # RED       R
        # GREEN     G
        # BLUE      B
        # Purple    P
        # YELLOW    Y

        print(k)
        if k == 114:
            current_color=0
            print('RED COLOR CHOSEN')
        if k == 103:
            current_color=1
            print('GREEN COLOR CHOSEN')
        if k == 98:
            current_color=2
            print('BLUE COLOR CHOSEN')
        
        if k==82:
            pen_radius+=1
        if k==84:
            if pen_radius!=0:
                pen_radius-=1

        if k == 112:
            current_color=2
            if DrawingPaused:
                print('Drawing Resumed (Press p again to pause)')
                DrawingPaused=False
            else:
                print('Drawing Paused (Press p again to resume)')
                DrawingPaused=True


        # check to see if the frame should be displayed to our screen
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 127:
            break
        # update the FPS counter
        fps.update()
        # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()

runMe()
