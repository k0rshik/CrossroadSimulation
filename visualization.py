import pygame
from pygame import gfxdraw
import numpy as np

from road import Waypoint, Road
from trafic_light import TrafficLight

road_width = 3.6


class Visualization:
    def __init__(self, sim, ticks_per_update=1):
        self._sim = sim
        self._current_waypoint = None
        self._ticks_per_update = ticks_per_update

        self.width = 1400
        self.height = 900
        self.bg_color = (250, 250, 250)

        self.fps = 60
        self.zoom = 5
        self.offset = (0, 0)

        self.flip_x = True

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.font.init()
        self.text_font = pygame.font.SysFont("Lucida Console", 20)

        pygame.display.set_caption("Crossroad Simulation")

    def loop(self, loop=None):
        clock = pygame.time.Clock()
        running = True
        while running:
            if loop:
                loop(self._sim)

            self.draw()

            pygame.display.update()
            clock.tick(self.fps)

            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        running = False
                    case pygame.KEYDOWN:
                        if pygame.key.get_pressed()[pygame.K_SPACE]:
                            self._sim.toggle()
                        if pygame.key.get_pressed()[pygame.K_UP]:
                            self._ticks_per_update += 1
                        if pygame.key.get_pressed()[pygame.K_DOWN]:
                            self._ticks_per_update = max(1, self._ticks_per_update-1)

                    # case pygame.MOUSEBUTTONDOWN:
                    #     pos = self.inverse_convert(event.pos)
                    #     for w in Waypoint.waypoints:
                    #         if abs(w.cords[0] - pos[0]) < 3 and abs(w.cords[1] - pos[1]) < 3:
                    #             if self._current_waypoint is None:
                    #                 self._current_waypoint = w
                    #             elif self._current_waypoint is not w:
                    #                 if event.button == 1:
                    #                     self._current_waypoint.connect(w, True)
                    #                 elif event.button == 3:
                    #                     self._current_waypoint.connect(w, False)
                    #                 self._current_waypoint = None
                    #             break
                    #     else:
                    #         if self._current_waypoint is None:
                    #             Waypoint(*pos)
                    #         else:
                    #             self._current_waypoint = None

    def run(self):
        def loop(sim):
            sim.run(self._ticks_per_update)

        self.loop(loop)

    def convert(self, x, y=None):
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (
            int(self.width / 2 + (x + self.offset[0]) * self.zoom),
            int(self.height / 2 + (y + self.offset[1]) * self.zoom)
        )

    def inverse_convert(self, x, y=None):
        if isinstance(x, list):
            return [self.inverse_convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.inverse_convert(*x)
        return (
            int(-self.offset[0] + (x - self.width / 2) / self.zoom),
            int(-self.offset[1] + (y - self.height / 2) / self.zoom)
        )

    def background(self, r, g, b):
        self.screen.fill((r, g, b))

    def circle(self, pos, radius, color, filled=True):
        gfxdraw.aacircle(self.screen, *self.convert(*pos), int(radius * self.zoom), color)
        if filled:
            gfxdraw.filled_circle(self.screen, *self.convert(*pos), int(radius * self.zoom), color)

    def polygon(self, vertices, color, filled=True):
        gfxdraw.aapolygon(self.screen, vertices, color)
        if filled:
            gfxdraw.filled_polygon(self.screen, vertices, color)

    def rotated_box(self, pos, size, angle=None, cos=None, sin=None, centered=True, color=(0, 0, 255), filled=True):
        x, y = pos
        l, h = size

        if angle:
            cos, sin = np.cos(angle), np.sin(angle)

        vertex = lambda e1, e2: (
            x + (e1 * l * cos + e2 * h * sin) / 2,
            y + (e1 * l * sin - e2 * h * cos) / 2
        )

        if centered:
            vertices = self.convert(
                [vertex(*e) for e in [(-1, -1), (-1, 1), (1, 1), (1, -1)]]
            )
        else:
            vertices = self.convert(
                [vertex(*e) for e in [(0, -1), (0, 1), (2, 1), (2, -1)]]
            )

        self.polygon(vertices, color, filled=filled)

    def draw_waypoints(self):
        for waypoint in Waypoint.waypoints:
            if self._current_waypoint is waypoint:
                self.circle((waypoint.x, waypoint.y), road_width / 2, (255, 0, 255))
            else:
                if waypoint.is_start:
                    self.circle((waypoint.x, waypoint.y), road_width / 2, (0, 255, 0))
                else:
                    if waypoint.is_end:
                        self.circle((waypoint.x, waypoint.y), road_width / 2, (255, 0, 0))
                    else:
                        self.circle((waypoint.x, waypoint.y), road_width / 2, (120, 120, 120))

    def draw_roads(self):
        for road in Road.roads:
            self.rotated_box(
                road.start.cords,
                (road.length, road_width),
                cos=road.cos,
                sin=road.sin,
                color=(120, 120, 120),
                centered=False
            )

    def draw_vehicle(self, vehicle):
        l, h = vehicle.height, vehicle.width
        road = vehicle.road
        sin, cos = road.sin, road.cos

        x = road.start.x + cos * vehicle.distance
        y = road.start.y + sin * vehicle.distance

        self.rotated_box((x, y), (l, h), cos=cos, sin=sin, color=vehicle.color, centered=True)

    def draw_vehicles(self):
        for vehicle in self._sim.vehicles:
            self.draw_vehicle(vehicle)

    def draw_traffic_lights(self):
        width = 3
        height = 9
        for t in TrafficLight.traffic_lights:
            self.rotated_box((t.x, t.y), (width, height), cos=t.cos, sin=t.sin, centered=True, color=(30, 30, 30))
            colors = [(60, 60, 60)] * 3

            if t.stage == 0:
                colors[2] = (0, 255, 0)
            if t.stage in (1, 3):
                colors[1] = (255, 255, 0)
            if t.stage in (2, 3):
                colors[0] = (255, 0, 0)

            self.circle((t.x - (height - width) * -t.sin / 2, t.y - (height - width) * t.cos / 2), width / 3,
                        colors[0])
            self.circle((t.x, t.y), width / 3, colors[1])
            self.circle((t.x + (height - width) * -t.sin / 2, t.y + (height - width) * t.cos / 2), width / 3,
                        colors[2])

    def draw_text(self):
        self.screen.blit(self.text_font.render(f'PassPerMinute={3600 * self._sim.vehicles_passed / self._sim.ticks:.4}',
                                               True, (0, 0, 0)), (0, 0))
        self.screen.blit(self.text_font.render(f'Count={self._sim.vehicles_spawned - self._sim.vehicles_passed}',
                                               True, (0, 0, 0)), (0, 25))
        self.screen.blit(self.text_font.render(f'Spawned={self._sim.vehicles_spawned}',
                                               True, (0, 0, 0)), (300, 0))
        self.screen.blit(self.text_font.render(f'Passed={self._sim.vehicles_passed}',
                                               True, (0, 0, 0)), (300, 25))
        self.screen.blit(self.text_font.render(f'Simulation speed={self._ticks_per_update}',
                                               True, (0, 0, 0)), (self.width-240, 0))

        if self._sim.paused:
            self.screen.blit(self.text_font.render("Paused",
                                                   True, (220, 0, 0)), (self.width // 2 - 36, self.height // 2 - 10))

    def draw(self):
        self.background(*self.bg_color)
        self.draw_waypoints()
        self.draw_roads()
        self.draw_vehicles()
        self.draw_traffic_lights()
        self.draw_text()
