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

<img src="https://github.com/splx-ai/agentic-radar/raw/main/docs/overview_image.png"/>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#description">Description</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#demo">Demo</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#code-of-conduct">Code Of Conduct</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

## Description 📝

The **Agentic Radar** is designed to analyze and assess agentic systems for security and operational insights. It helps developers, researchers, and security professionals understand how agentic systems function and identify potential vulnerabilities.

It allows users to create a security report for agentic systems, including:
1. **Workflow Visualization** - a graph of the agentic system's workflow✅
2. **Tool Identification** - a list of all external and custom tools utilized by the system✅
3. **Vulnerability Mapping** - a table connecting identified tools to known vulnerabilities, providing a security overview✅

The comprehensive HTML report summarizes all findings and allows for easy reviewing and sharing.

**Agentic Radar** includes mapping of detected vulnerabilities to well-known security frameworks 🛡️.
+ [OWASP Top 10 LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

+ [OWASP Agentic AI – Threats and Mitigations](https://genaisecurityproject.com/resource/agentic-ai-threats-and-mitigations)

**Why Use It?** 🔎

Agentic systems have complex workflows and often interact with multiple tools, making transparency and security assessment challenging. This tool simplifies the process by offering a structured view of workflows, tools, and potential risks.


**Detailed Report**

<p align="center">
  <img src="https://github.com/splx-ai/agentic-radar/raw/main/docs/report_part1.png" width="390" height="650" style="margin-right: 50px;" >  
  <img src="https://github.com/splx-ai/agentic-radar/raw/main/docs/report_part2.png" width="390" height="650"/>
</p>

## Getting Started 🚀

### Prerequisites

Agentic Radar uses graphviz and cairo for dependency graph visualization.

- graphviz
```sh
# homebrew
brew install graphviz

# linux
apt-get install graphviz
```

- cairo
```sh
# homebrew
brew install cairo

# linux
apt-get install libcairo
```

### Installation
```sh
pip install agentic-radar

# Check that it is installed
agentic-radar --version
```

## Usage

Run `agentic-radar --help` for more info:
```
Usage: agentic-radar [OPTIONS] COMMAND [ARGS]...

Options:
  -i, --input-dir TEXT            Path to the directory where all the code is
                                  [env var: AGENTIC_RADAR_INPUT_DIRECTORY;
                                  default: .]
  -o, --output-file TEXT          Where should the output report be stored
                                  [env var: AGENTIC_RADAR_OUTPUT_FILE;
                                  default: report_20250311_122338.html]
  --version
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  langgraph  Scan code written with LangGraph
  crewai     Scan code written with CrewAI
```


## Roadmap 📈

Planned features (in no particular order)

- [ ] Framework Support
  - [x] [LangGraph](https://github.com/langchain-ai/langgraph)
  - [x] [CrewAI](https://github.com/crewAIInc/crewAI)
  - [x] [n8n](https://github.com/n8n-io/n8n)
  - [ ] [LlamaIndex](https://github.com/run-llama/llama_index)
  - [ ] [Swarm](https://github.com/openai/swarm)
  - [ ] [PydanticAI](https://github.com/pydantic/pydantic-ai)
  - [ ] [AutoGen](https://github.com/microsoft/autogen)
  - [ ] [Dify](https://github.com/langgenius/dify)
- [ ] CI
  - [ ] Code style checks
  - [ ] Automated releases to PyPi
- [ ] Improve report design
  - [ ] Improve SVG scaling

## Demo 🎥

<img src="https://github.com/splx-ai/agentic-radar/raw/main/docs/demo.gif"/>

<br>

**[Demo Google Colab Notebook](https://colab.research.google.com/drive/1AAN23QAMsm0C7KGRmSSw7G2WFatzIa46?usp=sharing) 📘**

Designed for AI engineers and security researchers, this demo showcases how to integrate **Agentic Radar** into your development workflow. ⚙️ 

It helps you understand agentic system behavior, visualize security risks, and enhance AI transparency in your applications. 🚀


## Community 🤝

We welcome contributions from the AI and security community! Join our [Discord community](https://discord.gg/QZQpef5PsD) to connect with other developers, discuss features, get support and contribute to **Agentic Radar** 🚀

If you like what you see, give us a star! It keeps us inspired to improve and innovate and helps others discover the project 🌟

## Frequently Asked Questions ❓

**Q: Is my source code being shared or is everything running locally?**  
A: Everything is running locally. Your source code is never uploaded anywhere.

## Contributing 💻 

[CONTRIBUTING](CONTRIBUTING.md)

## Code Of Conduct 📜
[CODE OF CONDUCT](CODE_OF_CONDUCT.md)

## License ⚖️

[LICENSE](LICENSE)
