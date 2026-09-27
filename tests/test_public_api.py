"""Regression tests for the documented package export surface."""

import importlib
import inspect

import pytest


PUBLIC_PACKAGES = (
    "homoloqode",
    "homoloqode.algebra",
    "homoloqode.codes",
    "homoloqode.decoders",
    "homoloqode.experiments",
    "homoloqode.integrations",
    "homoloqode.noise",
    "homoloqode.topology",
    "homoloqode.visualization",
)


@pytest.mark.parametrize("package_name", PUBLIC_PACKAGES)
def test_public_exports_are_named_importable_and_documented(
    package_name: str,
) -> None:
    package = importlib.import_module(package_name)

    assert package.__all__ == sorted(package.__all__)
    assert len(package.__all__) == len(set(package.__all__))
    for name in package.__all__:
        assert isinstance(name, str)
        assert hasattr(package, name)
        assert inspect.getdoc(getattr(package, name))
