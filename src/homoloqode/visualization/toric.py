"""Matplotlib visualization for ``square_toric_complex`` geometries.

Periodic edges are drawn as short stubs leaving the fundamental square. Face
centers are derived from the stable ``f[x,y]`` identifiers so faces crossing a
periodic boundary remain at the boundary instead of being averaged inward.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import numpy as np
from numpy.typing import ArrayLike

from homoloqode.algebra.gf2 import as_binary_vector
from homoloqode.topology.cell_complex import CellComplex2D


def _parse_grid_position(edge_id: str) -> tuple[int, int]:
    """Parse ``(x, y)`` from an ``e_h``, ``e_v``, or ``f`` identifier."""

    inner = edge_id[edge_id.index("[") + 1 : edge_id.index("]")]
    x_str, y_str = inner.split(",")
    return int(x_str), int(y_str)


def _validated(vector: ArrayLike | None, *, length: int, name: str) -> np.ndarray:
    """Return a length-validated vector or an all-zero default."""

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
    """Plot a square toric complex with optional binary overlays.

    Edge overlays ``x_error``, ``z_error``, ``logical_x``, and ``logical_z``
    follow ``complex_.edges`` order. ``x_syndrome`` follows vertex/X-check
    order, while ``z_syndrome`` follows face/Z-check order. Input objects are
    read only and are never modified.

    Periodic edges are rendered as boundary stubs. If ``ax`` is supplied, its
    owning figure is reused; otherwise a new figure and axes are created.
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
    x_syndrome = _validated(
        x_syndrome,
        length=len(complex_.vertices),
        name="x_syndrome",
    )
    z_syndrome = _validated(
        z_syndrome,
        length=len(complex_.faces),
        name="z_syndrome",
    )

    used_labels = set()

    def _label(text: str) -> str | None:
        if text in used_labels:
            return None
        used_labels.add(text)
        return text

    style_by_index = {}
    for i in range(n):
        if x_error[i] and z_error[i]:
            style_by_index[i] = {
                "color": "purple",
                "linewidth": 3,
                "label": _label("Y-error"),
            }
        elif x_error[i]:
            style_by_index[i] = {
                "color": "blue",
                "linewidth": 3,
                "label": _label("X-error"),
            }
        elif z_error[i]:
            style_by_index[i] = {
                "color": "red",
                "linewidth": 3,
                "label": _label("Z-error"),
            }
        elif logical_x[i]:
            style_by_index[i] = {
                "color": "green",
                "linestyle": "dashed",
                "linewidth": 2,
                "label": _label("logical X"),
            }
        elif logical_z[i]:
            style_by_index[i] = {
                "color": "orange",
                "linestyle": "dashed",
                "linewidth": 2,
                "label": _label("logical Z"),
            }
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
        is_wrap = (is_horizontal and grid_x == L - 1) or (
            not is_horizontal and grid_y == L - 1
        )
        if is_wrap and is_horizontal:
            x2 = x1 + 1
        elif is_wrap and not is_horizontal:
            y2 = y1 + 1

        style = style_by_index[i]
        ax.plot([x1, x2], [y1, y2], zorder=1, **style)

    violated_vx = [
        vertex.coordinates[0]
        for index, vertex in enumerate(complex_.vertices)
        if x_syndrome[index]
    ]
    violated_vy = [
        vertex.coordinates[1]
        for index, vertex in enumerate(complex_.vertices)
        if x_syndrome[index]
    ]
    if violated_vx:
        ax.scatter(
            violated_vx,
            violated_vy,
            s=250,
            facecolors="none",
            edgecolors="blue",
            linewidth=2,
            marker="o",
            zorder=4,
            label=_label("violated X-check"),
        )

    face_centers = []
    for f in complex_.faces:
        fx, fy = _parse_grid_position(f.id)
        face_centers.append((fx + 0.5, fy + 0.5))

    ax.scatter(
        [center[0] for center in face_centers],
        [center[1] for center in face_centers],
        color="lightgray",
        s=15,
        zorder=2,
        label=_label("face center"),
    )

    violated_fx = [c[0] for i, c in enumerate(face_centers) if z_syndrome[i]]
    violated_fy = [c[1] for i, c in enumerate(face_centers) if z_syndrome[i]]
    if violated_fx:
        ax.scatter(
            violated_fx,
            violated_fy,
            s=250,
            facecolors="none",
            edgecolors="red",
            linewidth=2,
            marker="s",
            zorder=4,
            label=_label("violated Z-check"),
        )

    ax.set_aspect("equal")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0))
    return fig, ax
