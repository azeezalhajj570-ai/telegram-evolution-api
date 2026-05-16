# Feature Specification: Horizontal Scaling

**Feature Branch**: `007-horizontal-scaling`

**Created**: 2026-05-16

**Status**: Draft

**Input**: User description: "Prepare the Telegram Evolution API for horizontal scaling across multiple API and worker nodes: distributed locks, instance ownership, heartbeats, node registry, failover, safe reconnect."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Instance Ownership Lock (Priority: P1)

As a platform operator, I want each Telegram instance to be owned by exactly one node at a time so that multiple containers do not create duplicate connections.

**Why this priority**: Preventing duplicate connections is the core requirement for safe horizontal scaling.

**Independent Test**: Can be tested by starting two application nodes, verifying each claims its assigned instances, and confirming the same instance never appears connected on both nodes.

**Acceptance Scenarios**:

1. **Given** two application nodes, **When** they both start and attempt to claim instance ownership, **Then** each instance is owned by exactly one node.
2. **Given** a node owns an instance, **When** another node attempts to acquire the same lock, **Then** it receives a "lock_held" error and does not start a Telethon client.
3. **Given** an instance ownership lock, **When** it is inspected in Redis, **Then** it contains the node ID, acquired timestamp, and TTL.
4. **Given** a node is shut down gracefully, **When** it releases its locks, **Then** the instances become available for other nodes to claim.

---

### User Story 2 - Heartbeat & Node Registry (Priority: P1)

As a platform operator, I want nodes to announce their presence via heartbeats so that the system can detect and recover from node failures.

**Why this priority**: Failure detection is essential for automated recovery.

**Independent Test**: Can be tested by starting a node, verifying it registers in the node registry with a heartbeat, then killing it and confirming the heartbeat expires and the node is marked dead.

**Acceptance Scenarios**:

1. **Given** a running node, **When** it starts, **Then** it registers in Redis with its node ID, hostname, start time, and an initial heartbeat timestamp.
2. **Given** a registered node, **When** its heartbeat interval elapses, **Then** the heartbeat timestamp is updated automatically.
3. **Given** a node crash, **When** the heartbeat expires (no update for 3 intervals), **Then** the node is considered dead and its instances can be reassigned.
4. **Given** a registered node, **When** I query the node registry, **Then** all active nodes are listed with their status and claimed instance count.

---

### User Story 3 - Worker Sharding (Priority: P2)

As a platform operator, I want message queue workers to be sharded across nodes so that each node processes jobs for the instances it owns.

**Why this priority**: Worker sharding prevents two nodes from processing the same queued job.

**Independent Test**: Can be tested by queueing messages on two instances owned by different nodes and verifying each node only processes jobs for its own instances.

**Acceptance Scenarios**:

1. **Given** a node that owns instance A, **When** a message is queued for instance A, **Then** the worker on that node processes it.
2. **Given** a node that does not own instance B, **When** a message is queued for instance B, **Then** the worker on that node skips it.
3. **Given** a node is shut down, **When** its instances are reassigned, **Then** the queued messages for those instances are processed by the new owning node.

---

### User Story 4 - Safe Reconnect & Graceful Handoff (Priority: P2)

As a platform operator, I want instance ownership to transfer cleanly between nodes without disrupting active message delivery.

**Why this priority**: Clean handoff prevents message loss during scaling events.

**Independent Test**: Can be tested by scaling down from 3 nodes to 2, verifying instances are reassigned, and confirming no messages are lost during the transition.

**Acceptance Scenarios**:

1. **Given** a shutdown signal, **When** a node receives it, **Then** it disconnects Telethon clients, releases instance locks, updates heartbeat to "shutting_down", and waits for inflight sends to complete (with timeout).
2. **Given** a node in "shutting_down" status, **When** another node detects the expired heartbeat, **Then** it acquires the lock and starts a Telethon client for each instance.
3. **Given** an instance claimed by a new node, **When** it connects, **Then** Telegram handles the old session invalidation and the new client takes over.
4. **Given** an inflight message during handoff, **When** the sending node dies, **Then** the message is retried by the queue worker on the new owning node.

---

### Edge Cases

- What happens when two nodes acquire the same lock simultaneously? Redis atomic SET NX ensures only one succeeds.
- What happens when a lock expires while the owning node is still alive? The node renews the lock periodically (auto-renewal).
- What happens when a node cannot reach Redis? It stops processing and enters a "degraded" state.
- What happens when the network partitions? Nodes that cannot renew locks release them; surviving nodes acquire them.
- What happens when all nodes crash? Instances remain disconnected; on restart, nodes re-acquire locks and reconnect.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST use Redis distributed locks (SET NX + TTL) for instance ownership.
- **FR-002**: Each instance lock MUST have a configurable TTL (default 30 seconds).
- **FR-003**: The system MUST auto-renew instance locks before TTL expiry (renewal at 1/3 TTL).
- **FR-004**: The system MUST maintain a node registry in Redis with heartbeat updates.
- **FR-005**: Node heartbeats MUST update every 10 seconds with a 30-second expiry.
- **FR-006**: The system MUST support querying the node registry for all active nodes.
- **FR-007**: Queue workers MUST only process jobs for instances owned by their node.
- **FR-008**: On graceful shutdown, the system MUST release all locks, disconnect clients, and update node status.
- **FR-009**: On detecting a dead node (expired heartbeat), surviving nodes MAY claim its orphaned instances.
- **FR-010**: The system MUST handle lock acquisition failures gracefully without crashing.

### Key Entities

- **InstanceLock**: A Redis key holding the owning node ID and acquired timestamp. TTL is auto-renewed. Format: `lock:instance:{instance_id}`.
- **NodeRegistration**: A Redis hashset entry for each active node. Fields: node_id, hostname, start_time, last_heartbeat, status (active/shutting_down/dead), claimed_instance_count.
- **HeartbeatMonitor**: Background task that periodically checks for expired heartbeats and reassigns orphaned instances.

## Success Criteria *(mandatory)*

- **SC-001**: Two nodes can each claim and maintain ownership of 10 instances without conflicts.
- **SC-002**: A node crash is detected within 30 seconds and its instances are reassigned within 10 seconds after detection.
- **SC-003**: Zero duplicate Telethon connections for the same instance across any number of nodes.
- **SC-004**: Graceful shutdown of a node completes within 10 seconds and releases all locks.
- **SC-005**: The node registry correctly reflects active nodes and their claimed instances at all times.
- **SC-006**: Lock acquisition overhead adds less than 5ms to instance connection time.

## Assumptions

- Redis is the single source of truth for instance ownership.
- Clock skew between nodes is minimal (< 1 second). All nodes use NTP.
- Telethon client disconnect is safe to call if the client is already disconnected.
- Session strings can be decrypted by any node (all nodes share the encryption key).
- The maximum number of concurrent nodes is 100 (well within Redis's capability).
- Node IDs are UUIDs generated at startup.
- Instance counts per node are balanced; this phase does not include automatic rebalancing.
