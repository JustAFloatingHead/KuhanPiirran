
#meillä on funktioita, voivat olla nollapaikkaisia, n-paikkaisia tai kaikki-paikkaisia
#lisäksi vakioita/muuttujia, funktiot tunnistetaan siitä, että niiden perään tulee sulkupari,
#jonka sisällä muuttujat ovat
#funktioille tarvitaan ainakin tallentamisohje ja laskemisohje, tallentamisohje kertoo
#millaisena kyseinen funktio tallennetaan tiedostoon
#laskemisohje kertoo, miltä funktio 'näyttää' tietyillä parametrin arvoilla

#funktio voi olla myös matematiikkafunktio, tällöin laskemisohje haetaan matematiikkamoduulista
#matemaattiset kaavat on tunnistettava ja muunnettava matematiikkafunktioiksi

#esimerkki muutoksen tapahtumisesta, käyttäjä tallentaa funktiot summa(x,y)=x+y
#tulo(x,y)=x*y ja binomi(x,y)=tulo(x,x)+2*tulo(x,y)+tulo(y,y)
#nämä tallennetaan tiedostoon muodossa summa(x,y)=sum(x,y), tulo(x,y)=prod(x,y) ja 
#binomi(x,y)=sum((sum(tulo(x,x),prod(2,tulo(x,y)))),tulo(y,y))
#tallennusprosessissa muutetaan siis jo matemaattiset operaattorit nimiksi, kuten prod ja sum

#funktion arvot lasketaan niin, että lasketaan esimerkiksi ensin binomi(2,3)=
#sum((sum(tulo(2,2),prod(2,tulo(2,3)))),tulo(2,3)) korvaamalla esiintymät
#sitten ylijääneestälausekkeesta käytetään korvaussääntöjä siinä esiintyville funktioille
#lopulta päädytään 1) kiintopistefunktioihin tai 2) matematiikkafunktioihin,
#1 kiintopistefunktiot voi tunnistaa niiden tallennusohjeesta, joka on esim forward(x)=forward(x),
# ts. kyseiset funktiot eivät enää muuta lauseketta, 
#(tällaisia funktioita tarvitaan tätä luokkaa hyödyntävissä projekteissa,
# ja se mitä ne tekevät määritellään niissä).  

#finds the placement of the pair of parenthesis, for example the pair of the  fmp("abr(23*+ab)+b)",3)=13 and fmp("abr(23*+ab)+b)",3)=10
#can locate the pair only if string[startin_location]=="(" else returns ValueError

import math
import numpy as np
from os import path 
import os
import random
import csv
import tkinter as tk
from tkinter import filedialog
import openpyxl




call_dict={}

class AntiMather:
#this is a class that takes strings and makes them as much antimathematical as possible
#for example 3+4sin(2x) -> sum(3,prod(4,sin(prod(2,x)))), it doesn't do anything to other strings like forward(4)|pircle(x)|line(3)
    function_str=""

    def __init__(self,function_str):
        self.function_str=function_str
        self.antisplit("|")#turns '|' to and operator
        self.anti_sign_start() # if function_str starts with + or -, we put 0 infront of it to help later steps
        self.double_signs_of()
        self.signs_to_operators({"^":"pow"}) # turns plusses into sum function representations
        self.signs_to_operators({"*":"prod","/":"div"}) # turns plusses into sum function representations
        # minus causes problems, we need to put minus(-a,b)-> minus(0,sum(a,b)) and minus(a,-b)-> sum(a,b)
        #and minus(-a,-b)->minus(b,a) 
        self.get_rid_of_minus_problem() 
        self.signs_to_operators({"+":"sum","-":"minus"}) # turns plusses into sum function representations
        self.function_str=self.indexify(self.function_str) #makes [] -> INDEX more precisely e.g. (4,6,7)[2]->INDEX(2,(4,6,7))
        self.indexvalue()
        self.remove_extra_parenthesis()

    #this takes self.function_str, for example "joku(2)|kok(3m5,235)|ojo()|hiphip(324,3)" and turns it to
    #AND(joku(2),kok(3m5,235),ojo(),hiphip(324,3)) 
    #of course this only holds for cut_symbol="|"
    def antisplit(self,cut_symbol):
        array=self.function_str.split(cut_symbol)
        if len(array)>1:
            self.function_str= "AND("
            for term in array:
                self.function_str += term+","
            self.function_str=self.function_str[:-1]+")"



    #makes [] go to index, for example  (3,4,5)[2] ->INDEX(2,(3,4,5))
    #multiple_indexes work this way ((a,b,c),(d,e,f))[1,2] -> INDEX((1,2),((a,b,c),(d,e,f))
    def indexify(self,function_str):
        new_str=function_str
        index_of_left_par=new_str.find("[")
        index_of_right_par=-1
        if index_of_left_par>0:
            index_of_right_par=find_matching_parenthesis(new_str,starting_location=index_of_left_par,parenthesis_type="[]")
            term_interval_before_par=smallest_complete_term_interval(new_str,index_of_left_par-1)
            term_part=new_str[term_interval_before_par[0]:term_interval_before_par[1]]
            index_part=new_str[index_of_left_par:index_of_right_par+1]
            new_str=new_str.replace(term_part+index_part,"INDEX(("+index_part[1:-1]+"),"+term_part+")")
            while new_str != function_str and new_str.find("[")>0:
                function_str=new_str
                index_of_left_par=new_str.find("[")
                index_of_right_par=-1
                if index_of_left_par>0:
                    index_of_right_par=find_matching_parenthesis(new_str,starting_location=index_of_left_par,parenthesis_type="[]")
                    term_interval_before_par=smallest_complete_term_interval(new_str,index_of_left_par-1)
                    term_part=new_str[term_interval_before_par[0]:term_interval_before_par[1]]
                    index_part=new_str[index_of_left_par:index_of_right_par]
                    new_str=new_str.replace(term_part+index_part,"INDEX(("+index_part[1:-1]+"),"+term_part+")")
            function_str=new_str
        return new_str

    #this turns functions of type INDEX(index_nro,(vector_com1,vector_comp2,...)) to vector_comp_index_nro
    #for example INDEX(2,(abba,lippa,koppa,p)) -> lippa (NOTE we use human notion of counting, lippa is the second item!)
    def indexvalue(self): #SOMEWAHT TESTED
        new_function_str=self.indexvalue_step(self.function_str)
        while new_function_str !=self.function_str:
            self.function_str=new_function_str
            new_function_str=self.indexvalue_step(self.function_str)


    def indexvalue_step(self,strin):#SOMEWHAT TESTED
        if strin.find("INDEX")==-1: #faster calculating
            return strin
        success=False
        for i in range(len(strin)):
            success=True
            interval=None
            cond=True
            this_term=""
            try: #bug fix, not every interval should be tried
                interval=smallest_complete_term_interval(strin,i)
                this_term=strin[interval[0]:interval[1]]
            except SyntaxError:
                cond=False

            if this_term[0:5]=="INDEX" and type_of(this_term)=="function_with_arguments" and cond:
                if function_name_of(this_term)=="INDEX":
                    arguments=arguments_of(this_term)
                    if len(arguments) !=2: #wrong number of arguments: this is actually sign of problems in the syntax
                        success=False
                    if arguments[1][0]!="(" or arguments[1][-1]!=")": #this_term must be of type INDEX(index,(x,y,z,w))
                        success=False
                    multi_index=[] #components for tensor
                    if is_number(arguments[0]):
                        multi_index=[int(float(arguments[0]))]
                    else:
                        try:
                            multi_index_component_strs=vector_components(arguments[0])
                            for i in range(len(multi_index_component_strs)):
                                multi_index.append(int(float(multi_index_component_strs[i])))
                        except SyntaxError:#it might be that we have for example function like mod(x,2) inside arguments[0], 
                            return strin #this must then be processed elsewhere, before returning here
                    replacer=""
                    try:
                        replacer=tensor_component(multi_index,arguments[1])
                    except IndexError:
                        success=False
                    if success:
                        return strin[:interval[0]:]+ replacer +strin[interval[1]:]
        return strin


        
                

    #adds 0 before self.function_str if it starts by + or -
    def anti_sign_start(self):
        if len(self.function_str)>0: 
            if self.function_str[0] in ["+","-"]:
                self.function_str="0"+self.function_str
        self.no_plus_after_parenthesis()

    #if there is "(+..." or "(-..." adds zero between as -> "(0+..." or -> "(0-...". This trick makes syntax easier
    def no_plus_after_parenthesis(self):#SOMEWHAT TESTED
        while self.function_str != self.no_plus_after_parenthesis_step(self.function_str):  
            self.function_str = self.no_plus_after_parenthesis_step(self.function_str)  

    def no_plus_after_parenthesis_step(self,strin):#SOMEWHAT TESTED
        strin=strin.replace("(+","(0+")
        strin=strin.replace(",+",",")
        return strin


    #takes of consecutive signs if possible
    def double_signs_of(self):
        while self.function_str != self.first_double_sign_of(self.function_str):
            self.function_str = self.first_double_sign_of(self.function_str)

    #takes of extra parenthesis in the self.function_Str
    def remove_extra_parenthesis(self):
        self.function_str=self.double_parenthesis_off(self.function_str)

    #takes of double parenthesis when possible
    def double_parenthesis_off(self,function_str):
        par_pairs=parenthesis_pairs(function_str) #all parenthesis pairs
        pot_par_pairs=[] #list of double parenthesis which are the inside parenthesis in string like this ((something))
        for pair in par_pairs:
            if pair[0]>0 and pair[1]<len(function_str)-1:
                if function_str[pair[0]-1] in [",","("] and function_str[pair[1]+1] in [",",")"] : 
                    pot_par_pairs.append(pair)
        for pair in pot_par_pairs:#for handling ((8))->(8) type of tranformations
            if len(vector_components(function_str[pair[0]:pair[1]+1]))==1:
                return self.double_parenthesis_off(function_str[:pair[0]]+function_str[pair[0]+1:pair[1]]+function_str[pair[1]+1:])
        for pair in pot_par_pairs: #for handling vectors ((2,3,4))->(2,3,4) for example NOTE added 26.1
            if [pair[0]-1,pair[1]+1] in par_pairs:
                return self.double_parenthesis_off(function_str[:pair[0]]+function_str[pair[0]+1:pair[1]]+function_str[pair[1]+1:])
        return function_str


    #one step of taking double signs of
    def first_double_sign_of(self,strin):
        signs=["+","-","*","/","^"]
        i=0
        first_sign_index=-1
        while i<len(strin)-1:
            if strin[i] in signs and strin[i+1] in signs:
                first_sign_index=i
                break
            i+=1
        if first_sign_index >=0 and first_sign_index< len(strin)-1: 
            first_sign=strin[first_sign_index]
            second_sign=strin[first_sign_index+1]
            if (first_sign,second_sign) not in [("+","+"),("+","-"),("-","-"),("-","+")]:
                raise SyntaxError("Thou have written bad syntax with signs and should be punished")
            if (first_sign,second_sign) in [("+","+"),("-","-")]:
                return strin[0:first_sign_index]+"+"+strin[first_sign_index+2:]
            if (first_sign,second_sign) in [("+","-"),("-","+")]:
                return strin[0:first_sign_index]+"-"+strin[first_sign_index+2:]
        return strin


    #takes all signs which are keys in sing_operator_dict and turns them in to corresponding operator, for example + -> sum
    #this done from left to right: here is an example:
    # signs_to_operators({"+":sum,"-":minus}) 8-6+23 -> sum(minus(8,6),23)    
    def signs_to_operators(self,sign_operator_dict):
        nro_of_signs=0 #meant to represent sum of number of signs in dict.keys()
        sign_keys=sign_operator_dict.keys()
        for sign in sign_keys:
            nro_of_signs += count(sign,self.function_str)
        while nro_of_signs>0:
            self.function_str=self.replace_first_sign(self.function_str,sign_operator_dict)
            nro_of_signs += -1

    # minus causes problems, we need to put minus(-a,b)-> minus(0,sum(a,b)) and minus(a,-b)-> sum(a,b)
    #and minus(-a,-b)->minus(b,a) 
    def get_rid_of_minus_problem(self):
        if "minus" in self.function_str:
            particles=list_of_particles(self.function_str)
            for i in range(len(particles)):
                this_particle=particles[i]
                if this_particle=="minus":
                    this_particle_index=interval_of_particle_nro(self.function_str,i)[0]
                    this_term=term_in_index(self.function_str,this_particle_index)
                    arguments=arguments_of(this_term)
                    replacer_str=this_term
                    if arguments[0][0]=="-" and arguments[1][0]=="-":
                        replacer_str="minus("+arguments[1][1:]+","+arguments[0][1:]+")" 
                    if arguments[0][0]!="-" and arguments[1][0]=="-":
                        replacer_str="sum("+arguments[0]+","+arguments[1][1:]+")" 
                    if arguments[0][0]=="-" and arguments[1][0]!="-":
                        replacer_str="minus(0,sum("+arguments[0][1:]+","+arguments[1]+"))" 
                    if replacer_str!=this_term:
                        self.function_str=self.function_str[0:this_particle_index]+replacer_str+self.function_str[this_particle_index+len(this_term):]
                        self.get_rid_of_minus_problem()

    #takes first occ2
    # urrance of sign in strin and forms a new strin, by replasing sign with usage of function notation
    #for example replace_first_sign("joku+loku+noku","+","sum") -> sum(joku,loku)+noku
    #this actually makes mistake like replace_first_sign("laku*joku+noku","+","sum") -> laku*sum(joku,noku)
    #that's why it is important which signs are replaced first 
    def replace_first_sign(self,strin,sign_operator_dict):
        nro_of_signs=0 #meant to represent sum of number of signs in dict.keys()
        sign_keys=sign_operator_dict.keys()
        for sign in sign_keys:
            nro_of_signs += count(sign,strin)
        if nro_of_signs==0:
            return strin
        sign_index=len(strin)
        sign_type="not found yet"
        found=False
        for i in range(len(strin)): #finds first index where the sign in question isn't after '(' or ','
            for sign in sign_keys:
                if strin[i]==sign and strin[max(i-1,0)] not in [",","("]:
                    sign_index=strin.find(sign)
                    sign_type=sign
                    found=True
                    break
            if found:
                break

        if sign_index==len(strin):#no sign was found
            return strin

        previous_term_interval=[]
        following_term_interval=[]
        operator_name=sign_operator_dict[sign_type]

        if sign_index in range(1,len(strin)-1):
            if sign_type=="-" and strin[sign_index-1]=="(": #this happens when there is thing like forward(-2-3), we put and extra 0
                #to make it look like forward(0-2-3)
                return self.replace_first_sign(strin[:sign_index]+"0"+strin[sign_index:],sign_operator_dict)
            
            previous_term_interval=0
            previous_term_interval= smallest_complete_term_interval(strin,sign_index-1)
            following_term_interval= smallest_complete_term_interval(strin,sign_index+1)
            while (previous_term_interval[0] != "0"): #for things like "-3+5" we need to force the minus into the sum like sum(-3,5)
                if sign_type in ["+","-"] and strin[previous_term_interval[0]-1] in ["-","+"]:
                    previous_term_interval[0]=previous_term_interval[0]-1
                else:
                    break

        if len(previous_term_interval)==2 and len(following_term_interval)==2: #if the sign is not in the end or beginning of strin
            mod_strin= strin[:previous_term_interval[0]]+operator_name+"("+strin[previous_term_interval[0]:previous_term_interval[1]]
            mod_strin += ","+ strin[following_term_interval[0]:following_term_interval[1]]+")"+strin[following_term_interval[1]:]
            return mod_strin
        return strin






class Function:
    name=""
    parameter_list=[]
    output_model_str="" #
    specified_assignment_str="" #this is basicly the assign_part if output_model_str, but while initiating the
    #function, user can  give more specified way to construct the assignment_part fir example changing x+y to sum(x,y) etc.

    #we create a function by its name and parameters, plus output_model str which saves the instructions what happens when this function
    #is applied. output_model_str is created into format name(parameter_list[0],parameter_list[1],...)== assignment_str
    #the exception is that is assignment_str=="" then the format is name(parameter_list[0],...)==name(parameter_list[0],...)
    def __init__(self,name,parameter_list=[],assignment_str="",specified_assignment_str=""): #SOMEWHAT TESTED
        self.name=name
        self.parameter_list=parameter_list
        self.automatic_output_model_str(assignment_str)
        self.output_model_str= add_missing_multiplication_signs(self.output_model_str)
        if specified_assignment_str=="": #if user doesn't give this string it is the same as assignment part of output_model_str
            self.specified_assignment_str=self.output_model_str.split("==")[1] 

    def display_function(self):
        print("function_name: ",self.name)
        print("function parameters: ",self.parameter_list)
        print("function output_model_str",self.output_model_str)
        print("specified_assignment_str",self.specified_assignment_str)

    #if the user doesn't spesify output_model_str, it is created here, for example Function(name="jaa",parameter_list=[x,y,z])
    #created output_model_str jaakko(x,y,z)==jaakko(x,y,z)
    def automatic_output_model_str(self,assignment_str=""): #SOMEWHAT TESTED
        result=self.name
        if len(self.parameter_list)==0: 
            if assignment_str=="":
                self.output_model_str= self.name+"("+")=="+self.name+"("+")"
            else:
                self.output_model_str= self.name+"("+")=="+assignment_str

        if len(self.parameter_list) != 0:
            result+="("
        for parameter in self.parameter_list:
            result += parameter +","

        if len(self.parameter_list) != 0:
            result= result[:-1]+")"
            self.output_model_str=result
            if assignment_str=="":
                self.output_model_str=result +"=="+result
            else:
                self.output_model_str=result+"=="+assignment_str

    #let say output_model_str is neliö(x)=prod(x,x), then this method returns neliö(x)
    def output_model_str_key_part(self):
        return self.output_model_str.split("==")[0]

    #let say output_model_str is neliö(x)=prod(x,x), then this method returns prod(x,x)
    def output_model_str_assign_part(self):
        return self.output_model_str.split("==")[1]

    #when in the parameters of this function are assigned with 'arguments' this is the new string created
    def function_str_with_assigned_arguments(self,arguments):#SOMEWHAT TESTED
        assign_dict={}
        for i in range(min(len(self.parameter_list),len(arguments))):
            assign_dict[self.parameter_list[i]]=arguments[i]
        particles=list_of_particles(self.specified_assignment_str)
        assigned_str=""
        for i in range(len(particles)):
            if particles[i] in assign_dict.keys():
                assigned_str += assign_dict[particles[i]]
            else:
                assigned_str += particles[i]
        return assigned_str


 #loads a file
def load_file_as_string(file_name:str,sub_directory:str):
    actual_name= sub_directory+"/"+file_name.strip("'")+".txt"#strip ' just in case
    if sub_directory=="":
        actual_name=file_name+".txt"
        # Open a file for reading
    with open(actual_name, "r") as file:
        # Read the contents of the file into memory
        instructions=file.read()
    return instructions

def save_text_file(directory_path, file_name, content):
    file_path = os.path.join(directory_path, file_name)
    with open(file_path, 'w') as file:
        file.write(content)



class FunctionDatabase:

    function_list=[] #user saved functions, these are Functions, not just names
    math_function_names=["log","ln","exp","prod","div","sum","minus","pow","min","max","mod","sin","random","cos","tan","asin","acos","atan"] #these can be calculated by math-module
    special_function_names=["QUOTE","AND","LOOP","INDEX","IF"] #when we see this we do special operation
    non_reducable_function_names=[] #these functions can't be reduced any further
    reserved_names=[] #this is a list of names that can't be put names of added functions or variables
    variable_dict={} #for saving variables, this dict migh look like this {hippu:3,käsky:move(4),käsky2:3*hippu}
    #variable_dict is used in such way that when user gives command like käsky=hippu, then the part after = is processed
    #and the processed version is saved in the dictionary so it gets new item {"käsky":str(proces...(hippu))}, when other orders
    #are later processed, if the contain str käsky, then this käsky is without showing to user, replaced by str(proces...(hippu))
    #then after this replacement, the order is processed 


    def __init__(self,filename="function_database",sub_directory="machinery",reserved_names=""):
        filetxt=load_file_as_string(filename,sub_directory)
        array=filetxt.split("\n")
        for item in array:
            if len(item)>2: #"just in case"
                self.function_list.append(self.construct_function_from_output_model(item))
        self.find_nonreducable_function_names() 
        self.variable_dict={}
        self.reserved_names=reserved_names

    #just for texting
    def print_function_list(self):
        flist=self.function_list
        print("These are the functions in function database")
        for function in flist:
            print(function.output_model_str)

    #info about this object
    def display_database(self): #TESTED
        print("function_list:")
        variable_list=self.variables_as_list()
        for func in self.function_list:
            print(func.output_model_str)
        print("nonreducable functions:")
        for names in self.non_reducable_function_names:
            print(names)
        for variable in variable_list:
            print("variable", variable)


    #if we want to have variables in list, this is how it is created
    def variables_as_list(self):
        variable_list=[]
        for key in self.variable_dict.keys():
            variable_list.append((key,self.variable_dict[key]))
        return variable_list
    #this processes the function_str to non_reducable format including only non_reducable functions, 
    #special_functions and math_functions
    #NOTE this is the main function

    def process_function_str(self,function_str):#SOME TESTING DONE
        new_function_str=self.math_rid(function_str) #gets rid of +,- etc, also created AND-operators
        new_function_str=self.reduse(new_function_str) #gets rid of non reducable functions
        while new_function_str != function_str:
            function_str=new_function_str
            new_function_str=self.math_rid(function_str)
            new_function_str=self.reduse(new_function_str)
        return new_function_str




    #first assigns the variables in variable_dict to function_str and then process the function_str returning it afterwards
    def assign_variables_and_process(self,function_str):#
        particles=list_of_particles(function_str)
        replaced_particles=[]
        variable_keys=self.variable_dict.keys()
        for i in range(len(particles)):
            replaced_particles.append(particles[i])
            if particles[i] in variable_keys:
                replaced_particles[i]=self.variable_dict[particles[i]]
        function_str=''.join(replaced_particles)
        new_function_str=self.process_function_str(function_str)
        return new_function_str

    #this processes the thing that is given in a main program,
    #if there is one == symbol, the function defined by by outputmodel of 'split[0]=split[1]' is saved
    #if there is no == symbols, total_function_str is split by "|" and processed in order, if there are definition of variables 
    #marked by '=', then those are done also in orders and assigned to all strings when it is time to process them
    def process_all(self,total_function_str):
        if count("==",total_function_str) not in [0,1]:
            return "syntax error" #too many function_assignments
        if count("==",total_function_str)==1: #we assign new function
            if type_of(total_function_str.split("==")[0])=="function_with_arguments":
                self.add_function_from_output_model(total_function_str.split("==")[0]+"=="+total_function_str.split("==")[1])
                return ""
        if count("==",total_function_str)==0:
            command_array=total_function_str.split("|")
            new_function_str=""
            for i in range(len(command_array)):
                if count("=",command_array[i])==1:
                    self.add_variable(command_array[i].split("=")[0],command_array[i].split("=")[1])
                    new_function_str += command_array[i]+"|" #modification 26.1. we leave the assignment to be seen so that turtle variables are easier to handle in main program

                if count("=",command_array[i])==0:
                    command_to_add= self.assign_variables_and_process(command_array[i])
                    new_function_str += command_to_add+"|"#as a last operation, we use loops, if this is done earlier, it might make extra loops
            total_function_str=self.all_loops(total_function_str,cutting_symbol="|") #added 24.1.
            new_function_str=new_function_str.strip("|")
            return new_function_str
                
    #this is basicly the same method as antisplit in AntiMather, but it is useful here slightly modified
    def andify(self,function_str,cut_symbol):
        array=function_str.split(cut_symbol)
        if len(array)>1:
            function_str= "AND("
            for term in array:
                function_str += term+","
            function_str=function_str[:-1]+")"
        return function_str

    #takes all loops and shifts their arguments
    def loops(self,function_str):
        function_str=self.andify(function_str,"|") #we need to have this here for the purposes of main program, so that
        #we can use only this method without processing other stuff
        intervals=self.locate_one_function_string_intervals(function_str)
        replace_dict={} #we need to do lot and lot of manouvres to make shifting LOOPs in such way that if two or more loops are involved
        #they don¨t mess around, for eg. LOOP(x,y)LOOP(y,x) should go to LOOP(y,x)LOOP(x,y)  
        for i in range(len(intervals)):
            this_one_string=function_str[intervals[i][0]:intervals[i][1]]
            if function_name_of(this_one_string)=="LOOP":
                arguments=arguments_of(this_one_string)
                replacer_str="LOOP("
                for i in range(1,len(arguments)):
                    replacer_str += arguments[i]+","
                replacer_str += arguments[0]+")"
                replace_dict[this_one_string]=replacer_str
        last_key_index=0
        for replacement_key in replace_dict.keys():
            last_key_index=function_str.find(replacement_key,last_key_index) #necessary trick to avoid double shifting
            function_str=function_str[:last_key_index]+replace_dict[replacement_key]+function_str[last_key_index+len(replacement_key):] 
        return function_str

    #this is a version of looping, that starts directly with user inputted string, which might contain for example 
    #operators +,- ...  etc. It returns the str in which only effects of looping are considered
    #HOWever, here no cutting symbols are allowed
    def loops_one_first(self,function_str):
        intervals=self.locate_one_function_string_intervals(function_str)
        replace_dict={} #we need to do lot and lot of manouvres to make shifting LOOPs in such way that if two or more loops are involved
        #they don¨t mess around, for eg. LOOP(x,y)LOOP(y,x) should go to LOOP(y,x)LOOP(x,y)  
        for i in range(len(intervals)):
            this_one_string=function_str[intervals[i][0]:intervals[i][1]]
            if function_name_of(this_one_string)=="LOOP":
                arguments=arguments_of(this_one_string)
                replacer_str="LOOP("
                for i in range(1,len(arguments)):
                    replacer_str += arguments[i]+","
                replacer_str += arguments[0]+")"
                replace_dict[this_one_string]=replacer_str
        last_key_index=0
        for replacement_key in replace_dict.keys():
            last_key_index=function_str.find(replacement_key,last_key_index) #necessary trick to avoid double shifting
            function_str=function_str[:last_key_index]+replace_dict[replacement_key]+function_str[last_key_index+len(replacement_key):] 
        return function_str

    #given a user inputted string, this returns a new string where all loops have taken one turn
    #NOTE this should be perfected so that it would allow useing cutting symbol inside of LOOP, not it produces an error
    def all_loops(self,function_str,cutting_symbol="|"):#SOMEWHAT TESTED
        array=function_str.split(cutting_symbol)
        result=""
        for com in array:
            result += self.loops_one_first(com)+ cutting_symbol
        result=result[:-(len(cutting_symbol))]
        return result

    #makes signs ^,*,/,+ and - to disappear replacing them be pow, prod, etc. and created AND-operators
    def math_rid(self,function_str): #SOMEWHAT TESTED
        function_str=add_missing_multiplication_signs(function_str)
        antti=AntiMather(function_str)
        return antti.function_str

    #every function_name from math, special and names of Functions added is listed here
    def list_of_all_function_names(self):#TESTED
        fn_list=self.math_function_names+self.special_function_names
        for x in self.function_list:
            fn_list += [x.name]
        return fn_list

    #list of names of the functions in self.function_list
    def function_list_names(self): #TESTED 
        fn_list=[]    
        for x in self.function_list:
            fn_list += [x.name]
        return fn_list

    #returns all the intervals of functions_with_arguments, possibly including multiplier
    def locate_one_function_string_intervals(self,function_str): #SOMEWHAT TESTED
        #add_to_call_counter("locate_one_function_string_intervals")
        intervals=[]
        par_pairs= parenthesis_pairs(function_str)
        interesting_trios=[]
        for pair in par_pairs:
            interesting_trios.append([pair[0],pair[0],pair[1]]) 
            #these trios are meant to represent indexes [starting position,(,)], thus we must move first index backwards
        for trio in interesting_trios:
            while is_nros_and_letters(function_str[trio[0]-1:trio[1]]) and trio[0]>0:
                trio[0]=trio[0]-1
        
        for trio in interesting_trios:
            if type_of(function_str[trio[0]:trio[2]+1]) in ["function_with_arguments","multiplied_function_with_arguments"]:
                intervals.append([trio[0],trio[2]+1])
        return intervals

    #taking a one_function_str returns the string for which it should be replaced for
    def one_function_replacer_str(self,one_function_str):
        name=function_name_of(one_function_str)
        if name not in self.list_of_all_function_names():
            return one_function_str
        if name in self.math_function_names:
            return self.math_assignment(one_function_str)
        if name in self.non_reducable_function_names:
            return one_function_str
        if name in self.function_list_names():
            return self.function_list_assignment(one_function_str)
        if name in ["AND","LOOP","QUOTE","INDEX"]:
            return one_function_str 
        if name in ["IF"]:
            return self.if_replacer(one_function_str)
 

    #if there is three parameters in one_function_str return last of the arguments if first two arguments are (possibly after processing)
    #same numbers, returns "" if they end up being different numbers, and returns original string, if at least one of them
        #isn't number.
    #if there are four arguments, then in case of first two argument being different numbers, thenm result is argument[3]
    # if they are the same, then argument 2 and if at least on of them is not a number, then return original string
    def if_replacer(self,one_function_str):
        name=function_name_of(one_function_str)
        arguments=arguments_of(one_function_str)
        if len(arguments)not in [3,4]:
            raise ValueError("There should be three arguments in if-clause")
        if one_function_str[:2]!= "IF":
            raise ValueError("We should be here only if this is IF-function")
        if arguments[0]==arguments[1]:
            return arguments[2]
        if is_real(arguments[0]) and is_real(arguments[1]):
            if abs(float(arguments[0])-float(arguments[1]))<0.00000001: #if we have two numbers close enough, we consider them the same
                return arguments[2] #otherwise for example 2.0 would be different to 2
            else:
                if len(arguments)==4: #user can input an optional fourth argument that tells what happens if condition if false
                    return arguments[3]
                else:
                    return "" #this happens, when we have reduced arguments to real numbers and thay still differ
            
        #it still might be that after other operations like assignment of variables it turns out that argumenta have same value
        return one_function_str #thus we just return the original string, if it is left after all processing, then main program
        #just ignores this function

    #given a string consisting of a math function and its arguments return the value of the function, if it can be calculated
    def math_assignment(self,one_function_str):
        vector_str=self.vector_operations(one_function_str)#if there are vectors to be summed, it is done here
        if vector_str!=one_function_str:
            return vector_str
        name=function_name_of(one_function_str)
        function_arguments=arguments_of(one_function_str)
        modified_function_arguments=[]
        for argument in function_arguments:
            mod_argument=argument
            while mod_argument[0]=="(" and mod_argument[-1]==")": #aded 21.1. to make possible to calculate for example prod(3,(-4)) ->-12
                if len(outest_comma_indexes(mod_argument[1:-1]))==0:#this is how we know it is not a vector
                    mod_argument=argument[1:-1]
            if is_real(mod_argument)==False:
                return one_function_str
            modified_function_arguments.append(mod_argument)
        if name not in self.math_function_names:
            raise ValueError("this is not a math function")
        
        value=0
        arguments_as_nros=[]
        for argument in modified_function_arguments:
            arguments_as_nros.append(float(argument))

        if name=="mod":
            value= arguments_as_nros[0]%arguments_as_nros[1]
        if name=="sum":
            value=sum(arguments_as_nros)
        if name=="minus":
            value=arguments_as_nros[0]-arguments_as_nros[1]
        if name in ["times","product","prod"]:
            value=1
            for argument in arguments_as_nros:
                value=value*argument
        if name in ["random"]:
            value=1
            #for argument in arguments_as_nros: OLD
            #    value=value*argument*random.random()
            if len(arguments_as_nros)==0:#e.g. random() returns value from interval (0,1)
                value=random.random()
            if len(arguments_as_nros)==1:#e.g. random(5) returns value from interval (0,5)
                value=value*arguments_as_nros[0]*random.random()
            if len(arguments_as_nros)==2:#e.g. random(-2,5) return value from interval (-2,5)
                value=value*(arguments_as_nros[1]-arguments_as_nros[0])*random.random()+arguments_as_nros[0]

        if name in ["divide","div"]:
            value=arguments_as_nros[0]/arguments_as_nros[1] #ZeroDivisionError is handled elsewhere

    
        if name== "sin":
            value=math.sin(arguments_as_nros[0])
        if name== "cos":
            value=math.cos(arguments_as_nros[0])
        if name== "tan":
            value=math.tan(arguments_as_nros[0])
    
        if name== "asin":
            value=math.asin(arguments_as_nros[0])
        if name== "acos":
            value=math.acos(arguments_as_nros[0])
        if name== "atan":
            value=math.atan(arguments_as_nros[0])
        
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

        if name == "min":
            value=min(arguments_as_nros)
        if name == "max":
            value=max(arguments_as_nros)

        value=value*function_multiplier(one_function_str) #for example in 3sum(2,4) multiplier is 3, and value without it 6, thus multiply
        return make_e_go_away(value) #this is a string, which doesn't contain exponents, absolute precision is 10^-20

    #we want to have more operations here, at least dot product
    def vector_operations(self,one_function_str):
        vector_str=vector_sum_str(one_function_str)
        if vector_str != one_function_str:
            return vector_str
        vector_str=dot_product_str(one_function_str)
        if vector_str != one_function_str:
            return vector_str
        vector_str=scalar_product_str(one_function_str)
        if vector_str != one_function_str:
            return vector_str
        return one_function_str

    #given a one_function_str this returns the string where function are assigned with arguments values
    #for example if neliö(x)=prod(x,x), then neliö(2)-> prod(2,2)
    def function_list_assignment(self,one_function_str):
        name=function_name_of(one_function_str)
        function_arguments=arguments_of(one_function_str)
        this_function=self.function_with_name(name)
        multiplier=function_multiplier(one_function_str)
        if multiplier== 1: #if there is a multiplier before the letter part of function name, it must be included
            multiplier=""
        return str(multiplier)+this_function.function_str_with_assigned_arguments(function_arguments)
        
        #KESKEN take this string which should have function with name in function_list_names() and assign this parameters using Function class 

    #given a name of function, this returns the Function-object with that name 
    def function_with_name(self,function_name):
        for func in self.function_list:
            if func.name==function_name:
                return func
        return None

    #aims to reduse function_str to simpler string using only "endpoint" functions which do not change anymore 
    def reduse(self,function_str):#some testing done
        new_function_str=self.reduse_step(function_str)
        while new_function_str != function_str:
            function_str=new_function_str
            new_function_str=self.reduse_step(function_str)
        return new_function_str


    def reduse_step(self,function_str):#some testing done        
        #add_to_call_counter("reduse_step")
        intervals=self.locate_one_function_string_intervals(function_str)
        possible_replacement_dict={}
        for i in range(len(intervals)):
            one_function_str=function_str[intervals[i][0]:intervals[i][1]]
            replacer_str=self.one_function_replacer_str(one_function_str)
            if replacer_str != one_function_str:
                possible_replacement_dict[one_function_str]=replacer_str
        for key in possible_replacement_dict.keys():
            if key[0:6]!="random":
                function_str=function_str.replace(key,possible_replacement_dict[key])
            if key[0:6]=="random":#if key is random..., then only one occurrance is replaced,this is to make random values chosen separately
                function_str=function_str.replace(key,possible_replacement_dict[key],1)
        return function_str

    #adds new variable to this database, it is not saved when program closes
    def add_variable(self,variable_name,variable_assignment_code):#SOME TESTING DONE
        if variable_name in self.reserved_names:
            return
        if type_of(variable_name)!="alpha_starter": 
            raise SyntaxError("Variable name is not ok")
        if is_syntax_ok(variable_assignment_code)==False:
            raise SyntaxError("assignment syntax fails")
        self.variable_dict[variable_name]=self.assign_variables_and_process(variable_assignment_code)

    #adds a function to the database
    def add_function(self,function):#SOME TESTING DONE
        self.function_list.append(function)
        if function.output_model_str_assign_part() == function.output_model_str_key_part():
            self.non_reducable_function_names.append(function.name)
        self.save_database_file()    

    #this allows adding a function to database (and memory txt-file) straight from model_str
    #model_str might consist of two or three parts, deoending of is specified_model_str given in the last part or not
    def add_function_from_output_model(self,model_str):
        if model_str[-1]=="|":
            model_str=model_str[:-1]
        if self.is_addable(model_str):
            new_function=self.construct_function_from_output_model(model_str)
            self.add_function(new_function)

    #give name of a function you want to remove from the database, it is removed if possible
    def remove_function_by_name(self,name):#TESTED
        user_added_function_names=self.function_list_names()
        if name not in user_added_function_names: #there is nothing to remove
            return "no such function: " +name
        function_to_remove=self.function_with_name(name) #this is not necessarily removed, only if it is possible
        parts=function_to_remove.output_model_str.split("==")
        if parts[0]==parts[1]: #this takes care that we don't remove functions like forward(x)=forward(x)
            return "can't remove basic function"
        #we then check if this function is used in other saved functions, then it can't be deleted
        for user_added_name in user_added_function_names: 
            if user_added_name != name and (name in self.function_with_name(user_added_name).output_model_str):
                return "you must remove at least function "+user_added_name+ " and perhaps other functions before removing "+name 
        self.function_list.remove(function_to_remove)
        self.save_database_file()
        return "removed "+name

    #this test can we add function described by output_model_str, it is possible only if key_part is 
    #function_with_arguments with arguments that are alpha_starters and
    #assign_part is syntactically ok, and contains only functions previously defined and variables given in the key_part
    #plus signs +,-,/,^,* and | and real_nros 
    def is_addable(self,model_str): #TESTED
        if model_str[-1]== "|":
            return False
        parts=model_str.split("==")
        for reserved in self.reserved_names: #no reserved name can be used as name or parameter name of function to be defined
            if reserved in parts[0]:
                return False
        if len(parts) not in [2,3]:
            return False
        if type_of(parts[0]) !="function_with_arguments": 
            return False
        if function_name_of(parts[0]) in self.list_of_all_function_names():
            return False
        parameters=arguments_of(parts[0])
        for par in parameters: #parameters must be alpha_starters, so they don't contain functions for example, not even numbers
            if is_alpha_starter(par)==False: #this leaves option that argument is some horrible thing like jkj3jo23
                return False 
        #key_part of output_model_str was ok let's now look assign part")
        if is_syntax_ok(parts[-1])==False:

            return False
        particles=list_of_particles(parts[-1])
        ok_names_list=self.list_of_all_function_names()
        ok_names_list += ["|","*","/","^","+","-",",","(",")","[","]"]
        ok_names_list += parameters
        ok_names_list += self.variable_dict.keys()
        for i in range(len(particles)):
            if (particles[i] in ok_names_list or is_pos_real(particles[i]))==False:
                return False
        return True

    #this puts self.non_reducable_function_names back in order
    def find_nonreducable_function_names(self):
        self.non_reducable_function_names=[]
        for function in self.function_list:
            if function.output_model_str_assign_part() == function.output_model_str_key_part():
                self.non_reducable_function_names.append(function.name)

    #saves current functions in the database file at machinery/function_database.txt
    def save_database_file(self):
        filetext=""
        for function in self.function_list:
            filetext += function.output_model_str + "=="+function.specified_assignment_str+"\n"
        save_text_file("machinery","function_database.txt",filetext)

    #returns a Function which is being constructed by this model_str. There are two possibilities
    #we migh have ginven strin like summa(x,y)=x+y with only one equal-sign, the specified_assignment_str, must be created by prosessing
    #or we might have given strin of type summa(x,y)=x+y=sum(x,y), now specified_assignment_str is just the last part, here "sum(x,y)""
    def construct_function_from_output_model(self,model_str):
        parts=model_str.split("==")
        function_name=function_name_of(parts[0])
        function_parameters=arguments_of(parts[0])
        this_function= Function(function_name,parameter_list=function_parameters,assignment_str=parts[1])
        if len(parts)==3: 
           this_function.specified_assignment_str=parts[2] 
        else:
            this_function.specified_assignment_str=self.assign_variables_and_process(parts[1]) #process... was changed to assign...
        return this_function





#gives vector components of string of type (x,y,z,w,...), raises error if it is not vector
#for example vector_components("(2,jojo,tyyppi(3),sipoo)") ->["2","jojo","tyyppi(3)","sipoo"]
#parenthesis type tells, which parenthesis 'enclose' the vector components
def vector_components(strin,parenthesis_type="()"):#TESTED
    if strin[0] != parenthesis_type[0] or strin[-1] != parenthesis_type[1]:
        raise SyntaxError("This is not a vector, you lied to us!")
    without_ends=strin[1:-1]
    comma_indexes=[0]+[x for x in outest_comma_indexes(without_ends)]+[len(without_ends)]
    vct_components=[without_ends[comma_indexes[0]:comma_indexes[1]]]
    for i in range(1,len(comma_indexes)-1):
        vct_components.append(without_ends[comma_indexes[i]+1:comma_indexes[i+1]])
    return vct_components

#this is meant to be used in occasion where we have just a number and we want to put parenthesis around it to make it
#look like it is a vector
def vectorise(strin,parenthesis_type="()"):
    result=strin
    if strin[0] != parenthesis_type[0] or strin[-1] != parenthesis_type[1]:
        result= parenthesis_type[0]+strin+parenthesis_type[1]
    if is_syntax_ok(result)==False:
        raise SyntaxError("It didn't vectorize, you lied to us!")
    return result


#if strin is a vector, and multi_index is just on number, this return vector component,
#for example let strin be matrix ((a,b),(c,d),(e,f)) and multi_index=[3,1] then 
#tensor_component([3,1],((a,b),(c,d),(e,f)) -> e. 
#if there is more multi_indexes than the rank of tensor represented by strin, then error is produces
def tensor_component(multi_index,strin,parenthesis_type="()"): #TESTED
    the_component=strin
    for i in range(len(multi_index)):
        the_component=vector_components(the_component,parenthesis_type)[multi_index[i]-1]
    return the_component

#this should be used cautiously since eg. in function_thing(2,3,4), (2,3,4) is not a vector
def is_it_a_vector(strin):
    if strin[0]=="(" and strin[-1]==")":
        return True
    return False

#given a string of type (a,b,c,...)+(e,f,g,...) or sum((a,b,c,...),(e,f,g,...)) returns a new string (sum(a,e),sum(b,f),...)
#this a sum of the vectors, NOTE if vectors are different lengths, this produces vector assuming that shorter vector
#has extra 0 components after its written components end
def vector_sum_str(function_str):#somewhat tested
    term_array=[]
    valid_term=False
    if count("+",function_str)==1:
        term_array=function_str.split("+")
        valid_term=True
    elif function_str[0:4]=="sum(" and function_str[-1]==")":
        arguments=arguments_of(function_str)
        if len(arguments)==2:
            term_array.append(arguments[0])
            term_array.append(arguments[1])
            valid_term=True
    if valid_term==False:
        return function_str
    if valid_term:
        if is_it_a_vector(term_array[0]) and is_it_a_vector(term_array[1]):
            v_comp1=vector_components(term_array[0])
            v_comp2=vector_components(term_array[1])
            new_component_str_array=[]
            for i in range(max(len(v_comp1),len(v_comp2))):
                sumterms=["0","0"]
                if i<len(v_comp1):
                    sumterms[0]=v_comp1[i]
                if i<len(v_comp2):
                    sumterms[1]=v_comp2[i]
                new_component_str_array.append("sum("+sumterms[0]+","+sumterms[1]+")")
            replacer_str="("
            for i in range(len(new_component_str_array)):
                replacer_str += new_component_str_array[i]+","
            replacer_str=replacer_str[:-1]+")"
            return replacer_str
    return function_str #if there was an argument that wasn't vector, we need to return the original str 

#if we have 'product' ie. dot product of two vectors given by function_str, then this calculates its form
#i.e. (2,3,4)*(4,5,6)->(prod(2,4)+prod(3,5)+prod(4,6)) we need to leave outer parenthesis and + symbols instead of sum
# so that rest of the stringprocessing is not disturbbed
def dot_product_str(function_str):#somewhat tested
    term_array=[]
    valid_term=False
    if count("*",function_str)==1:
        term_array=function_str.split("*")
        valid_term=True
    elif (function_str[0:5]=="prod(" or function_str[0:6]=="times(" or function_str[0:4]=="dot(") and function_str[-1]==")":
        arguments=arguments_of(function_str)
        if len(arguments)==2:
            term_array.append(arguments[0])
            term_array.append(arguments[1])
            valid_term=True
    if valid_term==False:
        return function_str
    if valid_term:
        if is_it_a_vector(term_array[0]) and is_it_a_vector(term_array[1]):
            v_comp1=vector_components(term_array[0])
            v_comp2=vector_components(term_array[1])
            if len(v_comp1)!=len(v_comp2): #if we don't do this (1,1)*(2,2)*(3,3) ->12 (this was tested)
                return function_str #thus we want to have same number of components in the product
            new_component_str_array=[]
            for i in range(max(len(v_comp1),len(v_comp2))):
                dotterms=["0","0"]
                if i<len(v_comp1):
                    dotterms[0]=v_comp1[i]
                if i<len(v_comp2):
                    dotterms[1]=v_comp2[i]
                new_component_str_array.append("prod("+dotterms[0]+","+dotterms[1]+")")
            replacer_str="("
            for i in range(len(new_component_str_array)):
                replacer_str += new_component_str_array[i]+"+"
            replacer_str=replacer_str[:-1]+")"
            return replacer_str
    return function_str #if there was an argument that wasn't vector, we need to return the original str 

#calculates scalar product string, for example '3*(aapo,4,5)'->(prod(3,aapo),prod(3,4),prod(3,5))
def scalar_product_str(one_function_str):
    term_array=[]
    valid_term=False
    if count("*",one_function_str)==1:
        term_array=one_function_str.split("*")
        valid_term=True
    elif (one_function_str[0:5]=="prod(" or one_function_str[0:6]=="times(" or one_function_str[0:8]=="product(" ) and one_function_str[-1]==")":
        arguments=arguments_of(one_function_str)
        if len(arguments)==2:
            term_array.append(arguments[0])
            term_array.append(arguments[1])
            valid_term=True
    if valid_term==False:
        return one_function_str

    if is_it_a_vector(term_array[1]) and is_real(term_array[0]) and valid_term:
        replacer_str="("
        v_comps=vector_components(term_array[1])
        for i in range(len(v_comps)):
            replacer_str += "prod("+term_array[0]+","+v_comps[i]+"),"
        replacer_str=replacer_str[:-1]+")"
        return replacer_str
    return one_function_str #if there was something wrong with arguments

def find_matching_parenthesis(strin:str,starting_location:int,parenthesis_type="()"): #TESTED
    counter=-1
    left_par=parenthesis_type[0]# this was changed, previously was just "("
    right_par=parenthesis_type[1]# and")""
    if strin[starting_location] != left_par:
        raise ValueError("No parenthesis at starting location")
    for i in range(starting_location+1,len(strin)):
        if strin[i]==left_par:
            counter = counter -1
        if strin[i]==right_par:
            counter = counter+1
        if counter==0:
            return i
    raise ValueError("There is no pair for the parenthesis")

#returns all the parenthesis pairs, for example parenthesis_pairs("joku()jok(())") -> [[4,5],[9,12],[10,11]]
#if there is no pair, returns string "syntax error"
def parenthesis_pairs(function_str):#TESTED
    if count("(",function_str)==0 and count(")",function_str)==0:
        return []
    if count("(",function_str) != count(")",function_str):
        return "syntax error"
    result=[]
    for i in range(len(function_str)):
        if function_str[i]=="(":
            try:
                result.append([i,find_matching_parenthesis(function_str,i)])
            except ValueError:
                return "syntax error"
    return result

#calculates indexes of smallest-length index_pair which includes index  
def smallest_wrap(function_str,index):#SOMEWHAT TESTED
    #add_to_call_counter("smallest_wrap")#for testing purposes only
    par_pairs=parenthesis_pairs(function_str)
    min_size=len(function_str)
    correct_pair=[0,len(function_str)]
    for pair in par_pairs:
        if pair[1]-pair[0]<min_size and index>=pair[0] and index <= pair[1]:
            min_size=pair[1]-pair[0]
            correct_pair=[pair[0],pair[1]+1] #+1 takes closing ")" in
    return correct_pair

#returns True, if syntax of function_str is without problems in the usage of parenthesis, this might need updates later
def is_parenthesis_syntax_ok(function_str): #TESTED
    par_charge=0 #"parenthesis charge" so how many parentheis there are
    for i in range(len(function_str)):
        if function_str[i]=="(":
            par_charge += 1
        if function_str[i]==")":
            par_charge += -1
        if par_charge<0:
            return False
    if par_charge!=0:
        return False
    return True

#test if string has problems with syntax
def is_syntax_ok(function_str):
    #if function_str=="":
    #    return True
    #add_to_call_counter("is_syntax_ok")
    if is_parenthesis_syntax_ok(function_str)==False:
        return False
    if function_str[0]==",":
        return False
    if len(function_str)>0:
        if function_str[-1] in ["+","*","/","*","^",",","("]:
            return False
    #later add more conditions for syntax
    return True



def load_file(file_path):
    _, file_extension = file_path.split('.', 1)
    file_extension = file_extension.lower()

    if file_extension == 'csv':
        with open(file_path, 'r', newline='', encoding='utf-8-sig') as file:
            csv_reader = csv.reader(file, delimiter=';')
            data_tuple = tuple(tuple(cell.strip() for cell in row) for row in csv_reader)
            return data_tuple

    elif file_extension in ['xlsx', 'xls']:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        data_tuple = tuple(tuple(cell.value for cell in row) for row in sheet.iter_rows())
        return data_tuple
    else:
        print(f"Unsupported file type: {file_extension}")

def load_file_dialog():
    file_path = filedialog.askopenfilename(title="Select File", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx;*.xls")])
    if file_path:
        tuple_thing=load_file(file_path)
        string_to_return="(("
        for thing in tuple_thing:
            for item in thing:
                string_to_return+= item.strip("'")+","
            string_to_return=string_to_return[:-1]+"),("
        string_to_return=string_to_return[:-2]+")"
        return string_to_return







#count nro of substrings
def count(substr,strin): #TESTED
    num = 0
    for i in range(len(strin)):
        if strin[i:i+len(substr)] == substr:
            num += 1
    return num

# returns the start and end indexes containing starting_index and being the maximal interval of substrings 
#containing only letters and numerals, including . and but not ,
# this is chosen that if pair=alfanum_str_interval(strin,starting_index) then strin[pair[0]:pair[1]] gives this maximal string
def alfanum_str_interval(strin,starting_index): #TESTED #after testing" " option added in the first if
    #add_to_call_counter("alfanum_str_interval")
    if is_nro_symbol_sequence(strin[starting_index])==False and strin[starting_index].isalpha()==False and strin[starting_index]!=" ":
        raise IndexError("Chosen index is doesn't correspond number or letter")
    start_index=max(starting_index,1) #we do not want to ask what is strin[-1], thus we set start_index at least 1
    end_index=starting_index
    while (is_nro_symbol_sequence(strin[max(start_index-1,0)]) or strin[max(start_index-1,0)].isalpha() or strin[max(start_index-1,0)]==" ") and start_index>0: #-1 since there is -1 perfomed in loop
        start_index= start_index-1 
    while (is_nro_symbol_sequence(strin[min(end_index,len(strin)-1)]) or strin[min(end_index,len(strin)-1)].isalpha() or strin[min(end_index,len(strin)-1)]==" ")  and end_index<len(strin):
        end_index= end_index+1
    return [start_index,end_index] 

#takes a string, and cuts its to peaces so that each piece is either a number or name or symbol of length 1 like ")" or ","
# for example sum,(prod(4),3|sum(2,3)) -> ['sum',',','(','prod','(','4',')',',','3','|','sum','(','2',',','3',')',')']
def list_of_particles(strin):#TESTED
    #add_to_call_counter("list_of_particles")
    running_index=0
    particles=[]
    while running_index<len(strin):
        pair=[running_index,running_index+1]
        try:
            pair=alfanum_str_interval(strin,running_index)
        except IndexError:
            pair=[running_index,running_index+1]
        running_index=pair[1]
        particles.append(strin[pair[0]:pair[1]])
    return particles
        
#given string and index on it, this return the information about in which particle we are.
#for example ("joku(3,15)|sin(x)",7) -> 4 since particles=["joku", "(", "3", ",", "15",...] and "joku(3,15)|sin(x)"[7]=1 which 
#is part of the 4th term in particles
def particle_nro_of_index(strin,index):#TESTED
    if index not in range(len(strin)):
        raise IndexError("there is no such index in the string")
    particles=list_of_particles(strin)
    particle_nro=0
    running_index=0
    for i in range(len(particles)):
        running_index += len(particles[particle_nro])
        if index<running_index:
            return particle_nro
        particle_nro += 1
    return particle_nro

#given strin and index, tells what are the start and end indexes of strin of indexth particle
#for example ("forward(4)|move(2,3,4,5)",5) -> [11,15] since "move" is the 5th particles, and it starts at 11 index and ends at 15th index
def interval_of_particle_nro(strin,particle_index):#TESTED
    particles=list_of_particles(strin)
    if particle_index not in range(len(strin)):
        raise IndexError("there is no such index in the string")
    start_index=0
    end_index=0
    for i in range(0,particle_index+1):
        start_index=end_index
        end_index += len(particles[i])
    return [start_index,end_index]

#returns True if it is a number, works for single char like "a"->False, "3"->True or string of chars
#returns True also for fake numbers like "." and "4.3..566" which have extra dots
def is_nro_symbol_sequence(strin): #TESTED
    #add_to_call_counter("is_nro_symbol_sequence")
    for cha in strin:
        if cha not in ["0","1","2","3","4","5","6","7","8","9","."]:
            return False
    return True

#for technical reason we had to had is_nro_symbol"." True 
def is_pos_real(strin):#TESTED
    if is_nro_symbol_sequence(strin)==False or count(".",strin)>1 or strin==".":
        return False
    return True 

#allowing also negative numbers or one + sign before number
def is_real(strin):#TESTED
    if is_pos_real(strin):
        return True
    if strin[0] in["-","+"] and is_pos_real(strin[1:]):
        return True
    return False 

#does string consist of numbers and letters (may contain unlimited number of '.' also)
def is_nros_and_letters(strin):#TESTED
    for cha in strin:
        if is_nro_symbol_sequence(cha)==False and cha.isalpha()==False and cha != " ": #" " option added 19.1 hope it doensn't break anything
            return False
    return True 

#does string consist only of letters
def is_pure_alpha(strin):#TESTED
    for cha in strin:
        if cha.isalpha()==False:
            return False
    return True

#this is true if string has only letters and possibly after that numbers after which no symbols at all
def is_alpha_starter(strin):#TESTED
    if len(strin)==0:
        return False
    if is_nros_and_letters(strin)==False:
        return False
    if is_pure_alpha(strin[0])==False: #strin must start with at least one alpha
        return False

    bets_are_off=False
    for cha in strin:
        if cha.isalpha()==False and cha!=" ": #i.e. it is a number, " " option added 20.1
            bets_are_off=True
        if bets_are_off and cha.isalpha():
            return False
    return True
        
    
#this is true if string has only numbers (possibly 0) following letters and then numbers (possibly 0)and not a single letter after that
#for example 345sin4, sin4 and sin are all True but 345 for example is not and sin35cos234 is not since there are numbers in the middle
def is_multiplied_alpha_starter(strin):#TESTED
    if is_nros_and_letters(strin)==False:
        return False
    bets_are_off=False
    for i in range(len(strin)):
        if strin[i].isalpha():
            return is_alpha_starter(strin[i:])
    return False #in this case there where only numbers


#returns the indexes of commas not inside parenthesis, for example 345,43,34,2 ->[0,3,6,9,11] and (32,23,4223,2) -> [] 
#and 23,(453,45),23 ->[2,11]
def outest_comma_indexes(strin): #TESTED
    if is_parenthesis_syntax_ok(strin)==False:
        return "syntax error"
    result_indexes=[]

    par_charge=0 #"parenthesis charge" so how many parentheis there are
    for i in range(len(strin)):
        if strin[i]=="(":
            par_charge += 1
        if strin[i]==")":
            par_charge += -1
        if par_charge==0 and strin[i]==",":
            result_indexes.append(i)
    return result_indexes


#this returns type of string, options are syntax error, number, alpha_starter, multiplied_alpha_starter, index
#function_with_arguments, multiplied_function_with_arguments and unholy_mess
#number is just number like "3.4" or "217"
# alpha_starter is name starting with letter possibly ending with number like "ymp2"
# multiplied_alpha_starter is like alpha_starter but starting with number, e.g. "13.5ymp2"
#index is [something]
#function_with_arguments is of the format alpha_starter(arguments) like "hauskaluku2(13,4,ketsuppi)"
#multiplied function_with_arguments is of the format multiplied_alpha_starter(arguments) like "18988hauskaluku2(13,sinappi,ketsuppi)"
#unholy_mess is the thing falling out of these categories like "forward(4)|pircle(3)" or "43a56bg"
def type_of(strin):#TESTED
    #add_to_call_counter("typeof")
    if is_syntax_ok(strin)==False:
        return "syntax error"
    particles=list_of_particles(strin)
    #OPtions function_name, multiplied_function_name,variable_name, number, function_with_parameters,
    if len(particles)==1:
        if is_pos_real(particles[0]):
            return "pos_real"
        if is_alpha_starter(particles[0]):
            return "alpha_starter"
        if is_multiplied_alpha_starter(particles[0]):
            return "multiplied_alpha_starter"
        if particles[0] in ["+","-","^","*","/"]:
            return "sign"
        else:
            return "unholy_mess"
    if len(particles)>1:
        if strin[0]=="[" and strin[-1]=="]":
            return "index"
        if strin[len(particles[0])] != "(":
            return "unholy_mess"
        if find_matching_parenthesis(strin,len(particles[0]))!=len(strin)-1:
            return "unholy_mess"  
        #if we have got this far, it means we have strin of type substr(stuff), 
            #where marked parentheses match
        elif is_alpha_starter(particles[0]): 
            return "function_with_arguments"
        elif is_multiplied_alpha_starter(particles[0]):
            return "multiplied_function_with_arguments"
        else:
            return "unholy_mess"     

#given a function_str and index, returns the interval for smallest term containing this index
def smallest_complete_term_interval(function_str,starting_index): #SOMEWHAT TESTED,
    # might need improvement, for example (jok(2),jok(3)) with starting index at "," would choose semantical unit jok(2), which is stupid
    #add_to_call_counter("smallest_complete_term_interval")#for testing purposes only
    if is_syntax_ok(function_str)==False:
        raise SyntaxError("syntax failed")
    if function_str[0]=="(" and starting_index==0:
        return smallest_wrap(function_str,0)
    particles=list_of_particles(function_str)
    this_particle_nro=particle_nro_of_index(function_str,starting_index) #how manyth particle this is
    this_particle=particles[this_particle_nro] #of what substring this particle consists of
    this_particle_type=type_of(this_particle) #what type of string this particle is
    this_particle_interval=interval_of_particle_nro(function_str,this_particle_nro) #what are the start and end indexes of this particle
    if this_particle_type == "sign": #this is a bug fix try, let's see if it handles issue with - signs
        parenthesis_interval=smallest_wrap(function_str,starting_index)
        if parenthesis_interval[0] != 0:
            return smallest_complete_term_interval(function_str,max(0,parenthesis_interval[0]))

    if this_particle== "=": #bug fix, if we ask smallest term containing = we must give some answer
        return smallest_wrap(function_str,starting_index)

    if this_particle=="[":
        if type_of(particles[this_particle_nro-1]) not in ["alpha_starter"]: #this happens 
            #when starting_index starts manydimensional parameter for example (23,45,12)
            return [starting_index,find_matching_parenthesis(function_str,starting_index,"[]")+1]

    if this_particle_type == "unholy_mess":
        raise SyntaxError("You have created a monster, repent and fix the syntax")
    
    if this_particle_type in ["multiplied_alpha_starter","alpha_starter","pos_real"]:
        if this_particle_nro>=len(particles)-1: #if it is the last particle, and it is also a alpha_starter, then it must be meaningful term
            return this_particle_interval
        if particles[this_particle_nro+1]=="(":
            opening_par_index=interval_of_particle_nro(function_str,this_particle_nro+1)[0]
            closing_par_index=find_matching_parenthesis(function_str,opening_par_index)
            return [this_particle_interval[0],closing_par_index+1]
        if particles[this_particle_nro+1] !="(":
            return this_particle_interval

    if this_particle==",":
        parenthesis_interval=smallest_wrap(function_str,starting_index)
        return smallest_complete_term_interval(function_str,max(0,parenthesis_interval[0]))

    if this_particle=="(":
        if type_of(particles[this_particle_nro-1]) not in ["alpha_starter"]: #this happens 
            #when starting_index starts manydimensional parameter for example (23,45,12)
            return [starting_index,find_matching_parenthesis(function_str,starting_index)+1]
        else:#this gets the function name included
            return smallest_complete_term_interval(function_str,max(0,starting_index-1))
    if this_particle==")":#reverts back to finding the term-interval related to the opening_index of matching "("
        parenthesis_interval=smallest_wrap(function_str,starting_index)
        return smallest_complete_term_interval(function_str,max(0,parenthesis_interval[0]))



    return [0,len(function_str)]#if everything else fails

#given a function_str, returns a smallest term, that index is contained of 
def term_in_index(function_str,index):#SOMEWHAT TESTED
    this_term_interval=smallest_complete_term_interval(function_str,index)
    this_term=function_str[this_term_interval[0]:this_term_interval[1]]
    return this_term

def list_arguments_of_function_in_index(function_str,index):#SOMEWHAT TESTED
    if index not in range(0,len(function_str)):
        raise IndexError("this index is not in the function_str")
    this_term=term_in_index(function_str,index)
    return arguments_of(this_term)
    
#given a string that just contains function, with arguments, returns it arguments. This doesn't work if the string isn't function
def arguments_of(one_function_str):
    if type_of(one_function_str) not in ["function_with_arguments","multiplied_function_with_arguments"]:
        raise SyntaxError("this string ain't seen no function, you failed")
    argument_start=one_function_str.find("(")
    argument_end=find_matching_parenthesis(one_function_str,argument_start)
    if one_function_str[argument_start+1:argument_end].strip()=="": #if one_function_str is type name(), then there is no arguments
        return []
    argument_part_without_pars=one_function_str[argument_start+1:argument_end]
    cutting_indexes= [argument_start] + [x +argument_start +1 for x in outest_comma_indexes(argument_part_without_pars)]+ [argument_end]
    #these were the locations that separate the arguments
    arguments=[]
    for i in range(len(cutting_indexes)-1):
        arguments.append(one_function_str[cutting_indexes[i]+1:cutting_indexes[i+1]].lstrip())        
    return arguments

#returns the name of the function in this string which must be comprised of one function_with its arguments, to make sense
#note that if there is a multiplier before the name, it is no included into the returned name
def function_name_of(one_function_str):
    if type_of(one_function_str) not in ["function_with_arguments","multiplied_function_with_arguments"]:
        raise SyntaxError("this string ain't seen no function, you failed")
    particles=list_of_particles(one_function_str)
    if type_of(particles[0])=="function_with_arguments": #this means that there is now multiplication before function e.g.23sin(4x)
        return particles[0]
    else:
        for i in range(len(one_function_str)):
            if is_pure_alpha(one_function_str[i]):
                return one_function_str[i:one_function_str.find("(")]


#returns the multiplicator of the function in this string as an int 
#this string must be comprised of one function_with its arguments, to make sense         
def function_multiplier(one_function_str):
    if type_of(one_function_str) not in ["function_with_arguments","multiplied_function_with_arguments"]:
        raise SyntaxError("this string ain't seen no function, you failed")
    particles=list_of_particles(one_function_str)
    if type_of(one_function_str)=="function_with_arguments": #this means that there is now multiplication before function e.g.23sin(4x)
        return 1 #multiplicator is 1 if there isn't any
    else:
        for i in range(len(one_function_str)): #when first letter is found this thinks that rest before is number
            if is_pure_alpha(one_function_str[i]):
                return float(one_function_str[:i])

#adds multiplication signs between any number-letter pair if they are in this order, with one exception, 
#if there is '^' before number, then '*' is not added, since exponentation must come first
#* is also added between ')' and another symbol except ")" or ","
# here are the cases to add * in the place of. number.(something), something).something   
def add_missing_multiplication_signs(function_str):
    add_indexes=[]
    for i in range(len(function_str)-1):
        cond1= is_pos_real(function_str[i])
        cond2= is_pure_alpha(function_str[i+1]) or function_str[i+1]=="("
        cond3= function_str[i]==")"
        cond4= is_pos_real(function_str[i+1]) or is_pure_alpha(function_str[i+1]) or function_str[i+1]=="("
        if (cond1 and cond2) or (cond3 and cond4):
            add_indexes.append(i)
     #we still need make sure that we don't add extra * in wrong places like in function2(x) we do not want to have function2*(x)
    final_indexes=[]
    particles=list_of_particles(function_str)
    for index in add_indexes:
        this_particle_nro=particle_nro_of_index(function_str,index) #how manyth particle this is
        this_particle=particles[this_particle_nro] #of what substring this particle consists of
        if type_of(this_particle)!= "alpha_starter":
            final_indexes.append(index)
    
    size=len(final_indexes)
    if size==0:
        return function_str
    result_str=function_str[:final_indexes[0]+1]
    for i in range(1,size):
        result_str += "*"+function_str[final_indexes[i-1]+1:final_indexes[i]+1] 
    result_str += "*"+function_str[final_indexes[-1]+1:]
    
    return result_str

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

#there are issues in making  e.g. "2.0" to int, this should make it happen
def make_it_int(thing):
    result=-345
    try:
        int(thing)
        return thing
    except ValueError:
        if is_nro_symbol_sequence(thing):
            whole_part=int(thing.split(".")[0])
            if whole_part=="":
                return 0
            return whole_part

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
#first parameter should be just one_fnction_str, 
#second parameter tells, in which format we want to return the parameters of one_function_str
#options are "str" "int" and "float"
def arguments_in_type(one_function_str,return_type="str"):
    arguments=[]
    if type_of(one_function_str)=="function_with_arguments":
        arguments=arguments_of(one_function_str)
        if return_type=="str":
            return arguments
        are_real_numbers=True #this will be true if all arguments are real numbers
        for arg in arguments:
            if is_real(arg)==False:
                are_real_numbers= False
        float_arguments=[] #these two will be left empty
        int_arguments=[] #if all are arguments are not numbers
        if are_real_numbers:
            for arg in arguments:
                float_arguments.append(float(arg))
                int_arguments.append(int(float(arg)))
        if return_type=="float": 
            return float_arguments
        if return_type=="int":
            return int_arguments

#given a float number, returns a string describing it without using exponent notation
def make_e_go_away(number:float,max_nro_of_decimals=16):#TESTED
    exponent=int(math.log10(max(abs(number),0.000000001))) #we can't let zero value in because exponent would go to minus infinity
    format_constant=max(min(max_nro_of_decimals,-exponent+10),1)
    return "{0:.{field_size}f}".format(number,field_size=format_constant)

#returns a power of ten which is smallest power of then that is greater than the number
def next_exponent_of_ten(number:float): #DOESTN WORK YET FOR EXAMPLE 0.7
    powers=int(math.log10(abs(number)))
    if number>=0:
        if number<=1:
            return math.pow(1/10,-powers)
        else:           
            return round(math.pow(10,powers+1))
    else:
        if number<-1:
            return -round(math.pow(10,powers+1))
        else:
            return -math.pow(10,powers)
    
#given a float number returns string which is cut when there are two many consecutive zeros after point
def zero_cut_string(number,max_nro_of_zeros=0,max_nro_of_decimals=13):
    number= number*(1.00000000001) # this slimy trick is meant to for example change 0.0499999999 to 0.0500000....
    string_nro=make_e_go_away(number,max_nro_of_decimals)

    consecutive_zeros=0
    activated=False
    cut_index=0
    start_index=0
    if string_nro[0]=="-":
        start_index=1
    for i in range(start_index,len(string_nro)):
        cut_index=i
        if string_nro[i]=="0":
            consecutive_zeros += 1
        elif string_nro[i] in [".","-"]: #if it is not 0 or . we end up cutting consecutive zero streak
            activated=True
            consecutive_zeros=0
        if consecutive_zeros>max_nro_of_zeros and activated:
            break
    
    dot_index=string_nro.find(".")
    if dot_index==-1:#this was integer
        return string_nro[:cut_index]+(len(string_nro)-cut_index)*"0"
    if dot_index>cut_index:
        return (string_nro[:cut_index]+(dot_index-cut_index)*"0").rstrip(".")
    if activated==False: #there wasn't any nonzero numbers
        return string_nro.rstrip("0").rstrip(".")
    else:
        return (string_nro[:cut_index]).rstrip("0").rstrip(".")

#for testing purposes
def add_to_call_counter(functionname):
    global call_dict
    if functionname not in call_dict.keys():
        call_dict[functionname]=1
    else:
        call_dict[functionname]=call_dict[functionname]+1 

#for testing purposes
def zero_the_counter():
    global call_dict
    call_dict={}

def speed_test():
    zero_the_counter()
    db=FunctionDatabase()
    for x in range(1,10):
        print(db.process_all("mod(2,"+str(x)+")mod(3,"+str(x)+")mod(5,"+str(x)+")mod(7,"+str(x)+")mod(11,"+str(x)+")"))
    print("call_counter",call_dict)

def speed_test2():
    zero_the_counter()
    print("start")
    for x in range(1,1000):
        antti=AntiMather(str(x)+"*("+str(x)+"+1)*("+str(x)+"+2)*("+str(x)+"+3)")
        #print(antti.function_str)
    print("call_counter",call_dict)
    print("done")
        

#given number, this tells what we should multiply it to get the smallest 10^n, which is larger than number and n is an integer 
def multiplier_to_next_exponent_of_ten(number):
    exponent=math.log10(max(abs(number),0.000000001)) #we can't let zero value in because exponent would go to minus infinity
    return math.pow(10,1-exponent+math.floor(exponent))

if __name__ == "__main__":
    random_things=["jok","345","235.734","vefvoj2","sdvsdv()","sdff(,23,sdf,3)","df()ewff()wef((we))","sdv(23,23(ewf))","sdffd4*evrve"]
    random_things +=["3*.4","e*sum(2,4x)","ln(e(2))","))45..5gorgm,er,990((","hi,hij|jo,jlik(","svv|forwar(23)","|erg|forwar()","forward(3)|sum(3"]
    random_things +=["sum,(prod(4),3|sum(2,3))","34.5+234/4","2*3*vefvoj2","gd()vsdv()","||ewgs-dff(,23,sdf,3)","4df(4)ewff(4)","sdv(sum(we.er))"]
    random_things +=[")93*.4","e))*sum(2,4x)","gln,(e**(2))","))","75,..,5gdwrgm,er,990((",")krihj|jo|kk","jirwa()|svv|forwar(23)"]
    random_things +=["3,4,5","onko(4),onko(5),onko(6,7)",".3454646","34.34.,234.4,34,778","3.a.4.5b6c","455hoh()","1.34jau3saa4(345)"]
    random_things +=[",3,4,5","(,(5,4,))",",jep(6,7),","(,994.346,)","(34,34,877)","34,34,877"]

    #speed_test2() #mennyt noin 6.4 sekuntia
    #cspeed_test()

    print("tensor stuff",tensor_component([1,3,1],"(((a,b),(c,d),(e,f)),((1,2,3),(4,5),(6,7,8)))" ))

    a=0.001*0.0001+7656
    print("normal:",a)
    b="{0:.12f}".format(a)
    print("new:",b)

    #load_file_dialog()


    antti=AntiMather("5")
    print("index_value_step",antti.indexvalue_step("INDEX((2,1),((1,2,3),(4,5,6)))"))

    print(antti.double_parenthesis_off("(3)*(2,4)"))
    #for thing in random_things:
    #    for i in range(1):#len(thing)):
    #        print(thing)
    #        try:
    #            antti=AntiMather(thing)
    #            print("thing",thing,antti.function_str)
    #        except IndexError:
    #            print("Not")
    #        except SyntaxError:
    #            print("syntax failed")
    print("minus still brings problems as in binomi(2,-3)", "it is hard to avoid *- combination")
    print("INDEX argumentti ei tunnista indexiä 2.0 vaikka tunnistaa 2:n ts. INDEX(2.0,(a,b)) ei tee mitään vaikka INDEX(2,(a,b)) toimii")
    print("jotenkin on liityttävä inttisyyteen")
    print(random.random())
    print("muista testata jossain vaiheessa, että jos funktion parametreissä on esim x ja x2, niin eihän x2:n paikalle korvata x:n argumenttia")

    print("zero cut:",zero_cut_string(0.5,max_nro_of_zeros=0))
    db= FunctionDatabase()

    print(db.assign_variables_and_process("(random(1),random(1))"))

    while True:
        add_or_remove=input("0 to remove, 1 to add function, 2 to process,  3 to add_variable, 4 to display info, 5 ass and pro, 6 everything, 7 type_of: ")
        if add_or_remove=="0":
            name=str(input("give a name of a function: "))
            db.remove_function_by_name(name)
        if add_or_remove=="1":
            output_model_str=str(input("give an output_model_str: "))
            antti=AntiMather(output_model_str.split("==")[1])
            improved_output_model=output_model_str.split("=")[0]+"=="+antti.function_str
            print("improved:")
            print(improved_output_model)
            db.add_function_from_output_model(improved_output_model)
        if add_or_remove=="2":
            function_str=str(input("string to process: "))
            print(db.process_function_str(function_str))
        if add_or_remove=="3":
            function_str=str(input("new variable instruction: "))
            variable_name=function_str.split("=")[0]
            variable_assignment_code=function_str.split("=")[1]
            db.add_variable(variable_name,variable_assignment_code)
        if add_or_remove=="4":
            db.display_database()
        if add_or_remove=="5":
            function_str=str(input("string to assign and process: "))
            print(db.assign_variables_and_process(function_str))
        if add_or_remove=="6":
            total_function_str=str(input("string to make it all: "))
            print(db.process_all(total_function_str))
        if add_or_remove=="7":
            strin=str(input("the string of which type you want to know:"))
            print("list of particles:",list_of_particles(strin),"type: ",type_of(strin))
            print("is_nros_and_letters",is_nros_and_letters(strin))
        if add_or_remove=="8":
            strin=str(input("the string of which you want to loop first:"))
            print(db.all_loops(strin,"|"))
        if add_or_remove=="9":
            number=float(input("the number to be multiplied by 0.1:"))
            print(make_e_go_away(number*0.1))



    while True:
        strin=str(input("give a function name: "))
        assignment_str=input("give an assignement str: ")
        jaakko=Function(strin,parameter_list=["x","y"],assignment_str=assignment_str)
        print("this name",jaakko.name)
        print("adding signs",add_missing_multiplication_signs(assignment_str))
        arguments=[]
        new_argument=""
        while new_argument!="-1":
            new_argument=input("give an index, -1 stops: ")
            try:
                if new_argument != "-1":
                    arguments.append(new_argument)
            except SyntaxError:
                print("you created a syntax error, no worry, it happens")
        db.add_function(jaakko)
        assign_str=jaakko.function_str_with_assigned_arguments(arguments)
        print(assign_str)
        math_rid_str=db.math_rid(function_str=assign_str)
        print("after math rid",math_rid_str)
        db.display_database()
        print("all function intervals",db.locate_one_function_string_intervals(math_rid_str))
        print(db.one_function_replacer_str(math_rid_str))
        print(db.process_function_str(assign_str))

    list_of_functions=[term_in_index,list_arguments_of_function_in_index]
    list_to_str_repr=""
    for i in range(len(list_of_functions)):
        list_to_str_repr += str(i)+ ": "+list_of_functions[i].__name__+", "

    function=list_of_functions[int(input("which function: "+list_to_str_repr))]
    while True:
        index=0
        strin=input("give a string: ")
        while index>=0:
            index=int(input("give an index, -1 stops: "))
            try:
                print(function(strin,index))
            except SyntaxError:
                print("you created a syntax error, no worry, it happens")



    #print("what to do next:")
    #print("function saving structure: consisting of saving code given by user and a way to make modified version used behind the scenes")
    #print("function to assign arguments to this function to create a new string")
    #print("AntiMather function")
    #print("class to insert functions by their given instructions, this class should be able to modify given")
    #print("function string to reduced tt, using only math_functions and basic functions")
    #print("class to save variables")
    #print("in the end user should be able to write a function and give variables (not permanently saved) so that behind the scenes")
    #print("this project turns this to a set of basic commands like forward(4) which are then executed in the 'main-method' of")
    #print("Kuhan piirrän. Even math methods should disappear (their values should be calculated)")
    #math_things=["3+4","5*6","7/8","9-10"]
    #math_things=["3+-+4","5^6(7/8+-7*5--3*(+3))"]
    #for thing in math_things:
    #    antti=AntiMather(thing)
    #    print(antti.function_str)

    #pentti=AntiMather("3")
    #print(pentti.no_signs_after_parenthesis_step("(3*(-4^(-6)))"))
                
        