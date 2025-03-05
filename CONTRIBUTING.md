# Contributing

If you want to submit a Pull Request, please read this document carefully, as it contains information guiding you through our PR process.

For guidance with submitting a PR or have any other question regarding the Agentic Scanner, join our Discord or Slack and get in touch with us through the dev channels.

## Prerequisites

When you want to add some code to the Agentic Scanner repository, first make sure that an issue or a bug exists in our issue tracker **and** the issue is marked as `help needed` **and** no-one has claimed it. This ensures that we don't duplicate work and invest our efforts in meaningful (and doable) tasks.

### Local development setup

You will need the following things for developing the Agentic Scanner:
- `graphviz` and `cairo`. These are necessary for the dependency chart visualization. Installation instructions can be found on https://www.cairographics.org/download/ and https://graphviz.org/download/.
- `python` (3.9+)
- `poetry` (2.0+)
- `git`. (v2.0.0+)

### Fork and clone the repository

1. For the Agentic Scanner repository to your personal Github account
2. Clone the forked repository:
```sh
git clone git@github.com:YOUR-USERNAME/agentic-scanner.git
```
3. Add the upstream remote for rebasing:
```sh
cd agentic-scanner
git remote add upstream git@github.com:splx-ai/agentic-scanner.git
```

### Development

Install all dependencies with:
```sh
poetry install

# Activate the virtual environment
source .venv/bin/activate # We recommend to configure poetry so it stores the virtual environment in the project repository
```

You can run the current development version with:
```sh
python agentic_scanner/cli.py --help
```

When writing the code, please use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/#summary). This enables automated versioning and utilizes a common practice for writing commit messages.

### Submitting a PR

Before submitting a PR make sure that your branch is rebased against the upstream main:
```sh
git fetch upstream
git rebase upstream/main
```

Additionaly, run the pre-commit checks with:
```sh
pre-commit run --all-files
```
