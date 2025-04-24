from typing import Literal, TypeAlias, List, Any


KeyValuePair = List[Any]
"""
Represents actions, e.g., ["fade", 25], ["zoomx", 150], etc.  
Note that most of pairs only have 2 elements, but some have 3 or more.  
```
[
    "xpos",
    [
        {
            "handler": "MoveAction",
            "start": "@+50",
            "time": 300,
            "value": "@"
        }
    ],
    1
]
"""
Language: TypeAlias = Literal["en", "cn", "tw"]
