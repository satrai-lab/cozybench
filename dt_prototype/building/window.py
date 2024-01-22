from read_coordinates import read_file
from itertools import groupby
from room import create_surfaces
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from door import agglomerate_per_height
      

def medium_point(surfaces): #Calculate the medium point of a surface
    vertices = [vertice for superficie in surfaces for vertice in superficie]
    # Calculate the medium point of the vertices
    medium_point = tuple(sum(coord) / len(vertices) for coord in zip(*vertices))

    return medium_point


def create_medium_point(medium_point, plan, tamanho=1.0): #draw the surface of the medium point
    if plan == 0:
        point1 = (medium_point[0], medium_point[1] - tamanho / 2, medium_point[2] - tamanho / 2)
        point2 = (medium_point[0], medium_point[1] - tamanho / 2, medium_point[2] + tamanho / 2)
        point3 = (medium_point[0], medium_point[1] + tamanho / 2, medium_point[2] + tamanho / 2)
        point4 = (medium_point[0], medium_point[1] + tamanho / 2, medium_point[2] - tamanho / 2)
    elif plan == 1:
        point1 = (medium_point[0] - tamanho / 2, medium_point[1], medium_point[2] - tamanho / 2)
        point2 = (medium_point[0] - tamanho / 2, medium_point[1], medium_point[2] + tamanho / 2)
        point3 = (medium_point[0] + tamanho / 2, medium_point[1], medium_point[2] + tamanho / 2)
        point4 = (medium_point[0] + tamanho / 2, medium_point[1], medium_point[2] - tamanho / 2)
    else:
        point1 = (medium_point[0] - tamanho / 2, medium_point[1] - tamanho / 2, medium_point[2])
        point2 = (medium_point[0] - tamanho / 2, medium_point[1] + tamanho / 2, medium_point[2])
        point3 = (medium_point[0] + tamanho / 2, medium_point[1] + tamanho / 2, medium_point[2])
        point4 = (medium_point[0] + tamanho / 2, medium_point[1] - tamanho / 2, medium_point[2])

    return [point1, point2, point3, point4]

def in_which_plan(surfaces): #Detect in which plan is the window
    coordinates_x = set(x for x, _, _ in surfaces)
    coordinates_y = set(y for _, y, _ in surfaces)
    coordinates_z = set(z for _, _, z in surfaces)
    if len(coordinates_z) == 1:
        return 2
    elif len(coordinates_x) == 1:
        return 0
    elif len(coordinates_y) == 1:
        return 1
    else:
        return ValueError
        
            
def main():
    results_windows, faces = read_file("../two room_Windows.ngsild")
    print("Number of windows: ", len(results_windows))
    surfaces = list()
    for window in results_windows:
        s, t = agglomerate_per_height(window) #Get only points with the extremities of the window
        u = create_surfaces(s, 3) #Create surfaces from these points
        v = create_surfaces(t, 3)
        w = u+v
        plan = in_which_plan(w[0])
        medium = medium_point(w) #Find the medium point of these surfaces
        n = create_medium_point(medium, plan) #Create new surface from this medium point
        surfaces.extend([n])

    

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