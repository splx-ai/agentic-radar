from typing import Optional

import pydot

from ..graph import ToolType

class AgentNode(pydot.Node):
    def __init__(self, name: str, label: str):
        # super().__init__(name + "_sg", color="none", bgcolor="none", label=label)

        super().__init__(
            name,
            # label=label,
            label="",
            xlabel=f"< <B>{label}</B> >",
            image="./assets/agent.svg",
            imagescale=True,
            shape="circle",
            color="#164FAE",
            # penwidth=20,
            fillcolor="#164FAE",
            labelloc="b",
            style="rounded,filled",
            regular=True,
            width=1.2,
            fixedsize=True,
        )

        # self.add_node(
        # pydot.Node(
        # name + "lbl",
        # label=label,
        # # label="",
        # shape="plaintext",
        # )
        # )

        # self.add_edge(pydot.Edge(name, name, label="<<table><tr><td>TT</td></tr></table>>", color="none", fontcolor="red", fontsize=20))
        # self.add_edge(pydot.Edge(name, name, label="dksjd", color="green"))
        # self.add_edge(pydot.Edge(name, name + "lbl", color="none", constraint=False, minlen=0, len=0.0001))


class BasicNode(pydot.Node):
    def __init__(self, name: str, label: str):
        super().__init__(
            name,
            # label=label,
            label="",
            xlabel=f"< <B>{label}</B> >",
            image="./assets/basic.svg",
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
        t = ''
        # TODO: depending on tool type, set different icon
        super().__init__(
            name,
            # label=label,
            label="",
            xlabel=f"< <B>{label}</B>"+"<BR/>"+str(tool_type or ToolType.DEFAULT) + " >",
            image="./assets/tool.svg",
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
            # label=label,
            label="",
            xlabel=f"< <B>{label}</B> >",
            image="./assets/custom_tool.svg",
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
