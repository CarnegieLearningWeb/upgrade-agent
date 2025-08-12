# UpGradeAgent

UpGrade is an open source A/B testing platform for education software. UpGradeAgent is a chatbot that can make requests to UpGrade's client API endpoints for testing, simulating, and verifying its functionalities based on natural language inputs.

This document states the MVP design of this chatbot which is able to make requests to the core client API endpoints of UpGrade. The app will be built with Python using the LangGraph library. We will use the Anthropic Claude Sonnet 4 model (I will provide `ANTHROPIC_API_KEY` in the .env file) for the agents.

For the MVP, the user will be interacting with the chatbot in the Terminal console (it may later become a Slack bot).

## Quick Reference

### Documentation

- [Core Terms](./docs/core-terms.md) - Essential UpGrade terminology and concepts
- [Assignment Behavior](./docs/assignment-behavior.md) - How assignment rules and consistency work together
- [API Reference](./docs/api-reference.md) - Complete API endpoints and request/response examples
- [Tools](./docs/tools.md) - Complete tool specifications and API integration patterns
- [Graph Structure](./docs/graph-structure.md) - LangGraph architecture, nodes, and routing logic
- [Example Chats](./docs/example-chats.md) - Sample bot interactions and conversation patterns
- [LangGraph Reference](./docs/langgraph-reference.md) - LangGraph documentation reference

### Implementation Structure

- `/src/agent/` - LangGraph nodes and graph definition
- `/src/tools/` - API integration and tool implementations
- `/src/models/` - Data models and response schemas
- `/reference/` - Contains UpGrade controller implementation for reference

## Bot Capabilities to Implement

- Explain Terms and Concepts: Answer questions about UpGrade terminology and concepts
- Version Check: Call health endpoint and return version info
- List Experiments: Query experiments by context or date filters
- Experiment Details: Fetch and explain experiment design details
- Create/Update/Delete Experiment: Create and modify experiments
- Visit Decision Point: Have users visit a decision point
- Condition Balance Testing: Enroll users and analyze condition distribution
- Consistency Rule Testing: Create experiments and verify assignment behavior

## Supported API endpoints

- Base API URL
- GET `/experiments/contextMetaData`: Get All Available App Contexts
- GET `/experiments/names`: Get All Defined Experiment Names
- GET `/experiments`: Get All Defined Experiments
- GET `/experiments/single/<experiment_id>` - Get Experiment
- POST `/experiments` - Create Experiment
- PUT `/experiments/<experiment_id>` - Update Experiment
- POST `/experiments/state` - Update Experiment Status
- DELETE `/experiments/<experiment_id>` - Delete Experiment
- POST `/v6/init` - Initialize Users
- POST `/v6/assign` - Get All Experiment Conditions
- POST `/v6/mark` - Record Decision Point Visit

## Experiments that are currently not supported

We will not support creating, updating the experiments with these settings. We also won't allow requesting `/v6/mark` (requires `experimentId`) for these unsupported experiments for now. Reject when asked.

- Within-subjects Experiments (set by Unit of Assignment)
- Factorial Experiments (set by Design Type)
- Stratified Random Sampling Experiments (set by Assignment Algorithm)
- TS Configurable (MOOClet) Experiments (set by Assignment Algorithm)

Also, we won't support adding or updating metrics for experiments, as well as logging the metrics data using the client API `v6/log`. Reject when asked about metrics. We also won't support anything related to feature flags and preview users. We also won't support creating or updating "public" segments. Reject when asked about these and other unknown terms.
