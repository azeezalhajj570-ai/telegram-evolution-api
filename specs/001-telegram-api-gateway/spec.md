# Feature Specification: Telegram API Gateway

**Feature Branch**: `001-telegram-api-gateway`

**Created**: 2026-05-16

**Status**: Draft

**Input**: User description of self-hosted Telegram API Gateway with instance management, authentication, messaging, and webhooks.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Instance Creation and Authentication (Priority: P1)

As a developer, I want to create a Telegram account instance and authenticate it using my phone number so that the gateway can act on behalf of my Telegram account.

**Why this priority**: Without an authenticated instance, no Telegram operations are possible. This is the foundation of the entire system.

**Independent Test**: Can be fully tested by creating an instance, requesting a login code, submitting the OTP, and verifying the instance status changes to "connected".

**Acceptance Scenarios**:

1. **Given** no existing instances, **When** I create a new instance with a valid name, **Then** the system returns a unique instance ID and the instance status is "pending".
2. **Given** a pending instance, **When** I request a login code for a valid phone number, **Then** the system sends a Telegram login code to the phone and returns a success confirmation.
3. **Given** a login code was requested, **When** I submit the correct OTP code, **Then** the instance status changes to "authenticated" and a session is created.
4. **Given** the account has two-factor authentication enabled, **When** I submit a correct 2FA password after OTP verification, **Then** the instance status changes to "connected".
5. **Given** an incorrect OTP, **When** I submit it, **Then** the system returns an error and the instance remains in its current state.
6. **Given** an authenticated instance, **When** I disconnect it, **Then** the instance status changes to "disconnected" but the session is preserved.

---

### User Story 2 - Sending Messages via API (Priority: P1)

As a developer, I want to send a Telegram message to any chat through a simple API call so that my application can send notifications, alerts, or messages programmatically.

**Why this priority**: Sending messages is the primary action developers need from the gateway.

**Independent Test**: Can be fully tested by authenticating an instance and sending a text message to a known chat, then verifying delivery.

**Acceptance Scenarios**:

1. **Given** a connected instance, **When** I send a text message to a valid chat ID, **Then** the message is delivered and the system returns a success response with the message ID.
2. **Given** a connected instance, **When** I send a message to an invalid chat ID, **Then** the system returns an error indicating the chat was not found.
3. **Given** a disconnected instance, **When** I attempt to send a message, **Then** the system returns an error indicating the instance is not connected.
4. **Given** Telegram returns a rate-limit error (FloodWait), **When** I send a message, **Then** the system returns the retry-after duration to the caller without crashing.

---

### User Story 3 - Incoming Message Webhooks (Priority: P2)

As a developer, I want to receive incoming Telegram messages as HTTP webhooks to my application so that I can react to messages in real time.

**Why this priority**: Real-time message reception enables interactive applications. It is core functionality but requires instance authentication and sending to be complete first.

**Independent Test**: Can be fully tested by configuring a webhook URL, having a second account send a message to the authenticated account, and verifying the webhook is delivered to a test endpoint.

**Acceptance Scenarios**:

1. **Given** a connected instance, **When** I configure a webhook URL for it, **Then** the system stores the configuration and returns a success response.
2. **Given** an instance with a configured webhook, **When** a new message arrives for that instance, **Then** the system sends a webhook payload with the message data to the configured URL.
3. **Given** an instance with a configured webhook, **When** the webhook delivery fails, **Then** the system retries delivery up to a configured maximum number of attempts.
4. **Given** a connected instance, **When** I retrieve the webhook configuration, **Then** the system returns the configured URL and settings.
5. **Given** an instance with a configured webhook, **When** I delete the webhook configuration, **Then** the system stops sending webhooks for that instance.

---

### User Story 4 - Chat and Message Management (Priority: P3)

As a developer, I want to list my Telegram chats and read recent messages so that I can browse conversations and integrate chat data into my application.

**Why this priority**: Chat management adds significant value but is secondary to sending and receiving messages.

**Independent Test**: Can be fully tested by authenticating an instance, listing chats, and fetching messages from a specific chat.

**Acceptance Scenarios**:

1. **Given** a connected instance, **When** I request the list of chats, **Then** the system returns all dialogs including chats, groups, and channels with metadata.
2. **Given** a connected instance with messages in a chat, **When** I request recent messages for that chat, **Then** the system returns messages with sender, content, and timestamps.
3. **Given** a connected instance with an empty chat, **When** I request recent messages, **Then** the system returns an empty list.
4. **Given** a disconnected instance, **When** I request chats or messages, **Then** the system returns an error indicating the instance is not connected.

---

### Edge Cases

- What happens when the Telegram account is already logged in elsewhere? The session may be invalidated — the gateway detects this and marks the instance as "auth_required".
- How does the system handle a phone number that is already registered with Telegram but not on this gateway? It proceeds with normal OTP authentication.
- What happens when two API requests try to use the same instance simultaneously? The system queues requests per instance and processes them sequentially.
- How does the system handle a Telegram server outage? Connection attempts fail gracefully with a clear error message and the instance remains in its current state.
- What happens when the database is unreachable? All API calls fail with a service unavailable error.
- How are concurrent instance creation requests with the same phone number handled? The system returns the existing instance if one already exists for that number.
- What happens when webhook delivery repeatedly fails? After exhausting retries, the system logs the failure and stops retrying.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow developers to create Telegram account instances with a unique identifier and human-readable name.
- **FR-002**: The system MUST allow developers to list all instances they have created.
- **FR-003**: The system MUST allow developers to retrieve details of a specific instance.
- **FR-004**: The system MUST allow developers to delete an instance and all associated data.
- **FR-005**: The system MUST initiate Telegram authentication by sending a login code to a provided phone number.
- **FR-006**: The system MUST verify an OTP code submitted against a pending authentication.
- **FR-007**: The system MUST accept a 2FA password if Telegram requires it after OTP verification.
- **FR-008**: The system MUST persist authenticated Telegram sessions so they survive service restarts.
- **FR-009**: The system MUST allow developers to connect a previously authenticated instance.
- **FR-010**: The system MUST allow developers to disconnect a connected instance without losing its session.
- **FR-011**: The system MUST send a text message from a connected instance to a specified chat.
- **FR-012**: The system MUST list all chats (dialogs) for a connected instance.
- **FR-013**: The system MUST return recent messages from a specified chat for a connected instance.
- **FR-014**: The system MUST listen for incoming Telegram messages on connected instances in real time.
- **FR-015**: The system MUST deliver incoming messages to a configured webhook URL.
- **FR-016**: The system MUST allow developers to configure, read, and delete webhook URLs per instance.
- **FR-017**: The system MUST sign webhook payloads so the receiving application can verify authenticity.
- **FR-018**: The system MUST retry failed webhook deliveries with exponential backoff.
- **FR-019**: The system MUST protect all API endpoints with authentication using API keys.
- **FR-020**: The system MUST report instance connection status: pending, authenticated, connected, disconnected, error.
- **FR-021**: The system MUST handle Telegram rate-limit errors gracefully and report the required wait time to the caller.
- **FR-022**: The system MUST protect session data so that it cannot be read even if the database is compromised.
- **FR-023**: The system MUST prevent sensitive authentication data (OTP codes, passwords, session secrets, API keys) from appearing in logs.
- **FR-024**: The system MUST support running multiple instances concurrently with independent connections to Telegram.
- **FR-025**: The system MUST send a test webhook event so developers can verify their webhook endpoint is working.

### Key Entities

- **User**: A person or service that owns instances and API keys. Each user can have multiple instances.
- **API Key**: A secret token used to authenticate API requests. Each API key is associated with one user.
- **Instance**: A single Telegram account managed by the gateway. Contains authentication state, connection status, and an encrypted session.
- **Webhook**: A configuration linking an instance to an external URL where events are delivered. Each instance can have one webhook.
- **Webhook Delivery**: A record of a webhook event sent to a URL, including status, attempts, and response.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can create a new Telegram instance and complete the full authentication flow (phone → OTP → 2FA) in under 5 minutes.
- **SC-002**: An authenticated session survives a full service restart — the developer can send a message without re-authenticating.
- **SC-003**: A developer can send a text message through the API and have it arrive at the destination chat within 10 seconds.
- **SC-004**: An incoming Telegram message triggers a webhook delivery to the developer's configured URL within 15 seconds.
- **SC-005**: Five or more instances can be authenticated and connected simultaneously, each independently sending and receiving messages.
- **SC-006**: When Telegram enforces a rate limit, the gateway returns the required wait time to the caller and resumes normal operation without manual intervention.
- **SC-007**: A developer can configure, test, modify, and delete webhook settings without service disruption.
- **SC-008**: No authentication secrets (OTP codes, passwords, API keys, session data) appear in any log output during normal operation or error conditions.

## Assumptions

- Developers will use the gateway from their own server infrastructure with reliable internet connectivity.
- Each developer manages their own API keys — the system does not provide a user registration or key management UI in the MVP.
- The gateway runs in a trusted environment (the developer's own infrastructure).
- Telegram accounts used with the gateway are existing, valid Telegram accounts.
- The gateway interacts with personal Telegram user accounts, not Telegram Bot accounts.
- A single PostgreSQL database and single Redis instance are sufficient for MVP-scale deployments.
- Webhook receivers are expected to respond with HTTP 2xx to acknowledge receipt. Other status codes trigger retries.
- Phone number ownership is verified through Telegram's standard OTP flow — no additional verification is performed.
- The system does not provide message history or sync — it only captures messages received while the instance is connected.
