"""Space system simulation."""

import pygame
import math
import random


closed = False
pygame.init()

clock = pygame.time.Clock()
size = (1680, 1050)
display = pygame.display.set_mode(size)
CENTER = size[0] / 2, size[1] / 2
FPS = 60
pygame.display.set_mode(size)
pygame.display.set_caption('Jam #2')
bg_color = (15, 15, 15)

timescale = 10**10  # Since the effects of gravity are extremely small during real time, scaling the time value makes things happen faster
planets = []

camera_x = 0
camera_y = 0

tracked = None

move_left = False
move_right = False
move_up = False
move_down = False


class Circle:
    def __init__(self, coords: tuple, radius: int, color: tuple):
        self.x, self.y = coords
        self.radius = radius
        self.color = color

    def draw(self):
        x = self.x + camera_x
        y = self.y + camera_y
        pygame.draw.circle(display, self.color, (round(x), round(y)), round(self.radius))

    def set_color(self, color: tuple):
        self.color = color


class Planet(Circle):

    def __init__(self, coords: tuple, color: tuple, mass: float, density: float=1, iv: tuple=(0, 0), acceleration: tuple=(0, 0)):
        super().__init__(coords, 0, color)
        self.mass = mass
        self.density = density
        self.radius = self.size
        self.exist = True
        self.ax, self.ay = acceleration[0], acceleration[1]
        self.ix, self.iy = iv[0], iv[1]
        self.plot_path = False

    def __repr__(self):
        return f'({self.x, self.y}), {self.mass}, {self.radius}, {self.exist}'

    @property
    def angle_motion(self) -> float:
        """Angle of motion"""
        x = self.x + self.ix - self.x
        y = self.y + self.iy - self.y
        return math.degrees(math.atan2(y, x))

    def angle_to(self, other) -> float:
        x = other.x - self.x
        y = other.y - self.y
        return math.degrees(math.atan2(y, x))

    def attraction_to_other(self, planet) -> float:
        """Returns the force of attraction to another planet"""
        d = self.distance_to(planet)
        if d == 0:  # Avoid division by zero error
            return 0
        f = self.g * ((planet.mass * self.mass) / d ** 2)
        return f  # Velocity over a frame

    def collide(self, planet) -> bool:
        d = self.distance_to(planet)
        if d > self.radius:
            return False
        else:
            return True

    def distance_to(self, planet) -> float:
        d = math.sqrt(math.fabs((self.x - planet.x)**2 + (self.y - planet.y)**2))
        return d

    def draw(self):
        super().draw()
        self.x += self.ax
        self.y += self.ay

    @property
    def g(self) -> float:
        """Gravitational constant of object"""
        g = 6.674 * (10**-11) / self.mass * timescale
        return g

    def merge(self, planet):
        """Merge 2 planets together when they collide"""
        if planet.exist is True and self.exist is True:
            # Pick the planet with the highest mass to be the origin
            planet.exist = False
            self.x = self.x if self.mass > planet.mass else planet.x
            self.y = self.y if self.mass > planet.mass else planet.y
            self.mass = self.mass + planet.mass
            self.density = max((self.density, planet.density))
            self.radius = self.size
            self.set_color(((self.color[0] + planet.color[0]) / 2, (self.color[1] + planet.color[1]) / 2, (self.color[2] + planet.color[2]) / 2))
            self.ix = 0
            self.iy = 0

    @property
    def size(self) -> int:
        return round(math.sqrt(self.mass) / self.density)  # Density allows more mass to exist in a smaller space

    def update(self, planet):
        if self.exist is True and planet.exist is True:
            f = self.attraction_to_other(planet)
            a = self.angle_to(planet)
            vx = f * math.cos(math.radians(a))
            vy = f * math.sin(math.radians(a))
            self.x += self.ix + vx
            self.y += self.iy + vy
            self.ix += vx
            self.iy += vy


planet1 = Planet((size[0] / 2 - 300, size[1] / 2), (150, 40, 150), 150, 1, (1.4, -2.4))
planet2 = Planet((size[0] / 2 + 300, size[1] / 2), (40, 150, 150), 150, 1, (-1.4, 2.4))
planet3 = Planet((size[0] / 2, size[1] / 2), (200, 200, 40), 10000, 2.5)
planet4 = Planet((size[0] / 2, size[1] / 2 + 500), (150, 150, 40), 300, 0.8, (-2, 1))
planets.append(planet1)
planets.append(planet2)
planets.append(planet3)
planets.append(planet4)


asteroid_count = 0
while asteroid_count > 0:
    asteroid_count -= 1
    pos = random.randrange(-200, size[0] + 200), random.randrange(-size[1], size[1] * 2)
    color = random.randrange(30, 130), random.randrange(30, 130), random.randrange(30, 130)
    speeds = random.uniform(-0.25, 0.25), random.uniform(-0.25, 0.25)
    asteroid = Planet(pos, color, random.randrange(15, 30), random.uniform(0.2, 0.5), speeds)
    planets.append(asteroid)


while not closed:
    pygame.display.update()
    display.fill(bg_color)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            closed = True
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                closed = True
                pygame.quit()
                quit()
            if event.key == pygame.K_a:
                move_left = True
            if event.key == pygame.K_d:
                move_right = True
            if event.key == pygame.K_s:
                move_down = True
            if event.key == pygame.K_w:
                move_up = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                move_left = False
            if event.key == pygame.K_d:
                move_right = False
            if event.key == pygame.K_s:
                move_down = False
            if event.key == pygame.K_w:
                move_up = False

    if move_up:
        camera_y -= 2.5
    if move_down:
        camera_y += 2.5
    if move_right:
        camera_x += 2.5
    if move_left:
        camera_x -= 2.5

    for i, planet in enumerate(planets):
        planet.draw()
        for o_i, o_planet in enumerate(planets):  # Compare other planets to this planet
            if o_i != i:
                planet.update(o_planet)
                if planet.collide(o_planet):
                    planet.merge(o_planet)
        if planet.exist is False:
            planets.pop(i)
    clock.tick(FPS)
