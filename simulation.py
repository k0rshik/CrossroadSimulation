import random

from road import Waypoint
from vehicle import Vehicle
from trafic_light import TrafficLight


class Simulation:
    def __init__(self):
        self.waypoints = []
        self.vehicles = []
        self._paused = False

        self.vehicles_spawned = 0
        self.vehicles_passed = 0
        self.ticks = 0

    def update(self):
        if self._paused:
            return
        self.ticks += 1
        for t in TrafficLight.traffic_lights:
            t.update()
        for v in self.vehicles:
            v.update()

        for w in Waypoint.waypoints:
            if w.is_start:
                for road in w.roads_from:
                    if random.randint(0, 1*60) == 0 and not road.check_for_vehicles(10):
                        self.vehicles.append(Vehicle(self, road))
                        self.vehicles_spawned += 1

    def toggle(self):
        self._paused = not self._paused

    @property
    def paused(self):
        return self._paused

    def run(self, steps):
        for _ in range(steps):
            self.update()
