"""models.py - numpy-based 3d models
"""
from collections import namedtuple
import numpy as np

from . import transforms as tr

Shape = namedtuple('Shape', ['vertices', 'faces', 'normals'])

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
    normals = tr.normals(vertices, faces)
    normals = np.hstack((normals, np.ones((len(normals), 1))))
    return Shape(vertices, faces, normals)
