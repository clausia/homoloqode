"""Reference periodic square cellulations and their CSS codes."""

from __future__ import annotations

from homoloqode.topology.cell_complex import (
    CellComplex2D,
    Edge,
    Face,
    OrientedEdge,
    Vertex,
)


def _vertex_id(x: int, y: int) -> str:
    return f"v[{x},{y}]"


def _horizontal_id(x: int, y: int) -> str:
    return f"e_h[{x},{y}]"


def _vertical_id(x: int, y: int) -> str:
    return f"e_v[{x},{y}]"


def square_toric_complex(size: int) -> CellComplex2D:
    """Construct an ``size x size`` square cellulation of the torus.

    Coordinates are interpreted modulo ``size``. Horizontal edges point in the
    positive x direction and vertical edges in the positive y direction.
    """

    if not isinstance(size, int) or isinstance(size, bool) or size < 1:
        raise ValueError("Toric lattice size must be a positive integer.")

    vertices = tuple(
        Vertex(_vertex_id(x, y), coordinates=(float(x), float(y)))
        for y in range(size)
        for x in range(size)
    )
    horizontal_edges = tuple(
        Edge(
            _horizontal_id(x, y),
            source=_vertex_id(x, y),
            target=_vertex_id((x + 1) % size, y),
        )
        for y in range(size)
        for x in range(size)
    )
    vertical_edges = tuple(
        Edge(
            _vertical_id(x, y),
            source=_vertex_id(x, y),
            target=_vertex_id(x, (y + 1) % size),
        )
        for y in range(size)
        for x in range(size)
    )
    faces = tuple(
        Face(
            id=f"f[{x},{y}]",
            boundary=(
                OrientedEdge(_horizontal_id(x, y), +1),
                OrientedEdge(_vertical_id((x + 1) % size, y), +1),
                OrientedEdge(_horizontal_id(x, (y + 1) % size), -1),
                OrientedEdge(_vertical_id(x, y), -1),
            ),
        )
        for y in range(size)
        for x in range(size)
    )
    return CellComplex2D(
        vertices=vertices,
        edges=horizontal_edges + vertical_edges,
        faces=faces,
    )


def toric_code(size: int) -> "CSSCode":
    """Construct the homological CSS code for a periodic square lattice."""

    return square_toric_complex(size).to_chain_complex().to_css_code()

