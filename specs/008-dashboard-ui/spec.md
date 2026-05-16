# Feature Specification: Dashboard UI

**Feature Branch**: `008-dashboard-ui`

**Created**: 2026-05-16

**Status**: Draft

**Input**: User description: "Build a web dashboard for the Telegram Evolution API using Next.js, TypeScript, Tailwind CSS, and shadcn/ui to manage instances, webhooks, API keys, and usage visually."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authentication & Organization Switching (Priority: P1)

As a user, I want to log in to the dashboard and switch between organizations so that I can manage my Team's Telegram infrastructure from a single dashboard.

**Why this priority**: Auth is the first thing every user needs.

**Independent Test**: Can be tested by logging in with valid credentials, seeing the organization switcher, switching orgs, and verifying the dashboard content updates for the selected organization.

**Acceptance Scenarios**:

1. **Given** valid credentials, **When** I log in, **Then** I am redirected to the dashboard with my default organization selected.
2. **Given** I belong to multiple organizations, **When** I use the organization switcher, **Then** the dashboard content updates to reflect the selected org.
3. **Given** invalid credentials, **When** I attempt to log in, **Then** I see an error message and remain on the login page.
4. **Given** no active session, **When** I navigate to any dashboard page, **Then** I am redirected to the login page.

---

### User Story 2 - Instance Management UI (Priority: P1)

As a user, I want to view, create, and manage my Telegram instances visually so that I don't need to use curl for common operations.

**Why this priority**: Instance management is the primary dashboard use case.

**Independent Test**: Can be tested by creating a new instance via the UI, seeing it appear in the instance list, clicking into its detail page, and performing actions like connect/disconnect.

**Acceptance Scenarios**:

1. **Given** the dashboard, **When** I view the instance list, **Then** I see all instances with their status, phone number, and connection state.
2. **Given** the instance list, **When** I click "Create Instance", **Then** a modal or form appears and I can create a new instance.
3. **Given** an instance in the list, **When** I click on it, **Then** I navigate to a detail page showing the instance status, webhook config, and recent activity.
4. **Given** the instance detail page, **When** I click "Connect" or "Disconnect", **Then** the instance status updates without a page reload.

---

### User Story 3 - Telegram Login Flow UI (Priority: P2)

As a user, I want a guided UI for the Telegram authentication flow so that I can authenticate instances without reading API docs.

**Why this priority**: The auth flow is complex; a guided UI dramatically improves the developer experience.

**Independent Test**: Can be tested by creating an instance, clicking "Authenticate", entering a phone number, receiving an OTP prompt, entering the code, and seeing the instance status change to "connected".

**Acceptance Scenarios**:

1. **Given** an unauthenticated instance, **When** I click "Authenticate", **Then** a step-by-step wizard guides me through phone number entry, OTP verification, 2FA (if needed), and connection.
2. **Given** the phone number step, **When** I enter a valid number, **Then** the UI advances to the OTP code input.
3. **Given** the OTP step, **When** I enter the correct code, **Then** the instance status updates to "connected" or prompts for 2FA.
4. **Given** the 2FA step, **When** I enter the password, **Then** the instance connects and the wizard completes.
5. **Given** any auth step fails, **When** I get an error, **Then** the UI shows a clear error message and allows retry.

---

### User Story 4 - Webhook & API Key Management (Priority: P2)

As a user, I want to configure webhooks and manage API keys through the UI so that I can set up integrations visually.

**Why this priority**: Webhooks and API keys are common configuration tasks.

**Independent Test**: Can be tested by configuring a webhook URL for an instance, then viewing the webhook config, then managing API keys (create and delete), and verifying the changes take effect.

**Acceptance Scenarios**:

1. **Given** an instance detail page, **When** I navigate to the webhook section, **Then** I can view, create, or delete the webhook URL.
2. **Given** the webhook section, **When** I click "Test", **Then** a test webhook is sent and the result is displayed.
3. **Given** the API keys page, **When** I create a new API key, **Then** the full key is shown once with a copy button.
4. **Given** the API keys page, **When** I view existing keys, **Then** the full key is masked (only last 4 characters visible).
5. **Given** the API keys page, **When** I delete a key, **Then** I am prompted for confirmation before deletion.

---

### User Story 5 - Usage & Activity Monitoring (Priority: P3)

As a user, I want to see message logs, webhook delivery logs, and usage statistics so that I can monitor my application's activity.

**Why this priority**: Usage monitoring enhances the dashboard but is not essential for core management.

**Independent Test**: Can be tested by sending messages via the API, then viewing the message logs in the dashboard and verifying they appear with correct timestamps.

**Acceptance Scenarios**:

1. **Given** message activity, **When** I view the message logs page, **Then** recent messages are displayed with timestamp, chat, status, and content preview.
2. **Given** webhook activity, **When** I view the webhook delivery logs, **Then** recent deliveries are displayed with status, attempt count, and response code.
3. **Given** the usage dashboard, **When** I view it, **Then** charts show messages sent, webhooks delivered, and active instances over time.
4. **Given** the usage dashboard, **When** I am near my quota limit, **Then** a warning indicator is displayed.

---

### Edge Cases

- What happens when the backend API is unreachable? The dashboard shows a connection error with a retry button.
- What happens when a user navigates to a deleted instance's detail page? A 404 page is displayed with a link back to the instance list.
- What happens when an API key creation fails? The error is displayed and the form remains filled for retry.
- What happens during the Telegram auth flow if the user navigates away? The flow state is preserved; they can return and continue.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The dashboard MUST have a login page that authenticates against the backend.
- **FR-002**: The dashboard MUST support organization switching.
- **FR-003**: The dashboard MUST display a list of instances with status indicators.
- **FR-004**: The dashboard MUST support creating new instances via a form/modal.
- **FR-005**: The dashboard MUST have an instance detail page with connection controls.
- **FR-006**: The dashboard MUST have a guided UI for the Telegram authentication flow.
- **FR-007**: The dashboard MUST support webhook CRUD operations.
- **FR-008**: The dashboard MUST support API key creation and deletion.
- **FR-009**: The dashboard MUST mask API keys after creation (show full key once, then mask).
- **FR-010**: The dashboard MUST display message logs and webhook delivery logs.
- **FR-011**: The dashboard MUST display usage statistics.
- **FR-012**: The dashboard MUST handle API errors gracefully with user-friendly messages.
- **FR-013**: The dashboard MUST use Next.js, TypeScript, Tailwind CSS, and shadcn/ui.
- **FR-014**: The dashboard MUST never display Telegram session strings.

### Key Entities (Frontend)

- **Page**: Login, Dashboard (org switcher + instance list), Instance Detail, Auth Wizard, Webhook Config, API Keys, Message Logs, Usage.
- **Component**: InstanceCard, StatusBadge, AuthWizardStepper, WebhookForm, ApiKeyDisplay, UsageChart.
- **API Client**: Typed fetch wrapper that authenticates and handles errors.

## Success Criteria *(mandatory)*

- **SC-001**: A user can log in, see their instances, create a new one, authenticate it, configure webhooks, and manage API keys — all without leaving the browser.
- **SC-002**: The Telegram auth wizard reduces the time to authenticate an instance from 5 minutes (curl) to under 1 minute.
- **SC-003**: API keys are masked everywhere except the one-time creation modal.
- **SC-004**: All pages load in under 2 seconds on a fast connection.
- **SC-005**: Error states (network failure, 4xx, 5xx) display user-friendly messages with recovery actions.

## Assumptions

- Backend APIs are already implemented (Phases 1-7).
- Authentication uses a JWT-based flow (Phase 5 user auth).
- The dashboard is a separate Next.js application in a `dashboard/` directory.
- shadcn/ui components are installed via `npx shadcn-ui@latest init`.
- The dashboard communicates with the backend via a typed API client.
- The login flow redirects to an OAuth provider or uses email/password against the backend.
- No real-time updates — data refreshes on page load or manual refresh.
- Mobile responsive design is desired but not required for MVP.
