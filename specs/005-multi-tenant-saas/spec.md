# Feature Specification: Multi-Tenant SaaS Layer

**Feature Branch**: `005-multi-tenant-saas`

**Created**: 2026-05-16

**Status**: Draft

**Input**: User description: "Convert the RelayStack API from single-owner MVP into a SaaS-ready multi-tenant platform with organizations, roles, scoped API keys, usage quotas, and audit logs."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Organization Management (Priority: P1)

As a platform operator, I want to create and manage organizations so that multiple teams can use the gateway independently.

**Why this priority**: Multi-tenancy is the core of the SaaS layer — everything else depends on orgs existing.

**Independent Test**: Can be tested by creating an organization, verifying it appears in the list, fetching its details, and confirming instances are isolated between organizations.

**Acceptance Scenarios**:

1. **Given** a platform admin, **When** I POST to `/organizations` with a name, **Then** a new organization is created with the caller as the owner.
2. **Given** an existing organization, **When** I GET `/organizations/{id}`, **Then** the response includes the org name, member count, current usage, and limits.
3. **Given** two organizations, **When** each creates an instance with the same name, **Then** both succeed and instances are isolated.
4. **Given** an organization member, **When** they list instances, **Then** they only see instances belonging to their organization.

---

### User Story 2 - Team Members & Roles (Priority: P1)

As an organization owner, I want to invite team members with specific roles so that I can delegate access securely.

**Why this priority**: Role-based access is essential for team collaboration.

**Independent Test**: Can be tested by inviting a member, verifying they can access org resources with their role permissions, and removing them to revoke access.

**Acceptance Scenarios**:

1. **Given** an org owner, **When** I POST to `/organizations/{id}/members` with a user email and role, **Then** the user is added as a member.
2. **Given** an org member with "viewer" role, **When** they attempt to create an instance, **Then** the API returns a 403 error.
3. **Given** an org member with "admin" role, **When** they manage instances, **Then** all management operations succeed.
4. **Given** an org owner, **When** I DELETE `/organizations/{id}/members/{user_id}`, **Then** the user is removed and loses access to org resources.

**Role Hierarchy**: `viewer < developer < admin < owner`

| Role | Read Instances | Write Instances | Manage Webhooks | Manage API Keys | Manage Members |
|------|---------------|----------------|----------------|----------------|----------------|
| viewer | ✅ | ❌ | ❌ | ❌ | ❌ |
| developer | ✅ | ✅ | ✅ | ❌ | ❌ |
| admin | ✅ | ✅ | ✅ | ✅ | ❌ |
| owner | ✅ | ✅ | ✅ | ✅ | ✅ |

---

### User Story 3 - Scoped API Keys & Usage Limits (Priority: P2)

As an organization admin, I want to create scoped API keys and enforce usage limits per organization so that I can control access and prevent abuse.

**Why this priority**: API key scopes and quotas are essential for production SaaS usage.

**Independent Test**: Can be tested by creating a read-only API key, verifying it cannot perform write operations, exhausting the monthly message quota, and confirming further sends are blocked.

**Acceptance Scenarios**:

1. **Given** an org admin, **When** I POST to `/organizations/{id}/api-keys` with a name and scopes, **Then** a new API key is returned (shown once).
2. **Given** a read-only API key, **When** I attempt to send a message, **Then** the API returns a 403 error.
3. **Given** an organization that has exceeded its monthly message quota, **When** any member sends a message, **Then** the API returns a 429 error with quota details.
4. **Given** an organization at its instance limit, **When** a member tries to create a new instance, **Then** the API returns a 429 error.
5. **Given** a deactivated API key, **When** I use it to authenticate, **Then** the API returns a 401 error.
6. **Given** an API key with "webhook:read" scope, **When** I GET the webhook config, **Then** it succeeds, but a PUT fails with 403.

---

### User Story 4 - Audit Logging (Priority: P3)

As a security-conscious organization owner, I want all sensitive actions logged so that I can review who did what and when.

**Why this priority**: Audit logging is important for compliance and security but can follow the core multi-tenant features.

**Independent Test**: Can be tested by performing several actions (create instance, delete webhook, add member) and verifying they appear in the audit log with correct actor, action, and timestamp.

**Acceptance Scenarios**:

1. **Given** any sensitive action (create/delete instance, manage members, change API keys), **When** the action completes, **Then** an audit log entry is created.
2. **Given** an organization, **When** I GET `/organizations/{id}/audit-logs`, **Then** the response returns paginated log entries with actor, action, resource, and timestamp.
3. **Given** an audit log, **When** I filter by action type, **Then** only matching entries are returned.
4. **Given** a member without admin role, **When** they request audit logs, **Then** the API returns a 403 error.

---

### Edge Cases

- What happens when an org owner is removed from their own org? The API prevents removing the last owner.
- What happens when an org hits its quota mid-request? The request is rejected before processing.
- What happens when an API key is deleted while in use? Active requests complete; new requests with that key fail.
- What happens when an organization is deleted? All associated instances, API keys, webhooks, and audit logs are deleted.
- How are usage counters reset? Monthly quotas reset on the first of each month.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support creating, reading, and deleting organizations.
- **FR-002**: The system MUST support adding and removing members from an organization.
- **FR-003**: The system MUST enforce role-based access control for all operations.
- **FR-004**: The system MUST support creating scoped API keys per organization.
- **FR-005**: The system MUST support deleting API keys.
- **FR-006**: The system MUST track usage counters per organization (messages sent, webhooks delivered, storage used).
- **FR-007**: The system MUST enforce monthly quotas per organization and reject requests that would exceed them.
- **FR-008**: The system MUST enforce instance limits per organization.
- **FR-009**: The system MUST audit log all sensitive actions with actor, action, resource, and timestamp.
- **FR-010**: The system MUST expose audit logs via API with pagination and filtering.
- **FR-011**: The system MUST prevent removing the last owner from an organization.
- **FR-012**: The system MUST support migrating existing single-tenant data to an organization.

### Key Entities

- **Organization**: A tenant. Fields: id, name, owner_id, member_count, created_at, settings (quotas, limits).
- **OrganizationMember**: A user-org membership. Fields: id, organization_id, user_id, role (owner/admin/developer/viewer), invited_by, joined_at.
- **ScopedApiKey**: An API key tied to an organization with scopes. Fields: id, organization_id, name, key_hash, scopes (JSON list), created_at, expires_at.
- **UsageCounter**: Tracks resource usage per org per period. Fields: organization_id, metric (messages_sent, webhooks_fired, storage_bytes), period_start, period_end, current_value, limit_value.
- **AuditLogEntry**: Immutable record of a sensitive action. Fields: id, organization_id, actor_id, action, resource_type, resource_id, details, ip_address, created_at.

## Success Criteria *(mandatory)*

- **SC-001**: A platform admin can create an org, invite two members with different roles, and verify permission enforcement in under 2 minutes.
- **SC-002**: A developer with a read-only API key cannot send messages, create instances, or manage webhooks.
- **SC-003**: An org that exhausts its monthly message quota receives a 429 error and normal service resumes after the quota resets or is upgraded.
- **SC-004**: All sensitive actions appear in the audit log within 5 seconds.
- **SC-005**: Existing MVP instances (created before multi-tenancy) are migrated to a default organization without data loss.

## Assumptions

- User authentication (login/signup) is handled by a separate auth service; this phase assumes authenticated users with JWT.
- The platform operator has a super-admin role outside org scoping.
- Monthly quotas are hard limits (not soft warnings).
- Usage counters are eventually consistent (updated asynchronously).
- Audit logs are append-only and never deleted.
- Audit log retention is 90 days (configurable).
- API key scopes use a simple string format: `messages:send`, `webhooks:read`, `instances:write`, `admin:*`.
