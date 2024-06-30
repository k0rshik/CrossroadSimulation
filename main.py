from simulation import Simulation
from visualization import Visualization
from road import Waypoint, Road, find_intersection
from trafic_light import TrafficLight
from math import radians

sim = Simulation()

a = 2
b = 90
c = 12
r = 3

South_start_left = Waypoint(a, b)
South_start_right = Waypoint(a + r, b)
South_end_left = Waypoint(-a, b)
South_end_right = Waypoint(-a - r, b)

South_start_left_cross = Waypoint(a, c)
South_start_right_cross = Waypoint(a + r, c)
South_end_left_cross = Waypoint(-a, c)
South_end_right_cross = Waypoint(-a - r, c)

North_start_left = Waypoint(-a, -b)
North_start_right = Waypoint(-a - r, -b)
North_end_left = Waypoint(a, -b)
North_end_right = Waypoint(a + r, -b)

North_start_left_cross = Waypoint(-a, -c)
North_start_right_cross = Waypoint(-a - r, -c)
North_end_left_cross = Waypoint(a, -c)
North_end_right_cross = Waypoint(a + r, -c)

East_start_left = Waypoint(b, -a)
East_start_right = Waypoint(b, -a - r)
East_end_left = Waypoint(b, a)
East_end_right = Waypoint(b, a + r)

East_start_left_cross = Waypoint(c, -a)
East_start_right_cross = Waypoint(c, -a - r)
East_end_left_cross = Waypoint(c, a)
East_end_right_cross = Waypoint(c, a + r)

West_start_left = Waypoint(-b, a)
West_start_right = Waypoint(-b, a + r)
West_end_left = Waypoint(-b, -a)
West_end_right = Waypoint(-b, -a - r)

West_start_left_cross = Waypoint(-c, a)
West_start_right_cross = Waypoint(-c, a + r)
West_end_left_cross = Waypoint(-c, -a)
West_end_right_cross = Waypoint(-c, -a - r)

Road(South_start_right, South_start_right_cross)
Road(North_start_right, North_start_right_cross)
Road(South_start_left, South_start_left_cross)
Road(North_start_left, North_start_left_cross)

Road(East_start_right, East_start_right_cross)
Road(West_start_right, West_start_right_cross)
Road(East_start_left, East_start_left_cross)
Road(West_start_left, West_start_left_cross)

Road(South_end_right_cross, South_end_right)
Road(North_end_right_cross, North_end_right)
Road(South_end_left_cross, South_end_left)
Road(North_end_left_cross, North_end_left)

Road(East_end_right_cross, East_end_right)
Road(West_end_right_cross, West_end_right)
Road(East_end_left_cross, East_end_left)
Road(West_end_left_cross, West_end_left)

Road(South_start_right_cross, North_end_right_cross)
Road(South_start_left_cross, North_end_left_cross)
Road(North_start_right_cross, South_end_right_cross)
Road(North_start_left_cross, South_end_left_cross)

Road(East_start_right_cross, West_end_right_cross)
Road(East_start_left_cross, West_end_left_cross)
Road(West_start_right_cross, East_end_right_cross)
Road(West_start_left_cross, East_end_left_cross)

South_start_left_cross.connect(West_end_left_cross, True, 8)
South_start_right_cross.connect(East_end_right_cross, False, 8)

West_start_left_cross.connect(North_end_left_cross, True, 8)
West_start_right_cross.connect(South_end_right_cross, False, 8)

North_start_left_cross.connect(East_end_left_cross, True, 8)
North_start_right_cross.connect(West_end_right_cross, False, 8)

East_start_left_cross.connect(South_end_left_cross, True, 8)
East_start_right_cross.connect(North_end_right_cross, False, 8)

traffic_light_durations = [600, 300, 900]
South_traffic_light = TrafficLight(10, 15, radians(0), traffic_light_durations)
South_start_left_cross.set_traffic_light(South_traffic_light)
South_start_right_cross.set_traffic_light(South_traffic_light)

North_traffic_light = TrafficLight(-10, -15, radians(180), traffic_light_durations)
North_start_left_cross.set_traffic_light(North_traffic_light)
North_start_right_cross.set_traffic_light(North_traffic_light)

East_traffic_light = TrafficLight(15, -10, radians(-90), traffic_light_durations, 2)
East_start_left_cross.set_traffic_light(East_traffic_light)
East_start_right_cross.set_traffic_light(East_traffic_light)

West_traffic_light = TrafficLight(-15, 10, radians(90), traffic_light_durations, 2)
West_start_left_cross.set_traffic_light(West_traffic_light)
West_start_right_cross.set_traffic_light(West_traffic_light)

for r1 in Road.roads:
    for r2 in Road.roads:
        if r1 is r2:
            continue
        if r1 not in Road.roads:
            continue
        if r2 not in Road.roads:
            continue
        find_intersection(r1, r2)

win = Visualization(sim)
win.zoom = 8
win.run()
