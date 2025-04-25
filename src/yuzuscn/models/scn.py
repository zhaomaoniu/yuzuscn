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

    def model_dump_json(
        self,
        *,
        indent=None,
        include=None,
        exclude=None,
        context=None,
        by_alias=True,  # set to True to use alias
        exclude_unset=False,
        exclude_defaults=False,
        exclude_none=False,
        round_trip=False,
        warnings=True,
        fallback=None,
        serialize_as_any=False,
    ):
        return super().model_dump_json(
            indent=indent,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            fallback=fallback,
            serialize_as_any=serialize_as_any,
        )

    def model_dump(
        self,
        *,
        mode="python",
        include=None,
        exclude=None,
        context=None,
        by_alias=True,  # set to True to use alias
        exclude_unset=False,
        exclude_defaults=False,
        exclude_none=False,
        round_trip=False,
        warnings=True,
        fallback=None,
        serialize_as_any=False,
    ):
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            fallback=fallback,
            serialize_as_any=serialize_as_any,
        )
