#Commands idea is to tell how to pack complex command prompts to basic commands to be  executed
import MemoryHandler
import string
import random
import math
import numpy as np

#makes commandline into list of smaller commands, for example #nuoli *2(nuoli+dots+#greenify) turns to [#nuoli *2(nuoli+dots)]
def space_list(commandline:str):
    return MemoryHandler.split_the_string(commandline, " ")

#returns one string, where the first * symbol is eliminated
def multiplies_off(command_segment:str):
    if command_segment[0]=="*":
        order_starts=command_segment.find("(") #order to be multiplied starts here
        order_ends=find_matching_parenthesis(command_segment,order_starts)
        if order_starts != -1:
            return (command_segment[order_starts+1:order_ends]+" ")*int(command_segment[1:order_starts])+command_segment[order_ends+1:]
    return command_segment

#finds the placement of the pair of parenthesis, for example the pair of the  fmp("abr(23*+ab)+b)",3)=13 and fmp("abr(23*+ab)+b)",3)=10
def find_matching_parenthesis(strin:str,starting_location:int):
    counter=-1
    if strin[starting_location] != "(":
        raise ValueError("No parenthesis at starting location")
    for i in range(starting_location+1,len(strin)):
        if strin[i]=="(":
            counter = counter -1
        if strin[i]==")":
            counter = counter+1
        if counter==0:
            return i
    raise ValueError("There is no pair for the parenthesis")
    


def take_off_double_space(commandline:str):
    result=commandline.replace("  "," ")
    return result

#takes of all multiply symbols in commandline (while making the needed syntax operations) returns individual command in a list 
def simplify(commandline:str):
    result=commandline
    while result.find("*")!=-1:
        #commands=space_list(commandline)
        index=result.find("*")
        help = result[0:index]
        help= help+multiplies_off(result[index:])
        result=help
        result=take_off_double_space(result)
    command_list = space_list(result)
    while "" in command_list:
        command_list.remove("") #this seems to be easiest trick to get away with empty orders
    return command_list


#tells the parameters in the string, note that color parameters are counted as one. i.e. for example [0.4,0.6,0.324]
#is only 1 parameter
def parameterlist(command:str): #changed 10:50 8.7. to accommodate text-variable with "," behaviour
    #if command[0] != "#":
    #    raise IndexError("Command has no parameters")   
    start_index = command.find("(")
    end_index = command.find(")")
    color_boolean=False
    new_command=command
    for i in range(start_index,end_index): 
        if command[i]=="[":
            color_boolean=True
        if command[i]=="]":
            color_boolean=False
        if color_boolean and command[i]==",":
            new_command=new_command[0:i]+"§"+new_command[i+1:] #now every ',' inside of color value is replaced by '§'


    text_boolean=False #this is to prevent , inside a text parameter to be "parameter-splitters"
    for i in range(start_index,end_index): 
        if command[i]=="'": 
            if text_boolean==False:
                text_boolean=True
            else:
                text_boolean=False    
        if text_boolean and command[i]==",":
            new_command=new_command[0:i]+"§"+new_command[i+1:] #now every ',' inside of text value is replaced by '§'

    parameter_array=MemoryHandler.split_the_string(new_command[start_index+1:end_index],",")#+1 takes away "(" 
    for i in range(0,len(parameter_array)):
        parameter_array[i]=parameter_array[i].replace("§",",",-1)
    return parameter_array


# Tells nth_parameter in basic command (in str), for example np ("#line(2,5,6)",0)=2 and np ("#line(2,5,6)",1)=5.
#handles color variables correctly
def nth_parameter_color_version(command:str,n:int):
    lista=parameterlist(command)
    if n >=len(lista) or n<0:
        raise IndexError("No such parameter number")  
    return lista[n]

#this was used until 17.6, it doesn't handle color variables correctly
def nth_parameter(command:str,n:int):
    #if command[0] != "#":
    #    raise IndexError("Command has no parameters")   
    start_index = command.find("(")
    end_index = len(command)
    parameter_array=MemoryHandler.split_the_string(command[start_index:end_index],",")
    parameter_array[0] = (parameter_array[0])[1:]
    parameter_array[len(parameter_array)-1]= (parameter_array[len(parameter_array)-1])[:-1]
    if n >=len(parameter_array) or n<0:
        return None 
    return parameter_array[n]


#class ShortCommand:


class Function:
    name=""
    parameter_list=[]
    output_model_str="" #output will be a a new Function, if this is a basic function

    def __init__(self,name,parameter_list=[],output_model_str=""):
        self.name=name
        self.parameter_list=parameter_list
        self.output_model_str=output_model_str
        if output_model_str=="":
            self.automatic_output_model_str()

    #makes a string representation of function, for example Function("forward",["x"],"forward(x)")
    #is represented as forward(x)=x and
    #Function("corner",["x","y"],"forward(x)|turn(y)") is represented as corner(x,y)=forward(x)|forward(y) 
    def representation_str(self): 
        result=self.name
        if len(self.parameter_list)==0: #i.e. function is actually a constant or variable
            return self.name+"="+self.output_model_str

        if len(self.parameter_list) != 0:
            result+="("
        for parameter in self.parameter_list:
            result += parameter +","

        if len(self.parameter_list) != 0:
            result= result[:-1]+")"
        return result +"="+self.output_model_str

    def automatic_output_model_str(self): #if there is no user spesified output_model_str, it is created here
        result=self.name
        if len(self.parameter_list)==0: #i.e. function is actually a constant or variable
            self.output_model_str= self.name

        if len(self.parameter_list) != 0:
            result+="("
        for parameter in self.parameter_list:
            result += parameter +","

        if len(self.parameter_list) != 0:
            result= result[:-1]+")"
            self.output_model_str=result

    #given arguments, calculates the representation, if the number of arguments is less than parameters, 
    #puts "syntax error" in place of missing argument 
    def representation_with_assigned_arguments(self,argument_list): 
        if len(argument_list) < len(self.parameter_list):
            argument_list+=(len(self.parameter_list)-len(argument_list))*["syntax error"]

        par_arg_dict={}
        for i in range(len(self.parameter_list)):
            par_arg_dict[self.parameter_list[i]]=argument_list[i]

        function_str=MemoryHandler.split_the_string(self.representation_str(),"=")[1]
        result=assign_arguments(function_str,par_arg_dict)
        return result

    #take parameters and form a string from them, the technic is best described by examples:
    #string_mutation({a:47,b:51},["prod(",a,"*"",b,")"])      prod(47,5.1) 
    #string_mutation({a:11,b:0.3,c:4},["prod(",a,b,c,")"])       prod(a,b,c)  
    #this method is used by checking if string is of some format, for example 
    #is_it_format(string,[type1,type2,...,typen]) which returns True is string in question can be concatenated from consecutive substrings
    #substr1,...,substrn such that syntax_test(substr1,type1), syntax_test(substr2,type2),... etc are all True  
def string_mutation(parameter_dict,end_format_list):
    result=""
    for i in range(end_format_list):
        if end_format_list[i] in parameter_dict.keys():
            result += parameter_dict[end_format_list[i]]
        else:
            result += end_format_list[i]


    #returns true if substrings string[0:cut_index[0]],string[cut_index[0]:cut_index[1]],...string[cut_index[n]:] 
    # are of the type type_test_list[i], where i is the index of sub_string      
    #for example is_it_format("sin(x2)",[3,4,6],["term","(","name",")"]) is true
    #while is_it_format("sin(x2)",[3,4,6],["term","(","number",")"]) is false
def is_it_format(string,cut_indexes,type_test_list):#Tested
    if len(type_test_list) != len(cut_indexes)+1:
        raise IndexError("There should be one more type_test than cut_index")
    array=[]
    if len(cut_indexes)==0:
        array=[string]
    else:
        array.append(string[0:cut_indexes[0]])
        for i in range(0,len(cut_indexes)-1):
            array.append(string[cut_indexes[i]:cut_indexes[i+1]])
        array.append(string[cut_indexes[-1]:])
    for i in range(len(array)):
        if syntax_test(array[i],type_test_list[i])==False:
            return False
    return True

#from the syntax of the function_str we look if the substring of function_str can be thought of as an argument in function
def is_it_argument(function_str,start_index,end_index): #NOTE there are probably problems in this 
    if start_index==0:
        return False
    if end_index==len(function_str):
        return False
    if start_index>=end_index:
        return False
    
    sub_str=function_str[start_index:end_index]
    if len(outside_commas(sub_str)) >0:
        return False
    if sub_str.find(")")<sub_str.find("("):
        return False
    if sub_str.count("(") != sub_str.count(")"):
        return False 
    if function_str[start_index-1] not in [",","("]:
        return False
    if function_str[end_index] not in [",",")"]:
        return False


    if function_str[start_index-1] in [",","("] and function_str[end_index] in [",",")"]:
        return True
    return False



    #just for testing, prints all things that can be thought as an argument in function_str
def print_all_arguments(function_str):
    for i in range(len(function_str)):
        for j in range(len(function_str)):
            if is_it_argument(function_str,i,j):
                print(function_str[i:j])


class Reduction:
    list_of_functions=[] #Functions, for example Function("turn",[x1],"turn(x1)")
    basic_functions=[] #this should be a subject of list_of_functions, it consists of those functions that have output_model_str
    #which is the same as function_name +"("+str(parameter_list[0])+","+str(parameter_list[0])+...+")"
    #i.e. string representation of basic_functions can't be reduced any further
    #NOTE I write this after few days brake, bbut I think the idea was that for example forward is basic function:
    #Its model string is forward(x1)=forward(x1)
    math_functions=[] #this is a special list of functions, 
    #for example Function(function_name="sin",parameters=["x1"],output_model_str="sin(x1)") can be listed as math function

    #NOTE you have to remember to add functions you are going to use in list_of_functions, otherwise things do not work
    def __init__(self,list_of_functions=[],math_functions=[]):
        self.list_of_functions=list_of_functions
        math_functions=math_functions
        self.set_basic_functions()

    #when initializing, this sets the basic_functions to be those functions in list_of_functions
    #that do not reduce the representations any further
    def set_basic_functions(self): 
        self.basic_functions=[]
        for function in self.list_of_functions:
            repr_str= function.representation_str()
            repr_array= MemoryHandler.split_the_string(repr_str,"=")
            if repr_array[0]==repr_array[1]:
                self.basic_functions.append(function)

    #in the list of functions we find a function by its name
    def get_function_by_name(self,name):
        for i in range(len(self.list_of_functions)):
            if self.list_of_functions[i].name==name:
                return self.list_of_functions[i]
        raise ValueError("no function with name 'name'")
        

    #returns a list of the names of all basic_functions
    def list_of_basic_function_names(self):
        basic_names=[]
        for b_function in self.basic_functions:
            basic_names.append(b_function.name)
        return basic_names
    
    #returns a list of the names of all functions
    def list_of_function_names(self):
        function_names=[]
        for l_function in self.list_of_functions:
            function_names.append(l_function.name)
        return function_names
    
    def list_of_math_function_names(self):
        mc=MathCommands()
        return mc.list_of_reserved_function_names 

    #returns a list of the names of function, which aren basic_functions
    def list_of_non_basic_function_names(self):
        the_list=[]
        for name in self.list_of_function_names():
            if name not in self.list_of_basic_function_names():
                the_list.append(name)
        return the_list

   
    def reduce_step(self,function_str):
        nb_function_names=self.list_of_non_basic_function_names()
        start_index=-1
        function_name=""
        for nb_function in nb_function_names:
            if function_str.find(nb_function)>-1:
                start_index=function_str.find(nb_function)
                function_name=nb_function
        if start_index==-1:
            return function_str
        print(start_index)
        end_index=find_function_end_index(function_str,start_index) #KESKEN kerro dokmentointoinnissa että tämä kertoo mihin loppuu strt_indexistä alkanut funktion osuteen liittynyt substr
        print("end_index",end_index)
        arguments=arguments_from_function_str(function_str[start_index:end_index+1])
        print("function_name",function_name,arguments)
        the_function=self.get_function_by_name(function_name)
        sub_str_after_assignment=the_function.representation_with_assigned_arguments(arguments)
        print("end result",function_str[0:start_index]+sub_str_after_assignment+function_str[end_index+1:])
        return function_str[0:start_index]+sub_str_after_assignment+function_str[end_index+1:]


    #if there are functions that aren't basic functions, this get rid of them
    def reduction_to_basic_functions_expression(self,function_str):
        i=0
        reduced_str=self.reduce_step(function_str)
        while i<100 and reduced_str != function_str: #NOTE due to limit 100, functions with over 100 compositions might stop working
            function_str=reduced_str
            reduced_str= self.reduce_step(function_str)
            i += 1
        return reduced_str
    
    #if there are math_functions in function_str, they are applied and this version of function_str is returned
    def math_reduction(self,function_str):
        mc=MathCommands()
        result_str=mc.syntax_fixes(function_str) #this for example turns 4*5 to prod(4,5)
        print("after syntax fixes",result_str)
        result_str=mc.from_combined_function_str_to_value(result_str)
        return result_str

    #this takes the function_str, and turns it to simplest possible form to execute its commands
    def fully_processed_function_str(self,function_str): #this seems to work nicely, when arguments are numbers, although slowly
        print("function_str in fully_pr...",function_str)
        result_str=self.reduction_to_basic_functions_expression(function_str)
        print("after_reduction_to_basics:",result_str)
        result_str=self.math_reduction(result_str)
        result_str=self.reduction_to_basic_functions_expression(result_str)
        return result_str

    



#count nro of substrings
def count(substr,theStr):
    num = 0
    for i in range(len(theStr)):
        if theStr[i:i+len(substr)] == substr:
            num += 1
    return num



#if there are (pure) numbers in 'function_str' they are taken away from parenthesis, for example (3+4)*(5)+((7))-(2.7) ->(3+4)*5+7-2.7
def all_numbers_out_of_parenthesis(function_str):
    result=function_str
    if len(function_str)==0:
        return ""
    for i in range(len(result)):
        if number_out_of_parenthesis(result,i)!=result:
            return all_numbers_out_of_parenthesis(number_out_of_parenthesis(result,i))
    return result

#given a string 'function_str' which has extra parenthesis inside each other, takes a way those extra parenthesis
#for example (((1,3)),((2,(5,7)))) -> ((1,3),(1,(5,7))) and ((2,5),(7),8) ->(2,5,7,8) NOTE that (last effect can sometimes be unwanted)
def double_parenthesis_off(function_str): #somewhat tested
    result=function_str
    cond1=True
    cond2=True
    while cond1 or cond2:
    #    pairs=parenthesis_pairs(result)
        cond1=False
   #     for pair in pairs: #extra_parenthesis of from ((something))
   #         if result[pair[0]+1]=="(" and result[pair[1]-1]==")" and cond==False:
   #             if find_matching_parenthesis(result,pair[0]+1)==pair[1]-1:
    #                result=result[:pair[0]]+result[pair[0]+1:pair[1]-1]+result[pair[1]:]
     #               cond1=True
      #              break
        pairs=parenthesis_pairs(result)
        pairs=pairs_without_end_indexes(pairs,len(result)-1)
        pairs=pairs_without_end_indexes(pairs,0)

        cond2=False
        for pair in pairs: #extra_parenthesis of from ((something))
            if result[pair[0]-1] in [",","("] and result[pair[1]+1] in [",",")"] and cond2==False:
                result=result[:pair[0]]+result[pair[0]+1:pair[1]]+result[pair[1]+1:]
                cond2=True
                break
    return result

#pairs should be list of int value pairs [x,y], returned pairs are all te pairs except those with x==index or y==index
def pairs_without_end_indexes(pairs,index):
    new_pairs=[]
    for pair in pairs:
        if pair[0] != index and pair[1] != index:
            new_pairs.append(pair)
    return new_pairs 

#if nro of "(" and ")" is the same, returns the indice of first "(" and last")"
def outest_parenthesis(function_str):
    if count("(",function_str)==0 and count(")",function_str)==0:
        return []
    if count("(",function_str) == count(")",function_str):
        return(function_str.find("("),function_str.rfind(")"))  
    for i in range(len(function_str)):
        if function_str[i]=="(":
            return [i,find_matching_parenthesis(function_str,i)]

#for example in sum(pow(x),product(y,z)), innest parenthesis pairs are [7,9] and [19,23], indexes of parenthesis with no parenthesis inside
def innest_parenthesis_pairs(function_str):
    if count("(",function_str)==0 and count(")",function_str)==0:
        return []
    result=[]
    if count("(",function_str) == count(")",function_str):
        for i in range(len(function_str)):
            if function_str[i]=="(":
                if function_str[i+1:].find(")")<function_str[i+1:].find("(") or function_str[i+1:].find("(")==-1:
                    result.append([i,i+1+function_str[i+1:].find(")")])  
    return result

#returns all the parenthesis pairs
def parenthesis_pairs(function_str):
    if count("(",function_str)==0 and count(")",function_str)==0:
        return []
    if count("(",function_str)!= count(")",function_str):
        return "syntax error"
    result=[]
    for i in range(len(function_str)):
        if function_str[i]=="(":
            result.append([i,find_matching_parenthesis(function_str,i)])
    return result

#for function, which name starts is in 'start_index' returns end index of interval containing the function parameters
#function_str[end_index]= ")" so note that function_str[start_index:end_index] does not contain ")"  
def find_function_end_index(function_str,start_index):
    end_index=-1
    optimal_pair=[len(function_str),len(function_str)]
    for pair in parenthesis_pairs(function_str):
        if pair[0]>start_index and pair[0]<optimal_pair[0]:
            optimal_pair=pair
    return optimal_pair[1]
        
        

    

    for i in range(len(function_str)):
        if function_str[i]=="(":
            result.append([i,find_matching_parenthesis(function_str,i)])
    return result

#for example if we want to get the substring describing parameters of function, we can find it with this
# it will be stri[next_parenthesis_interval(stri,index)[0]:next_parenthesis_interval(stri,index)[1]]
#where index is an index of char belonging to function_str
#note that given interval contains ")" 
def next_parenthesis_interval(stri,index): #somewhat tested
    help_index=stri[index:].find("(")
    if help_index==-1:
        return None #there were no "("" parenthesis after this index
    start_index=index+help_index
    for pair in parenthesis_pairs(stri):
        if pair[0]==start_index:
            return [start_index,pair[1]+1]
    return None
    


#returns the substring of function_str which has left and right_parenthesis in the given indexes
def sub_function_str_with_parenthesis(function_str,left_parenthesis:int,right_parenthesis:int):
    if left_parenthesis<= 0 and right_parenthesis>=len(function_str)-1:
        return function_str
    if function_str[left_parenthesis] != "(":
        raise IndexError("Left parenthesis is not there")
    if function_str[right_parenthesis] != ")":
        raise IndexError("Right parenthesis is not there")
    opt1=function_str[0:left_parenthesis].rfind(",")
    opt2=function_str[0:left_parenthesis].rfind("(")
    opt3=function_str[0:left_parenthesis].rfind(")")
    opt4=function_str[0:left_parenthesis].rfind("|")
    start_index=max(0,opt1+1,opt2+1,opt3+1,opt4+1)
    return function_str[start_index:right_parenthesis+1]


#finds indexes of outest commas, for example if function_str is tulo(sum(moi,hei),moi) then the only outest  comma is the last on
# in tulo(sum(moi,hei)) there is no outest commas, and in tulo(sum(moi,hei),moi,sum(moi,moi)) there are two outest commas, the ones in the middle
def outest_commas(function_str):
    index_list=[]
    parenthesis_difference=0
    for i in range(len(function_str)):
        if function_str[i]=="(":
            parenthesis_difference += 1
        if function_str[i]==")":
            parenthesis_difference += -1
        if parenthesis_difference == 1 and function_str[i]==",":
            index_list += [i]
        if parenthesis_difference<0:
            raise SyntaxError("function_str syntax is invalid, too many ')'")
        if parenthesis_difference==0 and function_str[i]==",": 
            raise SyntaxError("function_str syntax is invalid, ',' in wrong plaace")
    return index_list

# this returns the indexes of commas, that are outside of functions, for example in the string sum(x,y),z, the comma before z
#is outside of function whereas the one between x and y is inside
def outside_commas(possible_function_str):
    parenthesis_difference=0
    outside_indexes=[]
    for i in range(len(possible_function_str)):
        if possible_function_str[i]=="(":
            parenthesis_difference += 1
        if possible_function_str[i]==")":
            parenthesis_difference += -1
        if parenthesis_difference==0 and possible_function_str[i]==",":
            outside_indexes.append(i)

    return outside_indexes

#this gets the function name, from string describing it, note that the syntax if this function_str might be corrupt
def function_name_from_function_str(function_str):
    return function_str[0:function_str.find("(")]

#taking a function_str returns the arguments of it, if it has ones
def arguments_from_function_str(function_str):
    comma_indexes=outest_commas(function_str)
    parenthesis_indexes=outest_parenthesis(function_str)
    list_of_arguments=[]
    if len(parenthesis_indexes)==2:
        comma_indexes=[parenthesis_indexes[0]]+comma_indexes+[parenthesis_indexes[1]]
        for i in range(len(comma_indexes)-1):
            list_of_arguments.append(function_str[comma_indexes[i]+1:comma_indexes[i+1]])
    return list_of_arguments




 #given a dictionary in the form of {parameter1:argument1,parameter2:argument2,...} this replaces every parameter in function_str
#by corresponding argument, for example assign_arguments("sin(prod(x2,x3))",{"x2",45,x3,"78"})=sin(prod(45,78))      
def assign_arguments(function_str,par_arg_dict):
    pairs=list_maximal_name_indexes(function_str)#these are automatically in ascending order, like [[2,3],[5,9],[11,17]]
    if len(pairs)==0:
        return function_str
    anti_pairs=[[0,pairs[0][0]]]
    for i in range(len(pairs)-1):
        anti_pairs.append([pairs[i][1],pairs[i+1][0]])
    anti_pairs.append([pairs[len(pairs)-1][1],len(function_str)])
    result=""

    for j in range(len(anti_pairs)-1):
        result += function_str[anti_pairs[j][0]:anti_pairs[j][1]]
        if function_str[pairs[j][0]:pairs[j][1]] in par_arg_dict.keys():
            result += par_arg_dict[function_str[pairs[j][0]:pairs[j][1]]]
        else:
            result += function_str[pairs[j][0]:pairs[j][1]]

    if function_str[anti_pairs[-1][0]:anti_pairs[-1][1]] in par_arg_dict.keys():
        result += par_arg_dict[function_str[anti_pairs[-1][0]:anti_pairs[-1][1]]]
    else:
        result += function_str[anti_pairs[-1][0]:anti_pairs[-1][1]]
    print("in assign arguments: function_str",function_str,"result",result,par_arg_dict)
    print("pairs, and antipairs:",pairs,anti_pairs)
    return result

#if there are values in the 'dict', that are simultaneously keys, this method helps to avoid some infinite loops
#which might be resulted from using 'dict' to cahnge values. This method creates two dictionaries, one dict1={key:antikey}
# other dict2= {antikey:values}, here antikeys are str:s which do not contain any key and also not any value
def middle_dictionaries(dict):
    keys_and_values=list(dict.keys())+list(dict.values())
    dict1={}
    dict2={}
    for key in list(dict.keys()):
        middle_value=random_str(5)
        while middle_value in keys_and_values: #in this unrealistic scenario we make sure that middle_values are not keys or values of 'dict'
            middle_value=random_str(5)
        dict1[key]=middle_value
        dict2[middle_value]=dict[key]
    return [dict1,dict2]

#just creates a random string that is not substring of string
def random_not_substring_of(string):
    result=random_str(4)
    while result in string:
        result=random_str(4)
    return result

#creates random_str of letters with length 'length'
def random_str(length:int):
    letters = string.ascii_lowercase 
    randomstr=''.join(random.choice(letters)for i in range(0,length))
    return randomstr


# for example in tulo(sum(moi,hei),moi,sum(moi,moi)), innest functions are moi,hei,moi,moi and moi, in more standard language
#they are constants or variables, but they can be thought as functions with 0 parameters
def is_it_innest_function(function_str):
    if function_str.find(",")==-1 and function_str.find("(")==-1:
        return True
    return False

#given a representation_str of function, for example "tulo(sum(moi,hei),moi,sum(moi,moi))"
#returns a function, which parameters are strings representing its outest parameters
#in the aforementioned case, function is Function with name tulo and parameter_list ["sum(moi,hei)","moi","sum(moi,moi)"]

# esim. ymp(x,y)=ja(jana(x),jana(y)) pallo(z)=ymp(z,ymp(z))=ja(jana(z),jana(ymp(z)))=ja(jana(z),jana(ja(jana(z),jana(z))))
#funk

class MathCommands:
    list_of_reserved_function_names=[]
    def __init__(self):
        self.list_of_reserved_function_names=math_function_list()

    #calculates value of math function, if all arguments are numbers
    def calculated_value_str(self,name:str,arguments:str):#somewhat tested
        value=0
        print("name,argments",name,arguments)
        result_str=name+"("
        for argument in arguments:
            result_str +=argument+","
        result_str=result_str[:-1]+")"
        for argument in arguments:
            if is_float(argument)==False:
                return result_str  
            argument=float(argument)
        
        arguments_as_nros=[]
        for argument in arguments:
            arguments_as_nros.append(float(argument))

        if name=="sum":
            value=sum(arguments_as_nros)
        if name in ["times","product","prod"]:
            value=np.prod(arguments_as_nros)
        if name in ["divide","div"]:
            print("aan",arguments_as_nros)
            value=arguments_as_nros[0]/arguments_as_nros[1]    
    
        if name== "sin":
            value=math.sin(arguments_as_nros[0])
        if name== "cos":
            value=math.cos(arguments_as_nros[0])
        if name== "tan":
            value=math.tan(arguments_as_nros[0])
        
        if name in ["pow","power"]:
            value=math.pow(arguments_as_nros[0],arguments_as_nros[1])

        if name == "sqrt":
            value=math.sqrt(arguments_as_nros[0])

        if name == "log":
            value=math.log(arguments_as_nros[0])

        if name == "ln":
            value=math.log(arguments_as_nros[0])

        if name == "exp":
            value=math.exp(arguments_as_nros[0])
            
        return str(value)

    #given a function_str this returns the value of this function as a str. This actually doesn't handle combined functions
    def from_simple_function_str_to_value(self,function_str):
        name=function_name_from_function_str(function_str)
        arguments=arguments_from_function_str(function_str)
        print("in fsftv fstr",function_str,"te rest",name,arguments)
        return self.calculated_value_str(name,arguments)

    #taking values of function_str, which might involve combined functions, returns a function_str with calculated values (if possible)
    def from_combined_function_str_to_value(self,function_str):
        result_str=self.combined_step(function_str)
        while result_str != function_str:
            function_str=result_str
            result_str=self.combined_step(function_str)
        return result_str
        
    #one step in the function from_combined_function_str_to_value.
    def combined_step(self,function_str):
        pairs=innest_parenthesis_pairs(function_str)
        replacer_str=""
        result=function_str
        print("in combined_step",function_str)
        for i in range(len(pairs)):
            innest_function_str=sub_function_str_with_parenthesis(function_str,pairs[i][0],pairs[i][1])
            replacer_str=self.from_simple_function_str_to_value(innest_function_str)
            print("in combined_step ri",replacer_str,innest_function_str)
            result=function_str.replace(innest_function_str,replacer_str)
        return result

 
    # fixes all syntax issues on function_str, for example turns 4*5 into prod(4,5)
    def syntax_fixes(self,function_str):
        result_str=self.add_implied_multiplication(function_str)
        print("after implied_mltiplication:", result_str)
        result_str=get_rid_of_math_symbols(result_str)
        return result_str

    #for example writing sin(x)cos(x), we actually mean sin(x)*cos(x), this adds multiplication signs into those places
    def add_implied_multiplication(self,string): #somewhat tested
        indexes=[]
        for i in range(len(string)-1):
            if string[i]==")" and string[i+1] not in [")",",","/","*","+","-"]: #index of * to be added for example in sin(x)cos(x)
                indexes.append(i)
            elif string[i].isnumeric() and string[i+1].isalpha(): #index of * to be added for example in  3sin(x)
                indexes.append(i)
        result=""
        for i in range(len(string)):
            if i not in indexes:
                result += string[i]
            else:
                result +=string[i]+"*"
        return result



#takes string and changes symbols +,-,* and/ to sum, minus,prod and div functions
def get_rid_of_math_symbols(string):
    result=star_to_prod_step(string) #for example 4*3 ->prod(4,3) this also includes 4/3 to div(4,3) modification
    while result != string:
        string=result
        result=star_to_prod_step(string) #for example 4*3 ->prod(4,3) this also includes 4/3 to div(4,3) modification
    print("after star_to_prod",result)
    result=plus_to_sum_step(result) #for example 4+3 ->sum(4,3) this also includes 4-3 to sum(4,-3) modification
    while result != string:
        string=result
        result=plus_to_sum_step(string) #for example 4+3 ->sum(4,3) this also includes 4-3 to sum(4,-3) modification
    return result


#tests if the number of parenthesis in string is equal
def equal_nro_of_parenthesis(string):
    if count("(",string)==count(")",string):
        return True
    else:
        return False

#which are the possible indexes in string, where a new semantical unit might start
def potential_cutting_indexes(string):
    cutting_indexes=[0]
    for i in range(1,len(string)):
        if string[i] in delimiter_list() or string[i] in math_operator_list():
            cutting_indexes.append(i)
            #cutting_indexes.append(i+1)
        elif string[i] not in delimiter_list()+math_operator_list() and string[i-1] in delimiter_list()+math_operator_list():
            cutting_indexes.append(i)
    cutting_indexes.append(len(string))
    return cutting_indexes

#returned index_pairs tell only possible index starting place and ending place for syntactically meaningful string
def potential_cutting_pair_indexes(string):
    cutting_indexes=potential_cutting_indexes(string)
    pair_indexes=[]
    for i in range(len(cutting_indexes)-1):
        for j in range(i+1,len(cutting_indexes)):
            if equal_nro_of_parenthesis(string[cutting_indexes[i]:cutting_indexes[j]]):
                pair_indexes.append([cutting_indexes[i],cutting_indexes[j]])
    return pair_indexes

#given string splits it to array composed of minimal components of syntax
def string_to_syntax_array(string):
    cutting_indexes=potential_cutting_indexes(string)
    array=[]
    for i in range(len(cutting_indexes)-1):
        array.append(string[cutting_indexes[i]:cutting_indexes[i+1]])
    return array

def print_cut_string(string): #for testing purposes
    pairs=potential_cutting_pair_indexes(string)
    for i in range(len(pairs)-1):
        print(string[pairs[i][0]:pairs[i][1]])

def print_split(string):
    cutting_indexes=potential_cutting_indexes(string)
    for i in range(len(cutting_indexes)-1):
        print(string[cutting_indexes[i]:cutting_indexes[i+1]])

def print_cut_syntax(string):#testing
    array=string_to_syntax_array(string)
    print(array)
    for item in array:
        print_syntax_analysis(item)

#for example 4*3 ->prod(4,3)
def star_to_prod_step(stri):
    index1=stri.find("*")
    index2=stri.find("/")
    if index1==-1 and index2==-1:
        return stri
    if (index1<index2 and index1>0) or index2==-1: # if leftmost operation is * instead of / 
        interval_pair=find_minimal_term_indexes(stri,index1)#start and end indexes for area consisting of the terms to be multiplied
        print("interval_pair",interval_pair)
        return stri[:interval_pair[0]]+"prod("+stri[interval_pair[0]:index1]+","+stri[index1+1:interval_pair[1]]+")"+stri[interval_pair[1]:]
    else: # if leftmost operation is / instead of * 
        interval_pair=find_minimal_term_indexes(stri,index2)#start and end indexes for area consisting of the terms to be multiplied
        return stri[:interval_pair[0]]+"div("+stri[interval_pair[0]:index2]+","+stri[index2+1:interval_pair[1]]+")"+stri[interval_pair[1]:]

def minus_syntax_fix(stri):
    print("do later KESKEN")

#for example 4+3 ->sum(4,3)
def plus_to_sum_step(stri): #NOTE minus is not currently handled, it would be good to handle in this method
    index=stri.find("+")
    if index==-1:
        return stri
    interval_pair=find_minimal_term_indexes(stri,index)#start and end indexes for area consisting of the terms to be summed
    return stri[:interval_pair[0]]+"sum("+stri[interval_pair[0]:index]+","+stri[index+1:interval_pair[1]]+")"+stri[interval_pair[1]:]

#for example prod(prod(4,3),5) to prod(4,3,5)
def prod_out_prod_step(string):
    try_pairs=potential_cutting_pair_indexes(string)
    result=string
    for pair in try_pairs:
        sub_str=string[pair[0]:pair[1]]
        #if is_function_with_arguments(sub_str): PALAUTETTAVA KUN TÄYDENNETTY
        #    array=arguments_of(sub_str) #KESKEN arguments of listaa sub_str:in uloimmat argumentit, jos niitä on ja syntx ok
        #    for item in array:
        #        if is_function_with_arguments(item):
        #            if item[0:4]=="prod"

#if the string consists of consecutive substrings sub_str0, sub_str1,..., etc such that each test[i] is satisfied by substr[i]
#KESKEN problem function_names are cutted at the beginning
def string_matching_structure(string,syntax_test_type_list):
    i=0
    test_nro=0
    cuts=potential_cutting_indexes(string)
    i_cut_index=0
    j_cut_index=0
    i=cuts[i_cut_index]
    j=cuts[j_cut_index]
    while i<len(string):
        j=cuts
        if test_nro>=len(syntax_test_type_list):
            return False
        while j <=len(string): #we test if sub_strings satisfies the syntax_test 
            if syntax_test(string[i:j],syntax_test_type_list[test_nro]):
                test_nro +=1
                i=j
                j=len(string)+1
            else: 
                j+1
    if test_nro==len(syntax_test_type_list): # if the last test_type was satisfied by choosing last substring to end in the end of string
        return True
    return False


#taking a test_str tells, if test_str is a type of object described in
def syntax_test(test_str,test_type):
    if test_type=="number": #is it float (str)
        return is_float(test_str)
    elif test_type=="operator": #is it a single char consisting of +,*,- or /
        return test_str in math_operator_list()
    elif test_type=="name": #atom name can be variable or name of the function, it starts by alphabet and doesn't include operators or delimiters 
        return is_name(test_str)   
    elif test_type=="math_function": #math_function is special case of name, as  "sin", "log" etc
        return test_str in math_function_list()  
    elif test_type=="delimiter": #parenthesis or ',' pr space " "
        return test_str in delimiter_list()
    elif test_type=="parameter": #name or number
        return is_parameter(test_str)
    elif test_type=="atom_term": #parameter, name(parameter,...,parameter) or parameter operator parameter
        return is_atom_term(test_str)
    elif test_type=="term": #atom_term, (term), name(term,term,...) or term operator term
        return is_term(test_str)
    elif test_type==test_str:# this allows testing for example if string is just ",", by using test_type ","
        return True
    else: #this has to be the last test
        return False

# if string[[start_index:end_index] is a term but adding one symbol to this substring makes it unterm, returns True 
def is_it_maximal_term(string,start_index,end_index): #tested, works as intended except although e.g. in sin(x), (x) is not maximal
    this_term_cond= is_term(string[start_index:end_index])
    next_term_cond=is_term(string[start_index:min(end_index+1,len(string))])==False or len(string)==end_index
    previous_term_cond=is_term(string[max(start_index-1,0):end_index])==False or start_index==0
    parameter_condition= string[min(end_index,len(string)-1)] != "(" #without this, function without parameters would be maximal
    return this_term_cond and next_term_cond and previous_term_cond and parameter_condition

#this finds a minimal_term from stri which stri[index] belongs to, 
# for example in find_minimal_term_indexes("sin(prod(3,4)+2)",5) returns [4,13] since smallest meaninggul semantical unit 
#containing "r" is prod(3,4)
def find_minimal_term_indexes(stri,index):
    list_of_maximal_term_indexes=[]
    for i in range(len(stri)):
        for j in range(i+1,len(stri)+1):
            if is_it_maximal_term(stri,i,j):
                list_of_maximal_term_indexes.append([i,j])
    best_indexes=[0,len(stri)]
    for pair in list_of_maximal_term_indexes:
        if pair[0]>=best_indexes[0] and pair[0] <= index and pair[1]<=best_indexes[1] and pair[1] > index:
            best_indexes=pair #note that it is important that pair[1] != index
    return best_indexes

#finds the start and end indexes of number with char in function_str[index], for example 234+4355*5,5 -> [4,8]
def find_minimal_number_indexes(function_str,index):
    interval=[index,index]
    cond=True
    while cond:
        cond=False
        if is_number(function_str[interval[0]:interval[1]+1]):
            interval[1] += 1
            cond=True
        if is_number(function_str[interval[0]-1:interval[1]]):
            interval[0] += -1
            cond=True
    return interval
        

#for testing above method
def print_minimal_term_analysis(stri):
    for i in range(len(stri)):
        print("string",stri,"index",i,stri[find_minimal_term_indexes(stri,i)[0]:find_minimal_term_indexes(stri,i)[1]])



#list types of which string can be tested to be in syntax_test function
def test_type_list():
    return ["number","name","operator","delimiter","math_function","parameter","atom_term","term",",","(",")"]


def print_syntax_analysis(string): #for testing, which type of thing, string is
    result_str=string+" is "
    for type in test_type_list():
        if syntax_test(string,type):
            result_str += type +"    "
    print(result_str)




def math_function_list():
    return ["sum","times","product","prod","divide","div","sin","cos","tan","pow","power","sqrt","log","ln","exp"]

def math_operator_list():
    return ["+","*","/","-"]

def delimiter_list():
    return ["(",")",","," "]

#first symbol shoulde be letter and no delimiters or operators are allowed to make this true 
def is_name(string):
    if len(string)<=0:
        return False
    if string[0].isalpha()==False:
        return False
    for thing in math_operator_list():
        if thing in string:
            return False
    for thing in delimiter_list():
        if thing in string:
            return False
    return True

#lists all the index_pairs for start and end index of maximal_names (substring that is name, bt if extended is not) 
def list_maximal_name_indexes(function_str):
    pairs=[]
    size=len(function_str)
    for i in range(0,size):
        for j in range(0,size+1):
            cond1=is_name(function_str[i:min(size,j+1)]) and size!=j
            cond2=is_name(function_str[max(0,i-1):j]) and 0!=i
            if i<j and is_name(function_str[i:j]) and cond1==False and cond2==False:
                pairs.append([i,j])
    
    print("function_str",function_str,"pairs",pairs)
    return pairs


#atom_parameter terms are numbers, or so-called function names (which aren't necessarely function names but might be varaible names)
def is_parameter(string):
    if is_float(string) or is_name(string): #is_name is string starting with alphabet that doesnät contain delimiters or operators
        return True
    return False
    
# is this string of the form parametet,  or name(parameter,...,parameter) or parameter operator parameter
def is_atom_term(string):
    if is_parameter(string):
        return True
    if count("(",string)==1 and count(")",string)==1 and string[-1]==")": #is this name(parameter,parameter,...,parameter)
        array=string[:-1].split("(")
        if is_name(array[0])==False:
            return False
        parameter_array=array[1].split(",")
        for parameter in parameter_array:
            if is_parameter(parameter)==False:
                return False
        return True
    
    nro_of_operators=0
    nro_of_limiters=0
    operators=math_operator_list() #*,+*- or /
    limiters=delimiter_list()#(, ",",")"
    help_str=string
    for operator in operators: #is this string parameter operator parameter, fro example 4*31.2
        nro_of_operators += count(operator,string)
        help_str=string.replace(operator,operators[0])
    for limiter in limiters:
        nro_of_limiters += count(limiter,string)

    if nro_of_operators==1 and nro_of_limiters==0:
        array=help_str.split(operators[0])
        if is_parameter(array[0]) and is_parameter(array[1]):
            return True
    
    return False




#test if this string is atom_term   or   name(term,...,term)   or   term operator term 
def is_term(string): 
    if equal_nro_of_parenthesis(string)==False:
        return False

    if is_atom_term(string):
        return True

    if len(string)==0: #no empty strings allowed
        return False
    
    if string[0]=="(" and string[-1]==")": #i.e. if 'x' is term, then '(x)' is term, where x is any string
        if is_term(string[1:-1]):
            return True

    for i in range(1,len(string)): #checking if this is a term of type term math_operator term 
        if string[i] in math_operator_list():
            if equal_nro_of_parenthesis(string[:i]) and equal_nro_of_parenthesis(string[i+1:]):
                if is_term(string[:i]) and is_term(string[i+1:]):
                    return True
    

    if string[-1]==")":#checking if this is a term of type name(term,...,term) 
        out_pair=outest_parenthesis(string)
        parameter_sub_str= string[out_pair[0]+1:out_pair[1]]
        if is_name(string[:out_pair[0]]):
            array=parameter_sub_str.split(",")
            cond=True
            for item in array:
                if is_term(item)==False:
                    cond=False
            if cond:
                return True
    return False



def is_float(s):
    for oper in ["*","/","+","-"]:
        if oper in s:
            return False
    try:
        float(s)
    except ValueError:
        return False  

    return True


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False            
    

class CommandLine:
    functions=[]
    constructed_functions=[]
    variables=[]

    def __init__(self):
        print("kesken")

    def representation_str(self):
        result=""
        for function in self.functions:
            result +=function+"|"
        return result




if __name__ == "__main__":

    print("START",find_minimal_number_indexes("343245,345,24,pfkp(34),dfg(99,2354.5+2)",30))
    print("teese",list_maximal_name_indexes("exp(ln(3)+binomi(x2)"))
    binomi=Function("binomi",parameter_list=["x1","x2"],output_model_str="prod(x1+x2,x1+x2)")
    rinom=Function("rinom",parameter_list=["x1","x2"],output_model_str="prod(sum(x1,x2),sum(x1,x2))")
    binomi2=Function("binomi2",parameter_list=["x1","x3"],output_model_str="prod(sum(x1,x3),x1-x3)")
    forward=Function("forward",parameter_list=["x1"])
    print(forward.representation_str())

    kolmioluku=Function("kolmioluku",parameter_list=["x1"],output_model_str="sum(div(prod(x1,x1),2),div(x1,2))")

    uusi=Function("uusi",parameter_list=["x","y"],output_model_str="x+3*y")
    pop=Function("uusi2",parameter_list=["x","y","z"],output_model_str="z*x/y")
    pop2=Function("uusi3",parameter_list=["x","y","z"],output_model_str="2+z/(x+2)*y")
    pop3=Function("uusi4",parameter_list=["x","y","z"],output_model_str="div(x,(sum(y,z)))")
    list_of_functions=[kolmioluku,binomi,rinom,binomi2,uusi,pop,pop2,pop3,forward]
    repe=Reduction(list_of_functions)

    print("Jakolasku pop3:ssa feilaa, onko syynä sisäkkäiset sulut? Koita ratkoa tuolla extra_p... avulla")
    print("vastaus",repe.fully_processed_function_str("uusi2(2,4,5)"),repe.fully_processed_function_str("uusi4(2,4,5)"))
    print("BUGI: UUDEN LASKUJÄRJESTY EI PELITÄ, JOSKUS ILMAANTUU MYÖS SATUNNAISSEKVENSSSEJÄ, KUTEN nioe NÄKYVIIN")
    #bf=repe.basic_functions  2+5/(2+2)*4
    #for b in bf:
    #    print(b.representation_str())
    #print(repe.reduction_to_basic_functions_expression("binomi(1,2)"))
    #fpro=repe.fully_processed_function_str("binomi(7,2)")

    #lpro=repe.fully_processed_function_str("sum(kolmioluku(kolmioluku(kolmioluku(3))),kolmioluku(5))")
    #print("fpro",fpro)

  
    #print(star_to_prod_step(star_to_prod_step(string)))

    mc=MathCommands()
    #print(mc.prod_fix("prod(1,prod(2,3*5))"))

    


    #VOISIKO SYNTAX ERRORIN TULKITA NIIN, ETTÄ EI OLE SIIS TERMI?
    #forbidden_symbols=[",","(",")","|"]
    #sub_str=(",895)")
    #print(list(set(forbidden_symbols)&set([2,3,","]))) #list intersection

    #print(sub_function_str_with_parenthesis("summa(binomi(1,3),binomi(1,7))",12,16))
    print(mc.from_combined_function_str_to_value("exp(ln(3)+binomi(2,3))"))
    #print(mc.from_combined_function_str_to_value("sum(3,4,12,13.4)"))

  






