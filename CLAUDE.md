# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
**Service Request Management** is an Odoo 17 module designed to digitize and automate the management of internal or customer service requests. It implements a structured workflow: `Draft` ➔ `Submitted` ➔ `Approved` ➔ `Done` (or `Cancelled`).

## Technical Architecture
The module follows Odoo's MVC architecture:
- **Models (`models/main.py`)**: Contains business logic, state machine transitions, data validation (`ValidationError`), and scheduled actions for deadline reminders.
- **Views (`views/service_request_views.xml`)**: Defines the User Interface, including Form views with status bars and Tree views.
- **Data (`data/`)**: 
    - `sequence.xml`: Auto-generation of request IDs (e.g., SR0001).
    - `email_templates.xml`: HTML templates for automated communication.
    - `cron.xml`: Defines the `Service Request: Deadline Reminder` scheduled action.
- **Security (`security/`)**: 
    - `res_groups.xml`: Defines `Service User` and `Service Manager` roles.
    - `ir.model.access.csv` & `record_rules.xml`: Manage access rights and row-level security.
- **Reports (`report/`)**: QWeb templates for generating PDF service request documents.

## Development Commands
As an Odoo module, development typically involves:
- **Installation/Update**: Install via Odoo Apps menu or start Odoo server with `-i service_request_managemen` (install) or `-u service_request_managemen` (update).
- **Testing Cron**: Manually trigger the deadline reminder via `Settings > Technical > Scheduled Actions > Service Request: Deadline Reminder`.
- **Developer Mode**: Ensure "Developer Mode" is active in Odoo to see technical fields and modify views.

## Key Constraints & Patterns
- **State Machine**: Ensure all state transitions are handled in `models/main.py` and reflect the workflow described in the README.
- **Security**: Always verify that new fields or models are added to `ir.model.access.csv` and mapped to the appropriate security groups.
- **Notifications**: Use the predefined email templates in `data/email_templates.xml` for consistency.
