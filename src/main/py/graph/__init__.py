"""
 :author: vic on 2023-10-14
"""
import math
import random

phi = math.pi * (math.sqrt(5.) - 1.)  # golden angle in radians


def fibonacci_sphere(samples=1000, scale=1):
    points = []
    limit = samples - 1 if samples > 1 else 1
    random.seed()
    dephase = random.random() * 2 - 1
    for i in range(samples):
        y = 1 - (i / float(limit)) * 2  # y goes from 1 to -1
        radius = math.sqrt(1 - y * y)  # radius at y

        theta = phi * i  # golden angle increment

        x = math.cos(theta) * radius
        z = math.sin(theta) * radius

        points.append((x * scale, y * scale, z * scale))

    return points


def swatches(size):
    increment = 360 / size
    sat = 1
    lum = 0.5
    chroma = 1
    colors = []
    for jump in range(size):
        hue = jump * increment
        hprime = hue / 60
        x = 1 - math.fabs((hprime % 2) - 1)
        if 0 <= hprime < 1:
            r = chroma
            g = x
            b = 0
        elif 1 <= hprime < 2:
            r = x
            g = chroma
            b = 0
        elif 2 <= hprime < 3:
            r = 0
            g = chroma
            b = x
        elif 3 <= hprime < 4:
            r = 0
            g = x
            b = chroma
        elif 4 <= hprime < 5:
            r = x
            g = 0
            b = chroma
        else:
            r = chroma
            g = 0
            b = x
        rgb = '0x' + hex(int(r * 255))[2:].zfill(2) + hex(int(g * 255))[2:].zfill(2) + hex(int(b * 255))[2:].zfill(2)
        colors.append(int(rgb, 0))

    return colors

# https://www.cmu.edu/biolphys/deserno/pdf/sphere_equi.pdf

class MultiLayerGraph(object):
    def __init__(self):
        self.layers = []

    def add_layer(self, node_data: list):
        self.layers.append()

    def get_layer(self, nodes=1) -> list:
        return fibonacci_sphere(nodes)
