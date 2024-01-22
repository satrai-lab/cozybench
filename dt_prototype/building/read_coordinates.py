import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def plot_3d_objects(ax, coordinates, faces):
    x, y, z = zip(*coordinates)
    
    # # Scatter plot for individual points
    ax.scatter(x, y, z, c='r', marker='o')

    # # Create a Poly3DCollection for the faces
    faces_collection = Poly3DCollection([[(x[i], y[i], z[i]) for i in face] for face in faces],
                                         alpha=0.5, linewidths=1, edgecolors='r')
    
    ax.add_collection3d(faces_collection)
    
    return [[(x[i], y[i], z[i]) for i in face] for face in faces]
    


def read_file(filename):
    json_objects = json.load(open(filename, "r"))
    results = list()
    surfaces = list()
    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Iterate over each object in the JSON file
    for obj in json_objects:
        # Extract coordinates and faces from the current object
        coordinates = obj['relativePosition']['value']['coordinates']
        faces = obj['relativePosition']['value']['faces']
        
        # Plot 3D objects
        cord_faces = plot_3d_objects(ax, coordinates, faces)
        results.append(cord_faces)
        surfaces.append(faces)

    # Set labels for the axes
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Display the 3D plot
    plt.show()
    return results, surfaces



def read_room(filename):
    json_objects = json.load(open(filename, "r"))
    results = list()
    names = list()
    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Iterate over each object in the JSON file
    for obj in json_objects:
        # Extract coordinates and faces from the current object
        coordinates = obj['relativePosition']['value']['coordinates']
        space_name = obj['name']['value']
        faces = obj['relativePosition']['value']['faces']
        
        # Plot 3D objects
        cord_faces = plot_3d_objects(ax, coordinates, faces)
        results.append(cord_faces)
        names.append(space_name)

    # Set labels for the axes
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Display the 3D plot
    # plt.show()
    return results, names



