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
import numpy as np
from matplotlib.path import Path
import Geometry
import json
from os import path
import math


SAMEPOINTLIMIT=0.00001


class Conditions:
    backgound_light=(1,1,1) #amount of light in r,g,b, 
    vector_lights=[] #vector light is of the form [(direction),(rgb-brightness1),(direction),(rgb-brightness1),..]
    def __init__(self,background_light,vector_lights):
        self.backgound_light=background_light
        self.vector_lights=vector_lights

    @classmethod
    def from_dict(cls, param_dict):
        """Create a TransformationParameters object from a dictionary."""
        # Extract values from the dictionary or use default if not provided
        background_light = param_dict.get('background_light', (1, 1, 1))
        vector_lights = param_dict.get('vector_lights', [])

        # Return an instance of TransformationParameters
        return cls(background_light, vector_lights)



    #thi
    def total_light_on_surface_without_shading(self,surface_normal_vector):
        total_light=self.backgound_light
        for vector_light in self.vector_lights:
            scalar_intensity = np.dot(surface_normal_vector, vector_light[0]) #vector_light[0] is light direction
            total_light+=np.dot(scalar_intensity,vector_light[1]) #vector_light[1] is the rgb vector, NOTE! this can be more than 1 component wise
        return total_light

    #static color is the color of polygon Or line in "normal" color conditions, face_material decides how much 
    #is reflected and surface_normal_vector affects also.
    def color_in_lightning(self,static_color,reflectivity,surface_normal_vector):
        total_light=self.total_light_on_surface_without_shading(surface_normal_vector)
        hc=(static_color[0]*reflectivity[0]*total_light[0],
                              static_color[1]*reflectivity[1]*total_light[1],
                              static_color[2]*reflectivity[2]*total_light[2])

        result= (max(0,1-math.exp(-hc[0])),max(0,1-math.exp(-hc[1])),max(0,1-math.exp(-hc[2])))
        if result[0]>1 or result[1]>1 or result[2]>1:
            print("STRANGE",result)

        return result
    
class FaceMaterial:
    property_dict={}
    reflectivity=(1,1,1)#this describes amounts of red, green and, blue light that material reflects. 
    #Larger values make the object seem brighter
    name="plastic"
    def __init__(self,property_dict):
        self.property_dict=property_dict
        self.name=self.property_dict.get("name","plastic")
        self.reflectivity=self.property_dict.get("reflectivity",(1,1,1))


    def to_dict(self):
        return self.property_dict


class TransformationParameters:
    def __init__(self, mass_center=(0, 0, 0), south_north_vector=(0, 1, 0),
                 greenwich_vector=(1, 0, 0), south_north_rotation=0,
                 greenwich_rotation=0, shift_vector=(0, 0, 0)):
        self.mass_center = mass_center
        self.south_north_vector = south_north_vector
        self.greenwich_vector = greenwich_vector
        self.south_north_rotation = south_north_rotation
        self.greenwich_rotation = greenwich_rotation
        self.shift_vector = shift_vector

    @classmethod
    def from_dict(cls, param_dict):
        """Create a TransformationParameters object from a dictionary."""
        # Extract values from the dictionary or use default if not provided
        mass_center = param_dict.get('mass_center', (0, 0, 0))
        south_north_vector = param_dict.get('south_north_vector', (0, 1, 0))
        greenwich_vector = param_dict.get('greenwich_vector', (1, 0, 0))
        south_north_rotation = param_dict.get('south_north_rotation', 0)
        greenwich_rotation = param_dict.get('greenwich_rotation', 0)
        shift_vector = param_dict.get('shift_vector', (0, 0, 0))

        # Return an instance of TransformationParameters
        return cls(mass_center, south_north_vector, greenwich_vector,
                   south_north_rotation, greenwich_rotation, shift_vector)
    
    def to_dict(self):
        params_dict={}
        params_dict["mass_center"] = self.mass_center #, (0, 0, 0)
        params_dict["south_north_vector"] = self.south_north_vector #, (0, 1, 0)
        params_dict["greenwich_vector"] = self.greenwich_vector #, (1, 0, 0)
        params_dict["south_north_rotation"] = self.south_north_rotation #, 0)
        params_dict["greenwich_rotation"] = self.greenwich_rotation, #0)
        params_dict["shift_vector"] = self.shift_vector, #(0, 0, 0))
        return params_dict




# Define the golden ratio
phi = (1 + np.sqrt(5)) / 2

#normalize vector to length radius
def normalize(v, radius=1.0):
    return (v / np.linalg.norm(v)) * radius

# Define the vertices of an icosahedron
def create_icosahedron(radius=1.0):
    vertices = [
        [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
        [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
        [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1]
    ]
    # Normalize vertices to fit on a sphere with radius 
    vertices = [normalize(np.array(v), radius) for v in vertices]
    # Define the 20 faces of the icosahedron
    faces = [
        [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
        [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
        [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
        [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
    ]
    
    return np.array(vertices), faces

# Subdivide a triangle into four triangles
def subdivide(vertices, faces, subdivisions,radius):
    vertex_map = {}
    
    # Function to get the midpoint vertex index
    def get_midpoint(v1_idx, v2_idx):
        key = tuple(sorted((v1_idx, v2_idx)))  # Use tuple for dictionary key
        if key not in vertex_map:
            # Convert vertices back to NumPy arrays for arithmetic
            midpoint = normalize((np.array(vertices[v1_idx]) + np.array(vertices[v2_idx])) / 2.0, radius)
            vertex_map[key] = len(vertices)
            vertices.append(midpoint)
        return vertex_map[key]
    
    for _ in range(subdivisions):
        new_faces = []
        for tri in faces:
            v1, v2, v3 = tri
            a = get_midpoint(v1, v2)
            b = get_midpoint(v2, v3)
            c = get_midpoint(v3, v1)
            new_faces.extend([[v1, a, c], [v2, b, a], [v3, c, b], [a, b, c]])
        faces = new_faces
    return np.array(vertices), faces

# Main function to generate the sphere mesh
def generate_sphere(subdivisions,radius=1.0):
    vertices, faces = create_icosahedron(radius)
    vertices = vertices.tolist()  # Convert to list for appending
    vertices, faces = subdivide(vertices, faces, subdivisions,radius)
    return np.array(vertices), np.array(faces)


#precision_circle is a number of vertices in the edge or the cylinder
#precision_side is side_length/face_length, ie. how many joined triangles is needed from one circle to other
def generate_cylinder(height,radius,precision_circle,precision_side):
    vertices=[]
    for j in range(precision_side+1):
        for i in range(precision_circle):
            zcor1=height/2-height*(j/precision_side)/2
            p1=[radius*math.cos(i*2*math.pi/precision_circle),radius*math.sin(i*2*math.pi/precision_circle),zcor1]
            vertices.append(p1)
        

    # Define the 20 faces of the icosahedron
    faces=[]
    for j in range(precision_side):
        for i in range(precision_circle-1):
            faces.append([j*precision_circle+i,(j+1)*precision_circle+i,j*precision_circle+i+1])
            faces.append([(j+1)*precision_circle+i,(j+1)*precision_circle+i+1,j*precision_circle+i+1])
        faces.append([(j+1)*precision_circle-1,(j+2)*precision_circle-1,j*precision_circle])
        faces.append([(j+2)*precision_circle-1,(j+1)*precision_circle,j*precision_circle])
    
    return np.array(vertices), faces


def generate_circle(center, radius, normal_vector, precision):
    # Muutetaan center NumPy-vektoriksi
    center = np.array(center)
    vertices = [center]
    
    # Normalisoidaan normal_vector
    normal_vector = normal_vector / np.linalg.norm(normal_vector)
    
    for j in range(precision + 1):
        # Lasketaan plane_vector
        plane_vector = np.array([
            radius * math.cos(j * 2 * math.pi / precision),
            radius * math.sin(j * 2 * math.pi / precision),
            0
        ])
        
        # Lasketaan shift_vector ristitulon avulla
        shift_vector = np.cross(normal_vector, plane_vector)
        
        # Lisätään uusi piste (center + shift_vector) vertices-listaan
        new_point = center + shift_vector
        vertices.append(new_point)

    faces=[]
    for j in range(len(vertices)-1):
        faces.append([0,j,j+1])
    return np.array(vertices), np.array(faces)

    # Step 2: Find a vector orthogonal to both v and v1 using the cross product




#chatGPT
def transform_point_location(point, params:TransformationParameters):
    # Convert inputs to numpy arrays for easier manipulation
    point = np.array(point)
    mass_center = np.array(params.mass_center)
    south_north_vector = np.array(params.south_north_vector)
    greenwich_vector = np.array(params.greenwich_vector)
    shift_vector = np.array(params.shift_vector)
    
    # 1. Place the object at mass_center
    point = point - mass_center
    
    # 2. Scale the object using the south_north_vector as the scale factor
    point = point * np.linalg.norm(south_north_vector)
    
    # 3. Rotate around the south_north_vector by south_north_rotation
    if params.south_north_rotation != 0:
        # Normalize the south_north_vector to get the rotation axis
        south_north_axis = south_north_vector / np.linalg.norm(south_north_vector)
        point = rotate_point(point, south_north_axis, params.south_north_rotation)
    
    # 4. Rotate around the greenwich_vector by greenwich_rotation
    if params.greenwich_rotation != 0:
        # Normalize the greenwich_vector to get the rotation axis
        greenwich_axis = greenwich_vector / np.linalg.norm(greenwich_vector)
        point = rotate_point(point, greenwich_axis, params.greenwich_rotation)
    
    # 5. Shift by the shift_vector
    point = point + shift_vector
    
    # Convert the point to a tuple before returning
    return tuple(point)



def rotate_point(point, axis, theta):
    """
    Rotates a point around a given axis by theta radians using Rodrigues' rotation formula.
    """
    axis = axis / np.linalg.norm(axis)
    point_rot = (point * np.cos(theta) + 
                 np.cross(axis, point) * np.sin(theta) + 
                 axis * np.dot(axis, point) * (1 - np.cos(theta)))
    return point_rot




def spherical_to_cartesian(r, theta, phi):
    # Calculate the Cartesian coordinates
    x = r * math.sin(theta) * math.cos(phi)
    y = r * math.cos(theta)
    z = r * math.sin(theta) * math.sin(phi)
    return x, y, z



#here y direction is up ie. theta is then 0 and 3,14 at the bottom
def cartesian_to_spherical(x, y, z):
    # Calculate the radial distance
    r = math.sqrt(x**2 + y**2 + z**2)
    
    # Calculate the polar angle
    theta = math.acos(y / r)
    
    # Calculate the azimuthal angle
    phi = math.atan2(z, x)
    
    return r, theta, phi


def rotate_vector_up(vector,degrees):
    r, theta, phi=cartesian_to_spherical(vector[0],vector[1],vector[2])
    rad=degrees*math.pi/180.0
    rotated_vector=spherical_to_cartesian(r, theta-rad, phi)
    return rotated_vector

def point_distance(point1,point2):
    squaresum=0
    for i in range(3):
        squaresum+=(point2[i]-point1[i])*(point2[i]-point1[i])
    return math.sqrt(squaresum)


def point_vector(start_point,end_point):
    return (end_point[0]-start_point[0],end_point[1]-start_point[1],end_point[2]-start_point[2])


def inner_product(point_vector1,point_vector2):
    sum=0
    for i in range(3):
        sum += point_vector1[i]*point_vector2[i]
    return sum


#loads a txt_file, tis is kinda same as load_file_as_string, but it was put inside class Layers for some stupid reasons
def load_text_file(file_name: str, sub_directory: str):
    actual_name = sub_directory + "/" + file_name.strip("'") + ".txt"  # strip ' just in case
    if sub_directory == "":
        actual_name = file_name + ".txt"

    try:
        # Open a file for reading
        with open(actual_name, "r") as file:
            # Read the contents of the file into memory
            instructions = file.read()
        return instructions
    except FileNotFoundError:
        # If the file is not found, return None
        return None


def load_drawing(drawing_name):
    instructions = load_text_file(drawing_name, "drawings")
    if instructions is None:
        # No file found, return None or handle as needed
        return None
    
    return Geometry.Drawing(instructions)



def angle_between_plane_and_vector(v1, v2, v3):
    # Calculate the normal vector of the plane spanned by v1 and v2
    normal_vector = np.cross(v1, v2)
    
    # Calculate the dot product between the normal vector and the third vector
    dot_product = np.dot(normal_vector, v3)
    
    # Calculate the magnitude of the normal vector and the third vector
    normal_vector_magnitude = np.linalg.norm(normal_vector)
    v3_magnitude = np.linalg.norm(v3)
    
    # Calculate the cosine of the angle between the normal vector and the third vector
    cos_angle = dot_product / (normal_vector_magnitude * v3_magnitude)
    
    # Calculate the angle between the normal vector and the third vector in radians
    angle = math.acos(cos_angle)
    
    # The angle between the plane and the third vector is the complement
    plane_vector_angle = math.pi / 2 - angle
    
    return plane_vector_angle


def projection(camera_point,camera_vector,point):
    if point==camera_point:
        return(0,0)
    if camera_vector==(0,0,0):
        return(0,0)
    camera_dist=point_distance(point,camera_point)
    camera_vector_length=point_distance((0,0,0),camera_vector)
    ip=inner_product(camera_vector,point_vector(camera_point,point))
    #calculate the angle betwwen where camera is pointing, and where the point is
    cos_of_angle=ip/(camera_dist*camera_vector_length)
    angle_from_camera_line=math.acos(cos_of_angle)
    if angle_from_camera_line>1.57 or angle_from_camera_line<-1.57:
        print("unvisible error")
        return "unvisible"
    #length of projected vector
    projection_length=(ip/camera_vector_length)
    #calculate distance in pixels of this points projection from origo
    distance_from_camera_line=projection_length*(math.sqrt((1-cos_of_angle*cos_of_angle)))
    if distance_from_camera_line<SAMEPOINTLIMIT:
        return (0,0)
    pixel_r= distance_from_camera_line*camera_vector_length/camera_dist
    
    camera_up_vector=rotate_vector_up(camera_vector,90)
    angle_from_y_axis=angle_between_plane_and_vector(camera_vector,camera_up_vector,point_vector(camera_point,point))
    sin_of_y_axis_angle=math.sin(angle_from_y_axis)
    distance_from_fake_y_axis=projection_length*sin_of_y_axis_angle #can be negative

    ip_from_up=inner_product(camera_up_vector,point_vector(camera_point,point))  
    y_sign=1
    if ip_from_up<0: #so if the angle between camera up direction and the direction of the object (point)
        #is over 90 degrees, then y is set negative
        y_sign=-1  
    final_x=pixel_r*distance_from_fake_y_axis/distance_from_camera_line
    final_y=y_sign*math.sqrt(max(0,pixel_r**2-final_x**2))
    return (round(final_x),round(final_y))
    #camera_up_vector=

#given a vector like (2,1,-5) returns two vectors with length of 1 and in right angles to given vector and each other
def find_orthogonal_vectors(v):
    # Normalize the input vector
    v = v / np.linalg.norm(v)
    
    # Step 1: Find a vector orthogonal to v
    # We can use a simple heuristic: if the x component is the smallest, swap y and z.
    if abs(v[0]) <= abs(v[1]) and abs(v[0]) <= abs(v[2]):
        v1 = np.array([0, -v[2], v[1]])
    elif abs(v[1]) <= abs(v[0]) and abs(v[1]) <= abs(v[2]):
        v1 = np.array([-v[2], 0, v[0]])
    else:
        v1 = np.array([-v[1], v[0], 0])
    
    # Normalize v1 to make it a unit vector
    v1 = v1 / np.linalg.norm(v1)
    
    # Step 2: Find a vector orthogonal to both v and v1 using the cross product
    v2 = np.cross(v, v1)
    
    # Normalize v2 to make it a unit vector
    v2 = v2 / np.linalg.norm(v2)
    
    return v1, v2







class Point3D:
    #point is meantto be (x,y,z) so not [x,y,z]
    def __init__(self,tr_param,point,radius=1,pencolor=(0,0,0)): 
        self.tr_param=tr_param
        self.point=point
        self.radius=radius
        self.pencolor=pencolor
    
    def get_point(self):
        return self.point
    


    def projected_point_to_Geometry(self,camera_point,camera_vector):
        transformed_point=transform_point_location(self.point) #first move the point
        projected_point=projection(camera_point,camera_vector,transformed_point) #then project
        if projected_point=="unvisible":
            return None
        return Geometry.Dot(projected_point,thickness=self.radius,pencolor=self.pencolor,pen_down=True,fc_change=True,fillcolor=True)




class Line3D:
    #end_point3D2 and end_point3D1 are the locations that are "saved" and tr_param
    #tells how thay are transformed if they are inside of Face3D
    end_point3D1=None
    end_point3D2=None
    thickness=1
    pencolor=(0,0,0)
    pendown=True

    def __init__(self,tr_param=None,property_dict={}): 
        if tr_param==None:
            tr_param=TransformationParameters()
        else:
            self.tr_param=tr_param
        self.set_properties_from_dict(property_dict,tr_param)


    def set_properties_from_dict(self,dict,tr_param):
        """Create a TransformationParameters object from a dictionary."""
        # Extract values from the dictionary or use default if not provided
        self.end_point3D1 = Point3D(tr_param,dict.get('endpoint1', (0, 0, 0)))
        self.end_point3D2 = Point3D(tr_param,dict.get('endpoint2', (0, 0, 0)))
        self.thickness = dict.get('thickness', 1)
        self.pencolor = dict.get('pencolor', (0,0,0))
        self.pendown = dict.get('pendown', True)

    def to_dict(self):
        return{"endpoint1":self.end_point3D1.get_point(),"endpoint2":self.end_point3D2.get_point(),"thickness":self.thickness,
               "pencolor":self.pencolor,"pendown":self.pendown}

    #@classmethod
    #def from_dict(cls, tr_param,line_dict):
    #    return cls(end_point3D1=Point3D(tr_param,line_dict["endpoint1"]), end_point3D2=Point3D(tr_param,line_dict["endpoint2"]),
    #               thickness=line_dict["thickness"],pencolor=line_dict["pencolor"],pendown=line_dict["pendown"])


    @classmethod
    def from_dict(cls, tr_param, line_dict):
        return cls(tr_param, property_dict=line_dict)


    def line_vector(self):
        end_point1=self.end_point3D1.get_point()
        end_point2=self.end_point3D2.get_point()
        return (end_point2[0]-end_point1[0],end_point2[1]-end_point1[1],end_point2[2]-end_point1[2])
        
    def line_length(self):
        return point_distance(self.end_point3D1.get_point(),self.end_point3D2.get_point())

    def print_info(self):
        print("Line3D, endpoints:",self.end_point3D1.get_point(),self.end_point3D2.get_point())

    def projected_line_to_Geometry(self,camera_point,camera_vector,tr_param):
        self.tr_param=tr_param #need to do this I guess? this is how the information about orientation flows from object to lines
        end_point1=transform_point_location(self.end_point3D1.get_point(),self.tr_param)
        end_point2=transform_point_location(self.end_point3D2.get_point(),self.tr_param)
        #end_point1 are calculated by "physical transformation", i.e. points are moved in the space
        #projection then makes "view tranformation" by projecting those 3D-points to 2D
        proj1=projection(camera_point,camera_vector,end_point1)
        proj2=projection(camera_point,camera_vector,end_point2)
        middle_point=((end_point1[0]+end_point2[0])/2,(end_point1[1]+end_point2[1])/2,(end_point1[2]+end_point2[2])/2)
        middle_point_distance=point_distance(middle_point,camera_point)
        thickness=max(1,round(self.thickness*point_distance((0,0,0),camera_vector)/middle_point_distance))
        if proj1=="unvisible" or proj2=="unvisible":
            return None
        #currently we return line which
        return Geometry.Line(end_point1=proj1,end_point2=proj2,thickness=thickness,pencolor=self.pencolor,pen_down=self.pendown,fc_change=True,fillcolor=(0.5,0.3,0.2))


def shift_rotation_transform_plane_to_xy(point_list):
    if len(point_list) < 3:
        raise ValueError("point_list must contain at least 3 points to define a plane")

    p0 = np.array(point_list[0])
    p1 = np.array(point_list[1])
    p2 = np.array(point_list[2])

    # Step 1: Shift all points so that p0 moves to the origin
    shift_vector = -p0
    p1_shifted = p1 + shift_vector
    p2_shifted = p2 + shift_vector

    # Step 2: Calculate vectors on the plane using the shifted points
    v1 = p1_shifted
    v2 = p2_shifted

    # Step 3: Calculate the normal vector of the plane
    normal_vect = np.cross(v1, v2)
    normal_vect = normal_vect / np.linalg.norm(normal_vect)  # Normalize the normal vector

    # Step 4: Find rotation axis and angle to align the normal vector with the z-axis
    z_axis = np.array([0, 0, 1])
    rotation_axis = np.cross(normal_vect, z_axis)
    sin_angle = np.linalg.norm(rotation_axis)
    cos_angle = np.dot(normal_vect, z_axis)
    rotation_axis = rotation_axis / np.linalg.norm(rotation_axis) if sin_angle != 0 else np.array([1, 0, 0])

    # Step 5: Construct the rotation matrix using Rodrigues' rotation formula
    K = np.array([[0, -rotation_axis[2], rotation_axis[1]],
                  [rotation_axis[2], 0, -rotation_axis[0]],
                  [-rotation_axis[1], rotation_axis[0], 0]])

    rotation_matrix = np.eye(3) + sin_angle * K + (1 - cos_angle) * np.dot(K, K)

    return shift_vector, rotation_matrix

def new_place_after_shift_rotation_transformation(point, shift, rotation_matrix):
    new_point = np.dot(rotation_matrix, point + shift)
    return new_point

def shift_rotate_point_list(point_list):
    shift, rotation_matrix = shift_rotation_transform_plane_to_xy(point_list)
    new_point_list = []
    for point in point_list:
        new_point_list.append(new_place_after_shift_rotation_transformation(point, shift, rotation_matrix))
    return new_point_list


def check_point_in_polygon(point_list, special_point):
    # Step 1: Find the transformation for point_list
    shift, rotation_matrix = shift_rotation_transform_plane_to_xy(point_list)
    
    # Step 2: Apply transformation to special_point
    transformed_special_point = new_place_after_shift_rotation_transformation(special_point, shift, rotation_matrix)
    
    # Step 3: Check if the transformed special_point's z-coordinate is close to 0
    if np.abs(transformed_special_point[2]) > 1e-6:
        print("The transformed special_point is not on the xy-plane.")
        return False
    
    # Step 4: Reduce to 2D and check if inside polygon
    # Transform the point_list to the xy-plane
    transformed_point_list = shift_rotate_point_list(point_list)
    
    # Extract the 2D coordinates (xy-plane) of the transformed points
    transformed_point_list_2d = [(point[0], point[1]) for point in transformed_point_list]
    transformed_special_point_2d = (transformed_special_point[0], transformed_special_point[1])
    
    # Create a Path object representing the polygon
    polygon_path = Path(transformed_point_list_2d)
    
    # Check if the special point lies inside the polygon
    is_inside = polygon_path.contains_point(transformed_special_point_2d)
    
    return is_inside

def distance_point_to_3d_line_segment(point, v1, v2):
    line_vec = v2 - v1
    point_vec = point - v1
    line_len = np.linalg.norm(line_vec)
    line_unitvec = line_vec / line_len
    projection_length = np.dot(point_vec, line_unitvec)
    projection = line_unitvec * projection_length
    
    if projection_length < 0:
        closest_point = v1
    elif projection_length > line_len:
        closest_point = v2
    else:
        closest_point = v1 + projection
    
    distance = np.linalg.norm(point - closest_point)
    return distance

def distance_point_to_polygon_edges_3d(point, point_list):
    min_distance = float('inf')
    num_points = len(point_list)
    
    for i in range(num_points):
        v1 = np.array(point_list[i])
        v2 = np.array(point_list[(i + 1) % num_points])  # Wrap around to first point
        distance = distance_point_to_3d_line_segment(point, v1, v2)
        min_distance = min(min_distance, distance)
    
    return min_distance

def minimum_distance_to_polygonal_face(point_list, camera_point):
    # Step 1: Find the transformation for point_list
    shift, rotation_matrix = shift_rotation_transform_plane_to_xy(point_list)
    
    # Step 2: Apply transformation to camera_point
    transformed_camera_point = new_place_after_shift_rotation_transformation(camera_point, shift, rotation_matrix)
    
    # Step 3: Calculate distance to the plane (z-coordinate)
    distance_to_plane = np.abs(transformed_camera_point[2])
    
    # Transform the point_list to the xy-plane
    transformed_point_list = shift_rotate_point_list(point_list)
    
    # Extract the 2D coordinates (xy-plane) of the transformed points
    transformed_point_list_2d = [(point[0], point[1]) for point in transformed_point_list]
    transformed_camera_point_2d = (transformed_camera_point[0], transformed_camera_point[1])
    
    # Create a Path object representing the polygon
    polygon_path = Path(transformed_point_list_2d)
    
    # Step 4: Check if the 2D projection of the special point is inside the polygon
    if polygon_path.contains_point(transformed_camera_point_2d):
        # If inside the polygon, the distance to the polygonal face is the distance to the plane
        return distance_to_plane
    else:
        # If outside the polygon, calculate the distance to the nearest edge, using 3D coordinates
        distance_to_edges_3d = distance_point_to_polygon_edges_3d(camera_point, point_list)
        return distance_to_edges_3d



def sign_of(x):
    if x==0:
        return 0
    if x>0:
        return 1
    if x<0:
        return -1


#this calculates a matrix, which transforms (0,0,1) to direction_vector, and (0,1,0) and (1,0,0)
#perpendicular to it in such a way that (1,0,0) is tranformed to vector with 0-z-component
def rotation_matrix3D(direction_vector):
        # Define the target vector v3
    v3 = np.array(direction_vector)  

    # Normalize v3 to ensure correct length
    v3 = v3 #/ np.linalg.norm(v3)

    # Calculate v1 which is orthogonal to v3 and (0,0,1)
    # We can use the cross product of v3 and (0,0,1) to get a candidate for v1
    v1_candidate = np.cross(v3, np.array([0, 0, 1]))

    # If the candidate vector is zero (when v3 is [0,0,1]), use [1,0,0] as the candidate
    if np.allclose(v1_candidate, [0, 0, 0]):
        v1_candidate = np.array([1, 0, 0])

    # Normalize v1 to have the same length as v3
    v1 = np.linalg.norm(v3)*v1_candidate / np.linalg.norm(v1_candidate)

    # Calculate v2 which is orthogonal to both v1 and v3
    v2_candidate = np.cross(v3, v1)
    v2=np.linalg.norm(v3)*v2_candidate/np.linalg.norm(v2_candidate)

    # Create the transformation matrix
    transformation_matrix = np.column_stack((v1, v2, v3))

    # Output the transformation matrix
    return transformation_matrix


#if we want to reuse face so that we don't need to create new face3D for every rotated version
#we can create one Face2D and from it create Face3D:s by shifting and rotating
class Face2D:
    face_mass_center=(0,0)
    drawing_rotation=0 #in radians how much the drawing is rotated counter-clockwise
    drawing_name=None
    inside_color=(0,1,0)
    visible_face=True
    face_material=FaceMaterial({})
    def __init__(self,face_material,lines3D=[],inside_color=(0,0,0),drawing_name=None,drawing_rotation=0,visible_face=True):
        self.lines3D=lines3D#lists of lines that 2D plane consists of, these are meant to have z-coordinate 0, perhaps if not, then some error would occur
        self.inside_color=inside_color#and fillcolor in KuhanPiirran
        self.drawing_rotation=drawing_rotation
        self.drawing_name=drawing_name
        self.visible_face=visible_face
        self.face_material=face_material


    def Face2DtoJson(self):
        # Oletetaan, että Line3D-olioilla on oma metodi `to_dict` tai vastaava
        lines3D_as_dicts = [line.to_dict() for line in self.lines3D]

        # Luodaan sanakirja olion attribuuteista
        face2D_dict = {
            "face_mass_center": self.face_mass_center,
            "drawing_rotation": self.drawing_rotation,
            "drawing_name": self.drawing_name,
            "inside_color": self.inside_color,
            "visible_face": self.visible_face,
            "lines3D": lines3D_as_dicts,
            "face_material": self.face_material.to_dict()
        }

        # Muunnetaan sanakirja JSON-muotoon
        return json.dumps(face2D_dict, indent=4)

    def save_face2d_to_file(self, filename):
        face2d_json = self.Face2DtoJson()
        with open(filename, 'w') as file:
            file.write(face2d_json)

    #this Face2D is turned into face3D by shifting mass_center by shift e.g.(3,4,5), 
    #face_direction vector tells in which direction the face is "looking", the lenght of this vector scales the face
    #face2D "has normal vector pointing at". But how is then the x-y-plane direction decided, you might ask?
    #the x-axis "vector" is turned so that it is 90 degrees to normal vector, with y-componen 0. 
    #the directions are x- axis -> east, y-axis ->north
    #after these, the face is rotated counter-clockwise with amount of face_rot in radiands
    def turnto_Face3D(self,tr_param,shift,face_direction_vector,face_rot):
        direction_rotation_matrix=rotation_matrix3D(face_direction_vector)
        
        #directional vectors for the countours of the face
        transformed_x_vector = np.dot(direction_rotation_matrix, (math.cos(face_rot),math.sin(face_rot),0))
        transformed_y_vector = np.dot(direction_rotation_matrix, (math.sin(face_rot),-math.cos(face_rot),0))
        transformed_z_vector = np.dot(direction_rotation_matrix, (0,0,1))
        face_mass_center3D=(self.face_mass_center[0]+shift[0],self.face_mass_center[1]+shift[1],shift[2])
        #in the case that face_direction_vector is in z-axis direction, we need to avoid zero division by calculating
        #values of Face3D drawing related rotation directly
        
        #directional vectors for drawing in face
        drawing_x_vector=tuple(np.dot(direction_rotation_matrix, (math.cos(face_rot+self.drawing_rotation),math.sin(face_rot+self.drawing_rotation),0)))
        drawing_y_vector=tuple(np.dot(direction_rotation_matrix, (math.sin(face_rot+self.drawing_rotation),-math.cos(face_rot+self.drawing_rotation),0)))

        lines_for_3D=[]
        for line3D in self.lines3D: #lines for the contours not for the drawing
            offsetpoint1=(line3D.end_point3D1.get_point()[0]-self.face_mass_center[0],line3D.end_point3D1.get_point()[1]-self.face_mass_center[1],0)
            offsetpoint2=(line3D.end_point3D2.get_point()[0]-self.face_mass_center[0],line3D.end_point3D2.get_point()[1]-self.face_mass_center[1],0)
            p1=np.dot(direction_rotation_matrix,offsetpoint1)
            p2=np.dot(direction_rotation_matrix,offsetpoint2)
            ep1=(p1[0]+shift[0],p1[1]+shift[1],p1[2]+shift[2])
            ep2=(p2[0]+shift[0],p2[1]+shift[1],p2[2]+shift[2])
            point3D1=Point3D(tr_param,ep1)
            point3D2=Point3D(tr_param,ep2)
            property_dict={"endpoint1":point3D1.get_point(),"endpoint2":point3D2.get_point(),
                           "thickness":line3D.thickness,"pencolor":line3D.pencolor,"pendown":line3D.pendown}
            lines_for_3D.append(Line3D(tr_param,property_dict))
            #pitää shiftata, suunnata face_directionilla ja sitten vielä rotatoida
            #mutta onko mahdollista tehdä shift aivan viimeisenä operaationa?
            #KESKEN muut parametrit 3D linjan tekemiseen ovat jo valmiina, mutta
            #uudet janat pitää muodostaa shiftauksien ja kiertojen avulla
        inside_color=self.inside_color
        visible_face=self.visible_face
        face_material=self.face_material
        return Face3D(tr_param,face_material,lines_for_3D,inside_color,self.drawing_name,drawing_x_vector,drawing_y_vector,face_mass_center3D,visible_face)

#a Face for 3D object, for this Face a 3D location of its vertices are setup
class Face3D:
    SAMELINELIMIT=0.00001
    face_mass_center=(0,0,0)
    #when Geometry.Drawing is attached to  this face, this will be the direction where Drawing x-axis points
    #NOTE that the direction here is defined before making transformation with tr_param
    drawing_x_vector=(1,0,0)
    #when Geometry.Drawing is attached to  this face, this will be the direction where Drawing x-axis points
    #NOTE that the direction here is defined before making transformation with tr_param
    drawing_y_vector=(0,1,0)
    attached_drawing=None
    visible_face=True
    face_material=FaceMaterial({})

    def __init__(self,tr_param,face_material=None,lines3D=[],inside_color=(0,0,0),drawing_name=None,
                 drawing_x_vector=None,drawing_y_vector=None,face_mass_center=None,visible_face=True):
        self.tr_param=tr_param
        self.lines3D=lines3D#lists of lines that 3D plane consists of, these must be on same plane (or very close), this must be checked with inner product
        self.inside_color=inside_color#and fillcolor in KuhanPiirran
        if face_material is not None:
            self.face_material=face_material
        else:
            self.face_material= FaceMaterial({})

        if drawing_x_vector==None or drawing_y_vector==None or face_mass_center==None:
            self.calculate_position() #sets the face_mass_center and drawing_x and y vectors if they are not given
        else:
            self.drawing_x_vector=drawing_x_vector
            self.drawing_y_vector=drawing_y_vector
            self.face_mass_center=face_mass_center
        self.drawing_name=drawing_name
        self.visible_face=visible_face
        self.attach_drawing_by_name()

    def set_inside_color(self,new_color):
        self.inside_color=new_color

    def calculate_position(self):
        sum_x=sum_y=sum_z=0
        vertice_list=self.transformed_vertices()
        nro_of_vertices=len(vertice_list)
        for i in range(len(vertice_list)):
            sum_x+=vertice_list[i][0]
            sum_y+=vertice_list[i][1]
            sum_z+=vertice_list[i][2]
        self.face_mass_center=(sum_x/nro_of_vertices,sum_y/nro_of_vertices,sum_z/nro_of_vertices)
        normal=self.normal_vector(vertice_list[0],vertice_list[1],vertice_list[2])
        self.drawing_x_vector,self.drawing_y_vector=find_orthogonal_vectors(normal)

    def attach_drawing_by_name(self):
        if self.drawing_name != "None" and self.drawing_name != "" and self.drawing_name != None:
            drawing = load_drawing(self.drawing_name)
            if drawing is not None and drawing != "":
                self.attach_drawing(drawing)
            else:
                # Optionally handle the case where the drawing couldn't be loaded
                print(f"Warning: Drawing '{self.drawing_name}' could not be loaded.")

    def attach_drawing(self, drawing):
        self.attached_drawing = drawing

    #calculates normal vector of length 1 for plane span by point3D1, point2 and point3
    #if points are in the same line returns just (0,0,0) vector
    def normal_vector(self,point1,point2,point3):
        property_dict1={"endpoint1":point1,"endpoint2":point2,"thickness":1,
               "pencolor":(1,1,1),"pendown":False}
        property_dict2={"endpoint1":point1,"endpoint2":point3,"thickness":1,
               "pencolor":(1,1,1),"pendown":False}
        line1=Line3D(self.tr_param,property_dict1)
        line2=Line3D(self.tr_param,property_dict2)
        lvector1=line1.line_vector()
        lvector2=line2.line_vector()
        i_comp=lvector1[1]*lvector2[2]-lvector1[2]*lvector2[1]
        j_comp=-lvector1[0]*lvector2[2]+lvector1[2]*lvector2[0]
        k_comp=lvector1[0]*lvector2[1]-lvector1[2]*lvector2[0]
        property_dict={"endpoint1":(0,0,0),"endpoint2":(i_comp,j_comp,k_comp),"thickness":1,
               "pencolor":(1,1,1),"pendown":False}
        unnormalized_line=Line3D(self.tr_param,property_dict) #line from origo to direction perpendicular to plae
        line_length=unnormalized_line.line_length()
        if line_length> self.SAMELINELIMIT:
            return (i_comp/line_length,j_comp/line_length,k_comp/line_length)
        else:
            return (0,0,0)


    #returns True iff points in the line are in the same 3D plane
    def is_it_a_real_plane(self):
        for i in range(len(self.lines3D)-1):
            point3D1=self.lines3D[i].end_point3D2
            point3D2=self.lines3D[i+1].end_point3D1
            dist=point_distance(point3D1.get_point(),point3D2.get_point())
            if dist>self.SAMELINELIMIT:
                return False #self.lines pitää järjestää niin, että edellinen line loppuu seuraavan alkuun
                #jos etäisyys ylittää kynnysetäisyyden se hylätään

        for i in range(len(self.lines3D)-2): #tarkastellaan kahta melkein peräkkäistä janaa, katsotaan
            #virittäväktö ensimmäisen janan päätepisteet saman tason riippumatta kumpi toisen janan 
            #piste otetaan mukaan
            point1=self.lines3D[i].end_point3D1.get_point()
            point2=self.lines3D[i].end_point3D2.get_point()
            point3=self.lines3D[i+2].end_point3D1.get_point()
            point4=self.lines3D[i+2].end_point3D1.get_point()
            normal1=self.normal_vector(point1,point2,point3)
            normal2=self.normal_vector(point1,point2,point4)
            dist=point_distance(normal1,normal2)
            if dist>self.SAMELINELIMIT: #jos normaalivektorit ovat (likimain) samat kaikkialla, testi läpäistään
                return False #self.lines3D pitää järjestää niin, että edellinen line loppuu seuraavan alkuun
                    #jos etäisyys ylittää kynnysetäisyyden se hylätään
        return True
            
    def vertices(self):
        point_list=[]
        point_list.append(self.lines3D[0].end_point3D1.get_point())
        for i in range(len(self.lines3D)):
            point_list.append(self.lines3D[i].end_point3D2.get_point())
        return point_list

    def transformed_vertices(self):
        point_list=[]
        point_list.append(transform_point_location(self.lines3D[0].end_point3D1.get_point(),self.tr_param))
        for i in range(len(self.lines3D)):
            transformed_location=transform_point_location(self.lines3D[i].end_point3D2.get_point(),self.tr_param)
            point_list.append(transformed_location)
        return point_list

    def distance_to_point_in_the_plane(self,camera_point):
        point_list=self.transformed_vertices()
        return minimum_distance_to_polygonal_face(point_list,camera_point)

            
    def print_info(self):
        for line3D in self.lines3D:
            print("line:",line3D.end_point3D1.get_point(),line3D.end_point3D2.get_point())


    def projected_Face3D_to_Geometry(self,camera_point,camera_vector,tr_param,conditions:Conditions):
        self.tr_param=tr_param
        moved_vertices=self.transformed_vertices() #so transformed according to tr_param
        some_normal_vector=(0,0,1)
        if len(moved_vertices)>3:
            some_normal_vector = np.cross(np.array(moved_vertices[1]) - np.array(moved_vertices[0]), 
                              np.array(moved_vertices[-2]) - np.array(moved_vertices[1]))

        surface_normal_vector=some_normal_vector/np.linalg.norm(some_normal_vector)
        #surface_normal_vector should now be orthogonal to plane of this face (tr_params effects weighted in)
        reflectivity=self.face_material.property_dict.get("reflectivity",(1,1,1))
        projected_drawing=Geometry.Drawing("")
        contour_polygon=Geometry.Polygon()
        for i in range(len(self.lines3D)):
            new_line=self.lines3D[i].projected_line_to_Geometry(camera_point,camera_vector,tr_param)
            if new_line != None:
                conditioned_color=conditions.color_in_lightning(new_line.pencolor,reflectivity,surface_normal_vector)
                new_line.pencolor=conditioned_color 
                contour_polygon.add_line(new_line)

        conditioned_color=conditions.color_in_lightning(self.inside_color,reflectivity,surface_normal_vector) 
        contour_polygon.set_inside_color(conditioned_color)
        #KESKEN, ainoa mikä on huomioitu tällä hetkellä valaistusolosuhteiden osalta on facen reunien rajaama
        #polygoni, eivät itse reunaviivat tai kuva

        if len(contour_polygon.vertices())>=3:
            if self.visible_face:
                projected_drawing.add_polygon(contour_polygon)
            else:#if we want to have transparen face, so basicly a hovering drowing
                lines_to_draw=contour_polygon.disintegrate()
                projected_drawing.add_linelist(lines_to_draw)
        if self.attached_drawing!=None:
            for element in self.attached_drawing.elements:
                if element.__class__.__name__ == "Polygon":
                    projected_poly=Geometry.Polygon()
                    for i in range(len(element.lines)):
                        thickness=element.lines[i].thickness #note that this should actually be changed depending on camera distance etc
                        pencolor_str_array=element.lines[i].pencolor
                        pencolor=(float(pencolor_str_array[0]),float(pencolor_str_array[1]),float(pencolor_str_array[2]))
                        pendown=element.lines[i].pen_down
                        #we need to calculate where line-endpoints go, this is done by summing
                        #to face_mass_center the x and y drawing_vectors multiplied by corresponding scalars
                        x_comp1 = element.lines[i].end_point1_x()
                        scaled_x_shift_vector = tuple(x_comp1 * x for x in self.drawing_x_vector)
                        y_comp1 = element.lines[i].end_point1_y()
                        scaled_y_shift_vector = tuple(y_comp1 * x for x in self.drawing_y_vector)
                        help_vector1 = tuple(x + y for x, y in zip(self.face_mass_center,scaled_x_shift_vector))
                        point1_pos=tuple(x + y for x, y in zip(help_vector1,scaled_y_shift_vector))
                        end_point3D1=Point3D(tr_param,point1_pos)
                        x_comp2 = element.lines[i].end_point2_x()
                        scaled_x_shift_vector = tuple(x_comp2 * x for x in self.drawing_x_vector)
                        y_comp2 = element.lines[i].end_point2_y()
                        scaled_y_shift_vector = tuple(y_comp2 * x for x in self.drawing_y_vector)
                        help_vector2 = tuple(x + y for x, y in zip(self.face_mass_center,scaled_x_shift_vector))
                        point2_pos=tuple(x + y for x, y in zip(help_vector2,scaled_y_shift_vector))
                        end_point3D2=Point3D(tr_param,point2_pos)
                        conditioned_color=conditions.color_in_lightning(pencolor,reflectivity,surface_normal_vector) 
                        if(abs(conditioned_color[2]-8.486)<0.01):
                            print("BINGO! error found")
                        property_dict={"endpoint1":end_point3D1.get_point(),"endpoint2":end_point3D2.get_point(),
                           "thickness":thickness,"pencolor":conditioned_color,"pendown":pendown}
                        new_line3D= Line3D(tr_param,property_dict)
                        if new_line3D != None:
                            projected_poly.add_line(new_line3D.projected_line_to_Geometry(camera_point,camera_vector,tr_param))
                    inside_color=(float(element.inside_color[0]),float(element.inside_color[1]),float(element.inside_color[2]))
                    conditioned_color=conditions.color_in_lightning(inside_color,reflectivity,surface_normal_vector) 
                    projected_poly.set_inside_color(conditioned_color)
                    #NOTE, on vielä korjaamatta tämä KESKEN, kun zoomattiin liian lähellle tuli virhe 'NoneType' object has no attribute 'end_point1'
                    #Ratkaisu lienee sellaisten viivojen poisto, joista puuttuu päätepiste (tod näk siksi, että se 1.57vehto ei toteudu)
                    projected_drawing.add_polygon(projected_poly)


                if element.__class__.__name__ == "Line":
                    thickness=element.thickness #note that this should actually be changed depending on camera distance etc
                    pencolor=(float(element.pencolor[0]),float(element.pencolor[1]),float(element.pencolor[2]))
                    pendown=element.pen_down
                    #we need to calculate where line-endpoints go, this is done by summing
                    #to face_mass_center the x and y drawing_vectors multiplied by corresponding scalars
                    x_comp1 = element.end_point1_x()
                    scaled_x_shift_vector = tuple(x_comp1 * x for x in self.drawing_x_vector)
                    y_comp1 = element.end_point1_y()
                    scaled_y_shift_vector = tuple(y_comp1 * x for x in self.drawing_y_vector)
                    help_vector1 = tuple(x + y for x, y in zip(self.face_mass_center,scaled_x_shift_vector))
                    point1_pos=tuple(x + y for x, y in zip(help_vector1,scaled_y_shift_vector))
                    end_point3D1=Point3D(self.tr_param,point1_pos)
                    
                    x_comp2 = element.end_point2_x()
                    scaled_x_shift_vector = tuple(x_comp2 * x for x in self.drawing_x_vector)
                    y_comp2 = element.end_point2_y()
                    scaled_y_shift_vector = tuple(y_comp2 * x for x in self.drawing_y_vector)
                    help_vector2 = tuple(x + y for x, y in zip(self.face_mass_center,scaled_x_shift_vector))
                    point2_pos=tuple(x + y for x, y in zip(help_vector2,scaled_y_shift_vector))
                    end_point3D2=Point3D(tr_param,point2_pos)
                    conditioned_color=conditions.color_in_lightning(pencolor,reflectivity,surface_normal_vector) 
                    property_dict={"endpoint1":end_point3D1.get_point(),"endpoint2":end_point3D2.get_point(),
                           "thickness":thickness,"pencolor":conditioned_color,"pendown":pendown}
                    new_line3D= Line3D(tr_param,property_dict)
                    projected_line=new_line3D.projected_line_to_Geometry(camera_point,camera_vector,tr_param)
                    if projected_line!=None:
                        projected_drawing.add_line(projected_line)
                if element.__class__.__name__ == "Dot":
                    print("Dot adding To be added")
        return projected_drawing



class Mesh3D:
    #this is just a list of triangles in 3D, and their colors, it can be used to create an Object#D
    mesh_dict_list=[] #consists of dictionaries for each triangle involved
    def __init__(self,inside_color):
        self.mesh_dict_list=[]
        #self.create_cylinder(inside_color,700,150,26,23)
        #self.create_sphere(inside_color,3)
        self.create_cylinder_with_ends(inside_color,700,150,62,1)
        self.colorize_using_image("yoda.png")



    def add_triangle(self,endpoint1,endpoint2,endpoint3,inside_color,visible_face:bool,faceMaterial:FaceMaterial):
        material_name=faceMaterial.name
        reflectivity=faceMaterial.reflectivity
        self.mesh_dict_list.append({"endpoint1":endpoint1,"endpoint2":endpoint2,"endpoint3":endpoint3,
                                    "inside_color":inside_color,"visible_face":visible_face,
                                    "name":material_name,"reflectivity":reflectivity})
        


    #camera_point and vector works as follows, camera is put into position of camera_point and
    #facing to the direction of camera_vector. Also norm(camera_vector)/norm(camera_point) should give the amount of
    #zoom (I guess). 
    # Color of each triangle in a mesh is cahnged according to the placements of the corners of
    #this camera_point,camera_vector2D projection of the vertices of the triangles by looking average of 
    #  pixels of image_filename
    def colorize_using_image(self,image_filename,camera_point=(0,10000,10000),camera_vector=(0,-7000,-7000)):
        im = Image.open(image_filename) # Can be many different formats.
        pix = im.load()
        (width,height)=im.size
        for triangle in self.mesh_dict_list:
            point3D1,point3D2,point3D3=triangle["endpoint1"],triangle["endpoint2"],triangle["endpoint3"]
            point1=projection(camera_point,camera_vector,point3D1)
            point2=projection(camera_point,camera_vector,point3D2)
            point3=projection(camera_point,camera_vector,point3D3) 
            point1=(point1[0]+width/2,point1[1]+height/2)
            point2=(point2[0]+width/2,point2[1]+height/2)
            point3=(point3[0]+width/2,point3[1]+height/2)
            print("3D points",point3D1,point3D2,point3D3)
            print("points",point1,point2,point3)
            average_color=PngMaker.triangle_average_color(point1,point2,point3,image_filename)
            average_color=(average_color[0]/256.0,average_color[1]/256.0,average_color[2]/256.0)
            print("average color",average_color)
            triangle["inside_color"]=average_color



    def create_sphere(self,inside_color,subdivisions):
        vertices,faces=generate_sphere(subdivisions,210)
        print("VERTICES",tuple(map(float,vertices[faces[0][0]])),vertices[faces[0][0]],vertices[faces[0][0]])
        for face in faces:
            print(face)
            self.add_triangle(tuple(map(float,vertices[face[0]])),tuple(map(float,vertices[face[1]])),tuple(map(float,vertices[face[2]])),inside_color,True,FaceMaterial({"name":"puu","reflectivity":(1,1,1)}))    


    def create_cylinder(self,inside_color,height,radius,precision_circle,precision_side):
        vertices,faces=generate_cylinder(height,radius,precision_circle,precision_side)
        for face in faces:
            print(face)
            self.add_triangle(tuple(map(float,vertices[face[0]])),tuple(map(float,vertices[face[1]])),tuple(map(float,vertices[face[2]])),inside_color,True,FaceMaterial({"name":"metalli","reflectivity":(1,0.5,1)}))    


    def create_cylinder_with_ends(self,inside_color,height,radius,precision_circle,precision_side):
        vertices,faces=generate_cylinder(height,radius,precision_circle,precision_side)
        for face in faces:
            print(face)
            self.add_triangle(tuple(map(float,vertices[face[0]])),tuple(map(float,vertices[face[1]])),tuple(map(float,vertices[face[2]])),inside_color,True,FaceMaterial({"name":"metalli","reflectivity":(1,0.5,1)}))    
        top_vertices,top_faces=generate_circle((0,0,height/2),radius,(0,0,1),precision_circle)
        bottom_vertices,bottom_faces=generate_circle((0,0,0),radius,(0,0,-1),precision_circle)
        for face in top_faces:
            print(face)
            self.add_triangle(tuple(map(float,top_vertices[face[0]])),tuple(map(float,top_vertices[face[1]])),tuple(map(float,top_vertices[face[2]])),inside_color,True,FaceMaterial({"name":"metalli","reflectivity":(1,0.5,1)})) 

        for face in bottom_faces:
            print("naama",face)
            self.add_triangle(tuple(map(float,bottom_vertices[face[0]])),tuple(map(float,bottom_vertices[face[1]])),tuple(map(float,bottom_vertices[face[2]])),inside_color,True,FaceMaterial({"name":"metalli","reflectivity":(1,0.5,1)})) 
            


class Object3D:
    #faces: Face3D objects that this object consists of, faces are 
    #mass_center: rotation happens through axis going trhough this point
    #south_north_vector: direction of the main axis. Adjusting the length of this changes the size
    #greenwich_vector: this is meant to point to the equator at greenwich meridian (if visual is helpful)
    #south_north_rotation: gives the amount of rotation (in radians) with respect to south_north_vector, 
    #greenwich_rotation: gives the amount of rotation (in radians) with respect to greenwich_vector, 
    
    #point locations are transformed in this order:
    #1.object is placed in mass_center
    #2. it is enlarged with factor south_north_vector
    #3. it is rotated with respect to axis which goes from mass_center to the direction of 
    # south_north_vector with amount of south_north_rotation (in radians)
    #4. it is rotated with respect to axis which goes from mass_center to the direction of
    #  greenwich_vector with amount of greenwich_rotation (in radians)
    #4. it is shifted by the amount of shift_vector

    faces=None
    face2D_dict_list=[]
    #face2d_dict_list looks like this [{"face2D_filename":"mustikkakasvot","shift":(0,0,150),
    # "face_direction_vector":(0,0,1),"face_rot":0},{"face2D_filename":"lapio","shift":(40,550,150),
    # "face_direction_vector":(0,1,),"face_rot":0.63}] NOTE there can be more fac
    mesh_dict_list=[]#míf this exists, it is the form of
    #[{endpoint1:(1,4,-5),endpoint2:(5,6,-9),endpoint3:(-12,-12,12),inside_color=(0.3,0.2,0.1),visible_face=True,'
    # name:"muovi","reflectivity":(1,0.4,2)}, {endpoint1:(10,234,-52),endpoint2:(15,0,9),endpoint3:(-1232,-112,132),
    # inside_color=(0.3,0.2,0.1),visible_face=True,'name:"rauta","reflectivity":(1,4,0.2)},...]

    dict_list=[]
    #face_dict_list here might be face2D_dict_list or mesh_dict depending on 
    # whether "face2D_filename" is "" (then it is mesh, otherwise 2D)
    def __init__(self, tr_param: TransformationParameters, dict_list=None):
        self.tr_param = tr_param
        self.faces=[]
        self.dict_list=dict_list
        print("creating object3D",self.tr_param,self.faces,self.dict_list)
        for item in dict_list:
            if item.get("face2D_filename")=="" or item.get("face2D_filename")==None:#if there is no face file associated
                self.add_face_from_mesh(item) #face2D_dict_list is going to look different here
            else:
                self.add_face_from_dict(item)
        #else: do we need these anymore?
        #    self.face2D_dict_list=[]
        #   self.mesh_dict_list=[]
    

    #updates transformationParameters of this object
    def update_tr_param(self,parameter_name,new_value):
        params_dict=self.tr_param.to_dict()
        params_dict[parameter_name]=new_value
        self.tr_param=self.tr_param.from_dict(params_dict)


    def add_face_from_mesh(self,mesh_face):
        face_material=FaceMaterial({"name":mesh_face["name"],"reflectivity":mesh_face["reflectivity"]})
        lines3D=[]
        lines3D.append(Line3D(self.tr_param,{"endpoint1":mesh_face["endpoint1"],"endpoint2":mesh_face["endpoint2"],"thickness":1,"pendown":False}))
        lines3D.append(Line3D(self.tr_param,{"endpoint1":mesh_face["endpoint2"],"endpoint2":mesh_face["endpoint3"],"thickness":1,"pendown":False}))
        lines3D.append(Line3D(self.tr_param,{"endpoint1":mesh_face["endpoint3"],"endpoint2":mesh_face["endpoint1"],"thickness":1,"pendown":False}))
        face3d=Face3D(self.tr_param,face_material,lines3D,inside_color=mesh_face["inside_color"],drawing_name=None,
                 drawing_x_vector=None,drawing_y_vector=None,face_mass_center=None,visible_face=True)

        self.faces.append(face3d)



    def add_face_from_dict(self,face2D_item):
        if face2D_item.get("face2D_filename") is not None and face2D_item.get("face2D_filename") !="":
            face2D=load_face2d_from_file(face2D_item.get("face2D_filename"),self.tr_param)
            shift=face2D_item.get("shift",(0,0,0))
            face_direction_vector=face2D_item.get("face_direction_vector",(0,1,0))
            face_rot=face2D_item.get("face_rot",0)
            self.faces.append(face2D.turnto_Face3D(self.tr_param,shift,face_direction_vector,face_rot))            

    def order_by_distance(self, camera_point):
        # Sort the faces based on their distance to the camera_point in reverse order
        self.faces.sort(key=lambda face: face.distance_to_point_in_the_plane(camera_point), reverse=True)


    def add_face(self, face):
        self.faces.append(face)

    def print_info(self):
        for face in self.faces:
            print("face:",face.vertices())

    def projected_Object3D_to_Geometry(self,camera_point,camera_vector,tr_param,condition:Conditions):
        self.tr_param=tr_param
        for i in range(len(self.faces)):
            self.faces[i].tr_param=tr_param #tr_param of faces need to be updated to match the one on objects
        self.order_by_distance(camera_point) #faces laitetaan tässä järjestykseen
        drawi=Geometry.Drawing("")
        for i in range(len(self.faces)):
            projected_drawing=self.faces[i].projected_Face3D_to_Geometry(camera_point,camera_vector,tr_param,condition)
            drawi.elements+=projected_drawing.elements
        return drawi

    def Object3D_to_temp_str(self,camera_point,camera_vector,tr_param,condition):
        drawi=self.projected_Object3D_to_Geometry(camera_point,camera_vector,tr_param,condition)
        temp_str=drawi.from_Drawing_to_temp_string()
        return Geometry.reduce(temp_str)


    def Object3DtoJson(self): 
        # Muunnetaan sanakirja JSON-muotoon
        print("Making Json",self.dict_list)
        return json.dumps(self.dict_list, indent=4)

    def save_object3d_to_file(self, filename):
        object3d_json = self.Object3DtoJson()
        with open(filename, 'w') as file:
            file.write(object3d_json)


class Frame:
    #stores a list of 3D objects and camera_vector and other global information
    #that can be used to create whole image

    def __init__(self,object3D_list,camera_vector,camera_point,condition):
        self.object3D_list=object3D_list
        self.camera_vector=camera_vector
        self.camera_point=camera_point
        self.condition=condition


#KESKEN, HAASTE ON NYT SE, ETTÄ composite objektiin on saatava dict list,
#mutta jos objekteissa on meshin ja face2D:n avulla luotuja sivuja, kumpaa pitää käyttää
#create from mesh vai perus create. Tätä varten pitäisi varmaan hio tiedostojen tallennusta
#niin, että kaikki Object tiedostot näyttävät samalta ja sivu kerrallaan luetaan onko mesh-sivu
#vai face2D sivu
#HUOM tällä hetkellä dict_list asetetaan noneksi alla, joten ei ihme, että tiedostoon tallentuu vain null

    def frameinfo(self):
        i=0
        print("FRAMEINFO:")
        for object in self.object3D_list:
            print("Object: ",i,object.tr_param)
            i+=1

    def composite_3Dobject(self):
        all_faces=[]
        dict_list=[]
        for object3D in self.object3D_list:
            for face in object3D.faces:
                #face.tr_param=object3D.tr_param #I am not sure if this is needed
                all_faces.append(face)
            dict_list+=object3D.dict_list
        #KESKEN, jotenkin tr_param katoaa varmaan seuraavan linjan takia ja objekti ei käänny kuvassa,
        #miten pitää huolta, että sivut joilla on eri tr_param voidaan yhdistää uudeksi objektiksi, jos objektilla on
        #vain yksi tr_param?
        composite_object=Object3D(TransformationParameters(),[])
        for i in range(len(all_faces)):
            print("HOW MANY FACES",i)
            composite_object.faces.append(all_faces[i]) #tr_param of faces need to be updated to match the one on objects


        composite_object.order_by_distance(self.camera_point) #faces laitetaan tässä järjestykseen
        return composite_object
    
    def composite_3Dobject_to_temp_str(self):
        composite_object=self.composite_3Dobject()
        drawi=Geometry.Drawing("")
        for i in range(len(composite_object.faces)):
            projected_drawing=composite_object.faces[i].projected_Face3D_to_Geometry(self.camera_point,self.camera_vector,composite_object.faces[i].tr_param,self.condition)
            drawi.elements+=projected_drawing.elements
        temp_str=drawi.from_Drawing_to_temp_string()
        return Geometry.reduce(temp_str)


def load_face2d_from_file(filename,tr_param):
    with open(filename, 'r') as file:
        face2d_dict = json.load(file)

    # Oletetaan, että `Line3D`-oliolla on metodi `from_dict`, joka luo olion sanakirjasta
    lines3D = [Line3D.from_dict(tr_param,line_dict) for line_dict in face2d_dict["lines3D"]]
    # Luodaan uusi `Face2D`-olio ladatuilla tiedoilla
    face_material_dict=face2d_dict.get("face_material",{})
    return Face2D(
        face_material=FaceMaterial(face_material_dict),
        lines3D=lines3D,
        inside_color=tuple(face2d_dict["inside_color"]),
        drawing_name=face2d_dict["drawing_name"],
        drawing_rotation=face2d_dict["drawing_rotation"],
        visible_face=face2d_dict["visible_face"]
    )


def save_face2D_using_drawing_and_contour_polygon(face_name,end_point_list2D,params_dict=None,face_material=None,inside_color=(0,0,0),drawing_name=None,drawing_rotation=0,visible_face=True):
   
    print("SF in",face_name,end_point_list2D,params_dict,face_material,inside_color,drawing_name,drawing_rotation,visible_face)
    if params_dict==None:
        params_dict = {"mass_center": (0, 0, 0), "south_north_vector": (0, 1, 0) , "greenwich_vector": (0, 0, 1),
                    "greenwich_rotation" : 0,"south_north_rotation" : 0,"shift_vector":(0,0,0)}
    tr_param=TransformationParameters.from_dict(params_dict)
    lines3D=[]
    for i in range(1,len(end_point_list2D)):
        coord1=(end_point_list2D[i-1][0],end_point_list2D[i-1][1],0)
        coord2=(end_point_list2D[i][0],end_point_list2D[i][1],0)
        property_dict={"endpoint1":coord1,"endpoint2":coord2,"thickness":5,"pencolor":(0,1,1)}
        line3d=Line3D(tr_param,property_dict)
        lines3D.append(line3d)
    coord1=(end_point_list2D[-1][0],end_point_list2D[-1][1],0)
    coord2=(end_point_list2D[0][0],end_point_list2D[0][1],0)
    property_dict={"endpoint1":coord1,"endpoint2":coord2,"thickness":5,"pencolor":(0,1,1)}
    line3d=Line3D(tr_param,property_dict)
    lines3D.append(line3d)
    drawing_filename="drawings"+drawing_name+".txt" #HYVIN KÖMPELÖÄ, koska jos kansion nimi muuttuu muualta, pitää muuttaaa tästä, mutta menköön
    if drawing_filename!=None:
        if path.exists(drawing_filename)==False: #do not add drawing if the file doesn¨t exist
            drawing_filename=None
    
    face2d=Face2D(face_material,lines3D,inside_color,drawing_name,drawing_rotation,visible_face)
    face2d.save_face2d_to_file(face_name+".json")


#return an object 3D with face face_name.json and drawing with drawing_name attached to this face which has contour given by end_point_list2D apanned polygon
def object3d_from_drawing_and_contour_polygon(face_name,end_point_list2D,params_dict=None,face_material=None,inside_color=(0,0,0),drawing_name=None,drawing_rotation=0,visible_face=True):
    if face_material==None:
        face_material=FaceMaterial({})
    
    if path.exists(face_name+".json")==False: #avoid overwriting old face
        save_face2D_using_drawing_and_contour_polygon(face_name,end_point_list2D,params_dict,face_material,inside_color,drawing_name,drawing_rotation,visible_face)
    face2D_dict_list=[{"face2D_filename":face_name+".json","shift":(0,0,0),"face_direction_vector":(0,0,1),"face_rot":0}]
    if params_dict==None:
        params_dict = {"mass_center": (0, 0, 0), "south_north_vector": (0, 1, 0) , "greenwich_vector": (0, 0, 1),
                    "greenwich_rotation" : 0,"south_north_rotation" : 0,"shift_vector":(0,0,0)}
    tr_param=TransformationParameters.from_dict(params_dict)
    object3d=Object3D(tr_param,face2D_dict_list)
    return object3d


#given a face_name, if a face already exists saves an object3D with this one face, if the face doesn't exists saves
#a new face with name face_name.json. This face has contour given by end_point_list2D (3D:ized) and drawing attached to it
#Object3D is formed containing only this one face and saved as object_name.json
def save3d_object_from_drawing_and_contour_polygon(object_name,face_name,end_point_list2D,params_dict=None,face_material=None,inside_color=(0,0,0),drawing_name=None,drawing_rotation=0,visible_face=True):
    object3d=object3d_from_drawing_and_contour_polygon(face_name,end_point_list2D,params_dict,face_material,inside_color,drawing_name,drawing_rotation,visible_face)   
    object3d.save_object3d_to_file("3Dobjects/"+object_name+".json")


def load_object3d_from_file(filename,tr_param):
    print("loading file",filename)
    with open(filename, 'r') as file:
        face2D_dict_list = json.load(file)
    return Object3D(tr_param,face2D_dict_list)



def save_photo_cylinder(savename,photo_name,inside_color,height,radius,height_pixels,side_pixels):
    mesh=Mesh3D(inside_color=(0.8,0,0.2))
    params_dict = {"mass_center": (0, 0, 0), "south_north_vector": (0, 1, 0) , "greenwich_vector": (1, 0, 0),
                "greenwich_rotation" : 0*np.pi / 180,"south_north_rotation" : 0*np.pi / 180,"shift_vector":(0,0,0)}

    tr_param=TransformationParameters.from_dict(params_dict)
    mesh.create_cylinder_with_ends(inside_color,height,radius,height_pixels,side_pixels)
    if photo_name!= "":
        mesh.colorize_using_image(photo_name)#for example yoda.png
    #print("MESH",mesh.mesh_dict_list)
    object3d_new=Object3D(tr_param, dict_list=mesh.mesh_dict_list)
    object3d_new.save_object3d_to_file("3Dobjects/"+savename+".json")




if __name__=="__main__":
    
    point = np.array((random.random(), random.random(), random.random()))  # Replace px, py, pz with the coordinates of your test point

    # Apply the transformation
    transformed_point1 = np.dot(rotation_matrix3D((point)), (1,0,0))
    transformed_point2 = np.dot(rotation_matrix3D((point)), (0,1,0))
    transformed_point3 = np.dot(rotation_matrix3D((point)), (0,0,1))
    # Output the original and transformed points
    print("Original point:", point)
    print("Transformed point:", transformed_point1,transformed_point2,transformed_point3)

    params_dict = {"mass_center": (650, 650, 650), "south_north_vector": (0, 1, 0) , "greenwich_vector": (1, 0, 0),
                "greenwich_rotation" : 3*np.pi / 180,"south_north_rotation" : 12*np.pi / 180,"shift_vector":(200,200,200)}

    tr_param=TransformationParameters.from_dict(params_dict)

    params_dict2 = {"mass_center": (150, 650, 850), "south_north_vector": (1, 1, 0) , "greenwich_vector": (1, -1, 1),
                "greenwich_rotation" : 3*np.pi / 180,"south_north_rotation" : 12*np.pi / 180,"shift_vector":(400,200,400)}



    tr_param2=TransformationParameters.from_dict(params_dict2)

    #line1=Line3D({},Point3D(tr_param,(150,150,0)),Point3D(tr_param,(-150,150,0)))
    #line2=Line3D({},Point3D(tr_param,(-150,150,0)),Point3D(tr_param,(-150,-150,0)))
    #line3=Line3D({},Point3D(tr_param,(-150,-150,0)),Point3D(tr_param,(150,-150,0)))
    #line4=Line3D({},Point3D(tr_param,(150,-150,0)),Point3D(tr_param,(150,150,0)))
    line1=Line3D(tr_param,{"endpoint1":(150,150,0),"endpoint2":(-150,150,0),"thickness":5,"pencolor":(0,1,1)})
    line2=Line3D(tr_param,{"endpoint1":(-150,150,0),"endpoint2":(-150,-150,0),"thickness":5,"pencolor":(0,1,0)})
    line3=Line3D(tr_param,{"endpoint1":(-150,-150,0),"endpoint2":(150,-150,0),"thickness":5,"pencolor":(1,0,1)})
    line4=Line3D(tr_param,{"endpoint1":(150,-150,0),"endpoint2":(150,150,0),"thickness":5,"pencolor":(1,0,0)})
    blueberryface=Face2D(FaceMaterial({"reflectivity":(0.2,0.7,0.6)}),lines3D=[line1,line2,line3,line4],inside_color=(0.3,0.9,0.4),drawing_name="mustikkavalmis",drawing_rotation=0,visible_face=True)

    blueberryface.save_face2d_to_file("materiaalimustikkakasvot.json")
    blueberryface=load_face2d_from_file("materiaalimustikkakasvot.json",tr_param)

    
    face2D_dict_list=[{"face2D_filename":"materiaalimustikkakasvot.json","shift":(0,0,150),
     "face_direction_vector":(0,0,1),"face_rot":0},{"face2D_filename":"materiaalimustikkakasvot.json","shift":(0,150,0),
     "face_direction_vector":(0,1,0),"face_rot":0.63},{"face2D_filename":"materiaalimustikkakasvot.json","shift":(150,0,0),
     "face_direction_vector":(1,0,0),"face_rot":1.23},{"face2D_filename":"materiaalimustikkakasvot.json","shift":(0,0,-150),
     "face_direction_vector":(0,0,-1),"face_rot":0},{"face2D_filename":"materiaalimustikkakasvot.json","shift":(0,-150,0),
     "face_direction_vector":(0,-1,0),"face_rot":0.63},{"face2D_filename":"materiaalimustikkakasvot.json","shift":(-150,0,0),
     "face_direction_vector":(-1,0,0),"face_rot":1.23}]

    object3d_new=Object3D(tr_param,face2D_dict_list)
    #object3d_new.save_object3d_to_file("materiaalimustikkakuutio.json")
    #object3d_new=Object3D(tr_param,[face3D1,face3D2,face3D3,face3D4,face3D5,face3D6])

    #mesh=Mesh3D(inside_color=(0.8,0,0.2))    
    #object3d_new=Object3D(tr_param, dict_list=mesh.mesh_dict_list)
    #object3d_new.save_object3d_to_file("omenapallo.json")


    for i in range(1):


        condition=Conditions(background_light=(0.1,2.5-0.02*i,2.2-0.02*i),vector_lights=[[(math.sin(5*i*math.pi/180),1,0.6),(1,1,3)],[(0,1,1),(1,1,1)]])

        #params_dict = {"mass_center": (650, 650, 650), "south_north_vector": (0, 1, 0) , "greenwich_vector": (1, 0, 0),
        #            "greenwich_rotation" : 3*i*np.pi / 180,"south_north_rotation" : i*12*np.pi / 180,"shift_vector":(200,200,200)}
        params_dict = {"mass_center": (0, 0, 0), "south_north_vector": (0, 1, 0) , "greenwich_vector": (1, 0, 0),
                "greenwich_rotation" : 2*i*np.pi / 180,"south_north_rotation" : 2*i*np.pi / 180,"shift_vector":(-200+19*i,-200,-200)}
        #tosi outo bugi, south_north_rotation 35*np.pi/180 EI BUGAA south_north_rotation 3*np.pi/180 BUGAA
        #ja south_north_rotation : 3*i*np.pi / 180 EI BUGAA
        params_dict2 = {"mass_center": (0, 0, 0), "south_north_vector": (0, 2, 0) , "greenwich_vector": (2, 0, 0),
                "greenwich_rotation" : -3*i*np.pi / 180,"south_north_rotation" : 0*i*np.pi / 180,"shift_vector":(+200-190*i,+200,-200)}

        params_dict3 = {"mass_center": (0, 0, 0), "south_north_vector": (1, 1, 0) , "greenwich_vector": (1, -1, 1),
                "greenwich_rotation" : 1*i*np.pi / 180,"south_north_rotation" :np.pi / 180,"shift_vector":(800-20*i,400,400)}



        condition=Conditions(background_light=(1+math.sin(i/10),2.5,2.2),vector_lights=[[(1,1,0.6),(1,1,3)],[(0,1,1),(1,1,1)]])

        tr_param=TransformationParameters.from_dict(params_dict)
        tr_param2=TransformationParameters.from_dict(params_dict2)
        tr_param3=TransformationParameters.from_dict(params_dict3) 

        camera_point = (3020, 3000, 3000)
        camera_vector =(-800.01,-800.01,-800.05)




        mesh=Mesh3D(inside_color=(0.8,0,0.2))
        #print("MESH",mesh.mesh_dict_list)
        object3d_new=Object3D(tr_param, dict_list=mesh.mesh_dict_list)
        object3d_new.save_object3d_to_file("taytettyyodalierio.json")

        #object3d_new=load_object3d_from_file("3Dobjects/kaksi.json",tr_param)
        #object3d_second=load_object3d_from_file("omenalierio.json",tr_param2)
        #object3d_third=load_object3d_from_file("3Dobjects/ilo.json",tr_param3)
        #frame=Frame([object3d_new,object3d_second,object3d_third],camera_vector,camera_point,condition)
        frame=Frame([object3d_new],camera_vector,camera_point,condition)
        object3d_new.tr_param=tr_param

        #object3d_new.tr_param=tr_param
        #object3d_new.order_by_distance(camera_point)
        temp_str=frame.composite_3Dobject_to_temp_str()


        #temp_str=object3d_new.Object3D_to_temp_str(camera_point,camera_vector,tr_param,condition)
        PngMaker.save_drawing_as(temp_str,"kuvatus.txt")
        #HUOM NOTE, kannattaa olla top_letf arvot noin (-width/2,height/2)
        PngMaker.draw_drawing(temp_str,width=800,height=600,topleft=(-400,300),bg_color=(0.8,0.8,0.8),save_name="pngs\\Face2Dmove7\\"+str(100000+i),style="basic")

    #KESKEN. Piirtää jo kuvsn, mmutta onpa kumma kuva. Miksi ei parempi?