# Service Request Management - Technical Documentation

This document provides a technical overview of the `service_request_management` module for Odoo 17.

## 1. Module Overview
- **Technical Name**: `service_request_management`
- **Dependencies**: `base`, `mail` (to support Chatter and internal communication).
- **Core Model**: `service.request`

## 2. Database Structure (`service.request`)

| Column | Type | Label | Attributes | Description |
| :--- | :--- | :--- | :--- | :--- |
| `name` | Char | Request Code | Required, Readonly, Copy=False | Unique ID (e.g., SR0001) |
| `customer_id` | Many2one | Customer | Tracking=True | Links to `res.partner` |
| `service_type` | Selection | Service Type | Required | Repair, Consulting, or Installation |
| `request_date` | Datetime | Request Date | Default=Now | When the request was made |
| `deadline` | Datetime | Deadline | Tracking=True | When the service must be finished |
| `state` | Selection | Status | Default='draft' | Draft -> Submitted -> Approved -> Done |
| `assigned_to` | Many2one | Assigned To | Tracking=True | Links to `res.users` |
| `amount_estimate`| Float | Est. Amount | - | Estimated cost of the service |
| `description` | Text | Description | - | Full details of the request |

### 2.1 Automatic Metadata Columns
These columns are managed by Odoo automatically:
- `id`: Primary Key.
- `create_date`: Record creation timestamp.
- `create_uid`: User who created the record.
- `write_date`: Last update timestamp.
- `write_uid`: User who last modified the record.

## 3. Security Implementation

### 3.1 Groups
- **Service User**: Basic access. Can create and edit requests.
- **Service Manager**: Admin access. Can approve and delete requests.

### 3.2 Record Rules (Visibility)
- **User Rule**: Users can only see records where `create_uid` is themselves.
- **Manager Rule**: Managers can see all records in the system.

## 4. Business Logic (Workflow)
The model includes the following status transitions:
1. **Draft**: The initial state.
2. **Submitted**: Requirement: `customer_id` must be set.
3. **Approved**: Requirement: `assigned_to` must be set.
4. **Done**: Final completion state.
5. **Cancelled**: Can be performed from most states.

---
*Created by Antigravity AI Guide - April 2026*
