# Framework Coverage Report
## Summary
- Total tests: 19
- Total supported tests: 19
- Passed ✅: 19
- Failed ❌: 0

## Tests
- **langgraph**
  - **edges**
    - **explicit_edges**
      - [add_edge_positional_arguments](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/edges/test_explicit_edges.py#L4) ✅
      - [add_edge_keyword_arguments](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/edges/test_explicit_edges.py#L44) ✅
      - [add_conditional_edges_keyword_arguments_without_map_local](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/edges/test_explicit_edges.py#L83) ✅
      - [add_conditional_edges_keyword_arguments_without_map_imported](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/edges/test_explicit_edges.py#L140) ✅
      - [add_conditional_edges_positional_arguments_without_map_local](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/edges/test_explicit_edges.py#L205) ✅
      - [add_conditional_edges_positional_arguments_without_map_imported](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/edges/test_explicit_edges.py#L262) ✅
      - [add_conditional_edges_keyword_arguments_with_map_local](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/edges/test_explicit_edges.py#L327) ✅
      - [add_conditional_edges_keyword_arguments_with_map_imported](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/edges/test_explicit_edges.py#L389) ✅
      - [add_conditional_edges_positional_arguments_with_map_local](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/edges/test_explicit_edges.py#L458) ✅
      - [add_conditional_edges_positional_arguments_with_map_imported](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/edges/test_explicit_edges.py#L520) ✅
    - **implicit_edges**
      - [add_node_with_Command_objects_single_return_single_value](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/edges/test_implicit_edges.py#L4) ✅
      - [add_node_with_Command_objects_single_return_multiple_values_list](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/edges/test_implicit_edges.py#L46) ✅
      - [add_node_with_Command_objects_single_return_multiple_values_conditional](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/edges/test_implicit_edges.py#L95) ✅
      - [add_node_with_Command_objects_multiple_returns_multiple_values_conditional](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/edges/test_implicit_edges.py#L148) ✅
  - **nodes**
    - **nodes**
      - [add_node_with_name_and_with_function_name](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/nodes/test_nodes.py#L4) ✅
      - [add_node_without_name_and_with_function_name](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/nodes/test_nodes.py#L37) ✅
      - [add_node_with_name_and_with_function_call](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/nodes/test_nodes.py#L71) ✅
  - **tools**
    - **tools**
      - [custom_tools](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/tools/test_tools.py#L5) ✅
      - [predefined_tools](https://github.com/splx-ai/agentic-radar/blob/e2ae815f23451a3823a50fa397f2aba8ea6b97aa/tests/unit_tests/langgraph/tools/test_tools.py#L28) ✅