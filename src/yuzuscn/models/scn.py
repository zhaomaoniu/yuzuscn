from pydantic import BaseModel
from typing import Dict, List, Union

from .scene import Scene
from .types import Language


class Scn(BaseModel):
    """
    A class to represent a Yuzu SCN file.
    """

    hash: str
    languages: List[Language]
    llmap: List[Dict[str, Union[str, List[int]]]]
    """```
[
    {
        "<scn.scene.label>": [
            7,
            10,
            13,
            ...
        ], # All non-dummy scenes
        "name": "<scn.name>_<language>.ks"
    }
]
```"""
    name: str
    outlines: List
    """Seems always empty."""
    scenes: List[Scene]
