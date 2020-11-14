"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

import random
import sys
from dataclasses import dataclass, field
from typing import List

from cloudstate.contexts import ClientActionContext
from cloudstate.entity_pb2 import Forward, SideEffect


@dataclass
class ActionContext(ClientActionContext):
    command_name: str
    errors: List[str] = field(default_factory=list)
    effects: List[SideEffect] = field(default_factory=list)
    forward: Forward = None

    # todo: is this correct? there is no command_id on the stateless function requests.
    command_id = random.randint(0, sys.maxsize)
