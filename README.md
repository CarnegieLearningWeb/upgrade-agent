# UpGradeAgent

UpGrade is an open source A/B testing platform for education software. UpGradeAgent is a chatbot that can make requests to UpGrade's client API endpoints for testing, simulating, and verifying its functionalities based on natural language inputs.

This document describes the MVP design of this chatbot which uses a **streamlined 5-node architecture** to provide reliable, context-aware conversations about A/B testing operations. The app is built with Python using the LangGraph library and Anthropic Claude Sonnet 4 model (claude-sonnet-4-20250514).

For the MVP, users interact with the chatbot in the Terminal console (it may later become a Slack bot).

## Design Principles

The app prioritizes:

- **Accuracy over token cost** - Reliable understanding and execution of A/B testing operations
- **Intelligent clarification** - Asks for clarification on ambiguous queries (e.g., "What's the status?") rather than making assumptions
- **Progressive information gathering** - Naturally collects missing information through conversation
- **Safety first** - Always confirms before potentially destructive actions
- **Conversational memory** - Retains and uses prior context within sessions

## Architecture Overview

UpGradeAgent uses a **streamlined 5-node architecture** that handles all conversation flows intelligently:

1. **Conversation Analyzer** (LLM) - Intent classification and orchestration
2. **Information Gatherer** (LLM) - Data collection and validation
3. **Confirmation Handler** (Non-LLM) - Safety confirmations for destructive actions
4. **Tool Executor** (Non-LLM) - API execution layer
5. **Response Generator** (LLM) - All user-facing communication

### Tool Architecture

Each node has access to specific tools that match its responsibilities:

- **Node-specific tool access**: Enforces architectural boundaries and maintains separation of concerns
- **Auto-storage pattern**: Gatherer tools automatically store results in predictable locations
- **Progressive parameter building**: Schema tools guide the LLM through complex parameter collection
- **Granular error handling**: Specific error types (api, auth, validation, not_found, unknown) for better debugging

## Quick Reference

### Core Documentation

- [Graph Structure](./docs/graph-structure.md) - Complete 5-node architecture design and implementation
- [Tools](./docs/tools.md) - Comprehensive tool specifications and API integration patterns

### Supporting Documentation

- [Core Terms](./docs/core-terms.md) - Essential UpGrade terminology and concepts
- [Assignment Behavior](./docs/assignment-behavior.md) - How assignment rules and consistency work together
- [API Reference](./docs/api-reference.md) - Complete API endpoints and request/response examples

*Note: Supporting documentation files contain the knowledge base content used by the Information Gatherer node.*

## Bot Capabilities

### Educational Features
- **Explain Terms and Concepts** - Answer questions about UpGrade terminology and A/B testing
- **Assignment Behavior Guidance** - Explain how different assignment rules interact
- **Schema Information** - Provide parameter requirements for various operations

### System Operations
- **System Health** - Check UpGrade service status and version information
- **Context Discovery** - List available app contexts and their supported values

### Experiment Management
- **List and Search** - Find experiments by name, context, or other criteria
- **Create Experiments** - Guide users through experiment creation with validation
- **Update Experiments** - Modify existing experiments with partial updates
- **Delete Experiments** - Safely remove experiments with confirmation
- **Status Management** - Start, stop, and change experiment states

### User Simulation & Testing
- **User Initialization** - Set up users with group memberships for testing
- **Condition Assignment** - Simulate users getting assigned to experimental conditions
- **Decision Point Tracking** - Record when users visit experiment decision points
- **Assignment Analysis** - Verify condition balance and consistency rule behavior

## Typical User Interactions

```
User: "What contexts are available?"
Bot: Lists all available contexts from UpGrade

User: "Create an experiment called 'Math Hints' in assign-prog context"
Bot: Guides through parameter collection → Confirms creation → Executes

User: "What conditions did user123 get for that experiment?"
Bot: Simulates user assignment and shows conditions

User: "Delete the Math Hints experiment"
Bot: ⚠️ Shows destruction warning → Confirms → Deletes if approved
```

## Supported API Endpoints

### System Information

- `GET /` - Health check and version info
- `GET /experiments/contextMetaData` - Get available app contexts and their supported values

### Experiment Management

- `GET /experiments/names` - Get all experiment names and IDs
- `GET /experiments` - Get all experiments with optional filtering
- `GET /experiments/single/<experiment_id>` - Get detailed experiment configuration
- `POST /experiments` - Create new experiment
- `PUT /experiments/<experiment_id>` - Update experiment configuration (supports partial updates)
- `POST /experiments/state` - Update experiment status (start/stop)
- `DELETE /experiments/<experiment_id>` - Delete experiment

### User Simulation & Testing

- `POST /v6/init` - Initialize users with group memberships
- `POST /v6/assign` - Get experiment condition assignments for users
- `POST /v6/mark` - Record decision point visits

## Environment Setup

### Required Configuration

```bash
# UpGrade API Configuration
UPGRADE_API_URL=http://localhost:3030/api  # or production URL
UPGRADE_AUTH_TOKEN=your_bearer_token

# Optional Configuration
DEFAULT_USER_ID=simulation_user
REQUEST_TIMEOUT=30
```

### Dependencies

- Python 3.8+
- LangGraph
- Anthropic Claude API access
- aiohttp for async API calls
- pydantic for data validation

## Limitations & Unsupported Features

The following UpGrade features are **not supported** in the MVP:

### Unsupported Experiment Types

- Within-subjects Experiments (Unit of Assignment)
- Factorial Experiments (Design Type)
- Stratified Random Sampling Experiments (Assignment Algorithm)
- TS Configurable (MOOClet) Experiments (Assignment Algorithm)

### Unsupported Features

- **Payload Management** - Viewing, adding, or updating payloads from experiments
- **Metrics and Logging** - Management and logging via `/v6/log` endpoint
- **Feature Flags** - Preview users and feature flag functionality
- **Public Segments** - Creation, management, or assignment of public segments
- **Advanced Analytics** - Detailed reporting and statistical analysis
- **Bulk Operations** - Mass experiment creation or updates
- **Import/Export** - Experiment configuration import/export

### Design Limitations

- **Terminal Interface Only** - Web UI not supported in MVP
- **Single Session Memory** - No persistence across application restarts
- **English Only** - No internationalization support
- **Basic Error Recovery** - Limited retry logic for transient failures

## Error Handling

The bot provides helpful error messages for common issues:

- **Authentication errors** - Clear guidance on token setup
- **Validation errors** - Specific parameter requirements and fixes
- **API errors** - User-friendly explanations of service issues
- **Not found errors** - Suggestions for finding the right resources
- **Unknown errors** - Graceful degradation with error reporting

## Development Notes

### Code Organization

```
/src/
  /nodes/          # LangGraph node implementations
  /tools/          # Tool functions organized by node
  /api/            # UpGrade API client
  /exceptions/     # Custom exception types
  /models/         # Pydantic data models
  /config/         # Configuration management
```

### Key Design Patterns

- **Async/await throughout** - All API calls and tools are async
- **Type safety** - Extensive use of TypedDict and Pydantic models
- **Error propagation** - Structured error handling with specific types
- **Auto-storage decorators** - Automatic result caching with predictable keys
- **Progressive disclosure** - Complex operations broken into guided steps
