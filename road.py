from math import sqrt


class Point:
    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y

    @property
    def cords(self) -> tuple[float, float]:
        return self._x, self._y

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y


class Waypoint(Point):
    waypoints = []

    def __init__(self, x: float, y: float, traffic_light=None):
        super().__init__(x, y)
        Waypoint.waypoints.append(self)
        self.roads_to = []
        self.roads_from = []
        self._traffic_light = traffic_light

    @property
    def is_start(self) -> bool:
        return len(self.roads_to) == 0

    @property
    def is_end(self) -> bool:
        return len(self.roads_from) == 0

    @property
    def is_stop(self) -> bool:
        if self._traffic_light is None:
            return False
        return self._traffic_light.is_stop

    def set_traffic_light(self, traffic_light):
        self._traffic_light = traffic_light

    def append_road_to(self, road):
        for r in self.roads_to:
            if is_right(road, r.start):
                Intersection(r.end.x, r.end.y, r, road)
            else:
                Intersection(r.end.x, r.end.y, road, r)
        self.roads_to.append(road)

    def append_road_from(self, road):
        self.roads_from.append(road)

    def remove_road_to(self, road):
        self.roads_to.remove(road)

    def remove_road_from(self, road):
        self.roads_from.remove(road)

    def connect(self, other, turn_left=True, resolution=20):
        if self is other:
            return
        for road in self.roads_to:
            if road.end is other:
                return
        for road in other.roads_from:
            if road.start is self:
                return

        if turn_left == ((self.x > other.x) == (self.y > other.y)):
            control = (self.x, other.y)
        else:
            control = (other.x, self.y)

        waypoints = curve(self, other, control, resolution)

        for i in range(1, len(waypoints)):
            Road(waypoints[i - 1], waypoints[i])


class Intersection(Point):
    intersections = []

    def __init__(self, x, y, main, secondary):
        super().__init__(x, y)
        Intersection.intersections.append(self)

        self._main_distance = sqrt((main.start.x - x) ** 2 + (main.start.y - y) ** 2)
        self._main = main
        main.add_intersection(self, self._main_distance)

        self._secondary_distance = sqrt((secondary.start.x - x) ** 2 + (secondary.start.y - y) ** 2)
        self._secondary = secondary
        secondary.add_intersection(self, self._secondary_distance)

    @property
    def main_road(self):
        return self._main

    @property
    def secondary_road(self):
        return self._secondary

    @property
    def main_distance(self):
        return self._main_distance

    @property
    def secondary_distance(self):
        return self._secondary_distance

    def have_road(self, road):
        if road is self._main:
            return True
        if road is self._secondary:
            return True
        return False

    def change_priority(self):
        self._main, self._secondary = self._secondary, self._main


class Road:
    roads = []

    def __init__(self, start, end):

        self._start = start
        self._end = end
        self._length = sqrt((self._start.x - self._end.x) ** 2 + (self._start.y - self._end.y) ** 2)
        self._sin = (self._end.y - self._start.y) / self._length
        self._cos = (self._end.x - self._start.x) / self._length

        self._intersections = []

        self._vehicles = []

        Road.roads.append(self)
        start.append_road_from(self)
        end.append_road_to(self)

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def length(self):
        return self._length

    @property
    def cos(self):
        return self._cos

    @property
    def sin(self):
        return self._sin

    @property
    def have_intersections(self):
        return len(self._intersections) > 0

    @property
    def intersections(self):
        return self._intersections

    def add_intersection(self, intersection, distance):
        for i in range(len(self._intersections)):
            if self._intersections[i][1] > distance:
                self._intersections.insert(i, (intersection, distance))
                return
        self._intersections.append((intersection, distance))

    def add_vehicle(self, vehicle):
        if vehicle not in self._vehicles:
            self._vehicles.append(vehicle)

    def remove_vehicle(self, vehicle):
        if vehicle in self._vehicles:
            self._vehicles.remove(vehicle)

    def check_intersection(self, distance, start_distance=0):
        if distance < 0:
            return None

        for intersection in self._intersections:
            if intersection[0].secondary_road is self:
                if start_distance > intersection[1]:
                    continue
                elif distance + start_distance > intersection[1]:
                    return intersection
                else:
                    return None

        distance -= self._length - start_distance
        nearest_intersection = None
        for road in self._end.roads_from:
            intersection = road.check_intersection(distance)
            if intersection is not None:
                if nearest_intersection is None or nearest_intersection[1] > intersection[1]:
                    nearest_intersection = intersection

        return nearest_intersection

    def check_for_vehicles(self, distance, start_distance=0, reverse=False):
        for v in self._vehicles:
            if reverse:
                v_dist = self._length - v.distance
            else:
                v_dist = v.distance

            if v_dist <= start_distance:
                continue
            elif v_dist < distance + start_distance:
                return True

        distance -= self._length - start_distance
        if distance <= 0:
            return False

        if reverse:
            if self.start.is_stop:
                return False
            for road in self.start.roads_to:
                if road.check_for_vehicles(distance, start_distance=0, reverse=reverse):
                    return True
        else:
            if self.end.is_stop:
                return True
            for road in self.end.roads_from:
                if road.check_for_vehicles(distance, start_distance=0, reverse=reverse):
                    return True
        return False

    def remove(self):
        self._start.remove_road_from(self)
        self._end.remove_road_to(self)
        Road.roads.remove(self)


def curve(start, end, control, resolution=8):
    if (start.x - end.x) * (start.y - end.y) == 0:
        return [start, end]

    points = [start]

    for i in range(1, resolution):
        t = i / resolution
        x = (1 - t) ** 2 * start.x + 2 * (1 - t) * t * control[0] + t ** 2 * end.x
        y = (1 - t) ** 2 * start.y + 2 * (1 - t) * t * control[1] + t ** 2 * end.y
        points.append(Waypoint(x, y))
    points.append(end)

    return points


def find_intersection(first, second):
    for intersection in first.intersections:
        if intersection[0].have_road(second):
            return None

    p0 = first.start
    p1 = first.end
    p2 = second.start
    p3 = second.end

    if (p0.cords == p2.cords) or (p0.cords == p3.cords) or (p1.cords == p2.cords) or (p1.cords == p3.cords):
        return

    s10_x = p1.x - p0.x
    s10_y = p1.y - p0.y
    s32_x = p3.x - p2.x
    s32_y = p3.y - p2.y

    denominator = s10_x * s32_y - s32_x * s10_y

    if denominator == 0:
        return  # collinear

    denominator_is_positive = denominator > 0

    s02_x = p0.x - p2.x
    s02_y = p0.y - p2.y

    s_numer = s10_x * s02_y - s10_y * s02_x

    if (s_numer <= 0) == denominator_is_positive:
        return  # no collision

    t_numer = s32_x * s02_y - s32_y * s02_x

    if (t_numer <= 0) == denominator_is_positive:
        return  # no collision

    if (s_numer >= denominator) == denominator_is_positive or (t_numer > denominator) == denominator_is_positive:
        return  # no collision

    # collision detected

    t = t_numer / denominator

    if is_right(first, second.start):
        Intersection(p0.x + (t * s10_x), p0.y + (t * s10_y), second, first)
    else:
        Intersection(p0.x + (t * s10_x), p0.y + (t * s10_y), first, second)


def is_right(road, waypoint):
    a = road.start
    b = road.end
    c = waypoint
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x) > 0
