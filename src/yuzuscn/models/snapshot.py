from typing import List, Dict, Any, Optional, Union, Literal, Callable
from pydantic import (
    Field,
    RootModel,
    BaseModel,
    ConfigDict,
    model_validator,
    model_serializer,
)

from .types import KeyValuePair


class Replay(BaseModel):
    """Represents the replay object in the state snapshot."""

    filename: Optional[str] = None
    """Filename of the replay."""
    loop: Optional[int] = None
    """`0` for no loop, `1` for loop."""
    start: Optional[Any] = None
    """Usually `None`, didn't see any other values."""
    state: Optional[int] = None
    """`0` for stopped, `1` for playing?"""
    volume: Optional[int] = None
    """Volume level, usually 0-100."""

    model_config = ConfigDict(
        extra="allow",
    )


class Update(BaseModel):
    """Represents the update object in the state snapshot."""

    state: Optional[int] = None
    """Same as Replay.state."""

    model_config = ConfigDict(
        extra="allow",
    )


class Transform(BaseModel):
    """Represents the transform object in the state snapshot."""

    method: Optional[str] = None
    """
    Transformation method, e.g., "crossfade"  
    """
    msgoff: Optional[bool] = None
    rule: Optional[str] = None
    time: int
    """Time in milliseconds."""

    model_config = ConfigDict(
        extra="allow",
    )


class ImageFileOptions(BaseModel):
    """Represents the options for image files in the state snapshot."""

    dress: Optional[str] = None
    face: Optional[str] = None
    pose: Optional[str] = None
    center: Optional[int] = None
    """Only seen in bar layers."""

    model_config = ConfigDict(
        extra="allow",
    )


class ImageFileDetails(BaseModel):
    """Represents the image file details in the state snapshot."""

    file: str
    options: Optional[ImageFileOptions] = None
    redraw: Optional[List[List[Any]]] = None
    """
    Used for image effects like blurring.  
    Only seen for stages.  
    Possible values:
    - `None`: No effects.
    - `[["doBoxBlur", 1, 1], ["doBoxBlur", 1, 1]]`: Two blurs with the same parameters.
    - `[["doBoxBlur", 2, 2], ["doBoxBlur", 2, 2]]`: Two blurs with the same parameters.
    """

    model_config = ConfigDict(
        extra="allow",
    )


class Redraw(BaseModel):
    """Represents the redraw object in the state snapshot."""

    disp: int
    """
    Display mode.  
    Observed values:
    - `2`: Displayed.
    - `4`: Hidden? Always appears with `posName: "無"`.
    """
    imageFile: ImageFileDetails
    posName: Optional[str] = None
    """Position name like '無', '出', '左', '右', '中', '顔', etc."""

    model_config = ConfigDict(
        extra="allow",
    )


class BgmDetails(BaseModel):
    """Represents the BGM details in the state snapshot."""

    name: str
    replay: Replay
    update: Update

    model_config = ConfigDict(
        extra="allow",
    )


class LoopSEDetails(BaseModel):
    """Represents the LSE(Looping Sound Effect) details in the state snapshot."""

    action: Optional[List[KeyValuePair]] = None
    name: str
    replay: Replay
    trans: Optional[Transform] = None
    update: Update

    model_config = ConfigDict(
        extra="allow",
    )


class StageDetails(BaseModel):
    """Represents the stage details in the state snapshot."""

    action: Optional[List[KeyValuePair]] = None
    class_name: Literal["stage"] = Field(..., alias="class")
    link: Optional[str] = ""
    name: str
    redraw: Redraw
    showmode: int
    """Show mode.  
    Observed values:
    - `0`: Hidden.
    - `1`: Appearing.
    - `2`: Disappearing.
    - `3`: Shown.
    """
    trans: Optional[Transform] = None
    type: Optional[Any] = None
    """Often `None`."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,  # Allows using field names as aliases during init
    )


class CharacterDetails(BaseModel):
    action: Optional[List[KeyValuePair]] = None
    hideact: Optional[List[KeyValuePair]] = None
    class_name: Literal["character"] = Field(..., alias="class")
    link: Optional[str] = ""
    """Often empty string."""
    name: str
    redraw: Optional[Redraw] = None
    showmode: int
    """Show mode.
    Observed values:
    - `0`: Hidden.
    - `1`: Appearing.
    - `2`: Disappearing.
    - `3`: Shown.
    """
    trans: Optional[Transform] = None
    """Transform object, often `None`."""
    type: Optional[Any] = None

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,  # Allows using field names as aliases during init
    )


class MsgwinDetails(BaseModel):
    """Represents the message window details in the state snapshot."""

    action: Optional[List[KeyValuePair]] = None
    hideact: Optional[List[KeyValuePair]] = None
    class_name: Literal["msgwin"] = Field(..., alias="class")
    link: Optional[str] = ""
    name: str
    # Redraw might be optional if the msgwin itself isn't showing specific content (showmode 0)
    redraw: Optional[Redraw] = None
    showmode: int
    type: Optional[Any] = None

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,  # Allows using field names as aliases during init
    )


class EventDetails(BaseModel):
    """Represents the event details(CGs) in the state snapshot."""

    action: Optional[List[KeyValuePair]] = None
    class_name: Literal["event"] = Field(..., alias="class")
    name: str
    redraw: Optional[Redraw] = None
    showmode: int
    type: Optional[Any] = None

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,  # Allows using field names as aliases during init
    )


class Event2Details(BaseModel):
    """Represents the event details(CGs) in the state snapshot."""

    action: Optional[List[KeyValuePair]] = None
    class_name: Literal["event2"] = Field(..., alias="class")
    name: str
    redraw: Optional[Redraw] = None
    showmode: int
    type: Optional[Any] = None

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,  # Allows using field names as aliases during init
    )


class CenterlayerDetails(BaseModel):
    """Represents the center layer details(UI overlays) in the state snapshot."""

    action: Optional[List[KeyValuePair]] = None
    class_name: Literal["centerlayer"] = Field(..., alias="class")
    link: Optional[str] = ""
    name: str
    redraw: Redraw
    showmode: int
    type: Optional[Any] = None

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,  # Allows using field names as aliases during init
    )


class SEDetails(BaseModel):
    """Represents the SE details in the state snapshot."""

    name: str

    model_config = ConfigDict(
        extra="allow",
    )


class FixCaptionDetails(BaseModel):
    """Represents the fix caption details in the state snapshot."""

    action: Optional[List[Union[KeyValuePair, None]]] = None
    class_name: Literal["fixcaption"] = Field(..., alias="class")
    link: Optional[str] = ""
    name: str
    redraw: Optional[Redraw] = None
    showmode: int
    type: Optional[Any] = None


details_map: Dict[str, Callable] = {
    "bgm": BgmDetails.model_validate,
    "loopse": LoopSEDetails.model_validate,
    "stage": StageDetails.model_validate,
    "character": CharacterDetails.model_validate,
    "msgwin": MsgwinDetails.model_validate,
    "event": EventDetails.model_validate,
    "event2": Event2Details.model_validate,
    "centerlayer": CenterlayerDetails.model_validate,
    "se": SEDetails.model_validate,
    "fixcaption": FixCaptionDetails.model_validate,
}


DataItemDetails = RootModel[
    Union[
        BgmDetails,
        LoopSEDetails,
        StageDetails,
        CharacterDetails,
        MsgwinDetails,
        EventDetails,
        Event2Details,
        CenterlayerDetails,
        SEDetails,
        FixCaptionDetails,
        Dict[str, Any],  # Fallback for robustness
    ]
]
"""Represents the details of a data item in the snapshot."""


class DataItem(BaseModel):
    """Represents one item in the 'data' array."""

    name: str
    class_name: str = Field(..., alias="class")
    details: DataItemDetails

    model_config = ConfigDict(
        extra="allow",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_data_item(cls, data):
        if isinstance(data, list):
            # Unpack the list into the DataItem fields
            name, class_name, details = data
            if class_name not in details_map:
                print(f"Warning: Unknown class name: {class_name}")
            else:
                details = details_map[class_name](details)
            return {"name": name, "class": class_name, "details": details}
        return data

    @model_serializer(mode="wrap")
    def serialize_data_item(self, handler):
        # Serialize the DataItem to a list format
        return [self.name, self.class_name, self.details]


class ShowDate(BaseModel):
    """Represents the date object in the snapshot point line."""

    back: Optional[Any] = None  # Type unclear
    date: Optional[str] = None
    fore: Optional[Any] = None  # Type unclear
    nowShow: Optional[int] = None
    """Indicates if the date is showing.  
    Observed values:
    - `0`: Not showing.
    - `1`: Showing.
    """

    model_config = ConfigDict(
        extra="allow",
    )


class Env(BaseModel):
    """Represents the environment object in the snapshot point line."""

    name: str
    action: Optional[List[Optional[str]]] = None  # Seen in one envupdate

    model_config = ConfigDict(
        extra="allow",
    )


class SnapshotPoint(BaseModel):
    """A class to represent a Yuzu SCN snapshot point."""

    meswinchange: Optional[str] = Field(None, alias="_meswinchange")
    data: List[DataItem]
    env: Env
    phonechat_showing: Optional[int]
    """
    Indicates if the phone chat is showing.  
    Observed values:
    - `0`: Not showing.
    - `1`: Showing.
    """
    scnchart: Optional[str] = None
    showdate: Optional[ShowDate] = None

    model_config = ConfigDict(
        populate_by_name=True,  # Allows using field names as aliases during init
        extra="allow",
    )
