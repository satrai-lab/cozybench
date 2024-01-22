from eppy.modeleditor import IDF
from io import StringIO
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import room
import window
import door

class Surface:
    def __init__(self, number, object, coordinates, parallel, windows, doors, plan):
        self.number = number
        self.object = object
        self.coordinates = coordinates
        self.parallel = parallel
        self.windows = windows
        self.doors = doors
        self.plan = plan

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

def point_surface(point, surface, plan): #Verify if point is inside surface
    # method of Ray Casting
    x, y, z = point
    n = len(surface)
    intersections = 0

    for i in range(n):
        x1, y1, z1 = surface[i]
        x2, y2, z2 = surface[(i + 1) % n]

        if plan == 2:
            if ((y1 <= y < y2) or (y2 <= y < y1)) and (x < max(x1, x2)):
                intersecao = (y - y1) * (x2 - x1) / (y2 - y1) + x1
                if x < intersecao:
                    intersections += 1
        if plan == 1:            
            if ((z1 <= z < z2) or (z2 <= z < z1)) and (x < max(x1, x2)):
                intersecao = (z - z1) * (x2 - x1) / (z2 - z1) + x1
                if x < intersecao:
                    intersections += 1
        if plan == 0:            
            if ((z1 <= z < z2) or (z2 <= z < z1)) and (y < max(y1, y2)):
                intersecao = (z - z1) * (y2 - y1) / (z2 - z1) + y1
                if y < intersecao:
                    intersections += 1    

    return intersections % 2 == 1

def surfaces_sobreposition(surface1, surface2, plan):
    # Verify if any point of surface 1 is inside surface 2
    for point in surface1:
        if point_surface(point, surface2, plan):
            return True

    # Verify if any point of surface 2 is inside surface 1
    for point in surface2:
        if point_surface(point, surface1, plan):
            return True

    # If there is no point inside any surface, there is no sobreposition
    return False


def check_parallel(surface1, surface2, plan): #Check if surfaces are parallel
    if plan == window.in_which_plan(surface2):
        if surfaces_sobreposition(surface1, surface2, plan): #If there is any sobreposition of surfaces
            if int(room.calculate_width(surface1, surface2)) <= 1: #Check if surfaces are closer to each other
                value = surface1[0][plan] #If so, they belong to the same plan
                for i in range(len(surface2)):
                    point = list(surface2[i])
                    point[plan] = value
                    surface2[i] = tuple(point)
                return surface2
    return None     


def parallel_windows(surface, windows, plan): #Check which window that is parallel with the surface
    result = list()
    for w in windows:  
        if check_parallel(surface, w, plan):
            result.append(w)
    return result

def parallel_doors(surface, doors, plan): #Check which door that is parallel with the surface
    result = list()
    for d in doors:
        if check_parallel(surface, d, plan):
            result.append(d)
    return result


def main():
    surfaces, spaces = room.main() #Get surfaces of the rooms

    windows = window.main() #Get surfaces of windows

    doors = door.main() #Get surfaces of doors

    parallel_surfaces = room.find_parallel_walls(surfaces, len(spaces)) #Get dictionary of parallel walls
    print("Number of surfaces in the building: ", len(surfaces), "\n")

    n_objects = 0
    group_surfaces = list()
    for i in range(len(surfaces)):
        plan = window.in_which_plan(surfaces[i]) #Find which plan is related to surface
        w_result = parallel_windows(surfaces[i], windows, plan) #Find windows related to surface
        d_result = parallel_doors(surfaces[i], doors, plan) #Find doors related to surface
        parallel = parallel_surfaces[i] #Get informations of the wall parallel with the surface
        group_surfaces.append(Surface( i, n_objects, surfaces[i], parallel, w_result, d_result, plan))
        if parallel[0] > i:
            n_objects += len(w_result) + len(d_result) + 1
        else: 
            n_objects += 1 
    

    #Create blank idf
    iddfile = "/usr/local/EnergyPlus-23-1-0/Energy+.idd" #Configure this with the file of the library of objects from EnergyPlus
    IDF.setiddname(iddfile)
    idftxt = " "
    idf = IDF(StringIO(idftxt)) # initialize the IDF object with the file handle

    #Put building and spaces information in the idf file
    idf.newidfobject("Building", Name = "Default Building") #Provisory name of the building

    idf.newidfobject("Zone", Name = "Thermal Zone Room") #Add space to idf file


    for s in spaces:
        idf.newidfobject("Space", Name = s, Zone_Name="Thermal Zone Room") #Add space to idf file

   
    #Put constructions names
    # idf.newidfobject("Construction", Name= "ExtSlabCarpet 4in ClimateZone 1-8") #Floor
    # idf.newidfobject("Construction", Name= "ASHRAE 189.1-2009 ExtRoof IEAD ClimateZone 2-5") #Roof
    # idf.newidfobject("Construction", Name= "Interior Wall") #Interior Wall
    # idf.newidfobject("Construction", Name= "ASHRAE 189.1-2009 ExtWall Mass ClimateZone 4") #Exterior Wall
    # idf.newidfobject("Construction", Name= "Interior Window") #Interior window
    # idf.newidfobject("Construction", Name= "ASHRAE 189.1-2009 ExtWindow ClimateZone") #Exterior Window
    # idf.newidfobject("Construction", Name= "Interior Door") #Interior door
    # idf.newidfobject("Construction", Name= "Exterior Door") #Exterior door
    
    
    #Put each surface, window and door in the idf file
    n_objects = 0
    n_rooms = len(spaces)
    n_walls = int(len(surfaces)/n_rooms)
    

    for surface in group_surfaces:        
        if (surface.number % n_walls) == 0: #Get name of the room
            name = spaces[int(surface.number/n_walls)]

        if surface.plan == 2: #Surface is a roof or a floor
            if surface.coordinates[0][2] == 0: #Surface is a floor
                s_type = "Floor"
                condition = "Ground"
                sun = "NoSun"
                wind = "NoWind"
                construction_name = "ExtSlabCarpet 4in ClimateZone 1-8"
            else: #Surface is a roof
                s_type = "Roof"
                condition = "Outdoors"
                sun = "SunExposed"
                wind = "WindExposed" 
                construction_name = "ASHRAE 189.1-2009 ExtRoof IEAD ClimateZone 2-5"
            wall = width =  ""
        else: #Surface is a wall
            s_type = "Wall"      
            if surface.parallel[1] <= 1: #Interior Wall
                wall = "Face " + str(group_surfaces[surface.parallel[0]].object)
                width = surface.parallel[1]
                condition = "Surface"
                construction_name = "Interior Wall"
                sun = "NoSun"
                wind = "NoWind"
            else: #Exterior Wall
                wall = width = ""
                construction_name =  "ASHRAE 189.1-2009 ExtWall Mass ClimateZone 4"
                condition = "Outdoors"
                sun = "SunExposed"
                wind = "WindExposed" 
        #Write new Wall
        idf.newidfobject("BuildingSurface:Detailed", Name = "Face " + str(surface.object), Zone_Name = "Thermal Zone Room", Construction_Name = construction_name, Space_Name = name, Surface_Type = s_type, 
        Outside_Boundary_Condition = condition, Outside_Boundary_Condition_Object = wall,  Sun_Exposure = sun, Wind_Exposure = wind,                    
        Vertex_1_Xcoordinate =  surface.coordinates[0][0], Vertex_1_Ycoordinate = surface.coordinates[0][1], Vertex_1_Zcoordinate = surface.coordinates[0][2],
        Vertex_2_Xcoordinate =  surface.coordinates[1][0],  Vertex_2_Ycoordinate = surface.coordinates[1][1], Vertex_2_Zcoordinate = surface.coordinates[1][2], 
        Vertex_3_Xcoordinate =  surface.coordinates[2][0],  Vertex_3_Ycoordinate = surface.coordinates[2][1], Vertex_3_Zcoordinate = surface.coordinates[2][2],
        Vertex_4_Xcoordinate =  surface.coordinates[3][0],  Vertex_4_Ycoordinate = surface.coordinates[3][1], Vertex_4_Zcoordinate = surface.coordinates[3][2])
        n_objects += 1
        
        if surface.object < group_surfaces[surface.parallel[0]].object: #To not write down the same door and window twice
            if surface.windows: #If the surface has a window, write it down to idf file
                for w in surface.windows:
                    print("Detected window on surface: ", surface.number)
                    if wall != "":
                        construction_name_window = "Interior Window" 
                    else:
                        construction_name_window = "ASHRAE 189.1-2009 ExtWindow ClimateZone"

                    idf.newidfobject("FenestrationSurface:Detailed",  Name = "Face " + str(n_objects), Surface_Type = "Window", Construction_Name = construction_name_window, Building_Surface_Name = "Face " + str(surface.object), Outside_Boundary_Condition_Object = wall,
                    Vertex_1_Xcoordinate =  w[0][0], Vertex_1_Ycoordinate = w[0][1], Vertex_1_Zcoordinate = w[0][2],
                    Vertex_2_Xcoordinate =  w[1][0],  Vertex_2_Ycoordinate = w[1][1], Vertex_2_Zcoordinate = w[1][2], 
                    Vertex_3_Xcoordinate =  w[2][0],  Vertex_3_Ycoordinate = w[2][1], Vertex_3_Zcoordinate = w[2][2],
                    Vertex_4_Xcoordinate =  w[3][0],  Vertex_4_Ycoordinate = w[3][1], Vertex_4_Zcoordinate = w[3][2])
                    
                    n_objects += 1
            if surface.doors: #If the surface has a door, write it down to idf file
                for d in surface.doors:
                    print("Detected door on surface: ", surface.number) 
                    if wall != "":
                        construction_name_door = "Interior Door" 
                    else:
                        construction_name_door = "Exterior Door"
                    
                    idf.newidfobject("FenestrationSurface:Detailed",  Name = "Face " + str(n_objects), Surface_Type = "Door", Construction_Name = construction_name_door, Building_Surface_Name = "Face " + str(surface.object), Outside_Boundary_Condition_Object = wall,
                    Vertex_1_Xcoordinate =  d[0][0], Vertex_1_Ycoordinate = d[0][1], Vertex_1_Zcoordinate = d[0][2],
                    Vertex_2_Xcoordinate =  d[1][0],  Vertex_2_Ycoordinate = d[1][1], Vertex_2_Zcoordinate = d[1][2], 
                    Vertex_3_Xcoordinate =  d[2][0],  Vertex_3_Ycoordinate = d[2][1], Vertex_3_Zcoordinate = d[2][2],
                    Vertex_4_Xcoordinate =  d[3][0],  Vertex_4_Ycoordinate = d[3][1], Vertex_4_Zcoordinate = d[3][2])
                    
                    n_objects += 1
            
        

    #Save idf file in output.idf
    idf.saveas("output.idf")


    #Plot surfaces, windows and doors

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for pos in range(len(surfaces)): 
        x, y, z = zip(*surfaces[pos])
        ax.scatter(x, y, z, c='r', marker='o')
        faces_collection = Poly3DCollection([[(x[i], y[i], z[i]) for i in range(4)] for point in surfaces[pos]], alpha=0.1, linewidths=1, edgecolors='r')
        ax.add_collection3d(faces_collection)

    for pos in range(len(windows)): 
        x, y, z = zip(*windows[pos])
        ax.scatter(x, y, z, c='g', marker='x')
        faces_collection = Poly3DCollection([[(x[i], y[i], z[i]) for i in range(4)] for point in windows[pos]], alpha=0.5, linewidths=1, edgecolors='g')
        ax.add_collection3d(faces_collection)

    for pos in range(len(doors)): 
        x, y, z = zip(*doors[pos])
        ax.scatter(x, y, z, c='y', marker='>')
        faces_collection = Poly3DCollection([[(x[i], y[i], z[i]) for i in range(4)] for point in doors[pos]], alpha=0.5, linewidths=1, edgecolors='y')
        ax.add_collection3d(faces_collection)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()

if __name__ == "__main__":
    main()
