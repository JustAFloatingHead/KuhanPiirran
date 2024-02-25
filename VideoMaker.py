import cv2
import os
import tkinter as tk
from tkinter import filedialog
import numpy as np
import PngMaker
import Geometry
from moviepy.editor import VideoFileClip, clips_array, ColorClip




def open_video(video_file):
    # Open the video file
    video = cv2.VideoCapture(video_file)
    # Check if the video opened successfully
    if not video.isOpened():
        print("Error: Unable to open video file")
        exit()
    # Read and display video frames
    while True:
        # Read a frame from the video
        ret, frame = video.read()
        # Check if frame is empty (end of video)
        if not ret:
            break

        # Display the frame
        cv2.imshow('Video', frame)

        # Wait for 'q' key to exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # Release the video object and close windows
    video.release()
    cv2.destroyAllWindows()



#this is a class for taking a single video and modify its properties
class VideoModify:
    def __init__(self, input_video):
        self.input_video = input_video

    def adjust_frame_rate(self, output_fps):
        clip = VideoFileClip(self.input_video)
        modified_clip = clip.set_fps(output_fps)
        return modified_clip


    def combine_modifications(self, frame_rate=None, color=None):
        clip = VideoFileClip(self.input_video)
        if frame_rate is not None:
            clip = clip.set_fps(frame_rate)
        if color is not None:
            colored_clip = ColorClip(size=clip.size, color=color, duration=clip.duration)
            clip = clips_array([[clip, colored_clip]])
            clip = clip.set_duration(clip.duration)
        return clip



#there are many properties associated with videos, listing them one by one in every method is space and time consuming
#instead we give VideoProperties object as a one single parameter
class VideoProperties: 
    video_dict={}
    key_list=["width","height","fps","ratio","starting_time","ending_time"]

    def __init__(self):
        self.video_dict={}
        self.video_dict["width"]=800 #width of the video
        self.video_dict["height"]=600 #height of the video
        self.video_dict["fps"]=30 # frames per second
        self.video_dict["ratio"]=1 # when picking pngs from videos, ratio means how manyth frame we pick to those pngs
        self.video_dict["starting_time"]=0 #when forming videos or pngs, in which point in time we start the video (in seconds)
        self.video_dict["ending_time"]=1000 # whivh point in time we end

#change value of parameter in dictionary (nothing happens if it is not one from the key_list given in the beginnning)
    def set_values(self,dict):
        for key in dict.keys():
            if key in self.key_list:
                self.video_dict[key]=dict[key]

#change value of one variable
    def set(self,key,value):
        if key in self.key_list:
            self.video_dict[key]=value
        else:
            raise ValueError("not a key")

#returns the parameter, if it is in the dictionary
    def get(self,parameter):
        return self.video_dict[parameter]
    
#return the relevant information about this object
    def info(self):
        print(self.png_dict)



#this class can combine videos in two ways, chronologically by putting one after other or spatially by putting one on top of another
#of course there must be a green screen color which is not shown on top
class VideoCombiner:
    def __init__(self, video1_path, video2_path, output_path):
        self.video1_path = video1_path
        self.video2_path = video2_path
        self.output_path = output_path

    def glue_videos(self,open_in_the_end="True"): #video1 is put first, and then video2 after it
        cap1 = cv2.VideoCapture(self.video1_path)
        cap2 = cv2.VideoCapture(self.video2_path)
        # Get video properties
        width1 = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
        height1 = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps1 = cap1.get(cv2.CAP_PROP_FPS)
        total_frames1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))

        width2 = int(cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
        height2 = int(cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps2 = cap2.get(cv2.CAP_PROP_FPS)
        total_frames2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))

        # Choose the size for the combined video
        combined_width = max(width1, width2)
        combined_height = max(height1, height2)

        # Create video writer for the combined video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can use other codecs like 'XVID', 'MJPG', etc.
        out = cv2.VideoWriter(self.output_path, fourcc, fps1, (combined_width, combined_height))

        # Read and process each frame
        for frame_number in range(total_frames1 +total_frames2):

            if frame_number<total_frames1:
                ret1, frame1 = cap1.read()
                frame1_resized = cv2.resize(frame1, (combined_width, combined_height))
                out.write(frame1_resized)
            else: 
                ret2, frame2 = cap2.read()
                frame2_resized = cv2.resize(frame2, (combined_width, combined_height))
                out.write(frame2_resized)

        # Release video capture and writer objects
        cap1.release()
        cap2.release()
        out.release()
        if open_in_the_end:
            open_video(self.output_path)#opens the video after everything is done

        #videos are "played at the same time" second video is placed on the top of the first, excepts its white space
    def combine_videos(self,open_in_the_end="True"):
        # Open the video files
        cap1 = cv2.VideoCapture(self.video1_path)
        cap2 = cv2.VideoCapture(self.video2_path)

        # Get video properties
        width1 = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
        height1 = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps1 = cap1.get(cv2.CAP_PROP_FPS)
        total_frames1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))

        width2 = int(cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
        height2 = int(cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps2 = cap2.get(cv2.CAP_PROP_FPS)
        total_frames2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))

        # Choose the size for the combined video
        combined_width = max(width1, width2)
        combined_height = max(height1, height2)

        # Create video writer for the combined video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can use other codecs like 'XVID', 'MJPG', etc.
        out = cv2.VideoWriter(self.output_path, fourcc, fps1, (combined_width, combined_height))

        # Read and process each frame
        for frame_number in range(max(total_frames1, total_frames2)):
            ret1, frame1 = cap1.read()
            ret2, frame2 = cap2.read()

            if not ret1 and not ret2:
                break

            #when the shorter video has ended, it is replaced by white frame, using next trick
# If one video is shorter, continue playing the last frame of the shorter video
            frame1_resized=None
            frame2_resized=None
            if not ret1:
                frame1_resized = cv2.resize(frame2, (combined_width, combined_height)) #trick of using frame2 as parameter, ensures existence
                frame1 = cv2.inRange(frame1_resized, (0, 0, 0), (255, 255, 255)) #frame 1 is now white
            else:
                frame1_resized = cv2.resize(frame1, (combined_width, combined_height))

            if not ret2:
                frame2_resized = cv2.resize(frame1, (combined_width, combined_height)) #same here
                frame2 = cv2.inRange(frame2_resized, (0, 0, 0), (255, 255, 255)) #frame 2 is now white
            else:
                frame2_resized = cv2.resize(frame2, (combined_width, combined_height))

            # Create a mask for white pixels in the first video
            white_mask1 = cv2.inRange(frame1_resized, (230, 230, 230), (255, 255, 255))
            black_mask1= cv2.bitwise_not(white_mask1)

            # Create a mask for white pixels in the second video
            white_mask2 = cv2.inRange(frame2_resized, (230, 230, 230), (255, 255, 255))
            black_mask2= cv2.bitwise_not(white_mask2)

            first_yes_second_not_mask= cv2.bitwise_and(black_mask1,white_mask2) #in here white_pixels should be those,
            #where first image has colors, but second has backround color, white

            # Copy pixel color from the first video for areas with white pixels in the second video
            combined_frame = cv2.bitwise_and(frame1_resized, frame1_resized, mask=first_yes_second_not_mask)#mask=cv2.bitwise_not(white_mask)
            combined_frame += cv2.bitwise_and(frame2_resized, frame2_resized, mask=cv2.bitwise_not(first_yes_second_not_mask))

            # Write the combined frame to the output video
            out.write(combined_frame)

        # Release video capture and writer objects
        cap1.release()
        cap2.release()
        out.release()
        if open_in_the_end:
            open_video(self.output_path)#opens the video after everything is done



#this class is given an input path which is a folder, the folder should contain image files like pngs
#convert_to_video method then turns those image files to animation/video        
class PngToVideoConverter:
    image_formats = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif")
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    #turns image files in the folder to video, note thay this doesnt ask if video with this name already exists and is now overwritten 
    def convert_to_video(self, output_video_path, frame_rate=30): 
        # Get all image files in the directory
        image_files = sorted([f for f in os.listdir(self.input_path) if f.lower().endswith(self.image_formats)])

        if not image_files:
            print("No image files found in the specified directory.")
            return


        # Get the dimensions of the largest image
        max_height, max_width = 0, 0
        for image_file in image_files:
            image_path = os.path.join(self.input_path, image_file)
            img = cv2.imread(image_path)
            height, width, _ = img.shape
            max_height = max(max_height, height)
            max_width = max(max_width, width)

        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can use other codecs like 'XVID', 'MJPG', etc.
        video_writer = cv2.VideoWriter(output_video_path, fourcc, frame_rate, (max_width, max_height))

        # Write PNG frames to video
        for image_file in image_files:
            image_path = os.path.join(self.input_path, image_file)
            img = cv2.imread(image_path)

            # Resize image to match the dimensions of the largest image
            img_resized = cv2.resize(img, (max_width, max_height))

            # Write the resized image to video
            video_writer.write(img_resized)

        video_writer.release()
        open_video(output_video_path)#opens the video after everything is done





class VideoToPngConverter:
    MAX_FRAMES = 10000  # Set the maximum number of frames
    image_formats = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif")
    def __init__(self, input_path, output_path):


        self.input_path = input_path
        self.output_path = output_path

    def convert_to_png(self,ratio:int): #for example if ratio=2 half of the frames are converted
        if ratio<1:
            ratio=1
        # Read video file
        cap = cv2.VideoCapture(self.input_path)

        # Create output directory if it doesn't exist
        os.makedirs(self.output_path, exist_ok=True)


        # Read frames and save as PNG images
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret or frame_count >= self.MAX_FRAMES:
                break

            frame_count += 1
            if frame_count%ratio != 0:
                continue
            image_filename = os.path.join(self.output_path, f"frame_{frame_count:04d}.png")
            cv2.imwrite(image_filename, frame)

        cap.release()

    #this takes video 'filename' taking every 'ratio'nth frame from it and turning it into Drawing, This Drawings are in turn
    #saved as pngs of which new video is formed with 'savename'
    #style tells the way we produce the image, options currently included are polygon, but we also want to have rectangle, triangle and simple
    def video_to_animation(self,output_directory_png,savename,ratio,prop:PngMaker.PngProperties):
        #input_video_file = pick_file("Select Input Video File", [("Video Files", "*.mp4")])
        #output_directory_png = pick_directory("Select Output Directory for PNGs")
        remove_files_in_drawing_animations() # this empties the folder where we put new png images
        self = VideoToPngConverter(self.input_path, output_directory_png)
        self.convert_to_png(ratio)
        image_files = sorted([f for f in os.listdir(output_directory_png) if f.lower().endswith(self.image_formats)])
        i=0
        for image_file in image_files: #we now have realistic pngs from video frames, we turn them into drawings (strings)
            i += 1
            image_path = os.path.join(output_directory_png, image_file) #image_file is just the name, so the directory path must be joined to it
            PngMaker.from_photo_to_cartoon(image_path,prop,image_path)# no savename lets see what happens ,name_of_drawing_str)
        p_to_v=PngToVideoConverter(output_directory_png,"animations") #pngs were in animations subdir and video is also put there
        p_to_v.convert_to_video("animations/"+savename+".mp4",int(30/min(30,ratio))) #if for example every 15th  frame from video is taken, then 2 of them us
        #shown in one second, minimum frame rate is 1 per second




#this saves a text_file with text "file_text" and name 'filename'
def save_text_file(file_text:str,filename:str):
    with open(filename,"w") as file:
    # Write the string to the file
        file.write(file_text)

def load_text_file(filename):
    with open(filename, "r") as file:
        # Read the contents of the file into memory
        instructions=file.read()
    return instructions

#directory is chosen directly, but without seeing which files are inside
def pick_directory(title):
    root = tk.Tk()
    root.withdraw()
    directory_path = filedialog.askdirectory(title=title)
    return directory_path

#directory is picked by using one file in this directory
def pick_directory_using_file(filetypes,initialdir=None):
    root = tk.Tk()
    root.withdraw()
    if initialdir != None:
        file_path = filedialog.askopenfilename(title="Choose any file in the folder to be processed", filetypes=filetypes,initialdir=initialdir)
    else:
        file_path = filedialog.askopenfilename(title="Choose any file in the folder to be processed", filetypes=filetypes)
    #directory_path = filedialog.askdirectory(title=title) old version
    directory_path=os.path.dirname(file_path)
    return directory_path

def pick_file(title, filetypes):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    return file_path

#produces a list of filenames in directory and its subdirectories
def list_files(directory):
    file_list=[]
    for root, _, files in os.walk(directory):
        for file in files:
            name_including_directory=os.path.join(root, file) #this name might looklike drawings\\kuva.png foo example
            file_list.append(name_including_directory[name_including_directory.find("\\")+1:]) #takes the directory out of name
    return file_list

#this empties the place where drawings for animations are temporarily stored
def remove_files_in_drawing_animations():
    directory="drawings/animations"
    file_list=list_files(directory)
    for file in file_list:
        os.remove("drawings/animations/"+file)
    file_list=list_files(directory)


if __name__ == "__main__":
    # Initialize VideoModify object with input video
    #video_modifier = VideoModify("animations/newthing.mp4")

    # Adjust frame rate
    #modified_clip_frame_rate = video_modifier.adjust_frame_rate(output_fps=14)

    # Adjust color
    #modified_clip_color = video_modifier.adjust_color(output_color=[120, 20, 40])  # Adjust color as per RGB values

    # Combine modifications
    #modified_clip_combined = video_modifier.combine_modifications(frame_rate=54, color=[120, 20, 40])

    # Export modified clips
    #modified_clip_frame_rate.write_videofile("animations/aikatikkarikone.mp4")
    #modified_clip_color.write_videofile("animations/varikastikkarikone.mp4")
    #modified_clip_combined.write_videofile("animations/sekatikkarikone.mp4")



    # Example usage
    #video_combiner = VideoCombiner("animations//noccojuttu.mp4", "animations//noccotaas.mp4", "animations//noccovideo.mp4")
    #video_combiner.glue_videos()

    #video_combiner2 = VideoCombiner("animations//Long Anakin.mp4", "animations//Heitto Anakin.mp4", "animations//Anakin throw.mp4")
    #video_combiner2.combine_videos()
    print("Video combination complete. Output saved at: output_combined.mp4")
    #print("SEURAAVAKSI KORJAA, NOPEAN VIDEON PITÄÄ PYSYÄ NOPEANA COMBINOINNISSA HITAAN VIDEON KANSSA")


    # Example usage for PngToVideoConverter
    #input_directory = pick_directory("Select Input Directory")
    #output_directory_video = pick_directory("Select Output Directory for Video")
    #png_to_video_converter = PngToVideoConverter(input_directory, output_directory_video)
    #output_video_path = os.path.join(output_directory_video, "animations/Kaikki.mp4")
    #png_to_video_converter.convert_to_video(output_video_path,frame_rate=30)
    #print(f"Conversion complete. Video saved at: {output_video_path}")

    # Example usage for VideoToPngConverter
    #input_video_file = "animations//Kaikki.mp4" #pick_file("Select Input Video File", [("Video Files", "*.mp4")])
    #output_directory_png = "animations/Kaikki2" #pick_directory("Select Output Directory for PNGs")
    #video_to_png_converter = VideoToPngConverter(input_video_file, output_directory_png)
    #video_to_png_converter.convert_to_png(ratio=1)
    #video_to_png_converter.video_to_animation(output_directory_png,savename="revontuli2",contr_points=10,ratio=15,percentage_limit=0.2,min_angle=10,end_contrast=2,color_divisions=10,style="triangle")
 
    print("KOLMIOALGORITMI VAATII JOKAISEN txt TIEDOSTON TALLENTAMISTA ERIKSEEN, polygon ei tarvitse")
    print("korjaa ettei enää tarvitsisi")
    print("Pääohjelman puolella ei vielä ole korjattu video_to_animation parametrejä joita on tullut lisää")

    #for file in os.path.
