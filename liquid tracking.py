import cv2
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox

#use .mp4 files

def tracking(video_path, pixels_per_mm, display_scale, zero_point_mm):
    #read the video file
    video = cv2.VideoCapture(video_path)
    if not video.isOpened(): #did OpenCV successfully open the video file?
        raise ValueError("Could not open the selected video file.")

    fps = video.get(cv2.CAP_PROP_FPS) #finds the fps of the video
    if fps <= 0:
        raise ValueError("Could not find the FPS.")

    ret, frame = video.read() #reads video frame that the loop is on, ret is a boolean that is true if the frame was read correctly
    if not ret: 
        raise ValueError("The selected video file does not contain any frames.")

    #get video dimensions
    video_height, video_width = frame.shape[:2] #gets the height and width of the video frame

    display_width = int(video_width * display_scale)
    display_height = int(video_height * display_scale)

    #format the video window
    cv2.namedWindow("Liquid tracking", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Liquid tracking", display_width, display_height)

    #defining the measurements for region of interest (ROI) for the liquid tracking
    #gives rectangle that is 100 pixels wide
    roi_top = int(video_height / 4)
    roi_bottom = int(video_height * 3 / 4)
    roi_left = int(video_width / 2 - 50)
    roi_right = int(video_width / 2 + 50)

    times = []
    heights = []
    frame_number = 0

    while ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #turns the frame to grayscale
        roi = gray[roi_top:roi_bottom, roi_left:roi_right] #defines the region of interest for the frame in grayscale
        roi_height, roi_width = roi.shape #finds the height and width of the region of interest

        center_x = int(round(roi_width / 2)) #center of the x-coordinate of the roi
        band = roi[:, center_x - 2:center_x + 2 + 1] #defines a vertical strip through the roi

        band = cv2.GaussianBlur(band, (5, 5), 0) #applies Gaussian blur to the band for noise reduction

        gradient = np.abs(np.diff(band.astype(np.float32), axis=0)) #calculates the gradient of the band
        gradient = np.mean(gradient, axis=1) #calculates the mean of the gradient

        if gradient.size > 0: #if the gradient is not empty
            meniscus = int(np.argmax(gradient)) #finds the position of where the gradient changes the most, which is the meniscus position
        else:
            meniscus = 0

        global_y = roi_top + meniscus #calculates the global y-coordinate of the meniscus
        liquid_height_pixels = (video_height - 1) - global_y #measures the height from the bottom of the video in pixels
        time = frame_number / fps #calculates the time for each frame

        times.append(time) 
        heights.append(liquid_height_pixels)

        global_x = roi_left + center_x #calculates the global x-coordinate of the meniscus

        cv2.line(frame, (global_x, roi_top), (global_x, roi_bottom), (255, 0, 0), 1) #draws a vertical line through the meniscus position in the frame
        cv2.circle(frame, (global_x, global_y), 5, (0, 0, 255), -1) #draws a red circle at the meniscus position in the frame

        if zero_point_mm is not None:
            zero_point_y = int(round(video_height - zero_point_mm * pixels_per_mm))
            zero_point_y = max(0, min(video_height - 1, zero_point_y))
            cv2.line(frame, (0, zero_point_y), (video_width - 1, zero_point_y), (0, 255, 0), 1)

        display_frame = cv2.resize(frame, (display_width, display_height)) #resizes the frame for display
        cv2.imshow("Liquid tracking", display_frame) #shows frame with tracking marker

        frame_number += 1 

        if cv2.waitKey(max(1, int(1000 / fps))) & 0xFF == ord("q"): #makes it so you can end the video early by pressing "q"
            break

        ret, frame = video.read() #reads the next frame in the video

    video.release()
    cv2.destroyAllWindows() #closes all OpenCV windows

    if len(times) == 0: #if no data was collected, an error message shows up
        print("No data collected to plot.")
        return

    heights_mm = [h / pixels_per_mm for h in heights] #converts the liquid height from pixels to mm
    if zero_point_mm is None:
        relative_heights_mm = heights_mm
    else:
        relative_heights_mm = [h_mm - zero_point_mm for h_mm in heights_mm] #measures oscillations around the chosen zero point

    #plotting results
    plt.figure(figsize=(10, 5))
    plt.plot(times, heights, color="blue")
    plt.xlabel("Time (s)")
    plt.ylabel("Liquid height (pixels)")
    plt.title("Liquid oscillations (pixels)")
    plt.grid()

    plt.figure(figsize=(10, 5))
    plt.plot(times, relative_heights_mm, color="green")
    plt.xlabel("Time (s)")
    plt.ylabel("Liquid height relative to zero point (mm)")
    plt.title("Liquid oscillations around chosen zero point (mm)")
    plt.grid()
    plt.show()

    with open("liquid_heights.txt", "w", encoding="utf-8") as file:
        if zero_point_mm is None:
            file.write("Time (s)\tLiquid height from bottom of video (mm)\n")
        else:
            file.write("Time (s)\tLiquid height relative to zero point (mm)\n")
        for t, h in zip(times, relative_heights_mm):
            file.write(f"{t:.4f}\t{h:.4f}\n")

#code for the interface
def main(): 
    main_window = tk.Tk() #creates the main window
    main_window.title("Liquid tracking")
    main_window.geometry("660x350")
    main_window.resizable(False, False)

    tk.Label(main_window, text="Select a video file to track the meniscus", font=("Arial", 11)).pack(pady=(16, 8))

    video_path = tk.StringVar() #lets the user select a video file to track the meniscus
    pixels_per_mm = tk.StringVar(value="") #lets the user input the number of pixels per mm (hopefully this can be calculated automatically in the future)
    display_scale = tk.StringVar(value="0.5") #lets the user input the scale factor for displaying the video, standard is 0.5
    zero_point_mm = tk.StringVar(value="") #lets the user choose a reference height above the bottom of the video; empty means use bottom of video

    def browse_video(): #function that lets the user select a video file to track the meniscus
        path = filedialog.askopenfilename(title="Select video", filetypes=[("Video files", "*.mp4 *.mov"), ("All files", "*.*")],) #lets the user select a video file to track the meniscus
        if path: 
            video_path.set(path) #video_path is set to the path of the selected video file
            status_label.config(text=f"Selected: {path}") #updates the status label to show the selected video file path

    def start_tracking(): #function that starts the tracking process
        if not video_path.get(): #stops tracking if no video is selected and shows an error message
            messagebox.showerror("No video selected", "Please choose a video file first.")
            return

        try:
            pixels = float(pixels_per_mm.get()) #converts the pixels per mm to a float
            scale = float(display_scale.get()) #converts the display scale to a float
            zero_point_text = zero_point_mm.get().strip()
            zero_point = float(zero_point_text) if zero_point_text else None
        except ValueError:
            messagebox.showerror("Invalid value", "Please enter valid numbers for pixels per mm and display scale.")
            return

        main_window.destroy() 

        try: #tries to run the tracking function, if it fails an error message shows up
            tracking(video_path.get(), pixels, scale, zero_point) 
        except Exception as exc:
            messagebox.showerror("Tracking failed", str(exc))

    tk.Button(main_window, text="Browse video", command=browse_video, width=18).pack(pady=4) #creates a button that lets the user select a video file to track the meniscus
    status_label = tk.Label(main_window, text="No video chosen yet", fg="gray40") #creates a label that shows the status of the video selection
    status_label.pack(pady=4)

    tk.Label(main_window, text="Pixels per mm:").pack(pady=(8, 2)) #creates a label that lets the user input the number of pixels per mm
    tk.Entry(main_window, textvariable=pixels_per_mm, width=12).pack() #creates an entry field for the user to input the number of pixels per mm

    tk.Label(main_window, text="Display scale factor:").pack(pady=(8, 2)) #creates a label that lets the user input the scale factor for displaying the video
    tk.Entry(main_window, textvariable=display_scale, width=12).pack() #creates an entry field for the user to input the scale factor

    tk.Label(main_window, text="Zero-point height above bottom (mm):").pack(pady=(8, 2)) #creates a label that lets the user choose the reference height for oscillations
    tk.Entry(main_window, textvariable=zero_point_mm, width=12).pack() #creates an entry field for the zero-point height
    tk.Button(main_window, text="Start tracking", command=start_tracking, width=18).pack(pady=10) #creates a button that starts the tracking process

    main_window.mainloop() #starts the main loop

main()