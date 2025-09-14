# Agentic Radar Development Timeline

This document provides a comprehensive view of the Agentic Radar project's development history and future roadmap.

## Project Overview
[Agentic Radar](https://github.com/splx-ai/agentic-radar) is a security scanner for agentic workflows, providing analysis, visualization, and vulnerability assessment for AI agent systems.

## Development Timeline

### Overall Project Timeline
```mermaid
gantt
    title Agentic Radar High Level Roadmap
    dateFormat YYYY-MM-DD
    axisFormat %Y-%m
    
    section Foundation
    Core Platform         :done, foundation, 2025-03-01, 2025-03-31
    
    section Framework Support
    Initial Frameworks     :done, frameworks-1, 2025-04-01, 2025-05-31
    Extended Frameworks    :active, frameworks-2, 2025-09-01, 2025-12-31
    
    section Visualization
    Basic Reports          :done, viz-1, 2025-04-01, 2025-08-31
    Enhanced Visualization :active, viz-2, 2025-09-01, 2025-12-31
    
    section Future
    Enterprise Features    :enterprise, 2026-01-01, 2026-12-31
```

### Completed Work (2025 Q1-Q2)
```mermaid
gantt
    title Foundation & Core Features (Completed)
    dateFormat YYYY-MM-DD
    axisFormat %Y-%m
    
    section Q1 Foundation
    Initial Release           :done, foundation, 2025-03-05, 2025-03-15
    LangGraph Support (#34)   :done, langgraph, 2025-03-05, 2025-03-20
    Basic Scanning            :done, scan-basic, 2025-03-05, 2025-03-25
    Documentation Setup       :done, docs-initial, 2025-03-05, 2025-03-30
    
    section Q2 Core Features
    CrewAI Integration (#33)  :done, crewai, 2025-04-01, 2025-04-30
    OpenAI Agents Support (#30) :done, openai-agents, 2025-04-01, 2025-05-15
    Agent Metadata Extract (#62, #65) :done, metadata, 2025-04-15, 2025-05-30
    Test Configuration (#82)  :done, test-config, 2025-05-01, 2025-05-15
```

### Current Work & Near-Term Roadmap (2025 Q3-Q4)
```mermaid
gantt
    title Current & Upcoming Work
    dateFormat YYYY-MM-DD
    axisFormat %Y-%m
    
    section September 2025 Active
    Graph JS Runtime Fixes    :done, graph-js-fix, 2025-09-01, 2025-09-11
    Render Only Graph 36      :done, graph-only, 2025-09-01, 2025-09-07
    System Prompts 39         :done, sys-prompts, 2025-09-01, 2025-09-07
    Export Graph JSON 99      :done, export-json, 2025-09-01, 2025-09-10
    AutoGen Improvements 103  :done, autogen-fix, 2025-09-05, 2025-09-10
    Test Coverage & Standards :done, test-coverage, 2025-09-10, 2025-09-11
    PR 107 Review Fixes       :done, pr-107-fixes, 2025-09-11, 2025-09-14
    Graph Visualization 35    :active, graph-viz, 2025-09-14, 2025-10-15
    LangGraph Bug Fix 94      :active, langgraph-bug, 2025-09-10, 2025-09-30
    
    section Q4 2025 Roadmap
    AutoGen Framework 41      :autogen, 2025-10-01, 2025-10-30
    PydanticAI Framework 42   :pydantic-ai, 2025-10-15, 2025-11-15
    PDF Export 37             :pdf-export, 2025-11-01, 2025-11-30
    Dify Framework 40         :dify, 2025-11-01, 2025-11-30
```

### Framework Support Timeline
```mermaid
gantt
    title Framework Integration Roadmap
    dateFormat YYYY-MM-DD
    axisFormat %Y-%m
    
    section Completed Frameworks
    LangGraph 34              :done, langgraph, 2025-03-05, 2025-03-20
    CrewAI 33                 :done, crewai, 2025-04-01, 2025-04-30
    OpenAI Agents 30          :done, openai-agents, 2025-04-01, 2025-05-15
    
    section Planned Frameworks
    AutoGen 41                :autogen-plan, 2025-10-01, 2025-10-30
    PydanticAI 42             :pydantic-plan, 2025-10-15, 2025-11-15
    Dify 40                   :dify-plan, 2025-11-01, 2025-11-30
    
    section Future Consideration
    LangChain                 :langchain-future, 2026-01-01, 2026-03-31
```

## Major Milestones

### Completed Milestones
- **March 2025**: Initial release with [LangGraph](https://langchain-ai.github.io/langgraph/) support ([#34](https://github.com/splx-ai/agentic-radar/issues/34))
- **April-May 2025**: [CrewAI](https://crewai.com/) integration ([#33](https://github.com/splx-ai/agentic-radar/issues/33)), [OpenAI Agents](https://platform.openai.com/docs/agents) support ([#30](https://github.com/splx-ai/agentic-radar/issues/30))
- **May 2025**: Agent metadata extraction ([#62](https://github.com/splx-ai/agentic-radar/issues/62), [#65](https://github.com/splx-ai/agentic-radar/issues/65)), test configuration ([#82](https://github.com/splx-ai/agentic-radar/issues/82))
- **September 2025**: Graph-only rendering ([#36](https://github.com/splx-ai/agentic-radar/issues/36)), system prompts section ([#39](https://github.com/splx-ai/agentic-radar/issues/39)), JSON export ([#99](https://github.com/splx-ai/agentic-radar/issues/99)), [AutoGen](https://autogen-ai.github.io/autogen/) improvements ([#103](https://github.com/splx-ai/agentic-radar/issues/103))

### Current Focus (September 2025)
- **[PR #107](https://github.com/splx-ai/agentic-radar/pull/107)**: Fixed JavaScript runtime errors and completed issues #36, #39 with comprehensive test coverage
- **[Issue #35](https://github.com/splx-ai/agentic-radar/issues/35)**: Graph visualization improvements still in progress (scaling, orientation, overlap reduction, styling)
- **[Issue #94](https://github.com/splx-ai/agentic-radar/issues/94)**: Fixing [LangGraph](https://langchain-ai.github.io/langgraph/) visualization bug (incomplete edge detection)
- Established [testing standards](testing-standards.md) for HTML+JavaScript components
- Addressed all PR review comments and improved test portability

### Active GitHub Issues (Open)
- **Framework Support**: [AutoGen](https://autogen-ai.github.io/autogen/) ([#41](https://github.com/splx-ai/agentic-radar/issues/41)), [PydanticAI](https://ai.pydantic.dev/) ([#42](https://github.com/splx-ai/agentic-radar/issues/42)), [Dify](https://dify.ai/) ([#40](https://github.com/splx-ai/agentic-radar/issues/40))
- **Export Features**: PDF export ([#37](https://github.com/splx-ai/agentic-radar/issues/37))
- **Visualization**: Graph improvements ([#35](https://github.com/splx-ai/agentic-radar/issues/35))
- **Bug Fixes**: [LangGraph](https://langchain-ai.github.io/langgraph/) [Langmanus agent](https://github.com/Darwin-lfl/langmanus) visualization ([#94](https://github.com/splx-ai/agentic-radar/issues/94))

### Upcoming Milestones
- **Q4 2025**: New framework integrations and export capabilities
- **Q1 2026**: Enterprise features and advanced analytics
- **Q2 2026**: Plugin ecosystem and cloud integration

## Development Phases

### Phase 1: Foundation (Complete)
- Core scanning capabilities
- Basic framework support ([LangGraph](https://langchain-ai.github.io/langgraph/))
- HTML report generation

### Phase 2: Framework Expansion (Complete)
- [CrewAI](https://crewai.com/), [OpenAI Agents](https://platform.openai.com/docs/agents), [AutoGen](https://autogen-ai.github.io/autogen/) support
- Tool and vulnerability detection
- [MCP server](https://modelcontextprotocol.io/) integration

### Phase 3: Advanced Security (In Progress)
- Runtime vulnerability testing
- Prompt hardening capabilities
- Enhanced visualization

### Phase 4: Enterprise & Scale (Planned)
- API development
- Cloud integration
- Advanced analytics and reporting
- Plugin architecture

## Technology Stack
- **Core**: [Python](https://python.org/), [PyPI](https://pypi.org/) packaging
- **Visualization**: [Mermaid](https://mermaid.js.org/), HTML/CSS/JS
- **Testing**: Runtime injection, [OpenAI](https://openai.com/) integration
- **Frameworks**: [LangGraph](https://langchain-ai.github.io/langgraph/), [CrewAI](https://crewai.com/), [OpenAI Agents](https://platform.openai.com/docs/agents), [AutoGen](https://autogen-ai.github.io/autogen/), [n8n](https://n8n.io/)