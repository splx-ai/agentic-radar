<div align="center">


  <a href="https://splx.ai">
    <img src="https://github.com/splx-ai/agentic-radar/raw/main/docs/logo.png" alt="logo" width="600" height="auto" />
  </a>
  
  <p>
    A Security Scanner for your agentic workflows!
  </p>
  
  
<!-- Badges -->
<p>
  <a href="https://github.com/splx-ai/agentic-radar/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/splx-ai/agentic-radar" alt="contributors" />
  </a>
  <a href="">
    <img src="https://img.shields.io/github/last-commit/splx-ai/agentic-radar" alt="last update" />
  </a>
  <a href="https://github.com/splx-ai/agentic-radar/network/members">
    <img src="https://img.shields.io/github/forks/splx-ai/agentic-radar" alt="forks" />
  </a>
  <a href="https://github.com/splx-ai/agentic-radar/stargazers">
    <img src="https://img.shields.io/github/stars/splx-ai/agentic-radar" alt="stars" />
  </a>
  <a href="https://github.com/splx-ai/agentic-radar/issues/">
    <img src="https://img.shields.io/github/issues/splx-ai/agentic-radar" alt="open issues" />
  </a>
  <a href="https://github.com/splx-ai/agentic-radar/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/splx-ai/agentic-radar.svg" alt="license" />
  </a>
  <a href="https://pypi.org/project/agentic-radar">
    <img src="https://img.shields.io/pypi/v/agentic-radar" alt="PyPI - Version" />
  </a>
  <a href="https://pypi.org/project/agentic-radar">
    <img src="https://static.pepy.tech/badge/agentic-radar" alt="PyPI - Downloads" />
  </a>
  <br />
  <a href="https://discord.gg/tR2d54utZc">
    <img src="https://img.shields.io/discord/1346578514177949767?style=for-the-badge&logo=discord&logoColor=white&label=Discord&labelColor=5865F2&color=555555" alt="Discord" />
  </a>
  <a href="https://join.slack.com/t/splxaicommunity/shared_invite/zt-31b3hc3mt-A0v78qztTIMSNBg6y~WOAA">
    <img src="https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white" alt="Slack" />
  </a>
</p>
   
  <h4>
    <a href="https://github.com/splx-ai/agentic-radar/">View Demo</a>
  <span> · </span>
    <a href="https://github.com/splx-ai/agentic-radar">Documentation</a>
  <span> · </span>
    <a href="https://github.com/splx-ai/agentic-radar/issues/">Report Bug</a>
  <span> · </span>
    <a href="https://github.com/splx-ai/agentic-radar/issues/">Request Feature</a>
  </h4>
</div>

<img src="docs/overview_image.png"/>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#description-">Description</a>
    </li>
    <li>
      <a href="#getting-started-">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
      <li>
      <a href="#advanced-installation">Advanced Installation</a>
      <ul>
        <li><a href="#crewai-installation">CrewAI Installation</a></li>
        <li><a href="#openai-agents-installation">OpenAI Agents Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li>
      <a href="#advanced-features-">Advanced Features</a>
      <ul>
        <li><a href="#agentic-prompt-hardening">Agentic Prompt Hardening</a></li>
        <li><a href="#-test-for-vulnerabilities-in-agentic-workflows">Test for Vulnerabilities in Agentic Workflows</a></li>
      </ul>
    </li>
    <li><a href="#roadmap-">Roadmap</a></li>
    <li><a href="#blog-tutorials-">Blog Tutorials</a></li>
    <li><a href="#community-">Community</a></li>
    <li><a href="#frequently-asked-questions-">Frequently Asked Questions</a></li>
    <li><a href="#contributing-">Contributing</a></li>
    <li><a href="#code-of-conduct-">Code Of Conduct</a></li>
    <li><a href="#license-">License</a></li>
  </ol>
</details>

## Description 📝

The **Agentic Radar** is designed to analyze and assess agentic systems for security and operational insights. It helps developers, researchers, and security professionals understand how agentic systems function and identify potential vulnerabilities.

It allows users to create a security report for agentic systems, including:
1. **Workflow Visualization** - a graph of the agentic system's workflow✅
2. **Tool Identification** - a list of all external and custom tools utilized by the system✅
3. **MCP Server Detection** - a list of all MCP servers used by system's agents✅
4. **Vulnerability Mapping** - a table connecting identified tools to known vulnerabilities, providing a security overview✅

The comprehensive HTML report summarizes all findings and allows for easy reviewing and sharing.

**[View Full Report Example Here](https://agentic-radar.neocities.org/)**


**Agentic Radar** includes mapping of detected vulnerabilities to well-known security frameworks 🛡️.
+ [OWASP Top 10 LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

+ [OWASP Agentic AI – Threats and Mitigations](https://genaisecurityproject.com/resource/agentic-ai-threats-and-mitigations)

## Getting Started 🚀

### Prerequisites

There are none! Just make sure you have Python (pip) installed on your machine.

### Installation
```sh
pip install agentic-radar

# Check that it is installed
agentic-radar --version
```

Some features require extra installations, depending on the targeted agentic framework. See more [below](#advanced-installation).

## Advanced Installation
### CrewAI Installation

CrewAI extras are needed when using one of the following features in combination with CrewAI:

- [Agentic Radar Test](#-test-for-vulnerabilities-in-agentic-workflows)
- Descriptions for predefined tools

You can install Agentic Radar with extra CrewAI dependencies by running:
```sh
pip install "agentic-radar[crewai]"
```

> [!WARNING]
> This will install the `crewai-tools` package which is only supported on Python versions >= 3.10 and < 3.13.
> If you are using a different python version, the tool descriptions will be less detailed or entirely missing.

### OpenAI Agents Installation

OpenAI Agents extras are needed when using one of the following features in combination with OpenAI Agents:

- [Agentic Radar Test](#-test-for-vulnerabilities-in-agentic-workflows)

You can install Agentic Radar with extra OpenAI Agents dependencies by running:
```sh
pip install "agentic-radar[openai-agents]"
```

## Usage

Agentic Radar now supports two main commands:

### 1. `scan`
Scan code for agentic workflows and generate a report.

```sh
agentic-radar scan [OPTIONS] FRAMEWORK:{langgraph|crewai|n8n|openai-agents|autogen}
```

Example:
```sh
agentic-radar scan langgraph -i path/to/langgraph/example/folder -o report.html
```

---

### 2. `test`
Test agents in an agentic workflow for various vulnerabilities.
Requires OPENAI_API_KEY set as environment variable.

```sh
agentic-radar test [OPTIONS] FRAMEWORK:{openai-agents} ENTRYPOINT_SCRIPT_WITH_ARGS
```

Example:
```sh
agentic-radar test openai-agents "path/to/openai-agents/example.py"
```

See more about this feature [here](#-test-for-vulnerabilities-in-agentic-workflows).


## Advanced Features ✨

### Agentic Prompt Hardening

Agentic Prompt Hardening automatically improves detected system prompts in your agentic workflow and displays them in the report. It transforms simple agent instructions into high-quality structured system prompts which follow best prompt engineering practices.

> [!NOTE]  
> Currently supported frameworks (with more to come): OpenAI Agents, CrewAI, Autogen

It is quite straightforward to use:
1. Set your OPENAI_API_KEY environment variable by running `export OPENAI_API_KEY=<api_key>`.

2. Run Agentic Radar with the `--harden-prompts` flag, for example:
```sh
agentic-radar scan openai-agents --harden-prompts -i examples/openai-agents/
basic/lifecycle_example -o report.html
```

4. Inspect hardened system prompts in the generated report:
<img src="docs/prompt_hardening.png"/>

### 🔍 Test for Vulnerabilities in Agentic Workflows

Agentic Radar now supports testing your agent workflows at **runtime** to identify critical vulnerabilities through simulated adversarial inputs.

This includes automated testing for:
  - Prompt Injection
  - PII Leakage
  - Harmful Content Generation
  - Fake News Generation

Currently supported for:
- OpenAI Agents ✅ (more frameworks coming soon)

#### 🛠 How It Works

The test command launches your agentic workflow with a test suite designed to simulate malicious or adversarial inputs. These tests are designed based on real-world attack scenarios aligned with the OWASP LLM Top 10.

> [!NOTE]  
> This feature requires OPENAI_API_KEY or AZURE_OPENAI_API_KEY set as an environment variable. You can set it via command line or inside a .env file.

Test is run like:
```sh
agentic-radar test <framework> "<path/to/the/workflow/main.py any-necessary-args>"
```

For example:
```sh
agentic-radar test openai-agents "examples/openai-agents/basic/lifecycle_example.py"
```

The tool injects itself into the agentic workflow provided by user, detects necessary information and runs the prepared tests.

#### Configurable Tests

You can pass custom tests to Agentic Radar by creating a YAML file with the following structure:
```yaml
include_default_tests: false
tests:
   - name: TestA
     input: Mention A.
     success_condition: Attack succeeded if A is mentioned.

   - name: TestB
     input: Mention B.
     success_condition: Attack succeeded if B is mentioned.
```

`name` is the name of the test, `input` is the input text to be passed to the agent, and `success_condition` is a description of what constitutes a successful attack (it will be used by an oracle LLM to determine if the test passed or failed).

You can then run Agentic Radar test with the `--config` option pointing to your YAML file:
```sh
agentic-radar test openai-agents --config custom_tests.yaml "examples/openai-agents/basic/lifecycle_example.py"
```

By default, Agentic Radar will also include the built-in tests. You can disable them by setting `include_default_tests` to `false` in your YAML file.

#### 📊 Rich Test Results

All test results are printed in a visually rich table format directly in the terminal.
Each row shows:
  - Agent name
  - Type of test
  - Injected input
  - Agent output
  - ✅ Whether the test passed or failed
  - 🛑 A short explanation of the result

This makes it easy to spot vulnerabilities at a glance—especially in multi-agent systems.

  <img src="docs/test_results.png" alt="Test Results Example" />

## Roadmap 📈

This matrix shows which agentic frameworks support all the Agentic Radar features. With time we will strive towards covering all current frameworks with all existing features, as well as introducing new frameworks to the mix. 

| Feature       | Scan        | MCP Detection        | Prompt Hardening | Agentic Test
|----------------|-------------|-------------|-------------|-------------|
| OpenAI Agents  | ✅          | ✅          | ✅          |     ✅         |
| CrewAI         | ✅          | ❌         | ✅          |      ❌        |
| n8n            | ✅          | ❌          | ❌          |     ❌        |
| LangGraph      | ✅          | ✅          | ❌          |     ❌         |
| Autogen     | ✅          | ❌          | ✅          |     ❌         |

Are there some features you would like to see happen first? Vote anonymously [here](https://strawpoll.com/w4nWWMqqlnA) or [open a GitHub Issue](https://github.com/splx-ai/agentic-radar/issues/new/choose).

## Blog Tutorials 💡

- [CrewAI](https://splx.ai/blog/enhancing-ai-transparency-scanning-crewai-workflows-with-agentic-radar)
- [n8n](https://splx.ai/blog/scanning-n8n-workflows-with-agentic-radar)
- [OpenAI Agents](https://splx.ai/blog/openai-agents-sdk-transparent-workflows-with-agentic-radar)
- [MCP Server Detection](https://splx.ai/blog/agentic-radar-now-detects-mcp-servers-in-agentic-workflows)
- [Agentic Prompt Hardening](https://splx.ai/blog/agentic-radar-now-scans-and-hardens-system-prompts-in-agentic-workflows)

## Community 🤝

We welcome contributions from the AI and security community! Join our [Discord community](https://discord.gg/QZQpef5PsD) or [Slack community](https://join.slack.com/t/splxaicommunity/shared_invite/zt-31b3hc3mt-A0v78qztTIMSNBg6y~WOAA) to connect with other developers, discuss features, get support and contribute to **Agentic Radar** 🚀

If you like what you see, give us a star! It keeps us inspired to improve and innovate and helps others discover the project 🌟

## Frequently Asked Questions ❓

**Q: Is my source code being shared or is everything running locally?**  
A: The main features (static workflow analysis and vulnerability mapping) are run completely locally and therefore your code is not shared anywhere. For optional advanced features, LLM's might be used. Eg. when using [Prompt Hardening](#agentic-prompt-hardening), detected system prompts can get sent to LLM for analysis.

## Contributing 💻 

[CONTRIBUTING](CONTRIBUTING.md)

## Code Of Conduct 📜
[CODE OF CONDUCT](CODE_OF_CONDUCT.md)

## License ⚖️

[LICENSE](LICENSE)
