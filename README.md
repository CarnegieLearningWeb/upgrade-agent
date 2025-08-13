# UpGradeAgent

UpGrade is an open source A/B testing platform for education software. UpGradeAgent is a chatbot that can make requests to UpGrade's client API endpoints for testing, simulating, and verifying its functionalities based on natural language inputs.

This document describes the MVP design of this chatbot which uses a **streamlined 5-node architecture** to provide reliable, context-aware conversations about A/B testing operations. The app is built with Python using the LangGraph library and Anthropic Claude Sonnet 4 model (claude-sonnet-4-20250514).

For the MVP, users interact with the chatbot in the Terminal console (it may later become a Slack bot).

## Design Principles

The app prioritizes:
- **Accuracy over token cost** - Reliable understanding and execution
- **Intelligent clarification** - Asks for clarification on ambiguous queries (e.g., "What's the status?") rather than making assumptions
- **Progressive information gathering** - Naturally collects missing information through conversation
- **Safety first** - Always confirms before potentially destructive actions
- **Conversational memory** - Retains and uses prior context within sessions

## Architecture Overview

UpGradeAgent uses a **streamlined 5-node architecture** that handles all conversation flows intelligently:

1. **Conversation Analyzer** - Understands user intent with full context
2. **Information Gatherer** - Collects missing information progressively  
3. **Confirmation Handler** - Ensures user approval before actions
4. **Tool Executor** - Executes UpGrade API operations safely
5. **Response Generator** - Creates natural, helpful responses

This architecture handles everything from simple greetings to complex multi-step experiment creation without the complexity of traditional router-based approaches.

## Quick Reference

### Documentation

- [Graph Structure](./docs/graph-structure.md) - Streamlined 5-node architecture design and implementation
- [Tools](./docs/tools.md) - API integration and tool specifications
- [Example Chats](./docs/example-chats.md) - Sample bot interactions demonstrating conversation patterns
- [Core Terms](./docs/core-terms.md) - Essential UpGrade terminology and concepts
- [Assignment Behavior](./docs/assignment-behavior.md) - How assignment rules and consistency work together
- [API Reference](./docs/api-reference.md) - Complete API endpoints and request/response examples
- [LangGraph Reference](./docs/langgraph-reference.md) - LangGraph framework documentation for implementation

### Implementation Structure

- `/src/agent/` - LangGraph nodes and graph definition
- `/src/tools/` - API integration and tool implementations
- `/src/models/` - Data models and response schemas
- `/reference/` - Contains UpGrade controller implementation for reference

## Bot Capabilities

### Core Conversational Abilities
- **Natural conversation** - Handles greetings, general questions, and context-aware follow-ups
- **Intelligent clarification** - Resolves ambiguous queries like "What's the status?"
- **Progressive information gathering** - Guides users through complex operations step-by-step
- **Error recovery** - Handles typos, wrong inputs, and helps users get back on track

### UpGrade-Specific Operations
- **Explain Terms and Concepts** - Answer questions about UpGrade terminology and A/B testing
- **System Health** - Check UpGrade service status and version information
- **Experiment Management** - List, create, update, delete, and start/stop experiments
- **Experiment Details** - Fetch and explain experiment configurations in detail
- **User Simulation** - Simulate users visiting decision points and getting assigned conditions
- **Testing & Analysis** - Test condition balance and verify consistency rule behavior

## Supported API Endpoints

### System Information
- `GET /` - Health check and version info
- `GET /experiments/contextMetaData` - Get available app contexts and their supported values

### Experiment Management
- `GET /experiments/names` - Get all experiment names and IDs
- `GET /experiments` - Get all experiments with optional filtering
- `GET /experiments/single/<experiment_id>` - Get detailed experiment configuration
- `POST /experiments` - Create new experiment
- `PUT /experiments/<experiment_id>` - Update experiment configuration
- `POST /experiments/state` - Update experiment status (start/stop)
- `DELETE /experiments/<experiment_id>` - Delete experiment

### User Simulation & Testing
- `POST /v6/init` - Initialize users with group memberships
- `POST /v6/assign` - Get experiment condition assignments for users
- `POST /v6/mark` - Record decision point visits

## Limitations & Unsupported Features

The following UpGrade features are **not supported** in the MVP:

### Unsupported Experiment Types
- Within-subjects Experiments (Unit of Assignment)
- Factorial Experiments (Design Type)  
- Stratified Random Sampling Experiments (Assignment Algorithm)
- TS Configurable (MOOClet) Experiments (Assignment Algorithm)

### Unsupported Features
- Metrics management and logging (`/v6/log` endpoint)
- Feature flags and preview users
- Public segment creation/management
- Advanced analytics and reporting

The bot will politely reject requests for these features and suggest supported alternatives.

## Example Interactions

### Simple Question
```
User: What is A/B testing?
Bot: A/B testing is a method of comparing two or more versions of something...
```

### Ambiguous Query Resolution  
```
User: What's the status?
Bot: I need clarification on what status you're asking about:
     1. UpGrade service health status
     2. Status of your experiments  
     3. Explanation of "status" concept
     Which one would you like to know about?
```

### Progressive Experiment Creation
```
User: Create a new experiment
Bot: I'll help you create a new experiment. What would you like to name it?

User: Homepage Test
Bot: Great! Which app context should this experiment run in?
     Available: assign-prog, mathstream, livehint-ai

User: assign-prog  
Bot: Perfect! Which decision point should this experiment target?...
```

See [Example Chats](./docs/example-chats.md) for complete conversation examples.

## Getting Started

1. **Review the Architecture**: Start with [Graph Structure](./docs/graph-structure.md) to understand the 5-node design
2. **Understand the Domain**: Read [Core Terms](./docs/core-terms.md) for UpGrade concepts
3. **See It In Action**: Browse [Example Chats](./docs/example-chats.md) for interaction patterns
4. **Implementation Details**: Check [Tools](./docs/tools.md) for API integration specifics
