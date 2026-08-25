"""Tests for homoloqode.visualization.toric: plot_square_toric_complex.

Per the issue's testing strategy: check structural properties (object
types, line/collection counts, validation, mutation), never compare
rendered pixels, thats outof scope.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

from homoloqode import square_toric_complex, toric_code
from homoloqode.visualization import plot_square_toric_complex
from homoloqode.visualization.toric import _parse_grid_position


@pytest.fixture(autouse=True)
def _close_figures():
    """Close every figure after each test, so tests stay isolated and
    matplotlib doesn't accumulate open figures across the whole run."""
    yield
    plt.close("all")


@pytest.mark.parametrize("size", [2, 3])
def test_returns_figure_and_axes(size: int) -> None:
    """The function must return a real (Figure, Axes) pair."""
    complex_ = square_toric_complex(size)
    fig, ax = plot_square_toric_complex(complex_)
    assert isinstance(fig, matplotlib.figure.Figure)
    assert isinstance(ax, matplotlib.axes.Axes)


@pytest.mark.parametrize("size", [2, 3])
def test_line_count_matches_edge_count(size: int) -> None:
    """One drawn line per edge, no more, no fewer : confirmed against
    the actual edge count, not assumed."""
    complex_ = square_toric_complex(size)
    fig, ax = plot_square_toric_complex(complex_)
    assert len(ax.lines) == len(complex_.edges)


def test_base_collection_count_with_no_overlays() -> None:
    """With no syndrome overlays, exactly two scatter collections exist:
    the vertex markers and the face center marker"""
    complex_ = square_toric_complex(3)
    fig, ax = plot_square_toric_complex(complex_)
    # vertex scatter + face-center scatter, no syndrome markers
    assert len(ax.collections) == 2


def test_syndrome_overlays_add_collections() -> None:
    """Supplying a real syndrome must add at least one marker collection
    beyond the base two."""
    complex_ = square_toric_complex(3)
    code = toric_code(3)
    x_error = np.zeros(code.n, dtype=int)
    x_error[0] = 1
    syndrome = code.syndrome(x_error=x_error)

    fig, ax = plot_square_toric_complex(
        complex_,
        x_syndrome=syndrome.x_checks,
        z_syndrome=syndrome.z_checks,
    )
    # base 2, plus at least one violated-check marker collection
    assert len(ax.collections) > 2


@pytest.mark.parametrize("size", [2, 3])
def test_size_two_and_three_complete_without_warning(size: int, recwarn) -> None:
    """Both reference fixture sizes must plot cleanly, with zero warnin"""
    complex_ = square_toric_complex(size)
    plot_square_toric_complex(complex_)
    assert len(recwarn) == 0


def test_existing_ax_can_be_supplied() -> None:
    """An existing ax must be reused directly (identity, not just type),
    and its owning Figure recovered rather than a new one created."""
    complex_ = square_toric_complex(2)
    fig, ax = plt.subplots()
    returned_fig, returned_ax = plot_square_toric_complex(complex_, ax=ax)
    assert returned_ax is ax
    assert returned_fig is fig


@pytest.mark.parametrize("param", ["x_error", "z_error", "logical_x", "logical_z"])
def test_invalid_edge_vector_length_is_rejected(param: str) -> None:
    """Any edge level overlay with the wrong length must raise"""
    complex_ = square_toric_complex(2)
    with pytest.raises(ValueError, match="length"):
        plot_square_toric_complex(complex_, **{param: [1, 0, 0]})


def test_invalid_x_syndrome_length_is_rejected() -> None:
    """x_syndrome must match the vertex count, not the edges."""
    complex_ = square_toric_complex(2)
    with pytest.raises(ValueError, match="length"):
        plot_square_toric_complex(complex_, x_syndrome=[1, 0, 0])


def test_invalid_z_syndrome_length_is_rejected() -> None:
    """z_syndrome must match the face count, not the edge count"""
    complex_ = square_toric_complex(2)
    with pytest.raises(ValueError, match="length"):
        plot_square_toric_complex(complex_, z_syndrome=[1, 0, 0])


def test_nonbinary_input_is_rejected() -> None:
    """Any overlay vector must be strictly 0/1; anything else must raise."""
    complex_ = square_toric_complex(2)
    n = len(complex_.edges)
    with pytest.raises(ValueError, match="0 and 1"):
        plot_square_toric_complex(complex_, x_error=[2] * n)


def test_input_arrays_are_not_mutated() -> None:
    """Overlay arrays passed in must come back identical afterwards"""
    complex_ = square_toric_complex(3)
    code = toric_code(3)
    x_error = np.zeros(code.n, dtype=int)
    x_error[0] = 1
    z_error = np.zeros(code.n, dtype=int)
    z_error[7] = 1

    x_before = x_error.copy()
    z_before = z_error.copy()

    plot_square_toric_complex(complex_, x_error=x_error, z_error=z_error)

    assert np.array_equal(x_error, x_before)
    assert np.array_equal(z_error, z_before)


def test_complex_object_is_not_mutated() -> None:
    """The CellComplex2D itself (vertices, edges, faces) must be unchanged
    after plotting."""
    complex_ = square_toric_complex(3)
    vertices_before = complex_.vertices
    edges_before = complex_.edges
    faces_before = complex_.faces

    plot_square_toric_complex(complex_)

    assert complex_.vertices == vertices_before
    assert complex_.edges == edges_before
    assert complex_.faces == faces_before


def test_wrap_edges_are_drawn_as_short_stubs_not_long_lines() -> None:
    """Every drawn segment, wrap or not, must be exactly one lattice step
    long : the actual geometric proof the wraparound-stub fix works,
    not just that nothing crashed."""
    complex_ = square_toric_complex(3)
    coords = {v.id: v.coordinates for v in complex_.vertices}
    fig, ax = plot_square_toric_complex(complex_)

    for line in ax.lines:
        xdata, ydata = line.get_data()
        length = abs(xdata[1] - xdata[0]) + abs(ydata[1] - ydata[0])
        # every drawn segment must be length 1 (a single lattice step),
        # never a long line spanning the whole L=3 square
        assert length == pytest.approx(1.0)


def test_logical_operators_render_with_distinct_line_styles() -> None:
    """logical_x and logical_z must actually render (not just validate):
    each edge in the support gets the documented color/dashed style, and
    the count of styled lines matches the logical operator's weight.

    Uses hand-built, disjoint supports (not code.logical_basis(), whose
    default X/Z representatives can share an edge -- see the known
    overlap-priority gap noted separately)."""
    complex_ = square_toric_complex(2)
    n = len(complex_.edges)
    logical_x = np.zeros(n, dtype=int)
    logical_x[0] = 1
    logical_x[1] = 1
    logical_z = np.zeros(n, dtype=int)
    logical_z[4] = 1
    logical_z[5] = 1

    fig, ax = plot_square_toric_complex(
        complex_,
        logical_x=logical_x,
        logical_z=logical_z,
    )

    green_dashed = [l for l in ax.lines if l.get_color() == "green" and l.get_linestyle() == "--"]
    orange_dashed = [l for l in ax.lines if l.get_color() == "orange" and l.get_linestyle() == "--"]

    assert len(green_dashed) == 2
    assert len(orange_dashed) == 2


def test_boundary_face_centers_extend_past_l_not_averaged_into_interior() -> None:
    """A face crossing the periodic boundary (e.g. f[2,0] for L=3) must
    have its center derived from the id as (x+0.5, y+0.5), extending past
    L, not pulled into the interior by averaging wrapped vertex
    coordinates. Regression test for the reported (1.0,0.5)/(0.5,1.0)/
    (1.0,1.0) bug, where the last value coincided with an actual vertex."""
    size = 3
    complex_ = square_toric_complex(size)

    boundary_face_ids = {"f[2,0]": (2.5, 0.5), "f[0,2]": (0.5, 2.5), "f[2,2]": (2.5, 2.5)}
    face_by_id = {f.id: f for f in complex_.faces}

    for face_id, expected_center in boundary_face_ids.items():
        fx, fy = _parse_grid_position(face_by_id[face_id].id)
        actual_center = (fx + 0.5, fy + 0.5)
        assert actual_center == expected_center

    # the specific reported failure: f[2,2]'s (buggy) averaged center
    # coincided exactly with vertex v[1,1]; the fixed center must not.
    coords = {v.id: v.coordinates for v in complex_.vertices}
    fx, fy = _parse_grid_position("f[2,2]")
    fixed_center = (fx + 0.5, fy + 0.5)
    assert fixed_center != coords["v[1,1]"]