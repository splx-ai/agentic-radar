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
