# Changelog

## [0.14.1](https://github.com/splx-ai/agentic-radar/compare/v0.14.0...v0.14.1) (2025-11-27)


### Bug Fixes

* **openai-agents:** prevent duplicate tool nodes in graph definition ([#118](https://github.com/splx-ai/agentic-radar/issues/118)) ([eb3184d](https://github.com/splx-ai/agentic-radar/commit/eb3184d5a3fa7f65b9a7e03035ca716a501d04a9))
* update vulnerable dependencies ([#120](https://github.com/splx-ai/agentic-radar/issues/120)) ([fc6788e](https://github.com/splx-ai/agentic-radar/commit/fc6788ef18711510a88bb5f9b9e783b8b07250a1))

## [0.14.0](https://github.com/splx-ai/agentic-radar/compare/v0.13.0...v0.14.0) (2025-10-08)


### Features

* **autogen:** add mcp detection for autogen agentchat ([#111](https://github.com/splx-ai/agentic-radar/issues/111)) ([902a4cd](https://github.com/splx-ai/agentic-radar/commit/902a4cd2736d05b799df8719fd86c475b7d318df))
* **crewai:** add support for crewai mcp server detection ([#112](https://github.com/splx-ai/agentic-radar/issues/112)) ([9e1f302](https://github.com/splx-ai/agentic-radar/commit/9e1f302fb510b811aada992b8855c0cd3b24c484))
* **n8n:** add mcp detection in n8n ([#114](https://github.com/splx-ai/agentic-radar/issues/114)) ([f3e7035](https://github.com/splx-ai/agentic-radar/commit/f3e7035b7abbed53fdd7ac8f6ce0e74237fce579))


### Bug Fixes

* **openai-agents:** improve mcp detection coverage ([#113](https://github.com/splx-ai/agentic-radar/issues/113)) ([036ed80](https://github.com/splx-ai/agentic-radar/commit/036ed80fc963434c6785c5d096e8de8e9b428d29))

## [0.13.0](https://github.com/splx-ai/agentic-radar/compare/v0.12.0...v0.13.0) (2025-07-17)


### Features

* add GitHub workflow example YAML ([#101](https://github.com/splx-ai/agentic-radar/issues/101)) ([e3be24f](https://github.com/splx-ai/agentic-radar/commit/e3be24fa9f9df0ce55d57e21815d521347a6de5b))


### Bug Fixes

* **autogen:** show teamless agents in the report ([#103](https://github.com/splx-ai/agentic-radar/issues/103)) ([22d79bf](https://github.com/splx-ai/agentic-radar/commit/22d79bf1fd26e1d27e1b9b6e6c60f5568f3e6658))

## [0.12.0](https://github.com/splx-ai/agentic-radar/compare/v0.11.1...v0.12.0) (2025-06-09)


### Features

* Export Graph as JSON ([#99](https://github.com/splx-ai/agentic-radar/issues/99)) ([30f6c89](https://github.com/splx-ai/agentic-radar/commit/30f6c89ad86340c4d825cd9f193046ebc82badae))

## [0.11.1](https://github.com/splx-ai/agentic-radar/compare/v0.11.0...v0.11.1) (2025-06-03)


### Bug Fixes

* set font color in report tables to black ([#96](https://github.com/splx-ai/agentic-radar/issues/96)) ([a81c92b](https://github.com/splx-ai/agentic-radar/commit/a81c92b3188fc5644a589eb7d722e0bc123cd8a6))

## [0.11.0](https://github.com/splx-ai/agentic-radar/compare/v0.10.1...v0.11.0) (2025-06-03)


### Features

* Autogen AgentChat scan support ([#95](https://github.com/splx-ai/agentic-radar/issues/95)) ([13edf17](https://github.com/splx-ai/agentic-radar/commit/13edf17ff90c24e8887e014b4419f25a296f5d0f))
* **langgraph:** implement simple heuristic for detecting agents ([#92](https://github.com/splx-ai/agentic-radar/issues/92)) ([aa4e86a](https://github.com/splx-ai/agentic-radar/commit/aa4e86aaa9294feb4d8a7a1f482473a785655ed0))

## [0.10.1](https://github.com/splx-ai/agentic-radar/compare/v0.10.0...v0.10.1) (2025-05-23)


### Bug Fixes

* missing dependencies regarding pyyaml and openai-agents ([#90](https://github.com/splx-ai/agentic-radar/issues/90)) ([16e3f5b](https://github.com/splx-ai/agentic-radar/commit/16e3f5b35b743569a02143ab8339094255bcd884))

## [0.10.0](https://github.com/splx-ai/agentic-radar/compare/v0.9.1...v0.10.0) (2025-05-12)


### Features

* add initial commit for MCP support in LangGraph ([#78](https://github.com/splx-ai/agentic-radar/issues/78)) ([5573d83](https://github.com/splx-ai/agentic-radar/commit/5573d834fcaa5f7c3b68f5ba58c8b0e36540eead))
* **prompt-hardening:** add pii protection step ([#85](https://github.com/splx-ai/agentic-radar/issues/85)) ([574c859](https://github.com/splx-ai/agentic-radar/commit/574c8596bc86830dc546f7d69003b3c7395f2821))
* **radar-test:** add optional config to tests ([#83](https://github.com/splx-ai/agentic-radar/issues/83)) ([2d3c61e](https://github.com/splx-ai/agentic-radar/commit/2d3c61ebdcc94ad9870e00b8145ff00ad1fcd2bc))
* rename probe to test ([#80](https://github.com/splx-ai/agentic-radar/issues/80)) ([153a418](https://github.com/splx-ai/agentic-radar/commit/153a4180c8073f0020c73174408bdd1bec767bdb))
* rename prompt enhancement to prompt hardening ([#84](https://github.com/splx-ai/agentic-radar/issues/84)) ([fcb941f](https://github.com/splx-ai/agentic-radar/commit/fcb941f44a31e9eed008f060d067cd0ecd3778f9))

## [0.9.1](https://github.com/splx-ai/agentic-radar/compare/v0.9.0...v0.9.1) (2025-04-26)


### Features

* **bump:** Temp add openai-agents dependency ([#76](https://github.com/splx-ai/agentic-radar/issues/76)) ([fc5cac2](https://github.com/splx-ai/agentic-radar/commit/fc5cac2a2cdc32ccb6fa5d6f53941a946efb17f7))

## [0.9.0](https://github.com/splx-ai/agentic-radar/compare/v0.8.0...v0.9.0) (2025-04-26)


### Features

* **bump:** Release 0.8.1 ([#74](https://github.com/splx-ai/agentic-radar/issues/74)) ([e6c538f](https://github.com/splx-ai/agentic-radar/commit/e6c538fea22067961e870c17f7bb0858362c870f))

## [0.8.0](https://github.com/splx-ai/agentic-radar/compare/v0.7.0...v0.8.0) (2025-04-26)


### Features

* **agent-vulnerability:** OpenAI Agents Improvements ([95bb67f](https://github.com/splx-ai/agentic-radar/commit/95bb67f0b4c7844c2d82985aa2ad67cca59d3c82))
* **probe:** Init Agentic Probe ([2e72045](https://github.com/splx-ai/agentic-radar/commit/2e72045703edae9cd97cf3b092a4599680901ad5))

## [0.7.0](https://github.com/splx-ai/agentic-radar/compare/v0.6.0...v0.7.0) (2025-04-23)


### Features

* adds initial unit tests for the LangGraph framework ([23dd317](https://github.com/splx-ai/agentic-radar/commit/23dd317fc0798dc5378f9fd99b23cd1d0438e4e8))
* **crewai:** add additional agent information to report ([#64](https://github.com/splx-ai/agentic-radar/issues/64)) ([2e4e2b2](https://github.com/splx-ai/agentic-radar/commit/2e4e2b29fa55c9bcae7a29c557d0c595aa27b554))
* **openai-agents:** add additional agent information to report ([#66](https://github.com/splx-ai/agentic-radar/issues/66)) ([0c880ab](https://github.com/splx-ai/agentic-radar/commit/0c880ab4179d8653504bde4f391c236da8f738c6))
* **openai-agents:** detection of MCP servers ([#68](https://github.com/splx-ai/agentic-radar/issues/68)) ([42a64b6](https://github.com/splx-ai/agentic-radar/commit/42a64b6fb8ce36adf6f1cb151cb25725670d92b0))
* Prompt Enhancement ([#67](https://github.com/splx-ai/agentic-radar/issues/67)) ([39b45e4](https://github.com/splx-ai/agentic-radar/commit/39b45e4d13e1c272e4c59f176580fa4ab4e7f358))

## [0.6.0](https://github.com/splx-ai/agentic-radar/compare/v0.5.1...v0.6.0) (2025-03-28)


### Features

* add OpenAI Agents framework analyzer ([6d20adb](https://github.com/splx-ai/agentic-radar/commit/6d20adb95a34d4738a462ead5002dafedf2a5281))
