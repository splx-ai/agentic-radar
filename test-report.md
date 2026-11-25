# Unknown (error while mapping name) Tests
| Category | Test Description | Status | Link |
|----------|------------------|--------|------|
| core | to_json output must be parseable by json.loads. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L49) |
|  | Serialized array length equals number of TestResult objects. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L55) |
|  | Every TestResult field appears verbatim in the JSON output. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L61) |
|  | Output should contain newlines (i.e. not be a single-line dump). | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L75) |
|  | Empty list produces a valid empty JSON array. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L80) |
|  |  | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L92) |
|  | Markdown report must include the top-level heading. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L96) |
|  | Summary section must reflect correct passed/failed counts. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L101) |
|  | Each agent name from the results must appear in the Markdown. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L108) |
|  | Each test name from the results must appear in the Markdown. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L114) |
|  | Passed results should be marked with PASSED. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L120) |
|  | Failed results should be marked with FAILED. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L125) |
|  | Detailed results table header row must be present. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L130) |
|  | Pipe characters inside explanations are escaped so the table stays valid. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L139) |
|  | Empty result list still produces a valid Markdown report with zeros. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L153) |
|  | write_results creates a readable JSON file at the target path. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L167) |
|  | write_results creates a readable Markdown file at the target path. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L175) |
|  | write_results must create missing parent directories automatically. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L183) |
|  | Passing an unknown format should raise ValueError. | Unknown | [link](tests/unit_tests/exporters/core/test_exporters.py#L189) |
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
