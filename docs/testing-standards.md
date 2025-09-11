# Testing Standards for Agentic Radar

This document establishes the testing standards for Agentic Radar, a Python project that generates interactive HTML reports with JavaScript visualization components.

## Problem Statement

Agentic Radar generates HTML reports containing interactive JavaScript visualizations using libraries like vis-network and ForceGraph. This creates a testing challenge:

- **Python code** generates HTML templates and embeds data
- **JavaScript code** runs in the browser to create interactive visualizations
- **User interactions** (layout switching, parameter controls) modify the visualizations dynamically

Traditional Python unit tests can verify HTML generation but cannot test the JavaScript functionality that users actually interact with.

## Testing Strategy: Tiered Approach

Based on research of similar open source projects (Plotly, Bokeh, Dash, Jupyter), we adopt a **tiered testing strategy**:

### Tier 1: Python Unit Tests (Required)
Test the Python code that generates HTML reports.

**Scope:**
- HTML template rendering
- Data serialization and embedding
- CLI flag behavior
- Report structure and content

**Tools:** pytest (existing)

**Examples:**
```python
def test_graph_only_generates_minimal_html(tmp_path):
    # Test HTML structure is correct
    
def test_system_prompts_section_appears_in_report(tmp_path):
    # Test template includes expected sections
```

**Status:** ✅ Already implemented and comprehensive

### Tier 2: Browser Integration Tests (Optional)
Test critical JavaScript functionality and user interactions.

**Scope:**
- Graph rendering and display
- Layout switching (force, hierarchical, circular)
- Parameter controls (sliders, dropdowns)
- Panel collapse/expand functionality
- Basic interactivity verification

**Tools:** pytest-playwright (recommended) or pytest-selenium

**Examples:**
```python
@pytest.mark.browser
def test_graph_renders_successfully(page):
    page.goto(f"file://{report_path}")
    page.wait_for_selector("#graph")
    # Verify graph container exists and has content

@pytest.mark.browser  
def test_layout_switching_works(page):
    page.goto(f"file://{report_path}")
    page.select_option("#layoutSelect", "hierarchical")
    # Verify layout change takes effect
```

**Status:** 🚧 To be implemented

### Tier 3: Manual/Visual Testing (As Needed)
Complex UI behaviors, visual appearance, cross-browser compatibility.

**Scope:**
- Visual regression testing
- Performance under different data loads
- Cross-browser compatibility
- Accessibility compliance

**Tools:** Manual testing, optional screenshot comparison

## Implementation Guidelines

### Browser Testing Setup

1. **Add pytest-playwright dependency:**
```bash
pip install pytest-playwright
playwright install
```

2. **Use pytest markers to separate test types:**
```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
markers = [
    "browser: marks tests as browser-based (deselect with '-m \"not browser\"')"
]
```

3. **Make browser tests optional:**
```bash
# Run all tests
pytest

# Skip browser tests (for faster development)
pytest -m "not browser"

# Run only browser tests
pytest -m browser
```

### Test Organization

```
tests/
├── unit_tests/           # Tier 1: Python unit tests
│   ├── test_analysis/
│   ├── test_report/
│   └── test_cli/
├── browser_tests/        # Tier 2: Browser integration tests  
│   ├── test_graph_rendering.py
│   ├── test_layout_switching.py
│   └── test_interactivity.py
└── cli_test.py          # Existing CLI tests
```

### CI/CD Integration

- **Unit tests:** Required for all PRs, must pass
- **Browser tests:** Optional, run in CI but don't block PRs if they fail
- **Documentation:** Include browser test results in PR comments when available

### Development Workflow

1. **For Python changes:** Run unit tests (`pytest -m "not browser"`)
2. **For HTML/JS changes:** Run browser tests (`pytest -m browser`)
3. **Before release:** Run full test suite (`pytest`)

## Why pytest-playwright over alternatives?

Based on 2024 ecosystem research:

**pytest-playwright advantages:**
- Faster and more reliable than Selenium
- Built-in video recording and screenshots for debugging
- Better debugging tools (trace viewer, inspector)
- Modern async architecture
- Official Microsoft support

**vs. Node.js/Puppeteer:**
- Keeps everything in Python ecosystem
- Better integration with existing pytest infrastructure
- No additional package managers (npm) required

**vs. No browser testing:**
- Catches real user-facing issues
- Validates JavaScript functionality actually works
- Provides confidence in interactive features

## Best Practices

### Writing Browser Tests

1. **Test user journeys, not implementation details**
2. **Use page object pattern for complex interactions**
3. **Include meaningful assertions:**
   ```python
   # Good: Test user-visible behavior
   assert page.locator("#layoutPanel").is_visible()
   
   # Better: Test functional outcome
   page.select_option("#layoutSelect", "hierarchical")
   assert page.locator("#hierarchicalParams").is_visible()
   ```

4. **Handle timing appropriately:**
   ```python
   # Wait for dynamic content
   page.wait_for_selector("#graph canvas")
   
   # Wait for animations to complete
   page.wait_for_timeout(500)
   ```

5. **Use descriptive test names:**
   ```python
   def test_switching_to_hierarchical_layout_shows_direction_controls():
   def test_collapsing_panel_hides_all_parameter_controls():
   ```

### Debugging Failed Tests

1. **Use built-in debugging features:**
   ```python
   # Add to failing test for debugging
   page.pause()  # Opens browser for manual inspection
   ```

2. **Capture screenshots on failure:**
   ```python
   # Automatic with pytest-playwright
   # Screenshots saved to test-results/
   ```

3. **Use trace viewer for complex failures:**
   ```bash
   pytest --tracing=on
   # View traces with: playwright show-trace trace.zip
   ```

## Migration Path

### Phase 1: Setup Infrastructure
- Add pytest-playwright dependency
- Configure test markers and organization
- Create basic browser test examples

### Phase 2: Critical Path Coverage
- Test graph rendering works
- Test layout switching functionality
- Test basic parameter controls

### Phase 3: Comprehensive Coverage
- Test edge cases and error conditions
- Add visual regression testing
- Optimize test performance and reliability

## Success Metrics

- **Unit test coverage:** Maintain >90% for Python code
- **Browser test reliability:** >95% pass rate in CI
- **Development velocity:** Browser tests don't slow down development
- **Bug prevention:** Catch JavaScript regressions before release

---

*This document should be updated as testing practices evolve and new requirements emerge.*