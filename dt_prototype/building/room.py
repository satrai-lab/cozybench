import numpy as np
from itertools import permutations
from read_coordinates import read_room


def same_coordinates(cord1, cord2): #Compare coordinates
    return np.allclose(cord1, cord2, 1e-6)

def sobreposition(face1, face2):
    face1 = np.array(face1)
    face2 = np.array(face2)
    p_face1 = list(permutations(face1)) #Create a list with all the permutations of the coordinates from first surface
    for p in p_face1: #Compare the coordinates yz of the permutations with the coordinates yz from second surface
        if all(same_coordinates(p[i][1], face2[i][1]) and same_coordinates(p[i][2], face2[i][2]) for i in range (len(face1))):
            return True
    return False

def calculate_width(face1, face2): #Calculate the width between two surfaces
    medium_point1 = np.mean(face1, axis=0)
    medium_point2 = np.mean(face2, axis=0)
    width = np.linalg.norm(medium_point1 - medium_point2)
    return width


def find_parallel_walls(surfaces, qtd_rooms): #Find the parallel surfaces 
    parallel_surfaces = {}
    number_surfaces = int(len(surfaces)/qtd_rooms)
    for i in range(number_surfaces): #The surfaces from a first room
        for j in range (number_surfaces, len(surfaces)): #The surfaces from a second room
            if(sobreposition(surfaces[i], surfaces[j])): #If they are parallel in the axis yz
                width = calculate_width(surfaces[i], surfaces[j])
                if parallel_surfaces.get(i) == None or width < parallel_surfaces[i][1]:
                    parallel_surfaces[i] = [j, width]          
                    parallel_surfaces[j] = [i, width]          
    return parallel_surfaces    #return dictionary of parallel walls       

def swap(coordinates, pos1, pos2):
    temp=coordinates[pos1]
    coordinates[pos1]=coordinates[pos2]
    coordinates[pos2]=temp
    return coordinates

def create_surfaces(list_points,n_cord=3): #unite the triangular surfaces in a unique surface
    surfaces = list()
    for i in range(0, len(list_points)-1): #pick a surface
            found = False
            for j in range(i+1,len(list_points)): #pick another surface
                diff_point = set(list_points[i]) - set(list_points[j])  #Get coordinates in first surface that are different in the second surface
                diff_point2 = (set(list_points[j]) - set(list_points[i])) #Get coordinate in second surface that is different in the first surface
                if len(diff_point) == 1: #if there is only one different point, they probably belong to the same surface
                    
                    diff_point = diff_point.pop()
                    diff_point2 = diff_point2.pop()
                    for cord in range(n_cord):  #Compare x,y,z of each coordinate according to the number of coordinates to compare
                        
                        if diff_point[cord] == diff_point2[cord]: #If at least one value is equal, they probably belong to same surface
                            similar_points = (set(list_points[i]) and set(list_points[j])) #Get similar points
                            new = list(filter(lambda e:e[cord]==diff_point[cord],similar_points)) #Need to verify if all points belong to the same plan, so they need to have the same coordinate
                            if len(new) == 3: #If all coordinates present the same point, they are a surface
                                forth_cord = set([tuple(diff_point)])
                                coordinates = list(similar_points.union(forth_cord)) #Set the coordinates together
                                
                                #Put points of coordinates in order to draw a square
                                if cord == 0: #if x is the same value for the 4 points
                                    coordinates.sort(key=lambda a: a[1]) #sort the points of the coordinates according the y
                                    try:  
                                        if [z[2] for z in coordinates[2:4]].index(coordinates[1][2]) != 0: #sort also the last two points according to the z
                                            coordinates = swap(coordinates, 2, 3)
                                    except ValueError:
                                        pass          
                                if cord == 1: #if y is the same value for the 4 points
                                    coordinates.sort(key=lambda a: a[0]) #sort the points of the coordinates according the x
                                    try:
                                        if [z[2] for z in coordinates[2:4]].index(coordinates[1][2]) != 0:  #sort also the last two points according to the z
                                            coordinates = swap(coordinates, 2, 3)
                                    except ValueError:
                                        pass 
                                if cord == 2: #if z is the same value for the 4 points
                                    coordinates.sort(key=lambda a: a[0]) #sort the points of the coordinates according the x
                                    try:
                                        if [y[1] for y in coordinates[2:4]].index(coordinates[1][1]) != 0: #sort also the last two points according to the y
                                            coordinates = swap(coordinates, 2, 3)
                                    except ValueError:
                                        pass          
    
                                
                                surfaces.append(coordinates)
                                found  = True
                            
                            
                                break
                    if found: #If a surface is found, stop loop and remove surface from other comparisons
                        list_points.pop(j)
                        break
    return surfaces                
    

def main():

    results_rooms, spaces = read_room("../two room_Rooms.ngsild")
    surfaces = list()
    for room in results_rooms:
        surfaces.extend(create_surfaces(room))       
    return surfaces, spaces

if __name__ == "__main__":
    main()