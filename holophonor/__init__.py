from ._version import __version__
from pluggy import HookimplMarker

holoimpl = HookimplMarker("holophonor")
"""Marker to be imported and used in plugins (and for own implementations)"""

__all__ = ["__version__", "holoimpl"]
