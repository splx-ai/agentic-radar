import os
import re

import jinja2

from .graph import (
    GraphDefinition,
    from_definition,
)


def generate(graph: GraphDefinition, out_file: str):
    svg = from_definition(graph).generate()

    # remove xml definition, and put relative width and height
    svg_lines = svg.splitlines()[1:]
    svg_lines[0] = re.sub(r'width="(.*?)"', 'width="100%"', svg_lines[0])
    svg_lines[0] = re.sub(r'height="(.*?)"', 'height="100%"', svg_lines[0])
    svg = "\n".join(svg_lines)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), "templates")
        )
    )

    template = env.get_template("template.html.jinja")

    template.stream(graph=svg).dump(out_file)
