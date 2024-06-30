from math import cos, sin


class TrafficLight:
    traffic_lights = []

    def __init__(self, x, y, angle, durations: list[int], current_stage=0):
        self._x = x
        self._y = y
        self._cos = cos(angle)
        self._sin = sin(angle)

        self._current_stage = current_stage
        self._durations = durations
        self._ticks = 0

        TrafficLight.traffic_lights.append(self)

    @property
    def stage(self):
        if self._current_stage == 2 and self._ticks >= (self._durations[2] - self._durations[1]):
            return 3
        return self._current_stage

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def cos(self):
        return self._cos

    @property
    def sin(self):
        return self._sin

    @property
    def is_stop(self):
        return self._current_stage != 0

    def update(self):
        if self._ticks >= self._durations[self._current_stage]:
            self._ticks = 0
            self._current_stage = (self._current_stage + 1) % 3
        else:
            self._ticks += 1
