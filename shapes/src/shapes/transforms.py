"""transforms.py - numpy-based 3D transform matrices
"""
import numpy as np
from math import cos, sin

def move(dx=0., dy=0., dz=0.):
    return np.array([
        [1., 0., 0., 0.],
        [0., 1., 0., 0.],
        [0., 0., 1., 0.],
        [dx, dy, dz, 1.],
    ], dtype=np.float32)

def scale(sx=1., sy=1., sz=1.):
    return np.array([
        [sx, 0., 0., 0.],
        [0., sy, 0., 0.],
        [0., 0., sz, 0.],
        [0., 0., 0., 1.],
    ], dtype=np.float32)

def rotate_x(d):
    return np.array([
        [1.,      0.,     0., 0.],
        [0.,  cos(d), sin(d), 0.],
        [0., -sin(d), cos(d), 0.],
        [0.,      0.,     0., 1.],
    ], dtype=np.float32)

def rotate_y(d):
    return np.array([
        [cos(d), 0., -sin(d), 0.],
        [    0., 1.,      0., 0.],
        [sin(d), 0.,  cos(d), 0.],
        [    0., 0.,      0., 1.],
    ], dtype=np.float32)

def rotate_z(d):
    return np.array([
        [ cos(d), sin(d), 0., 0.],
        [-sin(d), cos(d), 0., 0.],
        [     0.,     0., 1., 0.],
        [     0.,     0., 0., 1.],
    ], dtype=np.float32)

def perspective(vertices, d=1):
    dy = d / np.delete(vertices, (0, 2, 3), 1)
    ones = np.ones_like(dy)
    tmat = np.hstack((dy, ones, dy, ones))
    return vertices * tmat

def normals(vertices, faces):
    columns = [
        [face[column] for face in faces]
        for column in range(3)
    ]
    e1 = vertices[columns[1], 0:3] - vertices[columns[0], 0:3]
    e2 = vertices[columns[2], 0:3] - vertices[columns[1], 0:3]
    return np.cross(e1, e2)
