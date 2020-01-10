"""models.py - numpy-based 3d models
"""
from collections import namedtuple
import numpy as np
from math import pi, tan

from . import transforms as tr

Shape = namedtuple('Shape', ['vertices', 'faces', 'normals', 'edges'])

def box():
    return cylinder(4)

def cylinder(segments):
    return extruder(segments).start_poly().extrude_poly(2).close().shape()

def cone(segments):
    s = extruder(segments).start_poly().extrude_point(2).shape()
    return s

def duble_cone(segments):
    s = extruder(segments).start_point().extrude_poly(1).extrude_point(1).shape()
    return(s)

def polygon(segments):
    point = np.array([tan(pi/segments), 1., 0. ,1.], dtype=np.float32)
    return np.array([
        point @ tr.rotate_z(angle)
        for angle in np.linspace(0, pi * 2, segments, endpoint=False)
    ])

class extruder:
    def __init__(self, segments):
        self.segments = segments

    POINT=0
    FACE=1
    EDGE=2

    def start_point(self ):
        self.vertices = np.array([[0., 0., -1., 1.]], dtype=np.float32)
        self.faces = []
        self.edges = []
        self.last = self.POINT
        return self

    def start_poly(self):
        self.vertices = polygon(self.segments) @ tr.move(0, 0, -1)
        self.faces = [_polygon_face(self.segments, 0, True)]
        self.edges = []
        self.last = self.FACE
        return self

    def extrude_point(self, dz):
        extrude_z = self.vertices[-1, 2] + dz
        if self.last == self.POINT:
            # If trying to extrude point form point - move the point
            self.vertices[-1, 2] = extrude_z
            return self
        elif self.last == self.EDGE:
            self.add_edges(_rim_edges(
                self.segments,
                len(self.vertices)-self.segments,
                len(self.faces)-self.segments,
                len(self.faces),
            ))
        else:
            self.add_edges(_polygon_edges(
                self.segments,
                len(self.vertices)-self.segments,
                len(self.faces)-1,
                len(self.faces)
            ))
        self.add_vertices(np.array([[0., 0., extrude_z, 1]]))
        self.add_edges(_cone_edges(
            self.segments,
            len(self.vertices)-1-self.segments,
            len(self.vertices)-1,
            len(self.faces)
        ))
        self.add_faces(_cone_faces(
            self.segments,
            len(self.vertices)-1-self.segments,
            len(self.vertices)-1,
        ))
        self.last=self.POINT
        return self

    def extrude_poly(self, dz):
        extrude_z = self.vertices[-1, 2] + dz
        self.add_vertices(polygon(self.segments) @ tr.move(0, 0, extrude_z))
        if self.last == self.POINT:
            self.add_edges(_cone_edges(
                self.segments,
                len(self.vertices)-self.segments,
                len(self.vertices)-self.segments-1,
                len(self.faces)
            ))
            self.add_faces(_cone_faces(
                self.segments,
                len(self.vertices)-self.segments,
                len(self.vertices)-self.segments-1,
                flip_direction=True,
            ))
            self.last = self.EDGE
            return self
        else:
            if self.last == self.EDGE:
                self.add_edges(_rim_edges(
                    self.segments,
                    len(self.vertices)-self.segments*2,
                    len(self.faces)-self.segments,
                    len(self.faces),
                ))
            else:
                self.add_edges(_polygon_edges(
                    self.segments,
                    len(self.vertices)-self.segments*2,
                    len(self.faces)-1,
                    len(self.faces),
                ))
            self.add_edges(_cylinder_edges(
                self.segments,
                len(self.vertices)-self.segments*2,
                len(self.vertices)-self.segments,
                len(self.faces)
            ))
            self.add_faces(_cylinder_faces(
                self.segments,
                len(self.vertices)-self.segments*2,
                len(self.vertices)-self.segments,
            ))
            self.last = self.EDGE
            return self

    def close(self):
        if self.last == self.POINT or self.last == self.FACE:
            return self
        self.add_edges(_polygon_edges(
            self.segments,
            len(self.vertices)-self.segments,
            len(self.faces),
            len(self.faces)-self.segments
        ))
        self.add_faces([_polygon_face(
            self.segments,
            len(self.vertices)-self.segments
        )])
        return self

    def shape(self):
        faces = np.array(self.faces)
        edges = np.array(self.edges)
        normals = tr.normals(self.vertices, self.faces)
        normals = np.hstack((normals, np.ones((len(normals), 1))))
        shape = Shape(self.vertices, faces, normals, edges)
        return shape

    def add_vertices(self, vertices):
        self.vertices = np.concatenate((self.vertices, vertices))

    def add_faces(self, faces):
        self.faces.extend(faces)

    def add_edges(self, edges):
        self.edges.extend(edges)


def _polygon_face(segments, vtx_st_i, flip_direction=False):
    face = range(vtx_st_i, vtx_st_i+segments)
    if flip_direction:
        face = reversed(face)
    return list(face)

def _polygon_edges(segments, vtx_st_i, poly_face_i, side_face_st_i):
    return [[
        vtx_st_i+n, vtx_st_i+(n+1)%segments,
        poly_face_i, side_face_st_i+n
    ] for n in range(segments)]

def _rim_edges(segments, vtx_st_i, bottom_face_st_i, top_face_st_i):
    return [[
        vtx_st_i+n, vtx_st_i+(n+1)%segments,
        bottom_face_st_i+n, top_face_st_i+n
    ] for n in range(segments)]

def _cylinder_faces(segments, bottom_vtx_st_i, top_vtx_st_i):
    return [[
        bottom_vtx_st_i+n, bottom_vtx_st_i+(n+1)%segments,
        top_vtx_st_i+(n+1)%segments, top_vtx_st_i+n,
    ] for n in range(segments)]

def _cylinder_edges(segments, bottom_vtx_st_i, top_vtx_st_i, face_st_i):
    return [[
        bottom_vtx_st_i+n, top_vtx_st_i+n,
        face_st_i+(n-1) % segments, face_st_i+n
    ] for n in range(segments)]

def _cone_faces(segments, edge_vtx_st_i, point_vtx_i, flip_direction=False):
    if flip_direction:
        return [
            [edge_vtx_st_i+n, point_vtx_i, edge_vtx_st_i+(n+1)%segments]
            for n in range(segments)
        ]
    else:
        return [
            [edge_vtx_st_i+n, edge_vtx_st_i+(n+1)%segments, point_vtx_i]
            for n in range(segments)
        ]

def _cone_edges(segments, edge_vtx_st_i, point_vtx_i, faces_st_i):
    return [[
        edge_vtx_st_i+n, point_vtx_i,
        faces_st_i+(n-1) % segments, faces_st_i+n
    ] for n in range(segments)]
