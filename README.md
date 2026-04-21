# Service Request Management

A professional Odoo 17 module for managing internal service requests with automated workflows, security levels, and reporting.

## 🚀 Features
*   **Request Management**: Track requests from Draft to Completion.
*   **Auto-Sequencing**: Automatic ID generation (SR0001, SR0002...).
*   **Security Layers**: 
    *   **Users**: Can only see and manage their own requests.
    *   **Managers**: Full visibility and approval power.
*   **Communication**: Integrated with Odoo Chatter for logs and internal messaging.
*   **Reporting**: Professional PDF reports for service summaries.
*   **Reminders**: Automated daily email notifications for upcoming deadlines.

## 🛠 Installation
1. Copy the `service_request_management` folder to your Odoo `addons` directory.
2. Restart your Odoo server.
3. Enable **Debug Mode** in Odoo.
4. Go to **Apps > Update Apps List**.
5. Search for "Service Request" and click **Activate**.

## 📁 Technical Info
*   **Model**: `service.request`
*   **Dependencies**: `base`, `mail`
*   **Author**: Zungg
*   **Version**: 1.0

---
*Developed as part of the Odoo 17 learning series.*
