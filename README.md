# multi-server-mcp-agent# Technical Documentation: Agentic AI Application Using Model Context Protocol (MCP)

## Project Overview

**Project Name:** IT Operations Assistant  
**Type:** Agentic AI Application  
**Primary Use Case:** Enterprise IT Operations Management  
**Framework:** Model Context Protocol (MCP)

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Architecture Overview](#2-architecture-overview)
3. [High-Level Design](#3-high-level-design)
4. [Component Details](#4-component-details)
5. [Libraries and Dependencies](#5-libraries-and-dependencies)
6. [Data Flow and Communication](#6-data-flow-and-communication)
7. [Implementation Details](#7-implementation-details)
8. [Use Case Scenarios](#8-use-case-scenarios)
9. [Deployment Considerations](#9-deployment-considerations)

---

## 1. Introduction

### 1.1 Purpose

This document describes the architecture, design, and implementation of an Agentic AI application built using the Model Context Protocol (MCP). The application serves as an IT Operations Assistant that integrates multiple backend systems to provide operational insights, manage work items, monitor repositories, and perform system diagnostics.

### 1.2 Scope

The application demonstrates enterprise-grade agentic AI capabilities including:
- Multi-system data retrieval and orchestration
- Intelligent reasoning and decision-making using LLM
- Conversational memory and context management
- Integration with Azure DevOps (Boards and Repos)
- Local system operations through terminal access

### 1.3 Requirements Satisfied

The implementation fulfills all assignment requirements:
- **Agent:** One LLM-powered agent with ReAct-style reasoning loop
- **MCP Client:** Centralized client layer managing all server connections
- **MCP Servers:** Three independent servers (Azure Boards, Azure Repos, Smart Terminal)
- **Transport Protocols:** Mixed implementation (HTTP and STDIO)
- **Enterprise Use Case:** IT Operations Assistant
- **Multi-server Orchestration:** Coordinated operations across all servers
- **Conversational Context:** Built-in memory management

---

## 2. Architecture Overview

### 2.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         USER LAYER                          │
│                  (Interactive CLI Interface)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ User Input/Output
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                      AGENT LAYER                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │         MCPAgent (Orchestration)                   │    │
│  │  - Groq LLM (Llama-3.3-70b-versatile)             │    │
│  │  - ReAct Reasoning Loop                            │    │
│  │  - Conversation Memory (max_steps=15)              │    │
│  │  - Tool Selection & Execution                      │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ MCP Protocol
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   MCP CLIENT LAYER                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │         MCPClient (Connection Manager)             │    │
│  │  - Configuration Parser (mcp.json)                 │    │
│  │  - Session Management                              │    │
│  │  - Transport Protocol Handler                      │    │
│  │  - Tool Discovery & Routing                        │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────┬────────────────┬──────────────┬───────────────┘
              │                │              │
       ┌──────▼─────┐   ┌─────▼──────┐  ┌───▼────────┐
       │    HTTP    │   │    HTTP    │  │   STDIO    │
       └──────┬─────┘   └─────┬──────┘  └───┬────────┘
              │                │              │
┌─────────────▼──────┐ ┌───────▼────────┐ ┌─▼─────────────────┐
│  MCP SERVER 1      │ │  MCP SERVER 2  │ │  MCP SERVER 3     │
│  Azure Boards      │ │  Azure Repos   │ │  Smart Terminal   │
│  (Port 8001)       │ │  (Port 8002)   │ │  (STDIO)          │
│                    │ │                │ │                   │
│  Tools:            │ │  Tools:        │ │  Tools:           │
│  - list_projects   │ │  - list_repos  │ │  - current_dir    │
│  - query_items     │ │  - list_branch │ │  - list_dir       │
│  - get_active      │ │  - get_commits │ │  - read_file      │
│  - get_unassigned  │ │  - list_prs    │ │  - search_file    │
│  - get_epics       │ │  - get_items   │ │  - file_info      │
│  - get_comments    │ │                │ │  - check_port     │
│  - pipeline_status │ │                │ │  - port_usage     │
└─────────┬──────────┘ └────────┬───────┘ └────────┬──────────┘
          │                     │                   │
          │                     │                   │
┌─────────▼─────────────────────▼───────────────────▼──────────┐
│                    DATA SOURCES LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Azure DevOps │  │ Azure DevOps │  │  Local File      │   │
│  │   Boards     │  │     Repos    │  │  System          │   │
│  │   (REST API) │  │   (REST API) │  │  (Project Root)  │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

### 2.2 Architectural Principles

**Layered Architecture:**
- Clear separation of concerns across four distinct layers
- Each layer has well-defined responsibilities and interfaces

**Protocol-Based Communication:**
- All inter-component communication follows MCP specification
- Standardized tool calling and response formats

**Extensibility:**
- New MCP servers can be added through configuration
- No code changes required in agent or client layers

**Security:**
- Sandboxed terminal operations (restricted to project root)
- Authentication through Azure Personal Access Tokens
- No direct database or system access from agent

---

## 3. High-Level Design

### 3.1 Design Philosophy

The application follows a **microservices-inspired architecture** where each MCP server represents an independent service with specific domain expertise. The agent layer acts as an intelligent orchestrator that coordinates these services to fulfill user requests.

### 3.2 Key Design Decisions

**1. Agent-Based Architecture**
   - **Rationale:** Provides intelligent reasoning and multi-step planning
   - **Benefit:** Can handle complex queries requiring multiple tool calls
   - **Implementation:** MCPAgent with built-in conversation memory

**2. Configuration-Driven Server Management**
   - **Rationale:** Enables dynamic server discovery and registration
   - **Benefit:** Easy to add/remove services without code changes
   - **Implementation:** JSON configuration file (mcp.json)

**3. Mixed Transport Protocols**
   - **Rationale:** Different backends require different communication patterns
   - **HTTP:** Suitable for remote Azure DevOps APIs (stateless)
   - **STDIO:** Efficient for local process communication (terminal server)

**4. Stateless MCP Servers**
   - **Rationale:** Servers don't maintain session state
   - **Benefit:** Scalable, reliable, easy to restart
   - **State Management:** Handled by agent's conversation memory

**5. Domain-Specific Server Separation**
   - **Rationale:** Azure Boards and Repos serve different purposes
   - **Benefit:** Cleaner code, independent scaling, focused responsibilities

### 3.3 System Workflow

**Typical Interaction Flow:**

1. **User Input:** User types a natural language query
2. **Agent Processing:** 
   - Agent receives input with conversation history
   - LLM reasons about required actions
   - Identifies relevant tools from available MCP servers
3. **Tool Execution:**
   - Agent invokes tools via MCP Client
   - Client routes requests to appropriate servers
   - Servers execute operations and return results
4. **Response Synthesis:**
   - Agent receives tool results
   - LLM processes and synthesizes information
   - Generates natural language response
5. **Memory Update:**
   - Conversation history updated with exchange
   - Context preserved for follow-up queries

---

## 4. Component Details

### 4.1 User Layer

**Component:** Interactive CLI Interface (client.py)

**Responsibilities:**
- Capture user input from terminal
- Display agent responses in real-time
- Provide conversation management commands (clear, exit)

**Features:**
- Asynchronous input handling
- Graceful error display
- Clean shutdown with resource cleanup

**Commands:**
- `exit` / `quit`: Terminate the application
- `clear`: Reset conversation memory
- Any other input: Processed as query

---

### 4.2 Agent Layer

**Component:** MCPAgent

**Core Functionality:**
- **LLM Integration:** Uses Groq's Llama-3.3-70b-versatile model
- **Reasoning Engine:** Implements ReAct pattern (Reasoning + Acting)
- **Memory Management:** Maintains conversation history
- **Tool Orchestration:** Selects and executes appropriate tools
- **Error Handling:** Gracefully handles tool failures

**Configuration Parameters:**
```python
agent = MCPAgent(
    llm=llm,                    # Language model instance
    client=client,               # MCP client for tool access
    max_steps=15,                # Maximum reasoning iterations
    memory_enabled=True          # Enable conversation memory
)
```

**Reasoning Loop:**
1. Receive user query + conversation history
2. Analyze query and determine action plan
3. Select appropriate tool(s) from available servers
4. Execute tool calls sequentially or in parallel
5. Process results and determine next action
6. Repeat until satisfactory answer or max_steps reached
7. Generate final response

**Memory System:**
- Stores entire conversation history
- Provides context for follow-up questions
- Can be cleared manually by user
- Helps maintain coherent multi-turn dialogues

---

### 4.3 MCP Client Layer

**Component:** MCPClient

**Responsibilities:**
- Parse MCP server configuration
- Establish connections to all configured servers
- Manage server sessions and lifecycle
- Route tool calls to appropriate servers
- Handle transport protocol differences

**Configuration Loading:**
```python
client = MCPClient.from_config_file("config/mcp.json")
```

**Session Management:**
- Maintains persistent connections to HTTP servers
- Manages subprocess for STDIO server
- Handles reconnection on failure
- Cleanup on shutdown

**Tool Routing:**
- Discovers available tools from all servers
- Creates unified tool catalog for agent
- Routes specific tool calls to correct server
- Handles response formatting

---

### 4.4 MCP Server Layer

#### 4.4.1 Azure Boards Server

**File:** azure_boards_server.py  
**Transport:** HTTP (Port 8001)  
**Framework:** FastMCP  
**Purpose:** Azure DevOps Boards integration

**Data Source:** Azure DevOps Work Items API

**Available Tools:**

1. **list_projects()**
   - Returns all Azure DevOps projects
   - No parameters required
   - Output: Project names and count

2. **query_work_items(project: str, wiql: str)**
   - Execute custom WIQL (Work Item Query Language) queries
   - Flexible querying capability
   - Returns detailed work item information

3. **get_active_work_items(project: str)**
   - Pre-built query for active work items
   - Ordered by last changed date
   - Common operational query

4. **get_unassigned_work_items(project: str)**
   - Finds active items without assignees
   - Useful for resource allocation
   - Helps identify bottlenecks

5. **get_current_epics(project: str)**
   - Lists all non-closed epics
   - Strategic planning view
   - High-level work tracking

6. **get_work_item_comments(project: str, work_item_id: int)**
   - Retrieves discussion threads
   - Shows collaboration history
   - Includes author and timestamp

7. **get_pipeline_status(project: str)**
   - Recent build pipeline runs
   - Status and result information
   - CI/CD monitoring

**Authentication:**
- Uses Azure Personal Access Token (PAT)
- HTTP Basic Auth with empty username
- Token stored in environment variable

**Error Handling:**
- HTTP status code validation
- 404 detection for missing resources
- Timeout protection (15 seconds)
- Exception wrapping with error details

#### 4.4.2 Azure Repos Server

**File:** azure_repos_server.py  
**Transport:** HTTP (Port 8002)  
**Framework:** FastMCP  
**Purpose:** Azure DevOps Repositories integration

**Data Source:** Azure DevOps Git Repositories API

**Available Tools:**

1. **list_repositories()**
   - All repositories in the project
   - Includes default branch information
   - Repository IDs and names

2. **list_branches(repository: str)**
   - All branches in specified repository
   - Formatted branch names (refs/heads/ removed)
   - Branch discovery

3. **get_latest_commits(repository: str, branch: str = "main", top: int = 5)**
   - Recent commit history
   - Configurable number of commits
   - Shows author, message, date

4. **list_pull_requests(repository: str)**
   - Active pull requests only
   - PR title, creator, status
   - Code review tracking

5. **get_repo_items(repository: str, path: str = "/")**
   - Browse repository structure
   - Files and folders at given path
   - One level recursion

**Authentication:**
- Same PAT-based approach as Boards server
- Shared Azure DevOps organization access

**Design Pattern:**
- Identical error handling as Boards server
- Consistent response format
- Shared utility function (azure_request)

#### 4.4.3 Smart Terminal Server

**File:** smart_terminal_server.py  
**Transport:** STDIO  
**Framework:** FastMCP (mcp.server.fastmcp)  
**Purpose:** Local file system and process operations

**Data Source:** Local file system (project root only)

**Available Tools:**

1. **current_working_directory()**
   - Returns project root path
   - No parameters
   - Orientation tool

2. **list_directory(path: str = ".")**
   - List files/folders in directory
   - Relative to project root
   - Security validated

3. **read_file(path: str)**
   - Read file contents
   - Text files only
   - UTF-8 encoding with error tolerance

4. **search_file(filename: str)**
   - Find files by name (case-insensitive)
   - Recursive search from project root
   - Returns full paths

5. **file_info(path: str)**
   - File metadata (size, modified date)
   - Directory detection
   - Formatted output (KB, ISO timestamps)

6. **check_port(port: int)**
   - Test if port is open or free
   - Localhost (127.0.0.1) only
   - Network diagnostics

7. **who_is_using_port(port: int)**
   - Identify process using port (Windows)
   - Uses netstat command
   - Process ID discovery

**Security Model:**
- **Path Validation:** All paths validated against project root
- **Access Restriction:** Cannot access parent directories
- **No Write Operations:** Read-only file system access
- **No Command Execution:** No arbitrary shell commands

**Implementation:**
```python
def safe_path(path: str) -> pathlib.Path:
    full_path = (PROJECT_ROOT / path).resolve()
    if not str(full_path).startswith(str(PROJECT_ROOT)):
        raise ValueError("Access outside project directory not allowed")
    return full_path
```

---

## 5. Libraries and Dependencies

### 5.1 Core Framework Libraries

**1. mcp-use**
- **Purpose:** MCP client and agent implementation
- **Version:** Latest (from PyPI)
- **Components Used:**
  - `MCPAgent`: Agent with reasoning capabilities
  - `MCPClient`: Client for managing MCP servers
- **Functionality:** Orchestration layer between LLM and MCP servers

**2. fastmcp**
- **Purpose:** MCP server framework
- **Version:** Latest
- **Usage:** Building HTTP and STDIO MCP servers
- **Features:**
  - Decorator-based tool definition (@mcp.tool)
  - Automatic protocol handling
  - Built-in transport support

**3. langchain-groq**
- **Purpose:** Groq LLM integration
- **Model:** llama-3.3-70b-versatile
- **Features:**
  - High-performance inference
  - Structured output support
  - Tool calling capabilities

### 5.2 HTTP and API Libraries

**4. requests**
- **Purpose:** HTTP client for Azure DevOps API
- **Usage:** REST API communication
- **Features Used:**
  - Basic authentication
  - JSON request/response handling
  - Timeout configuration
  - Exception handling

**5. HTTPBasicAuth (requests.auth)**
- **Purpose:** Authentication for Azure APIs
- **Usage:** PAT token authentication
- **Pattern:** Empty username with PAT as password

### 5.3 Utility Libraries

**6. python-dotenv**
- **Purpose:** Environment variable management
- **Usage:** Load .env files for secrets
- **Variables:**
  - GROQ_API_KEY: Groq authentication
  - AZURE_ORG: Azure organization name
  - AZURE_PROJECT: Azure project name
  - AZURE_PAT: Personal Access Token

**7. asyncio**
- **Purpose:** Asynchronous programming
- **Usage:** Agent execution and event loop management
- **Pattern:** async/await for I/O operations

**8. pathlib**
- **Purpose:** Modern file path handling
- **Usage:** Path validation and manipulation
- **Security:** Resolve paths and prevent directory traversal

**9. socket**
- **Purpose:** Network programming
- **Usage:** Port availability checking
- **Functionality:** TCP port testing

**10. subprocess**
- **Purpose:** System command execution
- **Usage:** Windows netstat queries
- **Security:** Limited to specific commands only

**11. datetime**
- **Purpose:** Timestamp handling
- **Usage:** Format file modification times
- **Output:** ISO 8601 format

**12. os**
- **Purpose:** Operating system interface
- **Usage:** Environment variables, file operations
- **Functionality:** Cross-platform compatibility

### 5.4 Dependency Summary

**Production Dependencies:**
```
mcp-use
fastmcp
langchain-groq
requests
python-dotenv
```

**Standard Library (No Installation Required):**
```
asyncio
pathlib
socket
subprocess
datetime
os
```

**Optional Development Dependencies:**
```
pytest (for testing)
black (for code formatting)
pylint (for linting)
```

---

## 6. Data Flow and Communication

### 6.1 Request Flow

**Step-by-Step Data Flow:**

```
[1] User Input
    └─> "What are the active work items in ProjectX?"

[2] Agent Receives Query
    └─> MCPAgent.run(user_input)
        └─> Adds to conversation history
        └─> Sends to LLM with available tools

[3] LLM Reasoning
    └─> Analyzes query
    └─> Determines need for Azure Boards data
    └─> Selects tool: get_active_work_items

[4] Tool Call Generation
    └─> {
          "tool": "get_active_work_items",
          "arguments": {"project": "ProjectX"}
        }

[5] MCP Client Routing
    └─> MCPClient.call_tool()
        └─> Identifies tool belongs to azure_boards server
        └─> Routes to HTTP endpoint: http://127.0.0.1:8001/mcp

[6] MCP Server Processing
    └─> Azure Boards Server receives request
        └─> Executes get_active_work_items("ProjectX")
        └─> Constructs WIQL query
        └─> Calls Azure DevOps API

[7] External API Call
    └─> GET https://dev.azure.com/{org}/{project}/_apis/wit/wiql
        └─> Authentication: Basic {PAT}
        └─> Returns work item IDs

[8] Data Enrichment
    └─> Fetch detailed work item information
        └─> GET .../workitems?ids=1,2,3
        └─> Extract: ID, title, state, assignee, type

[9] Response to Client
    └─> {
          "count": 3,
          "items": [
            {"id": 1, "title": "Fix bug", "state": "Active", ...},
            {"id": 2, "title": "Add feature", "state": "Active", ...}
          ]
        }

[10] Agent Processing
     └─> LLM receives tool result
     └─> Synthesizes natural language response
     └─> Updates conversation memory

[11] User Output
     └─> "There are 3 active work items in ProjectX:
          1. Fix bug (Active, assigned to John)
          2. Add feature (Active, assigned to Jane)
          3. Update docs (Active, unassigned)"
```

### 6.2 Multi-Server Orchestration Example

**Complex Query:** "Compare the latest commits in the backend repository with the current sprint's work items"

**Orchestration Flow:**

```
[Agent Decision]
├─> Need repository data → Azure Repos Server
│   └─> get_latest_commits(repository="backend", branch="main")
│
└─> Need sprint data → Azure Boards Server
    └─> query_work_items(project="MyProject", wiql="...")

[Parallel Execution]
├─> HTTP Request to Port 8002 (Repos)
│   └─> Returns: 5 recent commits with messages
│
└─> HTTP Request to Port 8001 (Boards)
    └─> Returns: 12 work items in current sprint

[Agent Synthesis]
└─> Correlates commit messages with work item titles
    └─> Identifies completed work
    └─> Identifies pending work
    └─> Generates summary report
```

### 6.3 Communication Protocols

**HTTP Transport (Azure Servers):**

**Request Format:**
```json
POST http://127.0.0.1:8001/mcp
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_active_work_items",
    "arguments": {
      "project": "ProjectX"
    }
  },
  "id": 1
}
```

**Response Format:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "count": 3,
    "items": [...]
  },
  "id": 1
}
```

**STDIO Transport (Terminal Server):**

**Communication via standard input/output streams:**
```
Client → Server: JSON-RPC message via stdin
Server → Client: JSON-RPC response via stdout
```

**Advantages:**
- Low latency (same process)
- No network overhead
- Simple process lifecycle

### 6.4 Error Propagation

**Error Flow:**

```
[Azure API Error]
└─> HTTP 404 or 500
    └─> azure_request() catches exception
        └─> Returns: {"error": "Resource not found"}
            └─> MCP Server returns error in response
                └─> MCP Client receives error
                    └─> Agent receives error as tool result
                        └─> LLM explains error to user
```

**User-Friendly Error Handling:**
- Raw errors transformed into explanations
- Agent provides context and suggestions
- Conversation continues despite errors

---

## 7. Implementation Details

### 7.1 Configuration Management

**MCP Configuration File (mcp.json):**

```json
{
  "mcpServers": {
    "azure_boards": {
      "transport": "http",
      "url": "http://127.0.0.1:8001/mcp"
    },
    "azure_repos": {
      "transport": "http",
      "url": "http://127.0.0.1:8002/mcp"
    },
    "smart_terminal": {
      "transport": "stdio",
      "command": "python",
      "args": ["server/smart_terminal_server.py"]
    }
  }
}
```

**Configuration Properties:**

- **transport:** Protocol type (http or stdio)
- **url:** HTTP endpoint for remote servers
- **command:** Executable for STDIO servers
- **args:** Arguments passed to STDIO server process

**Environment Configuration (.env):**

```
GROQ_API_KEY=gsk_...
AZURE_ORG=your-organization
AZURE_PROJECT=your-project
AZURE_PAT=your-personal-access-token
```

### 7.2 Authentication Flow

**Groq Authentication:**
```python
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)
# API key loaded automatically from GROQ_API_KEY env var
```

**Azure DevOps Authentication:**
```python
response = requests.request(
    method,
    url,
    auth=HTTPBasicAuth("", AZURE_PAT),
    timeout=15
)
```

**Pattern:** Empty username + PAT as password  
**Security:** PAT never logged or displayed

### 7.3 Conversation Memory Implementation

**Memory Structure:**
```python
# Inside MCPAgent
conversation_history = [
    {"role": "user", "content": "What active work items exist?"},
    {"role": "assistant", "content": "There are 3 active items..."},
    {"role": "user", "content": "Who is assigned to item 2?"},
    {"role": "assistant", "content": "Item 2 is assigned to Jane..."}
]
```

**Benefits:**
- Context preservation across turns
- Follow-up question handling
- Pronoun resolution ("it", "that item", "the same project")
- Natural conversation flow

**Memory Management:**
```python
agent.clear_conversation_history()  # Manual reset
# Or automatic based on max_steps limit
```

### 7.4 Reasoning Loop

**ReAct Pattern Implementation:**

```
THOUGHT: User wants to know active work items in ProjectX
ACTION: Call get_active_work_items with project="ProjectX"
OBSERVATION: Received 3 active items
THOUGHT: User might want details about specific items
ACTION: Return summary with item details
```

**Loop Termination Conditions:**
1. Satisfactory answer generated
2. max_steps (15) reached
3. No more applicable tools
4. Error that cannot be recovered

### 7.5 Error Handling Strategy

**Layered Error Handling:**

**Level 1 - Server:**
```python
def azure_request(method: str, url: str, **kwargs):
    try:
        response = requests.request(...)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
```

**Level 2 - Client:**
- Validates server responses
- Handles connection failures
- Manages timeouts

**Level 3 - Agent:**
```python
try:
    response = await agent.run(user_input)
    print(response)
except Exception as e:
    print(f"❌ Error: {e}")
```

**Level 4 - User Interface:**
- Displays errors in user-friendly format
- Maintains application stability
- Continues accepting input after errors

---

## 8. Use Case Scenarios

### 8.1 Sprint Planning Assistant

**Scenario:** Engineering manager needs sprint overview

**User Query:**
```
"What are the current epics and how many active work items 
do we have? Also check if there are any unassigned items."
```

**Agent Workflow:**
1. Calls `get_current_epics(project)`
2. Calls `get_active_work_items(project)`
3. Calls `get_unassigned_work_items(project)`
4. Synthesizes summary with counts and recommendations

**Output:**
```
Sprint Overview for ProjectX:

Current Epics (3):
1. User Authentication System
2. Payment Integration
3. Mobile App Development

Active Work Items: 24
- 18 assigned
- 6 unassigned (need attention)

Recommendation: Assign the 6 unassigned items before 
sprint planning to ensure balanced workload.
```

### 8.2 Code Review Monitor

**Scenario:** Team lead wants PR status update

**User Query:**
```
"Show me all active pull requests in the backend 
repository and the recent commits on main branch"
```

**Agent Workflow:**
1. Calls `list_pull_requests(repository="backend")`
2. Calls `get_latest_commits(repository="backend", branch="main")`
3. Correlates information
4. Highlights pending reviews

**Output:**
```
Backend Repository Status:

Active Pull Requests (4):
1. "Add authentication middleware" by John (PR #45)
2. "Fix database connection leak" by Sarah (PR #46)
3. "Update API documentation" by Mike (PR #47)
4. "Optimize query performance" by Lisa (PR #48)

Recent Main Branch Commits (5):
1. "Merge PR #44: Add logging" - 2 hours ago
2. "Fix typo in README" - 5 hours ago
3. "Update dependencies" - 1 day ago
...

Note: 4 PRs awaiting review. Consider prioritizing PR #46 
(bug fix) for immediate review.
```

### 8.3 System Diagnostics

**Scenario:** DevOps engineer troubleshooting port conflicts

**User Query:**
```
"Check if ports 8001 and 8002 are in use, and if so, 
tell me which processes are using them"
```

**Agent Workflow:**
1. Calls `check_port(8001)`
2. Calls `check_port(8002)`
3. If ports open, calls `who_is_using_port(8001)`
4. Calls `who_is_using_port(8002)`
5. Provides diagnostic information

**Output:**
```
Port Status:

Port 8001: OPEN
  └─> Process: python.exe (PID: 12345)
      Command: python azure_boards_server.py

Port 8002: OPEN
  └─> Process: python.exe (PID: 12346)
      Command: python azure_repos_server.py

Both ports are occupied by your MCP servers, which is expected.
```

### 8.4 Multi-System Investigation

**Scenario:** Product owner investigating feature status

**User Query:**
```
"Find work item #1234, show its comments, then check 
if there are any recent commits related to it in the 
frontend repository"
```

**Agent Workflow:**
1. Calls `query_work_items()` to get work item #1234 details
2. Calls `get_work_item_comments(work_item_id=1234)`
3. Extracts feature name from work item
4. Calls `get_latest_commits(repository="frontend")`
5. Searches commit messages for feature reference
6. Synthesizes timeline of feature development

**Output:**
```
Work Item #1234: "Implement dark mode toggle"
Status: Active
Assigned: UI Team

Recent Discussion (3 comments):
1. PM: "Can we have this ready by Friday?"
2. Developer: "Working on it, 80% complete"
3. Designer: "Icons ready for dark theme"

Related Commits in Frontend:
1. "Add dark mode CSS variables" - 1 day ago
2. "Implement theme toggle component" - 2 days ago
3. "Update color palette for dark mode" - 3 days ago

Progress: Development ongoing, recent activity indicates 
work is on track for completion.
```

---

## 9. Deployment Considerations

### 9.1 Deployment Architecture

**Local Development Setup:**
```
Project Root/
├── client.py                    # Main application entry
├── config/
│   └── mcp.json                 # Server configuration
├── server/
│   ├── azure_boards_server.py   # HTTP server (8001)
│   ├── azure_repos_server.py    # HTTP server (8002)
│   └── smart_terminal_server.py # STDIO server
├── .env                         # Environment variables (gitignored)
└── requirements.txt             # Python dependencies
```

**Startup Sequence:**
1. Start Azure Boards server: `python server/azure_boards_server.py`
2. Start Azure Repos server: `python server/azure_repos_server.py`
3. Run main client: `python client.py`
   - Client automatically spawns smart_terminal server via STDIO

### 9.2 Production Considerations

**Scalability:**
- HTTP servers can be deployed independently
- Load balancing possible for HTTP endpoints
- Multiple client instances can share servers
- Horizontal scaling of MCP servers supported

**Security:**
- All secrets in environment variables
- PAT rotation policy required
- HTTPS for production Azure endpoints
- Network isolation for terminal server

**Monitoring:**
- Log all tool invocations
- Track API rate limits (Azure DevOps)
- Monitor server health endpoints
- Conversation metrics (average steps, success rate)

**High Availability:**
- Health checks for HTTP servers
- Automatic restart for STDIO processes
- Graceful degradation if servers unavailable
- Circuit breaker pattern for external APIs

### 9.3 Environment Requirements

**Python Version:** 3.8+

**Network Requirements:**
- Internet access for Groq API
- Internet access for Azure DevOps API
- Local ports 8001, 8002 available
- Firewall rules for outbound HTTPS

**System Requirements:**
- Minimum 4GB RAM (LLM operations)
- Local file system read access
- Python subprocess support

### 9.4 Configuration Best Practices

**Security:**
```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use strong PAT with minimal permissions
# Principle: Read-only access where possible
```

**Reliability:**
```python
# Implement timeout for all external calls
timeout=15  # seconds

# Retry logic for transient failures
max_retries=3
```

**Monitoring:**
```python
# Add logging throughout
import logging
logging.basicConfig(level=logging.INFO)
logger.info(f"Tool called: {tool_name}")
```

### 9.5 Troubleshooting Guide

**Common Issues:**

**Issue 1: GROQ_API_KEY not found**
- Solution: Verify .env file exists and contains GROQ_API_KEY

**Issue 2: Azure API 401 Unauthorized**
- Solution: Check PAT expiration, regenerate if needed

**Issue 3: Port already in use**
- Solution: Use `who_is_using_port()` to identify process, terminate if necessary

**Issue 4: STDIO server not responding**
- Solution: Check server file path in mcp.json, ensure Python executable is correct

**Issue 5: Agent timeout (max_steps reached)**
- Solution: Simplify query or increase max_steps parameter

---

## Conclusion

This Agentic AI application demonstrates a production-ready implementation of the Model Context Protocol for enterprise IT operations. The architecture successfully integrates multiple backend systems through a unified intelligent interface, enabling complex multi-step reasoning and natural language interaction.

**Key Achievements:**
- ✅ Full MCP specification compliance
- ✅ Multi-server orchestration with mixed transports
- ✅ Enterprise-grade security and error handling
- ✅ Conversation memory and context management
- ✅ Extensible, maintainable architecture

**Future Enhancements:**
- Add more MCP servers (Jira, Slack, GitHub)
- Implement caching layer for frequent queries
- Add streaming responses for real-time feedback
- Build web UI alongside CLI interface
- Implement role-based access control
- Add comprehensive test suite

---

**Document Version:** 1.0  
**Last Updated:** March 2026  
**Author:** Technical Documentation Team
