import math
import Geometry
from typing import List



#creates a memory fragment type is "string". color is taken as a float[]
def create_memory_fragment(order_code: str, polygon_sides: int, size:int, pensize: int,forward: int,rotation: int,color: List[float]):
    fragment= "#|"+order_code+"|"+str(polygon_sides)+"|"+str(size)+"|"+str(pensize)+"|"+str(forward)+ "|"+str(rotation)+ "|"
    fragment = fragment+  color_to_string(color)
    return fragment

#gives a string code for parameter type
def parameter_type_to_string(number:str):
    if number>6 or number<0:
        raise IndexError("No such parameter number")
    if number==0:
        return "order type"
    if number==1:
        return "polygon"
    if number==2:
        return "size"
    if number==3:
        return "pen"
    if number==4:
        return "jump"
    if number==5:
        return "turn"
    if number==6:
        return "color"

#gives a number related to parameter type
def parameter_type_to_int(string:str):
    array = ["order type", "polygon", "size", "pen", "jump", "turn", "color"]
    if string in array:
        return array.index(string)
    else:
        raise ValueError("No such parameter type")

# turns a string of instruction into list (cut by #). Note that memory is saved as a one long string, so this helps to "memorify" a saved file
def instructions_to_memory(instructions:str):
    list = split_the_string(instructions,"#")[1:]#poistetaan eka, että ei jää tyhjää käskyä
    for i in range (0,len(list)):
        list[i] = "#"+list[i]
    return list

#takes a string of commands no '#' in those, and spits out command_string with less unneccessary commands
def reduce(command_string:str):
    command_string=command_string.replace("||","|",-1)
    command_string=reducedoubles(command_string)
    command_string=command_string.replace("||","|",-1)
    command_string=reduceupdowns(command_string)

def reducedoubles(command_string):
    array=split_the_string(command_string,"|")
    new_array=[]
    for i in range(0,len(array)-1):
        if array[i]!=array[i+1]:
            new_array.append(array[i])
    new_array.append(array[-1])
    result=glue_the_split(new_array,"|")
    return result

def reduceupdowns(command_string:str):
    array=split_the_string(command_string,"|")
    new_array=[]
    state="b"
    for i in range(0,len(array)):
        if array[i] not in ["penup()","pendown()"] or (array[i]=="penup()" and state!="u" )or (array[i]=="pendown()" and state!="d"):
            new_array.append(array[i])
        if array[i]=="penup()":
            state="u"
        if array[i]=="pendown()":
            state="d"
    result=glue_the_split(new_array,"|")
    return result

def reducegotos(command_string:str):
    print("do this later", command_string)




#shortens the number of decimals in color
def color_tuple_shortener(color:List[float],decimals:int):
    if len(color) != 3:
        raise ValueError("need to have three parameters for color")
    if decimals<0:
        raise ValueError("can't have negative number of decimals")
    if decimals==0:
        raise ValueError("please don't pick this number, it is a very, very stupid number")
    strinc_color=[str(color[0])[0:decimals+2],str(color[1])[0:decimals+2],str(color[2])[0:decimals+2]]
    return [float(strinc_color[0]),float(strinc_color[1]),float(strinc_color[2])]

#returns a list of parameter values of fragment
def fragment_to_list(fragment:str):
    fragment_as_a_list=[]
    for i in range(0,7):
        fragment_as_a_list.append(parameter_number(fragment,i))
    return fragment_as_a_list

#color representation is changed from example list [0.4,0.5,0.2] to (0.4,0.5,0.2)
def color_to_string(color: List[float]):
#    if len(color)!=3:
 #       raise TypeError("Color variable has to have three parameters")
    return "("+str(color[0])+","+str(color[1])+","+str(color[2])+")"
    
#returns a float-list representing a color, which was given as a string 
def string_to_color(color_string: str):
    string_list=split_the_string(color_string, ",")
    string_list[0]=string_list[0][1:] #take off (
    string_list[2]=string_list[2][:-1] #take off )
    color=[float(string_list[0]),float(string_list[1]),float(string_list[2])]
    return color


#gets parameter from the fragment, returns it as a string
def parameter_number(fragment:str,parameter_number:int):
    array = split_the_string(fragment[2:], "|") #this akward [2:] is made since otherwise # is the first parameter
    array[6] = string_to_color(array[6]) # color parameters must be handled as float[]
    return array[parameter_number]

#returns a fragment with altered value in parameter number
def set_parameter(fragment:str,number:int, new_parameter:any):
    list=fragment_to_list(fragment)
    list[number]=new_parameter
   # list[6] = string_to_color(list[6])#tulos pitää saada niin, että väri on lista
    return create_memory_fragment(list[0],list[1],list[2],list[3],list[4],list[5],list[6])

#return float value of R in the fragment
def get_R_from_fragment(fragment:str):
    return parameter_number(fragment,6)[0]

#return float value of G in the fragment
def get_G_from_fragment(fragment):
    return parameter_number(fragment,6)[1]

#return float value of B in the fragment
def get_B_from_fragment(fragment):
    return parameter_number(fragment,6)[2]

# Split the string into an array of strings
def split_the_string(input_string, cut_symbol):
    string_array = input_string.split(cut_symbol)
    if " " in string_array:
        string_array.remove(" ") #jos alussa tai lopussa on tyhjää, ne on hyvä poistaa
    if "" in string_array: #6.8. this if clause was added, hope it doesnt ruin anything
        string_array.remove("") #kokeellinen muutos, toivottavasti ei tuo ongelmia
    return string_array

#Take a string array and glue it with glue_symbol, for example gts(["ab","cde","fg"],*)=ab*cde*fg
def glue_the_split(string_array, glue_symbol):
    result=""
    for string in string_array:
        result=result+ glue_symbol+string
    return result [1:] 
#returns a new memory, with fragment removed from the place number
def delete_fragment(memory:List[str],number:int):
    if number>=len(memory) or number<0:
        raise IndexError("Index is not in the memory")

    memory1=memory[0:number]
    memory2=memory[number+1:]
    memory=memory1
    for fragment in memory2:
        memory.append(fragment)
    return memory


# inserts a fragment, in index number 'number' without deleting any fragments. Thus memory is expanded by one fragment.
def insert_a_fragment_at(memory:List[str],number:int,new_fragment:str):
    if number > len(memory):
        raise IndexError("not a good index to put new fragment")
    new_memory=memory_copy(memory)
    new_memory.append([])# to create space for new fragment
    new_memory[number]=new_fragment
    size=len(new_memory)
    for i in range(number+1,size):
        new_memory[i]=memory[i-1]
    return new_memory

# insert a list of fragments in memory (without destroying existing fragments)
def insert_a_fragment_list_at(memory:List[str],number:int,fragment_list:List[str]):
    new_memory=memory_copy(memory)
    for i in range(0,len(fragment_list)):
        new_memory=insert_a_fragment_at(new_memory,number+i,fragment_list[i])
    return new_memory

#replace a fragment in place number with new_fragment
def replace_fragment(memory:List[str],new_fragment:str, number:int):
    new_memory=memory_copy(memory)
    new_memory[number]=new_fragment
    return new_memory

def fragment_number(memory:List[str],number:str):
    return memory[number]

#returns a copy of memory
def memory_copy(memory:List[str]):
    size=len(memory)
    copy=[]
    for i in range(0,size):
        copy.append(fragment_number(memory,i))
    return copy

#returns a memory, with parameter parameter_number in fragment number fragment_numberchanged to new_-value 
def replace_parameter_value_in_fragment(memory:List[str], fragment_number:int,parameter_number:int,new_value:any):
    new_memory=memory_copy(memory)
    replaced_fragment = set_parameter(memory[fragment_number],parameter_number,new_value)
    new_memory[fragment_number]=replaced_fragment
    return new_memory

#returns a memory with jumps, pensize, and size scaled with same factor (for example scale_factor 2 doubles the size) 
def scale(memory:List[str],scale_factor):
    new_memory=memory_copy(memory)
    for i in range(0,len(memory)):
        new_memory=replace_parameter_value_in_fragment(new_memory,i,2,int(scale_factor*float(parameter_number(new_memory[i],2))))
        new_memory=replace_parameter_value_in_fragment(new_memory,i,3,int(scale_factor*float(parameter_number(new_memory[i],3))))
        new_memory=replace_parameter_value_in_fragment(new_memory,i,4,int(scale_factor*float(parameter_number(new_memory[i],4))))
    return new_memory


#if drawing starts from (0,0) with direction 0, where does the fragment end (with normal scaling)?
def calculate_fragment_end_point(fragment:str):
    if parameter_number(fragment,0)=="m":
        return [int(float(parameter_number(fragment,4))),0]#oudon näköinen float lisätään kokeeksi, sillä kenties string ei muutu intiksi suoraan.
    if parameter_number(fragment,0)=="a":
        return [int(float(parameter_number(fragment,2))),0]
    if parameter_number(fragment,0)=="p" and parameter_number(fragment,1)=="1":#eli jos piirretään 1 sivuista "polygonia"
        return [int(float(parameter_number(fragment,2))),0]
    else:
        return [0,0]
    
#if drawing starts from (0,0) with direction 0, in which direction does the fragment end (with normal scaling)?
def calculate_fragment_end_rotation(fragment=str):
    if parameter_number(fragment,0)=="r":
        return int(parameter_number(fragment,5))
    else:
        return 0

#if drawing starts from (0,0) with direction "start_rotation", where does the fragment end (with normal scaling)?   
def calculate_rotated_fragment_end_point(fragment=str,start_rotation=int):
    helpvalues=calculate_fragment_end_point(fragment)
    complex=[math.cos((math.pi*2*start_rotation)/360), math.sin((math.pi*2*start_rotation)/360)]
    x= complex[0]*helpvalues[0] - complex[1]*helpvalues[1]
    y= complex[0]*helpvalues[1] + complex[1]*helpvalues[0]
    return [x,y]

#if drawing starts from (0,0) with direction "start_rotation", where does the fragment rotate (with normal scaling)?   
def calculate_rotated_fragment_end_rotation(fragment=str,start_rotation=int):
    rotation=start_rotation+calculate_fragment_end_rotation(fragment)
    if rotation>360:
        rotation=rotation-360
    return rotation

#seuraavaksi pitäisi kirjoittaa koko muistille loppupisteet
def fragment_list_end_point(fragment_list):
    location=[0,0]
    rotation=0
    for i in range (0,len(fragment_list)):
        location[0]=location[0]+calculate_rotated_fragment_end_point(fragment_list[i],rotation)[0]
        location[1]=location[1]+calculate_rotated_fragment_end_point(fragment_list[i],rotation)[1]
        rotation=calculate_rotated_fragment_end_rotation(fragment_list[i],rotation)
    return location

#muuten sama algoritmi, mutta palautetaan rotaatio    
def fragment_list_end_rotation(fragment_list):
    location=[0,0]
    rotation=0

    for i in range (0,len(fragment_list)):
        location[0]=location[0]+calculate_rotated_fragment_end_point(fragment_list[i],rotation)[0]
        location[1]=location[1]+calculate_rotated_fragment_end_point(fragment_list[i],rotation)[1]
        rotation=calculate_rotated_fragment_end_rotation(fragment_list[i],rotation)
    return rotation

def list_of_end_points(memory:List[str]):
    end_points =[[0,0]]
    previous_rot = 0
    previous_x = 0
    previous_y = 0
    size=len(memory)
    for i in range(0,size):
        new_x = previous_x+calculate_rotated_fragment_end_point(memory[i],previous_rot)[0]
        new_y= previous_y+calculate_rotated_fragment_end_point(memory[i],previous_rot)[1]
        previous_rot=calculate_rotated_fragment_end_rotation(memory[i],previous_rot)
        end_points.append([new_x,new_y])#jostain syystä tässä oli memory[0:i]
        previous_x=new_x #tämä on tavallaan tarpeettoman monimutkaista, mutta selvittää algoritmin idean paremmin
        previous_y=new_y
    return end_points

def list_of_end_rotations(memory:List[str]):
    end_rotations =[0]
    previous_rot = 0
    size=len(memory)
    for i in range(0,size):
        new_rot=calculate_rotated_fragment_end_rotation(memory[i],previous_rot)
        end_rotations.append(new_rot)#jostain syystä tässä oli memory[0:i]
        previous_rot=new_rot #tämä on tavallaan tarpeettoman monimutkaista, mutta selvittää algoritmin idean paremmin
    return end_rotations


#returns a list of ending points in memory, NOTE that the length of list is len(memory +1)
# first ending point is at [0,0] NOTE vanha versio, jonka voi poistaa, jos uusi toimii
def list_of_end_points2(memory:List[str]):
    end_points=[[0,0]]#to add the starting location to list
    for i in range(0,len(memory)):
        end_points.append(fragment_list_end_point(memory[0:i+1]))#jostain syystä tässä oli memory[0:i]
    return end_points

#returns a list of ending rotations in memory, NOTE that the length of list is len(memory +1)
# first rotation point is 0 in the start NOTE vanha algoritmi, toivottavasti uusi on parempi
def list_of_end_rotations2(memory:List[str]):
    end_rotations=[0]
    for i in range(0,len(memory)):
        end_rotations.append(fragment_list_end_rotation(memory[0:i+1]))#jostain syystä tässä oli memory[0:i]
    return end_rotations

#turns memory (which is in the original #-format, into command format, with the help of goto_memory())
def raw_drawing_instructions(memory:List[str]):
    goto=[]
    goto.append("£v|0|0|0|1|10|[0.5,0.5,0.5]|u")
    heading=0
    x=0
    y=0
    for fragment in memory:
        i_list = instruction_list(x,y,heading,fragment)
        x=i_list[1]
        y=i_list[2]
        heading=i_list[3]
        go="£"+i_list[0]+"|"+ str(i_list[1])+"|"+ str(i_list[2])+"|"+ str(i_list[3])+"|"+str(i_list[4])+"|"
        go=go+str(i_list[5])+"|"+str(i_list[6])+"|"+str(i_list[7])
        goto.append(go)

    if "" in goto:
        goto.remove("")#get rid of empty values
    
    print("tältä näyttää goto:",goto)
    command_list=[]

    for inst in goto:
        parameters = split_the_string(inst,"|")
        print("tältä näyttää parameters", parameters)
        if parameters[0]=="£v": #arvojen vaihto
            command_list.append("pensize("+parameters[4]+")")
            command_list.append("color("+parameters[6]+")")
        if parameters[0]=="£a" or parameters[0]=="£p" or parameters[0]=="£l": #nuoli, polygoni, jana
            command_list.append("pendown()")
            command_list.append("pensize("+parameters[4]+")")
            command_list.append("color("+parameters[6]+")")
            command_list.append("goto("+parameters[1]+","+parameters[2]+")")
        if parameters[0]=="£b": #begin fill
            command_list.append("fillcolor("+parameters[6]+")")
            command_list.append("begin_fill()")
        if parameters[0]=="£e": #end fill
            command_list.append("end_fill()")
        if parameters[0]=="£c": #circle
            command_list.append("pendown()")
            command_list.append("pensize("+parameters[4]+")")
            command_list.append("color("+parameters[6]+")")
            command_list.append("circle("+parameters[5] +")")
        if parameters[0]=="£m": #jump
            command_list.append("penup()")
            command_list.append("pensize("+parameters[4]+")")
            command_list.append("color("+parameters[6]+")")
            command_list.append("goto("+parameters[1] +","+parameters[2]+")")
        if parameters[0]=="£r": #rotaation
            command_list.append("setheading("+parameters[3] +")")   

    return command_list



#this creates a new type of memory, which works in absolute coordinates instead of orders to jump,
#turn, line etc
#fragment structure of this memory is: #order|to_x|to_y|heading_after|_pensize|up/down|color
#it tells,what to do|where to go (x)|where to go(y)|position of turtle head after order|pensize during order
#|is pen up or down during order|what is the color
def goto_memory(memory:List[str]):
    goto=[]
    goto.append("£v|0|0|0|1|10|[0.5,0.5,0.5]|u")
    heading=0
    x=0
    y=0
    for fragment in memory:
        i_list = instruction_list(x,y,heading,fragment)
        x=i_list[1]
        y=i_list[2]
        heading=i_list[3]
        go="£"+i_list[0]+"|"+ str(i_list[1])+"|"+ str(i_list[2])+"|"+ str(i_list[3])+"|"+str(i_list[4])+"|"
        go=go+str(i_list[5])+"|"+str(i_list[6])+"|"+str(i_list[7])
        goto.append(go)
    return goto

#takes a string from goto_memory and return value of its parameter or parameter_type
def goto_parameter(goto_fragment:str, parameter_type):
    to_list= split_the_string(goto_fragment[1:],"|") #puts parameters on the list
    if parameter_type=="order":
        return to_list[0]
    if parameter_type=="x":
        return int(to_list[1])
    if parameter_type=="y":
        return int(to_list[2])
    if parameter_type in["heading","rotation"]:
        return int(to_list[3])
    if parameter_type=="pen":
        return int(to_list[4])
    if parameter_type=="size":
        return int(to_list[5])
    if parameter_type=="color":
        return to_list[6]
    if parameter_type=="updown":
        return to_list[7]
    
    

#gives a list associated to single memory_fragment, this list is used to make goto_type memory_fragment
#this instruction_list doesn't draw polygons (pencil is left on the same location)
#this can be left as it is.
def instruction_list(x,y,heading,memory_fragment):
    goto_list=["v",0,0,0,1,10,"(0.5,0.5,0.5)","d"]#order,x,y,rot,pensize,objectsize,color,penup/down
    goto_list[0]=parameter_number(memory_fragment,0)#order

    if parameter_number(memory_fragment,0) in ["c","v","r","b","e"]:
        goto_list[1]=x #pysyy paikallaan
        goto_list[2]=y #pysyy paikallaan
    if parameter_number(memory_fragment,0)=="p" and parameter_number(memory_fragment,1)!="1":
        goto_list[1]=x #pysyy paikallaan
        goto_list[2]=y #pysyy paikallaan
    if parameter_number(memory_fragment,0) in ["a","l"]:
        goto_list[1]=x+Geometry.x_movement(heading,int(parameter_number(memory_fragment,2))) #piirtää
        goto_list[2]=y+Geometry.y_movement(heading,int(parameter_number(memory_fragment,2))) #piirtää
    if parameter_number(memory_fragment,0) == "m":
        goto_list[1]=x+Geometry.x_movement(heading,int(parameter_number(memory_fragment,4))) #hyppää
        goto_list[2]=y+Geometry.y_movement(heading,int(parameter_number(memory_fragment,4))) #hyppää
    if parameter_number(memory_fragment,0)=="p" and int(parameter_number(memory_fragment,1))==1: #suora
        goto_list[1]=x+Geometry.x_movement(heading,int(parameter_number(memory_fragment,2))) #liikkuu
        goto_list[2]=y+Geometry.y_movement(heading,int(parameter_number(memory_fragment,2))) #liikkuu

    if parameter_number(memory_fragment,0) in ["r"]:
        goto_list[3]=heading+ int(parameter_number(memory_fragment,5)) #kääntyy
    else:
        goto_list[3]=heading #ei käänny
    if goto_list[3]>360:
        goto_list[3]=goto_list[3]-360

    goto_list[4]=parameter_number(memory_fragment,3)#pensize

    goto_list[5]=parameter_number(memory_fragment,2)#object size

    goto_list[6]=parameter_number(memory_fragment,6)#color
    
    if parameter_number(memory_fragment,0) in ["c","a","p","l","r","b","e"]:
        goto_list[7]="d" #pen down
    else:
        goto_list[7]="u" #pen up
    
    return goto_list





#gives a short description (str) of what was done in memory string index (compared to index-1)
def shorten_command(string_array,index:int):
    if len(string_array)<2:
        return "no command"
    if index==len(string_array):
        return "end"
    if index>len(string_array):
        raise IndexError("too large index")
    if index<0:
        raise IndexError("negative index is not allowed")
    if index==0:
        return "start"
    result="Nr: "+str(index)+": "
    this_fragment=string_array[index]
    order_type=parameter_number(this_fragment,0)
    if order_type == "v":
        result += "Value change"
    if order_type == "b":
        result += "Begin to fill"
    if order_type == "e":
        result += "End to fill"
    if order_type == "a":
        result += "Arrow: size = " + str(parameter_number(this_fragment,parameter_type_to_int("size")))
    if order_type == "p":
        result += "Polygon, sides: " +str(parameter_number(this_fragment,parameter_type_to_int("polygon"))) +" size = " + str(parameter_number(this_fragment,parameter_type_to_int("size")))
    if order_type == "m":
        result += "Jump: " +str(parameter_number(this_fragment,parameter_type_to_int("jump")))
    if order_type == "r":
        result += "Turn: " +str(parameter_number(this_fragment,parameter_type_to_int("turn")))
    if order_type == "s":
        result += "Square: size" +str(parameter_number(this_fragment,parameter_type_to_int("size")))
    return result

#this makes this type of change: (0.5, 0.23, 0.325) -> [0.5,0.23,0.325]
def colortuplestr_to_liststr(tuple:str):
    array=split_the_string(tuple,",")
    r=array[0].strip(" ")
    r=r.strip("(")
    r=r.strip(")")
    g=array[1].strip(" ")
    g=g.strip("(")
    g=g.strip(")")
    b=array[2].strip(" ")
    b=b.strip("(")
    b=b.strip(")")
    return "["+r+","+g+","+b+"]"
    

if __name__ == "__main__":
    fragment1=create_memory_fragment("a",0,1,12,45,54,[0.231,0.4324,0.2])
    fragment2=create_memory_fragment("r",0,2,12,45,354,[0.231,0.4324,0.2])
    fragment3=create_memory_fragment("r",0,3,12,45,97,[0.231,0.4324,0.2])
    fragment4=create_memory_fragment("v",0,4,12,45,254,[0.21,0.24,0.3])
    fragment5=create_memory_fragment("a",0,5,12,45,254,[0.21,0.24,0.3])

    fragment6="#|r|1|72|15|20|344|(0.5019607843137255, 0.5019607843137255, 0.5019607843137255)"
    memory=[fragment1,fragment2,fragment3,fragment4,fragment5,fragment6]
    print("memory:", memory)
    goto_memory=goto_memory(memory)
    print("this is goto_memory",goto_memory)
    print("raws:",raw_drawing_instructions(memory))

    lista=[34,23,12,456,34,24,34,34,17]
    print(lista)
    while 34 in lista:
        lista.remove(34)
        print(lista)
    print(lista)
    
    test=3
    if test==1:
        print("1")
    elif test==3:
        print("3")
    elif test==5:
        print("5")
    else:
        print("else")


    print(color_tuple_shortener(color=[0.3,0.4,0.5],decimals=2))
#    new_memory=replace_parameter_value_in_fragment(memory,2,3,77)
 #   print(new_memory)
  #  print(memory)

#    print(fragment_list_end_rotation(memory))
 #   print(fragment_list_end_point(memory))
  #  print(glue_the_split(["ferg","dbw","34g","dsvfbsdfb"],"*"))