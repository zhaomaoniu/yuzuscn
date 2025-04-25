from typing import List, TypeAlias, Union, Optional, Any, Dict
from pydantic import BaseModel, model_serializer, model_validator, RootModel

from .types import KeyValuePair
from .snapshot import SnapshotPoint
from .events import Event as EventLine


class SnapshotPointLine(BaseModel):
    """
    A class to represent a Yuzu SCN snapshot point line.
    """

    index: int
    """
    The index of the snapshot point.  
    Increments from 1 to `<scn.scene.spCount>`.
    """
    text_index_a: Union[int, SnapshotPoint]
    """
    A mixed sequence of integers and SnapshotPoints, where the integers are the indices of the text lines.  
    SnapshotPoints always appear when `<scn.scene.lines.select(SnapshotPointLine)[n-1]> is None`.  
    i.e. 
    ```
    snapshot_point_lines = [line for line in scene.lines if isinstance(line, SnapshotPointLine)]
    for i in range(len(snapshot_point_lines) - 1):
        if snapshot_point_lines[i].text_index_a is None:
            assert isinstance(snapshot_point_lines[i + 1].text_index_a, SnapshotPoint)
    ``` 
    """
    text_index_b: Optional[int]
    """
    A mixed sequence of integers and None, where the integers are the indices of the text lines.  
    In a valid list of snapshot points, if `text_index_b` is None, then in the next line, `text_index_a` must be a SnapshotPoint.  
    i.e.
    ```
    snapshot_point_lines = [line for line in scene.lines if isinstance(line, SnapshotPointLine)]
    for i in range(len(snapshot_point_lines) - 1):
        if snapshot_point_lines[i].text_index_b is None:
            assert isinstance(snapshot_point_lines[i + 1].text_index_a, SnapshotPoint)
    ```
    """
    flag: Optional[int]
    """
    A flag that indicates whether the line is the start or end of snapshot points.  
    `1`: start or end of snapshot points.  
    `None`: otherwise.
    """
    original_line: int
    """
    The original line number in the `.ks` file.  
    It will always be greater than or equal to `<scn.scene.firstLine>`.
    """
    voice_tag: Optional[int]
    """
    A value corresponding to `<scn.scene.text[3]>`.  
    If `text_index_b` is None, this field is also None.
    """
    unused_a: Optional[Any] = None
    """
    Mostly `None`, but sometimes it is a string.
    """
    unused_b: Optional[Any] = None

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            keys = [
                "index",
                "text_index_a",
                "text_index_b",
                "flag",
                "original_line",
                "voice_tag",
                "unused_a",
                "unused_b",
            ]
            if len(data) not in (5, 8):
                raise ValueError("Line must have 5 or 8 elements")
            d = dict(zip(keys, data + [None] * (8 - len(data))))
            if isinstance(d["text_index_a"], dict):
                d["text_index_a"] = SnapshotPoint.model_validate(d["text_index_a"])
            return d
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        lst = [
            self.index,
            self.text_index_a,
            self.text_index_b,
            self.flag,
            self.original_line,
        ]
        if self.text_index_b is not None:
            lst += [self.voice_tag, self.unused_a, self.unused_b]
        return lst


TextIndexLine: TypeAlias = int
ResourceLine: TypeAlias = str


class Line(
    RootModel[
        Union[
            SnapshotPointLine,
            EventLine,
            TextIndexLine,
            ResourceLine,
        ]
    ]
):
    """A class to represent a Yuzu SCN line."""

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) == 0:
                raise ValueError("Line must have at least 1 element")
            if isinstance(data[0], str):
                return EventLine.model_validate(data)
            elif isinstance(data[0], int):
                return SnapshotPointLine.model_validate(data)
            else:
                raise ValueError("Line must be a list of strings or integers")
        return data


class Dialogue(BaseModel):
    """
    A class to represent Yuzu SCN text data.
    """

    display_name: Optional[str] = None
    content: str
    length: Optional[int]

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            keys = [
                "display_name",
                "content",
                "length",
            ]
            if len(data) < 2:
                raise ValueError("A dialogue must have at least 2 elements")
            d = dict(zip(keys, data + [None] * max(3 - len(data), 0)))
            return d
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        lst = [
            self.display_name,
            self.content,
        ]
        if self.length is not None:
            lst.append(self.length)
        return lst


class VoiceData(BaseModel):
    """
    A class to represent a Yuzu SCN voice data.
    """

    name: str
    pan: int
    type: int
    voice: str


class Text(BaseModel):
    """
    A class to represent a Yuzu SCN text line.
    """

    character: Optional[str]
    dialogues: List[Dialogue]
    voices: Optional[List[VoiceData]]
    value: int
    snapshot_point: SnapshotPoint

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            keys = [
                "character",
                "dialogues",
                "voices",
                "value",
                "snapshot_point",
            ]
            if len(data) != 5:
                raise ValueError("Line must have 5 elements")
            d = dict(zip(keys, data))
            return d
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        lst = [
            self.character,
            self.dialogues,
            self.voices,
            self.value,
            self.snapshot_point,
        ]
        return lst


class Next(BaseModel):
    """
    A class to represent a Yuzu SCN next scene.
    """

    storage: str
    """`<scn.name>`"""
    target: str
    """`<scn.scene.label>`"""
    type: int


class Scene(BaseModel):
    """
    A class to represent a Yuzu SCN scene.
    """

    firstLine: int
    jumplabels: Optional[Dict[str, int]] = None
    label: str
    lines: List[Line]
    nexts: List[Next]
    preevals: Optional[List[Union[KeyValuePair, str]]] = None
    """key-value pairs of variables to be set before the scene is loaded."""
    postevals: Optional[List[Union[KeyValuePair, str]]] = None
    """key-value pairs of variables to be set after the scene is loaded."""
    spCount: int
    """
    Number of snapshot point.  
    Should be equal to `<scn.scene.lines.select(SnapshotPointLine)[0]>`.
    """
    texts: Optional[List[Text]] = None
    """
    Dialogues in the scene.  
    Dummy scenes usually don't have this field.
    """
    title: Union[List[str], str]
    """
    For dummy scenes, this is usually an empty string.  
    For real scenes, this may be a list of titles for each language.
    """
    version: int

    @model_serializer(mode="wrap")
    def dump_without_none(self, handler):
        return {
            k: getattr(self, k)
            for k in [
                "firstLine",
                "jumplabels",
                "label",
                "lines",
                "nexts",
                "preevals",
                "postevals",
                "spCount",
                "texts",
                "title",
                "version",
            ]
            if getattr(self, k) is not None
        }
