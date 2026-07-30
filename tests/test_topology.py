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

