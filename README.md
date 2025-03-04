<div align="center">


  <a href="https://splx.ai"><img src="docs/logo.svg" alt="logo" width="200" height="auto" /></a>
  <h1>Agentic Radar</h1>
  
  <p>
    A Security Scanner for your agentic workflows!
  </p>
  
  
<!-- Badges -->
<p>
  <a href="https://github.com/splx-ai/agentic-scanner/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/splx-ai/agentic-scanner" alt="contributors" />
  </a>
  <a href="">
    <img src="https://img.shields.io/github/last-commit/splx-ai/agentic-scanner" alt="last update" />
  </a>
  <a href="https://github.com/splx-ai/agentic-scanner/network/members">
    <img src="https://img.shields.io/github/forks/splx-ai/agentic-scanner" alt="forks" />
  </a>
  <a href="https://github.com/splx-ai/agentic-scanner/stargazers">
    <img src="https://img.shields.io/github/stars/splx-ai/agentic-scanner" alt="stars" />
  </a>
  <a href="https://github.com/splx-ai/agentic-scanner/issues/">
    <img src="https://img.shields.io/github/issues/splx-ai/agentic-scanner" alt="open issues" />
  </a>
  <a href="https://github.com/splx-ai/agentic-scanner/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/splx-ai/agentic-scanner.svg" alt="license" />
  </a>
</p>
   
  <h4>
    <a href="https://github.com/splx-ai/agentic-scanner/">View Demo</a>
  <span> · </span>
    <a href="https://github.com/splx-ai/agentic-scanner">Documentation</a>
  <span> · </span>
    <a href="https://github.com/splx-ai/agentic-scanner/issues/">Report Bug</a>
  <span> · </span>
    <a href="https://github.com/splx-ai/agentic-scanner/issues/">Request Feature</a>
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

Agentic Scanner uses graphviz and cairo for dependency graph visualization.

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
pip install agentic-scanner

# Check that it is installed
agentic-scanner --version
```

## Usage

Run `agentic-scanner --help` for more info:
```
Usage: agentic-scanner [OPTIONS] COMMAND [ARGS]...

Options:
  -i, --input-dir TEXT            Path to the directory where all the code is
                                  [env var: AGENTIC_SCANNER_INPUT_DIRECTORY;
                                  default: .]
  -o, --output-file TEXT          Where should the output report be stored
                                  [env var: AGENTIC_SCANNER_OUTPUT_FILE;
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


## Roadman


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
