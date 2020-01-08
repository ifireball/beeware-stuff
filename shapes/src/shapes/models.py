"""models.py - numpy-based 3d models
"""
from collections import namedtuple
import numpy as np

Shape = namedtuple('Shape', ['vertices', 'faces'])

def box():
    vertices = np.array([
        (x, y, z, 1.)
        for x in (-1., 1.) for y in (-1., 1.) for z in (-1., 1.)
    ], dtype=np.float32)
    faces = np.array([
        [0, 1, 3, 2],
        [0, 4, 5, 1],
        [0, 2, 6, 4],
        [7, 3, 1, 5],
        [7, 5, 4, 6],
        [7, 6, 2, 3],
    ])
    return Shape(vertices, faces)

def normals(vertices, faces):
    e1 = vertices[faces[:,1], 0:3] - vertices[faces[:,0], 0:3]
    e2 = vertices[faces[:,2], 0:3] - vertices[faces[:,1], 0:3]
    return np.cross(e1, e2)
