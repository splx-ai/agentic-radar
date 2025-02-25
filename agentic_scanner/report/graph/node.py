from importlib import resources
from typing import Optional

import pydot

from ...graph import ToolType


class AgentNode(pydot.Node):
    def __init__(self, name: str, label: str):
        super().__init__(
            name,
            label="",
            xlabel=f"< <B>{label}</B> >",
            image=str(resources.files(__package__) / "assets" / "agent.svg"),
            imagescale=True,
            shape="circle",
            color="#164FAE",
            penwidth=20,
            fillcolor="#164FAE",
            labelloc="b",
            style="rounded,filled",
            regular=True,
            width=1.2,
            fixedsize=True,
        )


class BasicNode(pydot.Node):
    def __init__(self, name: str, label: str):
        super().__init__(
            name,
            label="",
            xlabel=f"< <B>{label}</B> >",
            image=str(resources.files(__package__) / "assets" / "basic.svg"),
            imagescale=True,
            fixedsize=True,
            shape="diamond",
            color="none",
            fillcolor="#039A93",
            labelloc="b",
            style="rounded,filled",
            regular=True,
            width=1.2,
        )


class ToolNode(pydot.Node):
    def __init__(self, name: str, label: str, tool_type: Optional[ToolType] = None):
        ttype = str(tool_type or ToolType.DEFAULT)
        super().__init__(
            name,
            label="",
            xlabel=f"< <B>{label}</B><BR/>{ttype} >",
            image=str(
                resources.files(__package__) / "assets" / "tools" / f"{ttype}.svg"
            ),
            imagescale=True,
            fixedsize=True,
            shape="box",
            color="none",
            fillcolor="#A937D6",
            style="rounded,filled",
            labelloc="b",
            regular=True,
            width=1,
        )


class CustomToolNode(pydot.Node):
    def __init__(self, name: str, label: str):
        super().__init__(
            name,
            label="",
            xlabel=f"< <B>{label}</B> >",
            image=str(resources.files(__package__) / "assets" / "custom_tool.svg"),
            imagescale=True,
            shape="box",
            color="#A937D6",
            fillcolor="#F7DEFC",
            style="rounded,filled,dashed",
            labelloc="b",
            regular=True,
            width=1,
            fixedsize=True,
        )
