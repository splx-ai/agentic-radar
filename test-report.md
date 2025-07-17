# LangGraph Tests
| Category | Test Description | Status | Link |
|----------|------------------|--------|------|
| edges |     Positional arguments in "add_edge".     | Passed✅ | [link](tests/unit_tests/langgraph/edges/test_explicit_edges.py#L6) |
|  |     Keyword arguments in "add_edge".     | Passed✅ | [link](tests/unit_tests/langgraph/edges/test_explicit_edges.py#L49) |
|  |     Keyword arguments in "add_conditional_edges". Routing function not imported.     | Passed✅ | [link](tests/unit_tests/langgraph/edges/test_explicit_edges.py#L91) |
|  |     Keyword arguments in "add_conditional_edges". Routing function imported.     | Passed✅ | [link](tests/unit_tests/langgraph/edges/test_explicit_edges.py#L151) |
|  |     Positional arguments in "add_conditional_edges". Routing function not imported.     | Passed✅ | [link](tests/unit_tests/langgraph/edges/test_explicit_edges.py#L219) |
|  |     Positional arguments in "add_conditional_edges". Routing function imported.     | Passed✅ | [link](tests/unit_tests/langgraph/edges/test_explicit_edges.py#L279) |
|  |     Keyword arguments in "add_conditional_edges". Path mapping not imported.     | Passed✅ | [link](tests/unit_tests/langgraph/edges/test_explicit_edges.py#L347) |
|  |     Keyword arguments in "add_conditional_edges". Path mapping imported.     | Passed✅ | [link](tests/unit_tests/langgraph/edges/test_explicit_edges.py#L412) |
|  |     Positional arguments in "add_conditional_edges". Path mapping not imported.     | Passed✅ | [link](tests/unit_tests/langgraph/edges/test_explicit_edges.py#L484) |
|  |     Positional arguments in "add_conditional_edges". Path mapping imported.     | Passed✅ | [link](tests/unit_tests/langgraph/edges/test_explicit_edges.py#L549) |
|  |     Implicitly defined by a single-value "goto" argument in a single Command object.     | Passed✅ | [link](tests/unit_tests/langgraph/edges/test_implicit_edges.py#L6) |
|  |     Implicitly defined by a list "goto" argument in a single Command object. (Conditional)     | Passed✅ | [link](tests/unit_tests/langgraph/edges/test_implicit_edges.py#L51) |
|  |     Implicitly defined by a multi-value "goto" argument in a single Command object. (Conditional)     | Passed✅ | [link](tests/unit_tests/langgraph/edges/test_implicit_edges.py#L103) |
|  |     Implicitly defined by single-value "goto" arguments in a multiple Command object. (Conditional)     | Passed✅ | [link](tests/unit_tests/langgraph/edges/test_implicit_edges.py#L159) |
| nodes |     Test that the analyzer correctly identifies agent nodes in a minimal LangGraph setup.     | Passed✅ | [link](tests/unit_tests/langgraph/nodes/test_agents.py#L7) |
|  |     The name of the node and node function in "add_node".     | Passed✅ | [link](tests/unit_tests/langgraph/nodes/test_nodes.py#L6) |
|  |     Only the name of the node function in "add_node".     | Passed✅ | [link](tests/unit_tests/langgraph/nodes/test_nodes.py#L42) |
|  |     The name of the node and a function call in "add_node".     | Passed✅ | [link](tests/unit_tests/langgraph/nodes/test_nodes.py#L79) |
| tools |     Custom tools defined with the @tool decorator.     | Passed✅ | [link](tests/unit_tests/langgraph/tools/test_tools.py#L7) |
|  |     Imported predefined tools.     | Passed✅ | [link](tests/unit_tests/langgraph/tools/test_tools.py#L32) |
