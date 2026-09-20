"""Finite two-dimensional cell complexes with explicit attaching walks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from homoloqode.algebra.gf2 import BinaryArray, as_binary_matrix


def _validate_id(value: str, *, kind: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{kind} id must be a non-empty string.")


@dataclass(frozen=True, slots=True)
class Vertex:
    """A labelled zero-cell with optional visualization coordinates."""

    id: str
    coordinates: tuple[float, ...] | None = None

    def __post_init__(self) -> None:
        _validate_id(self.id, kind="Vertex")
        if self.coordinates is not None:
            object.__setattr__(self, "coordinates", tuple(self.coordinates))


@dataclass(frozen=True, slots=True)
class Edge:
    """An oriented one-cell.

    The orientation is used to describe attaching walks. It disappears from
    boundary matrices after reduction over the binary field.
    """

    id: str
    source: str
    target: str

    def __post_init__(self) -> None:
        _validate_id(self.id, kind="Edge")
        _validate_id(self.source, kind="Source vertex")
        _validate_id(self.target, kind="Target vertex")


@dataclass(frozen=True, slots=True)
class OrientedEdge:
    """A reference to an edge used with either orientation."""

    edge_id: str
    orientation: int = 1

    def __post_init__(self) -> None:
        _validate_id(self.edge_id, kind="Edge reference")
        if isinstance(self.orientation, bool) or self.orientation not in (-1, 1):
            raise ValueError("Edge-reference orientation must be +1 or -1.")


@dataclass(frozen=True, slots=True)
class Face:
    """A two-cell whose boundary is an ordered, oriented edge walk."""

    id: str
    boundary: tuple[OrientedEdge, ...]

    def __post_init__(self) -> None:
        _validate_id(self.id, kind="Face")
        object.__setattr__(self, "boundary", tuple(self.boundary))


@dataclass(frozen=True, slots=True)
class CellComplex2D:
    """A finite 2D cell complex with explicit stable tuple ordering.

    ``vertices``, ``edges``, and ``faces`` determine the bases of ``C0``,
    ``C1``, and ``C2`` respectively. Their tuple order is preserved in every
    derived label sequence and boundary matrix.
    """

    vertices: tuple[Vertex, ...]
    edges: tuple[Edge, ...]
    faces: tuple[Face, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "vertices", tuple(self.vertices))
        object.__setattr__(self, "edges", tuple(self.edges))
        object.__setattr__(self, "faces", tuple(self.faces))
        self._validate()

    @staticmethod
    def _require_unique(ids: tuple[str, ...], *, kind: str) -> None:
        if len(ids) != len(set(ids)):
            raise ValueError(f"{kind} ids must be unique.")

    def _validate(self) -> None:
        vertex_ids = tuple(vertex.id for vertex in self.vertices)
        edge_ids = tuple(edge.id for edge in self.edges)
        face_ids = tuple(face.id for face in self.faces)
        self._require_unique(vertex_ids, kind="Vertex")
        self._require_unique(edge_ids, kind="Edge")
        self._require_unique(face_ids, kind="Face")

        vertices = set(vertex_ids)
        for edge in self.edges:
            if edge.source not in vertices or edge.target not in vertices:
                raise ValueError(
                    f"Edge {edge.id!r} references a vertex outside the complex."
                )

        edges = {edge.id: edge for edge in self.edges}
        for face in self.faces:
            for reference in face.boundary:
                if reference.edge_id not in edges:
                    raise ValueError(
                        f"Face {face.id!r} references unknown edge "
                        f"{reference.edge_id!r}."
                    )
            self._validate_closed_boundary(face, edges)

    @staticmethod
    def _oriented_endpoints(
        reference: OrientedEdge, edges: dict[str, Edge]
    ) -> tuple[str, str]:
        edge = edges[reference.edge_id]
        if reference.orientation == 1:
            return edge.source, edge.target
        return edge.target, edge.source

    @classmethod
    def _validate_closed_boundary(cls, face: Face, edges: dict[str, Edge]) -> None:
        if not face.boundary:
            return
        endpoints = [
            cls._oriented_endpoints(reference, edges) for reference in face.boundary
        ]
        for index, (_, end) in enumerate(endpoints):
            next_start, _ = endpoints[(index + 1) % len(endpoints)]
            if end != next_start:
                raise ValueError(
                    f"Boundary walk of face {face.id!r} is not closed between "
                    f"positions {index} and {(index + 1) % len(endpoints)}."
                )

    @property
    def vertex_ids(self) -> tuple[str, ...]:
        """Return vertex identifiers in ``C0`` basis order."""

        return tuple(vertex.id for vertex in self.vertices)

    @property
    def edge_ids(self) -> tuple[str, ...]:
        """Return edge identifiers in ``C1`` basis and qubit order."""

        return tuple(edge.id for edge in self.edges)

    @property
    def face_ids(self) -> tuple[str, ...]:
        """Return face identifiers in ``C2`` basis order."""

        return tuple(face.id for face in self.faces)

    def boundary_matrices(self) -> tuple[BinaryArray, BinaryArray]:
        """Return ``(d1, d2)`` using vertex, edge, and face tuple order."""

        vertex_index = {label: index for index, label in enumerate(self.vertex_ids)}
        edge_index = {label: index for index, label in enumerate(self.edge_ids)}
        d1 = np.zeros((len(self.vertices), len(self.edges)), dtype=np.uint8)
        d2 = np.zeros((len(self.edges), len(self.faces)), dtype=np.uint8)

        for column, edge in enumerate(self.edges):
            d1[vertex_index[edge.source], column] ^= 1
            d1[vertex_index[edge.target], column] ^= 1

        for column, face in enumerate(self.faces):
            for reference in face.boundary:
                d2[edge_index[reference.edge_id], column] ^= 1

        return (
            as_binary_matrix(d1, name="d1"),
            as_binary_matrix(d2, name="d2"),
        )

    def to_chain_complex(self) -> "ChainComplex2D":
        """Construct and validate the associated three-term chain complex."""

        from homoloqode.topology.chain_complex import ChainComplex2D

        d1, d2 = self.boundary_matrices()
        return ChainComplex2D(
            d1=d1,
            d2=d2,
            c0_labels=self.vertex_ids,
            c1_labels=self.edge_ids,
            c2_labels=self.face_ids,
        )
