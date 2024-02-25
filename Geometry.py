import math
import MemoryHandler
import Commands
import PngMaker
import random
import png
from typing import List
from tkinter import messagebox, scrolledtext
from PIL import Image
from PIL import ImageDraw,ImageFont
from icecream import ic
import shapely.geometry
from shapely.geometry import Point, Polygon
import FunctionOperator


INTERSECTION_CONSTANT=1
SHRINK_CONSTANT=2.5 #tells how large cap we draw between painted polygons and their contours
MAXIMUM_VERTICES=150
VERTICE_CONSTANT=8 #from how far we recognize a vertice
OVERLAP_CONSTANT=2.5 # for testing purposes very large value, maybe 1.5 would be right
WHERE_WE_ARE_CONSTANT=6 #if we are nearer that this to polygon edge, polygon isn't chosen by clicking
#call_dict={}#for testing purposes
#for testing purposes
#def add_to_call_counter(functionname):
#    global call_dict
#    if functionname not in call_dict.keys():
#        call_dict[functionname]=1
#    else:
#        call_dict[functionname]=call_dict[functionname]+1 

def distance(x,y,to_x,to_y):
    return math.dist((x,y),(to_x,to_y))

def pdistance(point1,point2):
    return math.dist(point1,point2)

#points are thought as vectors, their sum is returned as int-valued point
def point_int_sum(point1,point2):
    return (int(point1[0]+point2[0]),int(point1[1]+point2[1]))

#points are thought as vectors, their - is returned as int-valued point
def point_int_minus(point1,point2):
    return (int(point1[0]-point2[0]),int(point1[1]-point2[1]))

#point is thought as vector, it is turned by angle angle counter clockwise
def point_int_turn(point,angle:int):
    com1=Complex(point[0],point[1])
    com2=Complex(math.cos(math.pi*angle/180),math.sin(math.pi*angle/180))
    com=complex_multiply(com1,com2)
    result=(round(com.real()),round(com.imag()))
    return result

# what is the angle to go from (x,y) to (to_x,to_y) (if heading is originally towards x-axis)
def angle_to(x,y,to_x,to_y):
    r=distance(x,y,to_x,to_y)
    deg=0
    if r>0:
        cx=to_x - x
        cy=to_y-y
        sin = cy/r
        cos = cx/r
        if cx>0:
            rad = math.asin(sin)
            deg = rad*180/math.pi
        else:
            rad = math.asin(sin)
            deg = 180-rad*180/math.pi
    if r==0:#if the points are equal we just pick 0 as value instead of None (or Error)
        return 0
    if deg<0: #this is a new modification, hope it doesn't cause problems
        deg=deg+360
    return deg

class Complex:
    z=[]

    def __init__(self,x,y):
        self.z=[x,y]

    def set_z(self,x,y):
        z=[x,y]

    def real(self):
        return self.z[0]
    
    def imag(self):
        return self.z[1]
    
    def to_string(self):
        return str(self.z[0])+ "+"+ str(self.z[1])+"i"

def complex_multiply(z1:Complex,z2:Complex):
    z=Complex(z1.real()*z2.real()-z1.imag()*z2.imag(),z1.real()*z2.imag()+z1.imag()*z2.real())
    return z

def complex_size(z:complex):
    squared=z.real()*z.real()+z.imag()*z.imag()
    return math.sqrt(squared)

def complex_inverse(z:Complex):
    squared=z.real()*z.real()+z.imag()*z.imag()
    inverse=Complex(z.real()/squared,-z.imag()/squared)
    return inverse

#this tells what happens to the coordinates z=x,y when z1=x1,y1 stays still and x_2,y_2 -> x_3,y_3 in such a way that angles are preserved
def spin_transformation(z:Complex,z1:Complex,z2:Complex,z3:Complex):
    help1=Complex(z.real()-z1.real(),z.imag()-z1.imag())
    help2=Complex(z3.real()-z1.real(),z3.imag()-z1.imag())
    help3=complex_inverse(Complex(z2.real()-z1.real(),z2.imag()-z1.imag()))
    result=complex_multiply(help1,complex_multiply(help2,help3))
    return result

#with transformation leaving x1,y1 into place and moving x2,y2 to x3,y3, these are the parameters to accomplish the transformation.
#result tells that we need to scale with factor sca... rotate with rotation rot..
def spin_transformation_parameters(z1:Complex,z2:Complex,z3:Complex):
    help2=Complex(z2.real()-z1.real(),z2.imag()-z1.imag())
    help3=Complex(z3.real()-z1.real(),z3.imag()-z1.imag())
    scalefactor=complex_size(complex_multiply(complex_inverse(help2),help3))
    rotation2=int(angle_to(z1.real(),z1.imag(),z2.real(),z2.imag()))
    rotation3=int(angle_to(z1.real(),z1.imag(),z3.real(),z3.imag()))
    rotation=int(rotation3-rotation2)
    return [scalefactor,rotation]

#first three parameters are original parameters which are given in layer_data_canvas also
#three last parameters are the same as in draw mode spin command. z1 stays still while z2 moves to z3
#returns the parameters two put into layerdata after spinning
def layer_parameters_after_spin(scalef:List[float],rot:int,shift:Complex,spinz1:Complex,spinz2:Complex,spinz3:Complex):
    spin_parameters=spin_transformation_parameters(spinz1,spinz2,spinz3)
    rad_parameter=spin_parameters[1]*math.pi/180 #amount of spinning done in radians
    new_scale_factorx=spin_parameters[0]*scalef[0] #*math.cos(rad_parameter)-spin_parameters[0]*scalef[1]*math.sin(rad_parameter)
    new_scale_factory=spin_parameters[0]*scalef[1] #*math.cos(rad_parameter)+spin_parameters[0]*scalef[0]*math.sin(rad_parameter)
    new_scale_factor=[new_scale_factorx,new_scale_factory]
    #for example with 90 deg spin, with no enlargement new y scaling factory should be old x scaling factor
    new_rotation=int(rot+spin_parameters[1])
    if new_rotation>360:
        new_rotation=new_rotation-360
    if new_rotation<0:
        new_rotation=new_rotation+360
    rot_to_complex=Complex(math.cos(math.pi*spin_parameters[1]/180),math.sin(math.pi*spin_parameters[1]/180))
    help1=Complex(spin_parameters[0]*rot_to_complex.real(),spin_parameters[0]*rot_to_complex.imag()) #rotaatio*skaalaus
    help2=Complex(shift.real()-spinz1.real(),shift.imag()-spinz1.imag())
    help3=complex_multiply(help2,help1)#r's'(\omega-z1)
    help4=Complex(spinz1.real()+help3.real(),spinz1.imag()+help3.imag()) #r's'(\omega-z1)+z1
    new_xshift=int(help4.real())
    new_yshift=int(help4.imag())
    #jotain merkkejä voi vielä olla väärin.
    return [new_scale_factor,new_rotation,new_xshift,new_yshift]

#this old method works with 1d-scaling i.e. when there is no different scaling factor for x and y-axis
def layer_parameters_after_spin_old(scalef:float,rot:int,shift:Complex,spinz1:Complex,spinz2:Complex,spinz3:Complex):
    spin_parameters=spin_transformation_parameters(spinz1,spinz2,spinz3)
    new_scale_factor=spin_parameters[0]*scalef
    new_rotation=int(rot+spin_parameters[1])
    if new_rotation>360:
        new_rotation=new_rotation-360
    if new_rotation<0:
        new_rotation=new_rotation+360
    rot_to_complex=Complex(math.cos(math.pi*spin_parameters[1]/180),math.sin(math.pi*spin_parameters[1]/180))
    help1=Complex(spin_parameters[0]*rot_to_complex.real(),spin_parameters[0]*rot_to_complex.imag()) #rotaatio*skaalaus
    help2=Complex(shift.real()-spinz1.real(),shift.imag()-spinz1.imag())
    help3=complex_multiply(help2,help1)#r's'(\omega-z1)
    help4=Complex(spinz1.real()+help3.real(),spinz1.imag()+help3.imag()) #r's'(\omega-z1)+z1
    new_xshift=int(help4.real())
    new_yshift=int(help4.imag())
    #jotain merkkejä voi vielä olla väärin.
    return [new_scale_factor,new_rotation,new_xshift,new_yshift]

class Line:
    #end_point1=(0,0)
    #end_point2=(0,0)
    #thickness=0 #gives a thicknesses of lines between vertices. Zero=penup
    #pencolor=[0,0,0] #these are called color
    #pen_down=False #true if pen is down
    #fc_change=True #Tells if fillcolor is changed "inside line"
    #fillcolor=[0,0,0]

    def __init__(self,end_point1,end_point2,thickness,pencolor,pen_down:bool,fc_change:bool,fillcolor): #fc_change tells if fillcolor is changed
        self.end_point1=end_point1
        self.end_point2=end_point2
        self.thickness=thickness
        self.pencolor=pencolor
        self.pen_down=pen_down
        self.fc_change=fc_change
        self.fillcolor=fillcolor

    #makes a copy of this line
    def copy(self):
        new_endpoint1=(self.end_point1_x(),self.end_point1_y())
        new_endpoint2=(self.end_point2_x(),self.end_point2_y())
        return Line(new_endpoint1,new_endpoint2,self.thickness,self.pencolor,self.pen_down,self.fc_change,self.fillcolor)

    def set_end_point1(self,point):
        self.end_point1=point     

    def set_end_point2(self,point):
        self.end_point2=point     

    def set_thickness(self,pensize):
        self.thickness=pensize   

    def set_pencolor(self,color):
        self.pencolor=color   

    def set_fillcolor(self,color):
        self.fillcolor=color      
        
    def set_fc_change(self,change:bool):
        self.fc_change=change   

    def set_pen_down(self,downness:bool):
        self.pen_down=downness 

        #returns topleft-corner and bottomright corner of this line
    def placement(self):
        th=self.thickness
        topleft=(min(self.end_point1_x()-th,self.end_point2_x()-th),min(self.end_point1_y()-th,self.end_point2_y()-th))
        bottomright=(max(self.end_point1_x()+th,self.end_point2_x()+th),max(self.end_point1_y()+th,self.end_point2_y()+th))
        return [topleft,bottomright]
    
    #if line is cutted at point, the two lines that are formed are returned
    def splitlines(self,point):
        line1=self.copy()
        line2=self.copy()
        line1.set_end_point2(point)
        line2.set_end_point1(point)
        return [line1,line2]

    #enlarges line
    def enlarge(self,times:float):
        self.end_point1=(round(self.end_point1[0]*times),round(self.end_point1[1]*times))
        self.end_point2=(round(self.end_point2[0]*times),round(self.end_point2[1]*times))
        self.thickness=round(self.thickness*times)
        if self.thickness<=0:
            self.thickness=1

    #enlarges width (x-dimension) of the line by factor of times
    def enlarge_width(self,times:float):#NOTE not tested
        self.end_point1=(round(self.end_point1[0]*times),round(self.end_point1[1]))
        self.end_point2=(round(self.end_point2[0]*times),round(self.end_point2[1]))
        self.thickness=round(self.thickness* math.sqrt(times))
        if self.thickness<=0:
            self.thickness=1

    #enlarges height (x-dimension) of the line by factor of times
    def enlarge_height(self,times:float):#NOTE not tested
        self.end_point1=(round(self.end_point1[0]),round(self.end_point1[1]*times))
        self.end_point2=(round(self.end_point2[0]),round(self.end_point2[1]*times))
        self.thickness=round(self.thickness* math.sqrt(times))
        if self.thickness<=0:
            self.thickness=1

    #shifts placement of the line
    def shift(self,x_shift,y_shift):
        self.set_end_point1((self.end_point1_x()+x_shift,self.end_point1_y()+y_shift))
        self.set_end_point2((self.end_point2_x()+x_shift,self.end_point2_y()+y_shift))
        
    #returns a line which is a combination of this and other line
    def glue_line(self,other_line,self_end_point,other_line_endpoint):
        result=self.copy()
        if self_end_point==1 and other_line_endpoint==1:
            result.set_end_point1(other_line.end_point2)
        elif self_end_point==1 and other_line_endpoint==2:
            result.set_end_point1(other_line.end_point1)
        elif self_end_point==2 and other_line_endpoint==2:
            result.set_end_point2(other_line.end_point1)
        elif self_end_point==2 and other_line_endpoint==1:
            result.set_end_point2(other_line.end_point2)
        return result
           
    #makes corner points int numbers instead of floats
    def intify(self):
        self.end_point1=(round(self.end_point1_x()),round(self.end_point1_y()))
        self.end_point2=(round(self.end_point2_x()),round(self.end_point2_y()))
        self.thickness=round(self.thickness)

    def end_point1(self):
        return self.end_point1
    
    def end_point2(self):
        return self.end_point2

    def end_point1_x(self):
        return self.end_point1[0]

    def end_point1_y(self):
        return self.end_point1[1]
    
    def end_point2_x(self):
        return self.end_point2[0]
    
    def end_point2_y(self):
        return self.end_point2[1]
    
    #returns the length of the line
    def lenght(self):
        return math.sqrt((self.end_point1_x()-self.end_point2_x())*(self.end_point1_x()-self.end_point2_x())+(self.end_point1_y()-self.end_point2_y())*(self.end_point1_y()-self.end_point2_y()))

    #tells if point is inside line
    def is_inside(self,point,extra=5):
        if self.distance_from_a_point(point)<self.thickness/2+extra:
            return True
        return False

    #tells how far the chosen point is from the line
    def distance_from_a_point(self,point):
        return distance_from_line_segment(self,point)

    def heading(self):
        return int(angle_to(self.end_point1_x(),self.end_point1_y(),self.end_point2_x(),self.end_point2_x()))

    #With this you can transfrom line to a piece of str. There is redundancy which should be deleted in Drawing
    def represent_as_temp_str(self):
        still=is_same(self.end_point1,self.end_point2)#true if the pen doesn't move
        result="pu()|goto("+str(self.end_point1_x())+","+str(self.end_point1_y())+")|"
        result +="co(["+str(self.pencolor[0])[:5]+","+str(self.pencolor[1])[:5]+","+str(self.pencolor[2])[:5]+"])|ps("+str(self.thickness)+")|"
        if self.pen_down:
            result += "pd()|"
        else:
            result += "pu()|"
        if still==False:
            result += "sh"+"("+str(int(angle_to(self.end_point1_x(),self.end_point1_y(),self.end_point2_x(),self.end_point2_y()))) 
            result += ")|goto("+str(self.end_point2_x())+","+str(self.end_point2_y())+")|"
        if self.fc_change:
            result += "fc(["+str(self.fillcolor[0])[:5]+","+str(self.fillcolor[1])[:5]+","+str(self.fillcolor[2])[:5]+"])|"
        return result
    
    "returns a string describing is 'line' under, over or crossing other line"
    def relative_position(self,line,overlapdist=OVERLAP_CONSTANT):
        list_of_options=["same","reverse","covers","reversecovers","halfcovers11","halfcovers12","halfcovers21","halfcovers22"]
        list_of_options=["halfcovered11","halfcovered12","halfcovered21","halfcovered22"]
        list_of_options+=["covered","reversecovered","crossing","joined11","joined12","joined21","joined22"]
        list_of_options+=["overlaps11","overlaps12","overlaps21","overlaps22","Ts1","Ts2","Tl1","Tl2","disjoint"]
        #'same' same end points,'reverse' same end points but in reverse order,'covers' self "swallows" whole line
        # 'covered' other way around, 'halfcoversxy':self endpoint_x=line endpoint_y but self "swallows" line, in halfcovered other way around  
        #  'crossing' just one point intersection, 'joinedxy': self endpoint_x is line endpoint_y

        #'overlapsxy' self end_pointx inside line and line endpoint_y is inside self
        #Tsx means self endpointx is inside line (forming t) and Tlx that line endpoint_x is inside self, "disjoint" means no contact
        [eps1,eps2]=[self.end_point1,self.end_point2]
        [epl1,epl2]=[line.end_point1,line.end_point2]
        #are the end_points xy same?
        [bsame11,bsame12]=[pdistance(eps1,epl1)<overlapdist,pdistance(eps1,epl2)<overlapdist]
        [bsame21,bsame22]=[pdistance(eps2,epl1)<overlapdist,pdistance(eps2,epl2)<overlapdist]
        #is and end_points x inside other line?
        bs1inl=distance_from_line_segment(line,self.end_point1)<overlapdist
        bs2inl=distance_from_line_segment(line,self.end_point2)<overlapdist
                       
        bl1ins=distance_from_line_segment(self,line.end_point1)<overlapdist
        bl2ins=distance_from_line_segment(self,line.end_point2)<overlapdist
                         
        #is there an intersection
        binters=is_there_intersection(self,line)

        if bsame11:
            if bsame22:
                return "same"
            elif bs2inl:
                return "halfcovered11"
            elif bl2ins:
                return "halfcovers11" 
            return "joined11"
        if bsame12:
            if bsame21:
                return "reverse"
            elif bs2inl:
                return "halfcovered12"
            elif bl1ins:
                return "halfcovers12" 
            return "joined12"
        if bsame22:
            if bs1inl:
                return "halfcovered22"
            elif bl1ins:
                return "halfcovers22" 
            return "joined22"
        if bsame21:
            if bs1inl:
                return "halfcovered21"
            elif bl2ins:
                return "halfcovers21" 
            return "joined21" #now we have gone through all the cases with same end_points
        if bs1inl and bs2inl:
            if pdistance(self.end_point1,line.end_point1)<pdistance(self.end_point2,line.end_point1):
                return "covered"
            else:
                return "reversecovered"
        if bl1ins and bl2ins:
            if pdistance(self.end_point1,line.end_point1)<pdistance(self.end_point1,line.end_point2):
                return "covers"
            else:
                return "reversecovers"
        if bs1inl and bl1ins:
            return "overlaps11"
        if bs1inl and bl2ins:
            return "overlaps12"
        if bs2inl and bl1ins:
            return "overlaps21"
        if bs2inl and bl2ins:
            return "overlaps22"
        #now only T and X shapes are left as possibilities
        if bs1inl:
            return "Ts1"
        if bs2inl:
            return "Ts2"
        if bl1ins:
            return "Tl1"
        if bl2ins:
            return "Tl2"
        if binters==False:
            return "disjoint"
        #only crossing is left as an option
        return "crossing"

class Writing:#this helps to save and handle writed elements in the drawings
    def __init__(self,pen_color,location,style,font,fontsize,text):
        self.pen_color=pen_color
        self.location=location
        self.style=style #i.e. normal, bold, italic
        self.font=font
        self.fontsize=fontsize
        self.text=text
    
    def represent_as_temp_str(self):
        result = "co(["+str(self.pen_color[0])[:5]+","+str(self.pen_color[1])[:5]+","+str(self.pen_color[2])[:5]+"])|"
        result += "pu()|goto("+str(self.location[0])+","+str(self.location[1])+")|pd()|"
        result += "wr("+ self.style +","+self.font+","+str(self.fontsize)+","+self.text+")|"
        return result


    #shifts placement of the writing
    def shift(self,x_shift,y_shift):
        self.location=(self.location[0]+x_shift,self.location[1]+y_shift)

    #enlarges writing
    def enlarge(self,times:float):
        self.location=(round(int(self.location[0])*times),round(int(self.location[1])*times))
        self.fontsize=round(int(self.fontsize[0])*times)
        if self.fontsize<=0:
            self.fontsize=1

    #this little bit stupid method is here since we need it, it actually changes both width and height of the text
    # by factor of square root of times. Text position is only moved horizontally
    def enlarge_width(self,times:float):#NOTE not tested
        self.location=(round(int(self.location[0])*times),round(int(self.location[1])))
        self.fontsize=round(int(self.fontsize)* math.sqrt(times))
        if self.fontsize<=0:
            self.fontsize=1

    #this little bit stupid method is here since we need it, it actually changes both width and height of the text
    # by factor of square root of times. Text position is only moved vertically
    def enlarge_height(self,times:float): #NOTE not tested
        self.location=(round(int(self.location[0])),round(int(self.location[1])*times))
        self.fontsize=round(int(self.fontsize)* math.sqrt(times))
        if self.fontsize<=0:
            self.fontsize=1




    #returns topleft-corner and bottomright corner of this writing
    def placement(self):
        #the following size is just a guess: later if you want to improve just count
        #number of longest streak of symbols not containing "\n" in x-component of size
        size=(int(self.fontsize)*len(self.text),int(self.fontsize)*(1+self.text.count("\n")))
        return [(self.location[0],self.location[1]),(int(self.location[0])+int(size[0]),int(self.location[1])+int(size[1]))]



class Polygon: #to help representing temporary_file_string as polygons
    #currently, if we want, we can create polygon from lines of which end_points do not connect each other,
    #this is somewhat problematic, so we have to take care to not to produce such polygons accidently
    def __init__(self):
        self.lines=[]#lists of lines that polygon consists of
        self.inside_color=[0,0,0]#and fillcolor in KuhanPiirran
        self.writings=[]#writings are strings represented in the same way as in temp_file_str e.g. "wr(Arial,3,bold,moi maailma)|"

    #returns the vertices of the polygon
    def vertices(self):
        verticelist=[]
        for line in self.lines:
            verticelist.append(line.end_point1)
        if len(self.lines)>0:
            verticelist.append(self.lines[-1].end_point2)
        return verticelist

    #returns the vertices of the polygon, without the double vertice in vertices(slef)
    def vertices2(self):
        verticelist=[]
        for line in self.lines:
            verticelist.append(line.end_point1)
        return verticelist

    #if three consecutive vertices look the same (same color, thickness) and are in the (almost) same line we take the middle one out
    def reduce_unnecessary_vertices(self,distance_variation):
        tries_to_reduce=100
        while tries_to_reduce>0 and len(self.lines)>2:
            tries_to_reduce += -1
            vertice_nro=int(random.random()*len(self.lines))
            succeeded=self.unnecessary_vertice_reduction_step(vertice_nro,distance_variation) #this does the reduction if possible and also returns
            #value telling if it succeeded
            if succeeded:
                tries_to_reduce=100

    #probably something between 0.5...2.0 is optimal value for distance_variation, it tells how far the middle point can be from the line
    #formed points next to  it
    def unnecessary_vertice_reduction_step(self,vertice_nro,distance_variation):
        if len(self.lines)>vertice_nro:
            line1=self.lines[vertice_nro-1]
            line2=self.lines[vertice_nro]
            cond0= line1.end_point2==line2.end_point1
            cond1= line1.thickness==line2.thickness
            cond2= line1.pencolor==line2.pencolor
            cond3= line1.pen_down==line2.pen_down
            cond4= pdistance_from_line_segment(line1.end_point1,line2.end_point2,line1.end_point2)<distance_variation 

            if cond1 and cond2 and cond3 and cond4:
                line1.end_point2=line2.end_point2
                self.lines.remove(line2)
                #we move end point of line1 to end point of line2 and then take away the line2 from the polygon
                #this is done only if they have same color and thickness and go approximately to the same direction
                return True
        return False

    #changes the visibility of lines
    def set_line_visibity(self,visibility:bool):
        for line in self.lines:
            line.pen_down=visibility

    #changes the visibility of lines
    def set_line_thickness(self,thickness:int):
        for line in self.lines:
            line.thickness=thickness

    #cshifts placement of the polygon
    def shift(self,x_shift,y_shift):
        for line in self.lines:
            line.end_point1=(line.end_point1[0]+x_shift,line.end_point1[1]+y_shift)
            line.end_point2=(line.end_point2[0]+x_shift,line.end_point2[1]+y_shift)

    #turns the polygon to mirror image by changing sign of y-values
    def flip_y_axis(self):
        for line in self.lines:
            line.end_point1=(line.end_point1[0],-line.end_point1[1])
            line.end_point2=(line.end_point2[0],-line.end_point2[1])

    #enlarges polygon
    def enlarge(self,times:float):
        for line in self.lines:
            line.end_point1=(round(line.end_point1[0]*times),round(line.end_point1[1]*times))
            line.end_point2=(round(line.end_point2[0]*times),round(line.end_point2[1]*times))
            line.thickness=(round(line.thickness*times))
            if line.thickness<=0:
                line.thickness=1

    #enlarges width (x-dimension) of the lines of polygon by factor of times
    def enlarge_width(self,times:float):
        for line in self.lines:
            line.end_point1=(round(line.end_point1[0]*times),round(line.end_point1[1]))
            line.end_point2=(round(line.end_point2[0]*times),round(line.end_point2[1]))
            line.thickness=(round(line.thickness*math.sqrt(times)))
            if line.thickness<=0:
                line.thickness=1

    #enlarges height (y-dimension) of the lines of polygon by factor of times
    def enlarge_height(self,times:float):
        for line in self.lines:
            line.end_point1=(round(line.end_point1[0]*times),round(line.end_point1[1]*times))
            line.end_point2=(round(line.end_point2[0]*times),round(line.end_point2[1]*times))
            line.thickness=(round(line.thickness*math.sqrt(times)))
            if line.thickness<=0:
                line.thickness=1


    #this tries to glue a new triangle to polygon. It succeeds if the triangle shares same side or more and polygon is not too complicwated
    #this method it super complicated and untested so it might not work
    def glue_triangle(self,triangle):
        tr_vertices=triangle.vertices()
        if len(tr_vertices)==3:
            index0=-1 
            index1=-1
            index2=-1
            how_many_hits=0
            for i in len(self.vertices()):
                if tr_vertices[0]==self.vertices()[i]:
                    index0=i
                    how_many_hits += 1
                if tr_vertices[1]==self.vertices()[i]:
                    index1=i
                    how_many_hits += 1
                if tr_vertices[2]==self.vertices()[i]:
                    index2=i
                    how_many_hits += 1
            if how_many_hits>4:#there is two much complication in polygon to try to solve
                return
            start=min(index0,index1,index2)
            end=max(index0,index1,index2)

            if (index0 !=-1 and index1 != -1) or (index0 !=-1 and index2 != -1) or (index1 !=-1 and index2 != -1):
                if how_many_hits==4:#there is a whole in polygon
                    self.lines.pop(start)
                    self.lines.pop(start+1)
                    self.lines.pop(start+2)
                elif index0 !=-1 and index1 != -1 and index2 != -1:#two shared sides (how_many_hits must be 3)
                    self.lines[end-1].end_point2=self.lines[end].end_point2
                    self.lines.pop(end)
                else: #only one shared side
                    if index1-index0==1: #tr_vertice2 must be added as a new vertice
                        sl=self.lines[end-1]
                        add_line1=Line(tr_vertices[0],tr_vertices[2],sl.thickness,sl.pencolor,sl.pen_down,sl.fc_change,self.inside_color)
                        add_line2=Line(tr_vertices[2],tr_vertices[1],sl.thickness,sl.pencolor,sl.pen_down,sl.fc_change,self.inside_color)
                        self.lines.insert(index0,add_line1)
                        self.lines.insert(index1+1,add_line2)
                        self.lines.pop(end)
                    if index1-index0==-1: #tr_vertice2 must be added as a new vertice
                        sl=self.lines[end-1]
                        add_line1=Line(tr_vertices[1],tr_vertices[2],sl.thickness,sl.pencolor,sl.pen_down,sl.fc_change,self.inside_color)
                        add_line2=Line(tr_vertices[2],tr_vertices[0],sl.thickness,sl.pencolor,sl.pen_down,sl.fc_change,self.inside_color)
                        self.lines.insert(index1,add_line1)
                        self.lines.insert(index0+1,add_line2)
                        self.lines.pop(end)
                    if index2-index0==1: #tr_vertice1 must be added as a new vertice
                        sl=self.lines[end-1]
                        add_line1=Line(tr_vertices[0],tr_vertices[1],sl.thickness,sl.pencolor,sl.pen_down,sl.fc_change,self.inside_color)
                        add_line2=Line(tr_vertices[1],tr_vertices[2],sl.thickness,sl.pencolor,sl.pen_down,sl.fc_change,self.inside_color)
                        self.lines.insert(index0,add_line1)
                        self.lines.insert(index2+1,add_line2)
                        self.lines.pop(end)
                    if index2-index0==-1: #tr_vertice1 must be added as a new vertice
                        sl=self.lines[end-1]
                        add_line1=Line(tr_vertices[2],tr_vertices[1],sl.thickness,sl.pencolor,sl.pen_down,sl.fc_change,self.inside_color)
                        add_line2=Line(tr_vertices[1],tr_vertices[0],sl.thickness,sl.pencolor,sl.pen_down,sl.fc_change,self.inside_color)
                        self.lines.insert(index2,add_line1)
                        self.lines.insert(index0+1,add_line2)
                        self.lines.pop(end)
                    if index2-index1==1: #tr_vertice0 must be added as a new vertice
                        sl=self.lines[end-1]
                        add_line1=Line(tr_vertices[1],tr_vertices[0],sl.thickness,sl.pencolor,sl.pen_down,sl.fc_change,self.inside_color)
                        add_line2=Line(tr_vertices[0],tr_vertices[2],sl.thickness,sl.pencolor,sl.pen_down,sl.fc_change,self.inside_color)
                        self.lines.insert(index1,add_line1)
                        self.lines.insert(index2+1,add_line2)
                        self.lines.pop(end)
                    if index2-index0==-1: #tr_vertice0 must be added as a new vertice
                        sl=self.lines[end-1]
                        add_line1=Line(tr_vertices[2],tr_vertices[0],sl.thickness,sl.pencolor,sl.pen_down,sl.fc_change,self.inside_color)
                        add_line2=Line(tr_vertices[0],tr_vertices[1],sl.thickness,sl.pencolor,sl.pen_down,sl.fc_change,self.inside_color)
                        self.lines.insert(index2,add_line1)
                        self.lines.insert(index1+1,add_line2)
                        self.lines.pop(end)




    #changes the polygon so that it's lines are now with endpoints given by vertices of vertice array
    def verticise(self,vertice_array,thickness,pencolor,pen_down,fc_change):
        self.lines=[]
        size=len(vertice_array)
        for i in range(0,size-1):
            add_line=Line(vertice_array[i],vertice_array[i+1],thickness,pencolor,pen_down,fc_change,self.inside_color)
            self.lines.append(add_line)
        if size>0:
            last_line=Line(vertice_array[size-1],vertice_array[0],thickness,pencolor,pen_down,fc_change,self.inside_color)
            self.lines.append(last_line)

    #return a line with given endpoints
    def line_with_vertices(self,point1,point2):
        for line in self.lines:
            if (line.end_point1==point1 and line.end_point2==point2) or (line.end_point2==point1 and line.end_point1==point2):
                return line

    #returns topleft-corner and bottomright corner of this polygon
    def placement(self):
        vertice_list=self.vertices()
        topleft_array=[vertice_list[0][0],vertice_list[0][1]]
        bottomright_array=[vertice_list[0][0],vertice_list[0][1]]
        for vertice in vertice_list:
            topleft_array=[min(topleft_array[0],vertice[0]),min(topleft_array[1],vertice[1])]
            bottomright_array=[max(bottomright_array[0],vertice[0]),max(bottomright_array[1],vertice[1])]
        return [(topleft_array[0],topleft_array[1]),(bottomright_array[0],bottomright_array[1])]

    #finds a line in a polygon and a point in that line that is closest  to given point
    def projection(self,point):
        nearest_point=None
        nearest_line=None
        mindist=10000000
        for line in self.lines:
            dist=pdistance(nearest_point_on_line(line,point),point)
            if dist<mindist:
                nearest_point=nearest_point_on_line(line,point)
                nearest_line=line
                mindist=dist
        return [nearest_point,nearest_line]

    #NOTE, added pu() in the first line 22.2.2024
    def represent_as_temp_str(self): #this represents Polygon aa piece of string that is direc
        result="pu()|bf()|fc(["+str(self.inside_color[0])[:5]+","+str(self.inside_color[1])[:5]+","+str(self.inside_color[2])[:5]+"])|"
        eraser=True #if there is no line, result must be erased to ""
        for line in self.lines:
            result += fc_off(line.represent_as_temp_str())
            eraser=False
        result+="ef()|"
        if eraser:
            result=""
        return result

    #all the contourlines get this pen_color
    def set_pencolor(self,color):
        for line in self.lines:
            line.pencolor=color 
    
    #aPolygon is now filled with this color
    def set_inside_color(self,color):
        self.inside_color=color 

    #all the contourlines get this thickness
    def set_thickness(self,pensize):
        for line in self.lines:
            line.thickness=pensize  

    #makes corner points int numbers instead of floats
    def intify(self):
        for line in self.lines:
            line.intify()

    def add_line(self,line):
        self.lines.append(line)

    #returns the lines which Polygon consists of and removes them from the polygon. This can be used for example
    #when bf() is called in the middle of filling polygon
    def disintegrate(self):
        array=[]
        for line in self.lines:
            array.append(line)
        self.lines=[]
        self.writings=[]
        return array

 

    def is_inside(self,point): #tells if given point is inside polygon
        vertice_list=self.vertices()
        pol=shapely.geometry.Polygon(vertice_list)
        poi=shapely.geometry.Point(point[0],point[1])
        return poi.within(pol)





    #Tells if line is completely inside of this polygon
    def is_line_inside(self,line:Line): #tells if line is inside-polygon
        if self.is_inside(line.end_point1)==False or self.is_inside(line.end_point2)==False:
            return False
        for line2 in self.lines:
            if is_there_intersection(line,line2):
                return False
        return True


    #returns the closest_line to the 'point' in the polygon contour
    def distance_from_closest_line(self,point): #how close a given point is from the closest line of the polygon
        min_dist=self.radius()
        for line1 in self.lines:
            dist=distance_from_line_segment(line1,point)
            if dist<min_dist:
                min_dist=dist
        return min_dist
    
    #returns the closest_line in polygons contour
    def closest_line(self,point):
        min_dist=self.radius()
        closest_line=None
        for line1 in self.lines:
            dist=distance_from_line_segment(line1,point)
            if dist<min_dist:
                min_dist=dist
                closest_line=line1
        return closest_line

    #returns number of the line in the polygon
    def line_nro(self,line):
        for i in range(len(self.lines)):
            if line==self.lines[i]:
                return i
        return -1


    def end_points(self):
        result=""
        for line in self.lines:
            result += str(line.end_point1)+str(line.end_point2)

    #gives a radius of polygon (its the distance of its most far away end points)
    def radius(self):
        radius=0
        size=len(self.lines)
        for i in range(size):
            for j in range(size):
                dist1=distance(self.lines[i].end_point1_x(),self.lines[i].end_point1_y(),self.lines[j].end_point1_x(),self.lines[j].end_point1_y())
                dist2=distance(self.lines[i].end_point1_x(),self.lines[i].end_point1_y(),self.lines[j].end_point2_x(),self.lines[j].end_point2_y())
                dist3=distance(self.lines[i].end_point2_x(),self.lines[i].end_point2_y(),self.lines[j].end_point2_x(),self.lines[j].end_point2_y())
                if dist1>radius:
                    radius=dist1
                if dist2>radius:
                    radius=dist2
                if dist3>radius:
                    radius=dist3
        return radius
    
    #this polygon is inside other polygon, if its radius is smaller and no lines in polygons intersect
    #returns True iff this polygon is inside another polygon 'poly2'
    def is_inside_polygon(self,poly2):
        if self.radius()<poly2.radius():
            return False
        if poly2.is_inside(self.lines[0].end_point1)==False: #if there is an endpoint in this polygon, not inside the other, it's game over
            return False
        size=len(self.lines)
        size2=len(poly2.lines)
        for i in range(size):
            for j in range(size2):
                if is_there_intersection(self.lines[i],poly2.lines[j]):
                    return False
        return True

    #Returns true iff this polygon has exactly the same contours as another polygon
    def identical_contours(self,poly2):
        self_line_endpoints=[]
        for i in range(len(self.lines)):
            self_line_endpoints.append(self.lines[i].end_point1,self.lines[i].end_point2)
        poly2_line_endpoints=[]
        for i in range(len(poly2.lines)):
            poly2_line_endpoints.append(poly2.lines[i].end_point1,poly2.lines[i].end_point2)
        #now we have lists of endpoint pairs, if we find even one endpoint pair without match, the contours are not identical

        for i in range(len(self_line_endpoints)):
            pair_is_found=False
            for j in range(len(poly2_line_endpoints)):
                if is_same(self_line_endpoints[0],poly2_line_endpoints[0]) and is_same(self_line_endpoints[1],poly2_line_endpoints[1]):
                    pair_is_found=True 
                if is_same(self_line_endpoints[0],poly2_line_endpoints[1]) and is_same(self_line_endpoints[1],poly2_line_endpoints[0]):
                    pair_is_found=True 
            if pair_is_found==False:
                return False
        #same search needs to be done to other direction since one direction only gives inclusion not equality
        for i in range(len(poly2_line_endpoints)):
            pair_is_found=False
            for j in range(len(self_line_endpoints)):
                if is_same(self_line_endpoints[0],poly2_line_endpoints[0]) and is_same(self_line_endpoints[1],poly2_line_endpoints[1]):
                    pair_is_found=True 
                if is_same(self_line_endpoints[0],poly2_line_endpoints[1]) and is_same(self_line_endpoints[1],poly2_line_endpoints[0]):
                    pair_is_found=True 
            if pair_is_found==False:
                return False
        return True

    #creates a random polygon for testing
    def random_polygon(self):
        nro_of_vertices=int(4+(3*random.random()))
        vertice_list=[]
        for i in range(nro_of_vertices):
            vertice_list.append((int(200-400*random.random()),int(200-400*random.random())))
        self.verticise(vertice_list,5,(random.random(),random.random(),random.random()),True,True)
        self.inside_color=(random.random(),random.random(),random.random())
        return self
        
class Drawing: #Drawing is a class that is meant to represent temp-file-string as a series of lines and polygons
    def __init__(self,temp_str:str):
        temp_str=reduce(temp_str)#first simplify
        self.elements=[]#these are lines and polygons and writings(?)
        temp_str=temp_str.strip("£")
        array=MemoryHandler.split_the_string(temp_str,"|")
        in_polygon=False #tells if current string are added in the polygon or just as a line
        c_pen_color=[0,0,0] #c here is for 'current'. These are the values currently in operation
        c_fill_color=[0,0,0]
        c_thickness=1 #i.e. pensize
        c_location=(0,0)
        c_pen_down=False
        temp_polygon=Polygon()#Currently operated polygon is saved here (if there is polygon to be operated)
        temp_polygon.inside_color=c_fill_color
        for plop in array:
            if plop=="bf()": #if filling starts from this command
                if in_polygon: #if it was already in progress, the beginning must be "anti"polygonized
                    line_array=temp_polygon.disintegrate()
                    for line in line_array:
                        self.elements.append(line)
                in_polygon=True #following things are added in the polygon
                temp_polygon=Polygon()
                temp_polygon.inside_color=c_fill_color
            if plop=="ef()" and in_polygon:
                if len(temp_polygon.lines)>0:#if there is at least one line in the polygon
                    starting_point=temp_polygon.lines[0].end_point1
                    add_invisible_line=False
                    if is_same(c_location,starting_point)==False: 
                        new_line=Line(c_location,starting_point,c_thickness,c_pen_color,False,False,c_fill_color)#fill_color should be irrelevant
                        temp_polygon.lines.append(new_line)#this is a line beginning from the end point of the polygon
                        invisible_line=Line(starting_point,c_location,c_thickness,c_pen_color,False,False,c_fill_color)
                        add_invisible_line=True
                    self.elements.append(temp_polygon)
                    if add_invisible_line:
                        self.elements.append(invisible_line)#this line might be unnecessary, but anyway it returns us to where we should be
                    in_polygon=False

                temp_polygon=Polygon()

            if plop[0:4]=="goto":
                new_x=int(Commands.nth_parameter(plop,0))
                new_y=int(Commands.nth_parameter(plop,1))
                new_line=Line(c_location,(new_x,new_y),c_thickness,c_pen_color,c_pen_down,True,c_fill_color)
                if new_x !=c_location[0] or new_y !=c_location[1]: #i.e. if we are really moving to new position
                    if in_polygon:
                        temp_polygon.lines.append(new_line)
                    if in_polygon == False:
                        self.elements.append(new_line)
                c_location=(new_x,new_y)
            if plop[0:2]=="fc":
                red=Commands.nth_parameter(plop,0)[1:]
                green=Commands.nth_parameter(plop,1)
                blue=Commands.nth_parameter(plop,2)[:-1]
                c_fill_color=[red,green,blue]
                temp_polygon.inside_color=c_fill_color #Vaikka polygoni olisi tyhjä, sen värin vaihto ei haittaa
            if plop[0:2]=="co":
                red=Commands.nth_parameter(plop,0)[1:]
                green=Commands.nth_parameter(plop,1)
                blue=Commands.nth_parameter(plop,2)[:-1]
                c_pen_color=[red,green,blue]
            if plop[0:2]=="ps":
                c_thickness=int(Commands.nth_parameter(plop,0))
            if plop=="pu()":
                c_pen_down=False
            if plop=="pd()":
                c_pen_down=True
            if plop[0:2]=="wr":#this is the way that information of writings is conserved
                style=Commands.nth_parameter(plop,0)#esim. "bold"
                fon=Commands.nth_parameter(plop,1)#esim. "Calibri"
                fontsize=Commands.nth_parameter(plop,2)#esim. "13
                text=plop[6:-1]
                text=text[text.find(",")+1:]
                text=text[text.find(",")+1:]
                text=text[text.find(",")+1:].strip("'")
                self.elements.append(Writing(c_pen_color,c_location,style,fon,fontsize,text))
        self.invisible_line_removal() #takes away consecutive invisible lines that leaving only one

    #returns list with two element, topleftcorner- and bottomrightcornercoordinates of this Drawing
    def placement(self):
        placement=[(0,0),(0,0)]
        if len(self.elements)>0:
            placement=[self.elements[0].placement()[0],self.elements[0].placement()[1]]
        for element in self.elements:
            topleft=(min(element.placement()[0][0],placement[0][0]),min(element.placement()[0][1],placement[0][1]))
            bottomright=(max(element.placement()[1][0],placement[1][0]),max(element.placement()[1][1],placement[1][1]))
            placement=[topleft,bottomright]
        return placement

    #we enlarge drawing to size of end_width*end_height, if other parameter is empty, then we just keep the ratio and fix one dimension
    def resize(self,end_width=None,end_height=None):#NOTE not tested
        [topleft,bottomright]=self.placement()
        width= abs(topleft[0]-bottomright[0])
        height=abs(topleft[1]-bottomright[1])
        if width<1 or height<1: #one dimensionis two small to resize
            return
        
        if end_width != None and end_height==None:
            self.enlarge(end_width/width)
    
        if end_width == None and end_height !=None:
            self.enlarge(end_height/height)

        if end_width != None and end_height != None:
            self.enlarge_width(end_width/width)
            self.enlarge_height(end_height/height)


    #moves current Geometry object in such a way that coordinate (0,0) is in the middle of its topleft and bottomright corner 
    def center(self):
        [topleft,bottomright]=self.placement()
        middle_point=[-int((topleft[0]+bottomright[0])/2),-int((topleft[1]+bottomright[1])/2)]
        self.shift(middle_point[0],middle_point[1])

                       
    #enlarges Drawing (or shrinks if times<1)
    def enlarge(self,times:float):
        for element in self.elements:
            element.enlarge(times)

    #enlarges Drawing in x-direction by factor of ¨times'
    def enlarge_width(self,times:float):
        for element in self.elements:
            element.enlarge_width(times)

    #enlarges Drawing in x-direction by factor of ¨times'
    def enlarge_height(self,times:float):
        for element in self.elements:
            element.enlarge_height(times)


    #puts this item on the top of drawed objects (so actually last in the list)
    def lift(self,element):
        enro=self.get_element_number(element)
        if enro !=-1:
            self.elements.pop(enro)
            self.elements.append(element)

        #puts this item on the bottom of drawed objects (so actually last in the list)
    def sink(self,element):
        enro=self.get_element_number(element)
        if enro !=-1:
            self.elements.pop(enro)
            self.elements.insert(0,element)

    #shifts everything in this Drawing
    def shift(self,x_shift,y_shift):
        for element in self.elements:
            if element.__class__.__name__ == "Line":
                element.shift(x_shift,y_shift)
            if element.__class__.__name__ == "Polygon":
                element.shift(x_shift,y_shift)
            if element.__class__.__name__ == "Writing":
                element.shift(x_shift,y_shift)


    #if color_gap is positive keeps every color in the drawing that is less than a color_gap away from middle_color
    #rest of the objects are removed
    #if filter is negative deletes everything closer to color_gap to middle color
    def filter_old(self,middle_color:List[float],gap:float):
        destroy_list=[]
        for element in self.elements:
            if element.__class__.__name__ == "Polygon":
                color_difference=color_gap(middle_color,element.inside_color)
                if (gap>=0 and color_difference>gap) or (gap<0 and color_difference<-gap):
                    destroy_list.append(element)
        for polygon in destroy_list:
            linelist=polygon.disintegrate()
            self.remove_element(polygon)
            self.add_linelist(linelist,"top")
        #at this points polygons with bad color should be destroyed but their contourlines added as elements in Drawing
        for element in self.elements:
            if element.__class__.__name__ == "Polygon":
                for line in element.lines:
                    color_difference=color_gap(middle_color,line.pencolor)
                    if (gap>=0 and color_difference>gap) or (gap<0 and color_difference<-gap):
                        line.set_pen_down(False) #line can't be destroyed since it is part of the contour, but it is now invisible                   
        destroy_list=[]
        for element in self.elements: #at this points polygons are already handled
            if element.__class__.__name__ == "Line":
                color_difference=color_gap(middle_color,element.pencolor)
                if (gap>=0 and color_difference>gap) or (gap<0 and color_difference<-gap):
                    destroy_list.append(element)
        for line in destroy_list:
            self.remove_element(line)

        destroy_list=[]
        for element in self.elements:
            if element.__class__.__name__ == "Writing":
                color_difference=color_gap(middle_color,element.pen_color)
                if (gap>=0 and color_difference>gap) or (gap<0 and color_difference<-gap):
                    destroy_list.append(element)
        for writing in destroy_list:
            self.remove_element(writing)




    #if color_gap is positive keeps every color in the drawing that is less than a color_gap away from middle_color
    #rest of the objects are removed
    #if filter is negative deletes everything closer to color_gap to middle color
    def filter(self,middle_color:List[float],gap:float):
        destroy_list=[]
        keep_list=[]
        for element in self.elements:
            if element.__class__.__name__ == "Polygon":
                color_difference=color_gap(middle_color,element.inside_color)
                if (gap>=0 and color_difference>gap) or (gap<0 and color_difference<-gap):
                    destroy_list.append(element)
                    linelist=element.disintegrate()
                    for line in linelist:
                        color_difference=color_gap(middle_color,line.pencolor)
                        if ((gap>=0 and color_difference>gap) or (gap<0 and color_difference<-gap))==False:
                            keep_list.append(line)
                else:
                    keep_list.append(element)
                    for line in element.lines:
                        color_difference=color_gap(middle_color,line.pencolor)
                        if (gap>=0 and color_difference>gap) or (gap<0 and color_difference<-gap):
                            line.set_pen_down(False) #line can't be destroyed since it is part of the contour, but it is now invisible                   
            if element.__class__.__name__ == "Line":
                color_difference=color_gap(middle_color,element.pencolor)
                if ((gap>=0 and color_difference>gap) or (gap<0 and color_difference<-gap))==False:
                    keep_list.append(element)

            if element.__class__.__name__ == "Writing":
                color_difference=color_gap(middle_color,element.pen_color)
                if ((gap>=0 and color_difference>gap) or (gap<0 and color_difference<-gap))==False:
                    keep_list.append(element)

        self.elements=[]
        for element in keep_list:
            if element.__class__.__name__ == "Polygon":
                self.add_polygon(element,"top")
            if element.__class__.__name__ == "Line":
                self.add_line(element,"top")
            if element.__class__.__name__ == "Writing":
                self.add_writing(element,"top")


    #makes corner points int numbers instead of floats
    def intify(self):
        for elem in self.elements:
            elem.intify()


        #this gives the element or a line inside a polygon that the point is located
    def where_we_are(self,point):
        size=len(self.elements)
        for i in range(0,size):
            if self.elements[size-1-i].__class__.__name__ == "Line":
                if self.element_number(size-1-i).is_inside(point) and self.element_number(size-1-i).pen_down:
                    return self.elements[size-1-i]
            if self.elements[size-1-i].__class__.__name__ == "Polygon":
                for line in self.elements[size-1-i].lines: #changed 25.8. now we should be able to click line even from "outside part" of polygon
                    if line.is_inside(point):
                        return line
                if self.element_number(size-1-i).is_inside(point): 
                    if self.element_number(size-1-i).distance_from_closest_line(point)>WHERE_WE_ARE_CONSTANT: #so if we are more than 10 pixels away from the contour
                        return self.elements[size-1-i]

        return None

    #this gives the element or a line inside a polygon that the point is located.
    #  Element is given exactly, not including any extra boundaries
    def exactly_where_we_are(self,point):
        size=len(self.elements)
        for i in range(0,size):
            if self.elements[size-1-i].__class__.__name__ == "Line":
                if self.element_number(size-1-i).is_inside(point,extra=0) and self.element_number(size-1-i).pen_down:
                    return self.elements[size-1-i]
            if self.elements[size-1-i].__class__.__name__ == "Polygon":
                for line in self.elements[size-1-i].lines: #changed 25.8. now we should be able to click line even from "outside part" of polygon
                    if line.is_inside(point,extra=0) and line.pen_down:
                        return line
                if self.element_number(size-1-i).is_inside(point): 
                    return self.elements[size-1-i]

        return None

        #this gives list of all the elements or a line inside a polygon that the point is located.
    #  Element is given exactly, not including any extra boundaries
    def all_where_we_are(self,point):
        size=len(self.elements)
        list_of_elements=[]
        for i in range(0,size):
            if self.elements[size-1-i].__class__.__name__ == "Line":
                if self.element_number(size-1-i).is_inside(point,extra=0) and self.element_number(size-1-i).pen_down:
                    list_of_elements.append(self.elements[size-1-i])
            if self.elements[size-1-i].__class__.__name__ == "Polygon":
                for line in self.elements[size-1-i].lines: #changed 25.8. now we should be able to click line even from "outside part" of polygon
                    if line.is_inside(point,extra=0) and line.pen_down:
                        list_of_elements.append(line)
                if self.element_number(size-1-i).is_inside(point): 
                    list_of_elements.append(self.elements[size-1-i])

        return list_of_elements


    #tells the info about the object in the point
    def exactly_info(self,point):
        item=self.exactly_where_we_are(point)
        if item==None:
            return "No items"
        if item.__class__.__name__== "Polygon":
            result= "Polygon: Vertices "+ str(item.vertices2())
            result += "\n Inside_color: "+str(item.inside_color)
            return result
        if item.__class__.__name__== "Line":
            result= "Line: endpoints "+ str(item.end_point1) +", "+str(item.end_point2)
            result += "\n color: "+str(item.pencolor)
            result += "\n size: "+str(item.pen_size)
            return result
        return ""
#like where_we_are, but when contourline inside of polygon is clicked, polygon is picked instead of its contourline
    def where_we_are2(self,point):
        size=len(self.elements)
        for i in range(0,size):
            if self.elements[size-1-i].__class__.__name__ == "Line":
                if self.element_number(size-1-i).is_inside(point) and self.element_number(size-1-i).pen_down:
                    return self.elements[size-1-i]
            if self.elements[size-1-i].__class__.__name__ == "Polygon":
                if self.element_number(size-1-i).is_inside(point): 
                    return self.elements[size-1-i]
                for line in self.elements[size-1-i].lines: #changed 25.8. now we should be able to click line even from "outside part" of polygon
                    if line.is_inside(point):
                        return line

        return None


    #this gives the element in which the point is located, or None if it is not located in any element
    def element_at(self,point):
        size=len(self.elements)
        for i in range(0,size):
            if self.elements[size-1-i].__class__.__name__ == "Line":
                if self.element_number(size-1-i).is_inside(point):
                    return self.elements[size-1-i]
            if self.elements[size-1-i].__class__.__name__ == "Polygon":
                if self.element_number(size-1-i).is_inside(point): 
                    return self.elements[size-1-i]

    #given list of vertices forming a polygon, this returns all elements that are at least partially inside polygon
    #formed by this verticelist
    def elements_inside_vertices(self,vertice_list):
        poly=shapely.geometry.Polygon(vertice_list)
        inside_elements=[]
        for element in self.elements:
            if element.__class__.__name__ == "Line":
                point1=element.end_point1
                point2=element.end_point2
                poi1=shapely.geometry.Point(point1[0],point1[1])
                poi2=shapely.geometry.Point(point2[0],point2[1])
                if poi1.within(poly) or poi2.within(poly):
                    inside_elements.append(element)
            if element.__class__.__name__ == "Polygon":
                cond=False
                for point in element.vertices(): 
                    poi=shapely.geometry.Point(point[0],point[1])
                    if poi.within(poly):
                        cond=True
                if cond:
                    inside_elements.append(element)
            if element.__class__.__name__ == "Writing":
                cond=False
                for point in element.placement(): 
                    poi=shapely.geometry.Point(point[0],point[1])
                    if poi.within(poly):
                        cond=True
                if cond:
                    inside_elements.append(element)
        return inside_elements

    #lists all the points in this drawing such that polygon with list of vertices 'vertice_list' intersects this drawing
    def intersections_with_polygon(self,vertice_list):
        list_of_points=[]
        for i in range(len(vertice_list)):
            point1=vertice_list[i-1]
            point2=vertice_list[i]
            list_of_points += self.plist_of_crossing_points(point1,point2)
        return list_of_points

    #given a vertice_list (which forms a polygon) bend all elements in this drawing that intersect with this polygons contour
    #remember that bending means creating a new vertice point in given position
    def bend_intersections_with_vertice_list(self,vertice_list):
        list_of_points=self.intersections_with_polygon(vertice_list)
        for point in list_of_points:
            self.bend_all(point)



    #if element number is a line, removes this line and replace it with two lines connected at point
    def bend(self,element,point):
        for i in range(len(self.elements)):
            if self.elements[i]==element and element.__class__.__name__ == "Line":
                new_lines=element.splitlines(point)
                self.elements=self.elements[:i]+new_lines+self.elements[i+1:]
                return new_lines
            if self.elements[i].__class__.__name__ == "Polygon":
                for j in range(len(self.elements[i].lines)):
                    if self.elements[i].lines[j]==element:
                        new_lines=element.splitlines(point)
                        self.elements[i].lines=self.elements[i].lines[:j]+new_lines+self.elements[i].lines[j+1:]
                        return new_lines

    #fast way to bend all points going near 'point' to go through it
    def bend_all(self,point):
        clines=self.contour_line_list()
        for cline in clines:
            if distance_from_line_segment(cline,point)<OVERLAP_CONSTANT:
                cline.splitlines(point)

    #split a polygon to two polygons, splitting starts from point1 and ends in point2
    def split_polygon(self,poly,point1,point2):
        line1=poly.closest_line(point1)
        line1point=(int(nearest_point_on_line(line1,point1)[0]),int(nearest_point_on_line(line1,point1)[1]))
        line2=poly.closest_line(point2)
        line2point=(int(nearest_point_on_line(line2,point2)[0]),int(nearest_point_on_line(line2,point2)[1]))
        lnro1=poly.line_nro(line1)
        lnro2=poly.line_nro(line2)
        if lnro1<lnro2:
            new_poly1=Polygon()
            new_poly1.inside_color=poly.inside_color
            new_poly1.lines=poly.lines[0:lnro1]
            line1split=line1.copy()
            line1split.set_end_point2(line1point)
            connect_line=line1split.copy()
            connect_line.set_end_point1(line1point)
            connect_line.set_end_point2(line2point)
            line2split=line2.copy()
            line2split.set_end_point1(line2point)
            new_poly1.lines.append(line1split)
            new_poly1.lines.append(connect_line)
            new_poly1.lines.append(line2split)
            new_poly1.lines += poly.lines[lnro2+1:]
            
            new_poly2=Polygon()
            connect_line2=line1split.copy()
            connect_line2.set_end_point1(line2point)
            connect_line2.set_end_point2(line1point)
            line1split2=line1.copy()
            line1split2.set_end_point1(line1point)
            new_poly2.lines=[connect_line2]+[line1split2]+poly.lines[lnro1+1:lnro2]
            line2split2=line2.copy()
            line2split2.set_end_point2(line2point)
            new_poly2.lines.append(line2split2)
            new_poly2.inside_color=poly.inside_color
            self.elements.append(new_poly1)
            self.elements.append(new_poly2)
            self.remove_element(poly)
        if lnro2<lnro1:# if points were clicked "in the wrong order"
            self.split_polygon(poly,point2,point1)





    #glues lines line1 and line2 colors, pensize etc. are taken from the line1
    def glue(self,point1,point2):
        line1=self.where_we_are(point1)
        line2=self.where_we_are(point2) 
        if line1.pen_down==False or line2.pen_down==False: #we must see both lines
            return
        
        if line1.__class__.__name__!="Line" or line2.__class__.__name__!="Line":
            return
        
        line1_end=1
        if pdistance(line1.end_point1,point1)>pdistance(line1.end_point2,point1):
            line1_end=2

        line2_end=1
        if pdistance(line2.end_point1,point2)>pdistance(line2.end_point2,point2):
            line2_end=2
        new_line=line1.glue_line(line2,line1_end,line2_end)
        self.remove_line(line1)
        self.remove_line(line2)
        self.add_line(new_line,"top")

    #changes the fill_color of clicked polygon. returns True if there was a polygon
    def change_fillcolor(self,point,new_fc):
        loc=self.where_we_are(point)
        if loc.__class__.__name__ == "Polygon":
            loc.inside_color=new_fc
            return True
        return False 
            

    #return parameters which tell pen-values after element. if element_number is negative, we give some fixed values.
    def parameters_after_element(self,element_number):
        c_location=(0,0)
        (new_x,new_y)=(0,0)
        c_thickness=5
        c_pen_color=[0.5,0.5,0.5]
        c_pen_down=True
        c_fill_color=[0.5,0.5,0.5]
        lout=Line(c_location,(new_x,new_y),c_thickness,c_pen_color,c_pen_down,True,c_fill_color)
        if element_number==0:
            return [lout.end_point1,lout.end_point2,lout.thickness,lout.pencolor,lout.pen_down,lout.fillcolor]
        if element_number>=0:
            if self.elements[element_number].__class__.__name__ == "Line":
                lout=self.elements[element_number]    
            if self.elements[element_number].__class__.__name__ == "Polygon":
                lout=self.elements[element_number].lines[-1]#i.e. the last line in the polygon (usually pen_up line)
        return [lout.end_point1,lout.end_point2,lout.thickness,lout.pencolor,lout.pen_down,lout.fillcolor]
    #parameters are [0]->where this element started [1]->point where we are, [2]-> pensize, [3]-> color, [4]-> pen_down, [5]-> fillcolor 

    #inserts a copy of line next to its position (so might be elsewhere than top or bottom)
    def insert_line_copy(self,item):
        enro=self.get_element_number(item)
        if enro != -1:
            itemcopy=item.copy()
            self.elements.insert(enro,itemcopy)
            return itemcopy
        for i in range(len(self.elements)): #if item is a line in polygon, a copy of this line is added in the polygon
            if self.elements[i].__class__.__name__=="Polygon":
                for j in range(len(self.elements[i].lines)):
                    itemcopy=item.copy()
                    self.elements[i].lines.insert(j,itemcopy)
                    return itemcopy


    #Polygon is added on the picture, where can be "top" or "botton"
    def add_polygon(self,poly:Polygon,where="top"):
        if where=="top" and len(poly.lines)>0:
            lpar=self.parameters_after_element(len(self.elements)-1)
            moving_line=Line(lpar[1],poly.lines[0].end_point1,lpar[2],lpar[3],False,True,lpar[5])
            self.elements.append(moving_line)
            if pdistance(poly.lines[0].end_point1,lpar[1])>OVERLAP_CONSTANT: #1 is test value, this tells that if polygon start and ending point aren't same, a
               # new invisible line is added between them
                jump_line=Line(poly.lines[-1].end_point2,poly.lines[0].end_point1,lpar[2],lpar[3],False,True,lpar[5]) #jumping must be invisible
                poly.lines.append(jump_line)
            for line in poly.lines: #Add contourlines of the polygon
                self.add_line(line,"top")
            self.elements.append(poly) #add the polygon
            size=len(self.elements)
            self.elements=self.elements[0:size-len(poly.lines)-1]+self.elements[size-1:size] #remove the contourlines from the elements
            #self.polygon_adding_effects(poly) #this isn't yet finished method

            
        if where=="bottom"and len(poly.lines)>0:
            jump_line=Line(lpar[0],self.parameters_after_element(0)[0],lpar[1],lpar[2],False,True,lpar[4]) #jumping must be invisible
            self.elements.insert(0,poly)#add poly to beginning
            self.elements.insert(1,jump_line)

    #adds writing in the drawing
    def add_writing(self,text:Writing,where="top"):
        if where=="top":
            self.elements.append(text)
        if where=="bottom":
            self.elements=text+self.elements

    #adds a single line in the drawing. There might be a problem due to adding this without a "jump" 
    # which makes a gap between this and previous lines 
    def add_line(self,lin:Line,where="top"):
        if where=="top":
            self.elements.append(lin)
        if where=="bottom":
            self.elements=[lin]+self.elements

    def add_circle(self,centerpoint,radius,thickness,color=[0.5,0.5,0.5],fillcolor=[0.2,0.2,0.2],pendown=True,filled=False,where="top",writings=[]):
        lines_to_add=intify(circle_lines(centerpoint,radius,thickness,color,fillcolor,pendown,filled))
        if filled:
            self.add_polygon(polygonize(lines_to_add,fillcolor,writings),where)
            return
        else:
            self.add_linelist(lines_to_add,where)

    #adds an arc (as list of lines, not polygo, to drawing)
    def add_arc(self,centerpoint,radius,starting_point,thickness,color=[0.5,0.5,0.5],fillcolor=[0.2,0.2,0.2],pendown=True,angle=90,where="top",writings=[]):
        lines_to_add=intify(arc_lines(centerpoint,radius,starting_point,thickness,color,fillcolor,pendown,angle))
        self.add_linelist(lines_to_add,where)

    #adds a rectangle with diagonal corners cornerpoint1, and cornerpoint2
    def add_rectangle(self,cornerpoint1,cornerpoint2,thickness,color=[0.5,0.5,0.5],fillcolor=[0.2,0.2,0.2],pendown=True,filled=False,where="top"):
        line1=Line(cornerpoint1,(cornerpoint1[0],cornerpoint2[1]),thickness,color,pendown,True,fillcolor)
        line2=Line((cornerpoint1[0],cornerpoint2[1]),cornerpoint2,thickness,color,pendown,True,fillcolor)
        line3=Line(cornerpoint2,(cornerpoint2[0],cornerpoint1[1]),thickness,color,pendown,True,fillcolor)
        line4=Line((cornerpoint2[0],cornerpoint1[1]),cornerpoint1,thickness,color,pendown,True,fillcolor)
        lines_to_add=[line1,line2,line3,line4]
        if filled:
            self.add_polygon(polygonize(lines_to_add,fillcolor,[]),where)
            return
        else:
            self.add_linelist(lines_to_add,where)

    def add_oval(self,centerpoint,x_radius,y_radius,thickness,color=[0.5,0.5,0.5],fillcolor=[0.2,0.2,0.2],pendown=True,filled=False,where="top",writings=[]):
        lines_to_add=intify(oval_lines(centerpoint,x_radius,y_radius,thickness,color,fillcolor,pendown,filled))
        if filled:
            self.add_polygon(polygonize(lines_to_add,fillcolor,writings),where)
            return
        else:
            self.add_linelist(lines_to_add,where)

    #adds a list of lines to drawing.There might be a problem due to adding this without a "jump" 
    # which makes a gap between this and previous lines 
    def add_linelist(self,linelist:Line,where="top"):
        if where=="top":
            for line in linelist:
                self.add_line(line,"top")
        if where=="bottom":#lines are actually in such a way that the last one ends totally in the bottom
            for line in linelist:
                self.add_line(line,"bottom")

    #this makes thing happen to lines under line1, for example removing them if they are completely under line1
    def handle_underlaying(self,line1):
        contourlines=self.contour_line_list()
        size=len(contourlines)
        if size>1: #i.e. if line is not only element
            for i in range(size-1):
                self.top_line_effect(line1,contourlines[size-i-2])

    #we look at a 'point' and we split all the lines going very near it to two lines joined by this point 
    def crossing_point_effect(self,point):
        contourlines=self.contour_line_list()
        size=len(contourlines)
        for line in contourlines:
            if distance_from_line_segment(line,point)<OVERLAP_CONSTANT:
                self.bend(line,point)

    def polygon_adding_effects(self,polygon):
        effecting_lines=polygon.lines
        effected_lines=self.contour_line_list()
        for line in effecting_lines:
            for eline in effected_lines:
                if eline not in effecting_lines:
                    self.top_line_effect(line,eline)
        self.remove_underlaying_lines(polygon)
        self.remove_underlaying_polygons(polygon)
        #for eline in effected_lines:
        #    if eline not in effecting_lines:
        #        self.top_polygon_effect(polygon,eline) 

    #removes lines that are under 'polygon' 
    def remove_underlaying_lines(self,polygon:Polygon):
        for tested_element in self.elements:
            if tested_element.__class__.__name__=="Line":
                if polygon.is_line_inside(tested_element):
                    self.remove_line(tested_element)
            
    #removes polygons that are under 'polygon' 
    def remove_underlaying_polygons(self,polygon:Polygon):
        for tested_element in self.elements:
            if tested_element.__class__.__name__=="Polygon":
                if polygon.is_inside_polygon(tested_element):
                    self.remove_element_number(self.get_element_number(tested_element))



        

    #Contourline line1 induces these effects to the line2 when line1 is added 
    def top_line_effect(self,line1,line2):
        relation_type=line1.relative_position(line2)
        if relation_type in ["same","reverse","covers","reversecovers","halfcovers11","halfcovers12","halfcovers21","halfcovers22"]:
            self.remove_line(line2)
        if relation_type == "halfcovers11":
            line2.set_end_point1(line1.end_point2)
        if relation_type == "halfcovers12":
            line2.set_end_point2(line1.end_point2)   
        if relation_type == "halfcovers21":
            line2.set_end_point1(line1.end_point1)   
        if relation_type == "halfcovers22":
            line2.set_end_point2(line1.end_point1)   
        if relation_type == "covered":
            new_lines=self.bend(line2,(0,0)) #this both splits the line (destroying it) and returns the splitted lines added
            new_lines[0].set_end_point2(line1.end_point1)#this is the first "half" of the splitted line
            new_lines[1].set_end_point1(line1.end_point2) #second half
        if relation_type == "reversecovered":
            new_lines=self.bend(line2,(0,0))
            new_lines[0].set_end_point2(line1.end_point2)#this is the first "half" of the splitted line
            new_lines[1].set_end_point1(line1.end_point1) #secon half
        if relation_type== "overlaps11":
            line2.set_end_point1(line1.end_point1)
        if relation_type== "overlaps12":
            line2.set_end_point2(line1.end_point1)
        if relation_type== "overlaps21":
            line2.set_end_point1(line1.end_point2)
        if relation_type== "overlaps22":
            line2.set_end_point2(line1.end_point2)

    #Contourline line1 induces these effects to the line2 when line1 is added 
    def top_polygon_effect(self,polygon,line2):
        list_of_intersections=[line2.end_point1,line2.end_point2]
        for line1 in polygon.lines:
            if is_there_intersection(line1,line2):
                list_of_intersections += line_intersections(line1,line2)
        
        ordered_inters=[] #here we list all intersection points in ascending order
        if has_a_slope(line2):
            ordered_inters=points_ordered_by_x(list_of_intersections)
        else:
            ordered_inters=points_ordered_by_x(list_of_intersections)
        
        middle_points=[] #here we calculate middle points between intersections. Next we evaluate if they are inside polygon and act accordingly
        if len(ordered_inters)>=2:
            middle_points.append(((ordered_inters[0][0]+ordered_inters[1][0])/2,(ordered_inters[0][1]+ordered_inters[1][1])/2))
            for i in range(1,len(ordered_inters)-1):
                middle_points.append(((ordered_inters[i][0]+ordered_inters[i+1][0])/2,(ordered_inters[i][1]+ordered_inters[i+1][1])/2))

            for i in range(len(middle_points)):
                if polygon.is_inside(middle_points[i])==False:
                    new_line=self.insert_line_copy(line2)#new line is inserted and can be operated by name new_line
                    new_line.set_end_point1((round(ordered_inters[i][0]),round(ordered_inters[i][1]))) 
                    new_line.set_end_point2((round(ordered_inters[i+1][0]),round(ordered_inters[i+1][1]))) 
            self.remove_line(line2)


    #removes element, argument is the element itself
    def remove_element(self,element):
        for i in range(len(self.elements)):
            if self.elements[i]==element:
                self.remove_element_number(i)
                return #list might get shorter and error happens, without this return

    #removes the element from Drawing
    def remove_element_number(self,element_number):
        self.elements.pop(element_number)
    
    #gives an element_number of element, if it has one
    def get_element_number(self,element):
        for i in range(len(self.elements)):
            if self.elements[i]==element:
                return i
        return -1

    #removes element from drawing by locating it by point. Element might also be line in polygons contour so not member of self.elements
    def remove_element_at(self,point):
        element=self.exactly_where_we_are(point)
        if element in self.elements:
            if self.get_element_number(element) != -1:
                self.remove_element_number(self.get_element_number(element))
                helpstring=reduce(self.from_Drawing_to_temp_string())
                self=Drawing(helpstring)
                return None
        for poly in self.elements: #name is little missleading, this is not always polygon
            if poly.__class__.__name__ == "Polygon":
                if element in poly.lines:
                    poly.lines.remove(element)
                    helpstring=reduce(self.from_Drawing_to_temp_string())
                    self=Drawing(helpstring)
                    return None
    
    #this should be a faster way to remove all elements at point, than just removing them one by one using remove_element_at
    def remove_all_elements_at(self,point): #not tested yet
        elements=self.all_where_we_are(point)
        for element in elements:
            if element in self.elements:
                if self.get_element_number(element) != -1:
                    self.remove_element_number(self.get_element_number(element))
        for poly in self.elements: #name is little missleading, this is not always polygon
            if poly.__class__.__name__ == "Polygon":
                if element in poly.lines:
                    poly.lines.remove(element)
        #There might be an error: if we remove lines in the contour of the polygon, does the inside of polygon survive this unscathered?
        #(as it should)
        helpstring=reduce(self.from_Drawing_to_temp_string())
        self=Drawing(helpstring)

    def remove_contourline_number(self,linenumber):
        contour_line=self.contour_line_list()[linenumber]
        if contour_line in self.elements:
            if self.get_element_number(contour_line) != -1:
                self.remove_element_number(self.get_element_number(contour_line))
                helpstring=reduce(self.from_Drawing_to_temp_string())
                self=Drawing(helpstring)
                return None
        for poly in self.elements: #name is little missleading, this is not always polygon
            if poly.__class__.__name__ == "Polygon":
                if contour_line in poly.lines:
                    poly.lines.remove(contour_line)
                    helpstring=reduce(self.from_Drawing_to_temp_string())
                    self=Drawing(helpstring)
                    return None

    #removes the line (if its in the drawing)
    def remove_line(self,line:Line):
        size=len(self.elements)
        if size>0:
            for i in range(len(self.elements)):
                if self.elements[size-i-1].__class__.__name__ == "Line":
                    if self.elements[size-i-1]==line:
                        self.elements.pop(size-i-1)

                size=len(self.elements) #size must change when elements are taken a eay
                if self.elements[size-i-1].__class__.__name__ == "Polygon":
                    psize=len(self.elements[size-i-1].lines)
                    for j in range(psize):

                        if self.elements[size-i-1].lines[psize-j-1]==line:
                            self.elements[size-i-1].lines.pop(psize-j-1)      



    #this takes all the point in start location (or within distance smaller than precision), to end_loc
    def move_vertice(self,start_loc,end_loc,precision=VERTICE_CONSTANT):
        for line in self.contour_line_list():
            if distance(line.end_point1_x(),line.end_point1_y(),start_loc[0],start_loc[1])<precision:
                line.set_end_point1(end_loc)
            if distance(line.end_point2_x(),line.end_point2_y(),start_loc[0],start_loc[1])<precision:
                line.set_end_point2(end_loc)

    #moves vertices, lines or polygons depending on clicking point
    def move(self,start_loc,end_loc,precision=VERTICE_CONSTANT):
        verticemove=False
        for line in self.contour_line_list():
            if distance(line.end_point1_x(),line.end_point1_y(),start_loc[0],start_loc[1])<precision:
                line.set_end_point1(end_loc)
                verticemove=True
            if distance(line.end_point2_x(),line.end_point2_y(),start_loc[0],start_loc[1])<precision:
                line.set_end_point2(end_loc)
                verticemove=True
        if verticemove:
            self.move_vertice(start_loc,end_loc)
            return

        element=self.where_we_are(start_loc)
        if element.__class__.__name__=="Line": #grabs line and moves it with same amount from both ends
            line_point=nearest_point_on_line(element,start_loc)
            line_point=(int(line_point[0]),int(line_point[1]))
            self.move_vertice(element.end_point1,(element.end_point1[0]+end_loc[0]-line_point[0],element.end_point1[1]+end_loc[1]-line_point[1]))
            self.move_vertice(element.end_point2,(element.end_point2[0]+end_loc[0]-line_point[0],element.end_point2[1]+end_loc[1]-line_point[1]))
        if element.__class__.__name__=="Polygon":
            for line in element.lines:
                line.end_point1=(line.end_point1[0]+end_loc[0]-start_loc[0],line.end_point1[1]+end_loc[1]-start_loc[1])
                line.end_point2=(line.end_point2[0]+end_loc[0]-start_loc[0],line.end_point2[1]+end_loc[1]-start_loc[1])




    #Returns lines in an order they are formed in the original temp_str given in init
    def line_list(self):
        array=[]
        for i in range(len(self.elements)):
            if self.elements[i].__class__.__name__ == "Line":
                array.append(self.elements[i])
            
            if self.elements[i].__class__.__name__ == "Polygon":
                for line in self.elements[i].lines:
                    array.append(line)

        return array

    #Returns polygons in an order they are formed in the original temp_str given in init
    def polygon_list(self):
        array=[]  
        for i in range(len(self.elements)):  
            if self.elements[i].__class__.__name__ == "Polygon":
                array.append(self.elements[i])

        return array
    
    #this gives a list of lines that are relevant in coloring, i.e. pen must be down or we must be in a polygon
    def contour_line_list(self):
        array=[]
        for i in range(len(self.elements)):
            if self.elements[i].__class__.__name__ == "Line":
                if self.elements[i].pen_down:
                    array.append(self.elements[i])
            
            if self.elements[i].__class__.__name__ == "Polygon":
                for line in self.elements[i].lines:
                    array.append(line)
        return array

    #taking contour_lines from this drawing, returns a Drawing with only contourlines showing
    def contour_line_Drawing(self):
        line_list=self.contour_line_list()
        new_Drawing=Drawing("")
        for line in line_list:
            line.thickness=1
            line.pencolor=(0,0,1)
            new_Drawing.add_line(line)
        return new_Drawing


    #returns ture if point is in contourline
    def is_in_contourline(self,point):
        clines=self.contour_line_list()
        for cline in clines:
            if distance_from_line_segment(cline,point)<0.000001:
                return True
        return False
    
    #if line going throug point and point2 intersects a contourline, returns True, else False
    #def intersects_contour_line(self,point1,point2):
    #    clines=self.contour_line_list()
    #    linified=Line(point1,point2,1,[0,0,0],True,True,[0,0,0])
    #    for cline in clines:
    #        if linified.relative_position(cline)=="crossing":
    #            return True
    #    return False

    #returns lines contour_linenumber, if it is in the contour_lines. If it is in many places, returns the largest number
    def contour_linenumber(self,line):
        csize=len(self.contour_line_list())
        for i in range(csize):
            if self.contour_line_list()[csize-1-i]==line:
                return csize-1-i
        return None


    #returns the type of line_number
    def type_of_contour(self,line_number):
        return self.contourline_type_list[line_number]

    #includes penup lines
    def line_with_linenumber(self,line_number):
        if line_number not in range(len(self.line_list())):
            raise IndexError("There is no line with such an index")
        return self.line_list()[line_number]
    
    #does not include penup lines
    def line_with_contour_linenumber(self,contour_line_number):
        if contour_line_number not in range(len(self.contour_line_list())):
            raise IndexError("There is no line with such an index")
        return self.contour_line_list()[contour_line_number]

    #lists the type of line, is it in a polygon or just line
    def line_type_list(self):
        array=[]
        counter=0
        for i in range(len(self.elements)):
            if self.elements[i].__class__.__name__ == "Line":
                if self.elements[i].pen_down:
                    array.append("linedown")
                if self.elements[i].pen_down==False:
                    array.append("lineup")
            
            if self.elements[i].__class__.__name__ == "Polygon":
                for line in self.elements[i].lines:
                    array.append("polygon")

        return array
    
    #lists a string descriping all contour lines types. Note that if line is both in self.elements and inside polygon
    #it is listed as a line in both TESTED 9.8.
    def contourline_type_list(self):
        result_list=[]
        list_of_elements=self.elements
        for cline in self.contour_line_list():
            if cline in list_of_elements:
                result_list.append("line")
            else:
                result_list.append("polygonline")
        return result_list


    #gives an array of index-pairs, where index-pair (i,j) represents that lines i and j cross each other 
    def list_of_crossings_index_pairs(self):
        list_of_lines=self.contour_line_list()
        crossings=[]
        size=len(list_of_lines)
        for i in range(0,size):
            for j in range(0,size):
                if is_there_intersection(list_of_lines[i],list_of_lines[j]):
                    crossings.append((i,j))
        return crossings

    #if we knoe the line_number, this lists the indexes(numbers) of lines that cross it. Saves computer time. 
    def list_of_crossing_indexes(self,contour_line_number):
        list_of_lines=self.contour_line_list()
        crossings=[]
        size=len(list_of_lines)
        for j in range(0,size):
            if is_there_intersection(list_of_lines[contour_line_number],list_of_lines[j]):
                crossings.append(j)
        return crossings        

    def contour_info(self):
        infostr=""
        counter=0
        for line in self.contour_line_list():
            infostr += "Contour line "+str(counter)+": "+ line.represent_as_temp_str()+"\n"
            counter+=1
        return infostr

    #lists points where lines[line_number] crosses another line
    def list_of_crossing_points_on_line(self,contour_line_number):
        array=self.list_of_crossing_indexes(contour_line_number)
        points=[]
        for item in array:
            for intersection in line_intersections(self.contour_line_list()[contour_line_number],self.contour_line_list()[item]):
                if self.contour_line_list()[contour_line_number] in self.contour_line_list():#so invisible lines do not add intersecions
                    points.append(intersection)
        return points       
    
        #lists points where line crosses another line
    def list_of_crossing_points(self,line):
        clines=self.contour_line_list()
        crossing_points=[]
        for cline in clines:
            if is_there_intersection(cline,line):
                crossing_points += line_intersections(cline,line)
        return crossing_points
    
        #lists points where line with endpoint point1 and point2 is crossed by contourline
    def plist_of_crossing_points(self,point1,point2):
        clines=self.contour_line_list()
        crossing_points=[]
        for cline in clines:
            if pis_there_intersection(point1,point2,cline.end_point1,cline.end_point2):
                crossing_points += pline_intersections(point1,point2,cline.end_point1,cline.end_point2)
        return crossing_points

    #returns True iiff we can move from point1 to point2 without intersecting contourlines
    def pno_crossing(self,point1,point2):
        crossings= self.plist_of_crossing_points(point1,point2)
        if crossings != []:
            for cross in crossings:
                if pdistance(cross,point1)>0.00001 and pdistance(cross,point2)>0.00001: #it is okay to "cross" in endpoints
                    return False
        return True


    #This finds a next intersection that line has, starting from starting_location. If direction is True, we go from end_point1
    #towards end_point2, if false, to the opposite direction.
    def next_intersection_point(self,contour_linenumber:int,starting_location,forward:bool):
        lines=self.contour_line_list()
        if distance_from_extended_line(lines[contour_linenumber],starting_location)>OVERLAP_CONSTANT: #this may or may not need adjustment
            raise ValueError("The point isn't in the line")
        potential_values=self.list_of_crossing_points_on_line(contour_linenumber)
        correct_value=starting_location
        smallest_distance=10000000
        tcd=0.0000006#too_close_distance changed 27.8.
        for pval in potential_values:
            d_start_pot= distance(pval[0],pval[1],starting_location[0],starting_location[1])
            d_endpoint1_pot=distance(pval[0],pval[1],lines[contour_linenumber].end_point1_x(),lines[contour_linenumber].end_point1_y())
            d_start_endpoint1=distance(starting_location[0],starting_location[1],lines[contour_linenumber].end_point1_x(),lines[contour_linenumber].end_point1_y())
            if tcd<d_start_pot<smallest_distance and forward and d_endpoint1_pot>d_start_endpoint1:
                correct_value=pval
                smallest_distance=d_start_pot
            if tcd<d_start_pot<smallest_distance and forward==False and d_endpoint1_pot<d_start_endpoint1:
                correct_value=pval
                smallest_distance=d_start_pot
        return correct_value #note that if there is no next_intersection point, this returns the starting_location

    #just next intersection of line
    def next_intersection(self,line,starting_location,forward:bool):
        if forward==False: #if we want to go backwards just change the end points of line
            epo1=line.end_point1
            epo2=line.end_point2
            line.set_end_point1(epo2)
            line.set_end_point2(epo1)
        if distance_from_extended_line(line,starting_location)>OVERLAP_CONSTANT: #this may or may not need adjustment
            raise ValueError("The point isn't in the line")
        potential_values=self.list_of_crossing_points(line)
        correct_value=None #this used to be starting location, now it is changed
        smallest_distance=10000000
        tcd=0.0006#too_close_distance changed 28.8.

        for pval in potential_values:
            d_start_pot= distance(pval[0],pval[1],starting_location[0],starting_location[1])
            d_endpoint2_pot=distance(pval[0],pval[1],line.end_point2_x(),line.end_point2_y())
            d_start_endpoint2=distance(starting_location[0],starting_location[1],line.end_point2_x(),line.end_point2_y())
            if tcd<d_start_pot<smallest_distance and d_endpoint2_pot<d_start_endpoint2 and d_start_pot<d_start_endpoint2+0.0001:
                correct_value=pval
                smallest_distance=d_start_pot
        return correct_value #note that if there is no next_intersection point, this returns the starting_location
    
    #what is the next point that (possibly imaginary) line with end points epo1 and epo2 crosses some contourline
    #this is defined in such a way that starting_location could be outside of "line" epo1-epo2. Don't use it in such way though
    def pnext_intersection(self,epo1,epo2,starting_location,forward:bool):
        if forward==False: #if we want to go backwards just change the end points of line
            helpp=epo1
            epo1=epo2
            epo2=helpp

        potential_values=self.plist_of_crossing_points(epo1,epo2)
        correct_value=None #this used to be starting location, now it is changed
        smallest_distance=10000000
        tcd=0.00006#too_close_distance changed 27.8.

        for pval in potential_values:
            d_start_pot= distance(pval[0],pval[1],starting_location[0],starting_location[1])
            d_endpoint2_pot=distance(pval[0],pval[1],epo2[0],epo2[1])
            d_start_endpoint2=distance(starting_location[0],starting_location[1],epo2[0],epo2[1])
            if tcd<d_start_pot<smallest_distance and d_endpoint2_pot<d_start_endpoint2 and d_start_pot<d_start_endpoint2+0.0001:
                correct_value=pval
                smallest_distance=d_start_pot
        return correct_value #note that if there is no next_intersection point, this returns the starting_location
    
    #given two points in lines[line_number] this method returns the next point we end up by following lines to clockwise direction
    def clockwise_line_step(self,contour_line_number,point1,point2):
        result_line_number=contour_line_number
        result_point1=point2#this doesn't change
        result_point2=point1#  these values mean that if we don't find continuation, we turn back to where we started

        list_of_lines_through_result_point1=self.contour_linenumbers_with_point(result_point1)
        list_of_potential_result_point2=[]
        for contour_linenumber in list_of_lines_through_result_point1:
            forward_pot=self.next_intersection_point(contour_linenumber,result_point1,True)
            backward_pot=self.next_intersection_point(contour_linenumber,result_point1,False)
            if distance(forward_pot[0],forward_pot[1],point2[0],point2[1])>0.1:#this 1 is a guess which might work or not
                list_of_potential_result_point2.append(forward_pot)
            if distance(backward_pot[0],backward_pot[1],point2[0],point2[1])>0.1:#this 1  is a guess which might work or not
                list_of_potential_result_point2.append(backward_pot)

        original_heading=angle_to(point2[0],point2[1],point1[0],point1[1]) #this actually in "backwards direction" to simplify calculations
        best_heading=361#we try to minimize this
        for pot_result2 in list_of_potential_result_point2:
            second_heading=angle_to(point2[0],point2[1],pot_result2[0],pot_result2[1])
            comparing_heading=second_heading-original_heading
            if comparing_heading<=0:
                comparing_heading +=360
            if comparing_heading<best_heading and is_same(pot_result2,point1)==False:#this should make sure that if there is point
                #that is not the same as the starting point, then we don't go back
                result_point2 =pot_result2
                best_heading=comparing_heading

        lines_of_possibilities=self.contour_linenumbers_with_point(result_point2)
        for linep in lines_of_possibilities:
            if linep in list_of_lines_through_result_point1: #ie this linep goes through both starting_point1 and 2
                result_line_number=linep
        return (result_line_number,result_point1,result_point2) #if everything is done correctly this gives the information for next
        #clockwise step

    #list lines with one endpoint (almost) the same as point
    def contour_linenumbers_with_endpoint(self,point):
        lines=self.contour_line_list()
        result=[]
        for i in range(len(lines)):
            if abs(lines[i].end_point1_x()-point[0])<= OVERLAP_CONSTANT and abs(lines[i].end_point1_y()-point[1])<= OVERLAP_CONSTANT:
                result.append(i)              #before there was 1 in the place of OVERL...:
            elif abs(lines[i].end_point2_x()-point[0])<= OVERLAP_CONSTANT and abs(lines[i].end_point2_y()-point[1])<= OVERLAP_CONSTANT:
                result.append(i)
        return result


    #return list of linenumbers of lines where point is (almost) located
    def linenumbers_with_point(self,point):
        lines=self.line_list()
        result=[]
        for i in range(len(lines)):
            if distance_from_extended_line(lines[i],point)<OVERLAP_CONSTANT: #before there was 0.00001 in the place of OVERL...
                endp1_distance=distance(lines[i].end_point1_x(),lines[i].end_point1_y(),point[0],point[1])
                endp2_distance=distance(lines[i].end_point2_x(),lines[i].end_point2_y(),point[0],point[1])
                if endp1_distance+endp2_distance<lines[i].lenght() +OVERLAP_CONSTANT:#before there was 0.00001 in the place of OVERL...
                    result.append(i)
        return result
    
        #return list of linenumbers of lines where point is (almost) located
        #TESTED 9.8.
    def contour_linenumbers_with_point(self,point):
        lines=self.contour_line_list()
        result=[]
        for i in range(len(lines)):
            if distance_from_extended_line(lines[i],point)<OVERLAP_CONSTANT:
                endp1_distance=distance(lines[i].end_point1_x(),lines[i].end_point1_y(),point[0],point[1])
                endp2_distance=distance(lines[i].end_point2_x(),lines[i].end_point2_y(),point[0],point[1])
                if endp1_distance+endp2_distance<lines[i].lenght() +OVERLAP_CONSTANT:
                    result.append(i)
        return result

    #for testing mainly
    def number_of_contour_lines(self):
        return len(self.contour_line_list())

    #starting from the point, this finds a closest (intersection)point in Drawing from it. It returns this linenumber, this point,
    #and a point for travelling to clockwise direction from this point
    def first_clockwise_step(self,point):
        lines=self.contour_line_list()
        starting_linenumber=None#this will be the line that is first travelled when polygon is made. It is chosen to be the line
        #that forms an angle with 'point' that this lines angle-first_angle is minimized
        starting_triplet=None #here we put the info to construct the first line segment
        mindist=10000000
        starting_point1=None
        starting_point2=None
        pot_starting_point1=None
        for i in range(len(lines)): #we look first to line closest to point
            #lähellä olevin piste
            pot_nearest_point=nearest_point_on_line(lines[i],point)
            pot_nearest_distance=distance_from_line_segment(lines[i],point)
            if pot_nearest_distance<mindist:
                starting_linenumber=i#this is probably unnecessary since this value is changed later
                mindist=pot_nearest_distance
                pot_starting_point1=pot_nearest_point
        #intersection points for nearest line:
        first_end_point=self.next_intersection_point(starting_linenumber,pot_starting_point1,True)
        second_end_point=self.next_intersection_point(starting_linenumber,pot_starting_point1,False)
        #headings from closest point to intersection of neares line
        first_heading=angle_to(point[0],point[1],first_end_point[0],first_end_point[1]) 
        second_heading=angle_to(point[0],point[1],second_end_point[0],second_end_point[1]) 
        if (second_heading-first_heading)%360<180: #there is a reason to this 
            starting_point1=second_end_point
            starting_point2=first_end_point
        else:
            starting_point1=first_end_point
            starting_point2=second_end_point

        starting_triplet=(starting_linenumber,starting_point1,starting_point2)
        return starting_triplet
    
    

    #draws a convex polygon which contains point, currenty contour_style has no meaning
    def convex_Polygon(self,point,fillcolor=[0.5,0.5,0.5],start_angle=0,rotation=360):
        clines=[]
        vertice_list=self.convex_Polygon_vertices(point,start_angle,rotation)
        if len(vertice_list)<=2: #not enough vertices to make polygon
            return None
        for i in range(len(vertice_list)-1):
            clines.append(Line(vertice_list[i],vertice_list[i+1],1,[0,0,0],False,False,fillcolor))
        clines.append(Line(vertice_list[len(vertice_list)-1],vertice_list[0],1,[0,0,0],False,False,fillcolor))
        poly=polygonize(clines,fillcolor,[])
        return poly
    
    #draws a convex polygon which contains point, currenty contour_style has no meaning
    def convex_Polygon_vertices(self,point,start_angle,rotation):
        vertice_list=[]
        angle=0
        len_CONST=10000
        first_point=(point[0]+x_movement(angle+start_angle,len_CONST),point[1]+y_movement(angle,len_CONST))
        test_line=Line(point,first_point,1,[0,0,0],True,True,[1,1,1])
        vertice_list.append(self.next_intersection(test_line,point,True))
        angle += 10
        condition=True
        while condition==True and angle<rotation: # we try to add second point until we find one of which adding does not cross lines  
            sec_point=(point[0]+x_movement(angle+start_angle,len_CONST),point[1]+y_movement(angle+start_angle,len_CONST))
            test_line=Line(point,sec_point,1,[0,0,0],True,True,[1,1,1])
            try_point=self.next_intersection(test_line,point,True)
            if self.pno_crossing(vertice_list[0],try_point) and self.pno_crossing(point,middle_point(vertice_list[0],try_point)):
                #second condition is also important, since no crossing might happen from the "outside"
                vertice_list.append(try_point)
                condition=False
            angle += 10

        while angle<360:
            third_point=(point[0]+x_movement(angle+start_angle,len_CONST),point[1]+y_movement(angle+start_angle,len_CONST))
            test_line=Line(point,third_point,1,[0,0,0],True,True,[1,1,1])
            try_point=self.next_intersection(test_line,point,True)
            old_angle=angle_to(vertice_list[-2][0],vertice_list[-2][1],vertice_list[-1][0],vertice_list[-1][1])
            try_angle=angle_to(vertice_list[-1][0],vertice_list[-1][1],try_point[0],try_point[1])

            if -0.0001<(try_angle-old_angle)<180 or (try_angle-old_angle)<-180: 
                if self.pno_crossing(try_point,vertice_list[-1]) and self.pno_crossing(point,middle_point(vertice_list[-1],try_point)):
                    vertice_list.append(try_point)                    #we can add the try point to convex_polygon vertices
                    if -0.0001<(try_angle-old_angle)<0.0001:
                        vertice_list.pop(-2)
                    #we are on the same line, so we remove the middle point
                        #so if we turn into "convex direction" and do not cross contourlines
            angle += 10
        
        while self.pno_crossing(vertice_list[-1],vertice_list[0])==False: #there might be crossing line from last vertice to first
            vertice_list.pop(-1)


        vertice_list=vertice_reduction(vertice_list)
        return vertice_list
    
    #tries to make polygon by making convex_polygon and then enlarging its sides, but seems not to work properly
    def inflated_Polygon(self,point,contour_size,contour_color,iterations=100):
        vertice_list=self.convex_Polygon_vertices(point,0,360)
        for i in range(iterations):
            #vertice_list=self.random_vertice_inflation(vertice_list)
            vertice_list=self.simple_random_inflation_step(vertice_list)
            #vertice_list=vertice_reduction(vertice_list)
        poly=Polygon()
        poly.verticise(vertice_list,contour_size,contour_color,False,True)
        poly.intify()
        return poly

#this makes polygon "inflate". It tries to bend one side of polygon larger from a random place, it returns 
# the possibly inflated polygon
    def random_vertice_inflation(self,vertice_list):
        vertice_list=vertice_reduction(vertice_list)
        size=len(vertice_list)
        i=int(random.random()*0.9999*size)
        point1=None
        point3=None
        if i==len(vertice_list)-1:
            point1=vertice_list[-1]
            point3=vertice_list[0]
        else:
            point1=vertice_list[i]
            point3=vertice_list[i+1]
        weight=random.random()
        point2=(point1[0]*weight+point3[0]*(1-weight),point1[1]*weight+point3[1]*(1-weight)) #we build a new convex polygon around point2
        #this adds new points to the original polygon

        if self.is_in_contourline(point2)==False and pdistance(point1,point3)>2:#2 is somewhat random value
            start_angle=angle_to(point3[0],point3[1],point1[0],point1[1])
            vertice_add_list=self.convex_Polygon_vertices(point2,start_angle,180)
            vertice_list=vertice_list[0:i+1]+vertice_add_list[:]+vertice_list[i+1:]

        vertice_reduction(vertice_list)

        return vertice_list

    #this works by picking one line randomly and trying to add random triangle to it without creating intersections
    def simple_random_inflation_step(self,vertice_list):
        vertice_list=vertice_reduction(vertice_list)
        size=len(vertice_list)
        i=int(random.random()*0.9999*size)
        point1=None
        point3=None
        if i==len(vertice_list)-1:
            point1=vertice_list[-1]
            point3=vertice_list[0]
        else:
            point1=vertice_list[i]
            point3=vertice_list[i+1]
        weight=random.random()
        point2=(point1[0]*weight+point3[0]*(1-weight),point1[1]*weight+point3[1]*(1-weight)) #we build a new triangle around point2
        #this adds new points to the original polygon
        if self.is_in_contourline(point2):
            return vertice_list
        test_line=Line(point2,point1,1,[0,0,0],True,True,[1,1,1])
        corner1=self.next_intersection(test_line,point2,True) #might be point1 or not
        if pdistance(point2,corner1)>pdistance(point2,point1):
            corner1=point1 # corner1 can't be further away that point1
        test_line2=Line(point2,point3,1,[0,0,0],True,True,[1,1,1])
        corner3=self.next_intersection(test_line2,point2,True) #might be point3 or not
        if pdistance(point2,corner3)>pdistance(point2,point3):
            corner3=point3 # corner1 can't be further away that point1
        angle_1=angle_to(point2[0],point2[1],corner1[0],corner1[1])
        angle_2=angle_to(point2[0],point2[1],corner3[0],corner3[1])
        test_dir=angle_1+random.random()*180 #this is the direction in which we try to find new trianle vertice to add
        if test_dir>360:
            test_dir=test_dir-360
        long=100000
        far_point=(point2[0]+x_movement(test_dir,long),point2[1]+y_movement(test_dir,long))
        test_line=Line(point2,far_point,1,[0,0,0],True,True,[1,1,1])
        try_point=self.next_intersection(test_line,point2,True)
        cond1=self.pno_crossing(corner1,try_point)
        cond2=self.pno_crossing(point2,middle_point(corner1,try_point))
        cond3=self.pno_crossing(corner3,try_point)
        cond4=self.pno_crossing(point2,middle_point(corner3,try_point))
        if cond1 and cond2 and cond3 and cond4: #if possible add corner2, if necessary corner3 and corner2.
            if pdistance(point3,corner3)>0.00001:
                vertice_list.insert(i+1,corner3)
            corner2=try_point
            vertice_list.insert(i+1,corner2)
            if pdistance(point1,corner1)>0.00001:
                vertice_list.insert(i+1,corner1)
        return vertice_list

    def element_number(self,element_number):
        return self.elements[element_number]
    
    #gives a nice eway to present data of Polygon
    def info(self):
        info_str=""
        for i in range(len(self.elements)):
            info_str += "\n Element number "+ str(i) +": "
            if self.elements[i].__class__.__name__ == "Line":
                info_str += "Line: "+self.elements[i].represent_as_temp_str()+"\n"
            if self.elements[i].__class__.__name__ == "Polygon":
                info_str += "Polygon: "
                for j in range(len(self.elements[i].lines)):
                    info_str+=self.elements[i].lines[j].represent_as_temp_str()+"\n"
            if self.elements[i].__class__.__name__ == "Writing":
                info_str += "Writing: "+self.elements[i].represent_as_temp_str()+"\n"
        return info_str
    
    def mini_info(self):
        info_str=""
        for i in range(len(self.elements)):
            info_str += "\n Element number "+ str(i) +": "
            if self.elements[i].__class__.__name__ == "Line":
                info_str += "Line: "+str(self.elements[i].pen_down) +str(self.elements[i].end_point1)+","+str(self.elements[i].end_point2)+")\n"
            if self.elements[i].__class__.__name__ == "Polygon":
                info_str += "Polygon: ("
                for j in range(len(self.elements[i].lines)):
                    info_str+=str(self.elements[i].lines[j].pen_down)+str(self.elements[i].lines[j].end_point1)+","+str(self.elements[i].lines[j].end_point2)+")"
            if self.elements[i].__class__.__name__ == "Writing":
                info_str += "Writing: "+str(self.elements[i].location)+self.elements[i].text+"\n"
        return info_str

    #seems stupid, but lets leave it here
    def from_temp_string_to_Drawing(self,temp_str:str):
        return self(temp_str)

    def from_Drawing_to_temp_string(self):
        temp_st="£"
        self.create_starting_line() #if first element isn't line, we create an invisible line to escape some bugs
        for item in self.elements:
            if item.__class__.__name__ == "Line":
                temp_st += item.represent_as_temp_str()
            if item.__class__.__name__ == "Polygon":
                temp_st += item.represent_as_temp_str()
            if item.__class__.__name__ == "Writing":
                temp_st += item.represent_as_temp_str()
        return reduce(temp_st) #this reduces unnecessary commands in temp_str, for example "changing" pensize from 3 to 3, is unnecessary


    #if necessary creates an invisible line at the begininning
    def create_starting_line(self):
        if len(self.elements)>0:
            item=self.elements[0]
            starting_point=(0,0)
            if item.__class__.__name__ == "Polygon":
                starting_point=item.vertices()[0]
                new_line=Line((0,0),starting_point,thickness=1,pencolor=[0,0,0],pen_down=False,fc_change=True,fillcolor=[0,0,0])
                self.add_line(new_line,where="bottom")





    
    def invisible_line_removal(self):
        esize=len(self.elements)
        for i in range(1,esize):
            if self.elements[esize-1-i].__class__.__name__=="Line" and self.elements[esize-2-i].__class__.__name__=="Line": 
                if self.elements[esize-1-i].pen_down==False and self.elements[esize-2-i].pen_down==False:
                    self.elements[esize-1-i].end_point1=self.elements[esize-2-i].end_point1
                    self.remove_element_number(esize-2-i)
                    


    #we ask what is the color in that is located on the box with 'topleft' corner and given width and height
    #this area is splitted on blocks whose size is resolution*resolution
    #coordinate tells the position in these intervals coordinate (0,0) is top_left corner
    #coordinate (0,y_intervals) is bottom_left corner (x_intervals,0) is upper_right corner
    def color_in(self,topleft,width:int,height:int,resolution:float,coordinate,bg_color):
        x_intervals=width/resolution
        y_intervals=height/resolution
        absolute_position=(int(topleft[0]+width*coordinate[0]/x_intervals),int(topleft[1]-height*coordinate[1]/y_intervals))
        color=float_color_to_rgb(bg_color)
        if self.exactly_where_we_are(absolute_position).__class__.__name__=="Line":
            line=self.exactly_where_we_are(absolute_position)
            color=float_color_to_rgb([float(line.pencolor[0]),float(line.pencolor[1]),float(line.pencolor[2])])
        elif self.exactly_where_we_are(absolute_position).__class__.__name__=="Polygon":
            poly=self.exactly_where_we_are(absolute_position)
            color=float_color_to_rgb([float(poly.inside_color[0]),float(poly.inside_color[1]),float(poly.inside_color[2])])
        return color

    def simple_png(self,topleft,width:int,height:int,resolution:float,name,bg_color):
        help_img=[]
        for y in range(int(height/resolution)):
            row=()
            for x in range(int(width/resolution)):
                color = self.color_in(topleft,width,height,resolution,(x,y),bg_color)
                row = row + color
            help_img.append(row)
        with open(name+".png", 'wb') as f:
            w = png.Writer(int(len(help_img[0])/3),len(help_img),greyscale=False)
            w.write(f, help_img)
        return help_img

    #a 2d array of which png can be drawn is given to iterated_png. It draws a new png, by first enlarging
    #the png, then smoothing it, and then finding the correct color for each pixel with neighbouring pixels with different color
    def iterated_png(self,topleft,width:int,height:int,resolution:float,name:str,img,enlarging_factor:float,bg_color):
        img=enlarge_color_array2d(img,enlarging_factor)
        img=smoothen_color_array(img,1)
        img=mystify_color_array2d(img)
        resolution=height/len(img) #modification, hope it helps
        for y in range(len(img)):
            for x in range(int(len(img[0])/3)):
                if img[y][3*x]==-1 or img[y][3*x+1]==-1 or img[y][3*x+2]==-1:
                    color = self.color_in(topleft,width,height,resolution,(x,y),bg_color)
                    img[y][3*x]=color[0]
                    img[y][3*x+1]=color[1]
                    img[y][3*x+2]=color[2]
        return img




    #makes a larger png be forming a simple png and enlarging it step by step to form larger pngs
    def png_series(self,topleft,width:int,height:int,resolution:int,name:str,enlarging_factor:float,iterations:int,bg_color):
        img=self.simple_png(topleft,width,height,resolution,"simp",bg_color)
        orig_name=name
        for i in range(iterations):
            img=self.iterated_png(topleft,width,height,resolution,name,img,enlarging_factor,bg_color)
        with open("pngs\\"+name+".png", 'wb') as f:
            w = png.Writer(int(len(img[0])/3),len(img),greyscale=False)
            w.write(f, img)
        # Open an Image
        timg = Image.open("pngs\\"+name+".png")
        # Call draw Method to add 2D graphics in an image
        I1 = ImageDraw.Draw(timg)
        # Add Text to an image

        for i in range(len(self.elements)): #NOTE currently this stops working correctly if png is zoomed to something else that 1-1 ratio
            if self.elements[i].__class__.__name__ == "Writing":
                wr=self.elements[i]
                writing_loc= [wr.location[0]-topleft[0],-wr.location[1]+topleft[1]]
                color=float_color_to_rgb([float(wr.pen_color[0]),float(wr.pen_color[1]),float(wr.pen_color[2])])
                I1.text(writing_loc,wr.text,fill=color,font = ImageFont.truetype(font_to_filename(wr.font,wr.style),int(int(wr.fontsize)*1.33)), anchor="ld")
            # NOTE later change the pencolor correct by using wr.pen_color and proper transform to rgb values

        # Display edited image
        timg.show()
 
        # Save the edited image
        timg.save("pngs\\"+name+".png")

    #given a list of Polygons creates a new polygon, which is other polygons, meshed into single polygon
    #only lines that share both same endpoints can be used to mesh polygons in the list together
    #returns None when there is a problem in glued_polygon
    def merge_polygons(self,polygon_list:List[Polygon]):
        poly_list=[]
        color_array=[]
        color=[0,0,0]
        for poly in polygon_list:
            poly_list.append(poly.vertices2())
            color_array.append((float(poly.inside_color[0]),float(poly.inside_color[1]),float(poly.inside_color[2]),len(poly.vertices2())))

        color=average_color(color_array)
        poly_vertices=glued_polygon(poly_list)
        if poly_vertices==None:
            return None
        new_polygon=Polygon()
        new_polygon.inside_color=color
        contour_color=color
        new_polygon.verticise(poly_vertices,1,contour_color,False,True)
        self.add_polygon(new_polygon)
        for poly in polygon_list:
            self.remove_element(poly)
        return new_polygon
    



    #def merges all polygons that are close enough in color to the 'color'
    def merge_by_color_old(self,color:List[float],gap:List[float]):
        all_polygons=self.polygon_list()
        relevant_polygons=[]
        for polygon in all_polygons:
            copol=polygon.inside_color
            if max(abs(float(copol[0])-float(color[0])),abs(float(copol[1])-float(color[1])),abs(float(copol[2])-float(color[2])))<gap:
                relevant_polygons.append(polygon)
        self.merge_polygons(relevant_polygons)

    #def merges all polygon, which are connected to starting_polygon with tiles close enough to same color   
    def merge_by_color(self,starting_polygon,gap):
        color=starting_polygon.inside_color
        connection_dict=self.color_connection_dict(color,gap)
        relevant_polygons=self.infected_polygons(starting_polygon,connection_dict)
        self.merge_polygons(relevant_polygons)

  
    #given a dictionary of which polygons are "somehow connected" returns a descendant of starting polygon
    def infected_polygons(self,starting_polygon,connection_dict):
        return connected_objects(starting_polygon,connection_dict)
    
    #Creates and returns a connection dictionary by polygons with similar enough color and shared sides
    def color_connection_dict(self,color,color_band_width):
        result_dict={}
        for poly1 in self.polygon_list():
            result_dict[poly1]=[]
            color1=poly1.inside_color
            if color_gap(color1,color)<color_band_width:
                for poly2 in self.polygon_list():
                    color2=poly2.inside_color
                    if color_gap(color2,color)<color_band_width:
                        if self.is_there_line_connection(poly1,poly2):
                            result_dict[poly1] += [poly2]
        return result_dict

    #Tells if polygons share one side i.e. they both have two same consecutive vertices
    def is_there_line_connection(self,poly1,poly2):
        pv1=poly1.vertices()
        pv2=poly2.vertices()
        for i in range(len(pv1)-1):
            for j in range(len(pv2)-1):
                if pv1[i]==pv2[j] and pv1[i+1]==pv2[j+1]:
                    return True
                if pv1[i]==pv2[j+1] and pv1[i+1]==pv2[j]:
                    return True
        return False
    
        #Tells if polygons inside colors are close to each other
    def is_there_color_connection(self,poly1,poly2,gap):
        color1=poly1.inside_color
        color2=poly2.inside_color
        if color_gap(color1,color2)<gap:
            return True
        return False

    #set new value for the colors closer or further avay
    def change_contrast(self,strength,stable_color):
        for line in self.contour_line_list():
            line.pencolor=PngMaker.contrast_shift_transformation((float(line.pencolor[0]),float(line.pencolor[1]),float(line.pencolor[2])),strength,stable_color)
        for polygon in self.polygon_list():
            polygon.inside_color=PngMaker.contrast_shift_transformation((float(polygon.inside_color[0]),float(polygon.inside_color[1]),float(polygon.inside_color[2])),strength,stable_color)
       

    #set new value for the colors closer or further avay from average value of colors in current png
    def change_contrast_wrt_average(self,strength):
        color_multiplier_list=[]
        for line in self.contour_line_list():
            color_multiplier_list.append((float(line.pencolor[0]),float(line.pencolor[1]),float(line.pencolor[2]),1))
        for polygon in self.polygon_list():
            color_multiplier_list.append((float(polygon.inside_color[0]),float(polygon.inside_color[1]),float(polygon.inside_color[2]),len(polygon.lines)))
        stable_color=average_color(color_multiplier_list)
        self.change_contrast(strength,stable_color)

    #sets every color to shade of grey
    def blackwhite(self):
        for line in self.contour_line_list():
            average_whiteness=(float(line.pencolor[0])+float(line.pencolor[1])+float(line.pencolor[2]))/3
            line.pencolor=(average_whiteness,average_whiteness,average_whiteness)
        for polygon in self.polygon_list():
            average_whiteness=(float(polygon.inside_color[0])+float(polygon.inside_color[1])+float(polygon.inside_color[2]))/3
            polygon.inside_color=(average_whiteness,average_whiteness,average_whiteness)


    def random_drawing(self):
        for i in range(1+int(16*random.random())):
            poly=Polygon()
            poly=poly.random_polygon()
            self.add_polygon(poly)
        return self

    #how far are two colors?
def color_gap(color1,color2):
    return abs(float(color1[0])-float(color2[0]))+abs(float(color1[1])-float(color2[1]))+abs(float(color1[2])-float(color2[2]))
           
  

def font_to_filename(font,fonttype):

    if font=="Calibri":
        if fonttype=="normal":
            return "calibri"
        if fonttype=="italic":
            return "calibrii"
        if fonttype=="bold":
            return "calibrib"
    if font=="Times new roman":
        if fonttype=="normal":
            return "times"
        if fonttype=="italic":
            return "timesi"
        if fonttype=="bold":
            return "timesbd"
    if font=="Verdana":
        if fonttype=="normal":
            return "verdana"
        if fonttype=="italic":
            return "verdanai"
        if fonttype=="bold":
            return "verdanab"
    if font=="Arial":
        if fonttype=="normal":
            return "arial"
        if fonttype=="italic":
            return "ariali"
        if fonttype=="bold":
            return "arialbd"
    if font=="Franklin Gothic":
        if fonttype=="normal":
            return "framd"
        if fonttype=="italic":
            return "framdit"
        if fonttype=="bold":
            return "framd"
    if font== "Tahoma":
        if fonttype=="normal":
            return "tahoma"
        if fonttype=="italic":
            return "tahoma"
        if fonttype=="bold":
            return "tahomabd"
    if font== "Georgia":
        if fonttype=="normal":
            return "georgia"
        if fonttype=="italic":
            return "georgiai"
        if fonttype=="bold":
            return "georgiab"
    if font=="Segoe Script":
        if fonttype=="normal":
            return "segoesc"
        if fonttype=="italic":
            return "segoesc"
        if fonttype=="bold":
            return "segoescb"
    if font== "Symbol":
        if fonttype=="normal":
            return "symbol"
        if fonttype=="italic":
            return "symbol"
        if fonttype=="bold":
            return "symbol"


#two tuples are given, returns true, if they have the same coordinates
def is_same(point1,point2):
    if abs(point1[0]-point2[0])<0.00001 and  abs(point1[1]-point2[1])<0.00001:
        return True
    return False

#dict is dictionary that contains objects as keys and set of objects as values. object 2 is considered connected to object 1
 # if object2 in dict[object1]. Or object2 in dict[object3] in dict[object1] and so forth. This kind of "connection descendants
 # of starting_object are returned by function 
def connected_objects(starting_object, dict):
    old_result=[]
    result=[starting_object]
    while len(result) != len(old_result):
        old_result=result
        try_to_add_list=[]
        for robject in result:
            if robject in dict.keys():
                try_to_add_list += dict[robject]
            for tadd in try_to_add_list:
                if tadd not in result:
                    result.append(tadd)
    return result


#takes of the fc_commands (used for the Lines in some place(s))
def fc_off(temp_str):
    temp_str=temp_str.strip("|")
    array=MemoryHandler.split_the_string(temp_str,"|")
    result_str=""
    for plop in array:
        if plop[0:2]!="fc":
            result_str += plop+"|"
    return result_str

#returns true if line segments intersects (it is not enough that their continuations intersect)
def is_there_intersection(line1:Line,line2:Line):
    if has_a_slope(line1)==False and has_a_slope(line2)==False and abs(line1.end_point1_x()-line2.end_point1_x())>0.000005:
        return False #two parallel non meeting lines
    if has_a_slope(line1)==False and has_a_slope(line2)==False and abs(line1.end_point1_x()-line2.end_point1_x())<0.00001:
        if is_between_or_almost(line2.end_point1_x(),line1.end_point1_x(),line1.end_point2_x()):
            return True
        if is_between_or_almost(line2.end_point2_x(),line1.end_point1_x(),line1.end_point2_x()):
            return True
        if is_between_or_almost(line1.end_point1_x(),line2.end_point1_x(),line2.end_point2_x()):
            return True
        if is_between_or_almost(line1.end_point2_x(),line2.end_point1_x(),line2.end_point2_x()):
            return True
        return False # True if at least one endpoint of line1 is inside other line
    if (has_a_slope(line1)==False and has_a_slope(line2)==True):
        (k,a)=ykxa(line2)
        (x_cutting,y_cutting)=(line1.end_point1_x(),k*line1.end_point1_x()+a)
        condition1=is_between_or_almost(y_cutting,line1.end_point1_y(),line1.end_point2_y())
        condition2=is_between_or_almost(x_cutting,line2.end_point1_x(),line2.end_point2_x())
        if condition1 and condition2:
            return True
        return False
    if (has_a_slope(line1)==True and has_a_slope(line2)==False):   
        (k,a)=ykxa(line1)
        (x_cutting,y_cutting)=(line2.end_point1_x(),k*line2.end_point1_x()+a)
        condition1=is_between_or_almost(y_cutting,line2.end_point1_y(),line2.end_point2_y())
        condition2=is_between_or_almost(x_cutting,line1.end_point1_x(),line1.end_point2_x())
        if condition1 and condition2:
            return True
        return False

    if is_same(ykxa(line1),ykxa(line2)): #both the constant a and slope k are (almost) the same
        if is_between_or_almost(line1.end_point1_x(),line2.end_point1_x(),line2.end_point2_x()):
            return True
        if is_between_or_almost(line1.end_point2_x(),line2.end_point1_x(),line2.end_point2_x()):
            return True
        if is_between_or_almost(line2.end_point1_x(),line1.end_point1_x(),line1.end_point2_x()):
            return True
        if is_between_or_almost(line2.end_point2_x(),line1.end_point1_x(),line1.end_point2_x()):
            return True
        return False
    #if we go to here we have two ines with finite slopes that intersect in one point if continues
    intersections=line_intersections(line1,line2)
    for intersection in intersections:
        condition1=is_between_or_almost(intersection[0],line1.end_point1_x(),line1.end_point2_x())
        condition2=is_between_or_almost(intersection[0],line2.end_point1_x(),line2.end_point2_x())
        if condition1 and condition2: # if intersection x-coordinate is on both line x-coordinates it must be on both lines 
            return True #if the x-coordinate of intersection is between lines end points x-coordinates, the it is in the line(segment)
    return False
    
#returns true if line segments defined by their endpoints intersects (it is not enough that their continuations intersect)
 #point11 and point12 are the endpoints of the first line
def pis_there_intersection(point11,point12,point21,point22):
    if phas_a_slope(point11,point12)==False and phas_a_slope(point21,point22)==False and abs(point11[0]-point21[0])>0.000005:
        return False #two parallel non meeting lines
    if phas_a_slope(point11,point12)==False and phas_a_slope(point21,point22)==False and abs(point11[0]-point21[0])<0.00001:
        if is_between_or_almost(point21[0],point11[0],point12[0]):
            return True
        if is_between_or_almost(point22[0],point11[0],point12[0]):
            return True
        if is_between_or_almost(point11[0],point21[0],point22[0]):
            return True
        if is_between_or_almost(point12[0],point21[0],point22[0]):
            return True
        return False # True if at least one endpoint of line1 is inside other line
    if (phas_a_slope(point11,point12)==False and phas_a_slope(point21,point22)==True):
        (k,a)=pykxa(point21,point22)#need to define ykxa to points NOTE
        (x_cutting,y_cutting)=(point11[0],k*point11[0]+a)
        condition1=is_between_or_almost(y_cutting,point11[1],point12[1])
        condition2=is_between_or_almost(x_cutting,point21[0],point22[0])
        if condition1 and condition2:
            return True
        return False
    if (phas_a_slope(point11,point12)==True and phas_a_slope(point21,point22)==False):   
        (k,a)=pykxa(point11,point12)
        (x_cutting,y_cutting)=(point21[0],k*point21[0]+a)
        condition1=is_between_or_almost(y_cutting,point21[1],point22[1])
        condition2=is_between_or_almost(x_cutting,point11[0],point12[0])
        if condition1 and condition2:
            return True
        return False

    if is_same(pykxa(point11,point12),pykxa(point21,point22)): #both the constant a and slope k are (almost) the same
        if is_between_or_almost(point11[0],point21[0],point22[0]):
            return True
        if is_between_or_almost(point12[0],point21[0],point22[0]):
            return True
        if is_between_or_almost(point21[0],point11[0],point12[0]):
            return True
        if is_between_or_almost(point22[0],point11[0],point12[0]):
            return True
        return False
    #if we go to here we have two ines with finite slopes that intersect in one point if continues
    intersections=pline_intersections(point11,point12,point21,point22)
    for intersection in intersections:
        condition1=is_between_or_almost(intersection[0],point11[0],point12[0])
        condition2=is_between_or_almost(intersection[0],point21[0],point22[0])
        if condition1 and condition2: # if intersection x-coordinate is on both line x-coordinates it must be on both lines 
            return True #if the x-coordinate of intersection is between lines end points x-coordinates, the it is in the line(segment)
    return False




#this returns a list of points which is the original list with duplicates removed and points listed in the order of their x-coordinate
def points_ordered_by_x(list_of_points):
            # Using sort + key
    new_ordering_parameter=[]
    for i in range(0,len(list_of_points)):
        new_ordering_parameter.append(list_of_points[i][0])

    new_ordering_parameter.sort(key = float)
    order=[]#tähän listataan indeksit järjestykseen, niin, että ensiksi tulee sen indeksin arvo,
    #jonka ordering_parameter on pienin
    size=len(list_of_points)
    for i in range(0,size):
        for j in range(0,size):
            if list_of_points[j][0]==new_ordering_parameter[i] and j not in order:
                order.append(j)
    result=[list_of_points[order[0]]]
    for i in range(1,size):
        if list_of_points[order[i]][0] != list_of_points[order[i-1]][0]:
            result.append(list_of_points[order[i]])
    return result

#this returns a list of points which is the original list with duplicates removed and points listed in the order of their x-coordinate
def points_ordered_by_y(list_of_points):
            # Using sort + key
    new_ordering_parameter=[]
    for i in range(0,len(list_of_points)):
        new_ordering_parameter.append(list_of_points[i][1])

    new_ordering_parameter.sort(key = float)
    order=[]#tähän listataan indeksit järjestykseen, niin, että ensiksi tulee sen indeksin arvo,
    #jonka ordering_parameter on pienin
    size=len(list_of_points)
    for i in range(0,size):
        for j in range(0,size):
            if list_of_points[j][1]==new_ordering_parameter[i] and j not in order:
                order.append(j)
    result=[list_of_points[order[0]]]
    for i in range(1,size):
        if list_of_points[order[i]][1] != list_of_points[order[i-1]][1]:
            result.append(list_of_points[order[i]])
    return result


#return True is a is between b and c
def is_between(a:float,b:float,c:float):
    if (b<=a and a<=c) or (c<=a and a<=b):
        return True
    return False

#return True is a is between b and c or very close to being in between them (used for roundinf reasons)
def is_between_or_almost(a:float,b:float,c:float):
    if (b-0.00001<=a and a<=c+0.00001) or (c-0.00001<=a and a<=b+0.00001):
        return True
    return False


#This will be true if line1 and line2 are parallel (or almost parallel) (Same direction or 180 angle), they can overlap or not   
def is_parallel(line1:Line,line2:Line):
    first_angle=angle_to(line1.end_point1_x(),line1.end_point1_y(),line1.end_point2_x(),line1.end_point2_y())
    second_angle=angle_to(line2.end_point1_x(),line2.end_point1_y(),line2.end_point2_x(),line2.end_point2_y())
    if abs(first_angle-second_angle)<0.00001:
        return True #if lines go in the same direction
    if abs(first_angle-second_angle)<180.00001 and abs(first_angle-second_angle)>179.99999:
        return True #if lines go to opposite directions
    return False

#if lines with these endpoints are parallel returns True. They can overlap or not
def pis_parallel(point11,point12,point21,point22):
    first_angle=angle_to(line1.end_point1_x(),line1.end_point1_y(),line1.end_point2_x(),line1.end_point2_y())
    second_angle=angle_to(line2.end_point1_x(),line2.end_point1_y(),line2.end_point2_x(),line2.end_point2_y())
    if abs(first_angle-second_angle)<0.00001:
        return True #if lines go in the same direction
    if abs(first_angle-second_angle)<180.00001 and abs(first_angle-second_angle)>179.99999:
        return True #if lines go to opposite directions    
    return False

def has_a_slope(line1:Line):
    return phas_a_slope(line1.end_point1,line1.end_point2)

#i.e. line with these endpoints is not vertical
def phas_a_slope(point1,point2):
    if abs(point1[0]-point2[0])<0.00001:
        return False
    else:
        return True

#tells the distance of point from line1, where line1 is continued from its endingpoints
def distance_from_extended_line(line1:Line,point):
    if abs(line1.end_point1_x()-line1.end_point2_x())<0.00001:
        return abs(point[0]-line1.end_point1_x())
    (k,a)=ykxa(line1)
    y_dis=abs(point[1]-k*point[0]-a)
    return y_dis/math.sqrt(1+k*k)

#this is an angle of corner located at point2 and sides going through point 1 and point 3
#Angle is calculated to clock or anticlockwise direction depending which gives smaller result (which is between 0 and 179)
def smaller_angle(point1,point2,point3):
    first_heading=angle_to(point2[0],point2[1],point1[0],point1[1])
    second_heading=angle_to(point2[0],point2[1],point3[0],point3[1])
    gon1=(first_heading-second_heading)%360
    gon2=(-first_heading+second_heading)%360
    if gon1<gon2:
        return gon1
    return gon2

#returns the smallest angle of triangle in degrees
def smallest_triangle_angle(point1,point2,point3):
    result=60
    if smaller_angle(point1,point2,point3)<result:
        result=smaller_angle(point1,point2,point3)
    if smaller_angle(point2,point3,point1)<result:
        result=smaller_angle(point2,point3,point1)
    if smaller_angle(point3,point1,point2)<result:
        result=smaller_angle(point3,point1,point2)
    return result

#Returns the angles of triangle
def triangle_angles(point1,point2,point3):
    return (smaller_angle(point1,point2,point3),smaller_angle(point2,point3,point1),smaller_angle(point3,point1,point2))

#tells the type of triangle (by largest angle)
def triangle_type(point1,point2,point3):
    largest_angle=60
    all_angles=triangle_angles(point1,point2,point3)
    for i in range(0,3):
        if all_angles[i]>largest_angle:
            largest_angle=all_angles[i]
    if largest_angle==90:
        return "right"
    if largest_angle>90:
        return "obtuse"
    return "acute"

#returns a point that is on the closest point
def nearest_point_on_line(line1:Line,point):
    closest_point=line1.end_point1
    #after next, closest point is (temporarily) the closest endpoint of line
    if distance(closest_point[0],closest_point[1],point[0],point[1])>distance(line1.end_point2[0],line1.end_point2[1],point[0],point[1]):
        closest_point=line1.end_point2

    #next we find if we can find even closer point by projection
    closeness_type=None
    if smaller_angle(point,line1.end_point1,line1.end_point2)>=91 or smaller_angle(point,line1.end_point2,line1.end_point1)>=91:
        closeness_type="endpoint"
    else:
        closeness_type="projection" #closest point is find by projection

    if closeness_type=="projection":
        closest_cand=None #this is a candidate of being closest point
        if has_a_slope(line1):
            (k1,a1)=ykxa(line1)
            if k1!=0:
                closest_point_x= (k1*point[1]+point[0]-a1*k1)/(k1*k1+1)
                closest_point_y= (k1*k1*point[1]+k1*point[0]+a1)/(k1*k1+1)
                closest_cand=(closest_point_x,closest_point_y)
            if k1==0:
                closest_cand=(point[0],line1.end_point1_y())
        if has_a_slope(line1)==False:
            closest_cand=(line1.end_point1_x(),point[1])
        test_dist1=distance(closest_cand[0],closest_cand[1],line1.end_point1_x(),line1.end_point1_y())
        test_dist2=distance(closest_cand[0],closest_cand[1],line1.end_point2_x(),line1.end_point2_y())
        line_length=line1.lenght()
        if test_dist1<line_length and test_dist2<line_length:
            closest_point=closest_cand 

    return closest_point


#given a vertice list of several polygons a new polygon is formed by glueing those polygons
#polygon
def polygon_list_points(poly_vertice_list_list):
    dictionary_of_points={}
    for poly_vertices in poly_vertice_list_list:
        for i in range(len(poly_vertices)):
            x1=poly_vertices[i][0]
            y1=poly_vertices[i][1]
            if (x1,y1) not in dictionary_of_points:
                dictionary_of_points[(x1,y1)]=1
            else:
                dictionary_of_points[(x1,y1)]=dictionary_of_points[(x1,y1)]+1
    return dictionary_of_points

#given a vertice list of several polygons a returns a dictionary which tells how many times a certain line is in the polygon
def polygon_list_lines(poly_vertice_list_list):
    dictionary_of_lines={}
    for poly_vertices in poly_vertice_list_list:
        for i in range(len(poly_vertices)):
            x1=poly_vertices[i][0]
            y1=poly_vertices[i][1]
            x2=poly_vertices[i-1][0]
            y2=poly_vertices[i-1][1]
            p1=(x1,y1) #in dictionary we have have system that recognices that point1,point2 and point2,point1 are same line
            p2=(x2,y2)
            if x1>x2 or (x1==x2 and y1>y2):
                p1=(x2,y2)
                p2=(x1,y1)
            if (p1,p2) not in dictionary_of_lines:
                dictionary_of_lines[(p1,p2)]=1
            else:
                dictionary_of_lines[(p1,p2)]=dictionary_of_lines[(p1,p2)]+1
    return dictionary_of_lines

#list points that are vertices in polygons exactly two times NOTE might be useless 
def polygon_list_double_points(poly_vertice_list_list):
    double_point_list=[]
    dictionary_of_points=polygon_list_points(poly_vertice_list_list)
    for key in dictionary_of_points.keys():
        if dictionary_of_points[key]==2:
            double_point_list.append(key)
    return double_point_list

#list points that are vertices in polygons exactly two times NOTE might be useless 
def polygon_list_single_lines(poly_vertice_list_list):
    single_line_list=[]
    dictionary_of_lines=polygon_list_lines(poly_vertice_list_list)
    for key in dictionary_of_lines.keys():
        if dictionary_of_lines[key]==1:
            single_line_list.append(key)
    return single_line_list

#line_list is of the form [((a,b),(c,d)),((e,f),(g,h)),...]
# it is changed to {(a,b):(c,d),(e,f):(g,h)}
def line_list_to_line_dict(line_list): #NOTE if there are two lines starting from same point, only one is given
    dict={}
    for line in line_list:
        if line[0] not in dict.keys():
            dict[line[0]]=[line[1]]
        else:
            dict[line[0]]=dict[line[0]]+[line[1]]
        if line[1] not in dict.keys():
            dict[line[1]]=[line[0]]
        else:
            dict[line[1]]=dict[line[1]]+[line[0]]
    return dict



#def glues polygons given their vertice_list to new polygon
def glued_polygon(poly_vertice_list_list):
    line_dict=line_list_to_line_dict(polygon_list_single_lines(poly_vertice_list_list))
    polygon=[]
    current_point=next(iter(line_dict))
    polygon.append(current_point)
    current_point=line_dict[current_point][0]
    while current_point not in polygon:
        if current_point != None:
            polygon.append(current_point)
        pot_points=line_dict[current_point]
        for point in pot_points:
            if point != polygon[-2] and point != polygon[-1]:
                current_point=point
    if len(polygon)!=len(line_dict):
        return None
    else:
        return polygon


#this tells the distance from line_segment (whichcan be larger than distance from extended line)
def distance_from_line_segment(line1:Line,point):
    point1=line1.end_point1
    point2=line1.end_point2
    point3=point
    tri_type=triangle_type(point1,point2,point3)
    if smaller_angle(point1,point2,point3)<90 and smaller_angle(point2,point1,point3)<90:
        return distance_from_extended_line(line1,point)
    dist1=distance(point1[0],point1[1],point3[0],point3[1])
    dist2=distance(point3[0],point3[1],point2[0],point2[1])
    if dist1<dist2:
        return dist1
    return dist2

#this tells the distance from 'point' to linesegment connecting points 'point1' and 'point2'
def pdistance_from_line_segment(point1,point2,point): #NOTE not tested yet
    tri_type=triangle_type(point1,point2,point)
    
    if smaller_angle(point1,point2,point)<90 and smaller_angle(point2,point1,point)<90:
        if pdistance(point1,point2)<0.00001: #i.e. if point1 and point2 are basicly the same point
            return pdistance(point1,point)
        if point1[0] != point2[0]:
            (k,a)=pykxa(point1,point2)
            y_dis=abs(point[1]-k*point[0]-a)
            return y_dis/math.sqrt(1+k*k)
        if point1[0] == point2[0]:#trust me, this is correct
            return abs(point1[0]-point[0])

    dist1=distance(point1[0],point1[1],point[0],point[1])
    dist2=distance(point[0],point[1],point2[0],point2[1])
    if dist1<dist2:
        return dist1
    return dist2

    
#this returns the parameters (k,a) of equation y=kx+a related to the line with
def ykxa(line:Line): 
    return pykxa(line.end_point1,line.end_point2) 

#this returns the parameters (k,a) of equation y=kx+a related to the line with
def pykxa(point1,point2):
    if abs(point1[0]-point2[0])<0.000000001 and abs(point1[1]-point2[1])>0.00001:
        raise ValueError("Kulmakerrointa ei ole olemasa")
    deltax=point2[0]-point1[0]      
    deltay=point2[1]-point1[1]
    k=deltay/deltax #make sure this can give float values not just intsw
    a=point1[1]-k*point1[0]  
    return (k,a) 


#returns a list of points where to lines intersect. Note that intersection might be outside of the line end points 
#if lines are on the same extended line, the end points of line1 and line 2 are returned
#in this method lines have to be the same or almost the same
def line_intersections(line1:Line,line2:Line):
    intersections=[]
    if has_a_slope(line1) and has_a_slope(line2):
        (k1,a1)=ykxa(line1)
        (k2,a2)=ykxa(line2)
        if abs(k1-k2)>0.00001:
            x=(a2-a1)/(k1-k2)
            y=k1*(a2-a1)/(k1-k2)+a1
            intersections.append((x,y))
        if is_same((k1,a1),(k2,a2)): #equations for the extended line are same or almost the same NOTE changed 27.8
            if is_between_or_almost(line1.end_point1_x(),line2.end_point1_x(),line2.end_point2_x()): #these if statements are new
                intersections.append(line1.end_point1)
            if is_between_or_almost(line1.end_point2_x(),line2.end_point1_x(),line2.end_point2_x()):
                intersections.append(line1.end_point2)
            if is_between_or_almost(line2.end_point1_x(),line1.end_point1_x(),line1.end_point2_x()):
                intersections.append(line2.end_point1)
            if is_between_or_almost(line2.end_point2_x(),line1.end_point1_x(),line1.end_point2_x()):
                intersections.append(line2.end_point2)
        
    if has_a_slope(line1) and has_a_slope(line2)==False:
        (k1,a1)=ykxa(line1)
        intersections.append((line2.end_point1_x(),k1*line2.end_point1_x()+a1))
    
    if has_a_slope(line2) and has_a_slope(line1)==False:
        (k2,a2)=ykxa(line2)
        intersections.append((line1.end_point1_x(),k2*line1.end_point1_x()+a2))

    if has_a_slope(line2)==False and has_a_slope(line1)==False:
        if abs(line1.end_point1_x()-line2.end_point2_x())<INTERSECTION_CONSTANT:
            if is_between_or_almost(line1.end_point1_y(),line2.end_point1_y(),line2.end_point2_y()):#these second if statements
                intersections.append(line1.end_point1)
            if is_between_or_almost(line1.end_point2_y(),line2.end_point1_y(),line2.end_point2_y()):#were added in 5.8.
                intersections.append(line1.end_point2)
            if is_between_or_almost(line2.end_point1_y(),line1.end_point1_y(),line1.end_point2_y()):
                intersections.append(line2.end_point1)
            if is_between_or_almost(line2.end_point2_y(),line1.end_point1_y(),line1.end_point2_y()):
                intersections.append(line2.end_point2)

    return intersections #return 1 point if line intersect each other and four points (line endpoints) if they are on the same extended line

#returns a list of points where two lines intersect. Note that intersection might be outside of the line end points 
#if lines are on the same extended line, points on both lines are returned
#in this method lines have to be the same or almost the same
def pline_intersections(point11,point12,point21,point22):
    intersections=[]
    if phas_a_slope(point11,point12) and phas_a_slope(point21,point22):
        (k1,a1)=pykxa(point11,point12)
        (k2,a2)=pykxa(point21,point22)
        if abs(k1-k2)>0.00001:
            x=(a2-a1)/(k1-k2)
            y=k1*(a2-a1)/(k1-k2)+a1
            intersections.append((x,y))
        if is_same((k1,a1),(k2,a2)): #equations for the extended line are same or almost the same
            if is_between_or_almost(point11[0],point21[0],point22[0]):
                intersections.append(point11)
            if is_between_or_almost(point12[0],point21[0],point22[0]):
                intersections.append(point12)
            if is_between_or_almost(point21[0],point11[0],point12[0]):
                intersections.append(point21)
            if is_between_or_almost(point22[0],point11[0],point12[0]):
                intersections.append(point22)
        
    if phas_a_slope(point11,point12) and phas_a_slope(point21,point22)==False:
        (k1,a1)=pykxa(point11,point12)
        intersections.append((point21[0],k1*point21[0]+a1))
    
    if phas_a_slope(point21,point22) and phas_a_slope(point11,point12)==False:
        (k2,a2)=pykxa(point21,point22)
        intersections.append((point11[0],k2*point11[0]+a2))

    if phas_a_slope(point21,point22)==False and phas_a_slope(point11,point12)==False:
        if abs(point11[0]-point22[0])<INTERSECTION_CONSTANT:
            if is_between_or_almost(point11[1],point21[1],point22[1]):#these second if statements
                intersections.append(point11)
            if is_between_or_almost(point12[1],point21[1],point22[1]):#were added in 5.8.
                intersections.append(point12)
            if is_between_or_almost(point21[1],point11[1],point12[1]):
                intersections.append(point21)
            if is_between_or_almost(point22[1],point11[1],point12[1]):
                intersections.append(point22)

    return intersections #return 1 point if line intersect each other and four points (line endpoints) if they are on the same extended line



#this returns two points which are in the symmetry line which goes through the point2 with "equal angles made with respect to point1 and 3"
def symmetry_points(point1,point2,point3,lenght:float):
    heading1=angle_to(point2[0],point2[1],point1[0],point1[1])
    heading2=angle_to(point2[0],point2[1],point3[0],point3[1])
    average_angle=(heading1+heading2)/2 #there used to read int(), renmoved 27.8
    shift_x=x_movement(average_angle,lenght)
    shift_y=y_movement(average_angle,lenght)
    result_point1=(point2[0]+shift_x,point2[1]+shift_y)
    result_point2=(point2[0]-shift_x,point2[1]-shift_y)
    return (result_point1,result_point2)


def polygonize(polylines:List[Line],fillcolor,writings:List[str]):
    poly=Polygon()
    poly.lines=polylines
    poly.inside_color=fillcolor
    poly.writings=writings
    return poly


#returns a verticelist corresponding a polygon which is little smaller than polygon described by vertice_list in the argument.
#  Works only for closed polygons?
def shrinked_vertice_list(vertice_list,shrink_amount=SHRINK_CONSTANT):
    updated_vertices=[]
    test_points=symmetry_points(vertice_list[-1],vertice_list[0],vertice_list[1],0.1)#test point is chosen very close to vertice
    candidates=symmetry_points(vertice_list[-1],vertice_list[0],vertice_list[1],shrink_amount)#while actual vertice might be further away
    if is_inside_vertice_list_span(vertice_list,test_points[0]):
 #first vertice shift
        updated_vertices.append(candidates[0])
    else:
        updated_vertices.append(candidates[1])

    for i in range(1,len(vertice_list)-1): #middle vertices shift
        test_points=symmetry_points(vertice_list[i-1],vertice_list[i],vertice_list[i+1],0.1)
        candidates=symmetry_points(vertice_list[i-1],vertice_list[i],vertice_list[i+1],shrink_amount)
        if is_inside_vertice_list_span(vertice_list,test_points[0]):
            updated_vertices.append(candidates[0])
        else:
            updated_vertices.append(candidates[1])

    test_points=symmetry_points(vertice_list[-2],vertice_list[-1],vertice_list[0],0.1)
    candidates=symmetry_points(vertice_list[-2],vertice_list[-1],vertice_list[0],shrink_amount)
    if is_inside_vertice_list_span(vertice_list,test_points[0]): #last vertice shift
        updated_vertices.append(candidates[0])
    else:
        updated_vertices.append(candidates[1])
    return updated_vertices




#tells if given point is inside polygon spanned by vertices on vertice_list
def is_inside_vertice_list_span(vertice_list,point):
    point1=point
    point2=(point[0]+20000,point[1]+427)#20000 and 427 are random numbers
    counter=0
    size=len(vertice_list)
    for i in range(size-1):
        if pis_there_intersection(point1,point2,vertice_list[i],vertice_list[i+1]):
            counter +=1
    if pis_there_intersection(point1,point2,vertice_list[size-1],vertice_list[0]):
        counter +=1
    if counter%2==0:
        return False
    return True


#listy is type [(0.23,0.11,078,1.5),(0.73,0.0,022,2.7)...] So it lists a color and its weight in tone tuple (r,g,b,w)
def average_color(color_multiplier_list):
    numerator=0
    red=0
    green=0
    blue=0
    for item in color_multiplier_list:
        red += item[3]*item[0]
        green +=item[3]*item[1]
        blue += item[3]*item[2]
        numerator += item[3]
    if numerator==0:#dodge zero division error
        numerator=1
    return (red/numerator,green/numerator,blue/numerator)


#HUOM ELI SIIS MUOKKAA RANDOM LISÄYSTÄ SILLEEN, ETTÄ SE SAA SYÖKSYÄ KOHTI OMAA VERTICE LISTAA VÄHÄN SATUNNAISEEN SUUNTAAN
#JA LASKEE SITTEN MIHIN TÖRMÄÄ SIINÄ
#returns point which is the next intersection from direction point1->point2. intersection in point1 does not count
#f a line between point point1 and point2 and lines spanned by vertice_list
def next_vertice_list_intersection(point1,point2,vertice_list):
    pot_inters=[]
    size=len(vertice_list)
    for i in range(size-1):
        if pis_there_intersection(point1,point2,vertice_list[i],vertice_list[i+1]):
            pot_inters += pline_intersections(point1,point2,vertice_list[i],vertice_list[i+1])
        if pis_there_intersection(point1,point2,vertice_list[size-1],vertice_list[0]):
            pot_inters += pline_intersections(point1,point2,vertice_list[size-1],vertice_list[0])
    result=None
    min_dist=1000000
    for pot_point in pot_inters:
        if 0.0001<pdistance(point1,pot_point)<min_dist:
            result=pot_point
            min_dist=pdistance(point1,pot_point)
    return result

#give a color in [a,b,c] form where 0<a,b,c<1, return a tuple  (r,g,b) with values between 0 and 255
def float_color_to_rgb(color:List[float]):
    return (int(255.9999*color[0]),int(255.9999*color[1]),int(255.9999*color[2]))

#AKGORITMIN TARKOITUS ON KATSOA HARVAKSEEN OLEVIA PISTEITÄ. JOS VIEREKKÄISISSÄ ON SAMOJA, NIIN TOD NÄK
#KAIKISSA LÄHUPISTEISSÄON SAMAT ARVOT, JOTEN NIITÄ EI OLE TARVE ERIKSEEN ENÄÄ TESTATA.
def boring_values(array2d):
    result_array=[]
    xsize=len(array2d)
    ysize=len(array2d[0])
    for x in range(0,xsize):
        row=ysize*[None]
        result_array.append(row)
    for x in range(1,xsize-1):
        ysize=len(result_array[x])
        result_array[x][0]=None
        result_array[x][ysize-1]=None
        for y in range(1,ysize-1):
            result_array[x][y]=array2d[x][y]
            if (array2d[x][y]!=array2d[x-1][y]) or  (array2d[x][y]!=array2d[x+1][y]) or (array2d[x][y]!=array2d[x][y-1]):
                result_array[x][y]=None
            if array2d[x][y]!=array2d[x-1][y-1] or  (array2d[x][y]!=array2d[x+1][y-1]) or (array2d[x][y]!=array2d[x][y+1]):
                result_array[x][y]=None
            if (array2d[x][y]!=array2d[x-1][y+1]) or  (array2d[x][y]!=array2d[x+1][y+1]):
                result_array[x][y]=None
    return result_array

#Returns an array thast has sides 'times' times longer than in the parameter, cell values are chosen in such way
# that this can be used to produce png-file with single pixels enlarged to larger blobs
def enlarge_color_array2d(color_array2d,times:float):
    new_array=[]
    xsize=len(color_array2d)
    ysize=len(color_array2d[0])
    for x in range(0,int(xsize*times)):
        row=(int(ysize*times))*[None]
        new_array.append(row)
    for x in range(int(xsize*times)):
        new_array[x]= triplet_array_enlargement(color_array2d[int(x/times)],times)
    return new_array

#takes a 'color_array2d' and makes new array 'mystified_array' of same size. mystified_array is the same as color_array2d, 
# except if there are two pixels close to each other with different colors, then the pixel in question is turned into -1,-1,-1
#(this -1,-1,-1 is just dummy-constant, which is later handled in other methods)
def mystify_color_array2d(color_array2d):
    xsize=len(color_array2d)
    ysize=len(color_array2d[0])
    mystified_color_array2d=minus_mn_array(xsize,ysize)
    for x in range(1,xsize-1):
        for y in range(3,ysize-6):
            orig=color_array2d[x][y:y+3]
            other_trip1=color_array2d[x-1][y-3:y]
            other_trip2=color_array2d[x-1][y:y+3]
            other_trip3=color_array2d[x-1][y+3:y+6]
            other_trip4=color_array2d[x][y-3:y]
            other_trip6=color_array2d[x][y+3:y+6]
            other_trip7=color_array2d[x+1][y-3:y]
            other_trip8=color_array2d[x+1][y:y+3]
            other_trip9=color_array2d[x+1][y+3:y+6]
            ots=[other_trip1,other_trip2,other_trip3,other_trip4,other_trip6,other_trip7,other_trip8,other_trip9]
            if orig==ots[0]==ots[1]==ots[2]==ots[3]==ots[4]==ots[5]==ots[6]==ots[7]:
                mystified_color_array2d[x][y]=color_array2d[x][y]
                mystified_color_array2d[x][y+1]=color_array2d[x][y+1]
                mystified_color_array2d[x][y+2]=color_array2d[x][y+2]
    return mystified_color_array2d

#takes array which length is divisible by three. Enlarges it by times, so that first triplet of array is first 
# repeated 'times' times that second triplet etc.
# for example [a,b,c,d,e,f] -> [a,b,c,a,b,c,a,b,c,d,e,f,d,e,f,d,e,f] if 'times' is 3 
def triplet_array_enlargement(array,times:int):
    new_array=[]
    for i in range(int(len(array)*times/3)):
        plop=array[3*int(i/times):3*int(i/times)+3]
        new_array += plop
    return new_array

#takes a color array and smoothens its contours by taking average values from neighbor-pixels
def smoothen_color_array(color_array2d,smooth_const:int):
    new_array=color_array2d
    for i in range(smooth_const):
        new_array=smooth_step(new_array)
    return new_array

#one step of smoothing color_variations
def smooth_step(color_array2d):
    xsize=len(color_array2d)
    ysize=len(color_array2d[0])
    new_array=empty_mn_array(xsize,ysize)
    for x in range(0,xsize):
        for y in range(ysize):
            if x>=1 and x<xsize-1 and y>=3 and y<ysize-3:
                new_array[x][y]=int((10*color_array2d[x][y]+color_array2d[x][y-3]+color_array2d[x][y+3]+color_array2d[x+1][y]+color_array2d[x-1][y])/14)
            else:
                new_array[x][y]=color_array2d[x][y]
    return new_array
            
#returns an empty array of dimension m x n
def empty_mn_array(m:int,n:int):
    result=[]
    for i in range(m):
        result.append([None]*n)
    return result

#returns an array of dimension m x n with all cells containing number -1
def minus_mn_array(m:int,n:int):
    result=[]
    for i in range(m):
        result.append([-1]*n)
    return result

#takes a vertice_list and adds a new vertice 'point' between vertice_list[vertice_nro] and vertice_list[vertice_nro+1]
#note that after this there are one more vertice in vertice list
def vertice_bend(vertice_list,vertice_nro,point):
    vertice_list.insert(vertice_nro,point)
    return vertice_list


#given a list of points, vertice reduction takes a way "palindromes" so if we go to one direction and return back to the same direction
#with exactly opposite steps, these steps are moved from the array
def vertice_reduction(points_array):
    size1=len(points_array)
    points_array=vertice_reduction_step(points_array)
    size2=len(points_array)
    while size2<size1:
        size1=len(points_array)
        points_array=vertice_reduction_step(points_array)
        size2=len(points_array)
        if size2<=2:
            return []
    points_array=middle_vertice_removal(points_array) #takes away vertices that are in the middle of line between vertices next to it
    return points_array

#returns true if two list of vertices are the same, different starting_vertice and different direction are allowed
#forexample [p1,p2,p3,p4] is same as [p3,p2,p1,p4], but [p1,p3,p2,p4] aren't since after p1 there should be p2 or p4.
#also [p1,p2,p2,p3,p4] is not same as [p1,p2,p3,p4] due to the repetition
#basicly the point is, do these verticelist span the same polygon
def are_same_vertices(vertice_list1,vertice_list2):
    if len(vertice_list1) != len(vertice_list2):
        return False
    starting_index=0
    size=len(vertice_list1)
    for i in range(size):
        if vertice_list1[i:size]==vertice_list2[0:size-i] and vertice_list1[0:i]==vertice_list2[size-i:size]:
            return True
        
    vertice_list2.reverse()
    for i in range(size):
        if vertice_list1[i:size]==vertice_list2[0:size-i] and vertice_list1[0:i]==vertice_list2[size-i:size]:
            return True
    return False

#takes a way "palindrome points"
def vertice_reduction_step(points_array):
    size=len(points_array)
    if is_same(points_array[0],points_array[size-1]):
        return points_array[:-1]
    if is_same(points_array[1],points_array[size-1]):
        return points_array[1:] #in this case actually the opening point is unnecessary

    looking_at=size-1
    while looking_at>1:
        if is_same(points_array[looking_at],points_array[looking_at-1]): #pi->p1
            points_array.pop(looking_at) #two same points following each other, ->last one is useless
        elif is_same(points_array[looking_at],points_array[looking_at-2]):#p1->p2->p1 going two p2 but returning, only first p1 is necessary
            points_array.pop(looking_at)
            points_array.pop(looking_at-1)
            looking_at=looking_at-1
        looking_at=looking_at-1
    return points_array

#returns the point in the middle of two points
def middle_point(point1,point2):
    return ((point1[0]+point2[0])/2,(point1[1]+point2[1])/2)

#takes away vertices that are in the middle of line between vertices next to it
def middle_vertice_removal(points_array):
    size=len(points_array)
    for i in range(1,size-1):
        angle1=angle_to(points_array[size-i][0],points_array[size-i][1],points_array[size-i-1][0],points_array[size-i-1][1])
        angle2=angle_to(points_array[size-i-1][0],points_array[size-i-1][1],points_array[size-i-2][0],points_array[size-i-2][1])
        if points_array[size-i-1]==points_array[size-i-2] or abs(angle1-angle2)<0.001 or abs(angle1-angle2)>359.999: #0.001 is somewhat random small value
            points_array.pop(size-i-1) #goodbye to unnecessary middle vertice
    return points_array
        
    


#takes away unnecessary commands from the temp_str
#NOTE in 27.1. we changed from Commands.nth... to Function=perator stuff
def reducestep(temp_str:str):
    reduced_str=""
    in_polygon=False #tells if current string are added in the polygon or just as a line
    c_pen_color="[-1,-1,-1]" #c here is for 'current'. These are the values currently in operation 
    c_fill_color="[-1,-1,-1]" #impossible values are choosen on purpose
    c_thickness=-1 #i.e. pensize
    c_location=(-12443160,-13466430)
    c_pen_down=None
    c_current_heading=370
    temp_str=temp_str.strip("£")
    array=MemoryHandler.split_the_string(temp_str,"|")
    if len(array)>0:
        if array[-1]=="":#if we don't remove a possible empty command in the end, we get a ayntax error while asking type_of()
            array=array[:-1]
    for order in array:
        arguments=[]
        if FunctionOperator.type_of(order)=="function_with_arguments":
            arguments=FunctionOperator.arguments_of(order)
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

        if order[0:2]=="fc":
            red=arguments[0][1:] #it is not clear whether we should have this [1:] or not? Prpose was to take [ out with Commands.nth_
            green=arguments[1]
            blue=arguments[2][:-1]
            if [red,green,blue]!=c_fill_color:
                reduced_str += order+"|"
                c_fill_color=[red,green,blue]
        if order[0:2]=="co":
            red=arguments[0][1:] #same here
            green=arguments[1]
            blue=arguments[2][:-1]
            if [red,green,blue]!=c_pen_color:
                reduced_str += order+"|"
                c_pen_color=[red,green,blue]
        if order=="bf()":
            if in_polygon == False:
                reduced_str += order+"|"
            in_polygon =True
        if order=="ef()":
            if in_polygon == True:
                reduced_str += order+"|"
            in_polygon =False
        if order[0:4]=="goto":
            if int_arguments[0]!=c_location[0] or int_arguments[1]!=c_location[1]:
                [new_x,new_y]=[int_arguments[0],int_arguments[1]]
                reduced_str += order+"|"
                c_location=(new_x,new_y)
        if order=="pu()":
            if c_pen_down != False:
                if reduced_str[-5:] in ["pu()|","pd()|"]:#this is done to take away unnecessary up/down changes
                    reduced_str=reduced_str[0:-5]
                reduced_str += order+"|"
                c_pen_down =False
        if order=="pd()":
            if c_pen_down!= True:
                if reduced_str[-5:] in ["pu()|","pd()|"]:#this is done to take away unnecessary up/down changes
                    reduced_str=reduced_str[0:-5]
                reduced_str += order+"|"
                c_pen_down =True
        if order[0:2]=="ps":
            if c_thickness != int(Commands.nth_parameter(order,0)):
                reduced_str += order+"|"
                c_thickness = int(Commands.nth_parameter(order,0))
        if order[0:2]=="wr":
            reduced_str += order+"|"
        if order[0:2]=="sh":
            if int_arguments[0]!=c_current_heading:
                reduced_str += order +"|"
                c_current_heading = int_arguments[0]
    return reduced_str

def reduce(temp_str:str):
    result="£"+reducestep(reducestep(reducestep(temp_str)))
    return result


#tells how much value of x-changes, if movement is done in the direction of current_rotation
def x_movement(angle:float,movement:float): #angle float used to be int before 27.8.
    x_move=math.cos(math.pi*angle/180)*movement
    return x_move

#tells how much value of y-changes, if movement is done in the direction of current_rotation
def y_movement(angle:float,movement:float):
    y_move=math.sin(math.pi*angle/180)*movement
    return y_move

# how much rotation is needed to set the heading towards to_x,to_y
def rotate_towards_angle(x,y,rotation,to_x,to_y):
    angle=angle_to(x,y,to_x,to_y)-rotation
    if angle<0:
        angle=angle+360
    return angle

def jump_parameters(x,y,rotation,to_x,to_y):
    return [to_x-x,to_y-y, rotate_towards_angle(x,y,rotation,to_x,to_y)]


#returns the lines that make up a circle
def circle_lines(center_point,radius,thickness,color=[0.5,0.5,0.5],fillcolor=[0.7,0.2,0.3],pendown=True,filled=False):
    lines_in_circle=[]
    starting_point=(center_point[0],center_point[1]-radius)#starts from below
    l=math.sqrt(0.5*math.pi*radius)
    tu=90/l
    runningangle=tu/2 #angle in the beginning
    end_point1,end_point2=starting_point #lets see if you can add values like this
    while runningangle<360:
        end_point1=starting_point
        end_point2=(starting_point[0]+x_movement(runningangle,l),starting_point[1]+y_movement(runningangle,l))
        runningangle += tu
        lines_in_circle.append(Line(end_point1,end_point2,thickness,color,pendown,True,fillcolor))
        starting_point=end_point2
    finalturn=tu/2-runningangle+360
    finalmove=l*finalturn/tu
    last_end_point1=end_point2
    last_end_point2=(end_point2[0]+finalmove,end_point2[1])
    lines_in_circle.append(Line(last_end_point1,last_end_point2,thickness,color,pendown,True,fillcolor))
    return lines_in_circle

def arc_lines(center_point,radius,starting_point,thickness,color=[0.5,0.5,0.5],fillcolor=[0.7,0.2,0.3],pendown=True, arc_angle=90):
    lines_in_arc=[]
    l=math.sqrt(0.5*math.pi*radius)
    tu=90/l
    starting_angle=angle_to(center_point[0],center_point[1],starting_point[0],starting_point[1])+90 #angle in the beginning +tu/2 is a guess
    runningangle=starting_angle
    end_point1=end_point2=starting_point #lets see if you can add values like this
    while runningangle<starting_angle+arc_angle:
        end_point1=starting_point
        end_point2=(starting_point[0]+x_movement(runningangle,l),starting_point[1]+y_movement(runningangle,l))
        runningangle += tu
        lines_in_arc.append(Line(end_point1,end_point2,thickness,color,pendown,True,fillcolor))
        starting_point=end_point2
    #finalturn=tu-runningangle+arc_angle+starting_angle
    #finalmove=l*finalturn/tu
    #last_end_point1=end_point2
    #last_end_point2=(end_point2[0]+finalmove,end_point2[1])
    #lines_in_arc.append(Line(last_end_point1,last_end_point2,thickness,color,pendown,True,fillcolor))
    return lines_in_arc

#lines for oval
def oval_lines(center_point,x_radius,y_radius,thickness,color,fillcolor,pendown=True,filled=False):
    ov_lines=circle_lines(center_point,y_radius,thickness,color,fillcolor,pendown,filled)
    x_scaling_constant=x_radius/y_radius #tells how much we need to move the x-coordinates of line-endpoints
    for line in ov_lines:
        new_end_x1=center_point[0]+x_scaling_constant*(line.end_point1_x()-center_point[0])
        line.set_end_point1((new_end_x1,line.end_point1_y()))
        new_end_x2=center_point[0]+x_scaling_constant*(line.end_point2_x()-center_point[0])
        line.set_end_point2((new_end_x2,line.end_point2_y()))
    return ov_lines

#takes a list of lines and makes their corner points integer
def intify(linelist:List[Line]):
    for line in linelist:
        line.intify()
    return linelist


#returns True, if point x,y is inside a triangle with vertices point1, point2 and point3
def is_it_in_triangle(test_point,point1,point2,point3):
    x=test_point[0]
    y=test_point[1]

    first_heading=angle_to(point1[0],point1[1],point2[0],point2[1])
    second_heading=angle_to(point1[0],point1[1],x,y)
    gon1=first_heading-second_heading

    first_heading=angle_to(point2[0],point2[1],point3[0],point3[1])
    second_heading=angle_to(point2[0],point2[1],x,y)
    gon2=first_heading-second_heading

    first_heading=angle_to(point3[0],point3[1],point1[0],point1[1])
    second_heading=angle_to(point3[0],point3[1],x,y)
    gon3=first_heading-second_heading

    direction="clockwise"
    if (angle_to(point3[0],point3[1],point1[0],point1[1])-angle_to(point2[0],point2[1],point3[0],point3[1])) % 360 <180:
        direction="anticlockwise"

    if gon1 % 360<180 and gon2 % 360<180 and gon3 % 360<180 and direction=="clockwise":
        return True
    
    if gon1 % 360>180 and gon2 % 360>180 and gon3 % 360>180 and direction=="anticlockwise":
        return True

    return False

if __name__ == "__main__":

    line1=Line((10,30),(20,0),3,[0,0,0],True,True,[1,1,1])
    line1_5=Line((20,0),(30,-10),3,[0,0,0],True,True,[1,1,1])
    line2=Line((30,-10),(40,-20),3,[0,0,0],True,True,[1,1,1])
    line3=Line((40,-20),(-100,-100),3,[0,0,0],True,True,[1,1,1])
    line4=Line((-100,-100),(200,-100),3,[0,0.1,0],True,True,[1,1,1])
    line5=Line((200, -100), (300, -100),3,[0,0.1,0],True,True,[1,1,1])
    line6=Line((300, -100), (-200, 200),3,[0,0,0],True,True,[1,1,1])
    line7=Line((-200, 200), (200, -200),3,[0,0,0],True,True,[1,1,1])
    line8=Line((50,-30), (10, 30),3,[0,0,0],True,True,[1,1,1])

    poly=Polygon()
    poly.add_line(line1)
    poly.add_line(line2)
    poly.add_line(line3)
    poly.add_line(line4)
    poly.add_line(line5)
    poly.add_line(line6)
    poly.add_line(line7)
    poly.add_line(line8)
    drawi=Drawing("")
    drawi.add_polygon(poly)
    poly.reduce_unnecessary_vertices(2)

    #drawi.add_line(line5)
    #drawi.add_line(line6)
    #drawi.add_line(line7)
    #drawi.add_line(line8)

    #test_line=Line((0,100),(100,100),1,[0,0,0],True,True,[1,1,1])

    #for j in range(10):
    #    random_values=[]
    #    for i in range(4):
    #        random_values.append(random.random()*100)


    poly=Polygon()
    poly=poly.random_polygon()
    poly2=Polygon()
    poly2=poly2.random_polygon()
    drawi=Drawing("")

    drawi=drawi.random_drawing()

    drawi.filter(middle_color=[0.6,0.6,0.6],gap=-0.8)
#testattu same,reverse,halfcovered12, halfcovers21, halfcovered11, halfcovers11, halfcovered22, halfcovers22, halfcovered21, halfcovers12
#halfcovers12, halfcovered21, joined12, joined21, joined11, joined22, Tl1, Ts1m, Tl2, Ts2, crossing, disjoint  , covers, covered
#overlaps21, overlaps12, overlaps11 
