from typing import Optional, TypeAlias, List, Any, Union, Literal, Dict, Callable
from pydantic import (
    Field,
    BaseModel,
    RootModel,
    ConfigDict,
    model_validator,
    model_serializer,
)

from .snapshot import DataItemDetails, Transform


class InitInstruction(BaseModel):
    """Instruction model for Yuzu SCN EnvUpdate to initialize objects."""

    action: Literal["init"]
    status: int
    """Initialization status.
    Observed values:
    - `1`: Initialize
    """

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 2:
                raise ValueError("Invalid length")
            return {
                "action": data[0],
                "status": data[1],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [
            "init",
            self.status,
        ]


class NewInstruction(BaseModel):
    """Instruction model for Yuzu SCN EnvUpdate to define new objects."""

    action: Literal["new"]
    name: str
    class_name: str = Field(..., alias="class")

    model_config = ConfigDict(
        populate_by_name=True,  # Allows using field names as aliases during init
        extra="allow",
    )

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 3:
                raise ValueError("Invalid length")
            return {
                "action": data[0],
                "name": data[1],
                "class_name": data[2],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [
            "new",
            self.name,
            self.class_name,
        ]


class DeleteInstruction(BaseModel):
    """Instruction model for Yuzu SCN EnvUpdate to delete objects."""

    action: Literal["del"]
    name: str

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 2:
                raise ValueError("Invalid length")
            return {"action": data[0], "name": data[1]}
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [
            "del",
            self.name,
        ]


class RenameInstruction(BaseModel):
    """Instruction model for Yuzu SCN EnvUpdate to rename objects."""

    action: Literal["ren"]
    name: str
    new_name: str = Field(..., alias="new")

    model_config = ConfigDict(
        populate_by_name=True,  # Allows using field names as aliases during init
        extra="allow",
    )

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 3:
                raise ValueError("Invalid length")
            return {
                "action": data[0],
                "name": data[1],
                "new_name": data[2],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [
            "ren",
            self.name,
            self.new_name,
        ]


Instruction = RootModel[
    Union[
        InitInstruction,
        NewInstruction,
        DeleteInstruction,
        RenameInstruction,
    ]
]
"""Instruction model for Yuzu SCN files."""


instruction_map: Dict[str, Callable] = {
    "init": InitInstruction.model_validate,
    "new": NewInstruction.model_validate,
    "del": DeleteInstruction.model_validate,
    "ren": RenameInstruction.model_validate,
}


class WaitEntry(BaseModel):
    """Wait entry model for Yuzu SCN files."""

    mode: int
    """Wait mode.  
    Observed values:
    - `0`
    - `1`
    """
    name: str
    """Object name of the wait entry."""


class Wait(BaseModel):
    """Wait model for Yuzu SCN files."""

    list: List[Union[WaitEntry, None]]


class StartlineEvent(BaseModel):
    """Startline event model for Yuzu SCN files."""

    vflag: Optional[int] = None
    """
    Voice flag  
    `0`: Narrator  
    `2`: Player  
    `3`: Character
    """
    name: Optional[str] = None
    """
    Speaker name  
    `None`: Narrator  
    `""`: Player  
    `"<name>"`: Character
    """
    text: Optional[int] = None
    """
    Text flag  
    `None`: Narrator  
    `0`: No text to display? Only observed in dummy scenes and the last line of a non-dummy scene  
    `1`: Text to display?
    """

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) not in (1, 7):
                raise ValueError("Invalid length")
            if data[0] != "startline":
                raise ValueError("Invalid startline event")
            if len(data) == 1:
                return dict()
            return {
                "vflag": data[2],
                "name": data[4],
                "text": data[6],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        if self.vflag is None:
            return ["startline"]
        return [
            "startline",
            "vflag",
            self.vflag,
            "name",
            self.name,
            "text",
            self.text,
        ]


class EnvUpdateEvent(BaseModel):
    """Environment update event model for Yuzu SCN files."""

    pretrans: Optional[List[Instruction]] = None
    update: List[Union[Instruction, DataItemDetails]]
    revpretrans: Optional[List[Instruction]] = None
    revupdate: Optional[List[Union[Instruction, DataItemDetails]]] = None
    wait: Optional[Wait] = None
    trans: Optional[Transform] = None
    msgoff: Optional[int] = None
    """Message off flag, same as `msgoff` in `Transform`.  
    `0`: On  
    `1`: Off
    """

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) < 2:
                raise ValueError("Invalid length")
            if data[0] != "envupdate":
                raise ValueError("Invalid envupdate event")
            data = data[1:]
            if len(data) % 2 != 0:
                raise ValueError("Invalid length")
            key_value_pairs = {}
            for i in range(0, len(data), 2):
                key = data[i]
                value = data[i + 1]
                if key == "update" or key == "revupdate":
                    if isinstance(value, list):
                        value = [
                            instruction_map[item[0]](item)
                            if isinstance(item, list)
                            else DataItemDetails.model_validate(item)
                            for item in value
                        ]
                elif key == "pretrans" or key == "revpretrans":
                    if isinstance(value, list):
                        value = [instruction_map[item[0]](item) for item in value]
                key_value_pairs[key] = value

            return key_value_pairs
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        result = ["envupdate"]
        for key in [
            "pretrans",
            "update",
            "revpretrans",
            "revupdate",
            "wait",
            "trans",
            "msgoff",
        ]:
            value = getattr(self, key)
            if value is not None:
                result.extend([key, value])
        return result


class DelayRunEvent(BaseModel):
    """Delay run event model for Yuzu SCN files."""

    label: str
    """
    Loop tuner label for the delay run event.  
    For the use of changing layers, it will be `vl<i>` where `<i>` is the layer number starting from `1`.  
    It is corresponding to the `.sli` file of the voice file.
    """
    delay_event_type: str
    """
    Delay run event type.  
    Always `envupdate`.
    """
    update: List[DataItemDetails]
    revupdate: List[DataItemDetails]
    trans: Optional[Transform] = None

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) not in (7, 9):
                raise ValueError("Invalid length")
            if data[0] != "delayrun":
                raise ValueError("Invalid delayrun event")
            data = data[1:]
            key_value_pairs = {}
            key_value_pairs["label"] = data[0]
            key_value_pairs["delay_event_type"] = data[1]
            for i in range(2, len(data), 2):
                key = data[i]
                value = data[i + 1]
                key_value_pairs[key] = value
            return key_value_pairs
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        result = ["delayrun", self.label, self.delay_event_type]
        for key in ["update", "revupdate", "trans"]:
            value = getattr(self, key)
            if value is not None:
                result.extend([key, value])
        return result


class WaitEvent(BaseModel):
    """Wait event model for Yuzu SCN files."""

    time: int
    """Wait time in milliseconds."""

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 3:
                raise ValueError("Invalid length")
            if data[0] != "wait":
                raise ValueError("Invalid wait event")
            return {"time": data[2]}
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [
            "wait",
            "time",
            self.time,
        ]


class ScnChartEvent(BaseModel):
    """SCN chart event model for Yuzu SCN files."""

    action: str
    """Action to perform.  
    Observed values:
    - `enter`
    - `leave`
    """
    name: str
    """Scn chart name, corresponds to game TJS scripts.  
    `"true"` for `leave` action.
    """

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 3:
                raise ValueError("Invalid length")
            if data[0] != "scnchart":
                raise ValueError("Invalid scnchart event")
            return {
                "action": data[1],
                "name": data[2],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [
            "scnchart",
            self.action,
            self.name,
        ]


class VoiceEffectEvent(BaseModel):
    """Voice effect event model for Yuzu SCN files."""

    action: str
    """Action to perform.  
    Observed values:
    - `clear`
    - `filter`
    """
    status: str
    """Voice effect status.
    Observed values:
    - `"true"`: On?
    - `"DSP_..."`: Effect name
    """

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 3:
                raise ValueError("Invalid length")
            if data[0] != "voeff":
                raise ValueError("Invalid voice effect event")
            return {
                "action": data[1],
                "status": data[2],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [
            "voeff",
            self.action,
            self.status,
        ]


class ChapterEvent(BaseModel):
    """Chapter event model for Yuzu SCN files."""

    values: List[Any]

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) < 2:
                raise ValueError("Invalid length")
            if data[0] != "chapter":
                raise ValueError("Invalid chapter event")
            return {
                "values": data[1:],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return ["chapter"] + self.values


class MsgOffEvent(BaseModel):
    """Message off event model for Yuzu SCN files."""

    event_type: Literal["msgoff"]

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 1:
                raise ValueError("Invalid length")
            if data[0] != "msgoff":
                raise ValueError("Invalid msgoff event")
            return {
                "event_type": data[0],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [self.event_type]


class MesWinChangeEvent(BaseModel):
    """Message window change event model for Yuzu SCN files."""

    type: str

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 3:
                raise ValueError("Invalid length, expected 3")
            if data[0] != "_meswinchange":
                raise ValueError("Invalid meswinchange event")
            return {
                "type": data[2],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [
            "_meswinchange",
            "type",
            self.type,
        ]


class QuickMenuEvent(BaseModel):
    """Quick menu event model for Yuzu SCN files."""

    action: str
    """Action to perform.  
    Observed values:
    - `fadein`
    - `fadeout`
    """
    status: str
    """Quick menu status.
    Observed values:
    - `"true"`: On?
    """

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 3:
                raise ValueError("Invalid length")
            if data[0] != "quickmenu":
                raise ValueError("Invalid quickmenu event")
            return {
                "action": data[1],
                "status": data[2],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [
            "quickmenu",
            self.action,
            self.status,
        ]


class ErEvent(BaseModel):
    """ER event model for Yuzu SCN files."""

    values: List[Any]
    """ER event values."""

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) < 2:
                raise ValueError("Invalid length")
            if data[0] != "er":
                raise ValueError("Invalid er event")
            return {
                "values": data[1:],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return ["er"] + self.values


class EndRecollectionEvent(BaseModel):
    """End recollection event model for Yuzu SCN files."""

    type: Literal["endrecollection"]

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 1:
                raise ValueError("Invalid length")
            if data[0] != "endrecollection":
                raise ValueError("Invalid endrecollection event")
            return {
                "type": data[0],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [self.type]


class PlayVoiceEvent(BaseModel):
    """Play voice event model for Yuzu SCN files."""

    loop: int
    """Loop status.  
    Observed values:
    - `1`: Loop
    """
    name: str
    """Character name of the voice."""
    type: int
    """Voice type.  
    Observed values:
    - `2`
    """
    voice: str
    """Voice file name."""

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 9:
                raise ValueError("Invalid length")
            if data[0] != "playvoice":
                raise ValueError("Invalid playvoice event")
            return {
                "loop": data[2],
                "name": data[4],
                "type": data[6],
                "voice": data[8],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [
            "playvoice",
            "loop",
            self.loop,
            "name",
            self.name,
            "type",
            self.type,
            "voice",
            self.voice,
        ]


class StopVoiceEvent(BaseModel):
    """Stop voice event model for Yuzu SCN files."""

    name: str
    """Character name of the voice."""
    type: int
    """Voice type.  
    Observed values:
    - `2`
    """

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 5:
                raise ValueError("Invalid length")
            if data[0] != "stopvoice":
                raise ValueError("Invalid stopvoice event")
            return {
                "name": data[2],
                "type": data[4],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [
            "stopvoice",
            "name",
            self.name,
            "type",
            self.type,
        ]


class ExitEvent(BaseModel):
    """Exit event model for Yuzu SCN files."""

    storage: str
    """Storage file name."""
    target: str
    """Target eval name?  
    Observed values:
    - `*endrecollectioneval`
    """
    eval: str
    """Eval a variable?  
    Observed values:
    - `kag.isRecollection`
    """

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 7:
                raise ValueError("Invalid length")
            if data[0] != "exit":
                raise ValueError("Invalid exit event")
            return {
                "storage": data[2],
                "target": data[4],
                "eval": data[6],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [
            "exit",
            "storage",
            self.storage,
            "target",
            self.target,
            "eval",
            self.eval,
        ]


class BeginSkipEvent(BaseModel):
    """Begin skip event model for Yuzu SCN files."""

    type: Literal["beginskip"]

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 1:
                raise ValueError("Invalid length")
            if data[0] != "beginskip":
                raise ValueError("Invalid beginskip event")
            return {
                "type": data[0],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [self.type]


class EndSkipEvent(BaseModel):
    """End skip event model for Yuzu SCN files."""

    type: Literal["endskip"]

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 1:
                raise ValueError("Invalid length")
            if data[0] != "endskip":
                raise ValueError("Invalid endskip event")
            return {
                "type": data[0],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [self.type]


class SysVoiceEvent(BaseModel):
    """System voice event model for Yuzu SCN files."""

    eyecatch: str
    """Auto mouse move?  
    Observed values:
    - `"true"`: On?
    """
    name: str
    """Position name?  
    Observed values:
    - `title`
    """
    chara: str
    """Shortened character name (e.g., `kag` for `Kagura`), same in voice file names."""

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data):
        if isinstance(data, list):
            if len(data) != 7:
                raise ValueError("Invalid length")
            if data[0] != "sysvoice":
                raise ValueError("Invalid sysvoice event")
            return {
                "eyecatch": data[2],
                "name": data[4],
                "chara": data[6],
            }
        return data

    @model_serializer(mode="wrap")
    def dump_as_list(self, handler):
        return [
            "sysvoice",
            "eyecatch",
            self.eyecatch,
            "name",
            self.name,
            "chara",
            self.chara,
        ]


FallbackEvent: TypeAlias = List[Any]
"""
Fallback event model for Yuzu SCN files.

This is a placeholder for any event that doesn't match the defined models.

Observed but not yet implemented events:
"""


event_map: Dict[str, Callable] = {
    "startline": StartlineEvent.model_validate,
    "envupdate": EnvUpdateEvent.model_validate,
    "delayrun": DelayRunEvent.model_validate,
    "wait": WaitEvent.model_validate,
    "scnchart": ScnChartEvent.model_validate,
    "voeff": VoiceEffectEvent.model_validate,
    "chapter": ChapterEvent.model_validate,
    "msgoff": MsgOffEvent.model_validate,
    "_meswinchange": MesWinChangeEvent.model_validate,
    "quickmenu": QuickMenuEvent.model_validate,
    "er": ErEvent.model_validate,
    "endrecollection": EndRecollectionEvent.model_validate,
    "playvoice": PlayVoiceEvent.model_validate,
    "stopvoice": StopVoiceEvent.model_validate,
    "exit": ExitEvent.model_validate,
    "beginskip": BeginSkipEvent.model_validate,
    "endskip": EndSkipEvent.model_validate,
    "sysvoice": SysVoiceEvent.model_validate,
}


class Event(
    RootModel[
        Union[
            StartlineEvent,
            EnvUpdateEvent,
            DelayRunEvent,
            WaitEvent,
            ScnChartEvent,
            VoiceEffectEvent,
            ChapterEvent,
            MsgOffEvent,
            MesWinChangeEvent,
            QuickMenuEvent,
            ErEvent,
            EndRecollectionEvent,
            PlayVoiceEvent,
            StopVoiceEvent,
            ExitEvent,
            BeginSkipEvent,
            EndSkipEvent,
            SysVoiceEvent,
            FallbackEvent,
        ]
    ]
):
    """Event model for Yuzu SCN files."""

    @model_validator(mode="before")
    @classmethod
    def parse(cls, data):
        if isinstance(data, list):
            if len(data) < 1:
                raise ValueError("Invalid length")

            if data[0] not in event_map:
                print(f"Warning: Unknown event type: {data[0]}")
                return data
            return event_map[data[0]](data)
        return data
