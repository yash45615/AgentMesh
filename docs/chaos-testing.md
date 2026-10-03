# AgentMesh Chaos Testing

## Objective

AgentMesh was tested under controlled infrastructure and worker failures
to verify failure detection, recovery, and continued operation.

## Tests

### 1. Worker Crash

- Started two workers.
- Submitted multiple benchmark tasks.
- Terminated one worker.
- Verified the remaining worker continued running.

### 2. Redis Failure

- Started AgentMesh workers.
- Verified Redis/Memurai availability.
- Stopped Memurai.
- Observed queue/infrastructure failure behavior.
- Restarted Memurai.
- Verified Redis availability was restored.
- Restarted/recovered workers as required.

### 3. Recovery

After restoring the failed dependency:

- Redis became reachable again.
- Workers were able to reconnect.
- AgentMesh resumed normal operation.

## Result

The chaos tests were used to validate AgentMesh behavior under
worker and queue-infrastructure failures.