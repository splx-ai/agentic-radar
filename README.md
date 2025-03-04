<div align="center">


  <a href="https://splx.ai"><img src="docs/logo.svg" alt="logo" width="300" height="auto" /></a>
  
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
  <a href="https://github.com/splx-ai/agentic-radar/blob/master/LICENSE">
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

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#features">Features</a>
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
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## Features

Create an AI Security report for Agentic Systems, including:
- dependency graph of all components in the Agentic System
- list of custom and third party tools used
- common security issues found in the Agentic System


OVDJE METNI SLIKU REPORTA


## Getting Started

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
                                  default: report_20250226_122829.html]
  --version
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  langgraph  Run scan for code written with LangGraph
```


## Roadmap


## Demo

OVDJE METNI GIF KAKO SE KORISTI I KAKO IZGLEDA REPORT

## Contributing

[CONTRIBUTING](CONTRIBUTING.md)

## Code Of Conduct
[CODE OF CONDUCT](CODE_OF_CONDUCT.md)

## License

[LICENSE](LICENSE.md)

## Contact

blabla
