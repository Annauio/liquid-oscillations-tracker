This code lets the user track the oscillations of a liquid being pushed into a vertical tube. 
This is done by creating a rectangle in the middle of the video being used. The rectangle has a width of 100 pixels and higth that is dependant on the height of the video (from 1/4 to 3/4 of the video).
The video is turned into greyscale and then the biggest change in the gradient in the rectangle is tracked. This is the meniscus. For this to work best, the liquid has to be dark, and not seethrough like water. In the example video the liquid is water dyed with red and blue food coloring. 

When you run the code, you should see a window pop up. This window will let the user the video they want to use from the files folder.
Under the "Browse video"-button, there are some more options for the tracking. 
Firstly, the has to write inn how many pixels one millimeter is in the video. This has not been implemented in the code, and has to be done manualy. For the example video 1 mm = 34.52 pixels. This has to be added because the code tracks the amount of pixels the liquid oscillates and then it converts this to mm. 
Secondly, the user can choose the display factor. This is because high resolution videoes can show up so big that the user cannot see the whole video while it is being tracked. The default value is 0.5 (50% smaller). This does not affect the tracking results. 
Thirdly, the user is able to choose at which height they want the "zero-line" to be. This is where the graph will be zero. If no value is written, then the graph will be plottet with the bottom of the video as the "zero-line".

After all the information is filled in, the user presses the "Satrt tracking"-button, and the video will pop up. There will also be displayed a blue, vertical line in the middle of the video that shows where the tracking is done, and on top of that line is a red circle that shows where the meniscus is. This lets the user see if the tracking is working and that the chosen area is correct. 
If the user has chosen a zero-line that is not the bottom of the video, a green, horisontal line will also be shown. This is the chosen zero-line. 

The whole video thas to be play to get all the data. The tracking can be stopped early by pressing "q", but this will cause the graph to only display data up until the point that the video was closed.

After the tracking is done, the graph for both millimeters and pixels will show up, showing the liquid oscillations. 

The code also collects all the datapoints in a .txt fil ecalled "liquid_heights.txt".
