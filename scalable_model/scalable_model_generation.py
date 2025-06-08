import json
import getopt
from pickle import FALSE
import sys
import random
import os
from faker import Faker
import shapely
from geopy import distance
from shapely.affinity import affine_transform
from shapely.geometry import Point, Polygon, MultiLineString, LineString
from shapely.ops import triangulate
from shapely import affinity
from shapely.geometry.multipolygon import MultiPolygon
from scipy.spatial import Voronoi
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
import shapely.geometry
import shapely.ops
import trimesh

def convert_to_cartesian(poly):
    # create poly from coordinates

    box = poly.minimum_rotated_rectangle
    # get coordinates of polygon vertices
    x, y = box.exterior.coords.xy
    # get length of bounding box edges
    edge_length = (distance.distance(([x[0], y[0]]), (x[1], y[1])).m, distance.distance(([x[1], y[1]]), (x[2], y[2])).m)

    # edge_length = (Point(x[0], y[0]).distance(Point(x[1], y[1])), Point(x[1], y[1]).distance(Point(x[2], y[2])))

    # get length of polygon as the longest edge of the bounding box
    length = max(edge_length)

    # get width of polygon as the shortest edge of the bounding box
    width = min(edge_length)

    return (Polygon([(0, 0), (length, 0), (length, width), (0, width), (0, 0)]))


def random_points_within(poly, num_points):
    min_x, min_y, max_x, max_y = poly.bounds

    points = []

    while len(points) < num_points:
        random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
        if (random_point.within(poly)):
            points.append(random_point)
            # points.append(random_point.centroid.coords[0])

    return points


# https://gist.github.com/sgillies/465156#file_cut.py

def cut(line, distance):
    # Cuts a line in two at a distance from its starting point
    if distance <= 0.0 or distance >= line.length:
        return [shapely.geometry.LineString(line)]
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [
                shapely.geometry.LineString(coords[:i + 1]),
                shapely.geometry.LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return shapely.geometry.LineString(coords[:i] + [(cp.x, cp.y)])


# usage message
def usage():
    print("Usage message here! TBA")


def main(argv):
    # command line arguments check
    # number = 0
    # try:
    #     opts, args = getopt.getopt(argv, "hn:", ["number="])
    # except getopt.GetoptError:
    #     usage()
    #     sys.exit(2)
    # # parse command line args
    # for opt, arg in opts:
    #     if opt == '-h':
    #         usage()
    #         sys.exit()
    #     elif opt in ("-n", "--number"):
    #         number = int(arg)
    # print(opts)

    ngsild_room = []
    ngsild_building = []
    ngsild_door = []
    ngsild_windows = []
    ngsild_floor = []


    rec_big = [(25.107879638671875, 35.31064272673245), (25.1491641998291, 35.31064272673245),
               (25.1491641998291, 35.33655353682269), (25.107879638671875,
                                                       35.33655353682269), (25.107879638671875, 35.31064272673245)]

    fake = Faker()
    device_categories = ["Amazon Echo", "Belkin Motion Sensor", "Belkin Switch", "Blipcate BP Meter", "Dropcam",
                         "HP Printer", "iHome PowerPlug", "LiFX Bulb", "NEST Smoke Sensor", "Netatmo Camera",
                         "Netatmo Weather Station", "Pixstart Photo Frame", "Samsung Smart Cam", "Smart Things",
                         "TP-Link Camera", "TP-Link Plug", "Triby Speaker", "Whitings Baby Monitor", "Whitings Scale",
                         "Whitings Sleep Sensor"]

    # device_categories=["actuator", "beacon", "endgun", "HVAC", "implement", "irrSection", "irrSystem", "meter", "multimedia", "network", "sensor"]
    device_controlled_properties = ["airPollution", "atmosphericPressure", "averageVelocity", "batteryLife",
                                    "batterySupply", "cdom", "conductance", "conductivity", "depth", "eatingActivity",
                                    "electricityConsumption", "energy", "fillingLevel", "freeChlorine",
                                    "gasConsumption", "gateOpening", "heading", "humidity", "light", "location",
                                    "milking", "motion", "movementActivity", "noiseLevel", "occupancy", "orp", "pH",
                                    "power", "precipitation", "pressure", "refractiveIndex", "salinity", "smoke",
                                    "soilMoisture", "solarRadiation", "speed", "tds", "temperature", "trafficFlow",
                                    "tss", "turbidity", "waterConsumption", "waterFlow", "waterLevel", "waterPollution",
                                    "weatherConditions", "weight", "windDirection", "windSpeed"]
    building_categories = ["apartments", "bakehouse", "barn", "bridge", "bungalow", "bunker", "cathedral", "cabin",
                           "carport", "chapel", "church", "civic", "commercial", "conservatory", "construction",
                           "cowshed", "detached", "digester", "dormitory", "farm", "farm_auxiliary", "garage",
                           "garages", "garbage_shed", "grandstand", "greenhouse", "hangar", "hospital", "hotel",
                           "house", "houseboat", "hut", "industrial", "kindergarten", "kiosk", "mosque", "office",
                           "parking", "pavilion", "public", "residential", "retail", "riding_hall", "roof", "ruins",
                           "school", "service", "shed", "shrine", "stable", "stadium", "static_caravan", "sty",
                           "synagogue", "temple", "terrace", "train_station", "transformer_tower", "transportation",
                           "university", "warehouse", "water_tower"]

    b_id = 0
    flr_id = 0
    dev_id = 0
    r_id = 0
    dr_id = 0
    wind_id = 0

    # test polygons

    list1 = []
    shape = Polygon([(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)])

    random1 = random.randint(100, 500)
    random2 = random.randint(100, 500)
    rec = [(0, 0), (0, random1), (random2, random1), (random2, 0)]

    # use for device location
    points = random_points_within(shape, 1)

    # take wall from room and create doors and windows
    x = []
    for qs in list(shape.exterior.coords):
        x.append(qs)

    selected = random.randint(0, len(list(shape.exterior.coords)) - 2)

    linetest = shapely.geometry.LineString([x[selected], x[selected + 1]])

    rand = random.uniform(0.2, linetest.length)
    test = cut(linetest, rand)

    try:
        max_num_of_communities = int(input("Enter the number of communities you want to simulate data for: "))
    except ValueError:
        print("Input is not an interger, exiting....")
        exit(0)

    max_num_of_buildings = 1
    max_num_of_floors = 3
    max_num_of_rooms = 2
    max_num_of_sensors = 0
    max_num_of_doors = 0
    max_num_of_windows = 1

    # preallocate list sizes
    all_files = []
    deletion_files = []
    device_files = []

    for _ in range(max_num_of_communities):
        all_files.append([0])
        deletion_files.append([0])
        device_files.append([0])

    howmany = max_num_of_communities + 3 * int(max_num_of_communities / 2)
    tt = random.randint(1, howmany)
    while (howmany % tt != 0):
        tt = random.randint(1, howmany)

    list1.append(tt)
    list1.append(howmany // tt)
    random.shuffle(list1)
    nx = list1[0]
    ny = list1[1]
    # nx, ny = 2, 4  # number of columns and rows

    polygon = Polygon(rec_big)
    #
    minx, miny, maxx, maxy = polygon.bounds
    dx = (maxx - minx) / nx  # width of a small part
    dy = (maxy - miny) / ny  # height of a small part
    horizontal_splitters = [shapely.geometry.LineString([(minx, miny + i * dy), (maxx, miny + i * dy)]) for i in
                            range(ny)]
    vertical_splitters = [shapely.geometry.LineString([(minx + i * dx, miny), (minx + i * dx, maxy)]) for i in
                          range(nx)]
    splitters = horizontal_splitters + vertical_splitters

    community_areas_shuffled = []
    community_areas = polygon
    for splitter in splitters:
        community_areas = MultiPolygon(shapely.ops.split(community_areas, splitter))
    for shuffling in community_areas.geoms:
        community_areas_shuffled.append(shuffling)
        random.shuffle(community_areas_shuffled)

    for i in range(max_num_of_communities):
        print("Community_" + str(i))
        buildings = []
        rand_buildings = random.randint(1, max_num_of_buildings)

        community_id = "urn:ngsi-ld:community:communityn_" + str(i)

        # slicing needs to be fixed to allow for normal buildings, leave it as is for now
        list1 = []
        howmany = max_num_of_buildings + max_num_of_buildings
        tt = random.randint(1, howmany)

        # find a way to make this quicker
        while (howmany % tt != 0):
            tt = random.randint(1, howmany)
        # tt=1

        list1.append(tt)
        list1.append(howmany // tt)
        random.shuffle(list1)
        nx = list1[0]
        ny = list1[1]
        # nx, ny = 2, 4  # number of columns and rows

        polygon = Polygon(community_areas_shuffled[i])
        #
        minx, miny, maxx, maxy = polygon.bounds
        dx = (maxx - minx) / nx  # width of a small part
        dy = (maxy - miny) / ny  # height of a small part
        horizontal_splitters = [shapely.geometry.LineString([(minx, miny + i * dy), (maxx, miny + i * dy)]) for i in
                                range(ny)]
        vertical_splitters = [shapely.geometry.LineString([(minx + i * dx, miny), (minx + i * dx, maxy)]) for i in
                              range(nx)]
        splitters = horizontal_splitters + vertical_splitters

        building_areas_shuffled = []
        building_areas = polygon
        it = 0
        for splitter in splitters:
            print("iteration" + str(it))
            it += 1
            building_areas = MultiPolygon(shapely.ops.split(building_areas, splitter))
        for shuffling in building_areas.geoms:
            building_areas_shuffled.append(shuffling)
            random.shuffle(building_areas_shuffled)

        # (max_num communities)
        for g in range(rand_buildings):
            print("Building_" + str(g))
            # (1-max_num buildings)
            # generate building inside community without overlapping with other buildings

            floors = []
            rand_floors = random.randint(max_num_of_floors, max_num_of_floors)
            # (1-max_num floors)
            building_id = "urn:ngsi-ld:building:community" + str(i) + "buildingn_" + str(b_id)
            b_id += 1
            buildings.append(building_id)
            for h in range(rand_floors):
                rooms = []
                rand_rooms = random.randint(max_num_of_rooms, max_num_of_rooms)
                # (1-max_num floors)
                floor_id = "urn:ngsi-ld:floor:community" + str(i) + "floorn_" + str(flr_id)
                flr_id += 1
                floors.append(floor_id)
                # generate floor is
                # generate floor shape inside of building shape or according to building shape
                floor_shape = convert_to_cartesian(building_areas_shuffled[g])
                list1 = []
                howmany = rand_rooms
                tt = random.randint(1, howmany)

                # find a way to make this quicker
                while (howmany % tt != 0):
                    tt = random.randint(1, howmany)
                # tt=1

                list1.append(tt)
                list1.append(howmany // tt)
                random.shuffle(list1)
                nx = list1[0]
                ny = list1[1]
                # nx, ny = 2, 4  # number of columns and rows

                polygon = floor_shape
                #
                minx, miny, maxx, maxy = polygon.bounds
                dx = (maxx - minx) / nx  # width of a small part
                dy = (maxy - miny) / ny  # height of a small part
                horizontal_splitters = [shapely.geometry.LineString([(minx, miny + i * dy), (maxx, miny + i * dy)]) for
                                        i in range(ny)]
                vertical_splitters = [shapely.geometry.LineString([(minx + i * dx, miny), (minx + i * dx, maxy)]) for i
                                      in range(nx)]
                splitters = horizontal_splitters + vertical_splitters

                room_areas_shuffled = []
                room_areas = polygon
                it = 0
                for splitter in splitters:
                    print("iteration" + str(it))
                    it += 1
                    room_areas = MultiPolygon(shapely.ops.split(room_areas, splitter))
                for shuffling in room_areas.geoms:
                    room_areas_shuffled.append(shuffling)
                    random.shuffle(room_areas_shuffled)

                    # floor_shape=convert_to_cartesian(building_areas_shuffled[g])

                for k in range(rand_rooms):
                    devices = []
                    windows = []
                    doors = []

                    # (1-max_num rooms)
                    # generate a room id
                    room_id = "urn:ngsi-ld:Room:community" + str(i) + "roomn_" + str(r_id)

                    r_id += 1

                    rand_sensors = random.randint(0, 0)
                    rand_doors = random.randint(max_num_of_doors, max_num_of_doors)
                    rand_windows = random.randint(max_num_of_windows, max_num_of_windows)
                    # generate room "shape" inside of floor shape, without overlapping with other rooms

                    for l in range(rand_sensors):
                        # (0-max_num sensors)
                        # roll the dice, if zero then no sensors in room
                        # add to total sensors of community
                        # generate a sensor id
                        # generate room "shape" inside of floor shape
                        device_id = "urn:ngsi-ld:Device:community" + str(i) + ":devicen_" + str(dev_id)

                        dev_id += 1

                        devices.append(device_id)

                        json_dump_device = {"id": device_id,
                                            "type": "Device",
                                            "category": {"type": "Property",
                                                         "value": str(random.choice(device_categories))},
                                            "batteryLevel": {"type": "Property", "value": str(random.random())},
                                            "controlledProperty": {"type": "Property", "value": str(
                                                random.choice(device_controlled_properties))},
                                            "deviceState": {"type": "Property",
                                                            "value": str(random.choice(["ok", "not_ok"]))},
                                            "ipAddress": {"type": "Property", "value": fake.ipv4()},
                                            "mcc": {"type": "Property", "value": "202"},
                                            "mnc": {"type": "Property", "value": "02"},
                                            "rssi": {"type": "Property", "value": str(random.random())},
                                            "serialNumber": {"type": "Property", "value": fake.pystr_format()},
                                            "value": {"type": "Property", "value": "100000000000000"},
                                            "relativePosition": {"type": "Property", "value": shapely.geometry.mapping(
                                                random_points_within(room_areas_shuffled[k], 1)[0])},
                                            "@context": ["https://smartdatamodels.org/context.jsonld",
                                                         "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]
                                            }

                        all_files[i].append(json_dump_device)
                        device_files.append(json_dump_device)
                        deletion_files[i].append(device_id)
                    for m in range(rand_doors):
                        door_id = "urn:ngsi-ld:Door:community" + str(i) + ":doorn_" + str(dr_id)

                        doors.append(door_id)

                        dr_id += 1
                        shape = room_areas_shuffled[k]
                        x = []
                        for qs in list(shape.exterior.coords):
                            x.append(qs)

                        selected = random.randint(0, len(list(shape.exterior.coords)) - 2)

                        linetest = shapely.geometry.LineString([x[selected], x[selected + 1]])
                        pt = []
                        for v in range(2):
                            pt.append(linetest.interpolate(random.random(), True))

                        test = shapely.geometry.LineString([pt[0], pt[1]])
                        # rand=random.uniform(0.5,linetest.length)
                        # test=cut(linetest,rand)

                        json_dump_door = {"id": door_id,
                                          "type": "Door",
                                          "relativePosition": {"type": "Property",
                                                               "value": shapely.geometry.mapping(test)},
                                          "@context": [
                                              "https://gitlab.isl.ics.forth.gr/api/v4/projects/82/repository/files/ngsild-models%2FBuilding%2Fcontext.json/raw",
                                              "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]
                                          }
                        all_files[i].append(json_dump_door)
                        deletion_files[i].append(door_id)
                        ngsild_door.append(json_dump_door)

                        # 1-max doors
                    for n in range(rand_windows):
                        windows_id = "urn:ngsi-ld:Window:community" + str(i) + ":windown_" + str(wind_id)

                        windows.append(windows_id)

                        wind_id += 1

                        shape = room_areas_shuffled[k]
                        x = []
                        for qs in list(shape.exterior.coords):
                            x.append(qs)

                        selected = random.randint(0, len(list(shape.exterior.coords)) - 2)

                        linetest = shapely.geometry.LineString([x[selected], x[selected + 1]])

                        pt = []
                        for v in range(2):
                            pt.append(linetest.interpolate(random.random(), True))
                        test = shapely.geometry.LineString([pt[0], pt[1]])

                        json_dump_window = {"id": windows_id,
                                            "type": "Window",
                                            "relativePosition": {"type": "Property",
                                                                 "value": shapely.geometry.mapping(test)},
                                            "@context": [
                                                "https://gitlab.isl.ics.forth.gr/api/v4/projects/82/repository/files/ngsild-models%2FBuilding%2Fcontext.json/raw",
                                                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]
                                            }
                        all_files[i].append(json_dump_window)
                        deletion_files[i].append(windows_id)

                        ngsild_windows.append(json_dump_window)

                        # save ids in list to have room relationships
                    #
                    rooms.append(room_id)

                    json_dump_room = {"id": room_id,
                                      "type": "Room",
                                      "name": {"type": "Property",
                                               "value": room_id.split("community")[-1]},
                                      "relativePosition": {"type": "Property",
                                                           "value": shapely.geometry.mapping((room_areas_shuffled[k]))},
                                      "numberOfDoors": {"type": "Property", "value": str(rand_doors)},
                                      "numberOfWindows": {"type": "Property", "value": str(rand_windows)},
                                      "doorsInRoom": {"type": "Relationship", "value": str(doors)},
                                      "windowsInRoom": {"type": "Relationship", "value": str(windows)},
                                      "onfloor": {"type": "Relationship", "value": floor_id},
                                      "sensors": {"type": "Relationship", "value": str(devices)},
                                      "@context": [
                                          "https://gitlab.isl.ics.forth.gr/api/v4/projects/82/repository/files/ngsild-models%2FBuilding%2Fcontext.json/raw",
                                          "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]
                                      }
                    all_files[i].append(json_dump_room)
                    deletion_files[i].append(room_id)

                    ngsild_room.append(json_dump_room)

                json_dump_floor = {"id": floor_id,
                                   "type": "Floor",
                                   "relativePosition": {"type": "Property", "value": shapely.geometry.mapping(
                                       convert_to_cartesian(building_areas_shuffled[g]))},
                                   "name": {"type": "Property", "value": fake.bothify(text='Room Name: ????-########')},
                                   "numberOfRooms": {"type": "Property", "value": str(rand_rooms)},
                                   "roomsOnFloor": {"type": "Relationship", "value": str(rooms)},
                                   "withinBuilding": {"type": "Relationship", "value": str(building_id)},
                                   "location": {"type": "Property",
                                                "value": shapely.geometry.mapping(building_areas_shuffled[g])},
                                   "@context": "[" + "https://gitlab.isl.ics.forth.gr/api/v4/projects/82/repository/files/ngsild-models%2FBuilding%2Fcontext.json/raw" + "," + "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld" + "]"
                                   }
                all_files[i].append(json_dump_floor)
                deletion_files[i].append(floor_id)

                ngsild_floor.append(json_dump_floor)

            json_dump_building = {"id": building_id,
                                  "type": "Building",
                                  "address": {"type": "Property", "value": fake.address()},
                                  "category": {"type": "Property", "value": str(random.choice(building_categories))},
                                  "InCommunity": {"type": "Relationship", "value": str(community_id)},
                                  "dataProvider": {"type": "Property", "value": fake.bs()},
                                  "description": {"type": "Property", "value": fake.sentence(nb_words=3)},
                                  "floorsAboveGround": {"type": "Property", "value": rand_floors},
                                  "floorsBelowGround": {"type": "Property", "value": "0"},
                                  "mapUrl": {"type": "Property", "value": fake.url()},
                                  "source": {"type": "Property", "value": fake.url()},
                                  "location": {"type": "Property",
                                               "value": shapely.geometry.mapping(building_areas_shuffled[g])},
                                  "@context": [
                                      "https://gitlab.isl.ics.forth.gr/api/v4/projects/82/repository/files/ngsild-models%2FBuilding%2Fcontext.json/raw",
                                      "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]
                                  }
            all_files[i].append(json_dump_building)
            deletion_files[i].append(building_id)

            ngsild_building.append(json_dump_building)

        json_dump_community = {"id": community_id,
                               "type": "Community",
                               "HasBuildings": {"type": "Relationship", "value": str(buildings)},
                               "name": {"type": "Property", "value": fake.bs()},
                               "location": {"type": "Property",
                                            "value": shapely.geometry.mapping(community_areas_shuffled[i])},
                               "@context": [
                                   "https://gitlab.isl.ics.forth.gr/api/v4/projects/82/repository/files/ngsild-models%2FBuilding%2Fcontext.json/raw",
                                   "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]
                               }
        all_files[i].append(json_dump_community)
        deletion_files[i].append(community_id)

        all_files[i] = json.dumps(all_files[i], indent=4)
        deletion_files[i] = json.dumps(deletion_files[i], indent=4)

        mode = 'w'

        with open("generated_entities_community_" + str(i) + ".ngsild", mode) as f:
            f.write(str(all_files[i]))
        with open("generated_entities_delete_community_" + str(i) + ".ngsild", mode) as f:
            f.write(str(deletion_files[i]))
    device_files = json.dumps(device_files, indent=4)
    with open("all_devices.ngsild", mode) as f:
        f.write(str(device_files))

    ngsild_room, ngsild_door, ngsild_windows = process_json_data(ngsild_room, ngsild_door, ngsild_windows)

    with open("ngsild_model/scalable_Building.ngsild", "w") as f:
        f.write(str(json.dumps(ngsild_building, indent=4)))
    with open("ngsild_model/scalable_Rooms.ngsild", "w") as f:
        f.write(str(json.dumps(ngsild_room, indent=4)))
    with open("ngsild_model/scalable_Floors.ngsild", "w") as f:
        f.write(str(json.dumps(ngsild_floor, indent=4)))
    with open("ngsild_model/scalable_Windows.ngsild", "w") as f:
        f.write(str(json.dumps(ngsild_windows, indent=4)))
    with open("ngsild_model/scalable_Doors.ngsild", "w") as f:
        f.write(str(json.dumps(ngsild_door, indent=4)))

def get_floor_number(floor_id):
    # 假设楼层ID的格式为 "urn:ngsi-ld:floor:community0floorn_X"
    # 提取楼层编号
    return int(floor_id.split('_')[-1])

def find_room_by_id(rooms, room_id):
    for room in rooms:
        if room['id'] == room_id:
            return room
    return None

def generate_3d_coordinates(coordinates, height):
    # 生成3D坐标
    base_coords = [list(coord) + [0] for coord in coordinates]
    top_coords = [list(coord) + [height] for coord in coordinates]
    return base_coords + top_coords

def generate_3d_faces(num_base_vertices):
    # 生成3D面
    faces = []
    # 底面和顶面
    faces.extend([[i, (i + 1) % num_base_vertices, (i + 1) % num_base_vertices + num_base_vertices, i + num_base_vertices] for i in range(num_base_vertices)])
    return faces

def process_json_data(rooms, doors, windows):
    processed_rooms = []
    processed_doors = []
    processed_windows = []

    # 处理rooms
    for room in rooms:
        try:
            floor_id = room["onfloor"]["value"]
            floor_number = get_floor_number(floor_id)
            height = floor_number * 3  # 每层楼3米

            geometry_type = room["relativePosition"]["value"]["type"]
            coordinates = room["relativePosition"]["value"]["coordinates"]

            if geometry_type == "Polygon":
                polygon_coords = coordinates[0]
                polygon = Polygon(polygon_coords)

                if not polygon.is_valid:
                    raise ValueError("Invalid polygon in room with id: {}".format(room["id"]))

                # 生成3D坐标和面
                vertices = generate_3d_coordinates(polygon_coords, height)
                faces = generate_3d_faces(len(polygon_coords))

                room['relativePosition']['value']['coordinates'] = vertices
                room['relativePosition']['value']['faces'] = faces

            processed_rooms.append(room)

        except Exception as e:
            print(f"Error processing room with id {room['id']}: {e}")

    # 处理doors和windows
    for door in doors:
        try:
            door_id = door['id']
            for room in rooms:
                if door_id in room.get("doorsInRoom", {}).get("value", []):
                    floor_id = room["onfloor"]["value"]
                    floor_number = get_floor_number(floor_id)
                    height = floor_number * 3  # 每层楼3米

                    coordinates = door["relativePosition"]["value"]["coordinates"]
                    geometry_type = door["relativePosition"]["value"]["type"]

                    if geometry_type == "LineString":
                        line_coords = coordinates
                        vertices = generate_3d_coordinates(line_coords, height)
                        faces = generate_3d_faces(len(line_coords))

                        door['relativePosition']['value']['coordinates'] = vertices
                        door['relativePosition']['value']['faces'] = faces
                    processed_doors.append(door)
                    break

        except Exception as e:
            print(f"Error processing door with id {door['id']}: {e}")

    for window in windows:
        try:
            window_id = window['id']
            for room in rooms:
                if window_id in room.get("windowsInRoom", {}).get("value", []):
                    floor_id = room["onfloor"]["value"]
                    floor_number = get_floor_number(floor_id)
                    height = floor_number * 3  # 每层楼3米

                    coordinates = window["relativePosition"]["value"]["coordinates"]
                    geometry_type = window["relativePosition"]["value"]["type"]

                    if geometry_type == "LineString":
                        line_coords = coordinates
                        vertices = generate_3d_coordinates(line_coords, height)
                        faces = generate_3d_faces(len(line_coords))

                        window['relativePosition']['value']['coordinates'] = vertices
                        window['relativePosition']['value']['faces'] = faces
                    processed_windows.append(window)
                    break

        except Exception as e:
            print(f"Error processing window with id {window['id']}: {e}")

    return processed_rooms, processed_doors, processed_windows


if __name__ == "__main__":
    main(sys.argv[1:])