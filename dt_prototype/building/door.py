from read_coordinates import read_file
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from room import create_surfaces
from itertools import groupby
from collections import Counter


def group_key(tup):
    return tup[2]

def agglomerate_per_height(windows): #Separates coordinates according to the maximum and minimum height
    windows_sorted = [sorted(sublist, key=group_key) for sublist in windows]
    groups = groupby(sorted(windows_sorted, key=lambda z: group_key(z[2])), key=lambda z: group_key(z[2]))
    d = [(key, list(group)) for key, group in groups]
    min_z = float("inf")
    max_z = 0
    cordinates = dict()
    
    for value in d:
        if value[0] > max_z:
            list_max = value[1]
            max_z = value[0]
        if value[0] < min_z: 
            list_min = value[1]
            min_z = value[0]

    cordinates['max'] = list_max #Return points with maximum height
    cordinates['min'] = list_min #Return points with minimum height
    

    return cordinates['max'], cordinates['min']
 

def create_door(point_min, point_max): #Draw door according to maximum and minimum coordinates
    coordinates = None
    for cord in range(0,3):
        if point_min[cord] == point_max[cord]:
            if cord == 0:
                sup_left = tuple((point_min[0], point_min[1], point_max[2]))
                inf_right = tuple((point_min[0], point_max[1], point_min[2]))
            if cord == 1:
                sup_left = tuple((point_min[0], point_min[1], point_max[2]))
                inf_right = tuple((point_max[0], point_min[1], point_min[2]))
            if cord == 2:
                sup_left = tuple((point_min[0], point_max[1], point_min[2]))
                inf_right = tuple((point_max[0], point_min[1], point_min[2]))
            coordinates = [point_min, sup_left, point_max, inf_right]       
            break    
       
    return coordinates  


def extremities(door): #Get coordinates of from extremities of the door
    result = list()
    position = list(map(list, zip(*door)))
    maximo = [max(pos) for pos in position]
    
    t = list(map(list, zip(*maximo))) #Get the values from coordinates in the extremity
    point_max = [max(pos) for pos in t] 
    point_min = [min(pos) for pos in t]

    result.append(create_door(tuple(point_min), tuple(point_max))) #Create door using maximum and minimum points
    return result
    
   
def main():
    results_doors, faces = read_file("../two room_Doors.ngsild")
    print("Number of doors: ", len(results_doors))
    surfaces = list()
    for door in results_doors:
        s, t = agglomerate_per_height(door)
        square1 = create_surfaces(s, 2) #Ignore surfaces with the same coordinate z
        square2 = create_surfaces(t, 2) 
        d = square1+square2
        r = extremities(d)
        surfaces.extend(r)
        
   
    
    #INDIVIDUAL PLOT
   
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # for pos in range(len(surfaces)): 
    #     x, y, z = zip(*surfaces[pos])
    #     ax.scatter(x, y, z, c='r', marker='o')
    #     faces_collection = Poly3DCollection([[(x[i], y[i], z[i]) for i in range(4)] for point in surfaces[pos]], alpha=0.5, linewidths=1, edgecolors='r')
    #     ax.add_collection3d(faces_collection)
    # ax.set_xlabel('X')
    # ax.set_ylabel('Y')
    # ax.set_zlabel('Z')
    # plt.show()

    
    return surfaces

if __name__ == "__main__":
    main()