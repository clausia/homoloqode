import numpy as np
import pytest

from homoloqode import (
    CellComplex2D,
    ChainComplex2D,
    Edge,
    Face,
    OrientedEdge,
    Vertex,
    square_toric_complex,
)
from homoloqode.algebra import matmul


@pytest.mark.parametrize(
    ("size", "cell_counts"),
    [
        (1, (1, 2, 1)),
        (2, (4, 8, 4)),
        (3, (9, 18, 9)),
    ],
)
def test_square_toric_cell_counts(
    size: int, cell_counts: tuple[int, int, int]
) -> None:
    complex_ = square_toric_complex(size)

    assert (
        len(complex_.vertices),
        len(complex_.edges),
        len(complex_.faces),
    ) == cell_counts


@pytest.mark.parametrize("size", [1, 2, 3])
def test_toric_boundary_maps_form_chain_complex(size: int) -> None:
    chain = square_toric_complex(size).to_chain_complex()

    assert not np.any(matmul(chain.d1, chain.d2))
    assert chain.delta0.shape == (2 * size * size, size * size)
    assert chain.delta1.shape == (size * size, 2 * size * size)


def test_repeated_loop_incidences_cancel_over_f2() -> None:
    chain = square_toric_complex(1).to_chain_complex()

    assert np.array_equal(chain.d1, np.zeros((1, 2), dtype=np.uint8))
    assert np.array_equal(chain.d2, np.zeros((2, 1), dtype=np.uint8))
    assert chain.betti_1 == 2


def test_open_face_boundary_is_rejected() -> None:
    with pytest.raises(ValueError, match="not closed"):
        CellComplex2D(
            vertices=(Vertex("a"), Vertex("b"), Vertex("c")),
            edges=(
                Edge("ab", "a", "b"),
                Edge("bc", "b", "c"),
            ),
            faces=(
                Face(
                    "f",
                    (
                        OrientedEdge("ab"),
                        OrientedEdge("bc"),
                    ),
                ),
            ),
        )


def test_invalid_chain_composition_is_rejected() -> None:
    with pytest.raises(ValueError, match="chain condition"):
        ChainComplex2D(
            d1=np.array([[1]], dtype=np.uint8),
            d2=np.array([[1]], dtype=np.uint8),
        )


@pytest.mark.parametrize("size", [0, -1, True, 1.5])
def test_toric_size_must_be_a_positive_integer(size: object) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        square_toric_complex(size)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "factory",
    [
        lambda: Vertex(""),
        lambda: Edge("", "a", "b"),
        lambda: Edge("e", "", "b"),
        lambda: Edge("e", "a", ""),
        lambda: OrientedEdge(""),
        lambda: Face("", ()),
    ],
)
def test_cell_identifiers_must_be_nonempty_strings(factory) -> None:
    with pytest.raises(ValueError, match="non-empty string"):
        factory()


@pytest.mark.parametrize("orientation", [0, 2, -2, True])
def test_oriented_edge_requires_a_signed_orientation(orientation: object) -> None:
    with pytest.raises(ValueError, match="orientation must be"):
        OrientedEdge("e", orientation=orientation)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("vertices", "edges", "faces", "kind"),
    [
        ((Vertex("v"), Vertex("v")), (), (), "Vertex"),
        (
            (Vertex("a"), Vertex("b")),
            (Edge("e", "a", "b"), Edge("e", "b", "a")),
            (),
            "Edge",
        ),
        (
            (Vertex("v"),),
            (),
            (Face("f", ()), Face("f", ())),
            "Face",
        ),
    ],
)
def test_cell_identifiers_must_be_unique(vertices, edges, faces, kind: str) -> None:
    with pytest.raises(ValueError, match=rf"{kind} ids must be unique"):
        CellComplex2D(vertices=vertices, edges=edges, faces=faces)


def test_edges_must_reference_vertices_in_the_complex() -> None:
    with pytest.raises(ValueError, match="outside the complex"):
        CellComplex2D(
            vertices=(Vertex("a"),),
            edges=(Edge("ab", "a", "b"),),
            faces=(),
        )


def test_faces_must_reference_edges_in_the_complex() -> None:
    with pytest.raises(ValueError, match="unknown edge"):
        CellComplex2D(
            vertices=(Vertex("a"),),
            edges=(),
            faces=(Face("f", (OrientedEdge("missing"),)),),
        )


def test_empty_face_boundary_is_valid() -> None:
    complex_ = CellComplex2D(
        vertices=(Vertex("v"),),
        edges=(),
        faces=(Face("f", ()),),
    )

    d1, d2 = complex_.boundary_matrices()
    assert d1.shape == (1, 0)
    assert d2.shape == (0, 1)


def test_chain_boundary_dimensions_must_be_compatible() -> None:
    with pytest.raises(ValueError, match="Boundary dimensions are incompatible"):
        ChainComplex2D(
            d1=np.zeros((1, 2), dtype=np.uint8),
            d2=np.zeros((3, 1), dtype=np.uint8),
        )


@pytest.mark.parametrize(
    ("labels", "message"),
    [
        (("a",), "Expected 2 labels"),
        (("a", "a"), "must be unique"),
        (("a", ""), "must be non-empty strings"),
        (("a", 1), "must be non-empty strings"),
    ],
)
def test_chain_basis_labels_are_validated(
    labels: tuple[object, ...], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        ChainComplex2D(
            d1=np.zeros((1, 2), dtype=np.uint8),
            d2=np.zeros((2, 0), dtype=np.uint8),
            c1_labels=labels,  # type: ignore[arg-type]
        )
