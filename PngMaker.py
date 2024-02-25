import math
import random
from PIL import Image, ImageDraw, ImageFilter
from PIL import ImageDraw,ImageFont
import png
import Geometry
import tkinter.filedialog as filedialog
from typing import List
import MemoryHandler 
from icecream import ic
import cv2

#there are many properties associated with pngs, and produced pngs, listing them one by one in every method is space and time consuming
#instead we give PngProperties object as a one single parameter
class PngProperties: 
    png_dict={}
    key_list=["detail_level","contrast_points","percentage","end_contrast","min_angle","min_line_length","pensize","style"]
    key_list +=["color_divisions","max_nro_of_colors","end_width","end_height","shrinking_factor","c_parameter","iterations"]
    def __init__(self):
        self.png_dict={}
        self.png_dict["detail_level"]=5 #with 1 we produce very small drawing in "polygon"-style, with 10 maximum size, larger size -> more details
        self.png_dict["contrast_points"]=30 # how many points we pick to make triangles or rectangles in that style
        self.png_dict["percentage"]=0.1 #when percentages are used in forming images
        self.png_dict["end_contrast"]=4 #larger values add more contrast in the png/drawings, value should be between -40 and 40
        self.png_dict["min_angle"]=15 # when making triangles, should be smaller than 30
        self.png_dict["min_line_length"]=10 #when making lines ofor drawings from png:s this is their minimum length
        self.png_dict["pensize"]=1 # thickness of contourlines
        self.png_dict["style"]="polygon" #which type of drawing/png we are making
        self.png_dict["color_divisions"]=5 #when creating png we can temporarily split spectrum of colors, e.g. with value 5, there are 5*5*5 colors available
        self.png_dict["max_nro_of_colors"]=20 # how many colors in total there can be
        self.png_dict["end_width"]=None #if we want to resize picture in the end the number of pixel in x-direction is put here
        self.png_dict["end_height"]=None #if we want to resize picture in the end the number of pixel in y-direction is put here
        self.png_dict["shrinking_factor"]=3 #when shrinking, sometimes this is useful
        self.png_dict["c_parameter"]=10 # how much tries we spent for looking  each contrast_points
        self.png_dict["iterations"]=5 # how much tries we spent for looking  each contrast_points

#change value of parameter in dictionary (nothing happens if it is not one from the key_list given in the beginnning)
    def set_values(self,dict):
        for key in dict.keys():
            if key in self.key_list:
                self.png_dict[key]=dict[key]

#change value of one variable
    def set(self,key,value):
        if key in self.key_list:
            self.png_dict[key]=value
        else:
            raise ValueError("not a key")

#returns the parameter, if it is in the dictionary
    def get(self,parameter):
        return self.png_dict[parameter]
    
#return the relevant information about this object
    def info(self):
        print(self.png_dict)

#if we need a standard version to make png, usually in the back of more specified version, we can use this to create it
def standard_back(pensize=3,style="rectangle"):
    back_prop=PngProperties() #this is for making backround to picture that fills the white holes which might form in main image
    back_prop.set("contrast_points",100)
    back_prop.set("c_parameter",5) 
    back_prop.set("min_angle",10)
    back_prop.set("min_line_length",10)
    back_prop.set("end_contrast",1)
    back_prop.set("color_divisions",3)
    back_prop.set("pensize",pensize) #might be good idea to use same pensize
    back_prop.set("style",style)
    back_prop.set("max_nro_of_colors",20) # how many colors in total there can be
    back_prop.set("end_width",None) #if we want to resize picture in the end the number of pixel in x-direction is put here
    back_prop.set("end_height",None) #if we want to resize picture in the end the number of pixel in y-direction is put here
    back_prop.set("shrinking_factor",3) #when shrinking, sometimes this is useful
    back_prop.set("c_parameter",10) # how much tries we spent for looking  each contrast_points
    back_prop.set("iterations",5) # how much tries we spent for looking  each contrast_points
    return back_prop


#taking file (a text file created in the main application) draws a png from it
#style tells what we draw options basic,contours, mincontours.
#contours draws contours in black to help painting insides in the main program, mincontours does the same, but with linethickness 1
def draw_drawing(file_str,width:int,height:int,topleft:int,bg_color,save_name:str,style:str):
    # Create a new image with a white background
    objects=[]
    topleft=(-topleft[0],topleft[1]) #shifting happens to the wrong direction if this is omitted 
    hex_color=hexagesimal_color(float(bg_color[0]),float(bg_color[1]),float(bg_color[2]))
    image = Image.new("RGB", (width, height), hex_color)
    draw = ImageDraw.Draw(image)
    drawi=Geometry.Drawing(file_str)
    drawi_items=drawi.elements
    for elem in drawi_items:
        if elem.__class__.__name__== "Polygon":
            red=float(elem.inside_color[0])
            gre=float(elem.inside_color[1])
            blu=float(elem.inside_color[2])
            if style=="basic":
                objects.append({"type": "polygon","vertices": vertice_shift(vertice_y_flip(elem.vertices()),topleft),"color": hexagesimal_color(red,gre,blu)})
            for cline in elem.lines:
                if cline.pen_down:
                    col="black" #if there is for example contour style, this is going to be the color
                    if style=="basic": #normal style color
                        col=hexagesimal_color(float(cline.pencolor[0]),float(cline.pencolor[1]),float(cline.pencolor[2]))
                    pen_width=cline.thickness
                    if style=="mincontour":
                        pen_width=1
                    points=[point_shift(point_y_flip(cline.end_point1),topleft), point_shift(point_y_flip(cline.end_point2),topleft)]
                    objects.append({"type": "line","points":points ,"color":col,"thickness":pen_width })

        if elem.__class__.__name__== "Line":
            if elem.pen_down:
                col="black" #if there is for example contour style, this is going to be the color
                if style=="basic": #normal style color
                    red=float(elem.pencolor[0])
                    gre=float(elem.pencolor[1])
                    blu=float(elem.pencolor[2])
                    col=hexagesimal_color(red,gre,blu)
                pen_width=elem.thickness
                if style=="mincontour":
                    pen_width=1
                points=[point_shift(point_y_flip(elem.end_point1),topleft), point_shift(point_y_flip(elem.end_point2),topleft)]
                objects.append({"type": "line","points": points,"color":col,"thickness":pen_width })
        if elem.__class__.__name__ == "Writing" and style=="basic":
            wr=elem
            writing_loc= [wr.location[0]+topleft[0],-wr.location[1]+topleft[1]]
            col=Geometry.float_color_to_rgb([float(wr.pen_color[0]),float(wr.pen_color[1]),float(wr.pen_color[2])])
            text_font=ImageFont.truetype(Geometry.font_to_filename(wr.font,wr.style),int(int(wr.fontsize)*1.33))
            objects.append({"type": "writing", "location":writing_loc,"text":wr.text,"color":col,"font":text_font})
            

    # Draw the polygons and lines with their respective colors
    for item in objects:
        if item["type"] == "polygon":
            draw.polygon(item["vertices"], fill=item["color"])
        elif item["type"] == "line":
            end_point1=item["points"][0]
            radius=int(item["thickness"]/2)
            bounding_box=[(end_point1[0]-radius,end_point1[1]-radius),(end_point1[0]+radius,end_point1[1]+radius)]
            draw.ellipse(bounding_box,fill=item["color"])
            draw.line(item["points"],fill=item["color"], width=item["thickness"])
            end_point2=item["points"][1]
            bounding_box2=[(end_point2[0]-radius,end_point2[1]-radius),(end_point2[0]+radius,end_point2[1]+radius)]
            draw.ellipse(bounding_box2,fill=item["color"])
        elif item["type"] == "writing":
            draw.text(item["location"],item["text"],fill=item["color"],font = item["font"],anchor="ld")
    # Save the image as a PNG file
    image.save(save_name+".png")
    # Close the image
    objects=[]
    image.close()

#given png-file 'filename' returns vertices of polygon which is the one containing 'point' and limited by 
# contours in the file
#color_gap tells how near we must be color_wise to the color of point, so that we let paint fill through it
def paint_area(filename,savename,point,filling_color,color_gap):
    im=Image.open(filename)
    pix=im.load()
    (width,height)=im.size
    pixels_to_change=[]
    orig_color=pix[point[0],point[1]]
    pixels_to_change.append(point)
    pix[point[0],point[1]]=filling_color
    stop=1000
    while stop>0 and len(pixels_to_change)>0: # used to have condition and orig_color != (0,0,0): changed in 8.11.
        new_pixels=[]
        for pixel in pixels_to_change:
            left_point=boxify(0,width,0,height,(pixel[0]-1,pixel[1]))
            right_point=boxify(0,width,0,height,(pixel[0]+1,pixel[1]))
            up_point=boxify(0,width,0,height,(pixel[0],pixel[1]-1))
            down_point=boxify(0,width,0,height,(pixel[0],pixel[1]+1))
            try_points=[left_point,right_point,up_point,down_point]
            for t_point in try_points:
                if color_distance(pix[t_point[0],t_point[1]],orig_color)<color_gap and pix[t_point[0],t_point[1]]!=filling_color:
                    pix[t_point[0],t_point[1]]=filling_color
                    new_pixels.append(t_point)
            #pixels_to_change[:]=(value for value in pixels_to_change if value != pixel)
        pixels_to_change=new_pixels
        stop += -1
    starting_point=(point[0],0)
    while pix[starting_point[0],starting_point[1]]!=filling_color and starting_point[1]<point[1]:
        starting_point=(starting_point[0],starting_point[1]+1)
    #this finds the largest possible contour, that¨s why we start from the top of the image to try to find contour
    #if the homotopy group is non-trivial (there is holes) then a largest area is found
    im.save(savename)
    poly=make_edge(savename,filling_color,color_gap=2,starting_point=starting_point,edge_lenght=1,reduction=True)
    poly.reduce_unnecessary_vertices(1)
    im.close()

    return poly


def load_text_file(filename):
    with open(filename, "r") as file:
        # Read the contents of the file into memory
        instructions=file.read()
    return instructions

    #loads a file, can be object, can be text, maybe also gif or extra? 
def load_file_as_string(file_name:str,sub_directory:str):
    actual_name= sub_directory+"/"+file_name.strip("'")+".txt"#strip ' just in case
    if sub_directory=="":
        actual_name=file_name+".txt"
        # Open a file for reading
    with open(actual_name, "r") as file:
        # Read the contents of the file into memory
        instructions=file.read()
    return instructions

#gives color of the pixel in (x,y)
def pixel_color(filename:str,x:int,y:int):
    im = Image.open(filename) # Can be many different formats.
    pix = im.load()
    #pix[x,y] = value  # Set the RGBA Value of the image (tuple)
    #im.save('alive_parrot.png')  # Save the modified pixels as .png

# cuts the possible colors in divisions*divisions*divisions colors, returns the one closest to the color
def simplify_color(color:List[float],divisions:int):
    if color[0]>1 or color[1]>1 or color[2]>1:
        raise ValueError("stupid color, must be between 0.0-1.0")
    return (int(1/2+color[0]*divisions)/divisions,int(1/2+color[1]*divisions)/divisions,int(1/2+color[2]*divisions)/divisions)

# cuts the possible color_component in divisions colors, returns the one closest to the color
def simplify_rgb_color_component(color_component:int,divisions:int):
    return int(round(((color_component)*divisions/255))*(255/divisions))

#gives a contrast for pixels of color1 and color2, where pixel values are between 0 and 255
def contrast_amount(color1,color2):
    return math.pow(abs(color1[0]-color2[0]),2)+math.pow(abs(color1[1]-color2[1]),2)+math.pow(abs(color1[2]-color2[2]),2)

#makes float_valued colors look more ungray
def contrast_shift_transformation(float_color,strength,stable_color):
    return anti_gray_function(float_color,strength,stable_color)

#makes rgb_valued colors look more ungray
def rgb_contrast_transformation(rgb_color,strength,stable_color):
    float_color=(rgb_color[0]/256,rgb_color[1]/256,rgb_color[2]/256)
    float_color=contrast_shift_transformation(float_color,strength,stable_color)
    return (int(float_color[0]*256),int(float_color[1]*256),int(float_color[2]*256))

#takes a value x in [0,1] and returns a value in the same_interval. 0->0, 0.5->0.5, and 1->1 but t 
def anti_gray_plus(x:float,stable_x:float):
    STRENGHT=0.03
    result=x

    v1=stable_x-0.5*min(stable_x, 1-stable_x)
    v2=stable_x+0.5*min(stable_x, 1-stable_x)
    if x<v1:
        result += -(x/(v1))*STRENGHT
    if v1<=x<v2:
        result += -STRENGHT+2*((x-v1)/(v2-v1))*STRENGHT
    if x>v2:
        result += +STRENGHT-((x-v2)/(1-v2))*STRENGHT
    return result

#takes a value x in [0,1] and returns a value in the same_interval. 0->0, 0.5->0.5, and 1->1 but t 
def anti_gray_minus(x:float,stable_x:float):
    STRENGHT=-0.03
    result=x

    v1=stable_x-0.5*min(stable_x, 1-stable_x)
    v2=stable_x+0.5*min(stable_x, 1-stable_x)
    if x<v1:
        result += -(x/(v1))*STRENGHT
    if v1<=x<v2:
        result += -STRENGHT+2*((x-v1)/(v2-v1))*STRENGHT
    if x>v2:
        result += +STRENGHT-((x-v2)/(1-v2))*STRENGHT
    return result


#takes a color and returns a color which is moven closer or further away from stable color depending on contrast strength
#the more negative contrast strength is the more everything moves to stable color
#the more positive, the further away the move from stable color
def anti_gray_function(color:List[float],contrast_strength:float,stable_color:List[float]):
    for i in range(3):
        if color[i]>40:
            color[i]=40
        if color[i]<-40:
            color[i]=-40
    is_it_plus = contrast_strength>0 #boolean
    contrast_strength=int(abs(contrast_strength))
    for j in range(contrast_strength):
        if is_it_plus:
            color=(anti_gray_plus(color[0],stable_color[0]),anti_gray_plus(color[1],stable_color[1]),anti_gray_plus(color[2],stable_color[2]))
        if is_it_plus==False:
            color=(anti_gray_minus(color[0],stable_color[0]),anti_gray_minus(color[1],stable_color[1]),anti_gray_minus(color[2],stable_color[2]))

     #we need the following operations because if there is exponential notation of color, for example 2.7199999999999984e-05, then
        #redusing this to 2.719 confuses other methods in the program
    if color[0]<0.001:
        color=(0,color[1],color[2])
    if color[1]<0.001:
        color=(color[0],0,color[2])
    if color[2]<0.001:
        color=(color[0],color[1],0)
    return color



# returns a list of points in the image that seem to be close of some contour in the image
def contrast_point_list(filename,quantity:int,quality:int):
    c_value_dict={} #here we save the contrast values of added points
    im = Image.open(filename) # Can be many different formats.
    pix = im.load()
    (width,height)=im.size
    for i in range(quantity): #we will find quantity number of points
        c_value=0
        best_point=(0,0)

        for i in range(quality): # quality number of points are searched, and best one is picked
            test_point= (int(random.random()*(width)),int(random.random()*(height)))
            j=0
            t_value=0
            while j in range(quality): #searching from neighbourhood of test_point, we eventually find quality number of points
                #against which we compare color of test_point. Note that in this loop, we could also have chosen some constant number
                #of iterations (like 10) instead of quality
                near_test_point= (test_point[0]-3+int(random.random()*7),test_point[1]-3+int(random.random()*7))
                if near_test_point[0] in range(0,width) and near_test_point[1] in range(0,height): 
                    j+=1
                    t_value +=contrast_amount(pix[test_point[0],test_point[1]],pix[near_test_point[0],near_test_point[1]]) #contrast in x-direction 3step
            if t_value>c_value:
                best_point=test_point
                c_value=t_value
        c_value_dict[best_point]=c_value

    # Sorting the dictionary by values in ascending order
    sorted_dict = sorted(c_value_dict.items(), key=lambda x: x[1],reverse=False)#reverse used to be True, changed to False 17.2.
    #idea is that now points with most contrast are picked last, which makes better pictures at keast in regtangles mode photos
    # Extracting the sorted points
    contrast_list = [item[0] for item in sorted_dict]
    return contrast_list

#takes a dictionary and sorts it by its values to new dict so that items are listed in the descending order according to their keys
def sorted_dict_from_dictionary(dict):
    sorted_dict = sorted(dict.items(), key=lambda x: x[1],reverse=True)
    return sorted_dict
#taking two triangles, if they share two same endpoints, we return two triangles with same area total covered, but other corners
#connected

#takes a dictionary and sorts it by its values to a list so that items are listed in the descending order according to their keys
def sorted_list_from_dictionary(dict):
    sorted_dict = sorted_dict_from_dictionary(dict)
    sorted_list=[]
    for i in range(len(sorted_dict)):
        sorted_list.append(sorted_dict[i][0])
    return sorted_list
#taking two triangles, if they share two same endpoints, we return two triangles with same area total covered, but other corners
#connected


def triangle_flip(triangle1,triangle2):
    for i in range(0,3):
        for j in range(0,3):
            if i!=j:
                if triangle1[0]==triangle2[i] and triangle1[1]==triangle2[j]:
                    if Geometry.pis_there_intersection(triangle1[0],triangle1[1],triangle1[2],triangle2[3-i-j]) == False:
                        return [triangle1,triangle2] #new triangle lines must be drawn inside old triangles
                    return [[triangle1[2],triangle2[3-i-j],triangle1[0]],[triangle1[2],triangle2[3-i-j],triangle1[1]]]
                if triangle1[0]==triangle2[i] and triangle1[2]==triangle2[j]:
                    if Geometry.pis_there_intersection(triangle1[0],triangle1[2],triangle1[1],triangle2[3-i-j]) == False:
                        return [triangle1,triangle2] #new triangle lines must be drawn inside old triangles
                    return [[triangle1[1],triangle2[3-i-j],triangle1[0]],[triangle1[1],triangle2[3-i-j],triangle1[2]]]
                if triangle1[1]==triangle2[i] and triangle1[2]==triangle2[j]:
                    if Geometry.pis_there_intersection(triangle1[1],triangle1[2],triangle1[0],triangle2[3-i-j]) == False:
                        return [triangle1,triangle2] #new triangle lines must be drawn inside old triangles
                    return [[triangle1[0],triangle2[3-i-j],triangle1[1]],[triangle1[0],triangle2[3-i-j],triangle1[2]]]
    return [triangle1,triangle2]


def middle_point(point1,point2):
    return (round((point1[0]+point2[0])/2),round((point1[1]+point2[1])/2))

#if possible, halves a triangle into two triangles
def triangle_halfing(point1,point2,triangle):
    extra_point=triangle[0]
    if point1 not in triangle or point2 not in triangle:
        return [triangle]
    else:
        if triangle[1] not in [point1,point2]:
            extra_point=triangle[1]
        if triangle[2] not in [point1,point2]:
            extra_point=triangle[2]

    triangle1=[middle_point(point1,point2),point1,extra_point]
    triangle2=[middle_point(point1,point2),point2,extra_point]

 
    return [triangle1,triangle2]

#returns a list of indexes with a large side
def large_triangle_indexes(triangle_list,size:int):
    large_triangles=[]
    for i in range(len(triangle_list)):
        if triangle_largest_side(triangle_list[i])>size:
            large_triangles.append(i)
    return large_triangles

#tells the length of the largest triangle
def triangle_largest_side(triangle):
    len1=Geometry.pdistance(triangle[0],triangle[1])
    len2=Geometry.pdistance(triangle[1],triangle[2])
    len3=Geometry.pdistance(triangle[0],triangle[2])
    return max(len1,len2,len3)

#returns true, if there is a common side with triangles
def shares_side(triangle1,triangle2):
    if triangle1[0] in triangle2 and triangle1[1] in triangle2:
        return True
    if triangle1[0] in triangle2 and triangle1[2] in triangle2:
        return True
    if triangle1[0] in triangle2 and triangle1[2] in triangle2:
        return True
    return False

#halvest the longest lines in triangles
def end_mutation_step(triangle_list):
    largest_side=0
    size=len(triangle_list)
    for i in range(10):
        try_size=triangle_largest_side(triangle_list[int(size*random.random())])
        if largest_side<try_size:
            largest_side=try_size
    upperlimit=0.9*try_size
    indexes=large_triangle_indexes(triangle_list,upperlimit)
    new_triangles=[]
    for index in indexes:
        len1=Geometry.pdistance(triangle_list[index][0],triangle_list[index][1])
        len2=Geometry.pdistance(triangle_list[index][1],triangle_list[index][2])
        len3=Geometry.pdistance(triangle_list[index][0],triangle_list[index][2])
        point1=triangle_list[index][0]
        point2=triangle_list[index][1]        
        if len2>=max(len1,len2,len3):
            point1=triangle_list[index][2] 
        elif len3>=max(len1,len2,len3):
            point2=triangle_list[index][2] 
        new_triangles += triangle_halfing(point1,point2,triangle_list[index])
    
    size=len(triangle_list)
    for i in range(len(triangle_list)): #NOTE might go wrong since what happens to indeces if we pop middle of iteration?
        if (size-i-1) in indexes:
            triangle_list.pop(size-i-1)
    triangle_list += new_triangles
    return triangle_list

#times tells how many times we do end_mutation step which halves the largest sides in the triangles
def end_mutation(triangle_list,times:int):
    for i in range(times):
        triangle_list=end_mutation_step(triangle_list)
    return triangle_list


#given a list of endpoints 'edge_list' this produces a new shorter list of endpoints if edges make "lasso"-shape. 
#only the lasso part is left, i.e. we look at the last end_point, and if it is also found in the list before
# we take the second last place where it was found and start our returned edgelist from there 
def lasso_cut(edge_list):
    end_point=edge_list[-1]
    index=0
    for i in range(len(edge_list)-1):
        if edge_list[i]==end_point:
            index=i
    return edge_list[index:]

#starting from a starting point, chooses pixel-locations from file, such that pixel color stays close to 'color'
#wandering stops when we end to the starting point or some other point in the curve
def simple_edge(filename,color:List[float],color_gap:int,starting_point):
    im = Image.open(filename) # Can be many different formats.
    pix = im.load()
    (width,height)=im.size
    u_point= (starting_point[0],starting_point[1]-1)
    l_point= (starting_point[0]-1,starting_point[1])
    lu_point= (starting_point[0]-1,starting_point[1]-1) #there is a reason for this not being the point on the right
    c_dist1= color_distance(pix[starting_point[0],starting_point[1]],pix[u_point[0],u_point[1]]) #to the right
    c_dist2= color_distance(pix[starting_point[0],starting_point[1]],pix[l_point[0],l_point[1]]) #to the down
    c_dist3= color_distance(pix[l_point[0],l_point[1]],pix[lu_point[0],lu_point[1]])#to the left
    c_dist4= color_distance(pix[lu_point[0],lu_point[1]],pix[u_point[0],u_point[1]])#to the up
    second_point=starting_point
    largest_dist=max(c_dist1,c_dist2,c_dist3,c_dist4)
    if c_dist1==largest_dist:
        second_point=(starting_point[0]+1,starting_point[1])
    elif c_dist2==largest_dist:
        second_point=(starting_point[0],starting_point[1]+1)
    elif c_dist3==largest_dist:
        second_point=(starting_point[0]-1,starting_point[1])
    elif c_dist4==largest_dist:
        second_point=(starting_point[0],starting_point[1]-1)

    edge=[starting_point,second_point]#do not change

    cut_distance=3000
    while cut_distance>0 and edge[-1] not in edge[:-1]:
        cut_distance += -1
        next_point=edge[-1]
        straight_vector=Geometry.point_int_minus(edge[-1],edge[-2])
        left_vector= Geometry.point_int_turn(straight_vector,270) #since y-axis is mirror to the standard 
        right_vector= Geometry.point_int_turn(straight_vector,90) #these angles are this way around
        pixels_to_left=pixels_on_the_side(pix,edge[-1],Geometry.point_int_sum(edge[-1],left_vector))
        pixels_to_straight=pixels_on_the_side(pix,edge[-1],Geometry.point_int_sum(edge[-1],straight_vector))
        pixels_to_right=pixels_on_the_side(pix,edge[-1],Geometry.point_int_sum(edge[-1],right_vector))
        lcond0=color_distance(color,pixels_to_left[0])<color_gap
        lcond1=color_distance(color,pixels_to_left[1])<color_gap
        if (lcond0==True and lcond1==False) or (lcond1==True and lcond0==False):
            new_try_point=Geometry.point_int_sum(edge[-1],left_vector)
            if new_try_point not in edge and new_try_point[0] in range(0,width) and new_try_point[1] in range(0,height):
                #if conditions used to be in range in range(1,width-1) and in range(1,height-1)
                next_point=new_try_point

        scond0=color_distance(color,pixels_to_straight[0])<color_gap
        scond1=color_distance(color,pixels_to_straight[1])<color_gap
        if (scond0==True and scond1==False) or (scond1==True and scond0==False):
            new_try_point=Geometry.point_int_sum(edge[-1],straight_vector)
            if new_try_point not in edge and new_try_point[0] in range(0,width) and new_try_point[1] in range(0,height):
                #if conditions used to be in range in range(1,width-1) and in range(1,height-1)
                next_point=new_try_point

        rcond0=color_distance(color,pixels_to_right[0])<color_gap
        rcond1=color_distance(color,pixels_to_right[1])<color_gap
        if (rcond0==True and rcond1==False) or (rcond1==True and rcond0==False):
            new_try_point=Geometry.point_int_sum(edge[-1],right_vector)
            if new_try_point not in edge and new_try_point[0] in range(0,width) and new_try_point[1] in range(0,height):
                #if conditions used to be in range in range(1,width-1) and in range(1,height-1)
                next_point=new_try_point
        edge.append(next_point)

    edge=lasso_cut(edge[:-1])#there are two same point at the end, so last point is removed before lasso_cut
    #random testing starts
    im.close()
    return edge

#returns a polygon drawn from file starting from the starting_point, following pixel with 'color' or near to it
def make_edge(filename,color:List[float],color_gap:int,starting_point,edge_lenght:int,reduction:bool):
    whole_edge=simple_edge(filename,color,color_gap,starting_point)
    result_edge=[]
    for i in range(int(len(whole_edge)/edge_lenght)):
        result_edge.append(whole_edge[edge_lenght*i])
    result_edge.append(whole_edge[-1])
    #NOTE currently if there is a "lasso"like shape, the beginning of lasso isn't cut even though it should be
    poly=Geometry.Polygon()
    color=(color[0]/256,color[1]/256,color[2]/256)
    poly.verticise(result_edge,1,color,True,True)
    if reduction: #if reduction is true, we take of consecutive vertices on same line
        poly.reduce_unnecessary_vertices(1) #added 5.11. parameter tells how far middle point can be to still be swallowed
    return poly

#this is like making edge with only difference being, that if starting point is not "good" i.e. part of an edge, then a new
#starting point is located above the initial starting point, color that is followed is the same as in starting point
def find_and_make_edge(filename,color_gap:int,starting_point,edge_lenght:int,reduction:bool):
    starting_color=pixel_color_in(filename,starting_point)
    comparing_point=starting_point
    comparing_color=pixel_color_in(filename,comparing_point)
    while color_distance(starting_color,comparing_color)<color_gap and comparing_point[1]>0:
        comparing_point=(comparing_point[0],comparing_point[1]-1)
        comparing_color=pixel_color_in(filename,comparing_point)
    starting_point=(comparing_point[0],comparing_point[1]+1)
    return make_edge(filename,starting_color,color_gap,starting_point,edge_lenght,reduction)

#colors edge in filename from thing at starting_point, used mostly for testing purposes
def color_edge(filename,savename,color_gap,starting_point,edge_lenght,edge_color):
    im=Image.open(filename)
    pix=im.load()
    start_color=pix[starting_point[0],starting_point[1]]
    poly=find_and_make_edge(filename,color_gap,starting_point,edge_lenght,False)
    save_png_copy_as(filename,savename)
    copyim=Image.open(savename)
    pixc=copyim.load()
    for vertice in poly.vertices():
        pixc[vertice[0],vertice[1]]=edge_color
    copyim.save(savename)



     



#point1 and point2 are meant to be points next to each other
#returns pixel colors of pixels next to line drawn from point1 to point2, the color on the left side is given first
def pixels_on_the_side(pix,point1,point2):
    if Geometry.pdistance(point1,point2)!=1:
        raise ValueError("points should be next to each other")
    if point1[1]>point2[1]:
        return [pix[point2[0]-1,point2[1]],pix[point2[0],point2[1]]]
    if point1[1]<point2[1]:
        return [pix[point1[0],point1[1]],pix[point1[0]-1,point1[1]]]
    if point1[0]<point2[0]:
        return [pix[point1[0],point1[1]-1],pix[point1[0],point1[1]]]
    if point1[0]>point2[0]:
        return [pix[point2[0],point2[1]],pix[point2[0],point2[1]-1]]
    
#we take a list of triangles and splits on side of one triangle to halfs, we try to pick large side
#quality tells how many times we try to get larger side
def halving_mutation(triangle_list,quality,probability,min_angle,filename):
    if random.random()>probability:
        return triangle_list #probability tells the probability of halving, now it doesn't happen

    point1=(0,0)
    point2=(0,0)
    point3=(0,0)
    best_point1=(5,5)#these are random values
    best_point2=(5,5)#
    best_point3=(0,0)
    variance=0
    fitness_number=0
    for i in range(quality):
        max_length=0
        index=int(random.random()*len(triangle_list))
        dist1=Geometry.pdistance(triangle_list[index][0],triangle_list[index][1])
        dist2=Geometry.pdistance(triangle_list[index][0],triangle_list[index][2])
        dist3=Geometry.pdistance(triangle_list[index][1],triangle_list[index][2])
        if dist1>max_length:
            point1=triangle_list[index][0]
            point2=triangle_list[index][1]
            point3=triangle_list[index][2]
            max_length=dist1
        if dist2>max_length:
            point1=triangle_list[index][0]
            point2=triangle_list[index][2]
            point3=triangle_list[index][1]
            max_length=dist2
        if dist3>max_length:
            point1=triangle_list[index][1]
            point2=triangle_list[index][2]
            point3=triangle_list[index][0]
            max_length=dist3
        triangle_variance=triangle_variance_estimator(point1,point2,point3,1,filename)#1 is test, I don't know what is a good value
        triangle_deviation=math.sqrt(triangle_variance)
        comparing_number=max_length* triangle_deviation
        if comparing_number>fitness_number:
            fitness_number=comparing_number
            best_point1=point1
            best_point2=point2


    poppable_triangle_indexes=[]
    addable_triangles=[]
    for i in range(len(triangle_list)):
        if best_point1 in triangle_list[i] and best_point2 in triangle_list[i]:
            poppable_triangle_indexes.append(i)
            addable_triangles += triangle_halfing(best_point1,best_point2,triangle_list[i])

    for add_tri in addable_triangles:        
        if Geometry.smallest_triangle_angle(add_tri[0],add_tri[1],add_tri[2])<min_angle: #too small angle to be added
            return triangle_list
    #it works, we can add new triangles
    size=len(triangle_list)
    for i in range(len(triangle_list)): #NOTE might go wrong since what happens to indeces if we pop middle of iteration?
        if (size-i-1) in poppable_triangle_indexes:
            triangle_list.pop(size-i-1)
    for add_tri in addable_triangles:
        triangle_list.append(add_tri)
    return triangle_list

#this tries to mutate list of triangles by flipping n-times
#there must be at least two triangles before this can be used
def triangle_list_mutation(triangle_list,nro_tries,min_angle):
    if len(triangle_list)<2:
        raise ValueError("more triangles needed")
    for i in range(nro_tries):
        index1=int(random.random()*len(triangle_list))
        index2=int(random.random()*len(triangle_list))
        if index1==index2:
            index1=0
            index2=1
        first_triangle=triangle_list[index1]
        second_triangle=triangle_list[index2]
        shared_sides=0
        if first_triangle[0] in second_triangle:
            shared_sides +=1
        if first_triangle[1] in second_triangle:
            shared_sides +=1
        if first_triangle[2] in second_triangle:
            shared_sides +=1
        if shared_sides==2:
            new_triangles=triangle_flip(first_triangle,second_triangle)
            tr10,tr11,tr12=new_triangles[0][0],new_triangles[0][1],new_triangles[0][2]
            tr20,tr21,tr22=new_triangles[1][0],new_triangles[1][1],new_triangles[1][2]
            if Geometry.smallest_triangle_angle(tr10,tr11,tr12)>min_angle and Geometry.smallest_triangle_angle(tr20,tr21,tr22)>min_angle:
                triangle_list[index1]=new_triangles[0]
                triangle_list[index2]=new_triangles[1]



#given a list of points, triangles are made that do not overlap each other
#min_angle tells roughly how small angles in triangles are acceptable
def non_overlapping_triangles(point_list,width,height,min_angle,halving_propability,filename):
    for point in point_list:
        if point[0]<0 or point[1]<0 or point[0]>width or point[1]>height:
            raise ValueError("points are not inside rectangle")
    #we put all the triangles in the following list, first two starting triangle are made that cover the whole area
    triangle_list=[[(0,0),(0,int((height-1)/2)),point_list[0]]]
    triangle_list.append([(0,int((height-1)/2)),(0,height-1),point_list[0]])
    triangle_list.append([(0,0),(int((width-1)/2),0),point_list[0]])
    triangle_list.append([(int((width-1)/2),0),(width-1,0),point_list[0]])
    triangle_list.append([(width-1,height-1),(width-1,int((height-1)/2)),point_list[0]])
    triangle_list.append([(width-1,int((height-1)/2)),(width-1,0),point_list[0]])
    triangle_list.append([(width-1,height-1),(int((width-1)/2),height-1),point_list[0]])
    triangle_list.append([(int((width-1)/2),height-1),(0,height-1),point_list[0]])
    triangle_list=end_mutation(triangle_list,2)

    for i in range(1,len(point_list)):
        new_point=point_list[i]
        halving_mutation(triangle_list,5,halving_propability,min_angle,filename)
        j=0
        triangle_list_mutation(triangle_list,100,min_angle)
        while j in range(0,len(triangle_list)):
            if Geometry.is_it_in_triangle(new_point,triangle_list[j][0],triangle_list[j][1],triangle_list[j][2]):
                add_cond=True
                if Geometry.smallest_triangle_angle(new_point,triangle_list[j][0],triangle_list[j][1])<min_angle:
                    add_cond=False
                if Geometry.smallest_triangle_angle(new_point,triangle_list[j][0],triangle_list[j][2])<min_angle:
                    add_cond=False
                if Geometry.smallest_triangle_angle(new_point,triangle_list[j][1],triangle_list[j][2])<min_angle:
                    add_cond=False
                if add_cond:
                    triangle_list.append([new_point,triangle_list[j][0],triangle_list[j][1]])#if point is inside old triangle
                    triangle_list.append([new_point,triangle_list[j][0],triangle_list[j][2]])#we split the old triangle to
                    triangle_list.append([new_point,triangle_list[j][1],triangle_list[j][2]])#three new triangles
                    triangle_list.pop(j) #and remove the old one
                    j=2*len(triangle_list) #so that we stop adding more triangles
            j+=1
    triangle_list=end_mutation(triangle_list,5)
    return triangle_list


#returns an average color inside triangle
def triangle_average_color(point1,point2,point3,filename):
    im = Image.open(filename) # Can be many different formats.
    pix = im.load()
    (width,height)=im.size
    min_x=min(point1[0],point2[0],point3[0],width)
    max_x=max(point1[0],point2[0],point3[0],1)
    min_y=min(point1[1],point2[1],point3[1],height)
    max_y=max(point1[1],point2[1],point3[1],1)
    redsum=0
    greensum=0
    bluesum=0
    pixel_total=0
    for i in range(min_x,max_x):
        for j in range(min_y,max_y):
            if Geometry.is_it_in_triangle((i,j),point1,point2,point3):
                pixel_total +=1
                redsum += pix[i,j][0]
                greensum += pix[i,j][1]
                bluesum += pix[i,j][2]
    if pixel_total==0:#if triangle is very small, we just take the pixel color from closest point
        return (pix[min(width-1,max_x),min(height-1,max_y)][0],pix[min(width-1,max_x),min(height-1,max_y)][1],pix[min(width-1,max_x),min(height-1,max_y)][2]) #there used to be grey color

    else:
        return (int(redsum/pixel_total),int(greensum/pixel_total),int(bluesum/pixel_total))


#this makes a new pixel map by taking a pixel_map from file1 and file2 and averaging them with percentage proportions (those need not
# to add 1 necessarely)
def pixel_combination(filename1,filename2,file1_percentage,file2_percentage,savename):
    im1 = Image.open(filename1) # Can be many different formats.
    (width1,height1)=im1.size
    pix1 = im1.load()
    im2 = Image.open(filename2) # Can be many different formats.
    (width2,height2)=im2.size
    pix2 = im2.load()
    (width,height)=(min(width1,width2),min(height1,height2))
    for i in range(width):
        for j in range(height):
            red=int(min(pix1[i,j][0]*file1_percentage+pix2[i,j][0]*file2_percentage,255))
            green=int(min(pix1[i,j][1]*file1_percentage+pix2[i,j][1]*file2_percentage,255))
            blue=int(min(pix1[i,j][2]*file1_percentage+pix2[i,j][2]*file2_percentage,255))
            pix1[i,j]=(red,green,blue)
    im1.save(savename)


#makes a new file from png-file. For pixel in the old file, if all pixels next to it are between a color distance of min_gap to max_gap
#then this pixel is colored as the closest color to the pixels next too it
def anti_blur_file(filename,savename,min_gap,max_gap):
    im = Image.open(filename) # Can be many different formats.
    (width,height)=im.size
    pix = im.load()
    pixel_color_array=zero_color_mn_array(width,height)
    for i in range(0,width):
        for j in range(0,height):
            le=boxify(0,width-1,0,height-1,(i-1,j))
            ri=boxify(0,width-1,0,height-1,(i+1,j))
            to=boxify(0,width-1,0,height-1,(i,j-1))
            bo=boxify(0,width-1,0,height-1,(i,j+1))
            le_color_dist= color_distance(pix[i,j],pix[le[0],le[1]])
            ri_color_dist= color_distance(pix[i,j],pix[ri[0],ri[1]])
            to_color_dist= color_distance(pix[i,j],pix[to[0],to[1]])
            bo_color_dist= color_distance(pix[i,j],pix[bo[0],bo[1]])
            min_dist=min(le_color_dist,ri_color_dist,to_color_dist,bo_color_dist)
            max_dist=max(le_color_dist,ri_color_dist,to_color_dist,bo_color_dist)
            if min_gap<min_dist and max_dist<max_gap: 
                pixel_color_array[i][j]=closest_color(pix[i,j],[pix[le[0],le[1]],pix[ri[0],ri[1]],pix[to[0],to[1]],pix[bo[0],bo[1]]])
            else:
                pixel_color_array[i][j]=pix[i,j] 
    for i in range(0,width):
        for j in range(0,height):
            pix[i,j]=pixel_color_array[i][j]
    im.save(savename)

#simplest way to follow shapes in pngs if they go trhough the edge is just to whiten some lines closesto to contour, this makes
# the contourlines go further away from edges 
def whiten_contour(filename,savename,contour_width):
    im = Image.open(filename) # Can be many different formats.
    (width,height)=im.size
    pix = im.load()
    for i in range(width):
        for j in range(min(height,contour_width)):
            pix[i,j]=(230,230,230) #all 230 here used to be 255, lets see waht happens
            pix[i,height-1-j]=(230,230,230)
    for i in range(height):
        for j in range(min(width,contour_width)):
            pix[j,i]=(230,230,230)
            pix[width-1-j,i]=(230,230,230)
    im.save(savename)
    im.close()

#makes a new file with pixels being average of pixels next to them in the original file
def blur_file(filename,savename):
    im = Image.open(filename) # Can be many different formats.
    (width,height)=im.size
    pix = im.load()
    pixel_color_array=zero_color_mn_array(width,height)
    for i in range(0,width):
        for j in range(0,height):
            le=boxify(0,width-1,0,height-1,(i-1,j))
            ri=boxify(0,width-1,0,height-1,(i+1,j))
            to=boxify(0,width-1,0,height-1,(i,j-1))
            bo=boxify(0,width-1,0,height-1,(i,j+1))
            help=rgb_color_average([pix[i,j],pix[le[0],le[1]],pix[ri[0],ri[1]],pix[to[0],to[1]],pix[bo[0],bo[1]]])
            pixel_color_array[i][j]=help
    for i in range(0,width):
        for j in range(0,height):
            pix[i,j]=pixel_color_array[i][j]
    im.save(savename)


#"starting" from the 'point' walks 'steps' number of random steps, and returns a point, where this walking ends
def random_walk(steps:int,point:List[int]):
    for i in range(steps):
        instruction=int(5*random.random())
        if instruction==0:
            point=(point[0]-1,point[1])
        if instruction==1:
            point=(point[0],point[1]-1)
        if instruction==2:
            point=(point[0]+1,point[1])
        if instruction==3:
            point=(point[0],point[1]+1)
    return point

#just saves a copy of the file with new name
def save_png_copy_as(filename,savename):
    fileim=Image.open(filename)
    fileim.save(savename)    

#takes a png from filename, shrinks it so that it's height+width<max_size, also simplifies its colors
def shrink_and_simplify(filename,savename,simplifying_divisions:int,max_nro_of_colors:int,max_size):
    fileim=Image.open(filename)
    (width,height)=fileim.size
    shrinking_amount=max(1,round((width+height)/max_size))
    shrinked_image_pixel_map(filename,savename,shrinking_amount,simplifying_divisions)
    im=Image.open(savename)
    pixel_map=im.load()
    force_n_colors(pixel_map,(0,0),im.size,max_nro_of_colors,0)
    im.save(savename)

def gaussian_blur(filename,savename,distance):
    im=Image.open(filename)
    blurred_image=im.filter(ImageFilter.GaussianBlur(distance))
    blurred_image.save(savename)

def simple_blur_diffusion(filename,simplifying_divisions:int,iterations:int,max_nro_of_colors:int):
    fileim=Image.open(filename)
    (width,height)=fileim.size
    shrinking_amount=1+round((width+height)/200)
    shrinked_image_pixel_map(filename,"shrink1.png",shrinking_amount,simplifying_divisions) #this is what we use at the end
    im=Image.open("shrink1.png")
    pixel_map=im.load()
    shrinked_image_pixel_map("shrink1.png","shrink2.png",4,simplifying_divisions) #it is further shrinked
    (width,height)=im.size
    for i in range(int(iterations/2)):
        blur_file("shrink2.png","shrink2.png")
    enlarged_image_pixelmap("shrink2.png","shrink2.png",2)
    for i in range(int(iterations/4)):
        blur_file("shrink2.png","shrink2.png")
    enlarged_image_pixelmap("shrink2.png","shrink2.png",2)
    for i in range(int(iterations/4)):
        blur_file("shrink2.png","shrink2.png")
        pixel_combination("shrink2.png","shrink1.png",0.9,0.1,"shrink2.png")
    im=Image.open("shrink1.png")
    pixel_map=im.load()
    (width,height)=im.size
    force_n_colors(pixel_map,(0,0),(width,height),max_nro_of_colors,0)
    im.save("shrink2.png")
    all_just_one_color_pngs("shrink2.png","just_one",max_nro_of_colors)
    return "just_one"



#give a list of rgb-colors, this returns an aaverage of those colors (in rgb also)
def rgb_color_average(color_array:List[List[float]]):
    red=0
    green=0
    blue=0
    for i in range(len(color_array)):
        red += color_array[i][0]
        green += color_array[i][1]
        blue += color_array[i][2]
    return (int(red/len(color_array)),int(green/len(color_array)),int(blue/len(color_array)))

#what is the average color of rectangle
def average_color_of_rectangle(filename,min_x,max_x,min_y,max_y):
    im = Image.open(filename) # Can be many different formats.
    pix = im.load()
    (width,height)=im.size
    if min_x<0 or min_y<0 or max_x>width or max_y>height:
        raise ValueError("Stupid values, try better")
    redsum=0
    greensum=0
    bluesum=0
    pixel_total=0
    for i in range(min_x,max_x):
        for j in range(min_y,max_y):
            pixel_total +=1
            redsum += pix[i,j][0]
            greensum += pix[i,j][1]
            bluesum += pix[i,j][2]
    if pixel_total==0:#if triangle is very small, we just take the pixel color from closest point
        return (pix[min(width-1,max_x),min(height-1,max_y)][0],pix[min(width-1,max_x),min(height-1,max_y)][1],pix[min(width-1,max_x),min(height-1,max_y)][2]) #there used to be grey color
    else:
        return (int(redsum/pixel_total),int(greensum/pixel_total),int(bluesum/pixel_total))

#given vertices of polygon, returns average color inside it in the file
#we also return the size, since it is important to add smallest polygons last
def average_color_and_size_of_polygon(filename,poly_vertices):
    #save_png_copy_as(filename,"copy.png")
    im = Image.open(filename) # Can be many different formats.
    pix=im.load()
    (width,height)=im.size
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.polygon(poly_vertices, fill=(0,0,0))
    # Save the image as a PNG file
    image.save("machinery/polygon.png")
    # Close the image
    image.close()
    polyim=Image.open("machinery/polygon.png")
    polypix = polyim.load()
    total_colored=0
    total_red=0
    total_green=0
    total_blue=0
    for i in range(width):
        for j in range(height):
            if polypix[i,j][0]<100: #100 is little random, we just pick some value between 0 and 255
                total_colored += 1
                add_color=pix[i,j]
                total_red +=add_color[0]
                total_green +=add_color[1]
                total_blue +=add_color[2]
    if total_colored==0:
        total_colored=1 #prevent division by zero
    average_col=(round(total_red/total_colored),round(total_green/total_colored),round(total_blue/total_colored))
    return [average_col,total_colored]

#what is the average color of file, probably gives wrong answer, maybe should be divided by three?
def average_color_of_file(filename):
    im = Image.open(filename) # Can be many different formats.
    (width,height)=im.size
    return average_color_of_rectangle(filename,0,width,0,height)

def triangle_color_variance(point1,point2,point3,filename):
    average_color=triangle_average_color(point1,point2,point3,filename)
    im = Image.open(filename) # Can be many different formats.
    pix = im.load()
    (width,height)=im.size
    min_x=min(point1[0],point2[0],point3[0],width)
    max_x=max(point1[0],point2[0],point3[0],1)
    min_y=min(point1[1],point2[1],point3[1],height)
    max_y=max(point1[1],point2[1],point3[1],1)
    variance=0
    pixel_total=0
    for i in range(min_x,max_x):
        for j in range(min_y,max_y):
            if Geometry.is_it_in_triangle((i,j),point1,point2,point3):
                pixel_total +=1
                variance += math.pow(pix[i,j][0]-average_color[0],2)+math.pow(pix[i,j][1]-average_color[1],2)+math.pow(pix[i,j][2]-average_color[2],2)
    if pixel_total==0:#if triangle is very small, we just take the pixel color from closest point
        return 0
    else:
        return (variance/pixel_total)


def triangle_variance_estimator(point1,point2,point3,quality,filename):
    im = Image.open(filename) # Can be many different formats.
    pix = im.load()
    (width,height)=im.size
    min_x=min(point1[0],point2[0],point3[0],width)
    max_x=max(point1[0],point2[0],point3[0],1)
    min_y=min(point1[1],point2[1],point3[1],height)
    max_y=max(point1[1],point2[1],point3[1],1)
    color_list=[]
    average_color=[128,128,128]
    variance=0
    pixel_total=0
    redsum=0
    greensum=0
    bluesum=0
    for i in range(round(quality*max((max_x-min_x),(max_y-min_y)))):
        test_x=min_x+int(random.random()*(max_x-min_x))
        test_y=min_x+int(random.random()*(max_y-min_y))
        if Geometry.is_it_in_triangle((test_x,test_y),point1,point2,point3):
            pixel_total +=1
            color_list.append(pix[test_x,test_y])
    if pixel_total>0:
        average_color=(int(redsum/pixel_total),int(greensum/pixel_total),int(bluesum/pixel_total)) 

    for i in range(len(color_list)):
        variance += math.pow(color_list[i][0]-average_color[0],2)
        variance += math.pow(color_list[i][1]-average_color[1],2)
        variance += math.pow(color_list[i][2]-average_color[2],2)
    if pixel_total>0:
        variance=variance/pixel_total
    else:
        variance=0
    return variance



#returns all_colors that are in the given pixel map, this are given with most popular color first
def all_colors_in_pixel_map(pix,width,height):
    color_dict=color_dict_of_pixel_map(pix,(0,0),(width,height))
    sorted_color_dict=sorted_dict_from_dictionary(color_dict)
    all_colors=[]
    for i in range(len(sorted_color_dict)):
        all_colors.append(sorted_color_dict[i][0])
    return all_colors

#loads a file 'filename' and saves all of its colors separately in own files called savename+str(i)+".png"
def all_just_one_color_pngs(filename,savename,limit_nro):
    im=Image.open(filename)
    pix = im.load()
    (width,height)=im.size
    all_colors=all_colors_in_pixel_map(pix,width,height)
    for i in range(min(len(all_colors),limit_nro)):
        just_one_color_png(filename,savename+str(i)+".png",all_colors[i],5)
    

#loading png with filename, produces a png, with white color, and only the pixels near the 'color' to be drawn as usual
def just_one_color_png(filename,savename,color,gap):
    im=Image.open(filename)
    pix = im.load()
    (width,height)=im.size
    image = Image.new("RGB", (width, height), "white")
    pix2 = image.load()
    for x in range(0,width):
        for y in range(0,height):
            if closest_color_distance(pix[x,y],[color])<gap:
                pix2[x,y]=pix[x,y]
    image.save(savename)

#produces a png, which describes the contrast in the original image
#  quality tells how exact value we find fo contrast, cdist tells how far away points we compare
def contrast_png(filename,savename,quality:int,cdist:int):
    im=Image.open(filename)
    pix = im.load()
    (width,height)=im.size
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    for x in range(0,width):
        for y in range(0,height):
            test_point=(x,y)
            j=0
            t_value=0
            while j in range(quality): #searching from neighbourhood of test_point, we eventually find quality number of points
                #against which we compare color of test_point. Note that in this loop, we could also have chosen some constant number
                #of iterations (like 10) instead of quality
                near_test_point= (test_point[0]-cdist+int(random.random()*2*cdist),test_point[1]-cdist+int(random.random()*2*cdist))
                if near_test_point[0] in range(0,width) and near_test_point[1] in range(0,height): 
                    j+=1
                    t_value +=contrast_amount(pix[test_point[0],test_point[1]],pix[near_test_point[0],near_test_point[1]]) #contrast in x-direction 3step
            draw.polygon([(x,y),(x,y+1),(x+1,y+1),(x+1,y)], fill=(min(255,int(0.06*t_value/quality)),0,0))
    # Save the image as a PNG file
    #filename=filename_end(filename)
    #where_saved="pngs\\redline.png" old name was this
    image.save(savename)
    # Close the image
    image.close()

#produces a png, which has black pixels in the places where color changes and white elsewhere
#  color_gap tells how much color needs to change to produce a black pixel
def simple_contrast_png(filename,savename,color_gap:int):
    im=Image.open(filename)
    pix = im.load()
    (width,height)=im.size
    image = Image.new("RGB", (width, height), "white")
    pix2=image.load()
    draw = ImageDraw.Draw(image)
    for x in range(0,width):
        for y in range(0,height):
            test_point=(x,y)
            n_points=[boxify(0,width,0,height,(x-1,y)),boxify(0,width,0,height,(x,y-1))]
            for near_test_point in n_points:
                if color_distance(pix[test_point[0],test_point[1]],pix[near_test_point[0],near_test_point[1]])>color_gap:    
                    pix2[x,y]=(0,0,0)
    # Save the image as a PNG file
    image.save(savename)
    # Close the image
    image.close()

#meant to take black pixels of without changing the "topology" of black pixels
def extra_black_off(filename,savename):
    im=Image.open(filename)
    pix = im.load()
    (width,height)=im.size
    for x in range(2,width-2):
        for y in range(2,height-2):
            test_point=(x,y)
            lu_points =[boxify(0,width,0,height,(x,y-1)),boxify(0,width,0,height,(x-1,y-1)),boxify(0,width,0,height,(x-1,y))]
            ru_points =[boxify(0,width,0,height,(x,y-1)),boxify(0,width,0,height,(x+1,y-1)),boxify(0,width,0,height,(x+1,y))]
            ld_points =[boxify(0,width,0,height,(x,y+1)),boxify(0,width,0,height,(x-1,y+1)),boxify(0,width,0,height,(x-1,y))]
            rd_points =[boxify(0,width,0,height,(x,y+1)),boxify(0,width,0,height,(x+1,y+1)),boxify(0,width,0,height,(x+1,y))]
            take_off= False
            if pix[x,y]==(0,0,0):
                take_off=True
            if take_off:
                cond1=True
                cond2=True
                for i in [1,2]:
                    if pix[lu_points[0][0],lu_points[0][1]]!=pix[lu_points[i][0],lu_points[i][1]]:
                        cond1=False
                    if pix[rd_points[0][0],rd_points[0][1]]!=pix[rd_points[i][0],rd_points[i][1]]:
                        cond1=False
                for i in [1,2]:
                    if pix[ru_points[0][0],ru_points[0][1]]!=pix[ru_points[i][0],ru_points[i][1]]:
                        cond2=False                    
                    if pix[ld_points[0][0],ld_points[0][1]]!=pix[ld_points[i][0],ld_points[i][1]]:
                        cond2=False

            if take_off and (cond1 or cond2):
                pix[x,y]=(255,255,255) 
    im.save(savename)
    im.close() 


#if  pix[i,j] and pix[i+1,j+1] are same color, but they aren't connected by pixel of same color in pix[i+1,j] or pix[i,j+1]
#they are either glued or one of them is recolored
def kosumis_off(filename,savename):
    nro_of_operations=0
    im=Image.open(filename)
    pix=im.load()
    (width,height)=im.size 
    #if kosumi is in 135 angle:
    for i in range(1,width-1):
        for j in range(1,height-2):
            fix_condition= (pix[i,j]==pix[i+1,j+1] and pix[i,j] not in [pix[i,j+1],pix[i+1,j]])
            if fix_condition:
                nro_of_operations += 1
                dl_condition= (pix[i-1,j+1]==pix[i,j+2] and  pix[i-1,j+1]==pix[i,j+1]  and pix[i-1,j+2] !=pix[i-1,j+1])
                #if dl condition is true, then glueing in fix condition might destroy another glueing in down left from kosumi
                if dl_condition==False:
                    pix[i,j+1]=pix[i,j]
                else:
                    new_red=int((pix[i,j-1][0]+pix[i+1,j][0])/2)
                    new_green=int((pix[i,j-1][1]+pix[i+1,j][1])/2)
                    new_blue=int((pix[i,j-1][2]+pix[i+1,j][2])/2)
                    pix[i,j]=(new_red,new_green,new_blue) #we cghange the pixel to middle color thus cutting the connection
                    if pix[i,j]==pix[i+1,j+1]: #in a very unlikely scenario, this average is the old color, then we change it again:
                        pix[i,j]=(int(new_red/2),int(new_green/2),int(new_blue/2))
    #if kosumi is in angle 45 
    for i in range(1,width-1):
        for j in range(1,height-2):
            fix_condition= (pix[i+1,j]==pix[i,j+1] and pix[i+1,j] not in [pix[i,j],pix[i+1,j+1]])
            if fix_condition:
                nro_of_operations += 1
                dl_condition= (pix[i-1,j]==pix[i,j] and  pix[i,j+1]==pix[i,j]  and pix[i-1,j-1] !=pix[i,j])
                #if dl condition is true, then glueing in fix condition might destroy another glueing in down left from kosumi
                if dl_condition==False:
                    pix[i,j]=pix[i+1,j]
                else:
                    new_red=int((pix[i,j+2][0]+pix[i+1,j+1][0])/2)
                    new_green=int((pix[i,j+2][1]+pix[i+1,j+1][1])/2)
                    new_blue=int((pix[i,j+2][2]+pix[i+1,j+1][2])/2)
                    pix[i,j+1]=(new_red,new_green,new_blue) #we cghange the pixel to middle color thus cutting the connection
                    if pix[i,j+1]==pix[i+1,j]: #in a very unlikely scenario, this average is the old color, then we change it again:
                        pix[i,j+1]=(int(new_red/2),int(new_green/2),int(new_blue/2))
    im.save(savename)


#this takes photo and overwrites it with cartooned version of it
#parameters are parameters for making this photo
#possible styles are currently "polygon,rectangle,triangle and simple". Simple doesn't produce txt.file at all is just blurs and colors
#with operations that make photo simpler
#contrast_points is relevant only for triangle and rectangle styles
def from_photo_to_cartoon(filename,prop:PngProperties,savename=None):
    pd=prop.png_dict
    back_prop=standard_back(pensize=pd["pensize"],style=pd["style"]) #for making backround without unintended white areas in the video
    
    back_file_name="drawings\\backhelpthing.txt"
    back_save_name=""
    if pd["style"]=="polygon":
        back_save_name=png_to_polygon_Drawing(filename,back_prop,savename=back_file_name)
    if pd["style"] in ["rectangle","triangle"]:
        back_save_name=from_png_to_Drawing(filename,prop,savename=back_file_name)
    #this both saves the file and
    
    saved_as="" #if type uses txt.file step to create image, the name of text file is stored here
    if pd["style"] in ["polygon","rectangle","triangle"]:
        if pd["style"]=="polygon":
            saved_as=png_to_polygon_Drawing(filename,prop,savename)
        if pd["style"] in ["rectangle","triangle"]:
            saved_as=from_png_to_Drawing(filename,prop,savename)
        #now original photo is changed to str, representing a drawing 
        back_str=load_text_file(back_save_name)# this is new
        file_str=load_text_file(saved_as)
        file_str=back_str+file_str.strip("£")#this is new
        drawi=Geometry.Drawing(file_str)
        [point1,point2]=drawi.placement()
        top_left=(point1[0],point2[1]) #these point needs to be chosen stupidy, i.e. this kind of top_right corner actually
        bottom_right=(point2[0],point1[1]) #and this is bottom_left, this is due to y-coordinate direction differences in png and turtle
        width=abs(point1[0]-point2[0])
        height=abs(point1[1]-point2[1])
        filename=filename[:filename.rfind(".")]
        #the style in next command is different style than the one in this method before
        if savename==None:
            savename=filename
        draw_drawing(file_str,width,height,topleft=top_left,bg_color=(1,1,1),save_name=filename,style="basic") #save_name used to be savename, changed it in 16.2.
    
    else: #this means that style is "simple", but if invalid style name is used, then simple is a default chosice
        if savename==None:
            savename=filename
        photo_to_simplified_png(filename,savename,prop)
    #it is important that savename=filename, when savename is not given as parameter, in this way the original photo is destroyed
    return savename


#this takes a (png)photo and creates another png which is a simplified version of this
#this simplified version is saved in savename
def photo_to_simplified_png(filename,savename,prop:PngProperties):
    fileim=Image.open(filename)
    (original_width,original_height)=fileim.size #going to need this later
    modified_file= "machinery/pmodified.png"
    shrinked_file="machinery/phelp.png"
    pd=prop.png_dict
    if pd["detail_level"]>10:
        pd["detail_level"]=10
    if pd["detail_level"]<1:
        pd["detail_level"]=1
    shrinked_size=50*pd["detail_level"]
    enlarged_image_pixelmap(filename,shrinked_file,shrinked_size/(original_width+original_height))
    gaussian_blur(shrinked_file,"machinery/gaussian3.png",distance=3)
    original_percentage=math.sqrt(pd["color_divisions"]/100) #this tells how much original image "shows" in the en result compared to blur
    if original_percentage>1:
        original_percentage=1
    if original_percentage<0:
        original_percentage=0
    pixel_combination(shrinked_file,"machinery/gaussian3.png",original_percentage,1-original_percentage,"machinery/gaussian3.png")
    gaussian_blur(shrinked_file,"machinery/gaussian3.png",distance=2)
    #detail_level-dependece in the next command might need removing

    pixel_combination(shrinked_file,"machinery/gaussian3.png",original_percentage,1-original_percentage,"machinery/gaussian3.png")
    percentage_mutation("machinery/gaussian3.png",modified_file,pd["iterations"],pd["percentage"])
    shrink_and_simplify(modified_file,modified_file,pd["color_divisions"],pd["max_nro_of_colors"],max_size=shrinked_size)
    resize_png(modified_file,modified_file,prop) #here we resize the image if prop values suggest so
    save_png_copy_as(modified_file,savename)

#resize the png to new size givebby prop, (if prophas None parametersin end_width and end_height, nothing happens)
def resize_png(filename,savename,prop:PngProperties):
    im=Image.open(filename)
    (width,height)=im.size
    end_width=prop.get("end_width")
    end_height=prop.get("end_height")
    new_image=None
    if width<1 or height<1: #one dimensionis two small to resize
        return
    if end_width != None and end_height==None:
        new_image=im.resize((end_width, int(height*end_width/width)))
    if end_width == None and end_height !=None:
        new_image=im.resize((int(width*end_height/height), end_height))
    if end_width != None and end_height != None:
        new_image=im.resize((end_width, end_height))
    new_image.save(savename)


#simplifies png:s colors and makes polygons that follow contour lines of colors
# percentage_limit tells how many percentage there must be certain color in order to not be reomved       
def photo_to_polygons(filename,prop:PngProperties):
    pd=prop.png_dict

    fileim=Image.open(filename)
    (original_width,original_height)=fileim.size #going to need this later
    modified_file= "machinery/pmodified.png"
    shrinked_file="machinery/phelp.png"
    if pd["detail_level"]>10:
        pd["detail_level"]=10
    if pd["detail_level"]<1:
        pd["detail_level"]=1
    shrinked_size=50*pd["detail_level"]
    enlarged_image_pixelmap(filename,shrinked_file,shrinked_size/(original_width+original_height))
    gaussian_blur(shrinked_file,"machinery/gaussian3.png",distance=3)
    original_percentage=math.sqrt(pd["color_divisions"]/100) #this tells how much original image "shows" in the en result compared to blur
    if original_percentage>1:
        original_percentage=1
    if original_percentage<0:
        original_percentage=0
    pixel_combination(shrinked_file,"machinery/gaussian3.png",original_percentage,1-original_percentage,"machinery/gaussian3.png")
    gaussian_blur(shrinked_file,"machinery/gaussian3.png",distance=2)
    #detail_level-dependece in the next command might need removing

    pixel_combination(shrinked_file,"machinery/gaussian3.png",original_percentage,1-original_percentage,"machinery/gaussian3.png")
    percentage_mutation("machinery/gaussian3.png",modified_file,pd["iterations"],pd["percentage"])
    shrink_and_simplify(modified_file,modified_file,pd["color_divisions"],pd["max_nro_of_colors"],max_size=shrinked_size)
    whiten_contour(modified_file,modified_file,2)
    for i in range(5):
        kosumis_off(modified_file,modified_file)

    poly_dict=extract_polygons_from_file(modified_file,shrinked_file,pd["pensize"],edge_length=int(1+pd["min_line_length"]/3)) 
    #3 in the last command should be the same as enlarging factor in png_to_p... to make min_line_length logical

    final_dict_of_polygons={}#here we list all the polygons that are sufficiently large size, 
    for poly in poly_dict.keys():
        if poly_dict[poly]>min(3,pd["min_line_length"]):#This value 3 is little random. it means minimum size of the polygon that is drawn and not leaved white
            final_dict_of_polygons[poly]=poly_dict[poly]

    list_of_polygons=sorted_list_from_dictionary(final_dict_of_polygons) #this list is now organized in such away that smallest polygons are last
    return list_of_polygons



#here filename and average_file are two png.files (jpg probably ok) with same size, 
#method returns a dictionary of {polygon:size of the polygon}, with polygons contours from the filename and colors from average_file
# usually the idea is that filename is a file which is blurred and handled to make it a simpler version of average file
def extract_polygons_from_file(filename,average_file,pensize,edge_length):
    im=Image.open(filename)
    copyfile="polycopy.png"
    whiten_contour(filename,filename,2)#just in case
    save_png_copy_as(filename,copyfile)
    pixc=im.load()
    (width,height)=im.size
    poly_dict={}
    i=0

    for x in range(3,width-3):
        for y in range(3,height-3):
            starting_point=(x,y)
            start_color=pixc[starting_point[0],starting_point[1]]
            poly_size=0 #here this is just to reduce if clauses inside other
            rgb_fillcolor=(100,100,0) #totally random value, shouldn't get used 
            if pixel_color_in(copyfile,starting_point)!=(255,255,255):
                poly=find_and_make_edge(filename,color_gap=1,starting_point=starting_point,edge_lenght=edge_length,reduction=True) 
                [rgb_fillcolor,poly_size]= average_color_and_size_of_polygon(average_file,poly.vertices())
                fillcolor=(rgb_fillcolor[0]/256,rgb_fillcolor[1]/256,rgb_fillcolor[2]/256)
                poly.inside_color=fillcolor
                poly.set_pencolor(fillcolor)#contour color is now changed equal to fillcolor
                poly.set_thickness=pensize#thickness for all contour_lines in polygon
                poly_dict[poly]=poly_size
                i += 1
                paint_area(copyfile,copyfile,starting_point,(255,255,255),1)
    return poly_dict




#if point is outside of a box(minx,maxx,miny,maxy) this returns a point, which is inside
def boxify(minx,maxx,miny,maxy,point):
    result_point=point
    if result_point[0]<minx:
        result_point=(minx,result_point[1]) 
    if result_point[0]>=maxx:
        result_point=(maxx-1,result_point[1]) 
    if result_point[1]<miny:
        result_point=(result_point[0],miny) 
    if result_point[1]>=maxy:
        result_point=(result_point[0],maxy-1)
    return result_point

#muuttaa värityypin kolmikosta oudoksi hexatyypiksi
def hexagesimal_color(r:float,g:float,b:float):
    redint=int(255.9*r)#this idea of 255.9 instead of 256 is to try to stop the possible error with value 256
    greenint=int(g*255.9)#not tested yet
    blueint=int(b*255.9)
    return "#%02x%02x%02x" % (redint,greenint,blueint) 

#y-coordinates in vertice-list are turned upside down
def vertice_y_flip(vertice_list):
    result=[]
    for vertice in vertice_list:
        result.append((vertice[0],-vertice[1]))
    return result

#returns a list of vertice points shifted by the amount of shiftpoint (which has two components) 
def vertice_shift(vertice_list,shiftpoint):
    result=[]
    for vertice in vertice_list:
        result.append((vertice[0]+shiftpoint[0],vertice[1]+shiftpoint[1]))
    return result    

#returns a list of vertice points shifted by the amount of shiftpoint (which has two components) 
def point_shift(point,shiftpoint):
    return (point[0]+shiftpoint[0],point[1]+shiftpoint[1])

#y-coordinates in vertice-list are turned upside down
def point_y_flip(point):
    return (point[0],-point[1])


def zero_color_mn_array(m:int,n:int):
    result=[]
    for i in range(m):
        result.append([0,0,0]*n)
    return result




#makes 'iterations' number of tries to change file to more unicolor i.e.
#we choose random boxes of size 'box_size' and if there is lot of the same color
#other pixels inside that box are changed on this same color
def unicolor_mutation(filename,box_size:int,iterations):
    im = Image.open(filename) # Can be many different formats.
    pix = im.load()
    (width,height)=im.size
    for i in range(0,iterations):
        topleft_point=(int(random.random()*(width-box_size)),int(random.random()*(height-box_size)))
        bottomright_point=(topleft_point[0]+box_size,topleft_point[1]+box_size)
        unicolor_mutation_step(pix,topleft_point,bottomright_point)
    im.save("unicolor.png")


#takes a pixel map (usually from file) and changes this pixel_map inside rectangle topleft_point x bottomright_point
#so that every pixel is changed to the color of one of the most_popular_colors in the original pixel_map 
#inside this rectangle
#contour_thickness tells how big contourline there is that isnot affected by color change. Set 0, if you want all to be affected
def force_n_colors(pixel_map,topleft_point,bottomright_point,number_of_colors,contour_thickness:int):
    color_dict=color_dict_of_pixel_map(pixel_map,topleft_point,bottomright_point)
    color_list=sorted_dict_from_dictionary(color_dict)
    min_gap=400/math.sqrt(number_of_colors) #colors must be at least this distance from each others
    available_colors=[] #here we list most popular colors 
    cond=True
    i=0
    while cond:
        if closest_color_distance(color_list[i][0],available_colors)>min_gap:
            available_colors.append(color_list[i][0])
        i+=1
        if i >= len(color_list) or len(available_colors)>=number_of_colors:
            cond=False

    for i in range(topleft_point[0]+contour_thickness,bottomright_point[0]-contour_thickness):
        for j in range(topleft_point[1]+contour_thickness,bottomright_point[1]-contour_thickness):
            pixel_map[i,j]=closest_color(pixel_map[i,j],available_colors)
    return pixel_map

#just returns the color of pixel in location 'point'
def pixel_color_in(filename,point):
    im=Image.open(filename)
    pix=im.load()
    return pix[point[0],point[1]]

#returns how far 'this_color' is from 'color'. The larger the value, the further from each other the colors are
def color_distance(this_color,color):
    return abs(this_color[0]-color[0])+abs(this_color[1]-color[1])+abs(this_color[2]-color[2])

#given an rgb color 'this_color' return a color that is closest to it in the list of (rgb)colors 'color_list' 
def closest_color(this_color,color_list):
    best_distance=10000
    result_color=this_color
    for color in color_list:
        try_distance=abs(this_color[0]-color[0])+abs(this_color[1]-color[1])+abs(this_color[2]-color[2])
        if try_distance<best_distance:
            best_distance=try_distance
            result_color=color
    return result_color

#given an rgb color 'this_color' returns a (color)distance of this_color to closest color_in_the_list in the list of (rgb)colors 'color_list' 
def closest_color_distance(this_color,color_list):
    best_distance=10000
    result_color=this_color
    for color in color_list:
        try_distance=abs(this_color[0]-color[0])+abs(this_color[1]-color[1])+abs(this_color[2]-color[2])
        if try_distance<best_distance:
            best_distance=try_distance
            result_color=color
    return best_distance


#changes the color of the pixels in box topleft_point to bottomright_point, if at least 60% pixels are the same color
#the contour-colors of the box aren't changed
def unicolor_mutation_step(pixel_map,topleft_point,bottomright_point):
    number_of_points=(bottomright_point[0]-topleft_point[0])*(bottomright_point[1]-topleft_point[1])
    color_dict=color_dict_of_pixel_map(pixel_map,topleft_point,bottomright_point)
    color_list=sorted_dict_from_dictionary(color_dict)
    if color_list[0][1]/number_of_points>0.6: #i.e. if 60% or more pixel are the same color
        untouch_x=int((bottomright_point[0]-topleft_point[0]+1)/3) #we leave some contour which color is not changed
        untouch_y=int((bottomright_point[1]-topleft_point[1]+1)/3)
        inside_topleft=(topleft_point[0]+untouch_x,topleft_point[1]+untouch_y)
        inside_bottomright=(bottomright_point[0]-untouch_x,bottomright_point[1]-untouch_y)
        pixel_map=pixelmap_box_to_color(pixel_map,inside_topleft,inside_bottomright,color_list[0][0])
    return pixel_map

#changes the color inside pixel map to the color 'color'
def pixelmap_box_to_color(pixel_map,topleft_point,bottomright_point,color:List[float]):
    for i in range(topleft_point[0],bottomright_point[0]):
        for j in range(topleft_point[1],bottomright_point[1]):
            pixel_map[i,j]=color
    return pixel_map


#returns a dictionary of number of different colors in file inside box with corners topleft_point and bottomright_point
def color_dict_of_box(filename,topleft_point,bottomright_point):
    im = Image.open(filename) # Can be many different formats.
    pix = im.load()
    (width,height)=im.size
    if topleft_point[0] not in range(0,width) or topleft_point[1] not in range(0,height):
        raise ValueError("point outside")
    if bottomright_point[0] not in range(0,width) or bottomright_point[1] not in range(0,height):   
        raise ValueError("point outside")
    return color_dict_of_pixel_map(pix,topleft_point,bottomright_point)


#returns a dictionary which tells for color how many pixels there are with that color
def color_dict_of_pixel_map(pix,topleft_point,bottomright_point):
    color_dict={}
    for i in range(topleft_point[0],bottomright_point[0]):
        for j in range(topleft_point[1],bottomright_point[1]):
            pixel_color=pix[i,j]
            if pixel_color in color_dict.keys():
                color_dict[pixel_color] += 1
            else:
                color_dict[pixel_color]=1
    return color_dict

#we remove all colors that are rare in this given area. Pixels that are closer to the edge of area are not changed
def percentage_mutation_step(pix,topleft_point,bottomright_point,percentage_limit,contour_width):
    color_dict=color_dict_of_pixel_map(pix,topleft_point,bottomright_point)
    sorted_color_dict=sorted_dict_from_dictionary(color_dict)
    size_of_area=abs(topleft_point[0]-bottomright_point[0])*abs(topleft_point[1]-bottomright_point[1])
    colors_to_keep=[]
    for i in range(len(sorted_color_dict)):
        percentage=sorted_color_dict[i][1]/size_of_area
        if percentage>percentage_limit:
            colors_to_keep.append(sorted_color_dict[i][0])

    for i in range(topleft_point[0]+contour_width,bottomright_point[0]-contour_width):
        for j in range(topleft_point[1]+contour_width,bottomright_point[1]-contour_width):
            if pix[i,j] not in colors_to_keep:
                which_side=int(4*random.random())
                if which_side==0:
                    pix[i,j]=pix[i-1,j]
                if which_side==1:
                    pix[i,j]=pix[i+1,j]
                if which_side==2:
                    pix[i,j]=pix[i,j-1]
                if which_side==3:
                    pix[i,j]=pix[i,j+1]

#we pick random areas from which we remove pixels that are too rare
def percentage_mutation(filename,savename,iterations:int,percentage_limit:float):
    im = Image.open(filename) # Can be many different formats.
    pix = im.load()
    (width,height)=im.size
    max_box_size=int(min(width,height)/math.pow(iterations,0.25))
    for i in range(iterations):
        box_size=int((1+random.random())*max_box_size/3)
        topleft_point=(int(random.random()*(width-box_size)),int(random.random()*(height-box_size)))
        bottomright_point=(topleft_point[0]+box_size,topleft_point[1]+box_size)
        topleft_point=boxify(0,width-1,0,height-1,topleft_point)
        bottomright_point=boxify(0,width-1,0,height-1,bottomright_point)
        percentage_mutation_step(pix,topleft_point,bottomright_point,percentage_limit,int(1+box_size/6))
    im.save(savename)


#produces a smaller pixel map of png file simplyfying_divisions tells how exact the color is
def shrinked_image_pixel_map(filename,savename,times:int,simplifying_divisions:int):
    im = Image.open(filename) # Can be many different formats.
    pix = im.load()
    (width,height)=im.size
    new_width=int(width/times)
    new_height=int(height/times)
    result_pix=zero_color_mn_array(new_height,new_width)#+1's added 15.10 but taken away 21.10
    for i in range(new_width*times):#changes from 3 to 4 in 10.10.
        for j in range(new_height*times): #accumalating pixel colors and finding their average changed -3 to -6 in 10.10.
            result_pix[int(j/times)][3*int(i/times)] +=  (pix[i,j][0])/(times*times)
            result_pix[int(j/times)][3*int(i/times)+1] += (pix[i,j][1])/(times*times)
            result_pix[int(j/times)][3*int(i/times)+2] += (pix[i,j][2])/(times*times)
    
    for i in range(len(result_pix)):
        for j in range(len(result_pix[0])): #only point is to make values int
            result_pix[i][j]=int(result_pix[i][j])
            if simplifying_divisions in range(1,254):
                result_pix[i][j]=simplify_rgb_color_component(result_pix[i][j],simplifying_divisions)

            #result_pix[i][j]=int(result_pix[i][j])#why there was this same for three times? now removed it
            #result_pix[i][j]=int(result_pix[i][j])

    with open(savename, 'wb') as f: #took +.png away 21.10.
        w = png.Writer(int(len(result_pix[0])/3),len(result_pix),greyscale=False)
        w.write(f, result_pix)


#enlarges a picture by factor 'times' (can also shrink)
def enlarged_image_pixelmap(filename,savename,times:float):
    im = Image.open(filename) # Can be many different formats.
    pix = im.load()
    (width,height)=im.size
    new_width=int(width*times)
    new_height=int(height*times)
    result_pix=zero_color_mn_array(new_height,new_width)#+1's added 15.10 but taken away 21.10
    for i in range(new_width):
        for j in range(new_height): #accumalating pixel colors and finding their average.
            result_pix[j][3*i] =  (pix[int(i/times),int(j/times)][0])
            result_pix[j][3*i+1] = (pix[int(i/times),int(j/times)][1])
            result_pix[j][3*i+2] = (pix[int(i/times),int(j/times)][2])
    
    for i in range(len(result_pix)):
        for j in range(len(result_pix[0])): #only point is to make values int
            result_pix[i][j]=int(result_pix[i][j])
            #if simplifying_divisions in range(1,254):
            #    result_pix[i][j]=simplify_rgb_color_component(result_pix[i][j],simplifying_divisions)

    with open(savename, 'wb') as f: #took +.png away 21.10.
        w = png.Writer(int(len(result_pix[0])/3),len(result_pix),greyscale=False)
        w.write(f, result_pix)

#this takes a list of points, makes them into triangles and returns a Drawing object which can be used to save a drawing file
def triangle_list_to_drawing(point_list,filename,picture_average_color,prop:PngProperties):
    pd=prop.png_dict
    times=pd["shrinking_factor"]
    im = Image.open(filename) # Can be many different formats.
    (width,height)=im.size
    triangle_list=non_overlapping_triangles(point_list,width,height,pd["min_angle"],pd["percentage"],filename)
    drawi=Geometry.Drawing("")
    for j in range(len(triangle_list)):
        point1=triangle_list[j][0]
        point2=triangle_list[j][1]
        point3=triangle_list[j][2]
        shrpoint1=(int(point1[0]/times),int(point1[1]/times))
        shrpoint2=(int(point2[0]/times),int(point2[1]/times))
        shrpoint3=(int(point3[0]/times),int(point3[1]/times))
        triangle_color=triangle_average_color(shrpoint1,shrpoint2,shrpoint3,"shrink.png")
        pen_color=(triangle_color[0]/256,triangle_color[1]/256,triangle_color[2]/256)
        if pd["color_divisions"]>0:
            pen_color=simplify_color(pen_color,pd["color_divisions"])
        vertice_array=[(point1[0],-point1[1]),(point2[0],-point2[1]),(point3[0],-point3[1])]
        thickness=pd["pensize"]
        poly=Geometry.Polygon()
        #poly.inside_color=contrast_shift_transformation(pen_color,end_contrast) #used to be just pen_color as the next line NOTe OLD
        poly.inside_color=anti_gray_function(pen_color,pd["end_contrast"],picture_average_color) # this sets picture average_color to
        #be stable and changes other colors closer or further away from it depending on how positive or negative end_contrast is
        poly.verticise(vertice_array,thickness,contrast_shift_transformation(pen_color,pd["end_contrast"],picture_average_color),True,True)
        drawi.add_polygon(poly)
    return drawi


#this takes a list of points, makes them into rectangles and returns a Drawing object which can be used to save a drawing file
def rectangle_list_to_drawing(point_list,filename,picture_average_color,prop:PngProperties):
    pd=prop.png_dict
    times=pd["shrinking_factor"]
    first_side_factor=50/len(point_list) #this might be better to include as parameter, let's see later if this needs to be changed
    im = Image.open(filename) # Can be many different formats.
    (width,height)=im.size
    rectangle_list=[((0,0),(width,0),(width,height),(0,height))]
    for i in range(len(point_list)):
        min_side=int(first_side_factor*(len(point_list)-i))+pd["min_line_length"]#
        #than this
        first_point=(max(0,point_list[i][0]-min_side),max(0,point_list[i][1]-min_side))
        second_point=(min(width,point_list[i][0]+min_side),max(0,point_list[i][1]-min_side))
        third_point=(min(width,point_list[i][0]+min_side),min(height,point_list[i][1]+min_side))
        fourth_point=(max(0,point_list[i][0]-min_side),min(height,point_list[i][1]+min_side))
        rectangle_list.append((first_point,second_point,third_point,fourth_point))
    drawi=Geometry.Drawing("")
    for j in range(len(rectangle_list)):
        point1=rectangle_list[j][0]
        point2=rectangle_list[j][1]
        point3=rectangle_list[j][2]
        point4=rectangle_list[j][3]
        shrpoint1=(int(point1[0]/times),int(point1[1]/times))
        shrpoint2=(int(point2[0]/times),int(point2[1]/times))
        shrpoint3=(int(point3[0]/times),int(point3[1]/times))
        shrpoint4=(int(point4[0]/times),int(point4[1]/times))
        rectangle_color=average_color_of_rectangle("shrink.png",shrpoint1[0],shrpoint3[0],shrpoint1[1],shrpoint3[1])
        pen_color=(rectangle_color[0]/256,rectangle_color[1]/256,rectangle_color[2]/256)
        if pd["color_divisions"]>0:
            pen_color=simplify_color(pen_color,pd["color_divisions"])
        vertice_array=[(point1[0],-point1[1]),(point2[0],-point2[1]),(point3[0],-point3[1]),(point4[0],-point4[1])]
        thickness=pd["pensize"]
        poly=Geometry.Polygon()
        #poly.inside_color=contrast_shift_transformation(pen_color,end_contrast) #used to be just pen_color as the next line NOTe OLD
        poly.inside_color=anti_gray_function(pen_color,pd["end_contrast"],picture_average_color) # this sets picture average_color to
        #be stable and changes other colors closer or further away from it depending on how positive or negative end_contrast is
        poly.verticise(vertice_array,thickness,contrast_shift_transformation(pen_color,pd["end_contrast"],picture_average_color),True,True)
        drawi.add_polygon(poly)
    return drawi

# shirnking_factor should be probably 3. end_contrast tells how much contrast
#is added to the colors at the end. cont_points tell how much we focus making new triangles on area with high details
#c_parameter tells how long we search to optimize each contrast_point
# if savename is None, savename is asked in the method, if savename is given, then it is not asked
def from_png_to_Drawing(filename,prop:PngProperties,savename=None):
    pd=prop.png_dict
    if pd["min_angle"]>30:
        pd["min_angle"]=30
    if pd["min_angle"]<1:
        pd["min_angle"]=1
    im = Image.open(filename) # Can be many different formats.
    (width,height)=im.size
    drawi=Geometry.Drawing("")
    if pd["style"]=="triangle" or pd["style"]=="rectangle":
        point_list=contrast_point_list(filename,pd["contrast_points"],pd["c_parameter"])
        shrinked_image_pixel_map(filename,"shrink.png",pd["shrinking_factor"],255)
        picture_average_color=average_color_of_file("shrink.png")
    if pd["style"]=="triangle":
        drawi=triangle_list_to_drawing(point_list,filename,picture_average_color,prop)
    if pd["style"]=="rectangle":#min_angle here is actually min side length
        drawi=rectangle_list_to_drawing(point_list,filename,picture_average_color,prop)
    drawi.center()
    drawi.resize(pd["end_width"],pd["end_height"]) #added 7.12.
    temp_str=drawi.from_Drawing_to_temp_string()

    if savename==None: #if no savename is given, then it is asked
        savename= save_drawing(temp_str)#this both saves the file and returns its name
    else:
        save_drawing_as(temp_str,savename)
    return savename

#this reuses parts of triangle_to_png_2 method. detail_level tells how much small details
# are picked, (with small detail_levels original png is shrinked more). detail_level values are forced from 1 to 10 
#contrast is added to the colors at the end, it should be between -30 to 30. 
def png_to_polygon_Drawing(filename,prop:PngProperties,savename=None):
    pd=prop.png_dict
    im = Image.open(filename) # Can be many different formats.
    (width,height)=im.size
    drawi=Geometry.Drawing("")
    enlarging_factor=3
    line_length=int(pd["min_angle"]/enlarging_factor) +1
    polygons=photo_to_polygons(filename,prop)
    for poly in polygons:
        poly.flip_y_axis()
        poly.enlarge(enlarging_factor)
        drawi.add_polygon(poly,"top")
    drawi.change_contrast_wrt_average(pd["end_contrast"])
    drawi.resize(pd["end_width"],pd["end_height"])  
    drawi.center()  #now picture should be in the center
    #if there is a bug involved in shifting
    temp_str=drawi.from_Drawing_to_temp_string()
    if savename==None: #if no save_name was given
        savename= save_drawing(temp_str)#this both saves the file and returns its name
    else: #in the case that savename was given as parameter
        save_drawing_as(temp_str,savename)
    return savename



#if we want to ask the name of the file, it's given here
def save_drawing(file_text):
    filename = filedialog.asksaveasfilename(defaultextension=".txt",initialdir="drawings/")
    with open(filename,"w") as file:
    # Write the string to the file
        file.write(file_text)
    return filename

#this saves a text_file with text "file_text" and name 'filename'
def save_drawing_as(file_text:str,filename:str):
    with open(filename,"w") as file:
    # Write the string to the file
        file.write(file_text)


#this is to get rid of whole path of filename
def filename_end(filename:str):
    help=MemoryHandler.split_the_string(filename,"/")
    realname=help[-1]#takes the string after last / symbol
    realname=realname[:-4]#gets rid of .txt
    return realname

#eeppinen 300,400,(200,300),(100,100)
#eeppinen2 300,400,(200,500),(100,100) kuva laskeutui alaspäin 200 askelta
#eeppinen3 300,400,(400,500),(100,100) kuva siirtyi oikealle 200 askelta 
#siis kuvan origo määräytyy koordinaattien vastaluvuista?

if __name__ == "__main__":

    prop=PngProperties()
    prop.info()
    prop.set_values({"contrast_points":99,"percentage":12})
    prop.info()
    prop.set_values({"detail_level":6,"contrast_points":100,"min_angle":15,"percentage":0.05,"end_contrast":2
                    ,"pensize":2,"color_divisions":13,"style":"simple","max_nro_of_colors":50})
    prop.set("end_height",700)
    from_photo_to_cartoon(filename="pngs/Anakin.jpg",prop=prop,savename="pngs/Anni final Anakin.png")
    #prop.set("end_width",50)

    pd=prop.png_dict
    pd["style"]="simo"
    prop.info()

    #resize_png("yoda.png","ohena.png",prop)
