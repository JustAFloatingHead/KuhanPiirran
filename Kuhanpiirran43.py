import colorsys
import math
import string
import time
from tkinter import messagebox, scrolledtext
import turtle
import tkinter as tk
import tkinter.colorchooser as colorchooser
import tkinter.filedialog as filedialog
from ast import literal_eval
from os import path 
import os
from tkinter import *
from tkinter import ttk 
import random
import Commands
import MemoryHandler
import Geometry
import Palette
import PngMaker
import VideoMaker
import CsvMaker
import png
import FunctionOperator
from typing import List
from icecream import ic
from PIL import Image, ImageTk
from PIL import ImageDraw, ImageFont
# Set the current working directory to "myfolder"
#os.chdir("OneDrive\Skrivbord\Matematiikan ydin\Python-kuvitukseen")
# Set the color mode to 1.0, for not to write names of the colors to save file
turtle.colormode(1.0)
#turtle.addshape(name="laajennusnuolet.gif",shape=None)
#turtle.addshape(name="pyörre.gif",shape=None)
turtle.speed(0)
turtle.delay(0)
t=turtle.Turtle(visible=False)
t.pencolor([0.5,0.5,0.5])
turtle_screen_bg_color="#ffffff"#this is white, DO NOT CHANGE from this color format
hideorigo=False #if this is true, origo will be hidden by white dot
temp_turtle = turtle.Turtle() #this is used to draw temporary file drawing
spin_turtle = turtle.Turtle(visible=False) #this is used as help to make "spin"-transformations on the image
size_turtle = turtle.Turtle(visible=False) #this is used as help to make stretch in x_axis
rotate_turtle = turtle.Turtle(visible=False) #this is used as help to make stretch in y_axis
layer_data_turtle=turtle.Turtle(visible=False) #this is used as help to make layer-data visual
temp_turtle.pencolor([0.2,0.2,0.2])
temp_turtle.fillcolor([0.6,0.6,0.6])
temp_turtle.shapesize(1.8,1.8,2)#kokeillaan tehdä tätä isommaksi
temp_turtle.penup()
#this executes command_line commands, when turtle screen is clicked
global screen
screen=turtle.Screen() #tarvitaanko tätä? Poistan läpällä?
screen.tracer(0)#välitön piirtäminen
screen.screensize(1500,1200)
screen.title("Kuhan piirran: draw like a pro, or like an ordinary human being")
global past #records old versions of temp_memo...
global layer_past # records old version of layer_items.items
global blueness #currently chosen brighness
blueness=0.5
global palc,palf # palette for color and for fillcolor
palc=Palette.Basic([0,1,0,1,0,1],0.5,[100,100],25,[150,150]) #first two numbers tell the interval of change of blueness and second two interval of redness and the last of blue
#these numbers are associated to choosing color in the panel
palf=Palette.Basic([0,1,0,1,0,1],0.5,[100,100],25,[300,150]) #first two numbers tell the interval of change of blueness and second two interval of redness and the last of blue
#these numbers are associated to choosing color in the panel
past=["","","","",""] #allows five undos index 0 is the most recent
layer_past=["","","","",""]
global DRAWTIME_CONSTANT#how fast a new point for mouse position is gotten when dragging turtle
DRAWTIME_CONSTANT=50
FRAME_CONSTANT=30 #how many frames per second is the initial value in scale of animation
# yodacoor variable tells where we are located in mini-images canvas
QUICK_WIDTH = 800 # when png-s are taken for animation this is the width, if it is not changed
QUICK_HEIGHT = 600 # when   png-s are taken for animation this is the height, if it is not changed
SCALEX=SCALEY = 0.01 #for drawing functions
ORIGOX=ORIGOY = 0.0 #what are the x and y values of the pixel drawn at origo, when function is drawn
yodacoor = None
origomode="show" # while drawing,shows origos of every layer if show, if hide, doesnt show
RECYCLING_ON=True #do we bring back variables like PT or do we leave them there
SCREENSHOTS_ON=False #do we take screenshots after commandline executions

def create_directory(directory_path):
    try:
        os.makedirs(directory_path)
    except FileExistsError:
        that=True #doesn't do anything but something is needed in except block
create_directory("./machinery")

#saves a text file with conten to directory_path/file_name, note that no '.txt' or other filetype is added on the end, if it is not there in the file_name 
def save_text_file(directory_path, file_name, content):
    file_path = os.path.join(directory_path, file_name)
    with open(file_path, 'w') as file:
        file.write(content)



class Layers:
    items=[]
    shortcuts=[]#user can add new shortcut commands here, they are saved into file called usershortcut.txt
    #objektin "rawkesa4" niin, että 
    # objektin mitat on skaalattu 1.5-kertaisiksi ja lähtökulmaa on kallistettu 23 astetta
    # lisäksi piirtäminen aloitetaan asettamalla kuvan origo (x,y)-sijaintiin (2,3), niin että 
    #viimeinen parametri kertoo objektin näkyvyystason. Visible ja active näyttävät samalta, mutta
    #muokkaukset kohdistuvat vain active layeriin
    #invisible ei näy ollenkaan
    example_item4=[2,"texts","simo",[1,1.4],23,45,34,"active",0,0,0,""]#uutena lisäyksenä r, g ja b shiftin arvot. nämä ovat välillä -1.0-1.0
    example_item5=[2,"gif","lalli",[1,1.5],23,45,34,"active",0.1,0.23,0.12,"extra"]#lisäksi viimeinen parametri on tarkoitettu tulevia lisäyksiä varten
    drawing_instructions=[] #here we list drawing_instructions for every drawing used in Layers
    global layer_parameter_dict
    layer_parameter_dict={"depth":0,"type":1,"name":2,"scale":3,"rotation":4,"x shift":5,"y shift":6,"visibility":7,"red":8,"green":9,"blue":10,"extra":11}

    def __init__(self):
        self.items=[]

        create_directory("./pngs")
        create_directory("./files")
        create_directory("./gifs")
        create_directory("./drawings")
        create_directory("./drawings/rsaves")
        create_directory("./drawings/animations")
        create_directory("./animations")



        #the next string is a drawing for simple arrow
        basic_text="£co([0.627, 0.627, 0.627])|fc([0.627, 0.627, 0.627])|sh(0)|ps(5)|pu()|goto(0,0)|"
        basic_text +="pd()|goto(75,0)|sh(150)|pd()|goto(57,9)|sh(330)|"
        basic_text +="pd()|goto(75,0)|sh(210)|pd()|goto(57,-10)|sh(30)|pd()|goto(75,0)|sh(360)|"

        if path.exists("drawings/basic.txt")==False: #this is for the new user starting to use the program
            with open("drawings/basic.txt", "w") as file:
        # Write the string to the file
                 file.write(basic_text)
        self.drawing_instructions=[]


        if path.exists("machinery/mini.txt")==False: #this stores a representation of how popular certain images are for adding to the file
            #this is for the new user starting to use the program 
            #under usual conditions this should just produce empty text.file, but if there are already images in "images"-dir
            #then these are given values, of how "popular" they are, i.e. are they among the first to appear in mini_popup
            # Load all PNG images from the "images" directory
            images_directory = "drawings"
            image_files = [f for f in list_files(images_directory) if f.endswith(".png")]
            minitext="" #text to be added in the txt. file
            index=0 #point of this is to make some initial difference to different pngs.
            for f in image_files:
                index+=1
                f_without_type=f[:-4]
                f_text=f_without_type+".txt"
                if f_text in list_files("drawings"):
                    minitext += f_text+":"+str(0.01*index)+"|"  
            with open("machinery/mini.txt", "w") as file:
        # Write the string to the file
                 file.write(minitext)

        #format of the file: £$kasky1=#goto(10,20)|#jump(20)|€£$kasky2=rect(20,14)|#line(30)|#load(kuva)|€
        #in this example we have to shortcut commands $kasky1 and $kasky2 and when loading the file
        #we get have shortcuts= [$kasky1=#goto(10,20)|#jump(20)|,$kasky2=rect(20,14)|#line(30)|#load(kuva)|]
    #RESTRICTED SYMBOLS $,€,£,|,"=","'". You could possibly use $ but i don't know what would happen

    def get_drawing_instructions(self):
        return self.drawing_instructions
    
    #for example if there is a drawing called lehmä in layer_items. then if instruction_item="lehmä", this returns the drawing orders of "lehmä" 
    #if there is no such item then returns empty str
    def get_drawing_instruction_str(self,instruction_item):
        result=""
        for inst in self.drawing_instructions:
            if inst[0]==instruction_item:
                return inst[1]
        return result
            
    def set_drawing_instructions(self,instruction_number:int,instruction_item:str,instruction_str:str):
        self.drawing_instructions[instruction_number]=[instruction_item,instruction_str]

    def set_drawing_instruction_str(self,instruction_item:str, instruction_str:str):
        for inst in self.drawing_instructions:
            if inst[0]==instruction_item:
                inst[1]=instruction_str



    #adds item, instruction is only added if there is no same file_name in the self already
    def add_item(self,depth:int,type:str,file_name:str,scale:list[float],rotation:int,shift_x:int,shift_y:int,state:str,rs:float,gs:float,bs:float,extra:str,instruction_str:str):
        add_instructions=True
        for i in range(len(self.items)):
            if self.items[i][2]==file_name:
                add_instructions=False
        self.items.append([depth,type,file_name,scale,rotation,shift_x,shift_y,state,rs,bs,gs,extra])
        if add_instructions:
            self.drawing_instructions.append([file_name,instruction_str])

    #when we for example change one layer_item to another, if other layer_str instruction is npt in drawing_instructions already
    #then it must be added with this
    def add_missing_instruction(self,file_name,instruction_str):
        add_instructions=True
        for i in range(len(self.items)):
            if self.items[i][2]==file_name:
                add_instructions=False
        if add_instructions:
            self.drawing_instructions.append([file_name,instruction_str])

    #items are ordered, so that the smaller the ordering parameter is, the smaller the index is in the new_ordering
    def reorder_items(self,ordering_parameter:List[float]):
        items_copy=[]
        for i in range(0,len(self.items)):
            items_copy.append(self.items[i])

        size=len(self.items)
        
        # Using sort + key
        new_ordering_parameter=[]
        for i in range(0,len(ordering_parameter)):
            new_ordering_parameter.append(ordering_parameter[i])

        new_ordering_parameter.sort(key = float)
        order=[]#tähän listataan indeksit järjestykseen, niin, että ensiksi tulee sen indeksin arvo,
        #jonka ordering_parameter on pienin
        for i in range(0,size):
            for j in range(0,size):
                if new_ordering_parameter[i]==ordering_parameter[j] and j not in order:
                    order.append(j)
        for i in range(0,size):
            self.items[i]=items_copy[order[i]]  


    #given a name of parameter e.g. "depth", returns the index where this parameter is stored in self.items.[layer_nro][]
    def layer_parameter_name_to_index(self,parameter_name:str):
        global layer_parameter_dict
        return layer_parameter_dict[parameter_name]

    #given an index of parameter in self.items.[layer_nro][] e.g. 3, returns the name of this parameter e.g. "scale" 
    def layer_index_to_parameter_name(self,index:int):
        global layer_parameter_dict
        for parameter_name in layer_parameter_dict.keys():
            if layer_parameter_dict[parameter_name]==index:
                return parameter_name
        return None

    #given a nro of layer and parameter_name (for example "depth"), the value of this parameter of this layer is set to new_value
    def change_layer_parameter(self,layer_nro,parameter_name,new_value):
        self.items[layer_nro][self.layer_parameter_name_to_index(parameter_name)]=new_value   

    #returns the value of given layers parameter with name parameter_name
    def get_layer_parameter(self,layer_nro,parameter_name):
        return self.items[layer_nro][self.layer_parameter_name_to_index(parameter_name)]    

    #given a parameter_name (for example "depth"), the value of this parameter is set to new_value in every active layer
    def change_active_layers_parameter(self,parameter_name,new_value):
        for i in range(len(self.items)):
            if self.items[i][7]=="active":
                self.change_layer_parameter(i,parameter_name,new_value)



    #returnstring representation of item:parameters. showmode tells which parameters aren shown
    def item_parameters_to_string(self,item_number,showmode:str):
        result=""
        global db
        if showmode=="normal":
            result=str(item_number +1)+ " " #users are not familiar with starting counting from 0, thus +1
            result=result+"depth:"+str(self.items[item_number][0])+", " 
            #result=result+str(self.items[item_number][1][:-1])+": "
            realname=self.items[item_number][2]
            showname=filename_end(realname+"****")#random 4 symbols in the end are needed since filenma:end swallows them
            result=result+showname[0:8]+", "#testing [0:8] showname trick was added 20.7. 
            result=result+"sc: ("+str(self.items[item_number][3][0])[0:4]+"," +str(self.items[item_number][3][1])[0:4]+"), "
            result=result+"rot.: "+str(self.items[item_number][4])+", "
            result=result+"shift: ("+str(self.items[item_number][5])+", "+str(self.items[item_number][6])+"), "
            result=result+self.items[item_number][7]
        if showmode=="color":
            result=str(item_number +1)+ " " #users are not familiar with starting counting from 0, thus +1
            result=result+"depth:"+str(self.items[item_number][0])+", "
            result=result+str(self.items[item_number][2])[0:8]+", "#testing [0:8]
            result=result+"red: "+str(self.items[item_number][8])[0:5]+", " #
            result=result+"green: "+str(self.items[item_number][9])[0:5]+", "
            result=result+"blue: "+str(self.items[item_number][10])[0:5]
        
        if showmode=="variables":
            result=""
            variable_list=db.variables_as_list()
            if len(variable_list)>item_number:
                result=variable_list[item_number][0][:20]
                if len(variable_list[item_number][0])>20:
                    result +="..."
                result +="="+variable_list[item_number][1][:20]
                if len(variable_list[item_number][1])>20:
                    result +="..."
        
        if showmode=="functions":
            result=""
            function_list=db.function_list
            if len(function_list)>item_number:
                result_array=function_list[item_number].output_model_str.split("==")
                result=result_array[0][:20]
                if len(result_array[0])>20:
                    result +="..."
                result += "==" +result_array[1][0:20]
                if len(result_array[1])>20:
                    result +="..."
        return result


    #gives a string representation of an item with indes item_number, this helps to save old version to use undo ctrl+z
    def item_to_string(self,item_number):
        result=""
        for i in range(0, len(self.items[item_number])):
            result += str(self.items[item_number][i])+"|"
        return result #leaves "|" after extra, this is intentional for a reason too long to explain

    #gives a string representation of this layers items, this helps to save old version to use undo ctrl+z
    def items_to_string(self):
        result=""
        for i in range(0, len(self.items)):
            result += "£"+self.item_to_string(i)
        result += "@"
        for i in range(0, len(self.drawing_instructions)):
            result += "£"+str(self.drawing_instructions[i]) #was "$"+ changed to "£" in 31.8.
        return result.strip("£")
    #this is going to look like [3,"objects",lehmä,...]|[...]@$['lehmä', 'pd()|goto(0,0)|...']$['lammas', pd()|...]...
    

    #takes the str representing items and set this Layers items to match  that description
    def from_str_to_layers(self,layer_str):
        self.items=[]
        if len(layer_str)<10:#this 10 is just random small number. If layer_str is basicly empty, then so must self be.
            return
        super_split=MemoryHandler.split_the_string(layer_str,"@")
        splitted_str=MemoryHandler.split_the_string(super_split[0],"£") #items in this list represent one item in this Layers() object
        for i in range(0,len(splitted_str)):
            item_str=MemoryHandler.split_the_string(splitted_str[i],"|")
            depth=int(item_str[0])
            name=item_str[2]
            scale_str=MemoryHandler.split_the_string(item_str[3],",")
            scale=[float(scale_str[0][1:]),float(scale_str[1][1:-1])]
            rotation=int(item_str[4])
            shift_x=int(item_str[5])
            shift_y=int(item_str[6])
            activity=item_str[7]
            shift_r=float(item_str[8])
            shift_g=float(item_str[9])
            shift_b=float(item_str[10])
            extra=item_str[11]
            drawing_instruction_part=super_split[1]
            false_start=drawing_instruction_part.find(name)
            drawing_instruction_add=drawing_instruction_part[false_start+1:].find("£")+1 # instruction_str starts with "pd()|" for example
            real_start=false_start+drawing_instruction_add
            end=drawing_instruction_part[real_start+1:].find("']")-1
            instruction_str=drawing_instruction_part[real_start:end]
            self.add_item(depth,"objects",name,scale,rotation,shift_x,shift_y,activity,shift_r,shift_g,shift_b,extra,instruction_str)
        

        
        


    #note that, we do not care special effects like rotations yet
    def drawItem(self,item_number:int,filetext:str,turtle:turtle):
        filetext=filetext.strip("£")#poistetaan alusta ja lopusta mahdolliset turhat symbolit, Added 6.8.
        array=MemoryHandler.split_the_string(filetext,"|")
        
        #following three orders sent the pen into opening position
        #idea is to prevent drawing a line from the origin to first goto-coordinate, when origin is shifted
        turtle.penup()
        turtle.goto(self.items[item_number][5],self.items[item_number][6])
        draw=False #this controls, whether to draw or leave invisible
        if self.items[item_number][7]=="visible" or self.items[item_number][7]=="active":
            draw=True

        if self.items[item_number][1]=="objects"and draw:
            for plop in array:
                self.draw_command(plop,self.items[item_number],turtle)
        
        if self.items[item_number][1]=="texts" and draw:
            for plop in array: #uusi kokeilu
                self.draw_command(plop,self.items[item_number],turtle)

        #for gifs
        if self.items[item_number][1]=="gifs" and draw:
            tur=turtle.Turtle()
            tur.penup()
            tur.goto(self.items[item_number][5],self.items[item_number][6]) #putting turtle to it shifted position
            filename=self.items[item_number][2]#gif tiedoston nimi ilman .gif päätettä
            global screen
            screen.addshape("gifs/"+filename+".gif")
            tur.shape("gifs/"+filename+".gif")
        
    
    #draws a single command, for example line
    def draw_command(self,plop:str,item,turtle:turtle):
        scale=item[3]
        scalex=float(item[3][0])
        scaley=float(item[3][1])
        rotation=int(item[4])
        shift_x=int(item[5])
        shift_y=int(item[6])
        if plop[0:4]=="goto": 
            x=Commands.nth_parameter(plop,0)
            y=Commands.nth_parameter(plop,1)
            [x,y]=self.coordinate_modifys(scale,rotation,shift_x,shift_y,x,y)
            turtle.goto(int(x),int(y))
        
        if plop[0:2]=="ps":
            pen=Commands.nth_parameter(plop,0)
            turtle.pensize(self.object_size_modify(scale,int(pen)))

        if plop=="pd()":
            turtle.pendown()

        if plop=="pu()":
            turtle.penup()

        if plop[0:2]=="co": 
            red=Commands.nth_parameter(plop,0)[1:]
            green=Commands.nth_parameter(plop,1)
            blue=Commands.nth_parameter(plop,2)[:-1]
            old_color=[float(red),float(green),float(blue)]
            shift_color=[item[8],item[9],item[10]]
            new_color=shifted_color(old_color,shift_color)
            if item[7]=="visible":
                bg_color=[screen.bgcolor()[0],screen.bgcolor()[1],screen.bgcolor()[2]]
                new_color=color_dimmening(new_color,bg_color)
            turtle.pencolor(new_color[0],new_color[1],new_color[2])

        if plop[0:2]=="fc":
            red=Commands.nth_parameter(plop,0)[1:]
            green=Commands.nth_parameter(plop,1)
            blue=Commands.nth_parameter(plop,2)[:-1]
            old_color=[float(red),float(green),float(blue)]
            shift_color=[item[8],item[9],item[10]]
            new_color=shifted_color(old_color,shift_color)
            if item[7]=="visible":
                bg_color=[screen.bgcolor()[0],screen.bgcolor()[1],screen.bgcolor()[2]]
                new_color=color_dimmening(new_color,bg_color)
            turtle.fillcolor(new_color[0],new_color[1],new_color[2])

        if plop=="bf()" or plop=="begin fill()":
            turtle.begin_fill()

        if plop=="ef()" or plop=="end fill()":
            turtle.end_fill()

        if plop=="circle":
            radius=Commands.nth_parameter(plop,0)
            turtle.circle(self.object_size_modify(scale,int(radius)))

        if plop[0:2]=="sh" or plop[0:7]=="heading":
            head=Commands.nth_parameter(plop,0)
            turtle.setheading(self.heading_rotation_modify(rotation,int(head)))

        if plop[0:2]=="wr": 
            style=Commands.nth_parameter(plop,0)#esim. "bold"
            fon=Commands.nth_parameter(plop,1)#esim. "Calibri"
            fontsize=Commands.nth_parameter(plop,2)#esim. "13
            text=plop[6:-1]
            text=text[text.find(",")+1:]
            text=text[text.find(",")+1:]
            text=text[text.find(",")+1:].strip("'")#oli ennnen [text.find(",")+1:-1]: en edes tiedä miten -1 vaikuttaa
            #trick here is to take the whole command and remove the "nontext"
            turtle.write(text,font=[fon, self.object_size_modify(scale,int(fontsize)),style])

    #returns a string that represents a drawing, which is similar to the item item_number, but with changes on the text
    def rewrite_copy(self,item_number:int,font:str,fontsize:int,style:str,text:str):
        textinfile= self.load_file_as_string(self.items[item_number][2],"drawings")
        array=MemoryHandler.split_the_string(textinfile,"|")
        new_array=[]
        for plop in array:
            if plop [0:2] !="wr":
                new_array.append(plop)
            if plop[0:2]=="wr":
                new_array.append("wr("+style+","+font+"," +str(fontsize) +","+ text+")")
        return MemoryHandler.glue_the_split(new_array,"|")+"|" #+"|"  added 18.11.
            
            


    
    def coordinate_modifys(self,scale:List[float],rotation:int,shift_x:int,shift_y:int,x,y):
        result=[x,y]
        result=self.coordinate_scale_modify(scale,x,y)
        result=self.coordinate_rotation_modify(rotation,result[0],result[1])
        result=self.coordinate_shift_modify(shift_x,shift_y,result[0],result[1])
        return [int(result[0]),int(result[1])]#we need int values, no floats

    #this is used for example to change goto(20,30) to goto(30,45) (when scale is 1.5)
    def coordinate_scale_modify(self,scale:List[float],x:int, y:int):
        return [int(int(x)*scale[0]),int(int(y)*scale[1])]
    
    #this is used to modify sizes of circles and pensize
    def object_size_modify(self,scale:List[float],size:int):
        return int(size*math.sqrt(abs(scale[0]*scale[1])))#takes geometrical average

    #this is used for example to rotate goto(x,y) to new point got(new_x,new_y)
    def coordinate_rotation_modify(self,rotation,x,y):
        rotation_complex=[math.cos((rotation*math.pi)/180),math.sin((rotation*math.pi)/180)]
        new_x=x*rotation_complex[0]-y*rotation_complex[1]
        new_y=x*rotation_complex[1]+y*rotation_complex[0]
        return [new_x,new_y]
    
    #this is used to rotate the heading of the turtle
    def heading_rotation_modify(self,rotation,heading):
        result=rotation+heading
        if result>360:
            result=result-360
        return result

    #this is used to move the origin of the object
    def coordinate_shift_modify(self,shift_x:int,shift_y:int,x:int,y:int):
        return [shift_x+x,shift_y+y]

    #loads a file, can be object, can be text, maybe also gif or extra? 
    def load_file_as_string(self,file_name:str,sub_directory:str):
        actual_name= sub_directory+"/"+file_name.strip("'")+".txt"#strip ' just in case
        if sub_directory=="":
            actual_name=file_name+".txt"
            # Open a file for reading
        with open(actual_name, "r") as file:
            # Read the contents of the file into memory
            instructions=file.read()
        return instructions

    #tallentaa ihan kaiken, ts. itemit, jonka perusteella kuva tuotetaan
    def save_layers(self,filename):
        global mode
        if mode=="drawing_mode":
            rsave_drawing() #with this we can save also the possibly unfinished layer
        file_text=""
        for item in self.items:
            file_text += str(item)+"|"
        file_text += "@"
        for instruction in self.drawing_instructions:
            file_text += str(instruction)+"|"
        with open(filename, "w") as file:
        # Write the string to the file
            file.write(file_text)

     


    #lataa layers-tiedoston: huom layers on muutettu files
    def load_layers(self):
        filename=filedialog.askopenfilename(initialdir="files/")
        filename= filename_without_subdir(filename,"files")# oli filename_end(filename), korvattiin 20.7. 11:55
        file_text=self.load_file_as_string(filename,"files")[:-1]
        self.items=[]#removes all the items
        parts=MemoryHandler.split_the_string(file_text,"@") # list with two things [0] for items and [1] for instructions
        array=MemoryHandler.split_the_string(parts[0].strip("|"),"|") #putting new items from filetext starts
        for term in array:
            par=MemoryHandler.split_the_string(term,",")
            for i in range(0,len(par)):
                par[i]=par[i].strip(" ").strip("[")
                par[i]=par[i].strip("]").strip("'")
            false_start=parts[1].find("'"+par[2]+"'")
            instruction_real_start=false_start+parts[1][false_start:].find("£")
            instruction=parts[1][instruction_real_start:parts[1].find("|'",instruction_real_start)]+"|"#"|"was added 25.8.
            self.add_item(int(par[0]),par[1],par[2],[float(par[3]),float(par[4])],int(par[5]),int(par[6]),int(par[7]),par[8],float(par[9]),float(par[10]),float(par[11]),par[12],instruction)
        self.redraw(t)
        return filename #this is used so that when saving file after loading it, its name is possible to "capture"from this return value



    #this makes a string of object modified due to layer orders, this helps to save the object or
    #merge one or more objects
    #NOTE unfortunately, lot of here is kind of repeat of draw_command, so if you change one of them
    #you probably need to change the other as well NOTE this gets files only from drawings, it cannot merge gifs
    def modified_object_to_string(self,item:List[str],start_index,end_index): #only commands in the interval [start_index:end_index] are returned
        scale=[float(item[3][0]),float(item[3][1])]
        rotation=int(item[4])
        shift_x=int(item[5])
        shift_y=int(item[6])
        shift_r=float(item[8])
        shift_g=float(item[9])
        shift_b=float(item[10])
        filetext=self.load_file_as_string(item[2],"drawings")
        filetext=filetext.strip("£")#poistetaan alusta ja lopusta mahdolliset turhat symbolit
        filetext=filetext.strip("|")#this is lost only temporarily, leaving "|" would make an empty "plop".
        array=MemoryHandler.split_the_string(filetext,"|")
        result="£" #+ "penup()|goto("+str(shift_x)+","+str(shift_y)+")"+"|pendown()|"#initializing the position, lets see if penup()...is unnecessary
        if start_index<0:
            start_index=0
        if end_index>len(array):
            end_index=len(array)
        for plop in array[start_index:end_index]: #tässä oli end_index -1 miksi -1!!!?
            if plop[0:4]=="goto":
                x=Commands.nth_parameter(plop,0)
                y=Commands.nth_parameter(plop,1)
                [x,y]=self.coordinate_modifys(scale,rotation,shift_x,shift_y,x,y)
                result=result+"goto("+str(x)+","+str(y)+")"
        
            if plop[0:2]=="ps":
                pen=Commands.nth_parameter(plop,0)
                result=result+"ps("+str(self.object_size_modify(scale,int(pen))) +")"

            if plop=="pd()":
                result=result+"pd()"

            if plop=="pu()":
                result=result+"pu()"

            if plop[0:2]=="co":
                red=Commands.nth_parameter(plop,0)[1:]
                green=Commands.nth_parameter(plop,1)
                blue=Commands.nth_parameter(plop,2)[:-1]
                old_color=[float(red),float(green),float(blue)]
                shift_color=[shift_r,shift_g,shift_b]
                new_color=shifted_color(old_color,shift_color)
                result=result+"co(["+str(new_color[0])+","+str(new_color[1])+","+str(new_color[2])+"])"

            if plop[0:2]=="fc":
                red=Commands.nth_parameter(plop,0)[1:]
                green=Commands.nth_parameter(plop,1)
                blue=Commands.nth_parameter(plop,2)[:-1]
                old_color=[float(red),float(green),float(blue)]
                shift_color=[shift_r,shift_g,shift_b]
                new_color=shifted_color(old_color,shift_color)
                result=result+"fc(["+str(new_color[0])+","+str(new_color[1])+","+str(new_color[2])+"])"

            if plop=="begin fill()" or plop=="bf()":
                result=result+"bf()"

            if plop=="end fill()"or plop=="ef()":
                result=result+"ef()"

            if plop[0:6]=="circle":
                radius=Commands.nth_parameter(plop,0)
                result=result+"circle("+str(self.object_size_modify(scale,int(radius)))+")"

            if plop[0:7]=="heading" or plop[0:2]=="sh":
                head=Commands.nth_parameter(plop,0)
                result=result+"sh("+str(self.heading_rotation_modify(rotation,int(head)))+")"

            if plop[0:2]=="wr":
                style=Commands.nth_parameter(plop,0)
                font=Commands.nth_parameter(plop,1)
                fontsize=Commands.nth_parameter(plop,2)
                text=plop[6:-1]
                text=text[text.find(",")+1:]
                text=text[text.find(",")+1:]
                text=text[text.find(",")+1:].strip("'")#trick here is to take the whole command and remove the "nontext"
                result=result+"wr("+style+","+font+"," +str(self.object_size_modify(scale,int(fontsize))) +","+ text+")"
                #it is not possible to rotate writing, 
                #and shifting parameters are already in another commands
            result=result+"|" #it is important that this is after all commands, so if you add new command type, but it before this

        result=result #tässä oli alunperin [:-1] mutta sitä ei tarvinne

        return result
    
    #layer item number 'item_number' is splitted into two parts. These create new items. The splitted item is also leaved.
    #names for the new items are name1 and name2
    def split_item_from_index(self,item_number:int,cut_index:int,name1:str,name2:str):
        str1=self.modified_object_to_string(self.items[item_number],0,cut_index)#+"|" tämä poistettiin modif... muutoksen takia
        str2=self.modified_object_to_string(self.items[item_number],cut_index,100000)
        save_string_to_file(str1,name1,"drawings") #tkirjoitetaan ekstitiedostot puolikkaista

        self.add_item(0,"objects",name1,[1,1],0,0,0,"visible",0,0,0,"",str1) #lisätään ne Layer():iin
        where_to_go=current_location(str1) #location in the split point
        where_to_head=current_heading(str1) #heading in the split point
        pensize_in_split=current_pensize(str1) #pensize in the split point
        color_in_split=current_pencolor(str1) #pencolor...
        fillcolor_in_split=current_fillcolor(str1)#fillcolor
        up_or_down=current_up_or_down(str1) #is the pen up or down in the split point
        bstr2 = "£co("+color_in_split+")|" #this bstr2 means a string added before str2
        bstr2 += "fc("+fillcolor_in_split+")|"
        bstr2 += "pu()|"
        bstr2 += "goto("+str(where_to_go[0])+","+str(where_to_go[1])+")|"
        bstr2 += "sh("+str(where_to_head)+")|"
        bstr2 += "ps("+str(pensize_in_split)+")|" #these where necessary to copy the state of the (potential) turtle
        if up_or_down=="down":
            bstr2 += "pd()|"
        save_string_to_file(bstr2+str2[1:],name2,"drawings")#here [1:] takes the £ out of str2
        self.add_item(0,"objects",name2,[1,1],0,0,0,"visible",0,0,0,"",str2)

    #splittaa kaikki aktiiviset layerit tästä indeksistä
    def split_active(self,cut_index:int,name1:str,name2:str):
        array=self.items
        for i in range(0,len(array)):
            if array[i][7]=="active":
                self.split_item_from_index(i,cut_index,name1,name2)


    #this gives a color code, which tells label background color depending on activity level
    def color_code(self,item_number:int):
        activity=self.items[item_number][7]
        if activity=="active":
            return "lightgreen"
        if activity=="visible":
            return "lightblue"
        if activity=="invisible":
            return "white"
        if activity=="dim":
            return "orange"
        if activity=="drawing":
            return "wheat1"
        return "gray"
        

    #draws origos of every layer
    def draw_origos(self):
        layer_data_turtle.clear()
        for i in range(len(self.items)):
            layer_data_turtle.penup()
            layer_data_turtle.goto(self.items[i][5],self.items[i][6])#goes to origo (I guess)
            layer_data_turtle.pendown()
            if self.items[i][7]=="active":
                layer_data_turtle.color("red")
            if self.items[i][7] in ["visible","invisible"]:
                layer_data_turtle.color("blue")
            layer_data_turtle.dot(15)


    #draws the Layers-object after change, turtle is actually pseudo parameter, t draws all
    def redraw(self,turtle:turtle):
        screen.tracer(0)#välitön piirtäminen
        global t
        t.clear()
        t.hideturtle()
        size=len(layer_items.items)
        depths=[]
        for i in range(0,size):
            depths.append(float(layer_items.items[i][0]))
        
        # Using sort + key
        depths.sort(key = float)

        order=[]#tähän listataan indeksit järjestykseen, niin, että ensiksi tulee sen indeksin arvo,
        #jonka depth on pienin
        for i in range(0,size):
            for j in range(0,size):
                if depths[i]==layer_items.items[j][0] and j not in order:
                    order.append(j)
        filetext=""#uusi alkaa tästä
        for i in range(0,len(order)):
            if self.items[order[i]][1]=="objects": #this is modifies so that only objects are drawn from txt.files
                filetext=self.get_drawing_instruction_str(self.items[order[i]][2])
                filetext=filetext.strip("£")#poistetaan alusta ja lopusta mahdolliset turhat symbolit
                layer_items.drawItem(order[i],filetext,turtle)
        global origomode
        layer_data_turtle.clear()
        if origomode=="show":
            self.draw_origos()
        screen.tracer(1)#piirretään joka viiva postettiin testinä 20.7. klo 7.35


    #draws the Layers-object, but slowly
    def slowdraw(self,turtle:turtle):
        global t
        screen.tracer(1)
        t.clear()
        t.color("white")
        t.pensize(20)
        t.penup()
        t.goto(0,0)
        t.dot(2000)
        t.hideturtle()
        screen.tracer(0)
        draw_temporary_file()
        size=len(layer_items.items)
        depths=[]
        for i in range(0,size):
            depths.append(float(layer_items.items[i][0]))
        
        # Using sort + key
        depths.sort(key = float)

        order=[]#tähän listataan indeksit järjestykseen, niin, että ensiksi tulee sen indeksin arvo,
        #jonka depth on pienin
        for i in range(0,size):
            for j in range(0,size):
                if depths[i]==layer_items.items[j][0] and j not in order:
                    order.append(j)

        filetext=""#uusi alkaa tästä
        for i in range(0,len(order)):
            if self.items[order[i]][1]=="objects": #this is modifies so that only objects are drawn from txt.files
                filetext=self.get_drawing_instruction_str(self.items[order[i]][2])
                filetext=filetext.strip("£")#poistetaan alusta ja lopusta mahdolliset turhat symbolit
                layer_items.drawItem(order[i],filetext,turtle)
        t.hideturtle()



    #changes the status of layer item item_number to new status
    def change_status(self,item_number,new_status):
        self.items[item_number][7]=new_status
        self.redraw(t)

    def change_status_without_redraw(self,item_number,new_status):
        self.items[item_number][7]=new_status

    #scales the item, for example if scale-parameter is 2.0 and scale_factor is 1.5,
    #then new scale-parameter is.Here it is ok that there is no separate scale parameters for x and y
    def scale(self,item_number,scale_factor):
        self.items[item_number][3]=[scale_factor*self.items[item_number][3][0],scale_factor*self.items[item_number][3][1]]
        #self.redraw(t) tätä metodia ei käytetä pelkällään, joten siirretään activeen    

    #scales all active items
    def scale_active(self,scale_factor):
        for i in range (0,len(self.items)):
            if self.items[i][7]=="active":
                self.scale(i,scale_factor)
        self.redraw(t)

    #rotates the item, for example if rotation-parameter is 200 and rotation is 15,
    #then new rotation-parameter is 215
    def rotate(self,item_number,rotation):
        self.items[item_number][4]=self.items[item_number][4]+rotation
        if self.items[item_number][4]>360:
            self.items[item_number][4]=self.items[item_number][4]-360
        #self.redraw(t) tätä metodia ei käytetä pelkällään, joten siirretään activeen   

    #rotates all active items
    def rotate_active(self,rotation):
        for i in range (0,len(self.items)):
            if self.items[i][7]=="active":
                self.rotate(i,rotation)
        self.redraw(t)

    #shifts the item, for example if rotation-parameter is 200 and rotation is 15,
    #then new rotation-parameter is 215
    def shift(self,item_number,shift_x,shift_y):
        if item_number>=0 and item_number<len(self.items):
            self.items[item_number][5]=self.items[item_number][5]+shift_x
            self.items[item_number][6]=self.items[item_number][6]+shift_y
        #self.redraw(t) #tätä metodia ei käytetty aiemmin pelkällään, joten se oli aiemmin poistettu, muutos 30.11. 


    #adds a copy of item item_number
    def copy(self,item_number):
        new_item=[]
        itn=item_number
        for i in range(0,3):#12:48, 28.6.
            new_item.append(self.items[itn][i])
        scale_thing=[self.items[itn][3][0],self.items[itn][3][1]] #this is needed otherwise just copying self.items[3] makes copies
        #scale factors change simultaniously
        new_item.append(scale_thing)
        for i in range(4,len(self.items[itn])):#12:48, 28.6.
            new_item.append(self.items[itn][i])
        self.items.append(new_item)
        #self.redraw(t) tätä metodia ei käytetä pelkällään, joten siirretään activeen  

    #copys all active items
    def copy_active(self):
        size=len(self.items)
        for i in range (0,size):
            if self.items[i][7]=="active":
                self.copy(i)
        self.redraw(t)  

    #changes a depth of item item_number
    def depth(self,item_number,new_depth):
        if item_number >= 0 and item_number<len(self.items) and is_number(new_depth):#is_number() is new test 30.11 whichcould be used elsewhere 
            self.items[item_number][0]=new_depth
        #self.redraw(t) tätä ei käytetä pelkällään joten siirretään activeen, niin piirtokerrat vähenevät  

    #changes a depth of all active items
    def depth_active(self,new_depth):
        size=len(self.items)
        for i in range (0,size):
            if self.items[i][7]=="active":
                self.depth(i,new_depth)
        self.redraw(t)

    #this thinks that items are drawn in the same objective size. And if they are further away, they look smaller.
    #distance is positive number where we are looking at the picture. Everything that has greater depth is not seen.
    #the closer the depth is to distance, the larger it looks
    def depth_to_scale(self,distance:int):
        for i in range (0,len(self.items)):
            if self.items[i][7]=="active":
                if self.items[i][0]<distance:
                    self.items[i][3]= [distance/(distance-self.items[i][0]),distance/(distance-self.items[i][0])]
                if self.items[i][0]>distance:
                    self.items[i][3]=[0,0]
        self.redraw(t)

   #this is similar to depth_to_scale but now, depth1 tells where we look and depth2 tells, which depth looks like normal size  
    def moving_depth_to_scale(self,depth1,depth2):
        for i in range (0,len(self.items)):
            if self.items[i][7]=="active":
                if self.items[i][0]<depth1:
                    self.items[i][3]= [(depth1-depth2)/(depth1-self.items[i][0]),(depth1-depth2)/(depth1-self.items[i][0])]
                if self.items[i][0]>depth1:
                    self.items[i][3]=[0,0]
        self.redraw(t)


    def scale_to_depth(self,distance:int):
        for i in range (0,len(self.items)):
            if self.items[i][7]=="active":
                sscale=math.sqrt(self.items[i][3][0]*self.items[i][3][1]) #overall scale is got geometrically
                self.items[i][0]=int(distance-(100/sscale))
        self.redraw(t)


    #makes layers look like they were looked at depth of layer distance
    def horizon(self,distance:int,horizon:List[int]):
        self.depth_to_scale(distance)
        for i in range (0,len(self.items)):
            if self.items[i][7]=="active":#seuraavassa säädetään shiftauksen määrää kohti horisonttipistettä, jos depth<0 ja kauemmas, kun depth>0
                if self.items[i][0]<distance:
                    self.items[i][5]=self.items[i][5]+ int((horizon[0]-self.items[i][5])*self.items[i][0]/(-distance+self.items[i][0]))
                    self.items[i][6]=self.items[i][6]+ int((horizon[1]-self.items[i][6])*self.items[i][0]/(-distance+self.items[i][0]))



    #shifts all active items
    def shift_active(self,shift_x,shift_y):
        for i in range (0,len(self.items)):
            if self.items[i][7]=="active":
                self.shift(i,shift_x,shift_y)
        self.redraw(t)


    #shifts all active colors in edit mode, colors stay between -1 and 1
    def shift_active_colors(self,shift_r:float,shift_g:float,shift_b:float):
        for i in range (0,len(self.items)):
            if self.items[i][7]=="active":
                new_color=[self.items[i][8]+shift_r,self.items[i][9]+shift_g,self.items[i][10]+shift_b]
                for j in range(0,3):
                    if new_color[j]<-1:
                        new_color[j]=-1
                    if new_color[j]>1:
                        new_color[j]=1
                self.items[i][8]=new_color[0]
                self.items[i][9]=new_color[1]
                self.items[i][10]=new_color[2]
        self.redraw(t)

    #shifts volor of one layer colors in edit mode, colors stay between -1 and 1
    def shift_one_color(self,layer_nro:int,shift_r:float,shift_g:float,shift_b:float):
        new_color=[self.items[layer_nro][8]+shift_r,self.items[layer_nro][9]+shift_g,self.items[layer_nro][10]+shift_b]
        for j in range(0,3):
            if new_color[j]<-1:
                new_color[j]=-1
            if new_color[j]>1:
                new_color[j]=1
        self.items[layer_nro][8]=new_color[0]
        self.items[layer_nro][9]=new_color[1]
        self.items[layer_nro][10]=new_color[2]



    #point x1,y1 stays still and x2,y2 moves to x3,y3. This is done for all active layers
    def spin_active(self,x1:int,y1:int,x2:int,y2:int,x3:int,y3:int):
        for i in range (0,len(self.items)):
            if self.items[i][7]=="active": 
                self.spin_one(i,x1,y1,x2,y2,x3,y3)


    #spins just one layer, the 'layer_nro'st layer
    def spin_one(self,layer_nro:int,x1:int,y1:int,x2:int,y2:int,x3:int,y3:int):
        if x1==x2 and y1==y2:
            return # this would make scale factor infinite if continued
        if len(self.items)<=layer_nro or 0>layer_nro:
            return # layer_nro was too large
        spinz1=Geometry.Complex(x1,y1)
        spinz2=Geometry.Complex(x2,y2)
        spinz3=Geometry.Complex(x3,y3)
        complex_shift=Geometry.Complex(self.items[layer_nro][5],self.items[layer_nro][6])
        new_parameters=Geometry.layer_parameters_after_spin(self.items[layer_nro][3],self.items[layer_nro][4],complex_shift,spinz1,spinz2,spinz3)
        self.items[layer_nro][3]=new_parameters[0]
        self.items[layer_nro][4]=new_parameters[1]
        self.items[layer_nro][5]=new_parameters[2]
        self.items[layer_nro][6]=new_parameters[3]

    #destroys item item_number from Layers-object
    def destroy(self,item_number):
        self.items.pop(item_number)

    #destroys all active items item_number from Layers-object
    def destroy_active(self):
        destroy_list=[]
        for i in range(0,len(self.items)):
            if self.items[i][7]=="active":
                destroy_list.append(i)

        size=len(destroy_list)
        for i in range(0,size):
            self.items.pop(destroy_list[size-i-1])#items are removed in descending order to not affect the indexes

    #this tells the countours of a drawing before shifting, scaling and rotation
    def untwisted_item_contours(self,item_number):
        filetext=self.load_file_as_string(self.items[item_number][2],"drawings")
        maxy=-100000000
        miny=100000000
        maxx=-100000000
        minx=100000000
        array=MemoryHandler.split_the_string(filetext,"|")
        size=len(array)
        for i in range(0,size):
            if array[i][0:4]=="goto":
                x=int(Commands.nth_parameter(array[i],0))
                y=int(Commands.nth_parameter(array[i],1))
                if x<minx:
                    minx=x
                if x>maxx:
                    maxx=x
                if y<miny:
                    miny=y
                if y>maxy:
                    maxy=y
        return [minx,miny,maxx,maxy]
    
    def real_contours(self,item_number):
        untwisted_parameters=self.untwisted_item_contours(item_number)
        lower_left=[untwisted_parameters[0],untwisted_parameters[1]]
        lower_right=[untwisted_parameters[2],untwisted_parameters[1]]
        upper_left=[untwisted_parameters[0],untwisted_parameters[3]]
        upper_right=[untwisted_parameters[2],untwisted_parameters[3]]
        item=self.items[item_number]
        scale=[float(item[3][0]),float(item[3][1])]
        rotation=int(item[4])
        shift_x=int(item[5])
        shift_y=int(item[6])
        realll= self.coordinate_modifys(scale,rotation,shift_x,shift_y,lower_left[0],lower_left[1])
        reallr= self.coordinate_modifys(scale,rotation,shift_x,shift_y,lower_right[0],lower_right[1])
        realul= self.coordinate_modifys(scale,rotation,shift_x,shift_y,upper_left[0],upper_left[1])
        realur= self.coordinate_modifys(scale,rotation,shift_x,shift_y,upper_right[0],upper_right[1])
        return [realll,reallr,realur,realul]#these are returned in counterclockwise directions
    
    #adds a new drawing, consisting of writing
    def add_text_layer(self,xpos:int,ypos:int,color:str,fillcolor:str,font:str,fontsize:int,fontstyle:str,text:str,drawingname:str):
        layer_str="" #this will be the str code for layer to be added
        layer_str += "£co("+ color+")|fc("+ fillcolor+")|sh(0)|ps("+str(fontsize)+")|pu()|goto("+str(0)+","+str(0)+")|"
        layer_str += "pd()|wr("+fontstyle+","+font+","+str(fontsize)+","+text+")|ef()|" # the last ef()| was added 24.8. to solve a bug
        temp_turtle.penup()
        #save_string_to_file(layer_str,drawingname,"drawings")
        self.add_item(0,"objects",drawingname,[1,1],0,xpos,ypos,"active",0,0,0,"",layer_str)
    
    #returns the number of the item, which origo (shift) is closest to (xpos,ypos)
    def closest_layer(self,xpos:int,ypos:int,distance_maximum=150):
        if len(self.items)==0:#an "error"
            return -1
        maxdis=10000000
        result=0
        for i in range(0,len(self.items)):
            comparing=Geometry.distance(xpos,ypos,self.items[i][5],self.items[i][6])
            if comparing<maxdis:
                result=i
                maxdis=comparing
        if maxdis>distance_maximum:#if there is no layers nearby
            result=-1
        return result
    
        #changes the activation of the closest layer
    def closest_layer_activation(self,xpos:int,ypos:int):
        closest=self.closest_layer(xpos,ypos)
        if self.items[closest][7]=="active":
            self.items[closest][7]="visible"
        elif self.items[closest][7]=="visible":
            self.items[closest][7]="invisible"
        elif self.items[closest][7]=="invisible":
            self.items[closest][7]="active"


#if function_database information containing txt-file doesn't yet exist, this creates it 
def initialize_function_database():
    if path.exists("machinery/function_database.txt")==False: #this is for the new user starting to use the program
        basic_function_key=["forward(x)","turn(x)","pircle(x)","spin(x1,y1,x2,y2,x3,y2)","line(x1,y1,x2,y2)"]
        basic_function_key += ["pircle(r)","rect(x,y)" ,"forward(x)", "jump(x)","goto(x,y)"]
        basic_function_key +=["setheading(a)", "turn(a)", "pensize(r)","color(c)","fillcolor(c)"]
        basic_function_key +=["rectangle(x1,y1,x2,y2)", "circle(x1,y1,x2,y2)", "oval(x1,y1,x2,y2)","arc(x1,y1,x2,y2,x3,y3)"]
        basic_function_key +=["line(x1,y1,x2,y2)"]
        basic_function_key +=["put(l)","save(l)","deletefunction(t)","spin(x1,y1,x2,y2,x3,y3,vect)"]
        basic_function_key +=["put(file)","depth(x)","depth(x,vect)","rotate(x)","rotate(x,vect)","scale(x,y)","scale(x,y,vect)"]
        basic_function_key +=["shift(x,y)","shift(x,y,vect)","x shift(x,y)","x shift(x,y,vect)","y shift(x,y)","y shift(x,y,vect)"]
        basic_function_key +=["abs stretch(x,y)","abs stretch(x,y,vect)","rel stretch(x,y)","rel stretch(x,y,vect)"]
        basic_function_key +=["abs pos(x,y)","abs pos(x,y,vect)","abs color(r,g,b)","abs color(r,g,b,vect)","abs angle(x)","abs angle(x,vect)"]
        basic_function_key +=[ "shift red(c)","shift red(x,vect)", "shift green(x)","shift green(x,vect)","shift blue(x)","shift blue(x,vect)"]
        #"more function must be added later"      


        function_output_model_list=[]
        for key in basic_function_key:
            function_output_model_list.append(key+"=="+key+"=="+key)
        filetext=""
        for strin in function_output_model_list:
            filetext += strin+"\n"
        with open("machinery/function_database.txt", "w") as file: #it saves a database of saved functions like neliö(x)=rect(x,x)
            # Write the string to the file
            file.write(filetext)

class Popularity: #for handling which are the most popular drawings to be added

    popularity_dict={} #dictionary of popularity (not ordered), {imagename:popularity}
    popularity_list=[] #imagenames with most popular iomage first
    popularity_file="machinery/mini.txt" #here we write the data bout the popularity
    image_directory="drawings" #this is the place where we will search the mini png.files
    def __init__(self,popularity_file="machinery/mini.txt",image_directory="drawings"):
        self.image_directory=image_directory 
        text=""
        if path.exists(popularity_file):
            # Open a file for reading
            with open(popularity_file, "r") as file:
            # Read the contents of the file into memory
                text=file.read()
        help_list=MemoryHandler.split_the_string(text,"|")


        for item in help_list:
            file_and_popularity=MemoryHandler.split_the_string(item,":")
            try:
                file_and_popularity[1]=float(file_and_popularity[1])
            except ValueError:
                file_and_popularity[1]=0.001
            self.popularity_dict[file_and_popularity[0]]=float(file_and_popularity[1]) #each filename is assigned to its popularity value 
        self.popularity_list=self.sorted_list_from_dictionary(self.popularity_dict)
        self.popularity_dict_to_txt(popularity_file) #thins should take care of deleting keys of missing files


    def init_mini_file(self,popularity_file="machinery/mini.txt"):
        self.popularity_file=popularity_file
        if path.exists(self.popularity_file)==False: #if this is somehow removed during operating let just introduce it back
            images_directory = self.image_directory
            image_files = [f for f in list_files(images_directory) if f.endswith(".png")] #used to be [f for f in os.listdir(images_directory) if f.endswith(".png")]
            minitext="" #text to be added in the txt. file
            index=0 #point of this is to make some initial difference to different pngs.
            for f in image_files:
                index+=1
                f_without_type=f[:-4]
                f_text=f_without_type+".txt"
                if f_text in list_files(images_directory):
                    minitext += f_text+":"+str(0.01*index)+"|"  

            with open(self.popularity_file, "w") as file:
        # Write the string to the file
                 file.write(minitext)

    #here we turn Popularity-object into txt-file, we also check here that it doesn't contain info about removed files
    #or miss info about existing files
    #NOTE this was fixed 20.1 due to slowing down program, NOTE 2 somewhat confusingly there are 
    #both self.image_directory and images_directory, they are a different thing, I guess
    def popularity_dict_to_txt(self,popularity_file="machinery/mini.txt"):
        self.init_mini_file(popularity_file) #in the case there was no txt-file it is created here
        images_directory = self.image_directory
        image_files = [f for f in list_files(images_directory) if f.endswith(".png")]
        #first we remove extra info about files not existing:
        list_of_removable_keys=[]
        filenames_in_images_directory=list_files(images_directory)
        for key in self.popularity_dict.keys():
            key_without_type=key[:-4]
            key_text=key_without_type+".txt"
            if (key[:-4]+".png" not in image_files) or (key not in filenames_in_images_directory): #we both must have drawings-txtfile and mini-image
                list_of_removable_keys.append(key)
        for rk in list_of_removable_keys:       
            self.popularity_dict.pop(rk,None) 
        #then we add what was missing
        fnames_in_image_directory=list_files(self.image_directory)
        fnames_in_popularity_dict=self.popularity_dict.keys()
        for f in image_files:
            f_without_type=f[:-4]
            f_text=f_without_type+".txt"
            if (f_text in fnames_in_image_directory) and (f_text not in fnames_in_popularity_dict):
                self.popularity_dict[f_text]=0.01 #some quite random starting value for popularity
        #then we produce the text
        minitext=""
        for key in self.popularity_dict.keys():
            minitext += key+":"+str(self.popularity_dict[key])[0:6]+"|" 
        with open(self.popularity_file, "w") as file:
        # Write the string to the file
            file.write(minitext)

    #takes a dictionary and sorts it by its values to new dict so that items are listed in the descending order according to their keys
    def sorted_dict_from_dictionary(self,dict):
        sorted_dict = sorted(dict.items(), key=lambda x: x[1],reverse=True)
        return sorted_dict

    #takes a dictionary and sorts it by its values to a list so that items are listed in the descending order according to their keys
    def sorted_list_from_dictionary(self,dict):
        sorted_dict = self.sorted_dict_from_dictionary(dict)
        sorted_list=[]
        for i in range(len(sorted_dict)):
            sorted_list.append(sorted_dict[i][0])
        return sorted_list

    #when new file is added to popularity_
    def new_file_added(self,filename):
        self.popularity_dict[filename] = 1
        self.popularity_list=self.sorted_list_from_dictionary(self.popularity_dict)
        self.popularity_dict_to_txt(self.popularity_file)

    #when drawing is used it (or its name) should get bonus for popularity, raising its ranking
    def popularity_bonus(self,filename):
        for key in self.popularity_dict:
            if self.popularity_dict[key]>0.0011: #there might be a bug, when value goes to small, related to 0.00001 for example
                #being turned into 0.1 e-5 type of expression this prevents that
                self.popularity_dict[key]=self.popularity_dict[key]*0.99 #slowly popularity vanishes without usage
        if filename in self.popularity_dict.keys():
            self.popularity_dict[filename] += 1
        else: 
            self.popularity_dict[filename] = 1
        self.popularity_list=self.sorted_list_from_dictionary(self.popularity_dict)
        self.popularity_dict_to_txt(self.popularity_file)




def test(event=None):
    global temporary_file_string
    global db
    global command_line_entry
    global SCALEX,SCALEY,QUICK_WIDTH,QUICK_HEIGHT,ORIGOX,ORIGOY
    change_layer_variable_parameter(layer_items,variable_name="ldepth",layer_nro=1,new_value=13)
    expression=command_line_entry.get("1.0", "end-1c")
    drawi=Geometry.Drawing(temporary_file_string)
    drawi.random_drawing()
    temporary_file_string=drawi.from_Drawing_to_temp_string()
    draw_temporary_file()

#produces a list of filenames in directory and its subdirectories
def list_files(directory):
    file_list=[]
    for root, _, files in os.walk(directory):
        for file in files:
            name_including_directory=os.path.join(root, file) #this name might looklike drawings\\kuva.png foo example
            file_list.append(name_including_directory[name_including_directory.find("\\")+1:]) #takes the directory out of name
    return file_list




#for rxample if you want function with name ymp, parameters c1,r1, with code #color(c1)|#circ(r1)|#line(30)|#jump(*x). Then this returns
# $ymp(*c,*r)=#color(c1)|#circ(r1)|#line(30)|#jump(*x), 
#huom, code stringissä pitäisi olla nimetty parametrit c1,c2,...,x1,x2,...,r1,r,2... Lisäksi niiden pitää esiintyä tässä järjestyksessä
#idea, create function kysyy yksi kerrallaan haluatko muuttaa koodissa esiintyvän *r:n *p:n jne. muotoon r_n, p_n tms. missä n on 
#järjestysnumero, kun funktio koodia sitten kysytään *c, *x valitataan toteuttaessa ja x_1, c_1 jne määräytyvät funktion koodista
def function_string(function_name:str,parameters:str,code_string:str):
    if len(parameters)==0:
        return "$"+function_name+"="+code_string
    
    result="$"+function_name+"("
    for i in range(0,len(parameters)):
        result="*"+parameters[i][0]+"," #we take first symbol of parameter, for example parameter x14 turns into *x
    result=result[:-1]+")"+"="+code_string
    return result

#HUOM, ONKOHAN POINTTIA JÄTTÄÄ MINKÄÄN MUUTTUJAN VALIKOINTIA MYÖHEMMÄKSI, TS OVATKO *x TYYPPISET MUUTTUJAT TURHIA code_strinissä?
#syöte muotoa function_str: $func(*r,*s,*c,*r)=#scale(s1)|#rotate(r_1)|#line(40)|#color(c_1)|#pensize(r_2)|#scale(*s). Tämä löytyy usershortcuts.txt:stä
# ja commandline_str: $func(12,0.4,[0.7,0.89,0.2],14)|:tämä löytyy komentolinjalta
# pelkkä function_str ei siis riitä kertomaan miten päin arvot sijoitetaan 
def function_values_to_commandline(function_str:str,command_line_str):
    function=MemoryHandler.split_the_string(function_str,"=")[0] #for example $func(*r,*s,*c,*r)
    number_of_parameters=function.count(",")+1
    expected_colons_in_com=number_of_parameters-1+2*function.count("*c") #color variables bring two extra ,
    if expected_colons_in_com != command_line_str.count(","):
        raise ValueError("unexpected number of variables")
    array=[]
    for i in range(0,number_of_parameters): 
        array[i]=Commands.nth_parameter(function,i) #array will be for example [*r,*s,*c,*r]
    replacer=[]
    new_function=MemoryHandler.split_the_string(function,"(")[0] # in this example $func( or just $func, when there is zero variables
    for j in range(0,number_of_parameters):
        replacer[j]=array[j][1]+array[0:j].count("*"+array[j][1])+1 #replacer will be in previous example [r1,s1,c1,r2]
        new_function+=replacer[j]+","
    new_function=new_function[:-1]
    if len(replacer)==0:
        new_function=new_function[:-1] #now function should be $func(r1,s1,c1,r2) for example, or just $func, if no parameters 
    #KESKEN, NEW FUNCRIONIN AVULLA PITÄÄ KORVATA ALKUPERÄISELTÄ COMMANDLINELTÄ MUUTTUJAT, VÄRIN KÄSITTELY PITÄÄ VIELÄ SETVIÄ
    function_description=MemoryHandler.split_the_string(function_str,"=")[1]    
    #in the example this is #scale(s1)|#rotate(r_1)|#line(40)|#color(c_1)|#pensize(r_2)|#scale(*s)

#taking a drawing file in drawings directory and creating a png-from it    
def create_mini_image(loadname,savename):
    file_str= layer_items.load_file_as_string(loadname,"drawings") # used to  be just load_file_as_string(save_name,"drawings")
    drawi=Geometry.Drawing(file_str)
    [point1,point2]=drawi.placement()
    size=max(abs(point1[0]-point2[0]),abs(point1[1]-point2[1]))
    if size<=0:
        size=1
    drawi.enlarge(80/size)#this leaves size of mini image to 80 pixels in the larger direction
    [point1,point2]=drawi.placement() #after enlarging of shrinking image, its placement must be calculated again
    top_left=(point1[0],point2[1]) #these point needs to be chosen stupidy, i.e. this kind of top_right corner actually
    bottom_right=(point2[0],point1[1]) #and this is bottom_left, this is due to y-coordinate direction differences in png and turtle
    width=bottom_right[0]-top_left[0]
    height=-bottom_right[1]+top_left[1]
    file_str=drawi.from_Drawing_to_temp_string()
    PngMaker.draw_drawing(file_str,width,height,top_left,bg_color=(1,1,1),save_name=savename,style="basic")
    popular_drawings.new_file_added(loadname+".txt") #now info about new file reaches also txt-file keeping track of most popular drawings

#returns number of files in directory
def nro_of_files_in_directory(directory_name:str):
    count=0
    for path in os.listdir(directory_name):
        if os.path.isfile(os.path.join(directory_name, path)):
            count += 1
    return count


#given a file string representing a drawing, return a string representing the same drawing, but resized to size end_width*end_height
def resize_drawing_str(file_str,end_width=None,end_height=None):
    drawi=Geometry.Drawing(file_str)
    drawi.resize(end_width,end_height)
    return drawi.from_Drawing_to_temp_string()


#forms a png from current turtle_drawings, saves it at animations/current_file_name/filenro.png
#top_left and bottom_right are coordinates which limit the area for pngs created for animation
def quick_png(top_left,bottom_right):
    global current_file_name,temporary_file_string
    file_str=merged_layer_as_string()
    if mode=="drawing_mode":
        file_str+=temporary_file_string.strip("£")
    drawi=Geometry.Drawing(file_str)
    width=bottom_right[0]-top_left[0]
    height=-bottom_right[1]+top_left[1]
    file_str=drawi.from_Drawing_to_temp_string()
    create_directory("animations/"+current_file_name) #used to be     create_directory("./animations/"+current_file_name)
    filenro=nro_of_files_in_directory("animations/"+current_file_name) #here it also used to be ./anim... not anim...
    savename= "animations//"+current_file_name+"//"+str(filenro+100000)
    spin_turtle.pencolor(turtle_screen_bg_color) #we don't care about the turtle, we just use it to change color_format
    bg_color=spin_turtle.pencolor()  
    PngMaker.draw_drawing(file_str,width,height,top_left,bg_color,save_name=savename,style="basic")
  

#saves any file to given subdirectory
def save_string_to_file(file_text,file_name,sub_directory):
    modified_file_name=sub_directory+"/"+file_name+".txt"
    truth=True
    if path.exists(modified_file_name):
        truth=messagebox.askyesno("File already exists","Overwrite?")
    if truth==False:#if user doesn't want to overwrite, then go away from the method
        return False
    with open(modified_file_name, "w") as file:
    # Write the string to the file
        file.write(file_text)
    return True #return value tells if new file was created

#when the new_button is pressed
def new_file(event=None):
    global temporary_file_string
    global current_file_name
    global label_starting_index
    current_file_name="new_file"
    truth=True
    truth=messagebox.askyesno("Creating a new file", "All unsaved work will be lost, continue?")
    if truth:
        temporary_file_string=""
        layer_items.items=[]
        temp_turtle.reset()
        temp_turtle.shapesize(1.8,1.8,2)
        t.reset()
        label_starting_index=0 #perhaps this removes a bug. Layers did not show after creating new file
        update_layer_labels()
        contin=messagebox.askyesno("Continue?","Do you want to use old drawings for the new file?")
        if contin:
            model_popup() #here user is asked to create model that new file is based on:

#this is to create an option to merge without giving the filename as parameter
def merge_active():
    filename=filedialog.asksaveasfilename(initialdir="./drawings",defaultextension=".txt")
    filename=filename_end(filename)
    merge_active_layers(filename)

#returns the string which represents the drawing formed from active layers, doesn't  yet save it
def merged_layer_as_string():
    result="£"
    lista=layer_items.items
    size=len(lista)
    depths=[]
    for i in range(0,size):
        depths.append(float(lista[i][0]))        
    depths.sort(key = float)
    # Printing output
    order=[]#tähän listataan indeksit järjestykseen, niin, että ensiksi tulee sen indeksin arvo,
        #jonka depth on pienin. Jos algoritmi toimii oikein, niin esimerkiksi depthien arvot
        # 3,-2,5,3,4,0 pitäisivät antaa tuloksen order=[1,5,0,3,4,2]
    for i in range(0,size):
        for j in range(0,size):
            if depths[i]==lista[j][0] and j not in order:
                order.append(j)
    for i in order:
        if lista[i][7]=="active":
            result=result+layer_items.modified_object_to_string(lista[i],0,100000)[1:]+ "pu()|" 
            #100 000 is arbitrary, needs to be > number of commands
    return result

#takes active items and saves them to new file
def merge_active_layers(filename:str):
    result=merged_layer_as_string()
    filename="drawings/"+filename+".txt"
    save_drawing_as(result,filename)

#creates a new file, by merging files with names in the list 'filenames'
def create_merged_files(filenames:List[str], new_filename):
    new_text=""
    for i in range(0,len(filenames)):
        new_text += load_file(filenames)
    save_string_to_file(new_text,new_filename,"files")
    messagebox.showinfo(title="Saving", message="merged files were saved as files/"+new_filename+".txt")

#from index onwards shifts the color to the average of current color and new_color
def shift_color_from(commands:str,index:int,r_shift:float,g_shift:float,b_shift:float):
    array=MemoryHandler.split_the_string(commands,"|")
    before_commands=array[0:index]
    beforestr=MemoryHandler.glue_the_split(before_commands,"|")
    r_past=0.5#if there is no value obtainable
    g_past=0.5#same
    b_past=0.5#same
    past_color_command=beforestr[last_command_of_type("co",beforestr)[0]:last_command_of_type("co",beforestr)[1]]
    #finds the last given color command before index
    if last_command_of_type("co",beforestr)[1]in range(0,index-1):#so if there is color command in commands-string
        #-1 in index-1 is a test to avoid a bug 10:50,28.6
        r_past=float(Commands.nth_parameter(past_color_command,0)[1:]) #1: takes the [of
        g_past=float(Commands.nth_parameter(past_color_command,1))
        b_past=float(Commands.nth_parameter(past_color_command,2)[:-1])
    shift_color=[r_shift,g_shift,b_shift]
    past_color=[r_past,g_past,b_past]
    color_now=shifted_color(past_color,shift_color)
    before_commands.append("co(["+str(color_now[0])+","+str(color_now[1])+","+str(color_now[2])+"])") #jos kynän väri muuttuu esim. vain alussa niin on lisättävä muutoskohtaan tieto
    for i in range(index,len(array)):
        if array[i][0:2]=="co" and i>=index:
            r_past=float(Commands.nth_parameter(array[i],0)[1:]) #1: takes the [of
            g_past=float(Commands.nth_parameter(array[i],1))
            b_past=float(Commands.nth_parameter(array[i],2)[:-1])
            shift_color=[r_shift,g_shift,b_shift]
            past_color=[r_past,g_past,b_past]
            color_now=shifted_color(past_color,shift_color)
            before_commands.append("co(["+str(color_now[0])+","+str(color_now[1])+","+str(color_now[2])+"])")
        else:
            before_commands.append(array[i])
    #now color() commands are ok, they are saved in before_commands next fill_color commands    
    temp_temporary="£"+MemoryHandler.glue_the_split(before_commands,"|")+"|"#"+"|" added 18.11.  
    return shift_fillcolor_from(temp_temporary,index,r_shift,g_shift,b_shift)


#from index onwards shifts the color to the average of current color and new_color
def shift_fillcolor_from(commands:str,index:int,r_shift:float,g_shift:float,b_shift:float):
    array=MemoryHandler.split_the_string(commands,"|")
    before_commands=array[0:index]
    beforestr=MemoryHandler.glue_the_split(before_commands,"|")
    past_color_command=beforestr[last_command_of_type("fc",beforestr)[0]:last_command_of_type("fc",beforestr)[1]]
    r_past=0.5#if there is no value obtainable
    g_past=0.5#same
    b_past=0.5#same
    #finds the last given color command before index
    if last_command_of_type("fc",beforestr)[1] in range(0,index-1):#so if there is fillcolor command in commands-string
        #-1 in index-1 is a test to avoid a bug 10:50,28.6
        r_past=float(Commands.nth_parameter(past_color_command,0)[1:]) #1: takes the [of
        g_past=float(Commands.nth_parameter(past_color_command,1))
        b_past=float(Commands.nth_parameter(past_color_command,2)[:-1])
    shift_color=[r_shift,g_shift,b_shift]
    past_color=[r_past,g_past,b_past]
    color_now=shifted_color(past_color,shift_color)
    before_commands.append("co(["+str(color_now[0])+","+str(color_now[1])+","+str(color_now[2])+"])") #jos kynän väri muuttuu esim. vain alussa niin on lisättävä muutoskohtaan tieto
    for i in range(index,len(array)):
        if array[i][0:2]=="fc" and i>=index:
            r_past=float(Commands.nth_parameter(array[i],0)[1:]) #1: takes the [of
            g_past=float(Commands.nth_parameter(array[i],1))
            b_past=float(Commands.nth_parameter(array[i],2)[:-1])
            shift_color=[r_shift,g_shift,b_shift]
            past_color=[r_past,g_past,b_past]
            color_now=shifted_color(past_color,shift_color)
            before_commands.append("fc(["+str(color_now[0])+","+str(color_now[1])+","+str(color_now[2])+"])")
        else:
            before_commands.append(array[i])
    return before_commands #name before_commands is misleading should be new_commands, but lets leave it there



#colors are given by three parameter float lists of values between 0 and 1 result is also a similar list
def shifted_color(past_color:List[float],shift_color:List[float]):
    new_color=[past_color[0]+shift_color[0],past_color[1]+shift_color[1],past_color[2]+shift_color[2]]
    for i in range(0,3):
        if new_color[i]>1:
            new_color[i]=1
        if new_color[i]<0:
            new_color[i]=0
    return new_color

#Takes color and shifts its toward bg_color. This will  be used for visible but not active layers
def color_dimmening(past_color:List[float],bg_color:List[float]):
    new_color=[(past_color[0]+5*bg_color[0])/6,(past_color[1]+5*bg_color[1])/6,(past_color[2]+5*bg_color[2])/6]
    for i in range(0,3):
        if new_color[i]>1:
            new_color[i]=1
        if new_color[i]<0:
            new_color[i]=0
    return new_color

def pen_from(commands:List[str],index:int,size:int):
    new_commands=[]
    for i in range(0,len(commands)):
        new_commands.append(commands[i])
        if i==index:
            new_commands.append("ps("+str(size)+")") #jos kynän väri muuttuu esim. vain alussa niin on lisättävä muutoskohtaan tieto
    for i in range(0,len(new_commands)):
        if new_commands[i][0:2]=="ps" and i>=index:
            new_commands[i]="ps("+str(size)+")"
    return new_commands

def add_command_at(commands:List[str],index:int,command:str):
    if index>len(commands):
        return commands+[command]
    if index<0:
        return [command]+commands
    new_commands=[]
    new_commands=commands[0:index]+[command]+commands[index:]
    return new_commands


def fontsize_from(commands:List[str],index:int,size:int):
    new_commands=[]
    for i in range(0,len(commands)):
        new_commands.append(commands[i])
    for i in range(0,len(new_commands)):
        if new_commands[i][0:2]=="wr" and i>=index:
            style=Commands.nth_parameter(new_commands[i],0)
            font=Commands.nth_parameter(new_commands[i],1)
            text=new_commands[i][6:-1]
            text=text[text.find(",")+1:]
            text=text[text.find(",")+1:]
            text=text[text.find(",")+1:]#trick here is to take the whole command and remove the "nontext"
            new_commands[i]="wr("+style+","+font+","+str(size)+","+text+")"
    return new_commands

def color_from(commands:List[str],index:int,color:List[float]):
    new_commands=[]
    for i in range(0,len(commands)):
        new_commands.append(commands[i])
        if i==index:
            new_commands.append("co("+str(color)+")") #jos kynän väri muuttuu esim. vain alussa niin on lisättävä muutoskohtaan tieto
    for i in range(0,len(new_commands)):
        if new_commands[i][0:2]=="co" and i>=index:
            new_commands[i]="co("+str(color)+")"
    return new_commands

def fillcolor_from(commands:List[str],index:int,color:List[float]):
    new_commands=[]
    for i in range(0,len(commands)):
        new_commands.append(commands[i])
        if i==index:
            new_commands.append("fc("+str(color)+")") #jos kynän väri muuttuu esim. vain alussa niin on lisättävä muutoskohtaan tieto
    for i in range(0,len(new_commands)):
        if new_commands[i][0:2]=="fc" and i>=index:
            new_commands[i]="fc("+str(color)+")"
    return new_commands



#this takes a list os commands and shifts all the coordinates starting from commmand number index
def shifted_commands_from(commands:List[str],index:int,x_shift:int,y_shift):
    new_commands=[]
    for i in range(0,len(commands)):
        new_commands.append(commands[i])
        if commands[i][0:4]=="goto" and i>=index:
            old_x=int(Commands.nth_parameter(commands[i],0))
            old_y=int(Commands.nth_parameter(commands[i],1))
            new_commands[i]="goto("+str(old_x+x_shift)+","+str(old_y+y_shift)+")"
    return new_commands

#this takes a list os commands and shifts all the coordinates starting from commmand number index
def rotated_commands_from(commands:List[str],index:int,rotation:int):
    fake_origo=[0,0]#rotation happens around this point, where turtle was at index
    new_commands=[]
    for i in range(0,index):#this loop finds the last location
        if commands[i][0:4]=="goto":
            x=int(Commands.nth_parameter(commands[i],0))
            y=int(Commands.nth_parameter(commands[i],1)) 
            fake_origo=[x,y]
    for i in range(0,len(commands)):
        new_commands.append(commands[i])
        if commands[i][0:4]=="goto" and i>=index:
            old_x=int(Commands.nth_parameter(commands[i],0))
            old_y=int(Commands.nth_parameter(commands[i],1))
            old_x_shift=old_x-fake_origo[0]#these tell what was the shift from rotation (fake)origo
            old_y_shift=old_y-fake_origo[1]#to old position, before rotation
            new_x_shift=int(old_x_shift*math.cos(math.pi*rotation/180)-old_y_shift*math.sin(math.pi*rotation/180))
            new_y_shift=int(old_y_shift*math.cos(math.pi*rotation/180)+old_x_shift*math.sin(math.pi*rotation/180))
            new_commands[i]="goto("+str(fake_origo[0]+new_x_shift)+","+str(fake_origo[1]+new_y_shift)+")" 
        if commands[i][0:2]=="sh" and i>=index:   
            old_heading=int(Commands.nth_parameter(commands[i],0))
            new_heading=old_heading+rotation
            if new_heading>360:
                new_heading -= 360
            new_commands[i]="sh("+str(new_heading)+")"
    return new_commands 


#this takes a list os commands and shifts all the coordinates starting from commmand number index
def scaled_xy_commands_from(commands:List[str],index:int,scale_factorx:float,scale_factory:float):
    fake_origo=[0,0]#rotation happens around this point, where turtle was at index
    new_commands=[]
    for i in range(0,index):#this loop finds the last location
        if commands[i][0:4]=="goto":
            x=int(Commands.nth_parameter(commands[i],0))
            y=int(Commands.nth_parameter(commands[i],1)) 
            fake_origo=[x,y]
    for i in range(0,len(commands)):
        new_commands.append(commands[i])
        if commands[i][0:4]=="goto" and i>=index:
            old_x=int(Commands.nth_parameter(commands[i],0))
            old_y=int(Commands.nth_parameter(commands[i],1))
            old_x_shift=old_x-fake_origo[0]#these tell what was the shift from rotation (fake)origo
            old_y_shift=old_y-fake_origo[1]#to old position, before rotation
            new_x_shift=int(old_x_shift*scale_factorx)
            new_y_shift=int(old_y_shift*scale_factory)
            new_commands[i]="goto("+str(fake_origo[0]+new_x_shift)+","+str(fake_origo[1]+new_y_shift)+")" 
        if commands[i][0:6]=="circle" and i>=index:#skaalataan nyt x:n mukaan, kun parametrejä vain yksi
            old_r=int(Commands.nth_parameter(commands[i],0))
            new_commands[i]="circle("+str(int(old_r*math.sqrt(scale_factorx*scale_factory)))+")"
        if commands[i][0:2]=="ps" and i>=index:
            old_p=int(Commands.nth_parameter(commands[i],0))
            new_commands[i]="ps("+str(round(old_p*math.sqrt(scale_factorx*scale_factory)))+")"
        if commands[i][0:2]=="wr" and i>=index:#skaalataan nyt x:n mukaan, kun parametrejä vain yksi
            style=Commands.nth_parameter(new_commands[i],0)
            fon=Commands.nth_parameter(new_commands[i],1)
            fontsize=int(Commands.nth_parameter(new_commands[i],2))
            text=new_commands[i][new_commands[i].find(",")+1:]
            text=text[text.find(",")+1:]
            text=text[text.find(",")+1:]
            text=text[text.find("'")+1:text.rfind("'")]
            fontsize=str(round(fontsize*math.sqrt(scale_factorx*scale_factory)))
            new_commands[i]="wr("+style+","+fon+","+fontsize+","+text+")|"
    
    return new_commands 

#this scales the x-axis, so it flattens everythin, excepts circles :(
def scaled_commands_from(commands:List[str],index:int,scale_factor:float):
    new_commands=scaled_xy_commands_from(commands,index,scale_factor,scale_factor)
    return new_commands


#this returns info about the command
def command_info(command:str):
    command_dict={}
    command_dict["LOOP(VCT)"]="list of commands written in place of VCT are done one by one"
    text="if first argument represen the same argument, does the thing in the third argument,"
    text=text+"if not, does the fourth argument (which is optional). May cause an error, if two first arguments aren't numbers"
    command_dict["IF(TXT,TXT,TXT,OPT)"]=text
    command_dict["draw|"]= "Draw a line from last position to the clicked position. Hotkey: ctrl+q."
    command_dict["relocate|"]="Go to the clicked position without drawing. Hotkey]= ctrl+m."
    command_dict["move|"]="moves a vertice close to clicked point to a new location chosen by next click"
    command_dict["circle(*r)|"]="Draw a circle, with radius *r, which can be written on \n the command line or picked later."
    command_dict["circle|"]="Draw a circle, first click sets the center and second the radius"
    command_dict["polygon|"]="Draw a polygon, two consecutive clicks near to each other end the drawing"
    command_dict["join|"]="Join two lines to each other by clicking them"
    text="Draw a polygon which approximates circle, i.e., a 'polygon circle'. If image is going to be stretched"
    text=text+ " with different values on x and y axis, circle stays circle, but pircle stretches as other elements."
    command_dict["pircle(NRO)|"]=text 
    command_dict["rect(*p)|"]="Draw a rectangle, with sides of lengths *p."
    command_dict["forward(*x)|"]="Draw a line of length *x in pixels to the direction which pen is heading."
    command_dict["jump(*x)|"]="Jump *x pixels to the direction which pen is heading. Nothing is drawn. Hotkey]= ctrl+j."
    command_dict["penup|"]="Put the pen up, so it doesn't draw while goto command is used."
    command_dict["pendown|"]="Put the pen down, so it draws."
    command_dict["goto(*p)|"]="Go to point given by the coordinates in *p variable. If pen is in down position, a line is drawn."
    command_dict["setheading(*r)|"]="Tell the pen in which direction the next line is drawn. 0 is right, 90 up, 180 left, 270 down. Hotkey]= ctrl+h."
    command_dict["turn(*r)|"]="Give an angle to which pen turns in counterclockwise direction. Hotkey]= ctrl+t."
    command_dict["pensize(NRO)|"]="Change the thickness of the pen."
    command_dict["color(COL)|"]="Change the color of the pen."
    command_dict["fillcolor(COL)|"]="Change the color, which pen uses to fill color between the lines."
    command_dict["begin fill|"]="When you use end_fill everything drawn between begin_fill and end_fill is filled with fillcolor. Hotkey]= ctrl+b."
    command_dict["end fill|"]="Stop filling. If the pen was filling, then color is added from the last begin_fill() command onwards. Hotkey]= ctrl+e."
    command_dict["repeat(NRO)|"]="Put in the first position in command_line, commands are repeated as many times as given by the parameter "
    command_dict["pow(NRO,SCX)"]
    command_dict["write("]="Write text, parameters are style, font, fontsize and the text. Hotkey]= ctrl+w."
    command_dict["put"]="Open previously saved drawing."
    command_dict["change(FILE)|"]="replace an active drawing by a dferent drawing, conserving the layer parameters."
    text="Save current drawing with the name given to the parameter *w. This can overwrite existing file with same name."
    text=text+"Start new drawing file immediately."
    command_dict["save(*w)|"]=text
    command_dict["showfunctions"]="Show your previously created functions. You can copy paste them, but not mody here.Hotkey]= ctrl+f." 
    command_dict[ "add function"]="Make a new shortcut command, which you can use later to produce a command on the commandline." 
    text="Delete your previously added function shortcut command, write the name of the command in *w. You can use "
    text=text+"showfunctions and copy paste the part '$yourfunctionname(...)' to the *w."
    command_dict[ "delete_function(*w)|"]=text
    command_dict["more..."]="More commands."
    command_dict["empty"]="Empties the command line. Hotkey= ctrl+x."
    command_dict["shift color(*x,*x,*x)|"]="Shift the color of all active layers. First parameter is for red, second for green, third to blue value."
    command_dict["delete(*r)|"]="From the end of drawing orders, delete last *r commands from the drawing."
    command_dict["deletefunction(*w)|"]="Delete every function-command that starts with given *w and is over 3 characters long."
    command_dict["place(FILE,PT)|"]="Places drawing you choose, to the position given by point"
    command_dict["rsave|"]="Saves the current drawing with random 8 letter name on subdirectory drawings/rsaves. Hotkey= ctrl+r."
    command_dict["depth(NRO)|"]="Change the depth of active layers. Higher depth layers are drawn above the lower ones."
    command_dict["rotate(ANG,OPT)|"]="Rotate active layers by angle *r."
    command_dict["scale(SC,OPT)|"]="Scale active layers by multiplier *s."
    command_dict["shift(*p)|"]="Shift active layers in the by *p pixels."
    command_dict["x sht(*x)|"]="Shift active layers in the x-direction by *x pixels."
    command_dict["y sht(*x)|"]="Shift active layers in the y-direction by *x pixels."
    command_dict["copy|"]="Make a copy of all active layers. Hotkey]= ctrl+c."
    command_dict["destroy|"]="Destroy all active layers from the file."
    command_dict["merge(*w)|"]="Forms a new drawing, which contains current active layers glued together. This new drawing is added to the file."
    command_dict["glue file|"]="Adds all drawings in an old file, to the file currently operated. The parameter will be chosen later."
    command_dict["spin(*p,*p,*p)|"]="Spin in the image, the first *p-coordinate stays fixed, second *p-coordinate moves to the place of the third *p-coordinate."
    command_dict["activate(*p,*p)|"]="Activate all the layers, whose origo is in the rectancle with diagonal coordinates given by *p and *p."
    command_dict["grid_positions"]="Sets layers in a grid formation and choose parameters for the number of columns, gaps and the randomness of placement."
    command_dict["orientation setup"]="Sets orientations for layers, i.e., how much objects are rotated and how much there is randomness in the rotation."
    command_dict["depth setup"]="Sets depths of the objects including the randomness of depths."
    command_dict["color setup"]="Set the amount of color shts and randomness involved in them."
    command_dict["depth to scale(NRO)|"]="Objects in the picture are zoomed as they were looked at the depth level *x."
    command_dict["scale to depth(NRO)|"]="Objects size stays the same, but their depths are changed as they were looked from depth *x."
    command_dict["from to(NRO,NRO)|"]="#objects are scaled according to size they are drawn and as they were looked at depth of 1st parameter with 2nd parameter being the normal size"
    command_dict["horizon(NRO,PT)|"]="Objects in the picture are zoomed as they were looked at the depth level *x. and there were a horizon at the point *p."
    text="puts a drawing with name FILE into depth NRO in such a way that it 'looks' like it was in the coordinate PT. The closer" 
    text=text+ "it is to the 'camera' the further a way it actually is from PT. with NRO=0 it is located exactly in PT."
    command_dict["putD3(FILE,PT,NRO)|"]=text 
    command_dict["throw(*l,*s)"]="Put the drawing *l in the place where you are dragging the mouse, *s is the time in seconds after next item is put" 
    text="put objects in a pseudo 3D grid. depth is the value for z-dimension. Objects size of the canvas is defined as"
    text=text+"they were seen by an observer located at depth 100."
    command_dict["3Dgrid setup"]=text 
    command_dict["activation setup"]="Set layers active by a specied property."
    text="Create new drawings for each active layer, so that every text in them is replaced by the given text."
    text=text+"These new layers are saved by random names and old layers are removed from the file."
    command_dict["rewrite(*w)|"]=text
    command_dict["position setup"]="Change the positions of active items."
    command_dict["order setup"]="Set the order of the layer according to some parameter."
    command_dict["add text"]="Add a piece of text into the current position as a new layer."
    text="if parameter is positive, filters out colors further away than the parameter from the pencolor"
    text= text+"if negative, filters out colors closer to the pencolor, values between -3 and 3 are meaningful"
    command_dict["filter(SCX)|"]=text
    text="Draw a dot diagram from CSV, two last parameters tell which columns from CSV are drawn on x- and y-axis."
    text=text+"Note that this columns must consist of numbers, and this numbers are drawn according to same coordinates as drawcoordinates|"
    command_dict["dots(CSV,NRO,NRO)|"]="Draw a dot diagram from CSV, two last parameters tell which columns from CSV are drawn"
    command_dict["transpose(TXT)|"]="for matrices like ((1,2),(3,4),(5,6)) this returns a str with flipped coordinates, e.g. ((1,3,5),(2,4,6))"

    return command_dict[command]

def command_lists(list_name:str):
    lista=[]
    if list_name=="draw":
        lista=["begin fill|","color(COL)|","draw|","end fill|","fillcolor(COL)|", "forward(NRO)|", "goto(PT)|","jump(NRO)|"]
        lista=lista+[ "lay(FILE)|", "pendown|","penup|","pensize(NRO)|","pircle(NRO)|","place(FILE,PT)|","put(FILE)|"]
        lista=lista+[ "rect(PT)|","relocate|","repeat(NRO)|","save(TXT)|","setheading(ANG)|","turn(ANG)|","write(TXT)|","empty","more..."]
        #draw is without parameters, it is meant to work as in HellaPicture note delete| is to be changed
        #to allow parameter
        #rect is not yet made
    if list_name=="draw2":
        lista=["acos(NRO)","asin(NRO)","atan(NRO)","cos(NRO)","deletefunction(TXT)","exp(NRO)","ln(NRO)",
               "max(NRO,NRO)","min(NRO,NRO)","mod(NRO,NRO)","pow(NRO,SCX)","random(NRO,NRO)","sin(NRO)","tan(NRO)",
               "draw function(TXT)|","draw coordinates|","dots(CSV,NRO,NRO)|","[]"]
        lista=lista+ ["empty", "more..."]

    if list_name=="draw3": #this is for simple commands, more closer to normal user preferences
        lista=["arc(PT,PT,PT)|","bend(PT,PT)|","change color|","change pensize|","circle(PT,PT)|","dot(PT)|",]
        lista +=["erase all|","erase top|","join(PT,PT)|","lift(PT)|","line(PT,PT)|","move(PT,PT)|","oval(PT,PT)|"]
        lista +=["paint|","pick color|","polygon(VCT)|","rectangle(PT,PT)|"]
        lista +=["sink(PT)|","spin(PT,PT,PT)|","split(PT,PT)|","write|","empty","more..."]

    if list_name=="draw4": #this is are 'photo effects'
        lista=["animation","blackwhite|","cartoon","center|","contrast(SCL)|","CSV"]
        lista+=["filter(SCX)|","info|"]
        lista +=["photo","resize(PT)|","rsave|","screenshot|","simplify|","empty","more..."]
    if list_name=="draw5":#these are for getting values from turtle, they can then be used in the functions
        lista=["bluefill","green","blue","col","fillcol","greenfill","pos","red","redfill","size","xcor","ycor","empty","more..."]

    if list_name=="draw6":
        lista=["LOOP(VCT)","IF(TXT,TXT,TXT,OPT)","transpose(TXT)|","empty","more..."]

    if list_name=="font_type":
        lista=["bold","italic","normal"]

    if list_name=="font":
        lista=["Arial","Calibri","Franklin Gothic","Georgia","Segoe Script","Symbol", "Tahoma","Times new roman","Verdana"]

    if list_name=="fontsize":
        lista=["1","2","3", "4", "6","8", "10","12", "14", "16","20", "25","30", "40","50","60", "80","100","120","150","200"]


    if list_name=="your_text":
        lista=["*w)|","your_text)|"]

    if list_name=="edit":
        lista=["add text","add function","change(FILE)|","copy|","deletefunction(TXT)|","depth(NRO,OPT)|"]
        lista+=[ "destroy|","glue file|","merge(TXT)|","place(FILE,PT)|","put(FILE)|","rel stretch(SP,OPT)","rotate(ANG,OPT)|","scale(SCL,OPT)|"]
        lista+=["shift(PT,OPT)|","shift red(PCT,OPT)|","shift green(PCT,OPT)|","shift blue(PCT,OPT)|","shift color(RGB,OPT)|","spin(PT,PT,PT,OPT)|"]
        lista+=["x shift(NRO,OPT)|","y shift(NRO,OPT)|","empty","more..."]
    
    if list_name=="edit2":
        lista=["3Dgrid setup","activate(PT,PT)|","activation setup","color setup","depth setup","depth to scale(NRO)|","grid positions"]
        lista+=["horizon(NRO,PT)|","order setup","orientation setup","position setup","putD3(FILE,PT,NRO)|","scale setup"] 
        lista+=["rewrite(TXT)|","scale to depth(NRO)|","from to(NRO,NRO)|","screenshot|","empty","more..."] #poistettiin #test
    
    if list_name=="edit3":
        lista=["abs pos(PT,OPT)|","abs stretch(SP,OPT)|","abs color(RGB,OPT)|","abs angle(ANG,OPT)|","empty","more..."]
    return lista     #here load should pick the file on edit mode, in draw list, it should put in draw mode.

#muuttaa värityypin kolmikosta oudoksi hexatyypiksi
def hexagesimal_color(r:float,g:float,b:float):
    redint=int(255.9*r)#this idea of 255.9 instead of 256 is to try to stop the possible error with value 256
    greenint=int(g*255.9)#not tested yet
    blueint=int(b*255.9)
    return "#%02x%02x%02x" % (redint,greenint,blueint) 



#QUICK_WIDTH and QUICK_HEIGHT determine screenshotsize, this method make screen that size
def match_screensize_with_screenshots():
    global QUICK_WIDTH,QUICK_HEIGHT
    screen.setup(QUICK_WIDTH,QUICK_HEIGHT) #testing, this should make screensize to match chosen parameters


temporary_file_string=""#this is used to record the commands done for layer which is currently drawed
initialize_function_database() #this thing must be here before introducing db, otherwise the file will be missing
reserved_words=["OPT","PCT","RGB","ADD","PT","SP","VCT","SCL","SCX","SCY","ANG","NRO","COL","TXT","FILE","CSV","IND"]
reserved_names=reserved_words #Later add more here, at least name of the functions
db=FunctionOperator.FunctionDatabase(reserved_names=reserved_names)  

#GUI stars here
# Create a GUI window
root = tk.Tk()
root_width=360
root_height=630
root.geometry(str(root_width)+"x"+str(root_height))
root.title("Kuhan piirran, Olli Hella, 2024")
match_screensize_with_screenshots()
screen.bgcolor(turtle_screen_bg_color)
temp_turtle.penup()#hope these three lines don't spoil anything 15.7.
temp_turtle.showturtle()
temp_turtle.goto(0,0)
layer_data_constant=18 #this tells how much (y)space is left for each layer_data
layer_command_constant=22 #this tells how much (y)space is left for each layer_command
command_list_name="edit" #this tells which list of commands is drawn
hotkey="enabled" #do hotkeys have effects
mousepos_data=[0,0,0,0] #first two arguments tell position of the mouse cursor and other two the length and width if the screen.
#these are changed only if position() method is binded to <Motion>

layer_items=Layers()#this is the data to be drawn
layer_items.redraw(t)
popular_drawings=Popularity() #lists popularity of the objects it is important that this happens after introducing Layers()
#the reason is that Layers creates the file machinery/mini.txt used by popular_drawings
writefontsize=14 #this is 9.7. added global variable. From now on fontsize and font are decided by these 
writefont="Calibri"
writefontstyle="normal"
#this shifts between different lists of commands to be put in the command line, lists differs 

current_file_name="my_file" #this is the name for the current file that appears when you try to save already saved file
#So this is changed when you save the file first time. With this you do not have to remember the name you saved the file before.



def set_writefontsize(size:int):
    global writefontsize
    writefontsize=size

def set_writefont(fon:str):
    global writefont
    writefont=fon

def set_writefontstyle(sty:str):
    global writefontstyle
    writefontstyle=sty

#tämän on tarkoitus jossain vaiheessa kertoa infoa komennoista
def display_info(event):
    update_layer_labels()
    global command_list_name
    sector=getsector(event.x,event.y)
    command_name=command_lists(command_list_name)[sector]
    messagebox.showinfo("information",command_name + "\n"+command_info(command_name))


#this replaces all the occurrances of string a in thestring be string b 
def replace_all(thestring:str, a:str,b:str):
    return thestring.replace(a,b,-1)

#if given array, how to replace all strings are in array elements by b
def replace_all_in_array(array:str,a:str,b:str):
    for i in range(0,len(array)):
        array[i]=replace_all(array[i],a,b)

#tells over which sector we are (meaningfull only over command_line_canvas)
def getsector(x:int,y:int):
    sector=3*int(y/layer_command_constant-1.2)
    sector=sector+int(3*x/root_width)
    return sector

#depending are we on the draw mode or edit mode
def change_command_menu(event):
    global command_list_name
    sector=getsector(event.x,event.y)
    if event.y<23:
        check_basic_line(event.x,event.y)#jos naputettiin tosi ylös, katsotaan osuiko johonkin nappiin.
        return
    #this tells roughly over which command text the mouse is
    global mode
    if mode=="drawing_mode":
        drawmode_command_list(sector)
    if mode=="edit_mode":
        editmode_command_list(sector)

def check_basic_line(x,y):
    global temporary_file_string
    global temp_turtle
    global mode
    global command_line_entry
    if x>10 and x<50:
        draw_mode()


    if x>65 and x<106:
        if temp_turtle.isdown()==True:
            temp_turtle.penup()
            temporary_file_string += "pu()|"
        else:
            temp_turtle.pendown()
            temporary_file_string += "pd()|"
    if x>115 and x<133:
        open_popup("pensize")#this takes care of the temporary string also

    if x>150 and x<200:
        isit=is_temp_filling()
        if isit:
            end_fill()     
        else:
            begin_fill()

    global command_list_name
    if x>210 and x<265:#setting the font
        command_list_name="font"
        if mode=="edit_mode":
            command_line_entry.delete('1.0',END)
            command_line_entry.insert(INSERT,"add text") 

    if x>270 and x<290:#setting the fontsize
        command_list_name="fontsize"

    draw_command_list()#this is what makes the command list how
    if x>320 and x<335:
        temp_turtle.pencolor(colorchooser.askcolor()[1])
        col1=str(MemoryHandler.color_tuple_shortener(temp_turtle.pencolor(),3)) #NOTE not yet tested
        temporary_file_string += "co("+ col1+")|"
    if x>340 and x<355:
        temp_turtle.fillcolor(colorchooser.askcolor()[1])
        col2=str(MemoryHandler.color_tuple_shortener(temp_turtle.fillcolor(),3))#NOTE not yet tested
        temporary_file_string += "fc("+ col2+")|" #these initiate colors
    basic_info()

def drawmode_command_list(sector:int):
    global command_list_name
    global writefont,writefontsize,writefontstyle

    if sector>=len(command_lists(command_list_name)):# this new addition makes sector value 0 if it tries to make index error
        sector=len(command_lists(command_list_name))-1

    if command_lists(command_list_name)[sector]!="more..." and command_list_name not in ["font","fontsize","font_type"]:
        if command_lists(command_list_name)[sector] != "add function":
            command_line_entry.insert(INSERT,command_lists(command_list_name)[sector]) #tmystisen bugin korjaus, älä muuta ellet ole varma mitä teet
            #NOTE TEDELLISEEN RIVIIN TEHTIIN MUOKKAUS 20.1
    if command_lists(command_list_name)[sector]=="put": #mikäli ollaan lataamassa tiedostoa
        filename=filedialog.askopenfilename(initialdir="drawings/")
        filename=filename_without_subdir(filename,"drawings")
        command_line_entry.insert(INSERT,"("+filename+")|")
    if command_lists(command_list_name)[sector]=="empty": #mikäli halutaan tyhjentää komennot
        command_line_entry.delete('1.0',END)


    elif command_list_name=="font": #purpose of this is that clicking basic_info font leads to picking the font here
        writefont=command_lists(command_list_name)[sector]
        basic_info()
        command_list_name="font_type"
    elif command_list_name=="fontsize": #purpose of this is that clicking basic_info font leads to picking the font here
        writefontsize=command_lists(command_list_name)[sector]
        basic_info()
        if mode=="drawing_mode":
            command_list_name="draw"
        else:
            command_list_name="edit"

    elif command_list_name=="font_type": #purpose of this is that clicking basic_info font leads to picking the font here
        writefontstyle=command_lists(command_list_name)[sector]
        basic_info()
        if mode=="drawing_mode":
            command_list_name="draw"
        else:
            command_list_name="edit"

    elif command_lists(command_list_name)[sector]=="put": #onkohan tälläkään enää käyttöä?
        command_list_name="draw" 
        command_line_entry.insert(INSERT,"|")# 
    elif command_lists(command_list_name)[sector]=="more...":
        if command_list_name=="draw":
            command_list_name="draw2"
            command_entry_canvas.config(bg="lightblue")#added 7.10
        elif command_list_name=="draw2":
            command_list_name="draw3"
            command_entry_canvas.config(bg="wheat2")#added 7.10
        elif command_list_name=="draw3":
            command_list_name="draw4"
            command_entry_canvas.config(bg="pink")#added 7.10
        elif command_list_name=="draw4":
            command_list_name="draw5"
            command_entry_canvas.config(bg="lightblue")#added 7.10
        elif command_list_name=="draw5":
            command_list_name="draw6"
            command_entry_canvas.config(bg="lightblue")#added 7.10
        elif command_list_name=="draw6":
            command_list_name="draw"
            command_entry_canvas.config(bg="wheat3")#added 7.10

        #return 0 #to not to write more... on the entry field
    draw_command_list()

#when in edit mode, here are the commandlists
def editmode_command_list(sector):
    global command_list_name
    global writefont,writefontsize,writefontstyle
    global hideorigo
    if sector>=len(command_lists(command_list_name)):# this new addition makes sector value 0 if it tries to make index error
        sector=len(command_lists(command_list_name))-1
    if command_lists(command_list_name)[sector]!="more..."and command_list_name not in ["font","fontsize","font_type"]:
        if command_lists(command_list_name)[sector] != "add function":
            command_line_entry.insert(INSERT,command_lists(command_list_name)[sector]) #tmystisen bugin korjaus, älä muuta ellet ole varma mitä teet
    if command_lists(command_list_name)[sector]=="put": #myös edit modessa voi ladata tiedoston, sitä
        #ei voi tosin enää muokata
        filename=filedialog.askopenfilename(initialdir="drawings/")
        filename= filename_without_subdir(filename,"drawings") #filename_end(filename) korvattiin 20.7.
        command_line_entry.insert(INSERT,"("+filename+")|")
    elif command_lists(command_list_name)[sector]=="empty": #mikäli halutaan tyhjentää komennot
        command_line_entry.delete('1.0',END)

    elif command_lists(command_list_name)[sector]=="more...":
        if command_list_name=="edit":
            command_list_name="edit2"
        elif command_list_name=="edit2":
           command_list_name="edit3" 
        elif command_list_name=="edit3":
           command_list_name="edit" 
    elif command_lists(command_list_name)[sector]=="grid_positions":
        grid_popup()
        command_line_entry.delete('1.0',END)
    elif command_lists(command_list_name)[sector]=="3Dgrid setup":
        D3_popup()
        command_line_entry.delete('1.0',END)
    elif command_lists(command_list_name)[sector]=="orientation setup":
        orientation_popup()
        command_line_entry.delete('1.0',END)
    elif command_lists(command_list_name)[sector]=="depth setup":
        depth_popup()
        command_line_entry.delete('1.0',END)
    elif command_lists(command_list_name)[sector]=="color setup":
        color_popup()
        command_line_entry.delete('1.0',END)
    elif command_lists(command_list_name)[sector]=="scale setup":
        scale_popup()
        command_line_entry.delete('1.0',END)
    elif command_lists(command_list_name)[sector]=="activation setup":
        active_popup()
        command_line_entry.delete('1.0',END)
    elif command_lists(command_list_name)[sector]=="position setup":
        position_popup()
        command_line_entry.delete('1.0',END)
    elif command_lists(command_list_name)[sector]=="order setup":
        layerorder_popup()
        command_line_entry.delete('1.0',END)
    
    elif command_list_name=="font": #purpose of this is that clicking basic_info font leads to picking the font here
        writefont=command_lists(command_list_name)[sector]
        basic_info()
        command_list_name="font_type"

    elif command_list_name=="fontsize": #purpose of this is that clicking basic_info font leads to picking the font here
        writefontsize=command_lists(command_list_name)[sector]
        basic_info()
        if mode=="drawing_mode":
            command_list_name="draw"
        else:
            command_list_name="edit"
    elif command_list_name=="font_type": #purpose of this is that clicking basic_info font leads to picking the font here
        writefontstyle=command_lists(command_list_name)[sector]
        basic_info()
        if mode=="drawing_mode":
            command_list_name="draw"
        else:
            command_list_name="edit"

    elif command_lists(command_list_name)[sector]=="put":
        command_line_entry.insert(INSERT,"|")# 

    draw_command_list()


def draw_command_list():#draws a list of commands to canvas depending on situation
    global command_list_name
    command_entry_canvas.delete("all") #gets rid of old drawings and texts
    draw_list()


def draw_list():
    command_entry_canvas.create_line((root_width/3),0,(root_width/3),300,fill="black")
    command_entry_canvas.create_line((2*root_width/3),0,(2*root_width/3),300,fill="black")
    for i in range(0,len(command_lists(command_list_name))):
        x=60+ (root_width/3)*(i%3)
        y=40+layer_command_constant*int(i/3)
        command_entry_canvas.create_text(x,y,text=command_lists(command_list_name)[i])
    basic_info()


helping_turtle = turtle.Turtle(visible=True) #might need to change this later
#helping_turtle.hideturtle()
temp_turtle.penup() #let's see if these two create a problem
temp_turtle.goto(0,0)
turtle.speed(0)
turtle.delay(0)
turtle.tracer(0)
mode="edit_mode" #this tells if one can draw a new item or not


#when mode is true, you can draw, when false, you can edit
def draw_mode():
    global mode #edit or draw
    global temporary_file_string  
    global command_list_name  
    global special_area_mode1
    global special_area_mode2

    if mode=="edit_mode": #nämä käskyt itse asiassa aloittavat piirtämisen
        mode="drawing_mode"
        temp_turtle.showturtle()
        temp_turtle.shapesize(1.8,1.8,2)#kokeillaan tehdä tätä isommaksi
        command_entry_canvas.config(bg="wheat1")#added 7.10"
        temporary_file_string=""
        temp_turtle.color(colorchooser.askcolor()[1])
        temp_turtle.fillcolor(colorchooser.askcolor()[1])
        col1=str(MemoryHandler.color_tuple_shortener(temp_turtle.pencolor(),3)) #NOTE not yet tested
        col2=str(MemoryHandler.color_tuple_shortener(temp_turtle.fillcolor(),3))#NOTE not yet tested
        temporary_file_string += "£co("+ col1+")|"
        temporary_file_string += "fc("+ col2+")|" #these initiate colors
        temporary_file_string += "sh(0)|" #normal heading
        temporary_file_string += "ps(5)|" #standard pensize
        temporary_file_string += "pu()|" #no extra lines made
        temporary_file_string += "goto(0,0)|" #standard pensize
        temporary_file_string += "pd()|" #if pen is not down then things can be left undrawn
        temp_turtle.penup()#17.7. 23:47
        temp_turtle.setheading(0)
        temp_turtle.goto(0,0)#17.7. 23:47
        temp_turtle.pensize(5)
        temp_turtle.pendown()
    
        command_line_entry.delete('1.0',END)
        command_list_name="draw3"
        draw_command_list() #correct list need to be chosen
        special_area_mode1="color"
        special_area_mode2="color"
        for item in layer_items.items:
            if item[7]=="active":
                item[7]="visible" #every other layer should turn to some nonactive state
        update_layer_labels() 
    else:
        mode="edit_mode"
        temp_turtle.penup()
        command_entry_canvas.config(bg="lightgreen")
        command_line_entry.delete('1.0',END)#kun piirros saatu valmiiksi tyhjennä komennot
        command_list_name="edit"
        temporary_file_string += "ef()|"# to avoid potential extra filling
        saving=False
        if len(temporary_file_string)>93: #this 93 is actually quite precise number, do not change, it tells how many symbols we have
            #even without added orders
            saving=messagebox.askyesno("Save drawing", "Do you want to save the drawing?")
        if saving:
            drawing_name = filedialog.asksaveasfilename(initialdir="./drawings",defaultextension=".txt")#10:54 20.7
            truth=True
            if path.exists(drawing_name):
                truth=messagebox.askyesno("File already exists","Overwrite?")
            if truth==False:#if user doesn't want to overwrite, then go away from the method
                return
            save_drawing_as(temporary_file_string,drawing_name)
            messagebox.showinfo("information","Layer was added and drawing was saved as "+drawing_name+".")
        
        temporary_file_string=""#get ready to draw new item
        draw_command_list() #correct list need to be chosen NOTE there is achance that this line should be removed
        ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returne
        temp_turtle.reset() #otherwise temp_turtle drawing are left on the screen
        set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
        temp_turtle.shapesize(1.8,1.8,2)
        update_layer_labels()
    layer_items.redraw(t)

def start_drawing(event=None):#d
    global current_file_name
    if mode=="edit_mode":
        draw_mode()
    elif mode=="drawing_mode":
        draw_mode()
        

#tells if there is variables left to pick
def are_there_variables_to_pick():
    global command_line_entry
    text=command_line_entry.get("1.0", "end-1c")
    index_of_first_pick=first_pick()
    if index_of_first_pick>=len(text):
        spin_turtle.reset()
        return False
    return True

#variable is picked based on the coordinates that left mouse was clicked on turtle canvas
def pick_variable(x:int,y:int):
    global command_line_entry
    global reserved_words
    global text_to_add,cursor_pos#information of things written must go to the tempturtle key listening thing
    text=command_line_entry.get("1.0", "end-1c")
    index_of_first_pick=first_pick()
    if index_of_first_pick>=len(text):
        spin_turtle.reset()
        return None
    
    screen.tracer(0)
    spin_turtle.penup()
    spin_turtle.goto(int(x),int(y))
    spin_turtle.dot(5)

    v_type=""
    for word in reserved_words:
        if text[index_of_first_pick:index_of_first_pick+len(word)]==word:
            v_type=word
    
    replacer_str=""
    comma_minus=0 #if we have to get rid of comma before this v_type, this is set to 1, like in OPT, we want this

    if v_type=="PT":
        replacer_str= "("+str(int(x))+","+str(int(y))+")"

    if v_type=="NRO":
        replacer_str= str(int(x))

    if v_type=="PCT":
        replacer_str= str(int(x)/256)

    if v_type=="RGB":#for changing colors in shift
        replacer_str= "(PCT,PCT,PCT)"

    if v_type=="SP":
        replacer_str= "("+str(int(x)/256)+","+str(int(y)/256)+")"

    if v_type=="COL":
        helping_turtle.pencolor(colorchooser.askcolor()[1])
        color=helping_turtle.pencolor()
        r=str(color[0])[0:5]
        g=str(color[1])[0:5]
        b=str(color[2])[0:5]
        replacer_str=r+","+g+","+b

    if v_type=="SCL":
        replacer_str= str(Geometry.distance(0,0,int(x),int(y))/100)[0:8]
    if v_type=="SCX":
        replacer_str= str(int(x)/100)
    if v_type=="SCY":
        replacer_str= str(int(y)/100)

    if v_type=="ANG":
        replacer_str=str(int(Geometry.angle_to(0,0,x,y)))

    if v_type=="VCT":
       replacer_str=str(int(x))+","+str(int(y))+",ADD"

    if v_type=="ADD":
       replacer_str=str(int(x))+","+str(int(y))+",ADD"
    
    if v_type=="CSV":
        #data_matrix_str=FunctionOperator.load_file_dialog()
        #replacer_str=data_matrix_str
        csv_popup()

    if v_type=="FILE": 
        filename = filedialog.askopenfilename(initialdir="drawings/")
        filename=filename_without_subdir(filename,"drawings")# 
        replacer_str=filename
    if v_type in ["TXT"]:
        replacer_str=""
        cursor_pos=index_of_first_pick
    if v_type in ["OPT"]:
        replacer_str=""
        cursor_pos=index_of_first_pick
        comma_minus=1
    if v_type in ["IND"]:
        index=layer_items.closest_layer(x,y,distance_maximum=2000)
        replacer_str=str(index+1)+",IND"
        cursor_pos=index_of_first_pick
        #comma_minus=1


    command_line_entry.delete('1.0',END)
    new_text=text[:index_of_first_pick-comma_minus]+replacer_str+text[index_of_first_pick+len(v_type):]
    command_line_entry.insert(INSERT,new_text)
    text_to_add=command_line_entry.get("1.0", "end-1c")


    basic_info()
    return replacer_str




#returns the first index of coordinate command in commandline
def first_pick():
    global command_line_entry
    global reserved_words
    text=command_line_entry.get("1.0", "end-1c")
    minimum=len(text)
    for word in reserved_words:
        if text.find(word)!=-1:
            if text.find(word)<minimum:
                minimum=text.find(word)
    return minimum




def command_entry_index_formatting(index:int):
    return str(1+int(index/command_line_entry.height))+"."+str(index%command_line_entry.width) #KESKEN
    

#saves currently drawn object to file and adds it as an item to layer.items
def save_drawing_as(file_text:str,filenam:str):
    global temporary_file_string
    with open(filenam,"w") as file:
    # Write the string to the file
        file.write(file_text)
    realname=filename_without_subdir(filenam,"drawings") #Lisätty 20.7.
    layer_items.add_item(0,"objects",realname,[1,1],0,0,0,"active",0,0,0,"",file_text)
    update_layer_labels()
    create_mini_image(realname,"drawings/"+realname)
    temporary_file_string=""

#I modified this so that the upper method used to be this one, but the filedialog part was in the upper one. Let's see if there is a bug
def save_drawing(file_text):
    filename = filedialog.asksaveasfilename(defaultextension=".txt",initialdir="drawings/")
    save_drawing_as(file_text,filename)

#We want to have method with no arguments, just to save temp_file_str
def save_temp_file():
    global temporary_file_string
    temporary_file_string += "ef()|"# otherwise filling dissappears
    save_drawing(temporary_file_string)

#method to abandon temporary drawing without saving
def delete_drawing():
    global mode
    global temporary_file_string
    temporary_file_string=""
    if mode=="drawing_mode":#there was no if before
        #mode=False
        layer_items.redraw(t)
        temp_turtle.reset()
        temp_turtle.shapesize(1.8,1.8,2)
        temp_turtle.color(colorchooser.askcolor()[1]) 
        temp_turtle.fillcolor(colorchooser.askcolor()[1])
        col1=str(MemoryHandler.color_tuple_shortener(temp_turtle.pencolor(),3)) 
        col2=str(MemoryHandler.color_tuple_shortener(temp_turtle.fillcolor(),3))
        temporary_file_string += "£co("+ col1+")|"
        temporary_file_string += "fc("+ col2+")|" #these initiate colors
        temporary_file_string += "sh(0)|" #normal heading
        temporary_file_string += "ps(5)|" #standard pensize
        temporary_file_string += "pu()|" #no extra lines made
        temporary_file_string += "goto(0,0)|" #start position is also needed to be added
        temporary_file_string += "pd()|" #so that things will be painted unless otherwise stated
        temp_turtle.setheading(0)
        temp_turtle.pensize(5)
        temp_turtle.penup()
        temp_turtle.goto(0,0)
        temp_turtle.pendown()
        draw_command_list()
    

#this is to get rid of whole path of filename
def filename_end(filename:str):
    help=MemoryHandler.split_the_string(filename,"/")
    realname=help[-1]#takes the string after last / symbol
    realname=realname[:-4]#gets rid of .txt
    return realname

# 20.7. this is to allow subdir working, all filename_end usages might be needed to replace by this
def filename_without_subdir(filename:str,subdirname):
    result=filename
    if subdirname in filename:
        result=result[result.find(subdirname):]
    result=result.replace("/","\\")#if there is "/" it is confused with dividing
    result=result[len(subdirname)+1:-4]
    return result

special_area_mode1="local"#this tells which kind of operations can be done in the lower part of canvas
#other options are at least global. Left side of areas.
special_area_mode2="local"#right side of areas.

#this is what happens when left mouse is clicked in layer_data_canvas area
def do_something(event):
    global temporary_file_string
    global special_area_mode1,special_area_mode2
    global shift_click_size
    global shift_click_pos
    #if len(layer_items.items)==0:#prevent errors
    #    return

    if is_it_in_pen_area(event.x,event.y) and mode=="drawing_mode":
        [bx,by]=[pen_area()[0],pen_area()[1]+100]
        if abs(bx-event.x)<10:
            temp_turtle.pensize(round(1+0.0008*(by-event.y)*(by-event.y)*(by-event.y)+0.3*(by-event.y)))
            temporary_file_string += "ps("+str(temp_turtle.pensize())+")|"
        if bx-event.x>10 and bx-event.x<25 and by-event.y<50 :
            if temp_turtle.isdown():
                temp_turtle.penup()
                temporary_file_string += "pu()|"
            else:
                temp_turtle.pendown()
                temporary_file_string += "pd()|"
        if bx-event.x<-10 and bx-event.x>-25 and by-event.y<50:
            if temp_turtle.filling():
                end_fill()
            else:
                temp_turtle.begin_fill()
                temporary_file_string += "bf()|"

        pen_area() #to redraw the colors
        basic_info()

    if is_it_in_shift_area(int(event.x),int(event.y)) and special_area_mode1=="global":
        layer_items.shift_active(2*int(event.x -middle_of_shift_area()[0]),-2*int(event.y-middle_of_shift_area()[1]))
        #the rest is for the DRAW_mode picture
        temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
        shift_x=2*int(event.x -middle_of_shift_area()[0])
        shift_y=-2*int(event.y -middle_of_shift_area()[1])
        changed_coms=shifted_commands_from(temp_coms,0,shift_x,shift_y)
        temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" #+"|" was added here 18.11.
        draw_temporary_file()
        update_layer_labels()
        layer_items.redraw(t)
        return

        
    if is_it_in_shift_area(int(event.x),int(event.y)) and special_area_mode1=="local": #this actually means that we are scaling
        for i in range(0,len(layer_items.items)): 
            if layer_items.items[i][7]=="active":
                layer_items.items[i][3][0]=abs(layer_items.items[i][3][0]*2*(event.x -shift_click_pos[0])/shift_click_size)
                layer_items.items[i][3][1]=abs(layer_items.items[i][3][1]*2*(event.y -shift_click_pos[1])/shift_click_size)
                layer_items.items[i][5]=int(layer_items.items[i][5]*2*abs(event.x -shift_click_pos[0])/shift_click_size)
                layer_items.items[i][6]=int(layer_items.items[i][6]*2*abs(event.y -shift_click_pos[1])/shift_click_size)
        #rest is for DRAW mode
        temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
        scale_factorx=1+2*(event.x -middle_of_shift_area()[0])/shift_click_size
        scale_factory=1+2*(event.y -middle_of_shift_area()[1])/shift_click_size
        changed_coms= scaled_xy_commands_from(temp_coms,0,scale_factorx,scale_factory)
        temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" #+"|"  was added here 18.11.
        draw_temporary_file()        
        
        update_layer_labels()
        layer_items.redraw(t)
        return #there shouldn¨t be double action
    
    if is_it_in_shift_area(int(event.x),int(event.y)) and special_area_mode1=="color": #added 14.8.
        global palc
        palc.loc=[shift_click_pos[0]+5,shift_click_pos[1]]
        xpos=event.x-palc.loc[0]
        ypos=event.y-palc.loc[1]
        if xpos<0 and (palc.color_show[3]-palc.color_show[2])>0.4:
            palc.blueness=(palc.color_show[0]*ypos+palc.color_show[1]*(palc.size[1]-ypos))/palc.size[1]

        if 0<xpos<palc.size[0] and (palc.color_show[3]-palc.color_show[2])>0.4:#0.4 is somewhat random, but don't change
            palc.zoomin(xpos,ypos)
        elif 0<xpos<palc.size[0] and (palc.color_show[3]-palc.color_show[2])<0.4:#0.4 is somewhat random, but don't change
            new_color=palc.zoomout(xpos,ypos)
            temp_turtle.pencolor((new_color[0],new_color[1],new_color[2]))
            temporary_file_string += "co(["+str(new_color[0])[0:5]+","+str(new_color[1])[0:5]+","+str(new_color[2])[0:5]+"])|"
        update_layer_labels()
        palc.paint_palette(layer_data_canvas)
        basic_info()




    if is_it_in_scale_area(int(event.x),int(event.y)) and special_area_mode2=="local":
        xdis=event.x-middle_of_scale_rotate_area()[0]
        ydis=event.y-middle_of_scale_rotate_area()[1]
        scale_factor=0.04*math.sqrt(xdis*xdis +ydis*ydis)
        rot_factor=int(Geometry.angle_to(0,0,xdis,-ydis))
        layer_items.scale_active(scale_factor)
        layer_items.rotate_active(rot_factor)
        #here the DRAW -mode commands start
        z=Geometry.Complex(0,0)
        z2=Geometry.Complex(25,0)
        z3=Geometry.Complex(xdis,ydis)#poistetiin - merkki ydis:n edestä 12.25 6.7.
        #we proceed by moving the stable point to 0,0 then scaling and rotating and then shifting the stable point back
        changed_coms=MemoryHandler.split_the_string(temporary_file_string,"|") #tässä esimerkiksi poistettiin origon merkitys, katsotaan mitä seuraa
        temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" #+"|"  wasadded here 18.11.
        paramets=Geometry.spin_transformation_parameters(z,z2,z3)
        temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
        changed_coms=scaled_commands_from(temp_coms,0,paramets[0])
        temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" #+"|"  wasadded here 18.11.
        temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
        changed_coms=rotated_commands_from(temp_coms,0,paramets[1])
        temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" #+"|"  wasadded here 18.11.
        temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
        temporary_file_string=MemoryHandler.glue_the_split(temp_coms,"|")+"|" #+"|"  wasadded here 18.11.
        draw_temporary_file()
        update_layer_labels()
        layer_items.redraw(t)
        return  #there shouldn¨t be double action
    
    if is_it_in_scale_area(int(event.x),int(event.y)) and special_area_mode2=="global":
        xdis=event.x-middle_of_scale_rotate_area()[0]
        ydis=event.y-middle_of_scale_rotate_area()[1]
        layer_items.spin_active(0,0,shift_click_size/4,0,xdis,-ydis)#with this values spin transformation keeps origo fixed and makes
        #logical scaling+rotation
        #rest is for DRAW-mode
        z=Geometry.Complex(0,0)
        z2=Geometry.Complex(25,0)
        z3=Geometry.Complex(xdis,-ydis) 
        #we proceed by moving the stable point to 0,0 then scaling and rotating and then shifting the stable point back
        changed_coms=MemoryHandler.split_the_string(temporary_file_string,"|") #tässä esimerkiksi poistettiin origon merkitys, katsotaan mitä seuraa
        temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" #+"|"  wasadded here 18.11.
        paramets=Geometry.spin_transformation_parameters(z,z2,z3)
        temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
        changed_coms=scaled_commands_from(temp_coms,0,paramets[0])
        temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" #+"|"  wasadded here 18.11.
        temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
        changed_coms=rotated_commands_from(temp_coms,0,paramets[1])
        temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" #+"|"  wasadded here 18.11.
        temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
        temporary_file_string=MemoryHandler.glue_the_split(temp_coms,"|")+"|" #+"|"  wasadded here 18.11.
        draw_temporary_file()
        update_layer_labels()
        layer_items.redraw(t)
        return

    if is_it_in_scale_area(int(event.x),int(event.y)) and special_area_mode2=="color": #added 19.8.
        global palf,distance
        palf.loc=[shift_click_pos[0]+distance+5,shift_click_pos[1]] #+200 is a test
        xpos=event.x-palf.loc[0]
        ypos=event.y -palf.loc[1]
        if xpos<0 and (palf.color_show[3]-palf.color_show[2])>0.4:
            palf.blueness=(palf.color_show[0]*ypos+palf.color_show[1]*(palf.size[1]-ypos))/palf.size[1]

        if 0<xpos<palf.size[0] and (palf.color_show[3]-palf.color_show[2])>0.4:#0.4 is somewhat random, but don't change
            palf.zoomin(xpos,ypos)
        elif 0<xpos<palf.size[0] and (palf.color_show[3]-palf.color_show[2])<0.4:#0.4 is somewhat random, but don't change
            new_color=palf.zoomout(xpos,ypos)
            temp_turtle.fillcolor((new_color[0],new_color[1],new_color[2]))
            temporary_file_string += "fc(["+str(new_color[0])[0:5]+","+str(new_color[1])[0:5]+","+str(new_color[2])[0:5]+"])|"

        update_layer_labels()
        palf.paint_palette(layer_data_canvas)
        basic_info()


    if is_it_in_mode_area1(int(event.x),int(event.y)):#changing from one type of image transformin to another
        if special_area_mode1=="local":
            special_area_mode1="global"
        elif special_area_mode1=="global":
            special_area_mode1="color"
        elif special_area_mode1=="color":
            special_area_mode1="local"
        update_layer_labels()

    if is_it_in_mode_area2(int(event.x),int(event.y)):#changing from one type of image transformin to another
        if special_area_mode2=="local":
            special_area_mode2="global"
        elif special_area_mode2=="global":
            special_area_mode2="color"
        elif special_area_mode2=="color":
            special_area_mode2="local"
        update_layer_labels()

    global label_starting_index#kertoo monennesta indeksistä alkaen layerit esitetään labeleinä
    global maximum_label_number
    global showmode # what info is shown about the layers
    global db
    layer_number=int(event.y/layer_data_constant)+label_starting_index-1
    if showmode in ["normal","color"]:
        if layer_number>len(layer_items.items) or layer_number<label_starting_index-1:#maximum number of layer-labels is currently 10, remember to change thi
            return #ei pysty muuttamaan layeria jota ei ole

    #if layer_number in [len(layer_items.items),label_starting_index+maximum_label_number] and event.x<root_width/2:# move layerlabels down by 4 
    #    label_starting_index +=4
    #    if label_starting_index>len(layer_items.items):
    #        label_starting_index=max(0,len(layer_items.items)-1)
    #    update_layer_labels() 
    
    if int(event.y/layer_data_constant)==0 and event.x>3*root_width/4:# change the info type
        if showmode=="normal":
            showmode="color"
            if label_starting_index>len(layer_items.items):
                label_starting_index=max(0,len(layer_items.items)-1)
        elif showmode=="color":
            showmode="variables"
            if label_starting_index>len(db.variables_as_list()):
                label_starting_index=0#max(0,len(db.variables_as_list())-1)
        elif showmode=="variables":
            showmode="functions"
            if label_starting_index>len(db.function_list):
                label_starting_index=0#max(0,len(db.function_list)-1)
        elif showmode=="functions":
            showmode="normal"
            if label_starting_index>len(layer_items.items):
                label_starting_index=max(0,len(layer_items.items)-1)
        update_layer_labels() 

    if int(event.y/layer_data_constant)==0 and  0<event.x<root_width/8:# if the upper area in layerdatacanvas is pressed, move to beginning 
        label_starting_index=0

    if int(event.y/layer_data_constant)==0 and  root_width/8<event.x  and event.x<2*root_width/8:# if the upper area in layerdatacanvas is pressed, move 9 labels up 
        label_starting_index -=9

    if int(event.y/layer_data_constant)==0 and  2*root_width/8<event.x and event.x<3*root_width/8:# if the upper area in layerdatacanvas is pressed, move 1 label up 
        label_starting_index -=1

    if int(event.y/layer_data_constant)==0 and  3*root_width/8<event.x and event.x<4*root_width/8:# if the upper area in layerdatacanvas is pressed, move 1 labels down 
        label_starting_index +=1

    if int(event.y/layer_data_constant)==0 and  4*root_width/8<event.x and event.x<5*root_width/8:# if the upper area in layerdatacanvas is pressed, move 9 labels down 
        label_starting_index +=9


    if int(event.y/layer_data_constant)==0 and  5*root_width/8<event.x and event.x<6*root_width/8:# if the upper area in layerdatacanvas is pressed, move 4 labels up 
        if showmode in ["normal","color"]:
            label_starting_index=len(layer_items.items)-maximum_label_number
        if showmode=="variables":
            label_starting_index=len(db.variables_as_list())-maximum_label_number
        if showmode=="functions":
            label_starting_index=len(db.function_list)-maximum_label_number
    if label_starting_index<0:
            label_starting_index=0

    if label_starting_index>=len(layer_items.items) and showmode in ["normal","color"]:
        label_starting_index=len(layer_items.items)-1

    if label_starting_index>=len(db.variables_as_list()) and showmode==["variables"]:
        label_starting_index=max(0,len(db.variables_as_list())-1)

    if label_starting_index>=len(db.function_list) and showmode==["functions"]:
        label_starting_index=max(0,len(db.function_list)-1)

    if label_starting_index<0:#moved this here 18.7.
        label_starting_index=0

    update_layer_labels() 
    if int(event.y/layer_data_constant)==0:#layer visibility may change unintentionally if it is not forbidden when this area is clicked
        return
    
    showing_layers=1
    if showmode in ["normal","color"]:
        showing_layers=max(len(layer_items.items)-label_starting_index,1)
    if showmode in ["variables"]:
        showing_layers=max(len(db.variables_as_list())-label_starting_index,1)
    if showmode in ["functions"]:
        showing_layers=max(len(db.function_list)-label_starting_index,1)


    if showing_layers>maximum_label_number:
        showing_layers=maximum_label_number#how many layer_labels are currently showing
    if layer_number in range(label_starting_index,label_starting_index+showing_layers) and showmode in ["normal","color"]:
        show_contours(layer_number)
        if layer_items.items[layer_number][7]=="active":
            layer_items.items[layer_number][7]="visible"
        elif layer_items.items[layer_number][7]=="invisible":
            layer_items.items[layer_number][7]="active"
        elif layer_items.items[layer_number][7]=="visible":
            layer_items.items[layer_number][7]="invisible"
        layer_items.redraw(t) #only draw if visibility was changed 5.7. klo 7.38 vaihdettiin redraw yhden layerin piirtoon
    
    if layer_number in range(label_starting_index,label_starting_index+showing_layers) and showmode in ["variables"]:
        is_it_left_side=(event.x-(root_width/2)<=0)
        if is_it_left_side: #inserts name of the variable
            command_line_entry.insert(INSERT,db.variables_as_list()[layer_number][0])
        if is_it_left_side==False: #inserts value of the variable
            command_line_entry.insert(INSERT,db.variables_as_list()[layer_number][1])

    if layer_number in range(label_starting_index,label_starting_index+showing_layers) and showmode in ["functions"]:
        is_it_left_side=(event.x-(root_width/2)<=0)
        if is_it_left_side: #inserts name of the variable
            command_line_entry.insert(INSERT,db.function_list[layer_number].output_model_str.split("==")[0])
        if is_it_left_side==False: #inserts value of the variable
            command_line_entry.insert(INSERT,db.function_list[layer_number].output_model_str.split("==")[1])

    update_layer_labels() 
   



#this should take the right clicked layer item and move a copy of it to be handled in draw mode
def do_something2(event):
    global mode
    global showmode
    global label_starting_index
    layer_number=max(int(event.y/layer_data_constant)+label_starting_index-1,0) 

    if mode=="edit_mode" and showmode in ["normal","color"]:#edit mode
        mode="drawing_mode"#draw mode
        global temporary_file_string
        temporary_file_string = layer_items.load_file_as_string(layer_items.items[layer_number][2],"drawings") # this should load the file
        draw_temporary_file()
        global command_list_name
        command_list_name="draw"
        command_line_entry.delete('1.0',END)
        draw_command_list() #correct list need to be chosen
        for item in layer_items.items:
            if item[7]=="active":
                item[7]="visible" #every other layer should turn to some nonactive state
        update_layer_labels() 
        #layer_items.redraw(t) ehkä tämän voi jättää tekemättä
        command_entry_canvas.config(bg="wheat1")#added 7.10

    if showmode=="functions":
        function_str=db.function_list[layer_number].output_model_str
        function_name=FunctionOperator.list_of_particles(function_str)[0]
        if messagebox.askyesno("remove function?","Remove a function: "+function_str):
            message=db.remove_function_by_name(function_name) #removes if can
            if message != None:
                messagebox.showinfo("Can't remove function",message) #displays a reason why it can't



def show_contours(layer_number):#shows contours of the layer with number layer_number
    corners=layer_items.real_contours(layer_number)
    global screen
    screen.tracer(0)
    layer_data_turtle.hideturtle()#we do not want to create a new turtle
    layer_data_turtle.color("black")
    layer_data_turtle.pensize(2)
    layer_data_turtle.penup()
    layer_data_turtle.goto(corners[0])
    layer_data_turtle.pendown()
    layer_data_turtle.goto(corners[1])
    layer_data_turtle.goto(corners[2])
    layer_data_turtle.goto(corners[3])
    layer_data_turtle.goto(corners[0])
    layer_data_turtle.penup()
    layer_data_turtle.goto(layer_items.items[layer_number][5],layer_items.items[layer_number][6])#goes to origo (I guess)
    layer_data_turtle.pendown()
    layer_data_turtle.color("red")
    layer_data_turtle.dot(15)
    layer_data_turtle.penup()
    turtle.ontimer(hide_contours,3000)    



#this is meant to show contours of Geometry.Drawing object: Just the lines, not insides of polygons
def show_contours_of_Drawing(drawi:Geometry.Drawing):
    global temporary_file_string
    new_drawi=drawi.contour_line_Drawing()
    file_str=new_drawi.from_Drawing_to_temp_string()
    temporary_file_string += file_str #this is just temporary solution, wwe don't actually 
    draw_temporary_file() #want to add this to temporary file
    #"remember to make show_contours_of_Drawing to work with more sophistication on saving file_str"

#taking a vertice_list, draws contours inside polygon it is forming
def show_contours_inside_polygon(vertice_list):
    if len(vertice_list)>2:
        drawi=Geometry.Drawing(temporary_file_string)
        inside_elements=drawi.elements_inside_vertices(vertice_list)
        drawi2=Geometry.Drawing("")
        for element in inside_elements:
            drawi2.elements.append(element)
        show_contours_of_Drawing(drawi2)

#given vertice_list, saves a file consisting of elements drawed inside this txt in file called paste.txt
def copy_by_vertices(vertice_list):
    global temporary_file_string
    drawi=Geometry.Drawing(temporary_file_string)    
    drawi.bend_intersections_with_vertice_list(vertice_list)
    shrinked_vertice_list=Geometry.shrinked_vertice_list(vertice_list,2)#we make polygon little smaller, to not include unwanted elements
    inside_elements=drawi.elements_inside_vertices(shrinked_vertice_list)
    drawi2=Geometry.Drawing("")
    for element in inside_elements:
        drawi2.elements.append(element)
    file_str=drawi2.from_Drawing_to_temp_string()
    save_string_to_file(file_str,"paste","machinery")
    save_string_to_file(file_str,"paste","drawings")# we can have this in both subdirs

#given vertice_list, saves a file consisting of elements drawed inside this txt in file called paste.txt and cuts this area of
def cut_by_vertices(vertice_list): 
    global temporary_file_string
    drawi=Geometry.Drawing(temporary_file_string)    
    drawi.bend_intersections_with_vertice_list(vertice_list)
    shrinked_vertice_list=Geometry.shrinked_vertice_list(vertice_list,2)#we make polygon little smaller, to not include unwanted elements
    inside_elements=drawi.elements_inside_vertices(shrinked_vertice_list)
    for element in inside_elements:
        drawi.elements.remove(element)
    temporary_file_string=drawi.from_Drawing_to_temp_string()
    drawi2=Geometry.Drawing("")
    drawi2.elements=inside_elements
    file_str=drawi2.from_Drawing_to_temp_string()
    save_string_to_file(file_str,"paste","machinery")
    save_string_to_file(file_str,"paste","drawings")# we can have this in both subdirs
    temporary_file_string=file_str
    draw_temporary_file()
    #"there are problems left, wrong things seems to leave")
    #"note that copy_by_verticesmight also need changes")


#given file saved in paste.txt adds this drawing in the point given
def paste(point):
    global temporary_file_string
    instructions=""
    with open("machinery/paste.txt","r") as file:
        instructions=file.read()
    drawi=Geometry.Drawing(instructions)
    drawi.shift(point[0],point[1])
    temporary_file_string += instructions
    draw_temporary_file()
    #"there is probably bugs, for example is pen left up or down?")
    #"point is not included yet ")



def hide_contours():#hides contours of the layer over which label mouse is howering in the layer_data_canvas
    layer_data_turtle.reset()


cut_points=[]
#with this method applied many times, layerdataturtle draws a shape of polygon, which is
# "saved" in point_list 
def pick_points_with_ld_turtle(new_point):

    if len(cut_points)==0:
        layer_data_turtle.reset()
        layer_data_turtle.penup()
        layer_data_turtle.goto(new_point[0],new_point[1])
        layer_data_turtle.pensize(2)
        layer_data_turtle.color((1,0,0))
        layer_data_turtle.pendown()
        cut_points.append(new_point)
    if len(cut_points)>0:
        layer_data_turtle.goto(new_point[0],new_point[1])
        layer_data_turtle.pensize(2)
        layer_data_turtle.color((1,0,0))
        cond1=Geometry.pdistance(cut_points[0],new_point)<10
        cond2=Geometry.pdistance(cut_points[-1],new_point)<10
        if cond1 or cond2:
            screen.tracer(1)
            screen.tracer(0)
            return cut_points
        else:
            cut_points.append(new_point)
    screen.tracer(1)
    screen.tracer(0)
    return cut_points


    

#this is meant to shift all the active layers
def shift_active(event):
    layer_items.shift_active(event.x,event.y)
    update_layer_labels()


#activates from save button or ctrl-s
def save_file(event=None):#s
    global current_file_name
    name = filedialog.asksaveasfilename(initialdir="./files",defaultextension=".txt")#10:54 20.7
    truth=True
    if path.exists(name):
        truth=messagebox.askyesno("File already exists","Overwrite?")
    if truth==False:#if user doesn't want to overwrite, then go away from the method
        return
    layer_items.save_layers(name)#file will be saved in this method at files\name.txt
    current_file_name=name #saves the name, so if we continue modifying, it remembers the current name
    messagebox.showinfo("information","File was saved as "+name+".")
    #open_popup("save_layers") #uutta muokkausta 20.7. poistettiin
    #layer_items.save_layers()#they are now saved in subdirectory called 'files'


#ctrl-p or save png button activates this, it then leads to png_popup
def make_png(event=None):
    messagebox.showinfo("Bounds","Pick drawing area")
    command_line_entry.delete('1.0',END)
    command_line_entry.insert(INSERT,"make_png(PT,PT)")



#for saving png
def png_popup(xcor_1,ycor_1,xcor_2,ycor_2):
    global layer_items, temporary_file_string
    global mode
    global turtle_screen_bg_color
    popup = tk.Toplevel(root)
    name_label=tk.Label(popup,text="File name:")
    name_label.pack()
    name_entry=tk.Entry(popup)
    name_entry.pack()

    def ready2(): #when we are making png with method in png_maker
        global temporary_file_string
        top_left=(min(xcor_1,xcor_2),max(ycor_1,ycor_2))
        bottom_right=(max(xcor_1,xcor_2),min(ycor_1,ycor_2))
        width=bottom_right[0]-top_left[0]
        height=-bottom_right[1]+top_left[1]
        save_name=name_entry.get()
        if mode=="drawing_mode":#if we are in drawing mode, we want to add the currently drawn pic to png
            random_save()
        merge_active_layers(save_name)
        if mode=="drawing_mode":
            layer_items.items.pop(-2) #get rid of random file created
        update_layer_labels()

        spin_turtle.pencolor(turtle_screen_bg_color) #we don't care about the turtle, we just use it to change color_format
        bg_color=spin_turtle.pencolor()  
        file_str= layer_items.load_file_as_string(save_name,"drawings") # used to  be just load_file_as_string(save_name,"drawings")
        PngMaker.draw_drawing(file_str,width,height,top_left,bg_color,"pngs\\"+save_name,"basic")
        temporary_file_string=""
        popup.destroy()

    def ready3(): #actually only difference is that we are making just the contour
        global temporary_file_string
        top_left=(min(xcor_1,xcor_2),max(ycor_1,ycor_2))
        bottom_right=(max(xcor_1,xcor_2),min(ycor_1,ycor_2))
        width=bottom_right[0]-top_left[0]
        height=-bottom_right[1]+top_left[1]
        save_name=name_entry.get()
        if mode=="drawing_mode":#if we are in drawing mode, we want to add the currently drawn pic to png
            random_save()
        merge_active_layers(save_name)
        if mode=="drawing_mode":
            layer_items.items.pop(-2) #get rid of random file created
        update_layer_labels()

        spin_turtle.pencolor(turtle_screen_bg_color) #we don't care about the turtle, we just use it to change color_format
        bg_color=spin_turtle.pencolor()  
        file_str= layer_items.load_file_as_string(save_name,"drawings") # used to  be just load_file_as_string(save_name,"drawings")
        PngMaker.draw_drawing(file_str,width,height,top_left,bg_color,"pngs\\"+save_name,"contour")
        temporary_file_string=""
        popup.destroy()



    abs_ready_button2=tk.Button(popup,text="Normal png",command=ready2)
    abs_ready_button2.pack()

    abs_ready_button3=tk.Button(popup,text="Contours only",command=ready3)
    abs_ready_button3.pack()


#loads layers file, ctrl+l
def load_file(event=None):
    truth=True
    truth = messagebox.askyesno("Load a file","All unsaved work is deleted, continue?")
    if truth==False:
        return
    global current_file_name
    current_file_name=layer_items.load_layers() #here one must realise that this line doesn't just return value for c_f_n but also
    #does the loading
    helping_turtle.reset()
    temp_turtle.reset()
    temp_turtle.shapesize(1.8,1.8,2)
    update_layer_labels()



#create frames
draw_or_edit_frame=tk.Frame(root,bg=turtle_screen_bg_color) #used to be blue
layer_commands_frame=tk.Frame(root,bg="orange")
layer_data_frame=tk.Frame(root,bg="lightgreen")




#Create canvases
#for picking commands
command_entry_canvas = tk.Canvas(draw_or_edit_frame,height=200,width=root_width,bg="lightgreen")
#for showing layerdata and quick shifts
layer_data_height=350
layer_data_canvas = tk.Canvas(layer_data_frame,height=layer_data_height,width=root_width,bg=turtle_screen_bg_color)#used to be blue

#Create entrys
command_line_entry = tk.Text(layer_commands_frame,height=1,width=50,font=("times new roman",11,"normal"))
command_line_entry.grid(row=0, column=0)
button_canvas=tk.Canvas(layer_commands_frame,height=54,width=root_width,bg="lightgreen")
button_canvas.grid(row=1,column=0)







#add frames
draw_or_edit_frame.grid(row=0,column=0)
layer_commands_frame.grid(row=8,column=0)
layer_data_frame.grid(row=15,column=0)

#create labels


#add canvas
layer_data_canvas.grid(row=0,column=0)
layer_data_canvas.bind("<Button-1>",do_something)
layer_data_canvas.bind("<B1-Motion>",do_something)
layer_data_canvas.bind("<Button-3>",do_something2)

command_entry_canvas.grid(row=1,column=0)
command_entry_canvas.bind("<Button-1>",change_command_menu)#pressing command_entry_canvas should
#put order to command_entry and perhaps change the list of possible commands
command_entry_canvas.bind("<Button-3>",display_info)



shift_click_pos=[40,225] #where is the area of canvas to shift active items
shift_click_size=100#how big is the area
distance=170# distance from the upper left corners from shift to rotate areas
#this opens a popup window to write a text NOTE generated by chatGPT



#for displaying mini-images of drawn objects

def mini_popup():
    global command_line_entry
    def on_canvas_click(event):
        # Get the coordinates of the click
        x, y = event.x, event.y
        can = event.widget#testing
        x_can = can.canvasx(event.x)# these
        y_can = can.canvasy(event.y)#are for
        # Update the global variable yodacoor
        global yodacoor
        yodacoor = (x_can, y_can)
        # Update the label in the main window with the coordinates
        sector=int(yodacoor[0]/90)+5*int(yodacoor[1]/90)
        command_line_entry.insert(END,"put("+str(popular_drawings.popularity_list[sector][:-4])+")|")


    # Create a new window for the popup
    popup = tk.Toplevel(root)
    popup.title("Popup Window")

    # Create a frame in the popup window
    frame = Frame(popup)
    frame.pack(expand=True, fill="both")

    # Create a canvas in the frame
    canvas = Canvas(frame, width=500, height=200, scrollregion=(0, 0, 500, 500))
    canvas.pack(side="left", expand=True, fill="both")

    # Create a scrollbar for the canvas
    scrollbar = Scrollbar(frame, command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Load all PNG images from the "drawings" directory
    images_directory = "drawings"
    potential_image_files = [f for f in list_files(images_directory) if f.endswith(".png")]
    image_files=[]
    for item in popular_drawings.popularity_list:
        if item[:-4]+".png" in potential_image_files:
            image_files.append(item[:-4]+".png")
    # Calculate positions and sizes for each PNG
    image_size = 90
    columns = 5
    padding = 10

    # List to store all PhotoImage objects
    image_list = []

    for i, image_file in enumerate(image_files):
        row = i // columns
        col = i % columns
        x_start = col * (image_size + padding)
        y_start = row * (image_size + padding)

        image_path = os.path.join(images_directory, image_file)
        img = Image.open(image_path).convert("RGBA")
        
        # Resize the image using LANCZOS resampling filter
        img.thumbnail((image_size, image_size), Image.LANCZOS)

        # Create PhotoImage object and store it in the list
        photo_img = ImageTk.PhotoImage(img,master=root)
        image_list.append(photo_img)

        # Paste the thumbnail onto the canvas
        canvas.create_image(x_start + image_size // 2, y_start + image_size // 2, anchor=tk.CENTER, image=photo_img)


    # Bind the canvas click event to on_canvas_click function
    canvas.bind("<Button-1>", on_canvas_click)

    # Store the image list in the canvas (to prevent it from being garbage collected)
    canvas.image_list = image_list





#for selecting active_layers by creating criteria for activation
def active_popup():
    activetruth=messagebox.askyesno("Change status", "Do you want to inactivate currently active layers?")
    global layer_items
    if activetruth:
        for i in range(0,len(layer_items.items)):
            if layer_items.items[i][7]=="active":
                layer_items.items[i][7]="visible"
        update_layer_labels()
        layer_items.redraw(t)
    active_pop = tk.Toplevel(root) 
    scrollbar = Scrollbar(active_pop,width=4)
    mylist = Listbox(active_pop, yscrollcommand = scrollbar.set )
    layer_number_label=tk.Label(active_pop,text="Activate layers with parameter between numbers")
    layer_number_label.grid(row=0,column=0)
    from_number_label=tk.Label(active_pop,text="From:")
    from_number_label.grid(row=0,column=3)
    to_number_label=tk.Label(active_pop,text="To:")
    to_number_label.grid(row=0,column=4)

    min_value=tk.Entry(active_pop)
    max_value=tk.Entry(active_pop)


    def destroy():
        update_layer_labels()
        layer_items.redraw(t)
        active_pop.destroy()

    def tivate_by_number(acde_variable): #here acde_variable keeps recor if we are activating or deactivating layers
        parametern=""
        errorval=0 #this is to put some stuff on except block
        min_val=min_value.get()
        max_val=max_value.get()
        try:
            parametern=mylist.selection_get()
        except TclError:
            errorval=1 #this is because I am not sure if except-block can be left empty
        if min_value.get()=="":
            min_val=-1000000
        
        if max_value.get()=="":
            max_val=1000000

        for i in range(0,len(layer_items.items)):
            activating_truth=False
            if parametern=="depth" and layer_items.items[i][0] in range(int(min_val),int(max_val)):
                if name_entry.get() in ["",layer_items.items[i][2]]:
                    activating_truth=True
            if parametern=="layer number" and i in range(int(min_val)-1,int(max_val)):
                if name_entry.get() in ["",layer_items.items[i][2]]:
                    activating_truth=True
            if parametern=="x-scale" and layer_items.items[i][3][0]>float(min_val) and float(max_val)>layer_items.items[i][3][0]:
                if name_entry.get() in ["",layer_items.items[i][2]]:
                    activating_truth=True
            if parametern=="y-scale" and layer_items.items[i][3][1]>float(min_val) and float(max_val)>layer_items.items[i][3][1]:
                if name_entry.get() in ["",layer_items.items[i][2]]:
                    activating_truth=True
            if parametern=="rotation" and layer_items.items[i][4]  in range(int(min_val),int(max_val)+1):
                if name_entry.get() in ["",layer_items.items[i][2]]:
                    activating_truth=True
            if parametern=="x-shift" and layer_items.items[i][5]  in range(int(min_val),int(max_val)+1):
                if name_entry.get() in ["",layer_items.items[i][2]]:
                    activating_truth=True
            if parametern=="y-shift" and layer_items.items[i][6]  in range(int(min_val),int(max_val)+1):
                if name_entry.get() in ["",layer_items.items[i][2]]:
                    activating_truth=True
            if parametern=="red-shift" and layer_items.items[i][8]>float(min_val) and float(max_val)>layer_items.items[i][8]:
                if name_entry.get() in ["",layer_items.items[i][2]]:
                    activating_truth=True
            if parametern=="green-shift" and layer_items.items[i][9]>float(min_val) and float(max_val)>layer_items.items[i][9]:
                if name_entry.get() in ["",layer_items.items[i][2]]:
                    activating_truth=True
            if parametern=="blue-shift" and layer_items.items[i][10]>float(min_val) and float(max_val)>layer_items.items[i][10]:
                if name_entry.get() in ["",layer_items.items[i][2]]:
                    activating_truth=True

            if activating_truth:
                if acde_variable==1:
                    layer_items.items[i][7]="active"
                if acde_variable==0 and layer_items.items[i][7]=="active":
                    layer_items.items[i][7]="visible"
        end_button=tk.Button(active_pop,text="Done",command=destroy)
        end_button.grid(row=2,column=0)
        update_layer_labels()

    def activate_by_number():
        tivate_by_number(1)
    
    def deactivate_by_number():
        tivate_by_number(0)

    parameter_type_label=tk.Label(active_pop,text="Parameter type:")
    parameter_type_label.grid(row=1,column=0)
    layer_number_button=tk.Button(active_pop,text="Activate",command=activate_by_number)
    layer_number_button2=tk.Button(active_pop,text="Deactivate",command=deactivate_by_number)
    scrollbar.grid(row=1,column=1)
    layer_number_button.grid(row=3,column=3)
    layer_number_button2.grid(row=3,column=4)
    name_label=tk.Label(active_pop,text="Name: (Optional)")
    name_entry=tk.Entry(active_pop)
    name_label.grid(row=2,column=3)
    name_entry.grid(row=2,column=4)
    mylist.insert(END, "depth")
    mylist.insert(END, "layer number")
    mylist.insert(END, "x-scale") 
    mylist.insert(END, "y-scale")
    mylist.insert(END, "rotation")  
    mylist.insert(END, "x-shift")
    mylist.insert(END, "y-shift") 
    mylist.insert(END, "red-shift")
    mylist.insert(END, "green-shift")
    mylist.insert(END, "blue-shift")
    
    #add more options later
    mylist.grid(column=2,row=1,rowspan=4)
    scrollbar.config( command = mylist.yview )
    min_value.grid(column=3,row=1)
    max_value.grid(column=4,row=1)



#for selecting active_layers by creating criteria for activation
def layerorder_popup():
    activetruth=messagebox.askyesno("Change layer order", "Do you want to activate all layers?")
    global layer_items
    if activetruth:
        for i in range(0,len(layer_items.items)):
            layer_items.items[i][7]="active"
        update_layer_labels()
        layer_items.redraw(t)
    order_pop = tk.Toplevel(root) 
    scrollbar = Scrollbar(order_pop,width=4)
    mylist = Listbox(order_pop, yscrollcommand = scrollbar.set )

    def destroy():
        order_pop.destroy()

    def tivate_by_number(acde_variable): #here acde_variable keeps recor if we are activating or deactivating layers
        parametern=""
        errorval=0 #this is to put some stuff on except block
        try:
            parametern=mylist.selection_get()
        except TclError:
            errorval=1 #this is because I am not sure if except-block can be left empty
        #this begins the ordering
        lista=layer_items.items
        size=len(lista)
        p_values=[]
        k=3 #this will be the index of the relevant parameter

        if parametern=="depth":
            k=0
        if parametern=="rotation":
            k=4
        if parametern=="x-shift": 
            k=5
        if parametern=="y-shift":
            k=6
        if parametern=="activity":
            k=7
        if parametern=="red-shift": 
            k=8
        if parametern=="green-shift":
            k=9
        if parametern=="blue-shift": 
            k=10


        for i in range(0,size):
            if k !=3 and k!=7:
                p_values.append(acde_variable*float(lista[i][k]))
        for i in range(0,size):
            if  parametern=="x-scale":
                p_values.append(acde_variable*float(lista[i][3][0]))
            if  parametern=="y-scale":
                p_values.append(acde_variable*float(lista[i][3][1]))
            if  parametern=="activity":
                if lista[i][7]=="active":
                    p_values.append(acde_variable*2)
                elif lista[i][7]=="visible":
                    p_values.append(acde_variable)
                elif lista[i][7]=="invisible":
                    p_values.append(0)
                


        for i in range(0,size):
            if lista[i][7]!="active" and k!=7:
                p_values[i]=acde_variable*10000000 #large value for inactive layers make them to be on the bottom after ordering

        layer_items.reorder_items(p_values)
        update_layer_labels()
        layer_items.redraw(t)

    def ascend_by_number():
        tivate_by_number(1)
    
    def descend_by_number():
        tivate_by_number(-1)

    parameter_type_label=tk.Label(order_pop,text="Parameter type:")
    parameter_type_label.grid(row=1,column=0)
    layer_number_button=tk.Button(order_pop,text="Ascending order",command=ascend_by_number) #ascending means that larger 
    layer_number_button2=tk.Button(order_pop,text="Descending order",command=descend_by_number)#value sents on the smallest layer_number
    scrollbar.grid(row=1,column=1)
    layer_number_button.grid(row=1,column=3)
    layer_number_button2.grid(row=2,column=3)
    end_button=tk.Button(order_pop,text="Done",command=destroy)
    end_button.grid(row=3,column=3)

    mylist.insert(END, "depth")
    mylist.insert(END, "x-scale") 
    mylist.insert(END, "y-scale")
    mylist.insert(END, "rotation")  
    mylist.insert(END, "x-shift")
    mylist.insert(END, "y-shift") 
    mylist.insert(END, "activity")
    mylist.insert(END, "red-shift")
    mylist.insert(END, "green-shift")
    mylist.insert(END, "blue-shift")
    
    #add more options later
    mylist.grid(column=2,row=1,rowspan=4)
    scrollbar.config( command = mylist.yview )









#starts creating a model for file
def model_popup():
    global layer_items
    model_pop = tk.Toplevel(root) 
    multi_button=tk.Button(model_pop,text="Ready")
    multa_button=tk.Button(model_pop,text="Continue")#this helps the placement issues. If multi button is not destroyed it ends in a stupid place
    more_button=tk.Button(model_pop,text="Add more")
    headline=tk.Label(model_pop, text="Choose the drawing(s) used in the file")
    model_field=tk.Text(model_pop, height=1, width=60)
    layer_scale=tk.Scale(model_pop,from_=1,to=100,orient=HORIZONTAL)
    the_drawing="basic" #if nothing is chosen this, whatever it is, is drawn
    filename = filedialog.askopenfilename(initialdir="drawings/")
    model_field.insert("1.0",filename_without_subdir(filename,"drawings"))
    def after_question():
        global the_drawing
        list_of_drawings=MemoryHandler.split_the_string(the_drawing,",")
        for drawing in list_of_drawings: #checking if there are the drawings that user inputted
            if path.exists("drawings/"+drawing+".txt")==False:
                filetruth=messagebox.askyesno("No drawing","There is no drawing "+"drawings/"+the_drawing+".txt. Try again?")
                if filetruth:
                    model_pop.destroy()
                    model_popup()
                else:
                    messagebox.showinfo("Start drawing","Make a drawing in DRAW-mode and save it by using 'Save drawing'-button. Then create a new file.")
                    draw_mode()
                    model_pop.destroy()
        lodlength=len(list_of_drawings)
        randomness=False
        if lodlength>1:
            randomness=messagebox.askyesno("random or not","Do you want to pick drawings randomly?")
        upperlimit=int(layer_scale.get())
        for i in range(0,upperlimit):
            if randomness:
                drawing=list_of_drawings[random.randint(0,lodlength-1)]
            else:
                drawing=list_of_drawings[i%lodlength]
            instructions=""
            with open("drawings/"+drawing+".txt","r")as file:
                instructions=file.read()
            layer_items.add_item(0,"objects",drawing,[1,1],0,0,0,"active",0,0,0,"",instructions)
        #headline.config(text="Other modifiers")
        layer_scale.destroy()
        multa_button.destroy()#just testing
        model_pop.destroy()#just testing
        color_truth=False
        scale_truth=False
        depth_truth=True
        orientation_truth=False
        grid_truth=False



        grid_truth=messagebox.askyesno("Grid","Set objects in grid?")
        if grid_truth:
            D3_truth=messagebox.askyesno("3D Grid?","A 3D grid perhaps?")    
            if D3_truth:
                D3_popup()
                depth_truth=False
            else:
                grid_popup()
        color_truth=messagebox.askyesno("Colors","Change coloring?")
        if color_truth:
            color_popup()
        scale_truth=messagebox.askyesno("Scale","Change scaling?")
        if scale_truth:
            scale_popup()
        if depth_truth:#if we are in 3D, this doesn't happen
            depth_truth=messagebox.askyesno("Depth","Change depth?")
        if depth_truth:
            depth_popup()
        orientation_truth=messagebox.askyesno("Orientation","Change orientation?")
        if orientation_truth:
            orientation_popup()

        layer_items.redraw(t)
        update_layer_labels()


    def drawing_choice():
        global the_drawing
        multi_button.destroy()#testi
        the_drawing=model_field.get("1.0", "end-1c")
        more_button.destroy()
        model_field.destroy()
        headline.config(text="Choose the number of layers")
        headline.pack()
        layer_scale.pack()
        multa_button=tk.Button(model_pop,text="Continue",command=after_question)
        multa_button.pack()

    def add_more():
        filename = filedialog.askopenfilename(initialdir="drawings/")
        model_field.insert("1.0",filename_without_subdir(filename,"drawings")+",")#poistettiin filename_end 20.7.

    headline.pack()
    model_field.pack() 
    multi_button.config(command=drawing_choice)
    multi_button.pack()
    more_button.config(command=add_more)
    more_button.pack()

            


#puts things in a grid layout and allows user to estimate random variation for position
def grid_popup():#using this layers are arranged in grid formation
    global layer_items
    popup = tk.Toplevel(root)
    number_of_active_layers=0
    for item in layer_items.items:
        if item[7]=="active":
            number_of_active_layers +=1
    column_scale= tk.Scale(popup,orient=HORIZONTAL,from_=1,to=number_of_active_layers)
    column_scale.pack()
    x_random_scale= tk.Scale(popup,orient=HORIZONTAL, from_=0,to=500,resolution=2)
    y_random_scale= tk.Scale(popup, from_=0,to=500,resolution=2)
    x_distance_scale=tk.Scale(popup,orient=HORIZONTAL, from_=0,to=400)
    y_distance_scale=tk.Scale(popup, from_=0,to=400)

    def ready():
        for i in range(0,len(layer_items.items)):
            if layer_items.items[i][7]=="active":
                randomx=int((random.random()-0.5)*2*x_random_scale.get()) 
                randomy=int((random.random()-0.5)*2*y_random_scale.get()) 
                layer_items.items[i][5]=int(x_distance_scale.get()*(i%column_scale.get()))+randomx
                layer_items.items[i][6]=int(y_distance_scale.get()*int(i/column_scale.get()))+randomy
        layer_items.redraw(t)
        popup.destroy()


    ready_button=tk.Button(popup,text="Ready",command=ready)
    column_label = tk.Label(popup,text="Number of colums")
    column_label.pack()
    x_distance_label = tk.Label(popup,text="x-distance between layers")
    x_distance_label.pack()
    x_distance_scale.pack()
    x_random_label = tk.Label(popup,text="x-distance randomness")
    x_random_label.pack()
    x_random_scale.pack()
    y_distance_label = tk.Label(popup,text="y-distance between layers")
    y_distance_label.pack()
    y_distance_scale.pack()
    y_random_label = tk.Label(popup,text="y-distance randomness")
    y_random_label.pack()
    y_random_scale.pack()

    ready_button.pack()

#Actually this should be called 3D-popup, but this name is due to python conventions
def D3_popup():#layers are arranged as they where in 3d
    global layer_items
    popup = tk.Toplevel(root)
    number_of_active_layers=0
    for item in layer_items.items:
        if item[7]=="active":
            number_of_active_layers +=1
    active_layers_label=tk.Label(popup,text="Active layers: "+str(number_of_active_layers))
    column_scale= tk.Scale(popup,orient=HORIZONTAL,from_=1,to=number_of_active_layers)
    row_scale= tk.Scale(popup,orient=HORIZONTAL,from_=1,to=number_of_active_layers)
    x_random_scale= tk.Scale(popup,orient=HORIZONTAL, to=1000,resolution=2)
    y_random_scale= tk.Scale(popup,orient=HORIZONTAL, to=1000,resolution=2)
    x_distance_scale=tk.Scale(popup,orient=HORIZONTAL, from_=0,to=1000,resolution=2)
    y_distance_scale=tk.Scale(popup,orient=HORIZONTAL, from_=0,to=1000,resolution=2)
    z_distance_scale=tk.Scale(popup,orient=HORIZONTAL, from_=0,to=1000,resolution=2)
    z_random_scale=tk.Scale(popup,orient=HORIZONTAL, from_=0,to=1000,resolution=2)
    column_number=1#these represent the number of colums, rows etc.
    row_number=1
    depth_number=1
    distance_button=tk.Button(popup,text="Choose distances")
    position_button=tk.Button(popup,text="Position choices")
    x_random_label = tk.Label(popup,text="x-distance randomness")
    y_random_label = tk.Label(popup,text="y-distance randomness")
    z_random_label = tk.Label(popup,text="z-distance randomness")

    x_distance_label=tk.Label(popup,text="x-distance between layers")
    y_distance_label=tk.Label(popup,text="y-distance between layers")
    z_distance_label=tk.Label(popup,text="z-distance between layers")
    leftcorner_x=0
    leftcorner_y=0
    leftcorner_z=0
    ready_button=tk.Button(popup)

    def ready():
        global dist_x,dist_y,dist_z,rand_x,rand_y,rand_z,column_number,row_number, leftcorner_x,leftcorner_y,leftcorner_z
        dist_x=x_distance_scale.get()
        dist_y=y_distance_scale.get()
        dist_z=z_distance_scale.get()
        rand_x=x_random_scale.get()
        rand_y=y_random_scale.get()
        rand_z=z_random_scale.get()
        llc=[leftcorner_x,leftcorner_y,leftcorner_z-100] #left lower corner position
        i=0
        for index in range(0,len(layer_items.items)):# we have index and i separately, since we want to put only active stuff to the grid
            if layer_items.items[index][7]=="active":
                ranx=int((random.random()-0.5)*2*rand_x) 
                rany=int((random.random()-0.5)*2*rand_y) 
                ranz=int((random.random()-0.5)*2*rand_z) 
                d3pos=[0,0,0]
                d3pos[0]=i%column_number*dist_x+llc[0]+ranx
                d3pos[1]=(int(i/column_number)%row_number)*dist_y+llc[1]+rany
                d3pos[2]=-int(i/(column_number*row_number))*dist_z+llc[2]+ranz #3D position of the layers
                if d3pos[2]>99: #random decision that 100 is the point from where we are looking
                    d3pos[2]>-100000 #those behind our back are thrown to very far
                
                scalef=100/(100-d3pos[2])

                layer_items.items[index][0]=int(d3pos[2])
                layer_items.items[index][5]=int(d3pos[0]*scalef)
                layer_items.items[index][6]=int(d3pos[1]*scalef)
                layer_items.items[index][3]=[scalef,scalef]
                i = i+1
        layer_items.redraw(t)
        popup.destroy()

    def distance_choices():
        global depth_number
        global number_of_active_layer
        global maximum_rows
        global column_number
        global row_number
        global leftcorner_x,leftcorner_y,leftcorner_z
        distance_button.destroy()
        leftcorner_x=x_distance_scale.get()
        leftcorner_y=y_distance_scale.get()
        leftcorner_z=z_distance_scale.get()
        x_distance_label.config(text="x-distance")
        y_distance_label.config(text="y-distance")
        z_distance_label.config(text="z-distance")
        ready_button.config(text="Ready",command=ready)
        row_label.config(text="rows: "+str(row_number))
        x_random_label.grid(row=4,column=0)
        x_random_scale.grid(row=5,column=0)
        y_random_label.grid(row=4,column=1)
        y_random_scale.grid(row=5,column=1)
        depth_number=int(1+((number_of_active_layers-1)/(row_number*column_number)))
        depth_label.config(text="depths: "+str(depth_number))
        depth_label.grid(row=1,column=2)
        z_random_label.grid(row=4,column=2)
        z_random_scale.grid(row=5,column=2)
        ready_button.grid(row=6,column=2)

    #this chooses the left lower corner and its depth in the grid
    def position_choices():
        global dist_x,dist_y,dist_z,rand_x,rand_y,rand_z,row_number
        row_number=row_scale.get()
        position_button.destroy()
        row_scale.destroy()
        row_label.config(text="rows: "+str(row_number))
        x_distance_label.config(text="left x-coordinate")
        y_distance_label.config(text="lower y-coordinate")
        z_distance_label.config(text="'distance from the camera'")
        x_distance_label.grid(row=2,column=0)
        x_distance_scale.grid(row=3,column=0)
        y_distance_label.grid(row=2,column=1)
        y_distance_scale.grid(row=3,column=1)
        z_distance_label.grid(row=2,column=2)
        z_distance_scale.grid(row=3,column=2)
        x_distance_scale.config(from_=-1000,to=1000,resolution=10) #allthough the name hasn't changed, these are now used for different purpose 
        y_distance_scale.config(from_=-1000,to=1000,resolution=10)
        z_distance_scale.config(from_=5,to=1000,resolution=5)
        distance_button.config(command=distance_choices)
        distance_button.grid(row=4,column=2)



    def row_choice():
        global maximum_rows
        global column_number

        column_number=column_scale.get()
        column_label.config(text="columns: "+str(column_number))
        row_choice_button.destroy()
        maximum_rows=int(number_of_active_layers/column_scale.get())
        row_scale.config(from_=1,to=maximum_rows)
        column_scale.destroy()
        row_label.grid(row=1,column=1)
        row_scale.grid(row=2,column=1)
        position_button.config(command=position_choices)
        position_button.grid(row=3,column=1)

    row_label=tk.Label(popup,text="Number of rows:")
    row_choice_button=tk.Button(popup,text="Ready",command=row_choice)
    column_label = tk.Label(popup,text="Number of colums")
    active_layers_label.grid(row=0,column=0)
    column_label.grid(row=1,column=0)
    column_scale.grid(row=2,column=0)
    depth_label=tk.Label(popup,text="Depth:")
    row_choice_button.grid(row=3,column=0)








#for adjusting the orientation of all active layers
def orientation_popup():
    global layer_items
    popup = tk.Toplevel(root)
    constant_rotation_label = tk.Label(popup,text="Constant rotation")
    rotation_increment_label = tk.Label(popup,text="Increasing rotation")
    constant_rotation_label.pack()
    constant_rotation_scale= tk.Scale(popup,orient=HORIZONTAL,from_=0,to=360)
    constant_rotation_scale.pack()
    rotation_increment_label.pack()
    rotation_increment_scale= tk.Scale(popup,orient=HORIZONTAL,from_=0,to=360)
    rotation_increment_scale.pack()
    random_label = tk.Label(popup,text="Random rotation limit")
    random_label.pack()
    random_rotation_scale= tk.Scale(popup,orient=HORIZONTAL, from_=0,to=360)

    def ready(multiplier):
        for i in range(0,len(layer_items.items)):
            if layer_items.items[i][7]=="active":
                randomr=int((random.random()-0.5)*2*random_rotation_scale.get()) +constant_rotation_scale.get()
                layer_items.items[i][4]=int((i*rotation_increment_scale.get()))+randomr+multiplier*layer_items.items[i][4]
                # steady increase in rotation with added random component
        layer_items.redraw(t)
        update_layer_labels()


    def actually_ready():
        popup.destroy()
        return "done" #so that we know that there is nothing left to do
    def abs_ready():
        ready(0)#this is a trick to reduce indentation.  1 represents summing by previous value
    def rel_ready():
        ready(1)

    actually_ready_button=tk.Button(popup,text="Close",command=actually_ready)
    random_rotation_scale.pack()
    abs_ready_button=tk.Button(popup,text="Absolute change",command=abs_ready)
    rel_ready_button=tk.Button(popup,text="Relative change",command=rel_ready)
    abs_ready_button.pack()
    rel_ready_button.pack()
    abs_ready_button.pack()
    rel_ready_button.pack()
    actually_ready_button.pack()

#for adjusting the depth of all active layers
def depth_popup():
    global layer_items
    popup = tk.Toplevel(root)
    constant_depth_label = tk.Label(popup,text="Constant depth")
    depth_increment_label = tk.Label(popup,text="Depth increasement")
    constant_depth_label.pack()
    constant_depth_scale= tk.Scale(popup,orient=HORIZONTAL,from_=-100,to=100)
    constant_depth_scale.pack()
    constant_depth_label.pack()
    depth_increment_label.pack()
    depth_increment_scale= tk.Scale(popup,orient=HORIZONTAL,from_=-100,to=100)
    depth_increment_scale.pack()
    random_label = tk.Label(popup,text="Random depth variation")
    random_label.pack()
    random_depth_scale= tk.Scale(popup,orient=HORIZONTAL, from_=0,to=300)

    def ready(multiplier):
        for i in range(0,len(layer_items.items)):
            if layer_items.items[i][7]=="active":
                randomd=int((random.random()-0.5)*2*random_depth_scale.get())+constant_depth_scale.get()
                layer_items.items[i][0]=int((i*depth_increment_scale.get()))+randomd+multiplier*layer_items.items[i][0]
                # steady increase in rotation with added random component
        layer_items.redraw(t)
        update_layer_labels()
        return "done" #so that we know that there is nothing left to do

    def actually_ready():
        popup.destroy()        
    def abs_ready():
        ready(0)#this is a trick to reduce indentation.  1 represents summing by previous value
    def rel_ready():
        ready(1)

    abs_ready_button=tk.Button(popup,text="Absolute change",command=abs_ready)
    rel_ready_button=tk.Button(popup,text="Relative change",command=rel_ready)
    actually_ready_button=tk.Button(popup,text="Close",command=actually_ready)
    random_depth_scale.pack()


    abs_ready_button.pack()
    rel_ready_button.pack()
    actually_ready_button.pack()

#for adjusting the scaling of all active layers
def scale_popup():
    global layer_items
    popup = tk.Toplevel(root)
    max_scale_label = tk.Label(popup,text="Scaling of the first object in x-direction")
    max_scale_label.grid(row=0,column=0)
    max_scale_scale= tk.Scale(popup,orient=HORIZONTAL,from_=0.1,to=5,resolution=0.1)
    max_scale_scale.grid(row=1,column=0)
    max_scale_scale.set(1.0)
    min_scale_label = tk.Label(popup,text="Scaling of the last object in x-direction")
    min_scale_label.grid(row=2,column=0)
    min_scale_scale= tk.Scale(popup,orient=HORIZONTAL,from_=0.1,to=5,resolution=0.1)
    min_scale_scale.grid(row=3,column=0)
    min_scale_scale.set(1.0)
    x_random_label = tk.Label(popup,text="Random scaling variation in x-direction")
    x_random_label.grid(row=4,column=0)
    x_random_scale= tk.Scale(popup,orient=HORIZONTAL, from_=0,to=5,resolution=0.1)
    x_random_scale.grid(row=5,column=0)

    maxy_scale_label = tk.Label(popup,text="Scaling of the first object in y-direction")
    maxy_scale_label.grid(row=0,column=1)
    maxy_scale_scale= tk.Scale(popup,orient=HORIZONTAL,from_=0.1,to=5,resolution=0.1)
    maxy_scale_scale.grid(row=1,column=1)
    maxy_scale_scale.set(1.0)

    miny_scale_label = tk.Label(popup,text="Scaling of the last object in y-direction")
    miny_scale_label.grid(row=2,column=1)
    miny_scale_scale= tk.Scale(popup,orient=HORIZONTAL,from_=0.1,to=5,resolution=0.1)
    miny_scale_scale.grid(row=3,column=1)
    miny_scale_scale.set(1.0)
    y_random_label = tk.Label(popup,text="Random scaling variation in y-direction")
    y_random_label.grid(row=4,column=1)
    y_random_scale= tk.Scale(popup,orient=HORIZONTAL,from_=0,to=5,resolution=0.1)
    y_random_scale.grid(row=5,column=1)

    def ready(ap):#ap is 1 for relative change and 0 for absolute
        num_items=0
        for i in range(0,len(layer_items.items)):
            if layer_items.items[i][7]=="active":
                num_items +=1
        
        x_depth_max=100-100/max_scale_scale.get()
        x_depth_min=100-100/min_scale_scale.get()
        y_depth_max=100-100/maxy_scale_scale.get()
        y_depth_min=100-100/miny_scale_scale.get()
        counter=0
        if num_items==1:#this is a trick to avoid division by zero
            num_items=2
            counter=1

        for i in range(0,len(layer_items.items)):
            if layer_items.items[i][7]=="active":
                x_random=(random.random()-0.5)*2*x_random_scale.get() 
                this_x_depth=x_depth_max*counter/(num_items-1)+x_depth_min*(num_items-1-counter)/(num_items-1)
                layer_items.items[i][3][0]=((1-ap)+ap*layer_items.items[i][3][0])*100/(100-this_x_depth)+x_random
                # steady increase in scale_x with added random component
                y_random=(random.random()-0.5)*2*y_random_scale.get()
                this_y_depth=y_depth_max*counter/(num_items-1)+y_depth_min*(num_items-1-counter)/(num_items-1)
                layer_items.items[i][3][1]=((1-ap)+ap*layer_items.items[i][3][1])*100/(100-this_y_depth)+y_random
                # steady increase in scale_y with added random component
                counter +=1

        update_layer_labels()
        layer_items.redraw(t)

    def actually_ready():
        popup.destroy()
        return "done" #so that we know that there is nothing left to do
    def abs_ready():
        ready(0)#this is a trick to reduce indentation.  1 represents summing by previous value
    def rel_ready():
        ready(1)

    abs_ready_button=tk.Button(popup,text="Absolute change",command=abs_ready)
    rel_ready_button=tk.Button(popup,text="Relative change",command=rel_ready)
    actually_ready_button=tk.Button(popup,text="Close",command=actually_ready)
    
    actually_ready_button.grid(row=6,column=2)
    abs_ready_button.grid(row=6,column=0)
    rel_ready_button.grid(row=6,column=1)


#for adjusting the positioning of all active layers
def position_popup():
    global layer_items
    popup = tk.Toplevel(root)
    posx_label = tk.Label(popup,text="Positioning in the x-direction")
    posx_label.grid(row=0,column=0)
    posx_scale= tk.Scale(popup,orient=HORIZONTAL,from_=-500,to=500)
    posx_scale.grid(row=1,column=0)
    posx_scale.set(0)
    xincrease_label = tk.Label(popup,text="Shifting increasement in the x-direction")
    xincrease_label.grid(row=2,column=0)
    xincrease_scale= tk.Scale(popup,orient=HORIZONTAL,from_=-500,to=500)
    xincrease_scale.grid(row=3,column=0)
    xincrease_scale.set(0)
    x_random_label = tk.Label(popup,text="Random movement in the x-direction")
    x_random_label.grid(row=4,column=0)
    x_random_scale= tk.Scale(popup,orient=HORIZONTAL, from_=0,to=500)
    x_random_scale.grid(row=5,column=0)

    posy_label = tk.Label(popup,text="Positioning in the y-direction")
    posy_label.grid(row=0,column=1)
    posy_scale= tk.Scale(popup,orient=HORIZONTAL,from_=-500,to=500)
    posy_scale.grid(row=1,column=1)
    posy_scale.set(0)

    yincrease_label = tk.Label(popup,text="Shifting increasement in the y-direction")
    yincrease_label.grid(row=2,column=1)
    yincrease_scale= tk.Scale(popup,orient=HORIZONTAL,from_=-500,to=500)
    yincrease_scale.grid(row=3,column=1)
    yincrease_scale.set(0)
    y_random_label = tk.Label(popup,text="Random movement in the y-direction")
    y_random_label.grid(row=4,column=1)
    y_random_scale= tk.Scale(popup,orient=HORIZONTAL,from_=0,to=500)
    y_random_scale.grid(row=5,column=1)


    def ready(ap):#ap is 1 for relative change and 0 for absolute
        num_items=0
        for i in range(0,len(layer_items.items)):
            if layer_items.items[i][7]=="active":
                num_items +=1

        counter=0
        if num_items==1:#this is a trick to avoid division by zero
            num_items=2
            counter=1

        for i in range(0,len(layer_items.items)):
            if layer_items.items[i][7]=="active":
                x_random=(random.random()-0.5)*2*x_random_scale.get()
                x_shift=xincrease_scale.get()*counter 
                layer_items.items[i][5]=int(posx_scale.get()+ap*layer_items.items[i][5]+x_shift+x_random)
                # steady increase in scale_x with added random component
                y_random=(random.random()-0.5)*2*y_random_scale.get()
                y_shift=yincrease_scale.get()*counter 
                layer_items.items[i][6]=int(posy_scale.get()+ap*layer_items.items[i][6]+y_shift+y_random)
                # steady increase in scale_y with added random component
                counter +=1

        update_layer_labels()
        layer_items.redraw(t)

    def actually_ready():
        popup.destroy()
        return "done" #so that we know that there is nothing left to do
    def abs_ready():
        ready(0)#this is a trick to reduce indentation.  1 represents summing by previous value
    def rel_ready():
        ready(1)

    abs_ready_button=tk.Button(popup,text="Absolute change",command=abs_ready)
    rel_ready_button=tk.Button(popup,text="Relative change",command=rel_ready)
    actually_ready_button=tk.Button(popup,text="Close",command=actually_ready)
    
    actually_ready_button.grid(row=6,column=2)
    abs_ready_button.grid(row=6,column=0)
    rel_ready_button.grid(row=6,column=1)

#file name is choosen here, just in the beginning
def file_name_popup():
    global current_file_name
    file_pop = tk.Toplevel(root)
    file_label_text="Choose file name. To make animations use Timer button.\n"
    file_label_text +="Frames will be saved to the subfolder animations/filename/ \n"
    file_label_text +="To make the animation, use animation-command and choose that subfolder."
    file_label=tk.Label(file_pop,text=file_label_text)
    file_label.grid(row=1,column=0)
    file_entry=tk.Entry(file_pop)
    file_entry.grid(row=2,column=0)
    file_entry.insert(INSERT,"new") 
    def ready():#produces the animation from pngs in the directory
        global current_file_name
        current_file_name=file_entry.get()
        file_pop.destroy()
    file_button=tk.Button(file_pop,text="Ready:",command=ready)
    file_button.grid(row=7,column=0)



#for adjusting overall setting of the program
def options_popup():
    popup = tk.Toplevel(root)
    popup.geometry("280x335")
    popup_width=420
    other_canvas = tk.Canvas(popup,height=100,width=popup_width,bg="white")
    other_canvas.grid(row=0,column=0)
    coorcan_color="lightblue"
    coordinate_canvas = tk.Canvas(popup,height=100,width=popup_width,bg=coorcan_color)
    coordinate_canvas.grid(row=1,column=0)
    global DRAWTIME_CONSTANT,QUICK_WIDTH,QUICK_HEIGHT
    global SCALEX,SCALEY #these should be used also in functions_popup, when it is ready
    global RECYCLING_ON #do we bring back variables
    global SCREENSHOTS_ON # do we take screenshots after executing commandline


    def bg_choose():
        global turtle_screen_bg_color
        spin_turtle.pencolor(turtle_screen_bg_color)
        turtle_screen_bg_color=colorchooser.askcolor()[1]
        screen.bgcolor(turtle_screen_bg_color)
        spin_turtle.pencolor(turtle_screen_bg_color)
        update_layer_labels()
        root.focus_force()
        popup.destroy()
    def faster_drawing():
        global DRAWTIME_CONSTANT
        DRAWTIME_CONSTANT=int(DRAWTIME_CONSTANT*0.9)
        if DRAWTIME_CONSTANT<2:
            DRAWTIME_CONSTANT=2
        drawing_lag_label.config(text="drawing lag: "+ str(DRAWTIME_CONSTANT))
    def slower_drawing():
        global DRAWTIME_CONSTANT
        DRAWTIME_CONSTANT=max(int(DRAWTIME_CONSTANT*1.1),int(DRAWTIME_CONSTANT+1))
        drawing_lag_label.config(text="drawing lag: "+ str(DRAWTIME_CONSTANT))

    def minus_width(): #width of pngs for animation is adjusted
        global QUICK_WIDTH
        QUICK_WIDTH=int(QUICK_WIDTH-20)
        if QUICK_WIDTH<=20:
            QUICK_WIDTH=20
        width_label.config(text="animation width: "+ str(QUICK_WIDTH))
        match_screensize_with_screenshots()

    def plus_width(): #width of pngs for animation is adjusted
        global QUICK_WIDTH
        QUICK_WIDTH=int(QUICK_WIDTH+20)
        if QUICK_WIDTH>4000:
            QUICK_WIDTH=4000
        width_label.config(text="animation width: "+ str(QUICK_WIDTH))
        match_screensize_with_screenshots()

    def minus_height(): #height of pngs for animation is adjusted
        global QUICK_HEIGHT
        QUICK_HEIGHT=int(QUICK_HEIGHT-20)
        if QUICK_HEIGHT<=20:
            QUICK_HEIGHT=20
        height_label.config(text="animation height: "+ str(QUICK_HEIGHT))
        match_screensize_with_screenshots()

    def plus_height(): #height of pngs for animation is adjusted
        global QUICK_HEIGHT
        QUICK_HEIGHT=int(QUICK_HEIGHT+20)
        if QUICK_HEIGHT>4000:
            QUICK_HEIGHT=4000
        height_label.config(text="animation height: "+ str(QUICK_HEIGHT))
        match_screensize_with_screenshots()

    color_choose_button=tk.Button(other_canvas,text="choose background color",command=bg_choose)
    color_choose_button.grid(column=0,row=0)
    drawing_lag_label=tk.Label(other_canvas,text="drawing lag: "+ str(DRAWTIME_CONSTANT))
    faster_button=tk.Button(other_canvas,text="-",command=faster_drawing,repeatinterval=50,repeatdelay=300)
    slower_button=tk.Button(other_canvas,text="+",command=slower_drawing,repeatinterval=50,repeatdelay=300)
    drawing_lag_label.grid(column=0,row=1)
    faster_button.grid(column=1,row=1)
    slower_button.grid(column=2,row=1)

    width_label=tk.Label(coordinate_canvas,text="animation width: "+ str(QUICK_WIDTH),bg=coorcan_color)
    width_minus_button=tk.Button(coordinate_canvas,text="-",command=minus_width,repeatinterval=50,repeatdelay=300,bg=coorcan_color)
    width_plus_button=tk.Button(coordinate_canvas,text="+",command=plus_width,repeatinterval=50,repeatdelay=300,bg=coorcan_color)
    width_label.grid(column=0,row=2)
    width_minus_button.grid(column=1,row=2)
    width_plus_button.grid(column=2,row=2)

    height_label=tk.Label(coordinate_canvas,text="animation height: "+ str(QUICK_HEIGHT),bg=coorcan_color)
    height_minus_button=tk.Button(coordinate_canvas,text="-",command=minus_height,repeatinterval=50,repeatdelay=300,bg=coorcan_color)
    height_plus_button=tk.Button(coordinate_canvas,text="+",command=plus_height,repeatinterval=50,repeatdelay=300,bg=coorcan_color)
    height_label.grid(column=0,row=3)
    height_minus_button.grid(column=1,row=3)
    height_plus_button.grid(column=2,row=3)

    

    def origomode_change():
        global origomode
        if origomode=="show":
            origomode="hide"
            origoshow_button.config(text="rotating axels: invisible")
        elif origomode=="hide":
            origomode="show"
            origoshow_button.config(text="rotating axels: visible")
        layer_items.redraw(t)
    origoshow_button=tk.Button(other_canvas,text="rotating axles: visible",command=origomode_change)
    origoshow_button.grid(column=2,row=0)
    
    def minus_scalex():
        global SCALEX
        if SCALEX<0.00001:
            SCALEX=0.00001
        SCALEX=SCALEX-0.01*FunctionOperator.next_exponent_of_ten(max(0.0001,abs(SCALEX)))
        scalex_label.config(text="scaler of x-axis: "+ FunctionOperator.make_e_go_away(SCALEX,max_nro_of_decimals=8)[0:8])
    def plus_scalex():
        global SCALEX
        if SCALEX>10000:
            SCALEX=10000
        SCALEX=SCALEX+0.01*FunctionOperator.next_exponent_of_ten(max(0.0001,abs(SCALEX)))
        scalex_label.config(text="scaler of x-axis: "+ FunctionOperator.make_e_go_away(SCALEX,max_nro_of_decimals=8)[0:8])
    def minus_scaley():
        global SCALEY
        if SCALEY<0.00001:
            SCALEY=0.00001
        SCALEY=SCALEY-0.01*FunctionOperator.next_exponent_of_ten(max(0.0001,abs(SCALEY)))
        scaley_label.config(text="scaler of y-axis: "+FunctionOperator.make_e_go_away(SCALEY,max_nro_of_decimals=8)[0:8])
    def plus_scaley():
        global SCALEY
        if SCALEY>10000:
            SCALEY=10000
        SCALEY=SCALEY+0.01*FunctionOperator.next_exponent_of_ten(max(0.0001,abs(SCALEY)))
        scaley_label.config(text="scaler of y-axis: "+ FunctionOperator.make_e_go_away(SCALEY,max_nro_of_decimals=8)[0:8])

    def minus_origox():
        global ORIGOX
        if ORIGOX<-10000:
            ORIGOX=-10000
        ORIGOX=ORIGOX-0.01*FunctionOperator.next_exponent_of_ten(max(0.0001,abs(ORIGOX)))
        origox_label.config(text="x-value in origo: "+ FunctionOperator.make_e_go_away(ORIGOX,max_nro_of_decimals=8)[0:8])
    def plus_origox():
        global ORIGOX
        if ORIGOX>10000:
            ORIGOX=10000
        ORIGOX=ORIGOX+0.01*FunctionOperator.next_exponent_of_ten(max(0.0001,abs(ORIGOX)))
        origox_label.config(text="x-value in origo: "+ FunctionOperator.make_e_go_away(ORIGOX,max_nro_of_decimals=8)[0:8])

    def minus_origoy():
        global ORIGOY
        if ORIGOY<-10000:
            ORIGOY=-10000
        ORIGOY=ORIGOY-0.01*FunctionOperator.next_exponent_of_ten(max(0.0001,abs(ORIGOY)))
        origoy_label.config(text="y-value in origo: "+ FunctionOperator.make_e_go_away(ORIGOY,max_nro_of_decimals=8)[0:8])
    def plus_origoy():
        global ORIGOY
        if ORIGOY>10000:
            ORIGOY=10000
        ORIGOY=ORIGOY+0.01*FunctionOperator.next_exponent_of_ten(max(0.0001,abs(ORIGOY)))
        origoy_label.config(text="y-value in origo: "+FunctionOperator.make_e_go_away(ORIGOY,max_nro_of_decimals=8)[0:8])

    theinfo_label=tk.Label(coordinate_canvas,text="coordinates for animations and drawing math: ",bg="yellow")
    theinfo_label.grid(column=0,row=0,columnspan=2)
    scalex_label=tk.Label(coordinate_canvas,text="scaler of x-axis: "+ str(SCALEX)[0:6],bg=coorcan_color)
    scalex_minus_button=tk.Button(coordinate_canvas,text="-",command=minus_scalex,repeatinterval=10,repeatdelay=300,bg=coorcan_color)
    scalex_plus_button=tk.Button(coordinate_canvas,text="+",command=plus_scalex,repeatinterval=10,repeatdelay=300,bg=coorcan_color)
    scaley_label=tk.Label(coordinate_canvas,text="scaler of y-axis: "+ str(SCALEY)[0:6],bg=coorcan_color)
    scaley_minus_button=tk.Button(coordinate_canvas,text="-",command=minus_scaley,repeatinterval=10,repeatdelay=300,bg=coorcan_color)
    scaley_plus_button=tk.Button(coordinate_canvas,text="+",command=plus_scaley,repeatinterval=10,repeatdelay=300,bg=coorcan_color)
    scalex_label.grid(column=0,row=5)
    scalex_minus_button.grid(column=1,row=5)
    scalex_plus_button.grid(column=2,row=5)
    scaley_label.grid(column=0,row=6)
    scaley_minus_button.grid(column=1,row=6)
    scaley_plus_button.grid(column=2,row=6)



    origox_label=tk.Label(coordinate_canvas,text="x-value in origo: "+ str(ORIGOX)[0:7],bg=coorcan_color)
    origox_minus_button=tk.Button(coordinate_canvas,text="-",command=minus_origox,repeatinterval=10,repeatdelay=300,bg=coorcan_color)
    origox_plus_button=tk.Button(coordinate_canvas,text="+",command=plus_origox,repeatinterval=10,repeatdelay=300,bg=coorcan_color)
    origoy_label=tk.Label(coordinate_canvas,text="y-value in origo: "+ str(ORIGOY)[0:7],bg=coorcan_color)
    origoy_minus_button=tk.Button(coordinate_canvas,text="-",command=minus_origoy,repeatinterval=10,repeatdelay=300,bg=coorcan_color)
    origoy_plus_button=tk.Button(coordinate_canvas,text="+",command=plus_origoy,repeatinterval=10,repeatdelay=300,bg=coorcan_color)
    origox_label.grid(column=0,row=7)
    origox_minus_button.grid(column=1,row=7)
    origox_plus_button.grid(column=2,row=7)
    origoy_label.grid(column=0,row=8)
    origoy_minus_button.grid(column=1,row=8)
    origoy_plus_button.grid(column=2,row=8)

    popup_canvas = tk.Canvas(popup,height=100,width=popup_width,bg=coorcan_color)
    popup_canvas.grid(row=2,column=0)
    animation_button=tk.Button(popup_canvas,text="animation",command=animation_popup,bg="yellow",width=9)
    animation_button.grid(column=0,row=0)
    photo_button=tk.Button(popup_canvas,text="photo",command=photo_popup,bg="yellow",width=9)
    photo_button.grid(column=1,row=0)
    grid_button=tk.Button(popup_canvas,text="grid",command=grid_popup,bg="yellow",width=9)
    grid_button.grid(column=2,row=0)
    D3_button=tk.Button(popup_canvas,text="3D grid",command=D3_popup,bg="yellow",width=9)
    D3_button.grid(column=3,row=0)
    color_button=tk.Button(popup_canvas,text="color",command=color_popup,bg="green",width=9)
    color_button.grid(column=0,row=1)
    scale_button=tk.Button(popup_canvas,text="scale",command=scale_popup,bg="green",width=9)
    scale_button.grid(column=1,row=1)
    position_button=tk.Button(popup_canvas,text="position",command=position_popup,bg="green",width=9)
    position_button.grid(column=2,row=1)
    depth_button=tk.Button(popup_canvas,text="depth",command=depth_popup,bg="green",width=9)
    depth_button.grid(column=3,row=1)
    orientation_button=tk.Button(popup_canvas,text="orientation",command=orientation_popup,bg="green",width=9)
    orientation_button.grid(column=0,row=2)
    order_button=tk.Button(popup_canvas,text="layer order",command=layerorder_popup,bg="green",width=9)
    order_button.grid(column=1,row=2)
    csv_button=tk.Button(popup_canvas,text="make csv",command=csv_popup,bg="green",width=9)
    csv_button.grid(column=2,row=2)
    def recycling_switch():
        global RECYCLING_ON
        if RECYCLING_ON:
            RECYCLING_ON=False
            recycling_button.config(text="Recycling: off")
        else:
            RECYCLING_ON=True
            recycling_button.config(text="Recycling: on")

    recycling_button=tk.Button(popup_canvas,text="Recycling: on",command=recycling_switch,bg="lightblue",width=12)
    recycling_button.grid(column=0,row=3)
    
    def screenshot_switch():
        global SCREENSHOTS_ON
        if SCREENSHOTS_ON:
            SCREENSHOTS_ON=False
            screenshots_button.config(text="Screenshots: off")
        else:
            SCREENSHOTS_ON=True
            screenshots_button.config(text="Screenshots: on")

    screenshots_button=tk.Button(popup_canvas,text="Screenshots: off",command=screenshot_switch,bg="lightblue",width=12)
    screenshots_button.grid(column=1,row=3)





#make animations out of saved pngs
def animation_popup():
    global current_file_name
    global save_entry
    video_pop = tk.Toplevel(root)
    save_label=tk.Label(video_pop,text="Save name:")
    save_label.grid(row=1,column=0)
    save_entry=tk.Entry(video_pop)
    save_entry.grid(row=1,column=1)
    frame_label=tk.Label(video_pop,text="Frames per second:")
    frame_label.grid(row=2,column=0)
    frame_scale=tk.Scale(video_pop,from_=1,to=100,orient=HORIZONTAL)
    frame_scale.set(FRAME_CONSTANT)
    frame_scale.grid(row=2,column=1)
    def ready():#produces the animation from pngs in the directory
        if save_entry.get()=="":
            messagebox.showinfo("Name required","Enter the name of the video first")
            return
        animation_button.config(text="Producing...")
        output_video_path=os.path.join("animations//", save_entry.get()+".mp4")#changed out... to this in 2.12. see if works
        truth=True
        if path.exists(output_video_path): #first let's make sure that we don't owerwrite old videos
            truth=messagebox.askyesno("File already exists","Overwrite?")
        if truth==False:#if user doesn't want to overwrite, then go away from the method
            return False
        input_directory = VideoMaker.pick_directory_using_file([("Image Files", "*.png"),("Image Files", "*.jpg")],"animations")
        #output_directory_video = VideoMaker.pick_directory("Select Output Directory for Video")
        png_to_video_converter = VideoMaker.PngToVideoConverter(input_directory, output_video_path)
        #output_video_path = os.path.join(output_directory_video, save_entry.get()+".mp4") old version changed 2.12.
        png_to_video_converter.convert_to_video(output_video_path,frame_rate=frame_scale.get())
        messagebox.showinfo(title="Conversion complete",message= "Video saved at "+ str(output_video_path))
        video_pop.destroy() 
    animation_button=tk.Button(video_pop,text="Choose folder to animate:",command=ready)
    animation_button.grid(row=3,column=0)
    global filename1,filename2
    filename1="" #these are names of the files to be combined
    filename2="" #these are names of the files to be combined
    def glue(): #put video2 after video 1
        if save_entry.get()=="":
            messagebox.showinfo("Name required","Enter the name of the video first")
            return
        result_video_name=os.path.join("animations//", save_entry.get()+".mp4")
        truth=True
        if path.exists(result_video_name): #first let's make sure that we don't owerwrite old videos
            truth=messagebox.askyesno("File already exists","Overwrite?")
        if truth==False:#if user doesn't want to overwrite, then go away from the method
            return False
        video_combiner = VideoMaker.VideoCombiner(filename1, filename2, result_video_name)
        video_combiner.glue_videos()
        messagebox.showinfo(title="Video combined",message="Video combined and saved as: "+result_video_name)
    def overlay():
        if save_entry.get()=="":
            messagebox.showinfo("Name required","Enter the name of the video first")
            return
        result_video_name=os.path.join("animations//", save_entry.get()+".mp4")
        truth=True
        if path.exists(result_video_name): #first let's make sure that we don't owerwrite old videos
            truth=messagebox.askyesno("File already exists","Overwrite?")
        if truth==False:#if user doesn't want to overwrite, then go away from the method
            return False
        video_combiner2 = VideoMaker.VideoCombiner(filename1, filename2, result_video_name)
        video_combiner2.combine_videos()
        messagebox.showinfo(title="Videos overlayed",message="Overlayed video saved as: "+result_video_name)

    def combine():#overlay two videos
        global filename1,filename2,save_entry

        def first_video(): #pick first video to combine
            global filename1,filename2
            filename1=filedialog.askopenfilename(initialdir="animations/")
            combine1_label.config(text="Video1:..."+filename1[-12:])
            if filename1!="" and filename2!="":
                glue_button=tk.Button(video_pop,text="Join videos",command=glue)
                glue_button.grid(row=6,column=0)
                overlay_button=tk.Button(video_pop,text="Overlay videos",command=overlay)
                overlay_button.grid(row=6,column=1)

        def second_video(): #pick first video to combine
            global filename1,filename2
            filename2=filedialog.askopenfilename(initialdir="animations/")
            combine2_label.config(text="Video2:..."+filename2[-12:])
            if filename1!="" and filename2!="":
                glue_button=tk.Button(video_pop,text="Join videos",command=glue)
                glue_button.grid(row=6,column=0)
                overlay_button=tk.Button(video_pop,text="Overlay videos",command=overlay)
                overlay_button.grid(row=6,column=1)
        combine1_label=tk.Label(video_pop,text="Video1:"+filename1)
        combine1_label.grid(row=5,column=0)
        combine1_button=tk.Button(video_pop,text="Choose first video:",command=first_video)
        combine1_button.grid(row=4,column=0)
        combine2_label=tk.Label(video_pop,text="Video2:"+filename2)
        combine2_label.grid(row=5,column=1)
        combine2_button=tk.Button(video_pop,text="Choose second video:",command=second_video)
        combine2_button.grid(row=4,column=1)
        save_entry=tk.Entry(video_pop)
        save_entry.grid(row=1,column=1)            
    combine_button=tk.Button(video_pop,text="Choose videos to join:",command=combine)
    combine_button.grid(row=3,column=1)



#pick a video and make a cartoon out of it, choose style and fps:s etc
def cartoon_popup():
    global layer_items
    cartoon_pop = tk.Toplevel(root) 
    video_path=None # the location of the video is saved in here
    cartoon_savename_label=tk.Label(cartoon_pop,text="Save cartoon as")
    cartoon_savename_entry=tk.Entry(cartoon_pop)
    cartoon_fps_label=tk.Label(cartoon_pop,text="Frames per second")
    cartoon_fps_entry=tk.Entry(cartoon_pop)

    video_label= tk.Label(cartoon_pop,text="Pick video to be cartoonized")

    def choose_video(): #for choosing the video
        global video_path
        video_path = VideoMaker.pick_file("Select Input Video File", [("Video Files", "*.mp4")])
        ready(video_path)

    cartoon_savename_label.grid(row=10,column=0)
    cartoon_savename_entry.grid(row=10,column=1)
    cartoon_fps_label.grid(row=11,column=0)
    cartoon_fps_entry.grid(row=11,column=1)
    video_button=tk.Button(cartoon_pop,text="Load:",command=choose_video)
    video_label.grid(row=12, column=0)
    video_button.grid(row=12, column=1)
    layer_contrast_label=tk.Label(cartoon_pop,text="Resolution: (1,3000)")#contr_points
    layer_contrast_label.grid(row=2,column=0)
    resolution_value_entry=tk.Entry(cartoon_pop)
    resolution_value_entry.grid(row=2,column=1)
    resolution_value_entry.insert(INSERT,"10")

    contrast_quality_label=tk.Label(cartoon_pop,text="Quality of contrast_points: (1...100)")#c_parameter
    contrast_quality_label.grid(row=3,column=0)
    cquality_entry=tk.Entry(cartoon_pop)
    cquality_entry.grid(row=3,column=1)
    cquality_entry.insert(INSERT,"5")

    min_angle_label=tk.Label(cartoon_pop,text="Minimum angle: (1...30)")#c_parameter
    min_angle_label.grid(row=4,column=0)
    min_angle_entry=tk.Entry(cartoon_pop)
    min_angle_entry.grid(row=4,column=1)
    min_angle_entry.insert(INSERT,"15")

    contrast_label=tk.Label(cartoon_pop,text="Contrast: (between -40.0...40.0)")#c_parameter
    contrast_label.grid(row=5,column=0)
    contrast_entry=tk.Entry(cartoon_pop)
    contrast_entry.grid(row=5,column=1)
    contrast_entry.insert(INSERT,"4")

    colorscale_label=tk.Label(cartoon_pop,text="Color richness: (between 0...256)")#c_parameter
    colorscale_label.grid(row=6,column=0)
    color_scale_entry=tk.Entry(cartoon_pop)
    color_scale_entry.grid(row=6,column=1)
    color_scale_entry.insert(INSERT,"5")
    var1=tk.IntVar()
    def rectangle_value():
        var1.set(1)
        layer_contrast_label.config(text="Resolution: (1,3000)")
        contrast_quality_label.config(text="Quality of contrast_points: (1...100)")
        min_angle_label.config(text="Minimum side lenght: (1...30)")
        contrast_label.config(text="Contrast: (between -40.0...40.0)")
        colorscale_label.config(text="Color richness: (between 0...256)")
    def triangle_value():
        var1.set(0)
        layer_contrast_label.config(text="Resolution: (1,3000)")
        contrast_quality_label.config(text="Quality of contrast_points: (1...100)")
        min_angle_label.config(text="Minimum angle: (1...30)")
        contrast_label.config(text="Contrast: (between -40.0...40.0)")
        colorscale_label.config(text="Color richness: (between 0...256)")
    def polygon_value():
        var1.set(2)
        layer_contrast_label.config(text="Percentage to keep color (between 0 and 0.5)")
        contrast_quality_label.config(text="Detail level from 1...10")
        min_angle_label.config(text="Minimum side length")
        contrast_label.config(text="Contrast: (between -40.0...40.0)")
        colorscale_label.config(text="Color richness: (between 1...256)")

    simple_color_checkbox=tk.Checkbutton(cartoon_pop,text="Rectangles",variable=var1, onvalue=1,offvalue=0,command=rectangle_value)
    simple_color_checkbox.grid(row=1,column=0)
    simple_color_checkbox=tk.Checkbutton(cartoon_pop,text="Triangles",variable=var1, onvalue=0,offvalue=1,command=triangle_value)
    simple_color_checkbox.grid(row=1,column=1)
    simple_color_checkbox=tk.Checkbutton(cartoon_pop,text="Polygons",variable=var1, onvalue=2,offvalue=1,command=polygon_value)
    simple_color_checkbox.grid(row=1,column=2)
    var1.set(1)#at the start we want to suggest making polygons
    pensize_label=tk.Label(cartoon_pop,text="Pensize: (between 1...100)")#pensize
    pensize_label.grid(row=7,column=0)
    pensize_entry=tk.Entry(cartoon_pop)
    pensize_entry.grid(row=7,column=1)
    pensize_entry.insert(INSERT,"1")

    def ready(video_path):
        global temporary_file_string
        
        prop=PngMaker.PngProperties()
        prop.set("contrast_points",int(resolution_value_entry.get()))
        prop.set("c_parameter",int(cquality_entry.get()))
        prop.set("min_angle",int(min_angle_entry.get()))
        prop.set("end_contrast",float(contrast_entry.get()))
        prop.set("color_divisions",int(color_scale_entry.get()))
        prop.set("pensize",int(pensize_entry.get()))
        prop.set("style","rectangle")
        save_name=""
        prop.set("percentage",0.1) #this is actually splitting_prob for triangles ans rectangles
        pd=prop.png_dict
        ratio=max(1,int(30/int(cartoon_fps_entry.get()))) #for example if ratio = 3, then every third frame is selected on the videom
        #if videos original frame rate is not 30, this might leed problems with too fast or slow motion animation


        savename=cartoon_savename_entry.get()  #cartoon will be put in animations/savename with name savename.mp4()
        dir_existence=os.path.isdir("animations/"+savename+"/")
        if dir_existence:
            truth=messagebox.askyesno("File already exists","Overwrite?")
            if truth==False:#if user doesn't want to overwrite, then go away from the method
                return
        #now we either have new filename, or want to overwrite old one
        create_directory("animations/"+savename+"/") #we create directory where new file goes  
        output_dir="animations/"+savename
        if var1.get()==0: 
            pd["style"]="triangle"
            pd["percentage"]=0.1
        if var1.get()==1:
            pd["style"]="rectangle"
            pd["percentage"]=0.1
        if var1.get()==2:
            pd["style"]="polygon"
            pd["percentage"]=float(contrast_entry.get())
            if pd["percentage"]<0:
                pd["percentage"]=0
            if pd["percentage"]>0.5 and pd["percentage"]<1:
                pd["percentage"]=0.5
            if pd["percentage"]>=1 and pd["percentage"]<=50:
                pd["percentage"]=pd["percentage"]/100 #this trick allows both using percentages and "absolute values"
            if pd["percentage"]>50:
                pd["percentage"]=0.5

        if pd["style"] in ["polygon","rectangle","triangle"]:
            video_to_png_converter = VideoMaker.VideoToPngConverter(video_path, output_path=output_dir)
            video_to_png_converter.video_to_animation(output_dir,savename,ratio,prop)
        
    def close():
        cartoon_pop.destroy() 

    file_choose4_button=tk.Button(cartoon_pop,text="Close:",command=close)
    file_choose4_button.grid(row=12,column=2)

#for creating csvfiles
def csv_popup():
    global db
    global command_line_entry
    def import_function(list):
        command_line_entry.insert("1.0",str(list[0])+"="+str(list[1])+"|")
    FunctionOperator.run_csv_maker(db,import_function)

#this can be used to draw functions NOTE KESKEN
def function_popup():
    global layer_items
    global SCALEX,SCALEY
    global ORIGOX,ORIGOY
    function_pop = tk.Toplevel(root) 
    function_name_label=tk.Label(function_pop,text="Name of the function:")#contr_points
    function_name_label.grid(row=1,column=0)
    function_name_entry=tk.Entry(function_pop)
    function_name_entry.grid(row=1,column=1)
    function_name_entry.insert(INSERT,"f")
    expression_label=tk.Label(function_pop,text="Function expression: "+function_name_entry.get()+"(x)=")#contr_points
    expression_label.grid(row=2,column=0)
    expression_entry=tk.Entry(function_pop)
    expression_entry.grid(row=2,column=1)
    expression_entry.insert(INSERT,"x")
    x_scale_label=tk.Label(function_pop,text="Scale of the x-axis:")#contr_points
    x_scale_label.grid(row=3,column=0)
    x_scale_entry=tk.Entry(function_pop)
    x_scale_entry.grid(row=3,column=1)
    x_scale_entry.insert(INSERT,text=str(SCALEX))
    y_scale_label=tk.Label(function_pop,text="Scale of the y-axis:")#contr_points
    y_scale_label.grid(row=4,column=0)
    y_scale_entry=tk.Entry(function_pop)
    y_scale_entry.grid(row=4,column=1)
    y_scale_entry.insert(INSERT,text=str(SCALEX))
    no_coordinates_checkbox=tk.Checkbutton(function_pop,text="No coordinates",variable=var1, onvalue=0,offvalue=1,command=no_coordinates_value)
    no_coordinates_checkbox.grid(row=5,column=0)
    coordinates_same_checkbox=tk.Checkbutton(function_pop,text="Coordinates, same layer",variable=var1, onvalue=1,offvalue=2,command=coordinates_in_same_layer_value)
    coordinates_same_checkbox.grid(row=5,column=1)
    coordinates_other_checkbox=tk.Checkbutton(function_pop,text="Coordinates, other layer",variable=var1, onvalue=2,offvalue=0,command=coordinates_in_other_layer_value)
    coordinates_other_checkbox.grid(row=5,column=2)

    var1=tk.IntVar() #records do we show coordinates
    def no_coordinates_value():
        var1.set(0)
    def coordinates_in_same_layer_value():
        var1.set(1)
    def coordinates_in_other_layer_value():
        var1.set(2)

    def close():
        photo_pop.destroy() 
    
    def ready():
        global db
        function_name=function_name_entry.get()
        #draw_coordinates(xscale,yscale) do this later
        xscale=x_scale_entry.get()
        yscale=y_scale_entry.get()
        expression=expression_entry.get()
        draw_function(xscale,yscale,expression)

    file_choose3_button=tk.Button(photo_pop,text="Create and add:",command=ready)
    file_choose3_button.grid(row=10,column=0)
    file_choose4_button=tk.Button(photo_pop,text="Close:",command=close)
    file_choose4_button.grid(row=10,column=1)



#make a drawing out of png file
def photo_popup():
    global layer_items
    photo_pop = tk.Toplevel(root) 
    layer_contrast_label=tk.Label(photo_pop,text="Resolution: (1,3000)")#contr_points
    layer_contrast_label.grid(row=1,column=0)
    resolution_value_entry=tk.Entry(photo_pop)
    resolution_value_entry.grid(row=1,column=1)
    resolution_value_entry.insert(INSERT,"10")

    contrast_quality_label=tk.Label(photo_pop,text="Quality of contrast_points: (1...100)")#c_parameter
    contrast_quality_label.grid(row=2,column=0)
    cquality_entry=tk.Entry(photo_pop)
    cquality_entry.grid(row=2,column=1)
    cquality_entry.insert(INSERT,"5")

    min_angle_label=tk.Label(photo_pop,text="Minimum angle: (1...30)")#c_parameter
    min_angle_label.grid(row=3,column=0)
    min_angle_entry=tk.Entry(photo_pop)
    min_angle_entry.grid(row=3,column=1)
    min_angle_entry.insert(INSERT,"15")

    contrast_label=tk.Label(photo_pop,text="Contrast: (between -40.0...40.0)")#c_parameter
    contrast_label.grid(row=4,column=0)
    contrast_entry=tk.Entry(photo_pop)
    contrast_entry.grid(row=4,column=1)
    contrast_entry.insert(INSERT,"4")

    colorscale_label=tk.Label(photo_pop,text="Color richness: (between 0...256)")#c_parameter
    colorscale_label.grid(row=5,column=0)
    color_scale_entry=tk.Entry(photo_pop)
    color_scale_entry.grid(row=5,column=1)
    color_scale_entry.insert(INSERT,"5")

    pensize_label=tk.Label(photo_pop,text="Pensize: (between 1...100)")#pensize
    pensize_label.grid(row=6,column=0)
    pensize_entry=tk.Entry(photo_pop)
    pensize_entry.grid(row=6,column=1)
    pensize_entry.insert(INSERT,"1")

    end_size_label=tk.Label(photo_pop,text="Resize to size: (leave empty, if not) ")#c_parameter
    end_size_label.grid(row=7,column=0,columnspan=2)
    end_width_entry=tk.Entry(photo_pop,text="width")
    end_height_entry=tk.Entry(photo_pop,text="height")
    end_width_entry.grid(row=8,column=0)
    end_height_entry.grid(row=8,column=1)

    var1=tk.IntVar()
    def rectangle_value():
        var1.set(1)
        layer_contrast_label.config(text="Resolution: (1,3000)")
        contrast_quality_label.config(text="Quality of contrast_points: (1...100)")
        min_angle_label.config(text="Minimum side lenght: (1...30)")
        contrast_label.config(text="Contrast: (between -40.0...40.0)")
        colorscale_label.config(text="Color richness: (between 0...256)")
    def triangle_value():
        var1.set(0)
        layer_contrast_label.config(text="Resolution: (1,3000)")
        contrast_quality_label.config(text="Quality of contrast_points: (1...100)")
        min_angle_label.config(text="Minimum angle: (1...30)")
        contrast_label.config(text="Contrast: (between -40.0...40.0)")
        colorscale_label.config(text="Color richness: (between 0...256)")
    def polygon_value():
        var1.set(2)
        layer_contrast_label.config(text="Percentage to keep color (between 0 and 0.5)")
        contrast_quality_label.config(text="Detail level from 1...10")
        min_angle_label.config(text="Minimum side length")
        contrast_label.config(text="Contrast: (between -40.0...40.0)")
        colorscale_label.config(text="Color richness: (between 1...256)")
    def simple_value():
        var1.set(3)
        layer_contrast_label.config(text="Percentage to keep color (between 0 and 0.5)")
        contrast_quality_label.config(text="Detail level from 1...10")
        contrast_label.config(text="Contrast: (between -40.0...40.0)")
        colorscale_label.config(text="Color richness: (between 1...256)")

     

    simple_color_checkbox=tk.Checkbutton(photo_pop,text="Rectangles",variable=var1, onvalue=1,offvalue=0,command=rectangle_value)
    simple_color_checkbox.grid(row=0,column=0)
    simple_color_checkbox=tk.Checkbutton(photo_pop,text="Triangles",variable=var1, onvalue=0,offvalue=1,command=triangle_value)
    simple_color_checkbox.grid(row=0,column=1)
    simple_color_checkbox=tk.Checkbutton(photo_pop,text="Polygons",variable=var1, onvalue=2,offvalue=1,command=polygon_value)
    simple_color_checkbox.grid(row=0,column=2)
    simple_color_checkbox=tk.Checkbutton(photo_pop,text="Simple",variable=var1, onvalue=3,offvalue=1,command=simple_value)
    simple_color_checkbox.grid(row=0,column=3)


    def ready(filename,actiontype):
        global temporary_file_string
        prop=PngMaker.PngProperties()
        back_prop=PngMaker.standard_back() #this is also PngProperties object
        #and it is for making backround to picture that fills the white holes which might form in main image
        prop.set("contrast_points",int(resolution_value_entry.get()))
        prop.set("c_parameter",int(cquality_entry.get()))
        prop.set("min_angle",int(min_angle_entry.get()))
        prop.set("min_line_length",int(min_angle_entry.get()))
        prop.set("end_contrast",float(contrast_entry.get()))
        prop.set("color_divisions",int(color_scale_entry.get()))
        prop.set("pensize",int(pensize_entry.get()))
        back_prop.set("pensize",int(pensize_entry.get())) #might be good idea to use same pensize
        prop.set("style","rectangle")
        if is_number(end_width_entry.get()):
            prop.set("end_width",int(end_width_entry.get()))
            back_prop.set("end_width",int(end_width_entry.get()))
        else:
            prop.set("end_width",None)
            back_prop.set("end_width",None)

        if is_number(end_height_entry.get()):
            prop.set("end_height",int(end_height_entry.get()))
            back_prop.set("end_height",int(end_height_entry.get()))
        else:
            prop.set("end_height",None)
            back_prop.set("end_height",None)

        save_name=""
        prop.set("percentage",0.1) #this is actually splitting_prob for triangles ans rectangles
        back_prop.set("percentage",0.2) #this is actually splitting_prob for triangles ans rectangles
        pd=prop.png_dict
        back_pd=back_prop.png_dict
        if var1.get()==0: 
            prop.set("style","triangle")
            prop.set("percentage",0.1)
            back_prop.set("style","triangle")
            back_prop.set("percentage",0.2)
        if var1.get()==1:
            prop.set("style","rectangle")
            prop.set("percentage",0.1)
            back_prop.set("style","rectangle")
            back_prop.set("percentage",0.2)
        if var1.get()==2:
            prop.set("style","polygon")
            prop.set("percentage",float(contrast_entry.get()))
            back_prop.set("style","polygon")
            back_prop.set("percentage",0.2)
            if pd["percentage"]<0:
                prop.set("percentage",0)
            if pd["percentage"]>0.5 and pd["percentage"]<1:
                prop.set("percentage",0.5)
            if pd["percentage"]>=1 and pd["percentage"]<=50:
                prop.set("percentage",pd["percentage"]/100) #this trick allows both using percentages and "absolute values"
            if pd["percentage"]>50: #back_prop doesn't need this trick
                prop.set("percentage",0.5)
        if var1.get()==3:
            prop.set("style","simple")
            back_prop.set("style","simple")

        if pd["style"] in ["rectangle","triangle"]:
            save_name=PngMaker.from_png_to_Drawing(filename,prop)#this both saves the file and
            save_name= filename_without_subdir(save_name,"drawings") 
            #returns the name of the file and also creates it in this same method
            if pd["style"]=="rectangle": #we don't need back wtih triangles
                back_save_name=PngMaker.from_png_to_Drawing(filename,back_prop,savename="machinery\\back.txt")#this both saves the file
                back_save_name= filename_without_subdir(back_save_name,"machinery") 
        if pd["style"] in ["polygon"]:
            save_name=PngMaker.png_to_polygon_Drawing(filename,prop)#this both saves the file and
            save_name= filename_without_subdir(save_name,"drawings") 
            #returns the name of the file and also creates it in this same method
            back_save_name=PngMaker.png_to_polygon_Drawing(filename,back_prop,savename="machinery\\back.txt")#this both saves the file and
            back_save_name= filename_without_subdir(back_save_name,"machinery") 
        if pd["style"]=="simple":
            save_name=PngMaker.from_photo_to_cartoon(filename,prop) 
            save_name= filename_without_subdir(save_name,"drawings") 
            back_save_name=PngMaker.from_photo_to_cartoon(filename,back_prop,savename="machinery\\back.txt") 
            back_save_name= filename_without_subdir(back_save_name,"machinery") 

        if actiontype==1 and pd["style"] in ["polygon","rectangle"]:
            #in this point we have two drawings one with save_name and other with back_save_name, we join them into one
            filetext= layer_items.load_file_as_string(save_name,"drawings")
            back_filetext= layer_items.load_file_as_string(back_save_name,"machinery")#we now put this on different layer, 
            new_text = back_filetext+filetext #this used to be just: temporary_file_string += filetext
            save_text_file(directory_path="drawings", file_name=save_name+".txt", content=new_text)

        if actiontype==2:#adds background and more detailed drawing to separate layers
            filetext= layer_items.load_file_as_string(save_name,"drawings")
            if  pd["style"] in ["polygon","rectangle"]:
                back_filetext= layer_items.load_file_as_string(back_save_name,"machinery")#we now put this on different layer, 
            #but consider glueing this before save_name file text
                layer_items.add_item(0,"objects",back_save_name,[1,1],0,0,0,"active",0,0,0,"",back_filetext)
            layer_items.add_item(0,"objects",save_name,[1,1],0,0,0,"active",0,0,0,"",filetext)
            layer_items.redraw(t)
            update_layer_labels()
        if actiontype==3: #adds into currently drawn layer
            filetext= layer_items.load_file_as_string(save_name,"drawings")
            back_filetext=""
            if  pd["style"] in ["polygon","rectangle"]:
                back_filetext= layer_items.load_file_as_string(back_save_name,"machinery")#we now put this on different layer, 
            temporary_file_string += back_filetext+filetext #this used to be just: temporary_file_string += filetext
            draw_temporary_file()
            update_layer_labels()

        if prop.get("style") != "simple":#in the end we create mini_image if style wasn't empty
            create_mini_image(save_name,"drawings/"+save_name)

    def file_choose():
        filename=filedialog.askopenfilename(initialdir="pngs/")
        ready(filename,1)
    
    def file_choose2():
        filename=filedialog.askopenfilename(initialdir="pngs/")
        ready(filename,2)
        if mode=="drawing_mode":#we want to go to edit mode
            draw_mode()

    def file_choose3():
        filename=filedialog.askopenfilename(initialdir="pngs/")
        ready(filename,3)

    def close():
        photo_pop.destroy() 

    file_choose_button=tk.Button(photo_pop,text="Png to drawing:",command=file_choose)
    file_choose_button.grid(row=9,column=1)
    file_choose2_button=tk.Button(photo_pop,text="Add as a layer:",command=file_choose2)
    file_choose2_button.grid(row=9,column=0)
    file_choose3_button=tk.Button(photo_pop,text="Create and add:",command=file_choose3)
    file_choose3_button.grid(row=10,column=0)
    file_choose4_button=tk.Button(photo_pop,text="Close:",command=close)
    file_choose4_button.grid(row=10,column=1)


#for adjusting the colorshifts of all active layers
def color_popup():
    global layer_items
    popup = tk.Toplevel(root)
    popup.geometry("420x240")
    r_shift_label = tk.Label(popup,text="Constant red shift") 
    g_shift_label = tk.Label(popup,text="Constant green shift")
    b_shift_label = tk.Label(popup,text="Constant blue shift")
    r_increment_label = tk.Label(popup,text="Red increasement")
    g_increment_label = tk.Label(popup,text="Green increasement")
    b_increment_label = tk.Label(popup,text="Blue increasement")
    r_shift_label.grid(row=0,column=0)
    r_shift_scale= tk.Scale(popup,orient=HORIZONTAL,from_=-256,to=256,bg="red")
    r_shift_scale.grid(row=1,column=0)
    g_shift_label.grid(row=2,column=0)
    g_shift_scale= tk.Scale(popup,orient=HORIZONTAL,from_=-256,to=256,bg="green")
    g_shift_scale.grid(row=3,column=0)
    b_shift_label.grid(row=4,column=0)
    b_shift_scale= tk.Scale(popup,orient=HORIZONTAL,from_=-256,to=256,bg="blue")
    b_shift_scale.grid(row=5,column=0)
    r_increment_label.grid(row=0,column=1)
    r_increment_scale= tk.Scale(popup,orient=HORIZONTAL,from_=-256,to=256,bg="red")
    r_increment_scale.grid(row=1,column=1)
    g_increment_label.grid(row=2,column=1)
    g_increment_scale= tk.Scale(popup,orient=HORIZONTAL,from_=-256,to=256,bg="green")
    g_increment_scale.grid(row=3,column=1)
    b_increment_label.grid(row=4,column=1)
    b_increment_scale= tk.Scale(popup,orient=HORIZONTAL,from_=-256,to=256,bg="blue")
    b_increment_scale.grid(row=5,column=1)
    r_random_label = tk.Label(popup,text="Random red variation")
    g_random_label = tk.Label(popup,text="Random green variation")
    b_random_label = tk.Label(popup,text="Random blue variation")

    r_random_scale= tk.Scale(popup,orient=HORIZONTAL,from_=0,to=256,bg="red")
    g_random_scale= tk.Scale(popup,orient=HORIZONTAL,from_=0,to=256,bg="green")
    b_random_scale= tk.Scale(popup,orient=HORIZONTAL,from_=0,to=256,bg="blue")


    def ready(multiplier):
        for i in range(0,len(layer_items.items)):
            if layer_items.items[i][7]=="active":
                r_random=(2*random.random()-1)*r_random_scale.get()+r_shift_scale.get()#second term is not actually random, its here to safe space
                layer_items.items[i][8]=(i*r_increment_scale.get()+r_random)/256 + multiplier*layer_items.items[i][8]# 
                g_random=(2*random.random()-1)*g_random_scale.get()+g_shift_scale.get()#same
                layer_items.items[i][9]=(i*g_increment_scale.get()+g_random)/256 + multiplier*layer_items.items[i][9] # 
                b_random=(2*random.random()-1)*b_random_scale.get()+b_shift_scale.get()#same
                layer_items.items[i][10]=(i*b_increment_scale.get()+b_random)/256 + multiplier*layer_items.items[i][10]# 
                for j in range(8,11):
                    if layer_items.items[i][j]<-1:
                        layer_items.items[i][j]=-1
                    if layer_items.items[i][j]>1:
                        layer_items.items[i][j]=1
        update_layer_labels()
        layer_items.redraw(t)

    def abs_ready():
        ready(0)#this is a trick to reduce indentation.  1 represents summing by previous value
    def rel_ready():
        ready(1)
    def actually_ready():
        popup.destroy()
        return "done" #so that we know that there is nothing left to do

    abs_ready_button=tk.Button(popup,text="Absolute change",command=abs_ready)
    rel_ready_button=tk.Button(popup,text="Relative change",command=rel_ready)
    actually_ready_button=tk.Button(popup,text="Close",command=actually_ready)
    r_random_label.grid(row=0,column=2)
    r_random_scale.grid(row=1,column=2)
    g_random_label.grid(row=2,column=2)
    g_random_scale.grid(row=3,column=2)
    b_random_label.grid(row=4,column=2)
    b_random_scale.grid(row=5,column=2)
    rel_ready_button.grid(row=7,column=0)
    abs_ready_button.grid(row=7,column=1)
    actually_ready_button.grid(row=7,column=2)


#parameter tell us what we want to do with user_text
def open_popup(parameter:str):
    global current_file_name
    popup = tk.Toplevel(root)

    label1 = tk.Label(popup,text=parameter)
    label1.pack()

    text1 = tk.Text(popup, height=5, width=60)  # Create a larger Text widget
    text1.pack()

    function_entry=tk.Entry(popup,text="function_name")
    if parameter=="add function":
        function_entry.pack() 


    def save_text():
        global temporary_file_string
        global mode
        global temp_turtle
        global current_file_name
        global writefont,writefontsize,writefontstyle
        user_text = text1.get("1.0", "end-1c")  # Retrieve the text from the Text widget
        if parameter=="*w":
            te=command_line_entry.get("1.0", "end-1c")
            te=te[0:first_pick()]+"'"+str(user_text)+"'"+te[first_pick()+2:]
            command_line_entry.delete('1.0',END)
            command_line_entry.insert(INSERT,te) 

            global command_list_name #these four lines are guesses
            if mode=="drawing_mode":
                command_list_name="draw"
            if mode=="edit_mode":
                command_list_name="edit"


        if parameter=="save_layers":
            written=text1.get("1.0", "end-1c")
            name="files\\"+ str(written)+".txt"
            truth=True
            if path.exists(name):
                truth=messagebox.askyesno("File already exists","Overwrite?")
            if truth==False:#if user doesn't want to overwrite, then go away from the method
                return
            layer_items.save_layers(name)#file will be saved in this method at files\name.txt
            current_file_name=written #saves the name, so if we continue modifying, it remembers the current name
            messagebox.showinfo("information","File was saved as "+name+".")

        if parameter=="save_temp_drawing":
            written=text1.get("1.0", "end-1c")
            name="drawings/"+ str(written)+".txt"
            truth=True
            if path.exists(name):
                truth=messagebox.askyesno("File already exists","Overwrite?")
            if truth==False:#if user doesn't want to overwrite, then go away from the method
                return
            save_drawing_as(temporary_file_string,name)
            messagebox.showinfo("information","Layer was added and drawing was saved as "+name+".")
            temporary_file_string=""#get ready to draw new item
            draw_command_list() #correct list need to be chosen
            temp_turtle.reset() #otherwise temp_turtle drawing are left on the screen
            temp_turtle.shapesize(1.8,1.8,2)
            update_layer_labels()
            layer_items.redraw(t)

        if parameter=="large_commandline":
            command_line_entry.delete('1.0',END)
            command_line_entry.insert(INSERT,text1.get("1.0", "end-1c"))
            text1.delete("1.0", "end-1c")
        open_popup_variable=text1.get("1.0", "end-1c")
        popup.destroy()

    def destroy():
        popup.destroy()



    pen_scale=tk.Scale(popup,from_=1,to=500,orient=HORIZONTAL)

    def set_pensize():
        global temporary_file_string
        temp_turtle.pensize(pen_scale.get())
        temporary_file_string += "ps("+str(pen_scale.get())+")|"
        basic_info()
        popup.destroy()


    
    button = tk.Button(popup, text="Done", command=save_text)
    button.pack()
    exit_button= tk.Button(popup, text="Exit without saving", command=destroy)


    if parameter=="save_temp_drawing":
        text1.config(height=1)
        label1.config(text="Save the drawing")
        button.config(text="Save")
        exit_button.pack()
    if parameter=="save_layers":
        exit_button.pack()            
        text1.config(height=1)
        text1.delete("1.0", "end-1c")
        text1.insert("1.0",current_file_name)#suggest the file name to stay the same as it was before
        label1.config(text="Save the file with name:")
        button.config(text="Save")
    if parameter=="large_commandline":
        label1.config(text="Commands in the commandline")
        exit_button.pack()
        button.config(text="Save modifications")
        text1.delete("1.0", "end-1c")
        text1.insert("1.0",command_line_entry.get("1.0", "end-1c"))
    if parameter=="pensize":
        text1.destroy()
        pen_scale.pack()
        button.config(text="Change pen size",command=set_pensize)     






#this actually draws the matrix /parameter is named as tensor) and saves it to temp...file, it uses columns with indexes x_axis_index and y_axis_index 
def matrix_drawing_orders(tensor,x_axis_index,y_axis_index):
    global db
    global SCALEX,SCALEY,ORIGOX,ORIGOY
    point_list=[]
    vector_component_list=[]
    for i in range(len(tensor)):
        vector_component_list.append(tensor[i])
    for vector in vector_component_list:
        try:
            x_component= float(vector[x_axis_index-1]) #-1 since human don't like 0
            y_component= float(vector[y_axis_index-1])
            point_list.append((x_component,y_component))
        except:
            nothing=0
    pixel_list=[]
    for item in point_list:
        add_dot_to_temp_str(point_to_pixel(item,xscale=SCALEX,yscale=SCALEY,origo_value=(ORIGOX,ORIGOY)))
        
#draws and adds dot to temporary_file_string        
def add_dot_to_temp_str(pixel):
    global temporary_file_string
    temp_turtle.penup()
    temp_turtle.goto(pixel[0],pixel[1])
    temp_turtle.pendown()
    temp_turtle.goto(pixel[0]+1,pixel[1])
    temp_turtle.penup()
    temporary_file_string += "pu()|goto("+str(pixel[0])+","+str(pixel[1])+")|"
    temporary_file_string += "pd()|goto("+str(pixel[0]+1)+","+str(pixel[1])+")|pu()|"
    draw_temporary_file()

#draws a function, the area it is drawn pixel-wise is  (pixminx,pixmaxx) x (pixminy,pixmaxy), scale tells size of the pixel in points
        #precision tells the distance in x-axis in pixels of how far the approximating points are from each other
        #origo_pixel_value tells values of x and y in pixel drawn at origo
        # potential choises for coordinate_mode are ["all,","just function","just axis","axis and lines", "axis, lines and values"]
def draw_function(assignment_str="",origo_value=(ORIGOX,ORIGOY),xscale=SCALEX,yscale=SCALEY,
                  pixminx=-int(QUICK_WIDTH/2),pixmaxx=int(QUICK_WIDTH/2),pixminy=-int(QUICK_HEIGHT/2),pixmaxy=int(QUICK_HEIGHT/2),
                  precision=5,coordinate_mode="just function"):
    global db
    global temporary_file_string
    if coordinate_mode != "just function": #if this is false, no coordinates are drawn
        draw_coordinates(origo_value,xscale,yscale,pixminx,pixmaxx,pixminy,pixmaxy,coordinate_mode)
    if precision<1:
        precision=1
    if coordinate_mode in ["axis","axis and line","axis, lines and values"]:
        return #no function is drawn
    function_points=[]#mathematical points, not pixel-coordinates
    db.remove_function_by_name("temp")#if there is old function with this name, it is deleted
    db.process_all("temp(x)=="+assignment_str)

    for x in range(round(pixminx/precision),round(pixmaxx/precision)):
        xcor=float(x*xscale*precision+origo_value[0])
        addblocker=False
        try:
            ycor=float(db.assign_variables_and_process("temp("+str(float(xcor))+")"))
        except ValueError: #for example taking squareroot of negative number
            addblocker=True
        except ZeroDivisionError:
            addblocker=True
        if addblocker==False:
            function_points.append((xcor,ycor))#probably arguument shold be string but lets try this
    function_pixels=[] #this saves things in pixels
    for point in function_points:
        pixel_x=round(point_to_pixel(point,origo_value,xscale,yscale)[0])
        pixel_y=round(point_to_pixel(point,origo_value,xscale,yscale)[1])
        function_pixels.append((pixel_x,pixel_y))

    drawi=Geometry.Drawing(temporary_file_string)
    for i in range(len(function_pixels)-1):
        end_point1=(int(function_pixels[i][0]),int(function_pixels[i][1]))
        end_point2=(int(function_pixels[i+1][0]),int(function_pixels[i+1][1]))
        thickness=temp_turtle.pensize()
        pencolor=temp_turtle.pencolor()
        pen_down=True
        fillcolor=temp_turtle.fillcolor()
        cond1= end_point1[0] in range(pixminx,pixmaxx) and end_point1[1] in range(pixminy,pixmaxy) 
        cond2= end_point2[0] in range(pixminx,pixmaxx) and end_point2[1] in range(pixminy,pixmaxy)
        new_line=Geometry.Line(end_point1,end_point2,thickness,pencolor,pen_down,True,fillcolor)
        if cond1 or cond2:
            drawi.add_line(new_line)
    temporary_file_string=drawi.from_Drawing_to_temp_string()

    draw_temporary_file()
    #layer_items.redraw(t)
    update_layer_labels()


#draws coordinate axishe area it is drawn pixel-wise is  (pixminx,pixmaxx) x (pixminy,pixmaxy), scale tells size of the pixel in points
# possible coordinate modes are ["just function","just axis","axis and lines", "axis, lines and values"]
def draw_coordinates(origo_value=(ORIGOX,ORIGOY),xscale=SCALEX,yscale=SCALEY,
                     pixminx=-int(QUICK_WIDTH/2),pixmaxx=int(QUICK_WIDTH/2),pixminy=-int(QUICK_HEIGHT/2),pixmaxy=int(QUICK_HEIGHT/2),
                     coordinate_mode="just axis"):
    global db
    global temporary_file_string
    global writefont,writefontstyle,writefontsize
    draw_value_lines=False
    show_value_text=False
    if coordinate_mode in ["axis and lines", "axis, lines and values"]:
        draw_value_lines=True
    if coordinate_mode in ["axis, lines and values"]:
        show_value_text=True
    axis_color=(0,0,0)
    coordinate_line_color=(0.2,0.2,1)
    dim_line_color=(0.7,0.7,1)
    ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
    drawi=Geometry.Drawing(temporary_file_string)
    origo_pixel=point_to_pixel((0,0),origo_value,xscale,yscale)#location of pixel representing origo
    if origo_value[0]>pixminx*xscale and origo_value[0]<pixmaxx*xscale:
        y_axis_line=Geometry.Line((origo_pixel[0],pixminy),(origo_pixel[0],pixmaxy),3,axis_color,True,False,(1,1,1))
        drawi.add_line(y_axis_line)        
    if origo_value[1]>pixminy*yscale and origo_value[1]<pixmaxy*yscale:
        x_axis_line=Geometry.Line((pixminx,origo_pixel[1]),(pixmaxx,origo_pixel[1]),3,axis_color,True,False,(1,1,1))
        drawi.add_line(x_axis_line)
    if  draw_value_lines:#for extra lines
        #first creating vertical lines:
        multipx=FunctionOperator.multiplier_to_next_exponent_of_ten(xscale)*20 #this is going to be the distance of pixels in lines in the coordinate system
        if multipx<80:
            multipx=multipx*2.5
        if multipx<80:
            multipx=multipx*2
        x_increasement=xscale*multipx #tells how much is the point distance of lines in x-direction
        middle_line_x=origo_pixel[0]%multipx #this is a pixel.x-coordinate of the coordinate line going to be drawn closeset to pixel origo
        
        multipy=FunctionOperator.multiplier_to_next_exponent_of_ten(yscale)*20 #this is going to be the distance of pixels in lines in the coordinate system
        if multipy<80:
            multipy=multipy*2.5
        if multipy<80:
            multipy=multipy*2
        y_increasement=yscale*multipy #tells how much is the point distance of lines in x-direction
        middle_line_y=origo_pixel[1]%multipy #this is a pixel y-coordinate of the coordinate line going to be drawn closest to pixel origo         

        for i in range(int(pixminx/multipx)-2,int(pixmaxx/multipx)+1):
            xpos=int(middle_line_x+i*multipx)
            if is_it_in_box((xpos,(pixminy+pixmaxy)/2),pixminx,pixminy,pixmaxx,pixmaxy):
                vertical_line=Geometry.Line((xpos,pixminy),(xpos,pixmaxy),1,coordinate_line_color,True,False,(1,1,1))
                drawi.add_line(vertical_line)
            divisions=5
            for j in range(1,divisions):
                if is_it_in_box((xpos+int(j*multipx/5),(pixminx+pixmaxx)/2),pixminx,pixminy,pixmaxx,pixmaxy):
                    drawi.add_line(Geometry.Line((xpos+int(j*multipx/5),pixminy),(xpos+int(j*multipx/5),pixmaxy),1,dim_line_color,True,False,(1,1,1)))

            if show_value_text: #do we add number telling the value of the line
                rounded_value= round((pixel_to_point((xpos,origo_pixel[1]),origo_value,xscale,yscale)[0])/x_increasement)*x_increasement
                value_string2=FunctionOperator.zero_cut_string(rounded_value,max_nro_of_zeros=0)
                found=False
                if is_it_in_box((xpos,origo_pixel[1]),pixminx,pixminy,pixmaxx,pixmaxy):
                    new_text=Geometry.Writing(axis_color,(xpos,origo_pixel[1]),writefontstyle,writefont,writefontsize,text=value_string2)
                    drawi.add_writing(new_text)
                    found=True
                if found==False:#if x-coordinate axis is not in the graph area
                    rounded_value= round((pixel_to_point((xpos,pixminy),origo_value,xscale,yscale)[0])/x_increasement)*x_increasement
                    value_string3=FunctionOperator.zero_cut_string(rounded_value,max_nro_of_zeros=0)
                    if is_it_in_box((xpos,pixminy),pixminx,pixminy,pixmaxx,pixmaxy):
                        new_text=Geometry.Writing(axis_color,(xpos,pixminy),writefontstyle,writefont,writefontsize,text=value_string3)
                        drawi.add_writing(new_text)
        #then horizontal lines:

        for i in range(int(pixminy/multipy)-2,int(pixmaxy/multipy)+1):
            ypos=int(middle_line_y+i*multipy)
            if is_it_in_box(((pixminx+pixmaxx)/2,ypos),pixminx,pixminy,pixmaxx,pixmaxy):
                horizontal_line=Geometry.Line((pixminx,ypos),(pixmaxx,ypos),1,coordinate_line_color,True,False,(1,1,1))
                drawi.add_line(horizontal_line)
            divisions=5
            for j in range(1,divisions):
                if is_it_in_box(((pixminx+pixmaxx)/2,ypos+int(j*multipy/5)),pixminx,pixminy,pixmaxx,pixmaxy):
                    drawi.add_line(Geometry.Line((pixminx,ypos+int(j*multipy/5)),(pixmaxx,ypos+int(j*multipy/5)),1,dim_line_color,True,False,(1,1,1)))

            if show_value_text: #do we add number telling the value of the line
                rounded_value= round((pixel_to_point((origo_pixel[0],ypos),origo_value,xscale,yscale)[1])/y_increasement)*y_increasement
                value_string2=FunctionOperator.zero_cut_string(rounded_value,max_nro_of_zeros=0)
                found=False
                if is_it_in_box((origo_pixel[0],ypos),pixminx,pixminy,pixmaxx,pixmaxy):
                    new_text=Geometry.Writing(axis_color,(origo_pixel[0],ypos),writefontstyle,writefont,writefontsize,text=value_string2)
                    drawi.add_writing(new_text)
                    found=True
                if found==False:#if x-coordinate axis is not in the graph area
                    rounded_value= round((pixel_to_point((pixminx,ypos),origo_value,xscale,yscale)[1])/x_increasement)*x_increasement
                    value_string3=FunctionOperator.zero_cut_string(rounded_value,max_nro_of_zeros=0)
                    if is_it_in_box((pixminx,ypos),pixminx,pixminy,pixmaxx,pixmaxy):
                        new_text=Geometry.Writing(axis_color,(pixminx,ypos),writefontstyle,writefont,writefontsize,text=value_string3)
                        drawi.add_writing(new_text)

    temporary_file_string=drawi.from_Drawing_to_temp_string()
    draw_temporary_file()
    set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
    update_layer_labels()
    
#test if given box is inside a box    
def is_it_in_box(point,xmin,ymin,xmax,ymax):
    if point[0]<xmin or point[0]>xmax or point[1]<ymin or point[1]>ymax:
        return False
    return True

#given a pixel, returns the coordinates of the point it represents
def pixel_to_point(pixel,origo_value=(ORIGOX,ORIGOY),xscale=SCALEX,yscale=SCALEY):
    point_x=origo_value[0]+xscale*pixel[0]
    point_y=origo_value[1]+yscale*pixel[1]
    return (point_x,point_y)

#given a pixel, returns the coordinates of the point it represents
def point_to_pixel(point,origo_value=(ORIGOX,ORIGOY),xscale=SCALEX,yscale=SCALEY):
    pixel_x=round((-origo_value[0]+point[0])/xscale)
    pixel_y=round((-origo_value[1]+point[1])/yscale)
    return (pixel_x,pixel_y)

#erases the thing located in (x,y), just the top, not the one down to it
def erase_top(x,y):
    global temporary_file_string
    temporary_file_string=Geometry.reduce(temporary_file_string)
    drawi=Geometry.Drawing(temporary_file_string)
    drawi.remove_element_at((int(x),int(y)))
    temporary_file_string=drawi.from_Drawing_to_temp_string()

#erases all things located in (x,y)
def erase_all(x,y):
    global temporary_file_string
    temporary_file_string=Geometry.reduce(temporary_file_string)
    drawi=Geometry.Drawing(temporary_file_string)
    drawi.remove_all_elements_at((int(x),int(y)))
    temporary_file_string=drawi.from_Drawing_to_temp_string()


def open_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def show_popup(file_path):
    
    popup_window = tk.Toplevel(root)
    popup_window.title("User created short-commands")
    
    frame = tk.Frame(popup_window)
    frame.pack(pady=10, padx=10)

    frame2 = tk.Frame(popup_window)
    frame2.pack(pady=9, padx=9)
    
    text_widget = scrolledtext.ScrolledText(frame, width=80, height=20)
    text_widget.pack()
    
    file_content = open_file(file_path)
    text_widget.insert(tk.END, file_content)

    popup_window.geometry("500x400") 



#this draw:s button to be pressed
def button_area():
    global button_info,button_info2,button_info3
    bsize=[int(root_width/4),18]

    for i in range(len(button_info)):
        button_canvas.create_rectangle(i*bsize[0],0,(i+1)*bsize[0],bsize[1],fill="lightgreen")
        button_canvas.create_text(int((i+0.5)*bsize[0]),int(bsize[1]/2),text=button_info[i][0])
        button_canvas.create_rectangle(i*bsize[0],bsize[1],(i+1)*bsize[0],2*bsize[1],fill="lightblue")
        button_canvas.create_text(int((i+0.5)*bsize[0]),int(3*bsize[1]/2),text=button_info2[i][0])
        button_canvas.create_rectangle(i*bsize[0],2*bsize[1],(i+1)*bsize[0],4*bsize[1],fill="orange")
        button_canvas.create_text(int((i+0.5)*bsize[0]),int(5*bsize[1]/2),text=button_info3[i][0])
    #what happens if button area is clicked with left mouse
    def button_area_effects(event):
        x_sector=int(event.x/bsize[0])
        y_sector=int(event.y/bsize[1])
        if y_sector==0:
            button_info[x_sector][1]()
        if y_sector==1:
            button_info2[x_sector][1]()
        if y_sector==2:
            button_info3[x_sector][1]()

    button_canvas.bind("<Button-1>",button_area_effects)#pressing command_entry_canvas should



#updates_layer_data_canvas¨
showmode="normal"# which info are shown in layer_labels
label_starting_index=0 #what is the first layer to be represented in layer_labels
maximum_label_number=10

def update_layer_labels():
    global showmode
    global label_starting_index
    global maximum_label_number
    global turtle_screen_bg_color
    global db
    layer_data_canvas.delete("all")

    total_items=1
    if showmode in ["normal","color"]:
        total_items= len(layer_items.items)-label_starting_index
        if total_items>maximum_label_number:
            total_items=maximum_label_number#show maximum number of ten items
    if showmode =="variables":
        total_items= len(db.variables_as_list())-label_starting_index #I don't know what label_starting_index is, but lets leave it here
        if total_items>maximum_label_number:
            total_items=maximum_label_number#show maximum number of ten items
    if showmode =="functions":
        total_items= len(db.function_list)-label_starting_index #I don't know what label_starting_index is, but lets leave it here
        if total_items>maximum_label_number:
            total_items=maximum_label_number#show maximum number of ten items
    
    #due to human visual system, we want the palette to be with same bgcolor as turtlescreen 
    layer_data_canvas.create_rectangle(0,200,root_width,350,fill=turtle_screen_bg_color)  
    layer_data_canvas.create_rectangle(0,0,root_width,layer_data_constant,fill="lightgrey") #for "buttons" like up   
    layer_data_canvas.create_rectangle(-1+root_width/2,0,1+root_width/2,layer_data_constant,fill="black") #for "buttons" like down   


    for i in range(0,total_items):
        bg_color="white"
        if showmode in ["normal","color"]: #this color choise done here was without if clause before
            bg_color=layer_items.color_code(i+label_starting_index)
        text1=layer_items.item_parameters_to_string(i+label_starting_index,showmode)
        x=0
        y=0+(i+2)*layer_data_constant
        x_1=root_width
        y_1=(i+3)*layer_data_constant
        layer_data_canvas.create_rectangle(x,y-20,x_1,y_1-20,fill=bg_color)
        if showmode in ["normal","color"]:
            layer_data_canvas.create_text(x+(root_width/2),y-10,text=text1) 
        if showmode in ["variables"]:
            center_distance=70 #how far from center in x-axis the text are put
            text_array= text1.split("=")
            layer_data_canvas.create_text(x+(root_width/2)-center_distance,y-10,text=text_array[0])             
            layer_data_canvas.create_text(x+(root_width/2)+center_distance,y-10,text=text_array[1]) 
        if showmode in ["functions"]:
            center_distance=70 #how far from center in x-axis the text are put
            text_array= text1.split("==")
            layer_data_canvas.create_text(x+(root_width/2)-center_distance,y-10,text=text_array[0])             
            layer_data_canvas.create_text(x+(root_width/2)+center_distance,y-10,text=text_array[1])

    if mode=="drawing_mode":#piirrosmoodi
        total_items+=1 #this isn't actually total number of items, since it includes the "button"
        if showmode in ["normal","color"]:
            layer_data_canvas.create_rectangle(0,(total_items+1)*layer_data_constant-20,root_width,(total_items+2)*layer_data_constant-20,fill="yellow")
            layer_data_canvas.create_text(root_width/2,(total_items+1)*layer_data_constant-10,text="Drawing")  
        layer_data_canvas.create_rectangle(3*root_width/4,0,1+3*root_width/4,layer_data_constant-1,fill="black") #for "buttons" like down   
    layer_data_canvas.create_text(7*root_width/8,layer_data_constant-10,text="info") #for "buttons" like down   
    layer_data_canvas.create_rectangle(1*root_width/8,0,1+1*root_width/8,layer_data_constant-1,fill="black") #for "buttons" like down   
    layer_data_canvas.create_text(1*root_width/16,layer_data_constant-10,text="<<<") #for "buttons" like down   
    layer_data_canvas.create_rectangle(2*root_width/8,0,1+2*root_width/8,layer_data_constant-1,fill="black") #for "buttons" like down   
    layer_data_canvas.create_text(3*root_width/16,layer_data_constant-10,text="<<") #for "buttons" like down   
    layer_data_canvas.create_rectangle(-1+3*root_width/8,0,1+3*root_width/8,layer_data_constant-1,fill="black") #for "buttons" like down   
    layer_data_canvas.create_text(5*root_width/16,layer_data_constant-10,text="<") #for "buttons" like down   
    layer_data_canvas.create_rectangle(4*root_width/8,0,1+4*root_width/8,layer_data_constant-1,fill="black") #for "buttons" like down   
    layer_data_canvas.create_text(7*root_width/16,layer_data_constant-10,text=">") #for "buttons" like down  
    layer_data_canvas.create_rectangle(5*root_width/8,0,1+5*root_width/8,layer_data_constant-1,fill="black") #for "buttons" like down   
    layer_data_canvas.create_text(9*root_width/16,layer_data_constant-10,text=">>") #for "buttons" like down    
    layer_data_canvas.create_rectangle(6*root_width/8,0,1+6*root_width/8,layer_data_constant-1,fill="black") #for "buttons" like down  
    layer_data_canvas.create_text(11*root_width/16,layer_data_constant-10,text=">>>") #for "buttons" like down  

    shift_rotate_scale_areas()
    pen_area()
    tip_area()



    #shift area
def shift_rotate_scale_areas():    
    global shift_click_pos
    global shift_click_size
    global distance
    global special_area_mode1,special_area_mode2
    global color_show
    global blueness
    sx=shift_click_pos[0]
    sy=shift_click_pos[1]
    sx1=shift_click_pos[0]+shift_click_size
    sy1=shift_click_pos[1]+shift_click_size
    if special_area_mode1=="local":
        layer_data_canvas.create_rectangle(sx,sy,sx1,sy1,fill="lightgreen")
        layer_data_canvas.create_text (sx+25,sy+15,text="stretch")
        layer_data_canvas.create_line(int((sx+sx1)/2),sy,int((sx+sx1)/2) ,sy1)
        layer_data_canvas.create_line(sx,int((sy+sy1)/2),sx1,int((sy+sy1)/2))
    if special_area_mode1=="global":
        layer_data_canvas.create_rectangle(sx,sy,sx1,sy1,fill="lightgreen")
        layer_data_canvas.create_text (sx+15,sy+15,text="shift")
        layer_data_canvas.create_line(int((sx+sx1)/2),sy,int((sx+sx1)/2) ,sy1)
        layer_data_canvas.create_line(sx,int((sy+sy1)/2),sx1,int((sy+sy1)/2))
    if special_area_mode1=="color":
        global palc
        palc.loc=[sx+5,sy]
        palc.paint_palette(layer_data_canvas)
        
    csx=sx+distance
    csy=sy
    csx1=sx1+distance
    csy1=sy1
    if special_area_mode2=="local":
        layer_data_canvas.create_rectangle(csx,csy,csx1,csy1,fill="yellow")
    if special_area_mode2=="global":
        layer_data_canvas.create_rectangle(csx,csy,csx1,csy1,fill="lightgreen")
    if special_area_mode2 in ["local","global"]:
        layer_data_canvas.create_line(int((csx+csx1)/2),csy,int((csx+csx1)/2) ,csy1)
        layer_data_canvas.create_line(csx,int((csy+csy1)/2),csx1,int((csy+csy1)/2))
        layer_data_canvas.create_text(csx+45,csy+15,text="spin")
        layer_data_canvas.create_oval(csx,csy,csx1,csy1)
        layer_data_canvas.create_oval((3*csx+csx1)/4,(3*csy+csy1)/4,(csx+3*csx1)/4,(csy+3*csy1)/4)
    if special_area_mode2=="color":
        global palf
        palf.loc=[sx+distance+5,sy]
        palf.paint_palette(layer_data_canvas)
#to create an area, which changes the mode and the shifting areas between local and global modes


#choosing size of pen
def pen_area():
    global shift_click_pos
    global shift_click_size
    global distance
    global temp_turtle
    sx=shift_click_pos[0]+40+distance/2
    sy=shift_click_pos[1]
    layer_data_canvas.create_rectangle(sx,sy,sx+20,sy+100,fill="yellow")
    layer_data_canvas.create_text(sx+9,sy-10,text="pen")
    layer_data_canvas.create_polygon([(sx,sy),(sx+10,sy+100),(sx+20,sy)],fill="black")
    layer_data_canvas.create_rectangle(sx-15,sy,sx,sy+50,fill="gray")
    layer_data_canvas.create_text(sx-8,sy+25,text="Tool 1",angle=90)
    layer_data_canvas.create_rectangle(sx+20,sy,sx+35,sy+50,fill="gray")
    layer_data_canvas.create_text(sx+27,sy+25,text="Tool 2",angle=90) 
    if temp_turtle.isdown():
        layer_data_canvas.create_rectangle(sx-15,sy+50,sx,sy+100,fill="black")
    if temp_turtle.isdown()==False:
        layer_data_canvas.create_rectangle(sx-15,sy+50,sx,sy+100,fill="white")
    if temp_turtle.filling():
        layer_data_canvas.create_rectangle(sx+20,sy+50,sx+35,sy+100,fill="red")
    if temp_turtle.filling()==False:
        layer_data_canvas.create_rectangle(sx+20,sy+50,sx+35,sy+100,fill="white")
    
    return [sx+10,sy] #returns a position in teh middle of top of the "meter"

#area for displaying tips for the user
def tip_area():
    global root_width
    global layer_data_height
    tip_text_collection = []
    tip_text_collection.append("In DRAW-mode, you can fast save drawing with ctrl+r")
    tip_text_collection.append("Top drawings lists the drawings you most often use, try clicking one")
    tip_text_collection.append("In DRAW-mode you can add old drawings by 'put', 'place' and 'lay' commands")
    tip_text_collection.append("When drawing canvas is clicked, every command in the line is performed")
    tip_text_collection.append("Separate commands you type with '|'")
    tip_text_collection.append("Variables are saved by 'variable=value' command, e.g. 'x=4'")
    tip_text_collection.append("Functions are saved by 'function'=='expression' command, e.g. 'func(x,y)==x*y+x'")
    tip_text_collection.append("Try fast double clicking of drawing screen, what happens?")
    tip_text_collection.append("In EDIT-mode, operations are performed only on active layers")
    tip_text_collection.append("OPT in EDIT-mode means you can list layernumbers you want to affect")
    tip_text_collection.append("Try changing color with 'red=a' command, where 0<a<1")
    tip_text_collection.append("Type 'IF(min(random(),0.5),0.5,forward(20),forward(-20))|' what happens?")
    tip_text_collection.append("If two first parameters in IF are same number, third parameter is performed")
    tip_text_collection.append("Try changing fillcolor with 'fillred=a' command, where 0<a<1")
    tip_text_collection.append("You can reuse old drawing by #load command")
    tip_text_collection.append("Type 'draw function(sin(x))', or some other function, variable must be x")
    tip_text_collection.append("Type 'drawcoordinates', and then change origo values from options, what happens?")
    tip_text_collection.append("Type 'drawcoordinates', and then change scaler values from options, what happens?")
    tip_text_collection.append("Type 'drawcoordinates', and then change origo values from options, what happens?")
    tip_text_collection.append("Try different tools by pressing Tool1 and Tool2")
    tip_text_collection.append("Red or white area below Tool 2 tells if the pen is filling")
    tip_text_collection.append("Black or white area below Tool 1 tells if the pen is down")
    tip_text_collection.append("ctrl+w let's you write a text")
    tip_text_collection.append("You can change the font y clicking the name of the font")
    tip_text_collection.append("Options: recycling on/off, tells if e.g. PT in goto(PT) is brought back after click")
    tip_of_the_day=tip_text_collection[int(random.random()*len(tip_text_collection))]
    layer_data_canvas.create_rectangle(0,layer_data_height,root_width,layer_data_height-20,fill="white")
    layer_data_canvas.create_text(root_width/2,layer_data_height-10,text=tip_of_the_day,font=("arial",7))

#middle spot coordinates of shift-area
def middle_of_shift_area():
    global shift_click_pos
    global shift_click_size
    global distance
    return [int(shift_click_pos[0]+shift_click_size/2),int(shift_click_pos[1]+shift_click_size/2)]

#middle spot coordinates of scale_rotate-area
def middle_of_scale_rotate_area():
    global shift_click_pos
    global shift_click_size
    global distance
    return [int(shift_click_pos[0]+distance+shift_click_size/2),int(shift_click_pos[1]+shift_click_size/2)]

def is_it_in_shift_area(xcor:int,ycor:int):
    global shift_click_size,special_area_mode1 #special area mode change 14.8. are is bigger in color mode
    
    if special_area_mode1=="color":
        if xcor-middle_of_shift_area()[0]>shift_click_size/2+5:
            return False
        if -xcor+middle_of_shift_area()[0]>shift_click_size/2+5:
            return False
        if ycor-middle_of_shift_area()[1]>shift_click_size/2:
            return False
        if -ycor+middle_of_shift_area()[1]>shift_click_size/2:
            return False
        return True

    if xcor-middle_of_shift_area()[0]>shift_click_size/2:
        return False
    if -xcor+middle_of_shift_area()[0]>shift_click_size/2:
        return False
    if ycor-middle_of_shift_area()[1]>shift_click_size/2:
        return False
    if -ycor+middle_of_shift_area()[1]>shift_click_size/2:
        return False
    return True
    
def is_it_in_scale_area(xcor:int,ycor:int):
    global distance
    new_x=xcor-distance
    return is_it_in_shift_area(new_x,ycor)#this is not a mistake, it assumes that the position of scale are
    #is always going to be 'distance' apart in x-coordinate direction


def is_it_in_mode_area1(xcor:int,ycor:int): 
    topmiddle=pen_area()
    if abs(topmiddle[0]-xcor-18)>8:
        return False
    if abs(topmiddle[1]+25-ycor)>25:
        return False
    return True
    #this is a way to decide in which place clicking changes the mode of areas 

def is_it_in_mode_area2(xcor:int,ycor:int): 
    topmiddle=pen_area()
    if abs(topmiddle[0]-xcor+16)>8:
        return False
    if abs(topmiddle[1]+25-ycor)>25:
        return False
    return True
    #this is a way to decide in which place clicking changes the mode of areas 


#is the location in pen_area
def is_it_in_pen_area(xcor:int,ycor:int):
    topmiddle=pen_area()
    if abs(topmiddle[0]-xcor)>25:
        return False
    if abs(topmiddle[1]+50-ycor)>50:
        return False
    return True



#returns starting and ending position interval [start,end] of last command in command_string. file with given name.
#parameters are included in the interval, command_string is usually going to be temporary_file_string
def last_command_of_type(command_type:str,command_string:str):
    start=command_string.rfind("|"+command_type)+1 #etsii viimeisen esiintymän, palauttaa -1 jos ei löydy
    start2=command_string.rfind("£"+command_type)+1 
    if start2>start:
        start=start2 
    if start==0:
        start=-1#these strange manouver takes care that for example color and fillcolor arent messed up
    l=command_string[start:].find("|")
    end=-1
    if l != 0:
        end=start+l
    if l == 0:
        end=len(command_string)
    return [start,end] #start is -1, if there is no command

#result is a list with elements [x,y,index], x,y is location and index is an index of command when turtle got there
def list_of_goto_points(file_string):
    commands=MemoryHandler.split_the_string(file_string,"|")
    lista=[]
    for i in range(0,len(commands)):
        if commands[i][0:4]=="goto":
            x=int(Commands.nth_parameter(commands[i],0))
            y=int(Commands.nth_parameter(commands[i],1))
            lista.append([x,y,i])
    return lista

#this tells the index of point in object file_string that is closest to the chosen point (x,y)
def index_of_closest_point(x:int,y:int,file_string):
    helpindex=0
    minimumsq=100000000
    lista=list_of_goto_points(file_string)
    for i in range(0,len(lista)):
        sq=(lista[i][0]-x)*(lista[i][0]-x)+(lista[i][1]-y)*(lista[i][1]-y)
        if sq<minimumsq:
            minimumsq=sq
            helpindex=i
    index=0
    if len(lista)>0:
        index=lista[helpindex][2]
    return index

#saves temporaryfile with random name
def random_save():
    global temporary_file_string
    temporary_file_string += "ef()|" #other types of saving also end with this. This corrects the problem with merging drawings
    letters = string.ascii_lowercase
    randomstring=''.join(random.choice(letters)for i in range(0,8))
    save_string_to_file(temporary_file_string,randomstring,"drawings/rsaves")
    layer_items.add_item(0,"objects","rsaves/"+randomstring,[1,1],0,0,0,"active",0,0,0,"",temporary_file_string)
    #"rsaves/"+ was added 25.8.
    temporary_file_string=""
    draw_command_list() #correct list need to be chosen
    temp_turtle.reset() #otherwise temp_turtle drawing are left on the screen
    temp_turtle.shapesize(1.8,1.8,2)
    update_layer_labels()
    layer_items.redraw(t)
    command_line_entry.delete('1.0',END)


#return true if and only if temporary_file is ACTUALLY filling
def is_temp_filling():
    global temporary_file_string
    bfvar=temporary_file_string.rfind("bf()")
    efvar=temporary_file_string.rfind("ef()")
    if bfvar>efvar:
        return True
    return False


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False




#if there is errors in the file_str representing drawing (which usually is temporary_file)
#  this simply takes away the parts of the code with order not working and returns fixed version
def drawing_file_error_fix(file_str):
    def is_float(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
    def is_number(s):
        try:
            int(s)
            return True
        except ValueError:
            return False
    orders=temporary_file_string.strip("£")
    command_list=MemoryHandler.split_the_string(orders,"|")
    parameters=[0,"objects","tempor",[1,1],0,0,0,"drawing",0,0,0,""] #draws unscaled and shifted version, with depth 0
    fixed_str="£"
    for command in command_list:
        keep=False
        command=command.strip("|")
        if command[0:4]=="goto":
            x=Commands.nth_parameter(command,0)
            y=Commands.nth_parameter(command,1)
            if is_number(x) and is_number(y):
                command="goto("+str(x)+","+str(y)+")"
                keep=True 
        if command[0:2]=="ps":
            x=Commands.nth_parameter(command,0)
            if is_number(x):
                command="ps("+str(x)+")"
                keep=True 
        if command=="pd()":
            keep=True
        if command=="pu()":
            keep=True
        if command[0:2]=="co":
            red=Commands.nth_parameter(command,0)[1:]
            green=Commands.nth_parameter(command,1)
            blue=Commands.nth_parameter(command,2)[:-1]
            if is_float(red) and is_float(green) and is_float(blue):
                command="co(["+str(red)+","+str(green)+","+str(blue)+"])"
                keep=True
        if command[0:2]=="fc":
            red=Commands.nth_parameter(command,0)[1:]
            green=Commands.nth_parameter(command,1)
            blue=Commands.nth_parameter(command,2)[:-1]
            if is_float(red) and is_float(green) and is_float(blue):
                command="fc(["+str(red)+","+str(green)+","+str(blue)+"])"
                keep=True
        if command=="bf()":
            keep=True
        if command=="ef()":
            keep=True
        if command[0:6]=="circle":#this might not be used anymore
            x=Commands.nth_parameter(command,0)
            if is_number(x):
                command="circle("+str(x)+")"
                keep=True
        if command[0:2]=="sh":
            x=Commands.nth_parameter(command,0)
            if is_number(x):
                command="sh("+str(x)+")"
                keep=True
        if command[0:2]=="wr": #test to writing is little bit lazy, it might leave unnoticed problems
            style=Commands.nth_parameter(command,0)#esim. "bold"
            fon=Commands.nth_parameter(command,1)#esim. "Calibri"
            fontsize=Commands.nth_parameter(command,2)#esim. "13
            text=Commands.nth_parameter(command,3)
            if is_number(fontsize):
                keep=True

        if keep==True:
            fixed_str += command+"|"
    
    return fixed_str



#after commands like #delete, the temporary file needs to be redrawn
def draw_temporary_file():
    global temporary_file_string
    global temp_turtle
    temp_turtle.reset()
    temp_turtle.shapesize(1.8,1.8,2)
    screen.tracer(0) #testi
    orders=temporary_file_string.strip("£")
    command_list=MemoryHandler.split_the_string(orders,"|")
    parameters=[0,"objects","tempor",[1,1],0,0,0,"drawing",0,0,0,""] #draws unscaled and shifted version, with depth 0
    try:
        for command in command_list:
            command=command.strip("|")
            layer_items.draw_command(command,parameters,temp_turtle) #this uses layer_items even though
        #temporary drawing isn't item yet, which might be a little bit misleading
    except:
        temporary_file_string=drawing_file_error_fix(temporary_file_string)
    if temp_turtle.filling(): # with this user basicly sees what is going to be filled, even though there
        temp_turtle.end_fill() #is not yet given end_fill command
        temp_turtle.begin_fill() #note that both previous and this command are not saved on temp_file
    screen.tracer(1) #let's see if this is taken away, does this stop working?
    screen.tracer(0) #let's see if this is put, does drawing stop working?

      
# this finds where we are heading according to command_string, which can be for example temporary_file_string
def heading_when_moving_to(x:int,y:int, command_string:str): 
    old_x=current_location(command_string)[0] 
    old_y=current_location(command_string)[1]
    heading=0 
    if old_x != x or old_y != y: #so if turtle is moving due to this command
        heading=int(Geometry.angle_to(old_x,old_y,x,y))
    else: #when turtle is still, pick the previous heading
        interval=last_command_of_type("sh",command_string)
        heading= int(Commands.nth_parameter(command_string[interval[0]:interval[1]],0)) 
    return heading

#this should tell where command_string commands lead, when command_string=temp-file, it tells where drawing ends (currently)
def current_location(command_string:str):
    old_x=0 
    old_y=0
    interval=last_command_of_type("goto",command_string)
    if interval[0] != -1:
        int_arguments=FunctionOperator.arguments_in_type(command_string[interval[0]:interval[1]],return_type="int")
        old_x=int_arguments[0]
        old_y=int_arguments[1]
    return [old_x,old_y]

# this tells when we last time started to begin to fill
def last_begin_fill_location(command_str:str):
    startbf=last_command_of_type("bf()",temporary_file_string)[0]
    if startbf==-1:
        return (0,0)
    else:
        return current_location(temporary_file_string[:startbf])


#returns an up or down depending on the upness and downess of the pen after(potential) execution of command_string
def current_up_or_down(command_string:str):
    last_up=last_command_of_type("pu",command_string)
    last_down=last_command_of_type("pd",command_string)
    if last_up>last_down:
        return "up"
    return "down"

#tells the last heading in the command_string, which can be for example temporary_file_string, telling then where temp_turtle is currently heading
def current_heading(command_string):
    heading=0
    interval=last_command_of_type("sh",command_string)
    if interval[0] != -1:
        heading=int(Commands.nth_parameter(command_string[interval[0]:interval[1]],0))
    return heading

#command_string can be example the temporary_file_string, then this gives temp_turtles current pensize
def current_pensize(command_string):
    pensize=0
    interval=last_command_of_type("ps",command_string)
    if interval[0] != -1:
        pensize=int(Commands.nth_parameter(command_string[interval[0]:interval[1]],0))
    return pensize

#this is returned as a string, for example '[0.4,0.26,0.78]'
def current_pencolor(command_string):
    color=[0.5,0.5,0.5]
    interval=last_command_of_type("co(",command_string) #here the '(' is for not to confuse with fillcolor
    if interval[0] != -1:
        color=command_string[interval[0]+3:interval[1]-1]# +3 is for the len("co("), -1 for taking ')' out
    return color

#this is returned as a string, for example '[0.4,0.26,0.78]'
def current_fillcolor(command_string):
    fillcolor=[0.5,0.5,0.5]
    interval=last_command_of_type("fc",command_string)
    if interval[0] != -1:
        fillcolor=command_string[interval[0]+3:interval[1]-1]# +3 is for the len("fc(")-1 for taking ')' out
    return fillcolor

#this gives information about color, pen etc.
def basic_info():
    command_entry_canvas.create_rectangle(0,0,root_width,25,fill="lightgrey")
        #yritetään laittaa näkyville kynän väri:
    if temp_turtle.pencolor()=="black": #bugin esto
        temp_turtle.pencolor([0.0,0.0,0.0])
    color=MemoryHandler.string_to_color(str(temp_turtle.pencolor()))
    r=color[0]
    g=color[1]
    b=color[2]
    hexcol=hexagesimal_color(r,g,b)
    command_entry_canvas.create_rectangle(root_width-40,5,root_width-25,20,fill=hexcol)

        #yritetään laittaa näkyville kynän täyttöväri:
    if temp_turtle.fillcolor()=="black": #bugin esto
        temp_turtle.fillcolor([0.0,0.0,0.0])
    color=MemoryHandler.string_to_color(str(temp_turtle.fillcolor()))
    fr=color[0]
    fg=color[1]
    fb=color[2]
    hexfill=hexagesimal_color(fr,fg,fb)
    command_entry_canvas.create_rectangle(root_width-20,5,root_width-5,20,fill=hexfill)

    result="mode: "
    if mode=="drawing_mode":
        result ="DRAW"
        command_entry_canvas.create_rectangle(11,5,48,20,fill="yellow")
    else:
        result = "EDIT"
        command_entry_canvas.create_rectangle(13,5,46,20,fill="lightgreen")
    command_entry_canvas.create_text(30,12,text=result)
    if temp_turtle.isdown():
        result = "pendown" 
        command_entry_canvas.create_rectangle(58,20,110,22,fill="black")
    else:
        result =" penup"   
    command_entry_canvas.create_text(85,12,text=result)
    result =str(temp_turtle.pensize()) 
    command_entry_canvas.create_text(123,12,text=result)

    #if is_temp_filling(): #old version
    if temp_turtle.filling(): #new version in 7.8.
        result = "  filling"
        command_entry_canvas.create_rectangle(152,5,190,20,fill=hexfill)
    else:
        result = "  not filling"
    command_entry_canvas.create_text(170,12,text=result)

    global writefont,writefontsize,writefontstyle #there was typo 'writefont_style', corrected 16.7.
    font_rep=writefont[0:8] #shorten version for graphics sake
    command_entry_canvas.create_text(238,12,text=font_rep,font=(writefont,10,writefontstyle))
    command_entry_canvas.create_text(285,12,text=writefontsize)
    pen_area()


#this is a function for very special occasion, given layer_indexes as list of strings 'vector_comp_str' 
#this method returns a new list of only those corresponding active layers, since user gives indexes as 1,2,3... not includin 0
#a special +1 trick must be made to recognize correct layernumbers 
def take_unactive_components_away(vector_comp_strs):
    indexstrs_to_pick=[]
    for vector_comp in vector_comp_strs:
        if layer_items.items[int(vector_comp)-1][7]=="active":
            indexstrs_to_pick.append(vector_comp)
    return indexstrs_to_pick

def command_line_repeat(nro_of_repeats:int,x,y):
    for i in range(min(1000,nro_of_repeats)):
        execute_command_line(x,y)

last_x=0
last_y=0
def execute_command_line(x:int,y:int):
    global xcor,ycor
    clear_commandline=False #if commandline should becleared after operations, change this to True
    global temporary_file_string
    global command_list_name #added 20:05,26.6.
    global layer_items
    global t,temp_turtle
    global writefont,writefontsize,writefontstyle
    global cut_points
    global last_x,last_y #when we need to kkonw the last position clicked
    global db
    global label_starting_index
    global end_draw
    end_draw=False#this is changed to True, if we want to draw the file after every command is performed 
    #(it might be drawn inside commands also)

    the_real_commands=command_line_entry.get("1.0", "end-1c")
    array=MemoryHandler.split_the_string(the_real_commands,"|")
    if len(array)>0: #if first command is repeat(NRO), where NRO is some number, then execute_commandline is repeated this many times
        if array[0][0:7]=="repeat(":
            repeats=0
            try:
                repeats=int(array[0][7:-1])
            except:
                return
            command_line_entry.delete('1.0','1.'+str(len(array[0])))
            command_line_repeat(repeats,x,y)
            return

    bring_back_values=None #some operations like paint() lose the values of pensize etc. when temporary_file is drawn at end
    #eg. after one paint pen is drawn up, and next paint does nothing. Values must be returned by saving them in this 'bring_back_balues'
    set_turtle_variables(turtle)
    turtle_key_mode1() #sets what happens when we write 


    pick_variable(int(x),int(y)) 
    if are_there_variables_to_pick():
        return #then execution ends here

    the_real_commands=command_line_entry.get("1.0", "end-1c")
    looped_commands=db.all_loops(the_real_commands)
    the_real_commands=db.process_all(the_real_commands) #this processing does all_loops in the beginning, thats why argument is the_real_commands
    command_line_entry.delete("1.0","end-1c")
    command_line_entry.insert("1.0",looped_commands) 
    last_x=x
    last_y=y
    #in next if clause, it is important use command_line_entry.get("1.0", "end-1c") not the_real_commands, since changing variables, makes trc empty
    if command_line_entry.get("1.0", "end-1c") in ["","write","write|"]  and mode=="drawing_mode": #if there is nothing in the commandline, temp_turtle is "summoned" there
        heading=heading_when_moving_to(int(x),int(y),temporary_file_string)
        temp_turtle.setheading(heading)
        if  the_real_commands in ["write","write|"]:
            temp_turtle.penup() 
            temporary_file_string += "pu()|"
            empty_text_to_add()
        temp_turtle.goto(int(x),int(y))#coordinates are from screenclick
        temporary_file_string += "sh"+"("+str(heading)+")|"
        temporary_file_string += "goto"+"("+str(int(x))+","+str(int(y))+")|"
        draw_temporary_file() 


    global elapsed_time #time between two last clicks on turtle window, added 11.11.
    if elapsed_time<0.4 and mode=="drawing_mode": #this is actually a double click  
        simulate_dragging(True)

    if elapsed_time>0.4: #new click ends dragging simulation   
        simulate_dragging(False)

    if  the_real_commands=="" and mode=="edit_mode":  #in edit mode, it is probably useful that turtle can jump
        layer_number=layer_items.closest_layer(x,y) 
        layer_origo=(0,0)
        something_clicked=layer_number != None and len(layer_items.items)>0
        if something_clicked:
            layer_origo=(layer_items.items[layer_number][5],layer_items.items[layer_number][6])
        if elapsed_time<0.3 and something_clicked: #this is actually a double click
            hide_active()
            layer_items.items[layer_number][7]="active"
            temp_turtle.penup()
            temp_turtle.goto(layer_origo[0],layer_origo[1])#coordinates are from screenclick
            draw_resize_turtles(temp_turtle.xcor(),temp_turtle.ycor())
            update_layer_labels()
            layer_items.redraw(t)
        
        if size_turtle.isvisible()==False and rotate_turtle.isvisible()==False and something_clicked:
            temp_turtle.penup()
            temp_turtle.goto(layer_origo[0],layer_origo[1])#coordinates are from screenclick
            draw_resize_turtles(temp_turtle.xcor(),temp_turtle.ycor())


    draw_command_list() #should get rid off coordinate picking grpahic
    the_real_commands=loop_replaced_command_string(the_real_commands)#this is a distinct operation compared to the command_line_changes
    #done by db.loops(the_real_commands) before
    array=MemoryHandler.split_the_string(the_real_commands,"|")

    if mode=="edit_mode": #when we are editing, not drawing
        for com in array:
            temp_turtle.penup()
            set_turtle_variables(temp_turtle) #sets the values of variables related to turtle in FunctinoDatabase
            arguments=[]
            if FunctionOperator.type_of(com)=="function_with_arguments":
                arguments=FunctionOperator.arguments_of(com)
            are_real_numbers=True #this will be true if all arguments are real numbers
            for arg in arguments:
                if FunctionOperator.is_real(arg)==False:
                    are_real_numbers= False
            float_arguments=[] #these two will be left empty
            int_arguments=[] #if all are arguments are not numbers
            if are_real_numbers:
                for arg in arguments:
                    float_arguments.append(float(arg))
                    int_arguments.append(int(float(arg)))

            if com[0:5] in ["lrot[","lpos[","lvis[","lcol[","lstr"] or com[0:7]=="ldepth[":
                change_layer_variable_parameter(layer_items,com[:com.find("=")],new_value=com[com.find("=")+1:])
                end_draw=True


            if com[0:15]=="deletefunction(":#deletes command given in the parameter
                function_name=arguments[0]
                if messagebox.askyesno("remove function?","Remove a function: "+function_name):
                    message=db.remove_function_by_name(function_name) #removes if can
                if message != None:
                    messagebox.showinfo("Can't remove function",message) #displays a reason why it can't


            if com[0:6]=="scale(":
                if len(arguments)<2:
                    layer_items.scale_active(float_arguments[0])
                else:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[1]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.scale(int(index_str)-1,float(arguments[0])) #-1 as elsewhere
                layer_items.redraw(t) #this redraw must be made otherwise no effect is seen after execute_com... is done
                    #same is true for the following shifts etc.


            if com[0:8]=="rewrite(":
                writetext=arguments[0]
                for i in range(0,len(layer_items.items)):
                    if layer_items.items[i][7]=="active":
                        lyi=layer_items.items[i] #to just shorten notation
                        new_layer_str=layer_items.rewrite_copy(i,writefont,writefontsize,writefontstyle,writetext)
                        letters = string.ascii_lowercase
                        randomstring=''.join(random.choice(letters)for i in range(0,8))
                        save_string_to_file(new_layer_str,randomstring,"drawings")
                        layer_items.add_item(lyi[0],"objects",randomstring,[lyi[3][0],lyi[3][1]],lyi[4],lyi[5],lyi[6],"visible",lyi[8],lyi[9],lyi[10],"",new_layer_str)
                        draw_command_list() #correct list need to be chosen, LETS see if this is a could idea to keep here
                        temp_turtle.reset() #otherwise temp_turtle drawing are left on the screen
                        temp_turtle.shapesize(1.8,1.8,2)
                        update_layer_labels()
                        layer_items.redraw(t)
                layer_items.destroy_active()
                layer_items.redraw(t)

            if com[0:7]=="rotate(":
                if len(arguments)<2:
                    layer_items.rotate_active(int(float(arguments[0])))
                else:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[1]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.rotate(int(index_str)-1,int(arguments[0])) #-1 as elsewhere
                layer_items.redraw(t) #this redraw must be made otherwise no effect is seen after execute_com... is done
                    #same is true for the following shifts etc.

            if com[0:6]=="shift(":
                x_shift,y_shift=None,None
                extraminus=0
                if FunctionOperator.is_real(arguments[0]): #shift given in two arguments 'a,b'
                    x_shift=int(float(arguments[0]))
                    y_shift=int(float(arguments[1]))
                else:#shift in one point arguments '(a,b)'
                    shift_vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[0]))
                    x_shift=int(float(shift_vector[0]))
                    y_shift=int(float(shift_vector[1]))
                    extraminus = -1
                if len(arguments)==2+extraminus:
                    layer_items.shift_active(x_shift,y_shift)
                else:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[2+extraminus]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.shift(int(index_str)-1,x_shift,y_shift) #-1 as elsewhere
                layer_items.redraw(t)

            if com[0:8]=="abs pos(":
                abs_x,abs_y=None,None
                extraminus=0
                if FunctionOperator.is_real(arguments[0]): #shift given in two arguments 'a,b'
                    abs_x=int(float(arguments[0]))
                    abs_y=int(float(arguments[1]))
                else:#shift in one point arguments '(a,b)'
                    abs_vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[0]))
                    abs_x=int(float(abs_vector[0]))
                    abs_y=int(float(abs_vector[1]))
                    extraminus = -1
                if len(arguments)==2+extraminus:
                    layer_items.change_active_layers_parameter("x shift",abs_x)
                    layer_items.change_active_layers_parameter("y shift",abs_y)
                else:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[2+extraminus]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.change_layer_parameter(int(index_str)-1,"x shift",abs_x)
                        layer_items.change_layer_parameter(int(index_str)-1,"y shift",abs_y) #-1 as elsewhere
                layer_items.redraw(t)



            if com[0:10]=="abs color(":
                abs_r,abs_g,abs_b=None,None,None
                extraminus=0
                if FunctionOperator.is_real(arguments[0]): #color given in three arguments 'r,g,b'
                    abs_r=float(arguments[0])
                    abs_g=float(arguments[1])
                    abs_b=float(arguments[2])
                else:#color in one "point" arguments '(r,g,b)'
                    abs_vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[0]))
                    abs_r=float(abs_vector[0])
                    abs_g=float(abs_vector[1])
                    abs_b=float(abs_vector[1])
                    extraminus = -2
                if len(arguments)==3+extraminus:
                    layer_items.change_active_layers_parameter("red",abs_r)
                    layer_items.change_active_layers_parameter("green",abs_g)
                    layer_items.change_active_layers_parameter("blue",abs_b)
                else:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[3+extraminus]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.change_layer_parameter(int(index_str)-1,"red",abs_r)
                        layer_items.change_layer_parameter(int(index_str)-1,"green",abs_g) 
                        layer_items.change_layer_parameter(int(index_str)-1,"blue",abs_b)#-1 as elsewhere
                layer_items.redraw(t)

            if com[0:10]=="abs angle(":
                abs_r=int(arguments[0])

                if len(arguments)==1:
                    layer_items.change_active_layers_parameter("rotation",abs_r)
                else:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[1]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.change_layer_parameter(int(index_str)-1,"rotation",abs_r)#-1 as elsewhere
                layer_items.redraw(t)

            if com[0:7]=="x shift":
                if len(arguments)<2:
                    layer_items.shift_active(int(float(arguments[0])),0)
                else:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[1]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.shift(int(index_str)-1,int(arguments[0]),0) #-1 as elsewhere
                layer_items.redraw(t)


            if com[0:7]=="y shift":
                if len(arguments)<2:
                    layer_items.shift_active(0,int(float(arguments[0])))
                else:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[1]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.shift(int(index_str)-1,0,int(arguments[0])) #-1 as elsewhere
                layer_items.redraw(t)


            if com[0:12]=="shift color(":
                if len(arguments)==1: #arguments '(r,g,b)'
                    color_vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[0]))
                    layer_items.shift_active_colors(float(color_vector[0]),float(color_vector[1]),float(color_vector[2]))
                if len(arguments)==3: #arguments 'r,g,b'
                    layer_items.shift_active_colors(float(arguments[0]),float(arguments[1]),float(arguments[2]))
                if len(arguments)==2: #arguments '(r,g,b),(indexes)'
                    color_vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[0]))
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[1]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.shift_one_color(int(index_str)-1,float(color_vector[0]),float(color_vector[1]),float(color_vector[2])) #-1 as elsewhere
                if len(arguments)==4:#arguments 'r,g,b,(indexes)'
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[3]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.shift_one_color(int(index_str)-1,float(arguments[0]),float(arguments[1]),float(arguments[2])) #-1 as elsewhere
                layer_items.redraw(t)


            if com[0:10]=="shift red(":
                if len(arguments)<2:
                    layer_items.shift_active_colors(float(arguments[0]),0,0)

                else:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[1]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.shift_one_color(int(index_str)-1,float(arguments[0]),0,0) #-1 as elsewhere
                layer_items.redraw(t)


            if com[0:12]=="shift green(":
                if len(arguments)<2:
                    layer_items.shift_active_colors(0,float(arguments[0]),0)
                else:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[1]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.shift_one_color(int(index_str)-1,0,float(arguments[0]),0) #-1 as elsewhere
                layer_items.redraw(t)

            if com[0:11]=="shift blue(":
                if len(arguments)<2:
                    layer_items.shift_active_colors(0,0,float(arguments[0]))
                else:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[1]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.shift_one_color(int(index_str)-1,0,0,float(arguments[0])) #-1 as elsewhere
                layer_items.redraw(t)
    

            if com[0:5]=="spin(": #first point is the one that does not rotate, second point moves to third point
                extraminus=0
                origo_x,origo_y,x_2,y_2,x_3,y_3=None,None,None,None,None,None

                if len(arguments) in [6,7]:
                    origo_x=int(float(arguments[0]))
                    origo_y=int(float(arguments[1]))
                    x_2=int(float(arguments[2]))
                    y_2=int(float(arguments[3]))
                    x_3=int(float(arguments[4]))
                    y_3=int(float(arguments[5]))

                if len(arguments) in [3,4]:
                    origo_comps=FunctionOperator.vector_components(arguments[0])
                    point2_comps=FunctionOperator.vector_components(arguments[1])
                    point3_comps=FunctionOperator.vector_components(arguments[2])
                    origo_x=int(float(origo_comps[0]))
                    origo_y=int(float(origo_comps[1]))
                    x_2=int(float(point2_comps[0]))
                    y_2=int(float(point2_comps[1]))
                    x_3=int(float(point3_comps[0]))
                    y_3=int(float(point3_comps[1]))

                if len(arguments) in [3,6]:
                    layer_items.spin_active(origo_x,origo_y,x_2,y_2,x_3,y_3)
                
                if len(arguments) in [4,7]:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[-1]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.spin_one(int(index_str)-1,origo_x,origo_y,x_2,y_2,x_3,y_3) #-1 as elsewhere
                layer_items.redraw(t)

            if com[0:8]=="horizon(":
                if len(arguments)==3:
                    layer_items.horizon(int(float(arguments[0])),[int(float(arguments[1])),int(float(arguments[2]))])
                if len(arguments)==2:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[-1]))
                    layer_items.horizon(int(float(arguments[0])),[int(float(vector[0])),int(float(vector[1]))])
                layer_items.redraw(t)
            if com[0:15]=="depth to scale(": #schanges the scale to correlate with depth. Closer to the depth is to *x the larger it gets  
                layer_items.depth_to_scale(int(float(arguments[0])))
                layer_items.redraw(t)
            if com[0:8]=="from to(":#objects are scaled according to size they are drawn and as they were looked at depth of 1st parameter
                layer_items.moving_depth_to_scale(int(float(arguments[0])),int(float(arguments[1])))#with 2nd parameter being the normal size
            if com[0:15]=="scale to depth(": #schanges the depth to correlate with scale. Closer to the depth is to *x the larger it gets  
                layer_items.scale_to_depth(int(float(arguments[0])))
                layer_items.redraw(t)
            if com[0:9]=="activate(": #all the layers with origo inside the rectangle formed by the points is activated
                xlimits,ylimits=None,None
                if len(arguments)==4:
                    xlimits=[int_arguments[0],int_arguments[1]]
                    ylimits=[int_arguments[2],int_arguments[3]]
                if len(arguments)==2:
                    vector1=FunctionOperator.vector_components(arguments[0])
                    xlimits=[int(float(vector1[0])),int(float(vector1[1]))]
                    vector2=FunctionOperator.vector_components(arguments[0])
                    ylimits=[int(float(vector2[0])),int(float(vector2[1]))]
                if ylimits[1]<ylimits[0]:
                    ylimits=[ylimits[1],ylimits[0]]
                if xlimits[1]<xlimits[0]:
                    xlimits=[xlimits[1],xlimits[0]]
                for i in range(0,len(layer_items.items)):
                    if layer_items.items[i][5] in range(xlimits[0],xlimits[1]) and layer_items.items[i][6] in range(ylimits[0],ylimits[1]):
                        layer_items.items[i][7]="active"
                        show_contours(i)
                command_line_entry.delete('1.0',END)
                layer_items.redraw(t)


            if com[0:12] in ["abs stretch(","rel stretch("]:#stretches current picture, either setting the scale value or multiplying the existing
                #"this produces some times odd results, things getting smaller when should be getting bigger etc."
                stretch_amount=None
                extraminus=0
                if FunctionOperator.is_real(arguments[0]):
                    stretch_amount=(float(arguments[0]),float(arguments[1]))
                else:
                    point1_comps=FunctionOperator.vector_components(arguments[0])
                    stretch_amount=(float(point1_comps[0]),float(point1_comps[1]))
                    extraminus=-1 # if strecthin info is "packed" into a point, there is one less argument


                if len(arguments)<3+extraminus:
                    for i in range(0,len(layer_items.items)):
                        if layer_items.items[i][7]=="active":
                            x_stretch_factor,y_stretch_factor=1,1
                            if com[0:3]=="rel":
                                x_stretch_factor=layer_items.items[i][3][0]
                                y_stretch_factor=layer_items.items[i][3][1]
                            layer_items.items[i][3]=[stretch_amount[0]*x_stretch_factor,stretch_amount[1]*y_stretch_factor]
                else:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[2+extraminus]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        x_stretch_factor,y_stretch_factor=1,1
                        if com[0:3]=="rel":
                            x_stretch_factor=layer_items.items[int(index_str)-1][3][0]
                            y_stretch_factor=layer_items.items[int(index_str)-1][3][1]
                        layer_items.items[int(index_str)-1][3]=[stretch_amount[0]*x_stretch_factor,stretch_amount[1]*y_stretch_factor]
                update_layer_labels()
                layer_items.redraw(t)
            
            if com[0:4]=="copy":
                layer_items.copy_active()
                layer_items.redraw(t)
                update_layer_labels()

            if com[0:7]=="destroy":
                layer_items.destroy_active()
                t.clear() #en ole varma onko tämä hyvä vai ei
                layer_items.redraw(t)
                label_starting_index=0 #perhaps this removes a bug. Layers did not show after destroying most of them.
                update_layer_labels()
            if com[0:6]=="depth(":
                depth=int(arguments[0])
                if len(arguments)<2:
                    layer_items.depth_active(depth)
                else:
                    vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[1]))
                    vector=take_unactive_components_away(vector)
                    for index_str in vector:
                        layer_items.depth(int(index_str)-1,int(float(arguments[0])))#-1 for human distaste of 0
                layer_items.redraw(t)
                update_layer_labels()
                basic_info()
            if com[0:5]=="load(":
                filename=str(Commands.nth_parameter(com,0))
                filetext= layer_items.load_file_as_string(filename,"drawings")
                layer_items.add_item(0,"objects",filename,[1,1],0,0,0,"active",0,0,0,"",filetext)
                layer_items.redraw(t)
                update_layer_labels()
                popular_drawings.popularity_bonus(filename+".txt")
            if  com[0:4]=="put(":
                drawin=Commands.nth_parameter(com,0)
                temp_turtle.goto(x, y)
                instructions=""
                with open("drawings/"+drawin+".txt","r") as file:
                    instructions=file.read()
                layer_items.add_item(0,"objects",drawin,[1,1],0,int(x),int(y),"active",0,0,0,"",instructions)
                layer_items.redraw(t)
                update_layer_labels()
                popular_drawings.popularity_bonus(drawin+".txt")

            if com[0:6]=="place(":
                filename=arguments[0]
                coords=None
                if len(arguments)==3:
                    coords=(int(float(arguments[1])),int(float(arguments[2])))
                if len(arguments)==2:
                    coord_comps=FunctionOperator.vector_components(arguments[1])
                    coords=(int(float(coord_comps[0])),int(float(coord_comps[1])))
                instructions=""
                with open("drawings/"+filename+".txt","r") as file:
                    instructions=file.read()
                layer_items.add_item(0,"objects",filename,[1,1],0,coords[0],coords[1],"active",0,0,0,"",instructions)
                layer_items.redraw(t)
                update_layer_labels()
                popular_drawings.popularity_bonus(filename+".txt")


            if  com[0:6]=="putD3(":
                filename=arguments[0]
                vector=FunctionOperator.vector_components(FunctionOperator.vectorise(arguments[1]))
                pos2dx=int(float(vector[0]))
                pos2dy=int(float(vector[1]))
                depth=int(float(arguments[2]))
                scalef=0
                if depth<100: #random decision that 100 is the point from where we are looking
                    scalef=100/(100-depth)
                instructions=""
                with open("drawings/"+filename+".txt","r") as file:
                    instructions=file.read()
                layer_items.add_item(depth,"objects",filename,[scalef,scalef],0,int(pos2dx*scalef),int(pos2dy*scalef),"active",0,0,0,"",instructions)
                layer_items.redraw(t)
                update_layer_labels()

            if com== "orientation setup":     
                orientation_popup()
            if com== "activation setup":     
                active_popup()
            if com== "order setup":     
                layerorder_popup()
            if com== "3Dgrid setup":     
                D3_popup()
            if com== "color setup":     
                color_popup()
            if com== "scale setup":     
                scale_popup()
            if com== "depth setup":     
                depth_popup()
            if com== "grid positions":     
                grid_popup()
            if com== "position setup":     
                position_popup()
            if com=="screenshot":
                if current_file_name in ["new_file","my_file"]:
                    messagebox.showinfo("Choose filename","First pick new filename. Screenshots are saved in animations/filename")
                    file_name_popup()
                else:
                    quick_png((-(int(QUICK_WIDTH/2)),int(QUICK_HEIGHT/2)),(int(QUICK_WIDTH/2),-(int(QUICK_HEIGHT/2)))) 

            if com=="add text":
                is_down=temp_turtle.isdown()
                temp_turtle.penup()
                temp_turtle.goto(int(x),int(y))
                spin_turtle.penup()
                if is_down:
                    temp_turtle.pendown()


            if com[0:8]=="giflayer":
                name=str(Commands.nth_parameter(com,0))
                layer_items.items.append([0,"gifs",name,[1,1],0,0,0,"active",0,0,0,""]) #there is not going to be any muumi.txt file for example
                #only the name of the gif is needed for drawing
                layer_items.redraw(t)
                update_layer_labels()
            if com[0:6]=="merge(":
                name=arguments[0]
                merge_active_layers(name)
            if com[0:7]=="change(":
                name=arguments[0]
                instruction_str= layer_items.load_file_as_string(name,"drawings")
                layer_items.add_missing_instruction(name,instruction_str)
                for i in range(0,len(layer_items.items)):
                    if layer_items.items[i][7]=="active":
                        layer_items.items[i][2]=name
                layer_items.redraw(t)
            if com[0:4]=="test":
                testarray=["abc","bbc","edvwv"]
                testarray=add_command_at(testarray,5,"kokof")

            if com[0:9]=="glue file":
                glued=Layers()
                glued.load_layers()
                for i in range(0,len(layer_items.items)):
                    lyi=layer_items.items[i]
                    instructions=layer_items.get_drawing_instruction_str(lyi[2])
                    glued.add_item(lyi[0],lyi[1],lyi[2],lyi[3],lyi[4],lyi[5],lyi[6],lyi[7],lyi[8],lyi[9],lyi[10],lyi[11],instructions)
                layer_items=glued
                layer_items.redraw(t)
                update_layer_labels()

            if com[0:9]=="make_png(":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                temp_turtle.penup()
                png_popup(int_arguments[0],int_arguments[1],int_arguments[2],int_arguments[3])
                command_line_entry.delete('1.0',END)
                the_real_commands= command_line_entry #this seems mistake, how to fix it
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()

    if mode=="drawing_mode": 
        #drawing mode, 
        for com in array:
            set_turtle_variables(temp_turtle) #sets the values of variables related to turtle in FunctinoDatabase
            com=turtle_variable_assignments_to_commands(com,temp_turtle)
            arguments=[]
            if FunctionOperator.type_of(com)=="function_with_arguments":
                arguments=FunctionOperator.arguments_of(com)
            are_real_numbers=True #this will be true if all arguments are real numbers
            for arg in arguments:
                if FunctionOperator.is_real(arg)==False:
                    are_real_numbers= False
            float_arguments=[] #these two will be left empty
            int_arguments=[] #if all are arguments are not numbers
            if are_real_numbers:
                for arg in arguments:
                    float_arguments.append(float(arg))
                    int_arguments.append(int(float(arg)))


            if com[0:15]=="deletefunction(":#deletes command given in the parameter
                function_name=arguments[0]
                what_happened=db.remove_function_by_name(function_name) #removes the function if it can, return str telling did it succeed
                command_line_entry.delete('1.0',END)
                command_line_entry.insert(INSERT,what_happened)
                command_list_name="draw"
                draw_command_list()
            if com=="draw":
                heading=heading_when_moving_to(int(x),int(y),temporary_file_string)
                temp_turtle.setheading(heading)
                temp_turtle.goto(int(x),int(y))
                temporary_file_string += "sh"+"("+str(heading)+")|"
                temporary_file_string += "pd()|goto"+"("+str(int(x))+","+str(int(y))+")|"
                draw_temporary_file()
        #for com in array: #tässä outo bugi, oli japteltu kahteen osaan toteutus
            if com[0:5]=="dots(":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                bring_back_values=ttvalues #these are needed in the end
                x_axis_index=int(arguments[1])
                y_axis_index=int(arguments[2])
                matrix_str=arguments[0]
                matrix_drawing_orders(FunctionOperator.matrix_str_to_actual_matrix(matrix_str),x_axis_index,y_axis_index)
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()

            if com=="relocate":
                temp_turtle.penup()
                heading=heading_when_moving_to(int(x),int(y),temporary_file_string)
                temp_turtle.setheading(heading)#for some reason this and next order were #ied. # was removed 2.8. 
                temp_turtle.goto(int(x),int(y))#coordinates are from screenclick
                temporary_file_string += "sh"+"("+str(heading)+")|"
                temporary_file_string += "pu()|goto"+"("+str(int(x))+","+str(int(y))+")|"
            if com[0:5]=="goto(": #does not change penup or pendown
                heading=heading_when_moving_to(int_arguments[0],int_arguments[1],temporary_file_string)
                temp_turtle.goto(int_arguments[0],int_arguments[1])#coordinates are from screenclick
                temporary_file_string += "sh"+"("+str(heading)+")|"
                temporary_file_string += "goto"+"("+str(int_arguments[0])+","+str(int_arguments[1])+")|"
                draw_temporary_file()
            if com[0:4]=="dot(": #this is kind of pseudo dot, it is a line of length 1
                bring_back_values=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                add_dot_to_temp_str((int_arguments[0],int_arguments[1]))
                #draw_temporary_file()
                

            if com[0:7]=="circle(":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                bring_back_values=ttvalues #these are needed in the end
                center_x,center_y,radius=None,None,None
                if len(arguments)==4:
                    center_x=int(float(arguments[0]))
                    center_y=int(float(arguments[1]))
                    radius=int(Geometry.distance(center_x,center_y,int(float(arguments[2])),int(float(arguments[3]))))
                if len(arguments)==2:
                    center_comps=FunctionOperator.vector_components(arguments[0])
                    outline_comps=FunctionOperator.vector_components(arguments[1])
                    center_x,center_y=int(float(center_comps[0])),int(float(center_comps[1]))
                    radius=int(Geometry.distance(center_x,center_y,int(float(outline_comps[0])),int(float(outline_comps[1]))))
                drawi=Geometry.Drawing(temporary_file_string)
                color_as_list=MemoryHandler.color_tuple_shortener(temp_turtle.pencolor(),3)
                fillcolor_as_list=MemoryHandler.color_tuple_shortener(temp_turtle.fillcolor(),3)
                paramet=[color_as_list,fillcolor_as_list,temp_turtle.pensize(),temp_turtle.isdown(),temp_turtle.filling()]
                drawi.add_circle((center_x,center_y),radius,paramet[2],paramet[0],paramet[1],paramet[3],paramet[4],where="top")
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()
                
            if com[0:4]=="arc(":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                bring_back_values=ttvalues #these are needed in the end
                center_x,center_y,arcstart_x,arcstart_y,arcend_x,arcend_y=None,None,None,None,None,None
                if len(arguments)==3:#prameters in format (x1,y1),(x2,y2)
                    center_str=FunctionOperator.vector_components(arguments[0])
                    center_x,center_y=int(float(center_str[0])),int(float(center_str[1]))
                    arcstart_str=FunctionOperator.vector_components(arguments[1])
                    arcstart_x,arcstart_y=int(float(arcstart_str[0])),int(float(arcstart_str[1]))
                    arcend_str=FunctionOperator.vector_components(arguments[2])
                    arcend_x,arcend_y=int(float(arcend_str[0])),int(float(arcend_str[1]))
                if len(arguments)==6:
                    center_x,center_y=int(float(arguments[0])),int(float(arguments[1]))
                    arcstart_x,arcstart_y=int(float(arguments[2])),int(float(arguments[3]))
                    arcend_x,arcend_y=int(float(arguments[4])),int(float(arguments[5]))
                starting_point=(arcstart_x,arcstart_y)
                angle1=Geometry.angle_to(center_x,center_y,arcstart_x,arcstart_y)
                angle2=Geometry.angle_to(center_x,center_y,arcend_x,arcend_y)
                angle=int(angle2-angle1)%360
                radius=int(Geometry.distance(center_x,center_y,arcstart_x,arcstart_y))
                drawi=Geometry.Drawing(temporary_file_string)
                color_as_list=MemoryHandler.color_tuple_shortener(temp_turtle.pencolor(),3)
                fillcolor_as_list=MemoryHandler.color_tuple_shortener(temp_turtle.fillcolor(),3)
                paramet=[temp_turtle.pensize(),color_as_list,fillcolor_as_list,temp_turtle.isdown()]
                drawi.add_arc((center_x,center_y),radius,starting_point,paramet[0],paramet[1],paramet[2],paramet[3],angle,where="top")
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()

            if com[0:5]=="oval(":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                bring_back_values=ttvalues #these are needed in the end
                center_x,center_y,radius_x,radius_y=None,None,None,None
                if len(arguments)==4:
                    center_x=int(float(arguments[0]))
                    center_y=int(float(arguments[1]))
                    radius_x=int(abs(int(float(arguments[2]))-center_x))
                    radius_y=int(abs(int(float(arguments[3]))-center_y))
                if len(arguments)==2:
                    center_comps=FunctionOperator.vector_components(arguments[0])
                    outline_comps=FunctionOperator.vector_components(arguments[1])
                    center_x,center_y=int(float(center_comps[0])),int(float(center_comps[1]))
                    radius_x=int(abs(int(float(outline_comps[0]))-center_x))
                    radius_y=int(abs(int(float(outline_comps[1]))-center_y))
                drawi=Geometry.Drawing(temporary_file_string)
                color_as_list=MemoryHandler.color_tuple_shortener(temp_turtle.pencolor(),3)
                fillcolor_as_list=MemoryHandler.color_tuple_shortener(temp_turtle.fillcolor(),3)
                paramet=[color_as_list,fillcolor_as_list,temp_turtle.pensize(),temp_turtle.isdown(),temp_turtle.filling()]
                drawi.add_oval((center_x,center_y),radius_x,radius_y,paramet[2],paramet[0],paramet[1],paramet[3],paramet[4],where="top")
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()
            if com[0:8]=="make_png":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                temp_turtle.penup()
                png_popup(int_arguments[0],int_arguments[1],int_arguments[2],int_arguments[3])
                command_line_entry.delete('1.0',END)
                the_real_commands= command_line_entry
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()

            if com[0:10]=="rectangle(":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                bring_back_values=ttvalues #these are needed in the end
                cornerpoint1,cornerpoint2=None,None
                if len(arguments)==4:
                    cornerpoint1=(int(float(arguments[0])),int(float(arguments[1])))
                    cornerpoint2=(int(float(arguments[2])),int(float(arguments[3])))
                if len(arguments)==2:
                    point_comps1=FunctionOperator.vector_components(arguments[0])
                    point_comps2=FunctionOperator.vector_components(arguments[1])
                    cornerpoint1=(int(float(point_comps1[0])),int(float(point_comps1[1])))
                    cornerpoint2=(int(float(point_comps2[0])),int(float(point_comps2[1])))
                drawi=Geometry.Drawing(temporary_file_string)
                color_as_list=MemoryHandler.color_tuple_shortener(temp_turtle.pencolor(),3)
                fillcolor_as_list=MemoryHandler.color_tuple_shortener(temp_turtle.fillcolor(),3)
                paramet=[color_as_list,fillcolor_as_list,temp_turtle.pensize(),temp_turtle.isdown(),temp_turtle.filling()]
                drawi.add_rectangle(cornerpoint1,cornerpoint2,paramet[2],paramet[0],paramet[1],paramet[3],paramet[4],where="top")
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()

            if com=="info":
                drawi=Geometry.Drawing(temporary_file_string)
                messagebox.showinfo("Information",drawi.exactly_info((x,y)))


            
            if com[0:8]=="simplify":
                drawi=Geometry.Drawing(temporary_file_string)
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                size=len(drawi.polygon_list())
                for i in range(0,10):
                    size_now=len(drawi.polygon_list())
                    poly=drawi.polygon_list()[int(size_now*random.random())]
                    drawi.merge_by_color(poly,0.3)
                    temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
            if com[0:5]=="photo":
                photo_popup()
            if com[0:9]=="animation":
                animation_popup()
            if com=="screenshot":
                if current_file_name in ["new_file","my_file"]:
                    messagebox.showinfo("Choose filename","First pick new filename. Screenshots are saved in animations/filename/")
                    file_name_popup()
                else:
                    quick_png((-(int(QUICK_WIDTH/2)),int(QUICK_HEIGHT/2)),(int(QUICK_WIDTH/2),-(int(QUICK_HEIGHT/2)))) 

            if com[0:7]=="cartoon":
                cartoon_popup()
            if com[0:7]=="pircle(":#circle that is actually large polygon
                radius=int_arguments[0]
                l=round(math.sqrt(0.5*math.pi*radius))
                tu=round(90/l)
                temp_turtle.pendown()
                temporary_file_string += "pd()|"
                runningangle=tu #how much angle has already changed
                while runningangle<360:
                    temp_turtle.setheading((current_heading(temporary_file_string)+tu)%360) #toivottavasti tämä % antaa modulon
                    temporary_file_string += "sh("+str(int(temp_turtle.heading()))+")|"
                    temp_turtle.forward(l) #there is danger, file parameters are defined usin turtle position
                    #were turtle to move due to some other reason, file would get stupid parameters
                    new_x=int(temp_turtle.xcor())
                    new_y=int(temp_turtle.ycor())
                    temporary_file_string += "goto("+str(new_x)+","+ str(new_y)+")|"
                    runningangle += tu
                finalturn=tu-runningangle+360
                finalmove=int(l*finalturn/tu)
                temp_turtle.setheading((current_heading(temporary_file_string)+finalturn)%360) #toivottavasti tämä % antaa modulon
                temporary_file_string += "sh("+str(int(temp_turtle.heading()))+")|"
                temp_turtle.forward(finalmove) #there is danger, file parameters are defined usin turtle position
                #were turtle to move due to some other reason, file would get stupid parameters
                new_x=int(temp_turtle.xcor())
                new_y=int(temp_turtle.ycor())
                temporary_file_string += "goto("+str(new_x)+","+ str(new_y)+")|"
                draw_temporary_file()

            if com[0:5]=="rect(":
                width=int(Commands.nth_parameter(com,0))
                height=int(Commands.nth_parameter(com,1))

                [cx,cy]=current_location(temporary_file_string)
                h=current_heading(temporary_file_string)
                x1=int(cx+width*math.cos(math.pi*h/180))
                y1=int(cy+width*math.sin(math.pi*h/180))
                h1=h+90
                if h1>360:
                    h1-=360
                x2=int(x1+height*math.cos(math.pi*h1/180))
                y2=int(y1+height*math.sin(math.pi*h1/180))
                h2=h+180
                if h2>360:
                    h2-=360
                x3=int(x2+width*math.cos(math.pi*h2/180))
                y3=int(y2+width*math.sin(math.pi*h2/180))
                h3=h+270
                if h3>360:
                    h3-=360
                temporary_file_string += "pd()|goto("+str(x1)+","+str(y1)+")|"+"sh("+str(h1)+")|"
                temporary_file_string += "goto("+str(x2)+","+str(y2)+")|"+"sh("+str(h2)+")|"
                temporary_file_string += "goto("+str(x3)+","+str(y3)+")|"+"sh("+str(h3)+")|"
                temporary_file_string += "goto("+str(cx)+","+str(cy)+")|"+"sh("+str(h)+")|"
                draw_temporary_file()
            if com[0:8]=="pensize(":
                ps=int_arguments[0]
                temp_turtle.pensize(ps)
                temporary_file_string += "ps"+"("+str(ps)+")|"
                draw_temporary_file()
            if com[0:11]=="setheading(":
                new_heading=int_arguments[0]
                temp_turtle.setheading(new_heading)
                temporary_file_string += "sh"+"("+str(new_heading)+")|"
                draw_temporary_file()
            if com[0:4]=="turn":
                interval=last_command_of_type("sh",temporary_file_string)
                old_heading=0
                if interval[0]==-1:#prevents an error, if there is no setheadin command before
                    old_heading=0
                else:
                    old_heading= int(Commands.nth_parameter(temporary_file_string[interval[0]:interval[1]],0)) 
                new_heading=int_arguments[0]+old_heading
                if new_heading>360:
                    new_heading -=360
                temp_turtle.setheading(new_heading)
                temporary_file_string += "sh"+"("+str(new_heading)+")|"
                draw_temporary_file()
            if com[0:8]=="forward(":
                temp_turtle.forward(int_arguments[0]) #there is danger, file parameters are defined usin turtle position
                #were turtle to move due to some other reason, file would get stupid parameters
                new_x=int(temp_turtle.xcor())
                new_y=int(temp_turtle.ycor())
                temporary_file_string += "pd()|goto("+str(new_x)+","+ str(new_y)+")|"
                draw_temporary_file()
            if com[0:5]=="jump(":
                temp_turtle.penup()
                temp_turtle.forward(int_arguments[0]) #there is danger, file parameters are defined usin turtle position
                #were turtle to move due to some other reason, file would get stupid parameters
                new_x=int(temp_turtle.xcor())
                new_y=int(temp_turtle.ycor())
                temporary_file_string += "pu()|goto("+str(new_x)+","+ str(new_y)+")|"
                draw_temporary_file()
            if com[0:6]=="color(":
                temp_turtle.pencolor(float(arguments[0]),float(arguments[1]),float(arguments[2]))
                temporary_file_string=temporary_file_string+ "co(["+arguments[0]+","+arguments[1]+","+arguments[2]+"])|"
                draw_temporary_file()
            if com[0:10]=="fillcolor(":
                temp_turtle.fillcolor(float(arguments[0]),float(arguments[1]),float(arguments[2]))
                temporary_file_string += "fc(["+arguments[0]+","+arguments[1]+","+arguments[2]+"])|"
                draw_temporary_file()
            if com[0:9]=="contrast(":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                drawi=Geometry.Drawing(temporary_file_string)
                drawi.change_contrast(int_arguments[0],temp_turtle.pencolor())
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()
            if com[0:14]=="draw function(":
                expression=arguments[0]
                pix=int(-QUICK_WIDTH/2 -10)
                pax=int(QUICK_WIDTH/2 +10)
                piy=int(-QUICK_HEIGHT/2-10)
                pay=int(QUICK_HEIGHT/2+10)
                origo_value=(ORIGOX,ORIGOY)
                xscale=SCALEX
                yscale=SCALEY
                draw_function(assignment_str=expression,coordinate_mode="just function",origo_value=origo_value,
                xscale=xscale,yscale=yscale,pixminx=pix,pixmaxx=pax,pixminy=piy,pixmaxy=pay)
   
            if com[0:16]=="draw coordinates":
                #expression=command_line_entry.get("1.0", "end-1c")
                pix=int(-QUICK_WIDTH/2 -10)
                pax=int(QUICK_WIDTH/2 +10)
                piy=int(-QUICK_HEIGHT/2-10)
                pay=int(QUICK_HEIGHT/2+10)
                origo_value=(ORIGOX,ORIGOY)
                xscale=SCALEX
                yscale=SCALEY
                draw_function(coordinate_mode="axis, lines and values",origo_value=origo_value,xscale=xscale,yscale=yscale,
                pixminx=pix,pixmaxx=pax,pixminy=piy,pixmaxy=pay)



            if com[0:7]=="resize(": #resize image to size givenby parameters
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                drawi=Geometry.Drawing(temporary_file_string)
                drawi.resize(int(float(arguments[0])),int(float(arguments[1])))
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()
            
            if com=="center": #puts currently drawn file into center
                drawi=Geometry.Drawing(temporary_file_string)
                drawi.center()
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                basic_info()

            if com[0:10]== "blackwhite":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                drawi=Geometry.Drawing(temporary_file_string)
                drawi.blackwhite()
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()
            if com[0:7]== "filter(": #if parameter is positive, filters out colors further away than the parameter from the pencolor
                #if negative, filters out colors closer to the pencolor
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                drawi=Geometry.Drawing(temporary_file_string)
                color_gap=float_arguments[0]
                drawi.filter([temp_turtle.pencolor()[0],temp_turtle.pencolor()[1],temp_turtle.pencolor()[2]],color_gap)
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()

            if com[0:3]=="cut":
                new_point=(int(x),int(y))
                nro_of_points=len(cut_points)
                if len(pick_points_with_ld_turtle(new_point))>nro_of_points:
                    cut_points=pick_points_with_ld_turtle(new_point)
                else: 
                    cut_by_vertices(cut_points)
                    cut_points=[]
                
            if com[0:4]=="copy":
                new_point=(int(x),int(y))
                nro_of_points=len(cut_points)
                if len(pick_points_with_ld_turtle(new_point))>nro_of_points:
                    cut_points=pick_points_with_ld_turtle(new_point)
                else: 
                    copy_by_vertices(cut_points)
                    cut_points=[]
            
            if com[0:5]=="paste":
                paste((int(x),int(y)))


            if com[0:10]=="shift red(":
                index=int_arguments[0]
                rshift=float_arguments[1]/256 
                changed_coms= shift_color_from(temporary_file_string,index,rshift,0,0)
                temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" 
                draw_temporary_file()

            if com[0:12]=="shift green(":
                index=int_arguments[0]
                gshift=float_arguments[1]/256
                changed_coms= shift_color_from(temporary_file_string,index,0,gshift,0)
                temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" 
                draw_temporary_file()

            if com[0:11]=="shift blue(":
                index=int_arguments[0]
                bshift=float_arguments[1]/256
                changed_coms= shift_color_from(temporary_file_string,index,0,0,bshift)
                temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" 
                draw_temporary_file()


            if com[0:6]=="write(":#it is importan to have "(" since there is a same name function without "|"
                text=arguments[0]
                temporary_file_string += "wr("+writefontstyle+","+writefont+","+str(writefontsize)+","+text+")|"
                draw_temporary_file()


            if com[0:4]=="spin": #first point is the one that does not rotate, ,second point moves to third point
                origo_x,origo_y,x_2,y_2,x_3,y_3=None,None,None,None,None,None
                if len(arguments)==6:
                    origo_x=int_arguments[0]
                    origo_y=int_arguments[1]
                    x_2=int_arguments[2]
                    y_2=int_arguments[3]
                    x_3=int_arguments[4]
                    y_3=int_arguments[6]
                if len(arguments)==3:
                    origo_comps=FunctionOperator.vector_components(arguments[0])
                    point2_comps=FunctionOperator.vector_components(arguments[1])
                    point3_comps=FunctionOperator.vector_components(arguments[2])
                    origo_x,origo_y=int(float(origo_comps[0])),int(float(origo_comps[1]))
                    x_2,y_2=int(float(point2_comps[0])),int(float(point2_comps[1]))
                    x_3,y_3=int(float(point3_comps[0])),int(float(point3_comps[1]))
                z=Geometry.Complex(origo_x,origo_y)
                z2=Geometry.Complex(x_2,y_2)
                z3=Geometry.Complex(x_3,y_3)
                #we proceed by moving the stable point to 0,0 then scaling and rotating and then shifting the stable point back
                if origo_x==x_2 and origo_y==y_2:
                    origo_x +=1 #this should stop dividing by zerp
                temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
                changed_coms=shifted_commands_from(temp_coms,0,-origo_x,-origo_y)
                temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" #added 18.11. same for several places in the next 20 lines
                paramets=Geometry.spin_transformation_parameters(z,z2,z3)
                temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
                changed_coms=scaled_commands_from(temp_coms,0,paramets[0])
                temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|"
                temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
                changed_coms=rotated_commands_from(temp_coms,0,paramets[1])
                temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|"
                temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
                changed_coms=shifted_commands_from(temp_coms,0,origo_x,origo_y)
                temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|"
                draw_temporary_file()
            if com=="begin fill":
                begin_fill()
            if com=="end fill":
                end_fill()
            if com=="pendown":
                temp_turtle.pendown()
                temporary_file_string += "pd()|"
            if com=="penup":
                temp_turtle.penup()
                temporary_file_string += "pu()|"
            if com[0:4]=="put(":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                bring_back_values=ttvalues #these are needed in the end
                filename=arguments[0]
                file_drawings= layer_items.load_file_as_string(filename,"drawings")
                drawi=Geometry.Drawing(file_drawings)#these three lines
                drawi.shift(int(x),int(y))#were added 11.11.
                file_drawings=drawi.from_Drawing_to_temp_string()#to enable shifting loaded file
                temporary_file_string += file_drawings.strip("£") #there used to be +"|" it was removed 23.2. due to bug 
                draw_temporary_file() #this should make the temporary turtle to draw the file
                popular_drawings.popularity_bonus(filename+".txt")
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
            if com[0:4]=="lay(":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                bring_back_values=ttvalues #these are needed in the end
                filename=arguments[0]
                file_drawings= layer_items.load_file_as_string(filename,"drawings")
                drawi=Geometry.Drawing(file_drawings)#these three lines
                coords=(temp_turtle.xcor(),temp_turtle.ycor())
                drawi.shift(coords[0],coords[1])#were added 11.11.
                file_drawings=drawi.from_Drawing_to_temp_string()#to enable shifting loaded file
                temporary_file_string += "pu()|goto("+str(coords[0])+","+str(coords[1])+")|"+file_drawings.strip("£")
                draw_temporary_file() #this should make the temporary turtle to draw the file
                popular_drawings.popularity_bonus(filename+".txt")    
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])        
            if com[0:6]=="place(":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                bring_back_values=ttvalues #these are needed in the end
                filename=arguments[0]
                coords=None
                if len(arguments)==3:
                    coords=(int(float(arguments[1])),int(float(arguments[2])))
                if len(arguments)==2:
                    coord_comps=FunctionOperator.vector_components(arguments[1])
                    coords=(int(float(coord_comps[0])),int(float(coord_comps[1])))
                file_drawings= layer_items.load_file_as_string(filename,"drawings")
                drawi=Geometry.Drawing(file_drawings)#these three lines
                drawi.shift(coords[0],coords[1])#were added 11.11.
                file_drawings=drawi.from_Drawing_to_temp_string()#to enable shifting loaded file
                temporary_file_string += "pu()|goto("+str(coords[0])+","+str(coords[1])+")|"+file_drawings.strip("£")+"pu()|"
                draw_temporary_file() #this should make the temporary turtle to draw the file
                popular_drawings.popularity_bonus(filename+".txt")            
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])

            if com[0:10]=="transpose(":
                print("try to do later, this is a little problematic, since the transposed value doesn't do anything in itself")
                print("it must be saved as a variable etc")


            if com[0:5]=="save(":
                filename= arguments[0]
                temporary_file_string += "ef()|"
                if save_string_to_file(temporary_file_string,filename,"drawings"): #this is controversial programming
                    # the saving is done already in if statement, if the statement is true
                    realname=filename_without_subdir(filename,"drawings") #Lisätty 20.7.
                    create_mini_image(filename,"drawings/"+filename)
                    layer_items.add_item(0,"objects",filename,[1,1],0,0,0,"active",0,0,0,"",temporary_file_string)
                    temporary_file_string=""
                    draw_command_list() #correct list need to be chosen
                    temp_turtle.reset() #otherwise temp_turtle drawing are left on the screen
                    temp_turtle.shapesize(1.8,1.8,2)
                    update_layer_labels()
                    layer_items.redraw(t)
                    command_line_entry.delete('1.0',END)
                    the_real_commands= command_line_entry
                    #the rest is not so important
                    temp_turtle.color(colorchooser.askcolor()[1]) 
                    temp_turtle.fillcolor(colorchooser.askcolor()[1])
                    col1=str(MemoryHandler.color_tuple_shortener(temp_turtle.pencolor(),3)) #NOTE not yet tested
                    col2=str(MemoryHandler.color_tuple_shortener(temp_turtle.fillcolor(),3))#NOTE not yet tested
                    temporary_file_string += "£co("+ col1+")|"
                    temporary_file_string += "fc("+ col2+")|" #these initiate colors
                    temporary_file_string += "sh(0)|" #normal heading
                    temporary_file_string += "ps(5)|" #standard pensize
                    temporary_file_string += "pu()|" #no extra lines made
                    temporary_file_string += "goto(0,0)|" #start position is also needed to be added
                    temporary_file_string += "pd()|" #so that things will be painted unless otherwise stated
                    temp_turtle.setheading(0)
                    temp_turtle.pensize(5)
                    #clear_commandline=True

            if com[0:5]=="rsave":
                random_save()     
                temp_turtle.color(colorchooser.askcolor()[1]) 
                temp_turtle.fillcolor(colorchooser.askcolor()[1])
                col1=str(MemoryHandler.color_tuple_shortener(temp_turtle.pencolor(),3)) #NOTE not yet tested
                col2=str(MemoryHandler.color_tuple_shortener(temp_turtle.fillcolor(),3))#NOTE not yet tested
                temporary_file_string += "£co("+ col1+")|"
                temporary_file_string += "fc("+ col2+")|" #these initiate colors
                temporary_file_string += "sh(0)|" #normal heading
                temporary_file_string += "ps(5)|" #standard pensize
                temporary_file_string += "pu()|" #no extra lines made
                temporary_file_string += "goto(0,0)|" #start position is also needed to be added
                temporary_file_string += "pd()|" #so that things will be painted unless otherwise stated
                temp_turtle.setheading(0)
                temp_turtle.pensize(5)
                #clear_commandline=True
          
            if com[0:7]=="delete(":
                new_tempor=temporary_file_string[:-1] #ottaa lopusta pois sen viivain
                deletes=int(Commands.nth_parameter(com,0))
                for i in range(0,deletes):
                    index=new_tempor.rfind("|")
                    new_tempor=temporary_file_string[0:index]
                temporary_file_string=new_tempor+"|"
                draw_temporary_file() #this should make the temporary turtle to draw the file
            
            if com=="pick color":
                origsize=temp_turtle.pensize()
                drawi=Geometry.Drawing(temporary_file_string)
                cobject=drawi.exactly_where_we_are((int(x),int(y))) 
                color_to_add=""
                if cobject.__class__.__name__ == "Line":#hwe take the color from the line if pen is down.
                    new_color=(float(cobject.pencolor[0]),float(cobject.pencolor[1]),float(cobject.pencolor[2]))
                    if temp_turtle.isdown():
                        temp_turtle.pencolor(new_color)
                        new_color=temp_turtle.pencolor()
                        temporary_file_string += "co(["+str(new_color[0])[0:5]+","+str(new_color[1])[0:5]+","+str(new_color[2])[0:5]+"])|"
                    if temp_turtle.filling():  
                        temp_turtle.fillcolor(new_color)
                        temporary_file_string += "fc(["+str(new_color[0])[0:5]+","+str(new_color[1])[0:5]+","+str(new_color[2])[0:5]+"])|"

                if cobject.__class__.__name__ == "Polygon":#hwe take the color from the line if pen is down.
                    new_color=(float(cobject.inside_color[0]),float(cobject.inside_color[1]),float(cobject.inside_color[2]))
                    if temp_turtle.isdown():
                        temp_turtle.pencolor(new_color) 
                        new_color=temp_turtle.pencolor()
                        temporary_file_string += "co(["+str(new_color[0])[0:5]+","+str(new_color[1])[0:5]+","+str(new_color[2])[0:5]+"])|"
                    if temp_turtle.filling():
                        temp_turtle.fillcolor(new_color) 
                        temporary_file_string += "fc(["+str(new_color[0])[0:5]+","+str(new_color[1])[0:5]+","+str(new_color[2])[0:5]+"])|"
                temp_turtle.pensize(origsize)
                draw_temporary_file()
                basic_info()

            if com=="change color":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                bring_back_values=ttvalues #these are needed in the end
                drawi=Geometry.Drawing(temporary_file_string)
                cobject=drawi.where_we_are((int(x),int(y))) 
                currentisfilling=temp_turtle.filling()
                contour_size=temp_turtle.pensize()
                contour_color=[temp_turtle.pencolor()[0],temp_turtle.pencolor()[1],temp_turtle.pencolor()[2]]
                currentfillcolor=[temp_turtle.fillcolor()[0],temp_turtle.fillcolor()[1],temp_turtle.fillcolor()[2]]
                downness=temp_turtle.isdown()
                if cobject.__class__.__name__ == "Line":#here we actually change just one line, nothing happens if pen is not down.
                    if downness:
                        cobject.set_pencolor(contour_color)
                if cobject.__class__.__name__ == "Polygon":#here we actually change just one line, nothing happens if pen is not down.
                    if currentisfilling:
                        cobject.set_inside_color(currentfillcolor)
                    if downness:
                        cobject.set_pencolor(contour_color)
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file() #this should make the temporary turtle to draw the file
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()

            if com[0:14]=="change pensize":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                bring_back_values=ttvalues #these are needed in the end
                drawi=Geometry.Drawing(temporary_file_string)
                cobject=drawi.where_we_are((int(x),int(y))) 
                currentisfilling=temp_turtle.filling()
                pensize=temp_turtle.pensize()
                downness=temp_turtle.isdown()
                if cobject.__class__.__name__ == "Line":#here we actually change just one line, nothing happens if pen is not down.
                    if downness:
                        cobject.set_thickness(pensize)
                if cobject.__class__.__name__ == "Polygon":
                    for line in cobject.lines: #changed 25.8. now we should be able to click line even from "outside part" of polygon
                        line.set_thickness(pensize)
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file() #this should make the temporary turtle to draw the file
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()

            if com[0:5]=="paint": 
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                bring_back_values=ttvalues #these are needed in the end
                temporary_file_string=Geometry.reduce(temporary_file_string)
                drawi=Geometry.Drawing(temporary_file_string)
                cobject=drawi.exactly_where_we_are((int(x),int(y)))
                currentisfilling=temp_turtle.filling()
                contour_size=temp_turtle.pensize()
                contour_color=[temp_turtle.pencolor()[0],temp_turtle.pencolor()[1],temp_turtle.pencolor()[2]]
                currentfillcolor=[temp_turtle.fillcolor()[0],temp_turtle.fillcolor()[1],temp_turtle.fillcolor()[2]]
                downness=temp_turtle.isdown()
                if cobject== None:
                    (width,height)=(800,600) #size of "helping png" int(x),int(y) will be in the middle of this
                    topleft=(int(x-width/2),int(y+height/2))
                    spin_turtle.pencolor(turtle_screen_bg_color) #we don't care about the turtle, we just use it to change color_format
                    bg_color=spin_turtle.pencolor() 
                    PngMaker.draw_drawing(temporary_file_string,width,height,topleft,bg_color,save_name="pngs\\"+"new paint",style="mincontour")
                    #changed from "new paint" to "pngs\\"+"new paint" in 14.11. due to changes in PngMaker.draw_drawing
                    #filling color is chosen randomly in the next polygon makin method, it is not displayed in the picture
                    poly=PngMaker.paint_area("pngs//new paint.png","pngs//new paint.png",(int(width/2),int(height/2)),(50,50,0),3)
                    if currentisfilling:
                        poly.inside_color=currentfillcolor
                    poly.set_line_visibity(downness)
                    if downness:
                        poly.set_line_thickness(contour_size)
                        poly.set_pencolor(contour_color)

                    poly.flip_y_axis()
                    poly.shift(int(x)-int(width/2),int(y)+int(height/2))
                    if poly.is_inside((int(x),int(y))): #if point clicked is not contoured, then stupid polygon might be drawn without this
                        if currentisfilling:
                            drawi.add_polygon(poly)
                        if currentisfilling==False:
                            lines=poly.disintegrate()
                            drawi.add_linelist(lines)

                if cobject.__class__.__name__== "Polygon":
                    if currentisfilling:
                        cobject.inside_color=currentfillcolor   
                    cobject.set_line_visibity(downness)
                    if downness:
                        cobject.set_line_thickness(contour_size)
                        cobject.set_pencolor(contour_color)       
                if cobject.__class__.__name__== "Line":              
                    if downness:
                        cobject.set_thickness(contour_size)
                        cobject.set_pencolor(contour_color)

                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file() #this should make the temporary turtle to draw the file
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()

            if com[0:6]=="convex": #paint the object and possibly its contours
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                temporary_file_string=Geometry.reduce(temporary_file_string)
                drawi=Geometry.Drawing(temporary_file_string)
                cobject=drawi.where_we_are2((int(x),int(y))) 
                currentfillcolor=[temp_turtle.fillcolor()[0],temp_turtle.fillcolor()[1],temp_turtle.fillcolor()[2]]
                if cobject.__class__.__name__ == "Polygon":
                    drawi.change_fillcolor((int(x),int(y)),currentfillcolor) #if we are already in polygon,
                    #we just change its color, but do not draw new contours. NOTE return boolean AND changrs the fillcolor     
                else:
                    poly=drawi.convex_Polygon((int(x),int(y)),currentfillcolor,0,360)
                    if poly != None:
                        poly.intify()
                        drawi.add_polygon(poly,"top")
                        #adds convex poylgon
                
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file() #this should make the temporary turtle to draw the file
                #last step is to return the original values
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()
            if com[0:9]=="erase top":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                erase_top(int(x),int(y))
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()
                draw_temporary_file()
            if com[0:9]=="erase all":
                #NOTE print("write method to calculate all elements where we exactly are, this should save lot of time,when everything is erased")
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                temporary_file_string=Geometry.reduce(temporary_file_string)
                drawi=Geometry.Drawing(temporary_file_string)
                if drawi.all_where_we_are((int(x),int(y))) != None:
                    erase_all(int(x),int(y))
                    drawi=Geometry.Drawing(temporary_file_string)
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()
            if com[0:5]=="lift(":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                temporary_file_string=Geometry.reduce(temporary_file_string)
                drawi=Geometry.Drawing(temporary_file_string)
                loc=None
                if len(arguments)==1:#prameters in format (x1,y1)
                    point_comps=FunctionOperator.vector_components(arguments[0])
                    loc=(int(float(point_comps[0])),int(float(point_comps[1])))
                if len(arguments)==2:#prameters in format (x1,y1)
                    loc=(int(float(arguments[0])),int(float(arguments[1])))
                if drawi.element_at(loc) != None:
                    drawi.lift(drawi.element_at(loc))
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()
            if com[0:5]=="sink(":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                temporary_file_string=Geometry.reduce(temporary_file_string)
                drawi=Geometry.Drawing(temporary_file_string)
                loc=None
                if len(arguments)==1:#prameters in format (x1,y1)
                    point_comps=FunctionOperator.vector_components(arguments[0])
                    loc=(int(float(point_comps[0])),int(float(point_comps[1])))
                if len(arguments)==2:#prameters in format (x1,y1)
                    loc=(int(float(arguments[0])),int(float(arguments[1])))
                if drawi.element_at(loc) != None:
                    drawi.sink(drawi.element_at(loc))
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()
            if com[0:5]=="join(":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                glue1_loc,glue2_loc=None,None
                if len(arguments)==2:#prameters in format (x1,y1),(x2,y2)
                    point1_comps=FunctionOperator.vector_components(arguments[0])
                    glue1_loc=(int(float(point1_comps[0])),int(float(point1_comps[1])))
                    point2_comps=FunctionOperator.vector_components(arguments[1])
                    glue2_loc=(int(float(point2_comps[0])),int(float(point2_comps[1])))
                if len(arguments)==4:
                    glue1_loc=(int(float(arguments[0])),int(float(arguments[1])))
                    glue2_loc=(int(float(arguments[2])),int(float(arguments[3])))

                temporary_file_string=Geometry.reduce(temporary_file_string)
                drawi=Geometry.Drawing(temporary_file_string)
                drawi.glue(glue1_loc,glue2_loc)
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()

            if com[0:5]=="move(": #moves a vertice close to clicked point to a new location
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                current_loc,new_loc=None,None
                if len(arguments)==2:#prameters in format (x1,y1),(x2,y2)
                    point1_comps=FunctionOperator.vector_components(arguments[0])
                    current_loc=(int(float(point1_comps[0])),int(float(point1_comps[1])))
                    point2_comps=FunctionOperator.vector_components(arguments[1])
                    new_loc=(int(float(point2_comps[0])),int(float(point2_comps[1])))
                if len(arguments)==4:
                    current_loc=(int(float(arguments[0])),int(float(arguments[1])))
                    new_loc=(int(float(arguments[2])),int(float(arguments[3])))
                temporary_file_string=Geometry.reduce(temporary_file_string)
                drawi=Geometry.Drawing(temporary_file_string)
                drawi.move(current_loc,new_loc)
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()

            if com[0:4]=="bend":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                current_loc,new_loc=None,None
                if len(arguments)==2:#prameters in format (x1,y1),(x2,y2)
                    point1_comps=FunctionOperator.vector_components(arguments[0])
                    current_loc=(int(float(point1_comps[0])),int(float(point1_comps[1])))
                    point2_comps=FunctionOperator.vector_components(arguments[1])
                    new_loc=(int(float(point2_comps[0])),int(float(point2_comps[1])))
                if len(arguments)==4:
                    current_loc=(int(float(arguments[0])),int(float(arguments[1])))
                    new_loc=(int(float(arguments[2])),int(float(arguments[3])))
                temporary_file_string=Geometry.reduce(temporary_file_string)
                drawi=Geometry.Drawing(temporary_file_string)
                element=drawi.where_we_are(current_loc)
                drawi.bend(element,new_loc)
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()

            if com[0:5]=="split":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                current_loc,new_loc=None,None
                if len(arguments)==2:#prameters in format (x1,y1),(x2,y2)
                    point1_comps=FunctionOperator.vector_components(arguments[0])
                    current_loc=(int(float(point1_comps[0])),int(float(point1_comps[1])))
                    point2_comps=FunctionOperator.vector_components(arguments[1])
                    new_loc=(int(float(point2_comps[0])),int(float(point2_comps[1])))
                if len(arguments)==4:
                    current_loc=(int(float(arguments[0])),int(float(arguments[1])))
                    new_loc=(int(float(arguments[2])),int(float(arguments[3])))
                temporary_file_string=Geometry.reduce(temporary_file_string)
                drawi=Geometry.Drawing(temporary_file_string)
                element=drawi.where_we_are2(current_loc)
                if element.__class__.__name__=="Polygon":
                    drawi.split_polygon(element,current_loc,new_loc)
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                basic_info()

            if com[0:8]=="polygon(":
                par=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                bring_back_values=par #these are needed in the end
                #temp_turtle.penup()
                #temp_turtle.goto(int_arguments[0],int_arguments[1])#note that this is not yet saved on temp_file
                #temp_turtle.pendown()
                vertice_list=[]#only the coordinates
                line_list=[]#the lines induced by coordinates
                if FunctionOperator.is_real(arguments[0]):
                    for i in range(int(len(arguments)/2)):
                        coordinates=(int(float(arguments[2*i])),int(float(arguments[2*i+1])))
                        vertice_list.append(coordinates)
                else:
                    for i in range(len(arguments)):
                        coordinates_str=FunctionOperator.vector_components(arguments[i])
                        vertice_list.append((int(float(coordinates_str[0])),int(float(coordinates_str[1]))))

                for i in range(len(vertice_list)-1):
                    line_list.append(Geometry.Line(vertice_list[i],vertice_list[i+1],par[0],par[1],par[2],par[3],par[4]))
                line_list.append(Geometry.Line(vertice_list[-1],vertice_list[0],par[0],par[1],par[2],par[3],par[4]))
                #this is a modification, used to be just line_list vertice_list[0] used to be vertice_list[i+1]
                drawi=Geometry.Drawing(temporary_file_string)
                poly=Geometry.Polygon()
                poly.lines=line_list
                poly.inside_color=temp_turtle.fillcolor()
                drawi.add_polygon(poly,"top")
                temporary_file_string=drawi.from_Drawing_to_temp_string()
                draw_temporary_file()
                set_turtle_values(temp_turtle,par[0],par[1],par[2],par[3],par[4])
                basic_info()

            if com[0:4]=="line":
                ttvalues=always_asked_parameters(temp_turtle) #after drawing this values will be returned
                bring_back_values=ttvalues #these are needed in the end
                arguments=FunctionOperator.arguments_of(com)
                temp_turtle.pendown()
                drawi=Geometry.Drawing(temporary_file_string)
                point1,point2=None,None
                if len(arguments)==2:#prameters in format (x1,y1),(x2,y2)
                    point1_comps=FunctionOperator.vector_components(arguments[0])
                    point1=(int(float(point1_comps[0])),int(float(point1_comps[1])))
                    point2_comps=FunctionOperator.vector_components(arguments[1])
                    point2=(int(float(point2_comps[0])),int(float(point2_comps[1])))
                if len(arguments)==4:
                    point1=(int(float(arguments[0])),int(float(arguments[1])))
                    point2=(int(float(arguments[2])),int(float(arguments[3])))
                if len(arguments) in [2,4]:#prameters in format (x1,y1,x2,y2)
                    par=always_asked_parameters(temp_turtle)
                    drawi.add_line(Geometry.Line(point1,point2,par[0],par[1],par[2],par[3],par[4]))
                    temporary_file_string=drawi.from_Drawing_to_temp_string()
                    draw_temporary_file()
                    set_turtle_values(temp_turtle,ttvalues[0],ttvalues[1],ttvalues[2],ttvalues[3],ttvalues[4])
                    basic_info()

    if clear_commandline==True:
        command_line_entry.delete('1.0',END)
    if RECYCLING_ON:
        recycle() #this e.g. turn line(3,4,5,6) ->line(PT,PT) or move(23,3,34,23) -> move(PT,PT) etc. so that user can pick the points again

    if SCREENSHOTS_ON:
        if current_file_name in ["new_file","my_file"]:
            messagebox.showinfo("Choose filename","First pick new filename. Screenshots are saved in animations/filename/")
            file_name_popup()
        else:
            quick_png((-(int(QUICK_WIDTH/2)),int(QUICK_HEIGHT/2)),(int(QUICK_WIDTH/2),-(int(QUICK_HEIGHT/2)))) 


    draw_command_list()
    temporary_file_string=Geometry.reduce(temporary_file_string)#added 6.8.
    spin_turtle.reset()
    global past
    past[4]=past[3]
    past[3]=past[2]
    past[2]=past[1]
    past[1]=past[0]
    past[0]=temporary_file_string
    global layer_past
    layer_past[4]=layer_past[3]
    layer_past[3]=layer_past[2]
    layer_past[2]=layer_past[1]
    layer_past[1]=layer_past[0]
    layer_past[0]=layer_items.items_to_string()
    set_turtle_variables(temp_turtle) #these are fir database variables
    basic_info()
    if bring_back_values!= None:
        set_turtle_values(temp_turtle,bring_back_values[0],bring_back_values[1],bring_back_values[2],bring_back_values[3],bring_back_values[4])
    update_layer_labels()
    refresh_all_layer_variables(layer_items)
    if end_draw==True:#for example if we cahnged layer_parameters with commands like ldepth[1]=3, then this is performed
        layer_items.redraw(t)
update_layer_labels()
draw_command_list()

#this turns back PT,COL,VCT etc in commands in command_line_entry, that were once chosen and now we want to be able to pick them again
def recycle():
    array=command_line_entry.get("1.0", "end-1c").split("|")
    new_com_str=""
    for item in array:
        try:
            new_com_str += one_str_recycle(item)+"|"
        except:
            new_com_str=new_com_str
    command_line_entry.delete('1.0',END)
    command_line_entry.insert(INSERT,new_com_str)



def one_str_recycle(com_str):
    recycling_orders=[("line(","line(PT,PT)"),("move(","move(PT,PT)"),("circle(","circle(PT,PT)")]
    recycling_orders +=[("oval(","oval(PT,PT)"),("arc(","arc(PT,PT,PT)"),("dot(","dot(PT)"),("polygon(","polygon(VCT)")]
    recycling_orders +=[("rectangle(","rectangle(PT,PT)"),("bend(","bend(PT,PT)"),("split(","split(PT,PT)"),("join(","join(PT,PT)")]
    recycling_orders +=[("lift(","lift(PT)"),("sink(","sink(PT)"),("goto(","goto(PT)"),("place(","place(FILE,PT)")]
    recycling_orders +=[("abs pos(","abs pos(PT,OPT)"),("abs color(","abs color(RGB,OPT)"),("abs stretch(","abs stretch(SP,OPT)")]
    recycling_orders +=[("abs angle(","abs angle(ANG,OPT)")]
    global db
    arguments=[]
    if FunctionOperator.type_of(com_str)=="function_with_arguments":
        arguments=FunctionOperator.arguments_of(com_str)

    #"KESKEN, argumentteja tarkoitus hyödyntää. Esimerkiksi jokin replacement tehdään vaan jos argumentit ovat lukuja jne."
    are_real_numbers=True #this will be true if all arguments are real numbers
    for arg in arguments:
        if FunctionOperator.is_real(arg)==False:
            are_real_numbers= False
    for r_order in recycling_orders:
        if r_order[0]== com_str[:len(r_order[0])]:
            return r_order[1]
    
    #"add more operations"
    return com_str

#returns all the most asked parameters of turtle state 
def always_asked_parameters(turtle:turtle):
    result= [turtle.pensize(),[turtle.pencolor()[0],turtle.pencolor()[1],turtle.pencolor()[2]]]
    result= result+ [turtle.isdown(),turtle.filling(),[turtle.fillcolor()[0],turtle.fillcolor()[1],turtle.fillcolor()[2]]]
    return result


#sets the turtle values, using always asked parameters for saving and this methodfor loading previously saved values is useful combo
def set_turtle_values(turtle,tpensize:int,tpencolor,tisdown:bool,tfilling:bool,tfillcolor):
    turtle.pensize(tpensize)
    turtle.pencolor(tpencolor)
    if tisdown:
        turtle.pendown()
    else:
        turtle.penup()
    if tfilling:
        turtle.begin_fill()
    else:
        turtle.end_fill()
    turtle.fillcolor(tfillcolor)

#this set values of variables in functiondatabase variables
def set_turtle_variables(turtle):
    global db
    db.add_variable(variable_name="pos",variable_assignment_code=str(turtle.pos()))
    db.add_variable(variable_name="xcor",variable_assignment_code=str(turtle.xcor()))
    db.add_variable(variable_name="ycor",variable_assignment_code=str(turtle.ycor()))
    db.add_variable(variable_name="size",variable_assignment_code=str(turtle.pensize()))
    db.add_variable(variable_name="red",variable_assignment_code=str(turtle.pencolor()[0]))
    db.add_variable(variable_name="green",variable_assignment_code=str(turtle.pencolor()[1]))
    db.add_variable(variable_name="blue",variable_assignment_code=str(turtle.pencolor()[2]))
    db.add_variable(variable_name="col",variable_assignment_code="("+str(turtle.pencolor()[0])+","+str(turtle.pencolor()[1])+","+str(turtle.pencolor()[2])+")")
    db.add_variable(variable_name="redfill",variable_assignment_code=str(turtle.fillcolor()[0]))
    db.add_variable(variable_name="greenfill",variable_assignment_code=str(turtle.fillcolor()[1]))
    db.add_variable(variable_name="bluefill",variable_assignment_code=str(turtle.fillcolor()[2]))
    db.add_variable(variable_name="fillcol",variable_assignment_code="("+str(turtle.fillcolor()[0])+","+str(turtle.fillcolor()[1])+","+str(turtle.fillcolor()[2])+")")

#testing




#if we change variable related to turtle in execute_command, then this is activated and moves turtle and does other stuuff like colorin
def turtle_variable_assignments_to_commands(com,turtle):
    global db
    if FunctionOperator.count("=",com)!=1:
        return com
    if com[:4]=="pos=":
        return db.assign_variables_and_process("goto("+com[4:]+")")
    if com[:5]=="xcor=":
        return db.assign_variables_and_process("goto("+com[5:]+","+str(turtle.ycor())+")")
    if com[:5]=="ycor=":
        return db.assign_variables_and_process("goto("+str(turtle.xcor())+","+com[5:]+")")
    if com[:5]=="size=":
        return db.assign_variables_and_process("pensize("+com[5:]+")")
    if com[:4]=="red=":
        return db.assign_variables_and_process("color("+com[4:]+","+str(turtle.pencolor()[1])+","+str(turtle.pencolor()[2])+")")
    if com[:6]=="green=":
        return db.assign_variables_and_process("color("+str(turtle.pencolor()[0])+","+com[6:]+","+str(turtle.pencolor()[2])+")")
    if com[:5]=="blue=":
        return db.assign_variables_and_process("color("+str(turtle.pencolor()[0])+","+str(turtle.pencolor()[1])+","+com[5:]+")")
    if com[:4]=="col=":#color isn't in variables list but it is indirectly affected by red,green and blue values
        return db.assign_variables_and_process("color"+com[4:])
    if com[:8]=="fillcol=":
        return db.assign_variables_and_process("fillcolor"+com[8:])
    if com[:8]=="redfill=":
        return db.assign_variables_and_process("fillcolor("+com[8:]+","+str(turtle.fillcolor()[1])+","+str(turtle.fillcolor()[2])+")")
    if com[:10]=="greenfill=":
        return db.assign_variables_and_process("fillcolor("+str(turtle.fillcolor()[0])+","+com[10:]+","+str(turtle.fillcolor()[2])+")")
    if com[:9]=="bluefill=":
        return db.assign_variables_and_process("fillcolor("+str(turtle.fillcolor()[0])+","+str(turtle.fillcolor()[1])+","+com[9:]+")")
    return com #if it was some other command, it should be returned unchanged

#this command makes the program to refresh variables telling layer parameters
def refresh_all_layer_variables(layer_object:Layers):
    global db
    abs_depth_vect=[]
    abs_pos_vect=[]
    abs_col_vect=[]
    abs_str_vect=[]
    abs_rot_vect=[]
    abs_vis_vect=[]
    
    for i in range(len(layer_object.items)):
        abs_depth_vect.append((layer_object.get_layer_parameter(i,"depth")))
        xsh_str=layer_object.get_layer_parameter(i,"x shift")
        ysh_str=layer_object.get_layer_parameter(i,"y shift")
        abs_pos_vect.append("("+str(xsh_str)+","+str(ysh_str)+")")
        red_str=str(layer_object.get_layer_parameter(i,"red"))
        green_str=str(layer_object.get_layer_parameter(i,"green"))
        blue_str=str(layer_object.get_layer_parameter(i,"blue"))
        abs_col_vect.append("("+red_str+","+green_str+","+blue_str+")")
        abs_rot_vect.append((layer_object.get_layer_parameter(i,"rotation")))
        x_str=layer_object.get_layer_parameter(i,"scale")[0]
        y_str=layer_object.get_layer_parameter(i,"scale")[1]
        abs_str_vect.append("("+str(x_str)+","+str(y_str)+")")
        abs_vis_vect.append((layer_object.get_layer_parameter(i,"visibility")))
    print("depth",FunctionOperator.vector_to_str(abs_depth_vect))
    print("stretch",FunctionOperator.vector_to_str(abs_str_vect))
    print("pos",FunctionOperator.vector_to_str(abs_pos_vect))
    print("col",FunctionOperator.vector_to_str(abs_col_vect))
    db.add_variable("ldepth",FunctionOperator.vector_to_str(abs_depth_vect))
    db.add_variable("lrot",FunctionOperator.vector_to_str(abs_rot_vect))
    db.add_variable("lpos",FunctionOperator.vector_to_str(abs_pos_vect))
    print("abs_col_vect",abs_col_vect,"after stringing:",FunctionOperator.vector_to_str(abs_col_vect))
    db.add_variable("lcol",FunctionOperator.vector_to_str(abs_col_vect))
    db.add_variable("lstr",FunctionOperator.vector_to_str(abs_str_vect))
    db.add_variable("lvis",FunctionOperator.vector_to_str(abs_vis_vect))

#given a layers object changes value of a variable in one layer
#variable_name_and_index is a string consisting variable name and index, for example rot[13]
#for example if we have two layers the change_layer_variable_parameter(layer_object,"ldepth[2]",17)
# changes the value of variable "ldepth" from (nro1,nro2) to (nro,17), where nro1 and nro 2 are the original values
#NOTE that this method in itself doesn't change the depth of the layer, just variable associated with it!
def change_layer_variable_parameter(layer_object:Layers,variable_name_and_index,new_value):
    global db
    print("BUGI, jos laittaa värikomponentille negatiivisen arvon, niin se bugaa, ainakin jos ktyseessä green tai blue")
    db.try_to_change_index(str(variable_name_and_index),str(new_value))
    layer_nro=db.process_function_str(str(variable_name_and_index[variable_name_and_index.find("[")+1:variable_name_and_index.find("]")]))
    if variable_name_and_index[0:7]=="ldepth[":#let's see if this works with depth first
        layer_object.items[int(layer_nro)-1][layer_object.layer_parameter_name_to_index("depth")]=int(new_value)
    if variable_name_and_index[0:5]=="lrot[":#let's see if this works with depth first
        layer_object.items[int(layer_nro)-1][layer_object.layer_parameter_name_to_index("rotation")]=int(new_value)
    if variable_name_and_index[0:5]=="lvis[":#let's see if this works with depth first
        layer_object.items[int(layer_nro)-1][layer_object.layer_parameter_name_to_index("visibility")]=new_value
    if variable_name_and_index[0:5]=="lpos[":#let's see if this works with depth first
        value_vector=FunctionOperator.vector_components(new_value)
        layer_object.items[int(layer_nro)-1][layer_object.layer_parameter_name_to_index("x shift")]=int(value_vector[0])
        layer_object.items[int(layer_nro)-1][layer_object.layer_parameter_name_to_index("y shift")]=int(value_vector[1])
    if variable_name_and_index[0:5]=="lcol[":#let's see if this works with depth first
        print("new_value",new_value)
        value_vector=FunctionOperator.vector_components(new_value)
        print("value_vector",value_vector)
        layer_object.items[int(layer_nro)-1][layer_object.layer_parameter_name_to_index("red")]=float(value_vector[0])
        layer_object.items[int(layer_nro)-1][layer_object.layer_parameter_name_to_index("green")]=float(value_vector[1])
        layer_object.items[int(layer_nro)-1][layer_object.layer_parameter_name_to_index("blue")]=float(value_vector[2])
    if variable_name_and_index[0:5]=="lstr[":#let's see if this works with depth first
        value_vector=FunctionOperator.vector_components(new_value)
        layer_object.items[int(layer_nro)-1][layer_object.layer_parameter_name_to_index("scale")][0]=[float(value_vector[0])]
        layer_object.items[int(layer_nro)-1][layer_object.layer_parameter_name_to_index("scale")][1]=[float(value_vector[0])]



def layer_variable_assignments_to_commands(com):
    if com[:4]=="col=":#color isn't in variables list but it is indirectly affected by red,green and blue values
        return db.assign_variables_and_process("color"+com[4:])

def leftshift():
    layer_items.shift_active(-3,0)
    #rest is for draw mode
    global temporary_file_string
    temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
    shift_x=-3
    shift_y=0
    changed_coms=shifted_commands_from(temp_coms,0,shift_x,shift_y)
    temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|"  #+"|" was returned here 18.11.
    draw_temporary_file()
    update_layer_labels()      

def rightshift():
    layer_items.shift_active(4,0)
    #rest is for draw mode
    global temporary_file_string
    temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
    shift_x=4
    shift_y=0
    changed_coms=shifted_commands_from(temp_coms,0,shift_x,shift_y)
    temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" 
    draw_temporary_file()  
    update_layer_labels()  

def upshift():
    layer_items.shift_active(0,3)
        #rest is for draw mode
    global temporary_file_string
    temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
    shift_x=0
    shift_y=3
    changed_coms=shifted_commands_from(temp_coms,0,shift_x,shift_y)
    temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" 
    draw_temporary_file() 
    update_layer_labels()   

def downshift():
    layer_items.shift_active(0,-4)
    #rest is for draw mode
    global temporary_file_string
    temp_coms=MemoryHandler.split_the_string(temporary_file_string,"|")
    shift_x=0
    shift_y=-4
    changed_coms=shifted_commands_from(temp_coms,0,shift_x,shift_y)
    temporary_file_string=MemoryHandler.glue_the_split(changed_coms,"|")+"|" 
    draw_temporary_file() 
    update_layer_labels()   


resize_turtle_time=0 #this will track when was the last operation done, to prevent resize_turtles from disappearing
#shows size_- and rotate_turtles and enables moving them
def draw_resize_turtles(x,y):
    global screen
    global command_line_entry
    global layer_items
    global size_turtle, rotate_turtle
    global resize_turtle_time
    resize_turtle_time=time.time()
    turtle.ontimer(try_hide_resize_turtles,4000)#testi
    if mode=="edit_mode":
        screen.tracer(0) #added 22.11.
        layer_number=layer_items.closest_layer(temp_turtle.xcor(),temp_turtle.ycor()) 
        corners=layer_items.real_contours(layer_number)
        size_turtle.showturtle()
        size_turtle.penup()
        size_turtle.goto(temp_turtle.xcor()+120,temp_turtle.ycor())
        #size_turtle.shape("laajennusnuolet.gif")
        size_turtle.shape("circle")
        size_turtle.ondrag(move_size_turtle)
        rotate_turtle.showturtle()
        rotate_turtle.penup()
        rotate_turtle.goto(temp_turtle.xcor()+60,temp_turtle.ycor())
        #rotate_turtle.shape("pyörre.gif")
        rotate_turtle.shape("circle")
        rotate_turtle.ondrag(move_rotate_turtle)
        layer_items.redraw(t)

#tells what happens if size_turtle is dragged
def move_size_turtle(x,y):
    global layer_items
    global resize_turtle_time
    resize_turtle_time=time.time()
    turtle.ontimer(try_hide_resize_turtles,4000)#testi
    size_turtle.ondrag(None)
    [now_x,now_y]=size_turtle.pos()
    #dist_last=math.sqrt(Geometry.pdistance(temp_turtle.pos(),size_turtle.pos()))
    #dist_now=math.sqrt(Geometry.pdistance(temp_turtle.pos(),(x,y)))
    dist_last=abs(temp_turtle.xcor()-now_x)
    dist_now=abs(temp_turtle.xcor()-x)
    size_turtle.goto(x, now_y) #used to be y instead of now_y, this is a test 22.11.
    scale_factor=(dist_now/dist_last)**3
    layer_items.scale_active(scale_factor)
    turtle.ontimer(size_renew,100)
    layer_items.redraw(t)
    turtle.tracer(0)
    update_layer_labels()

def size_renew():
    size_turtle.ondrag(move_size_turtle)


#tells what happens if rotate_turtle is dragged. i.e. active drawings are rotated
def move_rotate_turtle(x,y):
    global layer_items
    global resize_turtle_time
    resize_turtle_time=time.time()
    turtle.ontimer(try_hide_resize_turtles,4000)#testi
    rotate_turtle.ondrag(None)
    [now_x,now_y]=rotate_turtle.pos()
    rotate_turtle.goto(x, y)
    angle_last=Geometry.angle_to(temp_turtle.xcor(),temp_turtle.ycor(),x,y)
    angle_now=Geometry.angle_to(temp_turtle.xcor(),temp_turtle.ycor(),now_x,now_y)
    rotate_factor=(round(angle_last-angle_now))%360
    layer_items.rotate_active(rotate_factor)
    turtle.ontimer(rotate_renew,100)
    layer_items.redraw(t)
    turtle.tracer(0)
    update_layer_labels()


def rotate_renew():
    rotate_turtle.ondrag(move_rotate_turtle)

#if it has been long enough since last operation, these turtles are hidden
def try_hide_resize_turtles():
    global resize_turtle_time
    current_time=time.time()
    elapsed_time=current_time-resize_turtle_time
    if elapsed_time>2.8:    
        rotate_turtle.hideturtle()
        size_turtle.hideturtle()


#what happens if turtle sreen is clicked with right mouse
def pick_coordinates(x,y):
    x=int(x)
    y=int(y)
    global spin_turtle
    global mode
    global screen
    global temporary_file_string

    if command_line_entry.get("1.0", "end-1c") == ""  and mode=="drawing_mode": #if there is nothing in the commandline, temp_turtle is "summoned" there
        heading=heading_when_moving_to(int(x),int(y),temporary_file_string)
        temp_turtle.setheading(heading)
        was_it_down=temp_turtle.isdown()
        temp_turtle.penup() 
        temporary_file_string += "pu()|"
        temp_turtle.goto(int(x),int(y))#coordinates are from screenclick
        temporary_file_string += "sh"+"("+str(heading)+")|"
        temporary_file_string += "goto"+"("+str(int(x))+","+str(int(y))+")|"
        if was_it_down:
            temporary_file_string += "pd()|"
        draw_temporary_file() 

    if command_line_entry.get("1.0", "end-1c")=="" and mode=="edit_mode":
        close_layer_number=layer_items.closest_layer(x,y) 
        if close_layer_number >= 0:
            layer_items.closest_layer_activation(x,y)
            show_contours(close_layer_number)
            
        screen.tracer(0) 
        temp_turtle.penup()
        temp_turtle.goto(x,y)
        layer_items.redraw(t)
        update_layer_labels()
        
    command_text=command_line_entry.get("1.0", "end-1c")
    first_add=command_text.find("ADD")
    first_opt=command_text.find("OPT")
    first_ind=command_text.find("IND")

    largenro=10000
    if first_add==-1:
        first_add=largenro
    if first_opt==-1:
        first_opt=largenro
    if first_ind==-1:
        first_ind=largenro


    if first_opt<min(first_add,first_ind):
        command_text = command_text[:first_opt] +"(IND)"+ command_text[first_opt+3:] 
    if first_add<min(first_opt,first_ind):
        command_text = command_text[:first_add-1] + command_text[first_add+3:] 
    if first_ind<min(first_opt,first_add):
        command_text = command_text[:first_ind-1] + command_text[first_ind+3:] 
    command_line_entry.delete("1.0","end-1c")
    command_line_entry.insert("1.0",command_text)
    basic_info()



start_drawing() #when opening the program, this changes the mode to edit_mode

helpx1=0
helpx2=50
helpy1=0
helpy2=50

#draws a box with spin_turtle
def draw_help_box():
    global helpx1,helpx2,helpy1,helpy2
    help_box(helpx1,helpy1,helpx2,helpy2)

#orders to draw box
def help_box(x1,y1,x2,y2):
    global spin_turtle
    spin_turtle.reset()
    spin_turtle.hideturtle()
    spin_turtle.penup()
    spin_turtle.pensize(3)
    spin_turtle.goto(x2,y1)
    spin_turtle.pendown()
    spin_turtle.goto(x1,y1)
    spin_turtle.goto(x1,y2)
    spin_turtle.goto(x2,y2)
    spin_turtle.goto(x2,y1)


# Idea is to use this method so that we "try" to move corner of help_box to new position(x2,y2)
#This succeeds if (x1,y1) is close enough to this corner
def move_help_box(x1,y1,x2,y2,distance_limit=10):
    global helpx1,helpx2,helpy1,helpy2
    if Geometry.pdistance((x1,y1),(helpx1,helpy1))<distance_limit:
        helpx1=x2
        helpy1=y2
        return
    if Geometry.pdistance((x1,y1),(helpx1,helpy2))<distance_limit:
        helpx1=x2
        helpy2=y2
        return
    if Geometry.pdistance((x1,y1),(helpx2,helpy1))<distance_limit:
        helpx2=x2
        helpy1=y2
        return
    if Geometry.pdistance((x1,y1),(helpx2,helpy2))<distance_limit:
        helpx2=x2
        helpy2=y2
        return



#should tell turtles position if needed
def position(event):
    global mousepos_data
    i,j = event.x, event.y
    screen = turtle.Screen()
    mousepos_data= [i,j,screen.window_height(),screen.window_width()]




control=False #this tells is control pressed or not
def controlpressed():
    global control
    control=True
    root.lift()

def controldown():
    global control
    control=False

#following commands lead to action iff control is pressed simultaneously with corresponding key
def cnew_file():#n
    global control
    if control:
        new_file() 

def cstart_drawing():#d
    global control
    if control:
        start_drawing() 


def cload_file():#l
    global control
    if control:
        load_file() 

def csave_file():
    global control
    if control:
        save_file() 

#copyis the active layers
def ccopy():#c
    global control
    if control:
        copy()

def copy(event=None):
        layer_items.copy_active()
        layer_items.redraw(t)
        update_layer_labels()

def delete_active(event=None):
    global label_starting_index
    layer_items.destroy_active()
    layer_items.redraw(t)
    label_starting_index=0 #perhaps this removes a bug. Layers did not show after destroying most of them.
    update_layer_labels()

#opens a pop_up with enlarged commandline
def clarge_commandline():#o
    global control
    if control:
        large_commandline()

#opens a pop_up with enlarged commandline
def large_commandline(event=None):
    open_popup("large_commandline")

#commandline emptied
def cempty():#x
    global control
    if control:
        empty()

def empty(event=None):
    empty_text_to_add()
    command_line_entry.delete('1.0',END)



#all layers to active
def cactivate():#a
    global control
    if control:
        activate()

def activate(event=None):
    for i in range(0,len(layer_items.items)):
        layer_items.change_status_without_redraw(i,"active")
    update_layer_labels()
    layer_items.redraw(t)



#all layers to visible
def cvisible():#v
    global control
    if control:
        visible()

def visible(event=None):
    for i in range(0,len(layer_items.items)):
        layer_items.change_status_without_redraw(i,"visible")
    update_layer_labels()
    layer_items.redraw(t)

#all layers to invisible
def cinvisible():#i
    global control
    if control:
        invisible()

def invisible(event=None):
    for i in range(0,len(layer_items.items)):
        layer_items.change_status_without_redraw(i,"invisible")
    update_layer_labels()
    layer_items.redraw(t)

#hides visible layers
def hide_inactive(event=None):
    for i in range(0,len(layer_items.items)):
        if layer_items.items[i][7]=="visible":
            layer_items.change_status_without_redraw(i,"invisible")
    update_layer_labels()
    layer_items.redraw(t)

#turns active layers on visible layers
def hide_active(event=None):
    for i in range(0,len(layer_items.items)):
        if layer_items.items[i][7]=="active":
            layer_items.change_status_without_redraw(i,"visible")
    update_layer_labels()
    layer_items.redraw(t)

#turns active layers on visible layers
def activate_visible(event=None):
    for i in range(0,len(layer_items.items)):
        if layer_items.items[i][7]=="active":
            layer_items.change_status_without_redraw(i,"visible")
    update_layer_labels()
    layer_items.redraw(t)

#start writing
def cwrite():#w
    global control
    if control:
        write()

def write(event=None):
    empty_text_to_add()
    command_line_entry.delete('1.0',END)
    command_line_entry.insert(INSERT,"write")
    turtle_key_mode1()
    

#saves current drawing with random name
def crsave_drawing():
    global control
    if control:
        rsave_drawing()

def rsave_drawing(event=None):#r
    command_line_entry.delete('1.0',END)
    command_line_entry.insert(INSERT,"rsave|")
    execute_command_line(0,0) #some coordinates are needed
    command_line_entry.delete('1.0',END)

def cbegin_fill():
    global control
    if control:
        begin_fill()

def begin_fill(event=None):#b
    global control
    global temporary_file_string
    temporary_file_string += "bf()|"
    temp_turtle.begin_fill()
    basic_info()

#ends filling
def cend_fill():
    global control
    if control:
        end_fill()

def end_fill(event=None):#e
    global control
    global temporary_file_string
    cur_loc=current_location(temporary_file_string)
    bf_loc=last_begin_fill_location(temporary_file_string)
    if Geometry.pdistance(cur_loc,bf_loc)>1:
        new_heading=int(Geometry.angle_to(cur_loc[0],cur_loc[1],bf_loc[0],bf_loc[1]))
        temporary_file_string += "sh("+str(new_heading)+")|"
        temp_turtle.setheading(new_heading)
    temporary_file_string += "goto("+str(bf_loc[0])+","+str(bf_loc[1])+")|"
    temporary_file_string += "ef()|"
    temp_turtle.goto(last_begin_fill_location(temporary_file_string)[0],last_begin_fill_location(temporary_file_string)[1])
    temp_turtle.end_fill()
    draw_temporary_file()
    basic_info()

#command_line is emptied and replaced by move
def cmove():
    global control
    if control:
        move()

def move(event=None):#m
    global control
    global temporary_file_string
    command_line_entry.delete('1.0',END)
    command_line_entry.insert(INSERT,"relocate|")
    
def cshow_functions():#f
    global control
    if control:
        show_functions()

def show_functions(event=None):#f
    show_popup("usershortcuts.txt")

def cup():#q
    global control
    if control:
        up()

def up(event=None):#q
    global temporary_file_string
    if temp_turtle.isdown():
        temp_turtle.penup()
        temporary_file_string += "pu()|"
    else:
        temp_turtle.pendown()
        temporary_file_string += "pd()|"
    basic_info()
    

def cheading():#h
    global control
    if control:
        heading()

def heading(event=None):#h
    command_line_entry.insert("1.0","setheading(ANG)|") 

def cjump():#j
    global control
    if control:
        jump()

def jump(event=None):#j
    command_line_entry.insert("1.0","jump(NRO)|")    

def cturn():#t
    global control
    if control:
        turn()

def turn(event=None):#t
    command_line_entry.insert("1.0","turn(AND)|") 

def cundo():#z
    global control
    if control:
        undo()

def undo(event=None):
    global past
    global temporary_file_string
    global layer_past
    global layer_items
    past[0]=past[1]
    past[1]=past[2]
    past[2]=past[3]
    past[3]=past[4]
    past[4]=temporary_file_string
    temporary_file_string=past[0]
    draw_temporary_file()
    layer_past[0]=layer_past[1]
    layer_past[1]=layer_past[2]
    layer_past[2]=layer_past[3]
    layer_past[3]=layer_past[4]
    layer_past[4]=layer_items.items_to_string()
    layer_items.from_str_to_layers(layer_past[0])
    update_layer_labels()
    layer_items.redraw(t)

#global perform NOTE MITÄ IHMETTÄ NÄMÄ KAKSI RIVIÄ OVAT? TESTIKSI POISTEETTU 31.8.
#import turtle

def credo():#y
    global control
    if control:
        redo()
 
def redo(event=None):#31.8. vähän arpapeliä tulivatko muutokset oikeassa järjestyksessä
    global past
    global temporary_file_string
    global layer_past
    global layer_items
    past[0]=temporary_file_string
    temporary_file_string=past[4]
    past[4]=past[3]
    past[3]=past[2]
    past[2]=past[1]
    past[1]=past[0]

    draw_temporary_file()
    layer_past[4]=layer_past[3]
    layer_past[3]=layer_past[2]
    layer_past[2]=layer_past[1]
    layer_past[1]=layer_past[0]
    layer_past[0]=layer_items.items_to_string()
    layer_items.from_str_to_layers(layer_past[0])

    update_layer_labels()
    layer_items.redraw(t)


#given an array of orders like [forward(3),x=4,rectangle(1,2,3,4), LOOP(goto(23,3),jump(4))] this replaces those items with LOOP
#with just their first argument
def loop_replaced_command_string(command_string):
    global db
    while command_string.find("LOOP(")!=-1:
        start_index=command_string.index("LOOP(")
        one_function_interval=FunctionOperator.smallest_complete_term_interval(command_string,start_index)
        one_function_str=command_string[one_function_interval[0]:one_function_interval[1]]
        arguments=FunctionOperator.arguments_of(one_function_str)
        if len(arguments)==0:#if there are no arguments in loop, we add empty argument there
            arguments.append("")
        command_string=command_string[:start_index]+arguments[-1]+command_string[one_function_interval[1]:]
    return command_string



dragging=False #tells if we are simulating dragging
screen_position=(0,0) #tells the current position of mouse in turtle screen
#this is to track mouse position in the turtle screen, even when mouse is not clicked
def motion(event):
    global screen_position
    global temporary_file_string
    x,y=event.x,event.y
    can = event.widget
    x_can = can.canvasx(event.x)
    y_can = -can.canvasy(event.y)#- is needed because of the flipping
    screen_position=(x,y)
    [now_x,now_y]=current_location(temporary_file_string)
    can.unbind('<Motion>')

    if Geometry.distance(now_x,now_y,x_can,y_can)>7: #so if we havent moved at least 7 pixel, there is not going to be new vertice
        direction=int(Geometry.angle_to(temp_turtle.xcor(),temp_turtle.ycor(),x_can,y_can))
        temp_turtle.setheading(direction)
        temporary_file_string += "sh("+str(int(temp_turtle.heading()))+")|"
        temp_turtle.goto(x_can, y_can)
        temporary_file_string += "goto("+str(int(x_can))+","+ str(int(y_can))+")|"
    return (x_can,y_can)

execution_interval=1.2 # tells how much time there is between executing main function
interval_phase="inactive" #tells if interval is already set
def set_execution_interval():
    global button_info3
    global current_file_name
    if current_file_name in ["new_file","my_file"]:
        messagebox.showinfo("Choose filename","First pick new filename. Screenshots are automatically saved in animations/filename/")
        file_name_popup()
    else:
        turtle.ontimer(increase_time,10)
        button_info3[3][0]="0.0"
        button_info3[3][1]=stop_increasing_time

#this sets the execution_timer to its current value
#executing
def stop_increasing_time():
    global button_info3
    global execution_interval
    button_info3[3][1]=init_timer #not a mistake, this changes the method which timer button performs when pressed to this new method
    execution_interval=float(button_info3[3][0])
    timed_execution()

#stupid name, but we want just to put executing timer into a state where it is when program is started 
def init_timer():
    global button_info3
    global execution_interval
    execution_interval=100000#a trick, when execution interval is large enough then the loop in execution is stopped
    button_info3[3][1]=set_execution_interval
    button_info3[3][0]="Timer"
    button_area()


#increases time in execution timer
def increase_time():
    global button_info3
    button_info3[3][0]=str(float(button_info3[3][0])+0.1)[0:4]
    button_area()

    if button_info3[3][1]==stop_increasing_time and float(button_info3[3][0])<20:
        turtle.ontimer(increase_renew,100) #used to be increase_time

def increase_renew():
    turtle.ontimer(increase_time)


def execution_renew():
    execute_command_line(temp_turtle.xcor(),temp_turtle.ycor())
    timed_execution()

#perform executing commandline, with time-intervals execution_interval
def timed_execution():
    global execution_interval
    global QUICK_HEIGHT, QUICK_WIDTH
    if execution_interval<10:
        turtle.ontimer(execution_renew,int(execution_interval*1000))





def simulate_dragging_renew():
    global dragging
    global screen_position
    screen.tracer(1)
    #temp_turtle.goto(screen_position[0], screen_position[1])
    #execute_command_line(temp_turtle.xcor(),temp_turtle.ycor())
    simulate_dragging(dragging)

#we want that when we double click, at least in drawing mode, turtle will automatically start behaving as it would be draggeg
#without a need to be actually dragged
def simulate_dragging(should_we_drag:bool):
    global dragging
    dragging=should_we_drag
    tcanvas=turtle.getcanvas()
    if dragging==False:
        tcanvas.unbind('<Motion>')
    if dragging:
        tcanvas.bind('<Motion>',motion)
        turtle.ontimer(simulate_dragging_renew,DRAWTIME_CONSTANT*1)



#this is what happens when mouse is dragged
def fxn(x, y):
    global temporary_file_string
    global temp_turtle
    global command_line_entry
    global mode #draw or edit

    if mode=="edit_mode":
        temp_turtle.penup()
    if command_line_entry.get("1.0", "end-1c") == "" and mode=="edit_mode": #edit moodi, tarkoitus lisätä jänniä toimintoja turtlea liikuttaessa
        temp_turtle.ondrag(None)
        [now_x,now_y]=temp_turtle.pos()
        temp_turtle.goto(x, y)
        layer_items.shift_active(int(x-now_x),int(y-now_y))
        turtle.ontimer(renew,100)
        layer_items.redraw(t)
        update_layer_labels()


    if command_line_entry.get("1.0", "end-1c")[0:6]=="throw(" and mode=="edit_mode": #edit moodi, tarkoitus lisätä jänniä toimintoja turtlea liikuttaessa
        temp_turtle.ondrag(None)
        drawin=Commands.nth_parameter(command_line_entry.get("1.0", "end-1c"),0)
        timer_value=int(1000*float(Commands.nth_parameter(command_line_entry.get("1.0", "end-1c"),1)))
        temp_turtle.goto(x, y)
        instructions=""
        with open("drawings/"+drawin+".txt","r") as file:
            instructions=file.read()
        layer_items.add_item(0,"objects",drawin,[1,1],0,int(x),int(y),"active",0,0,0,"",instructions)
        turtle.ontimer(renew,timer_value)
        layer_items.redraw(t)
        update_layer_labels()


    if command_line_entry.get("1.0", "end-1c") == "" and mode=="drawing_mode":
        [now_x,now_y]=current_location(temporary_file_string)
        temp_turtle.ondrag(None) 
        if Geometry.distance(now_x,now_y,x,y)>7: #so if we havent moved at least 7 pixel, there is not going to be new vertice
            direction=int(Geometry.angle_to(temp_turtle.xcor(),temp_turtle.ycor(),x,y))
            temp_turtle.setheading(direction)
            temporary_file_string += "sh("+str(int(temp_turtle.heading()))+")|"
            temp_turtle.goto(x, y)
            temporary_file_string += "goto("+str(int(x))+","+ str(int(y))+")|"
        # call again
        turtle.ontimer(renew,DRAWTIME_CONSTANT)
        turtle.ontimer(draw_temporary_file,DRAWTIME_CONSTANT*5)
    

#help_box osaa nyt piirtää laatikon kömpelösti kun hiirtä vedetään, koita keksiä parempi tapa")
#tätä voi sitten hyödyntää esimerkiksi tekstilaatikon tekoon.")

def renew():
    temp_turtle.ondrag(fxn)



text_to_add=""
cursor_pos=0

#empties text_to_add when needed
def empty_text_to_add():
    global text_to_add, cursor_pos
    text_to_add=""
    cursor_pos=0

#this reacts to key press made in turtle frame
def key_pressed(ch):
    global text_to_add, cursor_pos
    text_to_add = text_to_add[:cursor_pos]+str(ch)+ text_to_add[cursor_pos:]
    if cursor_pos<len(text_to_add):
        cursor_pos += 1
    helping_turtle.hideturtle()
    layer_data_turtle.hideturtle()


#for removing one letter from the end of the text
def backspace_pressed():
    global text_to_add,cursor_pos
    if len(text_to_add)>0 and cursor_pos>0: #if cursor pos is 0, then cursor_pos-1 is -1 which would lead to bug
        text_to_add=text_to_add[:cursor_pos-1]+ text_to_add[cursor_pos:]
    if cursor_pos>0:
        cursor_pos += -1

#for add empty char
def space_pressed():
    global text_to_add,cursor_pos
    if len(text_to_add)>0:
        text_to_add=text_to_add[:cursor_pos]+" "+text_to_add[cursor_pos:]
    if cursor_pos<len(text_to_add):
        cursor_pos += +1


#add new line in to writing
def enter_pressed():
    global text_to_add,cursor_pos
    if len(text_to_add)>0:
        text_to_add=text_to_add[:cursor_pos]+"\r"+text_to_add[cursor_pos:]
    if cursor_pos<len(text_to_add):
        cursor_pos += +1



#writes the text saved in text_to_add variable
def write_text():
    global text_to_add
    spin_turtle.clear()
    spin_turtle.penup()
    spin_turtle.goto(temp_turtle.xcor(),temp_turtle.ycor())
    spin_turtle.pencolor(temp_turtle.pencolor())
    spin_turtle.write(writing_instructions()[0],font=(writefont,writefontsize,writefontstyle))

#finishes writing in add text, in editmode, new layer is made, in drawmode, just text is written
def finish_writing():
    global text_to_add,cursor_pos,mode
    global writefontsize,writefont,writefontstyle
    global temporary_file_string
    if mode=="edit_mode":
        filename=text_to_add[0:8]
        filename=''.join(filter(str.isalnum, filename))#this takes all strange non alphanumerical symbols out from the file
        letters = string.ascii_lowercase #for naming the file
        randomstr=''.join(random.choice(letters)for i in range(0,4))
        filename= filename[0:8]+randomstr
        [red,green,blue]=temp_turtle.pencolor()
        colo="["+str(red)+","+str(green)+","+str(blue)+"]" #does this work? We will see.
        [fred,fgreen,fblue]=temp_turtle.fillcolor()
        fillcolo="["+str(fred)+","+str(fgreen)+","+str(fblue)+"]"
        layer_items.add_text_layer(temp_turtle.xcor(),temp_turtle.ycor(),colo,fillcolo,writefont,writefontsize,writefontstyle,text_to_add,filename)
        layer_items.redraw(t) #last operation for file_name, may cause errors if in the text, there are forbidden symbols 
        spin_turtle.clear()
        text_to_add=""
        cursor_pos=0
    if mode=="drawing_mode":
        style=writefontstyle
        fon=writefont
        fontsize=writefontsize
        [red,green,blue]=temp_turtle.pencolor()
        colo="["+str(red)+","+str(green)+","+str(blue)+"]" #does this work? We will see.
        [fred,fgreen,fblue]=temp_turtle.fillcolor()
        fillcolo="["+str(fred)+","+str(fgreen)+","+str(fblue)+"]"
        temporary_file_string += "co("+colo+")|fc("+fillcolo+ ")|wr("+style+","+fon+","+str(fontsize)+","+text_to_add+")|"
        draw_temporary_file()
    update_layer_labels()

#cursor of the text to be added by turtle is moved left
def cursor_left():
    global cursor_pos,text_to_add
    if cursor_pos>0:
        cursor_pos += -1


#cursor of the text to be added by turtle is moved right
def cursor_right():
    global cursor_pos,text_to_add
    if cursor_pos<len(text_to_add):
        cursor_pos += 1


#This tells what we are going to write with add text command
def writing_instructions():
    global cursor_pos,text_to_add
    return [text_to_add[:cursor_pos]+"|"+text_to_add[cursor_pos:],cursor_pos]

def key_pressed2(event):
    global text_to_add
    text_to_add="" 

#changes what happens when key is pressed turtle window is open
def turtle_key_mode1():
    global text_to_add,cursor_pos
    root.unbind('<KeyPress>')
    bind_control_commands()#makes ctrl+ commands work
    if command_line_entry.get("1.0", "end-1c") in ["add text","write","add text|","write|"] :
        root.bind('<KeyPress>', on_key_press_mode2)
        if text_to_add[0:8]=="add text" or text_to_add[0:5]=="write":
            text_to_add=""
            cursor_pos=0
        else:
            finish_writing()
    else:
        root.bind('<KeyPress>', on_key_press_mode1)
        text_to_add=command_line_entry.get("1.0", "end-1c")
        cursor_pos=len(text_to_add)
    # Focus the root window to capture key events
    root.focus_force()

#sets current_time and elapsed time variables depending on last click timing
def record_click_time(x, y):
    global last_click_time,current_time,elapsed_time
    last_click_time=current_time 
    current_time= time.time()
    elapsed_time = current_time - last_click_time


# Set up the click event listener
turtle.onscreenclick(record_click_time,add=True)
current_time= time.time()
elapsed_time=10 #just testing


#changes what happens when key is pressed turtle window is open
def turtle_key_mode2():
    global text_to_add,cursor_pos
    root.bind('<KeyPress>', None)
    bind_control_commands()#makes ctrl+ commands work
    root.bind('<KeyPress>', on_key_press_mode2)
    # Focus the root window to capture key events
    root.focus_force()
    text_to_add=""
    cursor_pos=0



#this is the mode for just writing on the commandline
def on_key_press_mode3(event=None):
    global text_to_add,cursor_pos
    text_to_add=""
    root.unbind('<KeyPress>')
    bind_control_commands()#makes ctrl+ commands work


command_line_entry.bind("<Button-1>",on_key_press_mode3)


def on_key_press_mode1(event):
    global cursor_pos,text_to_add
    key = event.char
    code=event.keycode
    symbol=event.keysym

    if symbol== "Return":
        enter_pressed()
    elif symbol=="BackSpace":
        backspace_pressed()
    elif symbol=="Left":
        cursor_left()
    elif symbol=="Right":
        cursor_right()
    elif symbol=="Escape":
        finish_writing()
    else:    
        text_to_add = text_to_add[:cursor_pos] +str(key) + text_to_add[cursor_pos:]
        cursor_pos += 1
    command_line_entry.delete('1.0',END)
    command_line_entry.insert(INSERT,text_to_add)  

# Function to handle key events #MADE BY chatGPT
#this mode is for writing in turtle canvas
def on_key_press_mode2(event):
    global cursor_pos,text_to_add
    key = event.char
    code=event.keycode
    symbol=event.keysym

    if symbol== "Return":
        enter_pressed()
        write_text()
    elif symbol=="BackSpace":
        backspace_pressed()
        write_text()
    elif symbol=="Left":
        cursor_left()
        write_text()
    elif symbol=="Right":
        cursor_right()
        write_text()
    elif symbol=="Escape":
        finish_writing()
    else:    
        text_to_add = text_to_add[:cursor_pos] +str(key) + text_to_add[cursor_pos:]
        cursor_pos += 1
    write_text()


#maybe not needed
def get_the_char(symbol:str):
    test_dict={"Return":"\n","7":"}","odiaeresis":"ö","adiaeresis":"ä"}
    return test_dict[symbol]

def turtle_key_unlisten():
    turtle.onkeypress(None)

def bind_control_commands():
    root.bind("<Control-b>",begin_fill)
    root.bind("<Control-c>",copy)
    root.bind("<Control-d>",start_drawing)
    root.bind("<Control-e>",end_fill)
    root.bind("<Control-f>",show_functions)
    root.bind("<Control-i>",invisible)
    root.bind("<Control-j>",jump)
    root.bind("<Control-k>",test)
    root.bind("<Control-l>",load_file)
    root.bind("<Control-m>",move)
    root.bind("<Control-n>",new_file)
    root.bind("<Control-p>",make_png)
    root.bind("<Control-q>",up)
    root.bind("<Control-r>",rsave_drawing)
    root.bind("<Control-s>",save_file)
    root.bind("<Control-o>",large_commandline)
    root.bind("<Control-t>",turn)
    root.bind("<Control-v>",visible)
    root.bind("<Control-w>",write)
    root.bind("<Control-x>",empty)
    root.bind("<Control-y>",redo)
    root.bind("<Control-z>",undo)
    root.bind("<Delete>",delete_active)

#short_keys, and commands with mouse
turtle.onscreenclick(execute_command_line,add=True)
turtle.onscreenclick(pick_coordinates,3,add=True)
temp_turtle.ondrag(fxn)
turtle_key_mode1() #sets what happens when we use keyboard 
command_line_entry.focus_force()


#next button_infos must be globally available
button_info=[["Draw/Edit",draw_mode],["Erase drawing",delete_drawing],["(N)ew file",new_file], ["(S)ave file",save_file]]
button_info2=[["(L)oad file",load_file],["Save a (p)ng",make_png],["Save drawing",save_temp_file],["Options",options_popup]]
button_info3=[["Top drawings",mini_popup],["Merge layers",merge_active],["Undo",undo],["Timer",set_execution_interval]]
# Create buttons for the thing under commandline
button_area()



# Start the GUI main loop
root.mainloop()

print("CSV haasteet: CSV pitää saada scrollattavaksi")
print("CSV:tä tallentaessa käskyillä goto(x,x^2) yhdelle sarakkeelle ja color(x*0.01,1,0) toiselle sarakkeelle, tuli lainausmerkit")
print("jälkimmäisen sarakkeen ympärille, ei kuitenkaan ensimmäisen, miksi? Miten lainausmerkit saa pois?")
print("kun koittaa ladata muuttujalle arvot, sarakkeet ja rivit menevät harmillisesti niin, että jos 'ohjeet' on ladattu CSV matriisi")
print("niin 'ohjeet[2] on sen toinen rivi, ei siis sarake. Toista saraketta ei siis saa kätevästi ulos.")
print("muuttuja=2+(5.0000000000,5.0000000000,5.0000000000)[2] aiheuttaa bugin, eli summaaminen ei toimi,jos se on vasemmalla puolella vektorikomponenttia")