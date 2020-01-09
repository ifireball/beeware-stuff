"""models.py - numpy-based 3d models
"""
from collections import namedtuple
import numpy as np
from math import pi, tan

from . import transforms as tr

Shape = namedtuple('Shape', ['vertices', 'faces', 'normals', 'edges'])

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
    return Shape(vertices, faces, normals, [])

def cylinder(segments):
    poly = polygon(segments)
    bottom = poly @ tr.move(0, 0, -1)
    top = poly @ tr.move(0, 0, 1)
    vertices = np.concatenate((bottom, top))
    faces = np.array([
        list(reversed(range(0, segments))),
        list(range(segments, segments * 2)),
    ] + [
        [n, (n+1) % segments, (n+1) % segments + segments, n + segments]
        for n in range(segments)
    ])
    edges = np.array(
        [[n, (n+1) % segments, 0, 2+n] for n in range(segments)] +
        [
            [(n+1) % segments + segments, n + segments, 1, 2+n]
            for n in range(segments)
        ] +
        [[n, n + segments, 2+(n-1) % segments, 2+n] for n in range(segments)]
    )
    normals = tr.normals(vertices, faces)
    normals = np.hstack((normals, np.ones((len(normals), 1))))
    return Shape(vertices, faces, normals, edges)

def cone(segments):
    poly = polygon(segments)
    bottom = poly @ tr.move(0, 0, -1)
    top = np.array([[0., 0., 1., 1.]], dtype=np.float32)
    vertices = np.concatenate((bottom, top))
    faces = np.array([
        list(reversed(range(0, segments))),
    ] + [
        [n, (n+1) % segments, segments]
        for n in range(segments)
    ])
    edges = np.array(
        [[n, (n+1) % segments, 0, 1+n] for n in range(segments)] +
        [[n, segments, 1+(n-1) % segments, 1+n] for n in range(segments)]
    )
    normals = tr.normals(vertices, faces)
    normals = np.hstack((normals, np.ones((len(normals), 1))))
    return Shape(vertices, faces, normals, edges)

def polygon(segments):
    point = np.array([tan(pi/segments), 1., 0. ,1.], dtype=np.float32)
    return np.array([
        point @ tr.rotate_z(angle)
        for angle in np.linspace(0, pi * 2, segments, endpoint=False)
    ])
