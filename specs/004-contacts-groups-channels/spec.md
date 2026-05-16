# Feature Specification: Contacts, Groups, Channels

**Feature Branch**: `004-contacts-groups-channels`

**Created**: 2026-05-16

**Status**: Draft

**Input**: User description: "Extend Telegram Evolution API with contact, group, and channel management: contact CRUD, group creation and member management, channel join/leave and message browsing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Contact Management (Priority: P1)

As a developer, I want to list, import, and remove Telegram contacts so that my application can manage a contact directory.

**Why this priority**: Contact management is the foundation for Telegram CRM and address-book workflows.

**Independent Test**: Can be tested by importing a contact via phone number, listing contacts to confirm it appears, and deleting the contact to remove it.

**Acceptance Scenarios**:

1. **Given** a connected instance, **When** I GET `/instances/{id}/contacts`, **Then** the response returns the contact list with names, phone numbers, and user IDs.
2. **Given** a valid phone number, **When** I POST to `/instances/{id}/contacts/import`, **Then** the contact is added to the Telegram contact list.
3. **Given** an existing contact, **When** I DELETE `/instances/{id}/contacts/{user_id}`, **Then** the contact is removed from the Telegram contact list.
4. **Given** a phone number not on Telegram, **When** I attempt to import it, **Then** the API returns an error indicating the user is not on Telegram.
5. **Given** a disconnected instance, **When** I access any contact endpoint, **Then** the API returns a 400 error.

---

### User Story 2 - Group Management (Priority: P1)

As a developer, I want to create Telegram groups, supergroups, add/remove members, and browse existing groups so that my application can support community management workflows.

**Why this priority**: Group management is the most common Telegram community automation need.

**Independent Test**: Can be tested by creating a new group, listing groups to confirm it appears, adding a member, removing the member, and verifying membership changes via group info.

**Acceptance Scenarios**:

1. **Given** a connected instance, **When** I POST to `/instances/{id}/groups` with a group name, **Then** a new group is created and the response includes the group ID.
2. **Given** one or more groups exist, **When** I GET `/instances/{id}/groups`, **Then** the response lists all groups the instance is a member of.
3. **Given** an existing group, **When** I POST to `/instances/{id}/groups/{group_id}/members` with a user ID, **Then** that user is added to the group.
4. **Given** a group member, **When** I DELETE `/instances/{id}/groups/{group_id}/members/{user_id}`, **Then** the user is removed from the group.
5. **Given** a group where the instance lacks admin rights, **When** I attempt to add or remove a member, **Then** the API returns a 403 error.
6. **Given** a supergroup, **When** I invite via a private invite link, **Then** the system returns the invite link in the group details.

---

### User Story 3 - Channel Operations (Priority: P2)

As a developer, I want to join, leave, list channels, and read channel messages so that my application can monitor and interact with channels.

**Why this priority**: Channel operations extend the gateway's reach to broadcast-style communication but are less commonly needed than groups.

**Independent Test**: Can be tested by joining a public channel via username, listing joined channels, reading recent messages, and leaving the channel.

**Acceptance Scenarios**:

1. **Given** a connected instance, **When** I POST to `/instances/{id}/channels/join` with a channel username or invite link, **Then** the instance joins the channel and the response includes the channel ID.
2. **Given** a joined channel, **When** I POST to `/instances/{id}/channels/leave`, **Then** the instance leaves the channel.
3. **Given** one or more joined channels, **When** I GET `/instances/{id}/channels`, **Then** the response lists all channels the instance follows.
4. **Given** a joined channel, **When** I GET `/instances/{id}/channels/{channel_id}/messages`, **Then** the response returns recent channel messages with pagination.
5. **Given** a private invite link, **When** I join via the link, **Then** the instance joins the private channel.

---

### Edge Cases

- What happens when importing a contact that is already in the contact list? The API returns success (idempotent).
- What happens when removing a contact that doesn't exist? The API returns a 404 error.
- What happens when creating a group with a name that violates Telegram's rules? Telegram rejects the creation; the error is propagated.
- What happens when joining a channel that doesn't exist? The API returns a 404 error.
- What happens when the instance is already a member of the group/channel? The API returns success (idempotent).
- What happens when an invite link is expired or invalid? The API returns a 400 error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST list Telegram contacts for a connected instance.
- **FR-002**: The system MUST import a contact by phone number.
- **FR-003**: The system MUST delete a contact by user ID.
- **FR-004**: The system MUST create a new Telegram group with a given name.
- **FR-005**: The system MUST list all groups the connected instance is a member of.
- **FR-006**: The system MUST add a user to a group by user ID.
- **FR-007**: The system MUST remove a user from a group by user ID.
- **FR-008**: The system MUST support joining a channel by username or invite link.
- **FR-009**: The system MUST support leaving a channel.
- **FR-010**: The system MUST list all channels the connected instance follows.
- **FR-011**: The system MUST return recent messages from a channel with pagination.
- **FR-012**: The system MUST return clear error messages when the instance lacks required permissions (e.g., not admin, not a member).

### Key Entities

- **Contact**: A Telegram contact associated with the connected instance. Fields: user_id, phone_number, first_name, last_name.
- **Group**: A Telegram group or supergroup. Fields: group_id, title, member_count, link (if public/set), is_supergroup.
- **Channel**: A Telegram channel. Fields: channel_id, title, username (if public), member_count, link.

## Success Criteria *(mandatory)*

- **SC-001**: A developer can import a contact, list contacts, and delete a contact in under 10 seconds total.
- **SC-002**: A developer can create a group, add two members, and verify membership via group list in under 15 seconds.
- **SC-003**: A developer can join a public channel, read the latest 20 messages, and leave the channel in under 20 seconds.
- **SC-004**: Each operation returns appropriate HTTP status codes (200, 201, 400, 403, 404).
- **SC-005**: Permission errors include a human-readable message explaining which permission is missing.

## Assumptions

- Contact import requires the target user's phone number to be registered on Telegram.
- Group creation by default creates a basic group. For supergroup conversion, use the existing promote API.
- The connected instance must have the `AddChatUser` permission to add members to a group.
- The connected instance must be an admin with `BanChatUser` permission to remove members.
- Channel join via username works for public channels only. Private channels require an invite link.
- Channel join via invite link works for private channels where the link is valid and not expired.
- Channel messages are read-only; this phase does not include sending to channels (covered by existing send-message).
- Group and channel webhook events are normalized in the existing webhook system.
