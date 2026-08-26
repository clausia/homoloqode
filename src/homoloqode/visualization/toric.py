"""Matplotlib visualization of a square toric complex.

Vertices are checks/qubit endpoints; edges are qubits. Coordinates come
straight from ``complex_.vertices``. Edge-level overlays (``x_error``,
``z_error``, ``logical_x``, ``logical_z``) must have one entry per edge,
in ``complex_.edges`` order -- confirmed to match qubit-index order used
by ``CellComplex2D.to_chain_complex`` (columns are built by
``enumerate(self.edges)``). ``x_syndrome`` has one entry per vertex
(X-checks); ``z_syndrome`` one entry per face (Z-checks) -- matching the
homological dictionary H_X = boundary-1, H_Z = boundary-2^T.

Periodic wrap edges: a naive straight line from a wrap edge's source to
its real target either crosses the whole square or, on this axis-aligned
square lattice specifically, lands exactly on top of real edges along the
same row/column (verified: e.g. a vertical wrap from (1,L-1) to (1,0)
passes straight through (1,1) and overlaps the two real edges already
there). Either way nothing in the picture would show the edge is special.
Fixed by drawing wraps as a short stub exiting the boundary (a "repeated
boundary strip" / fundamental-polygon style diagram) instead of the real
target: extend one lattice step past the source, in the same direction,
using the exact size L = max(x-coordinate) + 1.
SO here is the final strategy:
Wrap detection is done by parsing the exact grid position out of the edge
id string (e_h[x,y] wraps iff x == L-1; e_v[x,y] wraps iff y == L-1),
not by comparing coordinate distances -- at L=2 a wrap and a normal edge
both jump exactly 1 unit and are not distinguishable by coordinates alone,
so the id, not the geometry, is the source of truth. This id convention
(e_h/e_v/v[x,y]/f[x,y]) is specific to square_toric_complex; this function
is scoped to that generator only, not to CellComplex2D in general.

Face centers: derived directly from the f[x,y] id as (x+0.5, y+0.5), not
by averaging the coordinates of the face's touched vertices. Averaging
breaks for any face that crosses the periodic boundary: for L=3, f[2,0]'s
vertices sit at x=2 and x=0, and averaging gives x=(2+0+2+0)/4=1.0 instead
of the correct x=2.5 -- pulling the center into the interior (and, for
f[2,2] specifically, landing it exactly on top of vertex v[1,1]). Deriving
from the id directly avoids this, and is consistent with the same
"extend past L rather than wrap to 0" convention already used for wrap
edges above.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

import numpy as np
from numpy.typing import ArrayLike

from homoloqode.topology.cell_complex import CellComplex2D
from homoloqode.algebra.gf2 import as_binary_vector


def _parse_grid_position(edge_id: str) -> tuple[int, int]:
    """Parse the exact (x, y) grid position out of an e_h[x,y]/e_v[x,y]/f[x,y] id."""
    inner = edge_id[edge_id.index("[") + 1 : edge_id.index("]")]
    x_str, y_str = inner.split(",")
    return int(x_str), int(y_str)      # well use this later to determine if the edge is in the end aka if it is wrap around


def _validated(vector: ArrayLike | None, *, length: int, name: str) -> np.ndarray:
    """Return a validated binary vector of the given length, or an all-zero
    default of that length if vector is None."""
    if vector is None:
        return np.zeros(length, dtype=np.uint8)
    validated = as_binary_vector(vector, name=name)
    if validated.shape[0] != length:
        raise ValueError(f"{name} must have length {length}; got {validated.shape[0]}.")
    return validated


def plot_square_toric_complex(
    complex_: CellComplex2D,
    *,
    x_error: ArrayLike | None = None,
    z_error: ArrayLike | None = None,
    x_syndrome: ArrayLike | None = None,
    z_syndrome: ArrayLike | None = None,
    logical_x: ArrayLike | None = None,
    logical_z: ArrayLike | None = None,
    ax: Axes | None = None,
) -> tuple[Figure, Axes]:
    """Plot a square toric complex, with optional error/syndrome/logical overlays.

    Input objects (``complex_`` and every overlay array) are read only;
    none are modified. Draws vertices, edges (colored/styled by whichever
    of x_error/z_error/logical_x/logical_z apply, with Y = x_error AND
    z_error both set), face centers, and violated-check markers for
    x_syndrome (open blue circles on vertices) and z_syndrome (open red
    squares on face centers). Periodic wrap edges are drawn as short
    stubs exiting the boundary; face centers are derived from the f[x,y]
    id, not averaged from vertex coordinates; see the module docstring
    for why both are necessary.

    If ``ax`` is given, drawing happens on it directly and its owning
    Figure is reused (via ``ax.figure``); otherwise a new Figure/Axes
    pair is created.
    """

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    n = len(complex_.edges)
    x_error = _validated(x_error, length=n, name="x_error")
    z_error = _validated(z_error, length=n, name="z_error")
    logical_x = _validated(logical_x, length=n, name="logical_x")
    logical_z = _validated(logical_z, length=n, name="logical_z")
    x_syndrome = _validated(x_syndrome, length=len(complex_.vertices), name="x_syndrome")
    z_syndrome = _validated(z_syndrome, length=len(complex_.faces), name="z_syndrome")

    ## here we are trying to define a dictonary for different colors instead of repeating them or write a new code eachtiem

    used_labels = set()

    def _label(text):
        """Return text the first time it's used, None on repeats -- keeps
        the legend from showing one duplicate entry per matching edge."""
        if text in used_labels:
            return None
        used_labels.add(text)
        return text

    style_by_index = {}
    for i in range(n):
        if x_error[i] and z_error[i]:
            style_by_index[i] = {"color": "purple", "linewidth": 3, "label": _label("Y-error")}
        elif x_error[i]:
            style_by_index[i] = {"color": "blue", "linewidth": 3, "label": _label("X-error")}
        elif z_error[i]:
            style_by_index[i] = {"color": "red", "linewidth": 3, "label": _label("Z-error")}
        elif logical_x[i]:
            style_by_index[i] = {"color": "green", "linestyle": "dashed", "linewidth": 2, "label": _label("logical X")}
        elif logical_z[i]:
            style_by_index[i] = {"color": "orange", "linestyle": "dashed", "linewidth": 2, "label": _label("logical Z")}
        else:
            style_by_index[i] = {"color": "gray", "linewidth": 1, "label": None}

    xs = [v.coordinates[0] for v in complex_.vertices]
    ys = [v.coordinates[1] for v in complex_.vertices]
    ax.scatter(xs, ys, color="black", zorder=3)

    L = int(max(xs)) + 1
    coords = {v.id: v.coordinates for v in complex_.vertices}

    for i, e in enumerate(complex_.edges):
        x1, y1 = coords[e.source]
        x2, y2 = coords[e.target]
        grid_x, grid_y = _parse_grid_position(e.id)
        is_horizontal = e.id.startswith("e_h")
        is_wrap = (is_horizontal and grid_x == L - 1) or (not is_horizontal and grid_y == L - 1)
        if is_wrap and is_horizontal:
            x2 = x1 + 1
        elif is_wrap and not is_horizontal:
            y2 = y1 + 1

        style = style_by_index[i]
        ax.plot([x1, x2], [y1, y2], zorder=1, **style)   # new syntax **style directly unpacks dictonary

    violated_vx = [v.coordinates[0] for i, v in enumerate(complex_.vertices) if x_syndrome[i]]
    violated_vy = [v.coordinates[1] for i, v in enumerate(complex_.vertices) if x_syndrome[i]]
    if violated_vx:
        ax.scatter(violated_vx, violated_vy, s=250, facecolors="none", edgecolors="blue",
                    linewidth=2, marker="o", zorder=4, label=_label("violated X-check"))

    face_centers = []
    for f in complex_.faces:
        fx, fy = _parse_grid_position(f.id)
        face_centers.append((fx + 0.5, fy + 0.5))

    ax.scatter([c[0] for c in face_centers], [c[1] for c in face_centers],
                color="lightgray", s=15, zorder=2, label=_label("face center"))

    violated_fx = [c[0] for i, c in enumerate(face_centers) if z_syndrome[i]]
    violated_fy = [c[1] for i, c in enumerate(face_centers) if z_syndrome[i]]
    if violated_fx:
        ax.scatter(violated_fx, violated_fy, s=250, facecolors="none", edgecolors="red",
                    linewidth=2, marker="s", zorder=4, label=_label("violated Z-check"))

    ax.set_aspect("equal")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0))
    return fig, ax