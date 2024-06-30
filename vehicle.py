import random


class Vehicle:
    def __init__(self, sim, road):
        self._simulation = sim
        self._road = road
        self._road.add_vehicle(self)

        self._distance = 0
        self._width = random.uniform(0.75, 1.25)
        self._height = random.uniform(1.7, 2.5)
        self._max_velocity = 0.2777 * random.randint(30, 60) / 60
        self._slow_velocity = 0.2777 * 6 / 60
        self._go_acceleration = 0.2777 * 1 / 60
        self._stop_acceleration = 0.2777 * -3 / 60
        self._slow_stop_acceleration = 0.2777 * -1.3 / 60
        self._color = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))

        self._velocity = 0 / 30

    @property
    def color(self):
        return self._color

    @property
    def distance(self):
        return self._distance

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def road(self):
        return self._road

    def update(self):
        self._velocity = max(self._velocity, 0)
        self._velocity = min(self._velocity, self._max_velocity)

        self._distance += self._velocity

        if self._distance >= self._road.length:
            if not self._road.end.is_end:
                self._distance = self.distance - self._road.length

                self._road.remove_vehicle(self)
                self._road = random.choice(self._road.end.roads_from)
                self._road.add_vehicle(self)
            else:
                self._simulation.vehicles.remove(self)
                self._simulation.vehicles_passed += 1
                self._road.remove_vehicle(self)

        if self.check_slow:
            if self.check_stop:
                self._velocity = 0
            else:
                self._velocity += self._slow_stop_acceleration
                self._velocity = max(self._slow_velocity, self._velocity)
        else:
            self._velocity += self._go_acceleration

    @property
    def check_slow(self):
        if self._road.check_for_vehicles(10, self.distance):
            return True
        intersection = self._road.check_intersection(14, self.distance)
        if intersection is not None:
            return intersection[0].main_road.check_for_vehicles(40, intersection[0].main_distance, True)

        return False

    @property
    def check_stop(self):
        if self._road.check_for_vehicles(6, self.distance):
            return True
        intersection = self._road.check_intersection(8, self.distance)

        if intersection is not None:
            return intersection[0].main_road.check_for_vehicles(30, intersection[0].main_distance, True)

        return False
