"""Tác giả: Doan Van Tai. Smoke test của môi trường package smr."""
import smr


def test_package_imports():
    assert smr.__version__
