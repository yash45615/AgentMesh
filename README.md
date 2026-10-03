# AgentMesh

## Distributed AI Agent Runtime & Task Execution Platform

AgentMesh is a distributed AI-agent runtime designed to execute, schedule, monitor, and recover background agent tasks across multiple workers.

The platform combines **FastAPI, PostgreSQL, Redis, multi-worker execution, agent runtime orchestration, retries, timeouts, heartbeats, observability, SLO monitoring, chaos testing, load testing, and CI/CD** into a single backend system.

The primary goal is to demonstrate how AI-agent workloads can be engineered as a reliable distributed system rather than running entirely inside a single API process.

---

## Architecture

```text
                         ┌──────────────────────┐
                         │      Client / User   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │                      │
                         │ Authentication       │
                         │ Agent Management     │
                         │ Task Management      │
                         │ Health / Metrics     │
                         └──────────┬───────────┘
                                    │
                 ┌──────────────────┴──────────────────┐
                 │                                     │
                 ▼                                     ▼
        ┌─────────────────┐                  ┌──────────────────┐
        │   PostgreSQL    │                  │  Agent Control   │
        │                 │                  │      Plane       │
        │ Users           │                  └────────┬─────────┘
        │ Agents          │                           │
        │ Tasks           │                           ▼
        │ Workers         │                  ┌──────────────────┐
        └─────────────────┘                  │ Task Scheduler   │
                                             └────────┬─────────┘
                                                      │
                                                      ▼
                                             ┌──────────────────┐
                                             │ Redis / Memurai  │
                                             │    Task Queue    │
                                             └────────┬─────────┘
                                                      │
                           ┌──────────────────────────┼──────────────────────────┐
                           │                          │                          │
                           ▼                          ▼                          ▼
                    ┌──────────────┐           ┌──────────────┐           ┌──────────────┐
                    │   Worker 1   │           │   Worker 2   │           │   Worker N   │
                    └──────┬───────┘           └──────┬───────┘           └──────┬───────┘
                           │                          │                          │
                           └──────────────────────────┼──────────────────────────┘
                                                      ▼
                                           ┌─────────────────────┐
                                           │    Agent Runtime    │
                                           │                     │
                                           │ Model Gateway       │
                                           │ Tool Execution      │
                                           │ Retry / Timeout     │
                                           │ State Management    │
                                           └──────────┬──────────┘
                                                      │
                                                      ▼
                                           ┌─────────────────────┐
                                           │ Results & Metrics   │
                                           └─────────────────────┘
```

---

## Key Features

* FastAPI REST API
* JWT authentication
* User management
* Agent management
* Task management
* PostgreSQL persistence
* Redis-compatible task queue
* Multi-worker task execution
* Agent runtime
* Model gateway abstraction
* Task retries
* Execution timeouts
* Worker heartbeats
* Failure recovery
* Health monitoring
* Metrics
* SLO monitoring
* Chaos testing
* Load testing
* Benchmark comparison
* Automated testing with Pytest
* GitHub Actions CI/CD

---

## Technology Stack

| Technology      | Purpose                            |
| --------------- | ---------------------------------- |
| Python 3.10     | Application runtime                |
| FastAPI         | REST API                           |
| PostgreSQL      | Persistent database                |
| SQLAlchemy      | ORM and database access            |
| Redis / Memurai | Distributed task queue             |
| AsyncIO         | Asynchronous execution             |
| JWT             | Authentication                     |
| Pytest          | Automated testing                  |
| GitHub Actions  | CI/CD                              |
| PowerShell      | Windows development and automation |

---

## Core Workflow

A task follows this general lifecycle:

```text
Client
   │
   ▼
FastAPI
   │
   ▼
Create Task
   │
   ▼
PostgreSQL
   │
   ▼
Redis Queue
   │
   ▼
Worker
   │
   ▼
Agent Runtime
   │
   ▼
Model Gateway / Tools
   │
   ▼
Task Result
   │
   ▼
PostgreSQL
```

Task states are managed throughout execution:

```text
CREATED
   │
   ▼
QUEUED
   │
   ▼
RUNNING
   │
   ├──────────────► COMPLETED
   │
   ├──────────────► FAILED
   │
   ├──────────────► TIMEOUT
   │
   └──────────────► RETRY
                         │
                         └──────► QUEUED
```

---

# Authentication

AgentMesh uses JWT-based authentication.

Authentication flow:

```text
Register
   │
   ▼
Login
   │
   ▼
JWT Token
   │
   ▼
Authenticated API Request
```

Protected resources include agent and task operations.

---

# Agent Management

Agents represent configurable execution units.

An agent can define:

* Name
* Description
* Agent type
* Model
* System prompt
* Capabilities
* Allowed tools
* Maximum concurrent tasks
* Execution timeout

Example:

```json
{
  "name": "Research Agent",
  "agent_type": "research",
  "model": "model-gateway",
  "capabilities": {
    "research": true,
    "summarization": true
  },
  "max_concurrent_tasks": 5,
  "timeout_seconds": 300
}
```

---

# Task Management

Tasks represent units of work submitted to an agent.

A task contains information such as:

* Owner
* Agent
* Task type
* Input data
* Result
* Status
* Priority
* Retry count
* Maximum retries
* Timeout
* Error information
* Timestamps

Example lifecycle:

```text
Task Created
     │
     ▼
Queued
     │
     ▼
Worker Picks Task
     │
     ▼
Running
     │
     ├── Success ──► Completed
     │
     ├── Failure ──► Retry
     │
     └── Timeout ─► Retry / Failed
```

---

# Distributed Task Queue

Redis is used to decouple task submission from task execution.

```text
                    Redis Queue
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
       Worker 1      Worker 2      Worker N
```

The queue stores task identifiers instead of SQLAlchemy ORM objects.

This keeps queue messages simple, serializable, and independent of the database session.

---

# Multi-Worker Execution

AgentMesh supports multiple workers processing tasks concurrently.

Example:

```text
                  Redis
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
   Worker 1     Worker 2     Worker 3
       │            │            │
       ▼            ▼            ▼
    Task A        Task B        Task C
```

Each worker:

1. Registers itself
2. Sends heartbeats
3. Retrieves queued tasks
4. Executes tasks
5. Updates task state
6. Handles failures
7. Continues processing

---

# Worker Heartbeats

Workers periodically report their health.

Worker information includes:

```text
worker_id
status
current_task_id
last_heartbeat
registered_at
```

Example:

```text
Worker: e5d111ad-d25b-4fcc-aebd-3fc78743c90a
Status: active
Heartbeat: alive
```

Heartbeats provide the foundation for detecting worker failures.

---

# Retry & Timeout Handling

AgentMesh supports bounded task retries.

```text
                 Task
                   │
                   ▼
                Worker
                   │
            ┌──────┴──────┐
            │             │
         Success        Failure
            │             │
            ▼             ▼
        Completed       Retry?
                          │
                     ┌────┴────┐
                     │         │
                    Yes        No
                     │         │
                     ▼         ▼
                   Retry     Failed
```

Retries prevent temporary failures from immediately becoming permanent task failures.

Timeouts prevent tasks from consuming worker capacity indefinitely.

---

# Model Gateway

Agent execution is separated from model-provider implementation through a model gateway abstraction.

```text
Agent Runtime
      │
      ▼
Model Gateway
      │
      ├── Provider A
      ├── Provider B
      └── Local / Test Model
```

This allows model implementations to change without tightly coupling the worker execution engine to one specific provider.

---

# Failure Recovery

Distributed systems must handle failures as expected operational events.

AgentMesh considers failures such as:

* Worker termination
* Redis interruption
* Database interruption
* Task execution failure
* Task timeout
* Repeated task failure

The runtime maintains task state and worker state so failures can be detected and handled.

---

# Observability

AgentMesh exposes operational endpoints for monitoring the system.

```text
GET /health
GET /health/database
GET /health/redis
GET /metrics
GET /slo
```

These endpoints provide information about:

* API availability
* Database connectivity
* Redis connectivity
* Runtime metrics
* Service-level objectives

---

# SLO Monitoring

The SLO subsystem provides reliability measurements for the platform.

Relevant dimensions include:

```text
Availability
Task Success Rate
Task Failure Rate
Execution Latency
Worker Availability
Queue Health
```

The goal is to monitor the behavior of the complete distributed system rather than only the API response status.

---

# Chaos Testing

AgentMesh includes failure testing to validate distributed-system behavior.

Example worker failure:

```text
Worker 1 ───── X
              │
              ▼
          Worker stops

Worker 2 ───────────────► continues processing
```

Chaos scenarios include:

* Worker failure
* Redis failure
* Worker restart
* Queue recovery
* Task state verification
* Infrastructure recovery

Example workflow:

```text
1. Start Redis
2. Start multiple workers
3. Submit tasks
4. Stop one worker
5. Observe remaining workers
6. Stop Redis
7. Observe system behavior
8. Restart Redis
9. Restart workers if required
10. Verify task and database state
```

Chaos-test results are documented in:

```text
docs/chaos-testing.md
```

---

# Load Testing

AgentMesh contains a dedicated load-testing subsystem.

Example:

```powershell
python -m app.loadtest.run_benchmark --tasks 10 --workers 1
```

Another example:

```powershell
python -m app.loadtest.run_benchmark --tasks 100 --workers 4
```

Benchmark reports are stored under:

```text
artifacts/load_tests/
```

Example:

```text
artifacts/
└── load_tests/
    ├── benchmark_10_tasks_1_workers.json
    ├── benchmark_100_tasks_1_workers.json
    └── benchmark_100_tasks_4_workers.json
```

The benchmark system can be used to compare:

* Throughput
* Execution time
* Worker utilization
* Queue behavior
* Task completion
* Failure rate
* Scaling behavior

Actual benchmark measurements should be generated from the environment rather than manually entered.

---

# API Endpoints

## Authentication

```text
POST /auth/register
POST /auth/login
GET  /users/me
```

## Agents

```text
POST /agents
GET  /agents
GET  /agents/{agent_id}
```

## Tasks

```text
POST /tasks
GET  /tasks/{task_id}
```

## System

```text
GET /health
GET /health/database
GET /health/redis
GET /metrics
GET /slo
```

Interactive API documentation is available through FastAPI Swagger UI.

---

# Project Structure

```text
AgentMesh/
│
├── app/
│   │
│   ├── core/
│   │   ├── redis.py
│   │   └── ...
│   │
│   ├── db/
│   │   ├── models.py
│   │   └── ...
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── agent.py
│   │   ├── worker.py
│   │   └── task.py
│   │
│   ├── queue/
│   │   └── task_queue.py
│   │
│   ├── runtime/
│   │   └── agent_runtime.py
│   │
│   ├── loadtest/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── loadtest.py
│   │   ├── runtime.py
│   │   ├── run_benchmark.py
│   │   ├── compare_results.py
│   │   └── start_workers.ps1
│   │
│   ├── worker.py
│   ├── main.py
│   └── ...
│
├── artifacts/
│   └── load_tests/
│
├── docs/
│   └── chaos-testing.md
│
├── tests/
│   └── ...
│
├── .github/
│   └── workflows/
│
├── .env.example
├── requirements.txt
└── README.md
```

---

# Local Setup

## Requirements

Install the following:

* Python 3.10+
* PostgreSQL
* Redis-compatible server
* Git

For Windows, Memurai can be used as the Redis-compatible server.

---

## Clone Repository

```powershell
git clone https://github.com/yash45615/AgentMesh.git
cd AgentMesh
```

---

## Create Virtual Environment

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## Configure Environment

Create a local `.env` file based on:

```text
.env.example
```

Do not commit `.env` to GitHub.

---

# PostgreSQL Setup

Create the database:

```sql
CREATE DATABASE agentmesh_db;
```

Configure the database connection using the variables defined in `.env.example`.

---

# Redis / Memurai Setup

For Windows development with Memurai:

```powershell
Get-Service Memurai
```

Test the Redis-compatible server:

```powershell
& "C:\Program Files\Memurai\memurai-cli.exe" ping
```

Expected output:

```text
PONG
```

---

# Running the API

Start the FastAPI server:

```powershell
cd D:\AgentMesh
.\venv\Scripts\Activate.ps1

uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Running a Worker

Open another PowerShell terminal:

```powershell
cd D:\AgentMesh
.\venv\Scripts\Activate.ps1

python -m app.worker
```

A successful worker startup produces output similar to:

```text
Worker <worker-id> started.
[Heartbeat] Worker <worker-id> alive
```

Multiple worker instances can be started in separate terminals.

---

# Running a Load Test

Example:

```powershell
python -m app.loadtest.run_benchmark --tasks 20 --workers 2
```

For larger workloads:

```powershell
python -m app.loadtest.run_benchmark --tasks 100 --workers 4
```

Results are written to:

```text
artifacts/load_tests/
```

---

# Testing

Run the complete test suite:

```powershell
pytest -q
```

Compile the application:

```powershell
python -m compileall app
```

Verify the load-testing subsystem:

```powershell
python -c "from app.loadtest import config, runtime, loadtest, run_benchmark, compare_results; print('Load-test subsystem OK')"
```

---

# CI/CD

GitHub Actions is used to automate project validation.

The CI pipeline is designed to perform:

```text
Checkout
   │
   ▼
Python Setup
   │
   ▼
Dependency Installation
   │
   ▼
Compilation
   │
   ▼
Automated Tests
   │
   ▼
Build Validation
```

Workflow files are located under:

```text
.github/workflows/
```

---

# Security

The project follows basic application security practices:

* JWT authentication
* Environment-based configuration
* Secrets excluded from source control
* Protected API endpoints
* Bounded retries
* Execution timeouts
* Worker state tracking
* Controlled task execution

Never commit:

```text
.env
API keys
Database passwords
JWT secrets
Credentials
Private certificates
```

---

# Engineering Challenges

AgentMesh focuses on engineering problems encountered when building distributed AI systems.

## State Consistency

Task state exists across multiple components:

```text
PostgreSQL
Redis
Worker
Agent Runtime
```

The system must maintain a consistent view of task execution.

## Worker Failure

A worker can terminate while processing a task.

The platform therefore uses:

```text
Heartbeat
+
Task State
+
Timeout
+
Retry
+
Recovery
```

## Queue Reliability

Queue messages contain task identifiers instead of SQLAlchemy objects.

This keeps the queue independent from ORM session state.

## Concurrency

Multiple workers can process independent tasks simultaneously.

This allows the system to investigate the relationship between worker count, throughput, latency, and reliability.

---

# Validation Strategy

AgentMesh validates the platform across multiple dimensions:

```text
                    AgentMesh Validation
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
     Functional        Reliability       Performance
       Testing           Testing           Testing
          │                 │                 │
          ▼                 ▼                 ▼
       Pytest          Chaos Testing      Load Testing
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ▼
                       CI/CD Checks
```

---

# Project Roadmap

## Foundation

* [x] FastAPI
* [x] PostgreSQL
* [x] SQLAlchemy
* [x] Authentication

## Distributed Execution

* [x] Agent API
* [x] Task API
* [x] Redis queue
* [x] Multiple workers
* [x] Agent runtime

## Reliability

* [x] Model gateway
* [x] Retry handling
* [x] Timeouts
* [x] Worker heartbeats
* [x] Failure recovery

## Production Engineering

* [x] Security
* [x] Observability
* [x] SLO monitoring
* [ ] Chaos testing
* [ ] Load testing
* [ ] CI/CD

## Portfolio Release

* [ ] GitHub documentation
* [ ] Architecture diagrams
* [ ] Screenshots
* [ ] Benchmark results
* [ ] Final engineering documentation

---

# What This Project Demonstrates

AgentMesh demonstrates practical experience with:

* Distributed systems
* Backend engineering
* AI-agent infrastructure
* REST API design
* FastAPI
* PostgreSQL
* SQLAlchemy
* Redis
* Asynchronous programming
* Task queues
* Worker orchestration
* Concurrency
* Fault tolerance
* Retry strategies
* Timeout handling
* Health monitoring
* Observability
* SLO engineering
* Chaos engineering
* Performance benchmarking
* Automated testing
* CI/CD

---

# Future Improvements

Potential future extensions include:

* Kubernetes-based worker orchestration
* Horizontal worker autoscaling
* Distributed tracing
* Prometheus integration
* Grafana dashboards
* Dead-letter queues
* Priority-based scheduling
* Persistent event logs
* WebSocket task streaming
* Multi-tenant isolation
* Advanced model routing
* Cost-aware model selection
* Tool execution sandboxing

---

# Author

**Yash**

GitHub:
https://github.com/yash45615

---

## Project Objective

AgentMesh explores how AI-agent workloads can be engineered as a distributed runtime with an emphasis on:

```text
Reliability
Scalability
Concurrency
Fault Tolerance
Observability
Performance
Automation
```

The project focuses not only on AI model execution, but also on the infrastructure required to operate agent workloads reliably at scale.
