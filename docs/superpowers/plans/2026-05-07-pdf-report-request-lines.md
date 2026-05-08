# PDF Report Request Lines Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current single-row description table in the service request PDF with a compact request-lines table that matches the existing email layout.

**Architecture:** Keep the change isolated to the QWeb report template in `report/service_request_report.xml`. Reuse the same data already rendered by the email templates: loop over `o.request_line_ids`, render the compact four-column table, and keep the existing totals and Notes section intact.

**Tech Stack:** Odoo 17, QWeb XML report templates, git

---

## File Structure

- Modify: `report/service_request_report.xml`
  - Replace the current single-row description table with a compact line-items table.
  - Keep the top summary block and Notes section unchanged.
- Modify: `TODO.md`
  - Mark item #13 as fixed after the report template is updated.
- No tests currently exist in this module.

### Task 1: Update the PDF report template

**Files:**
- Modify: `report/service_request_report.xml:32-48`
- Verify against: `data/email_templates.xml:17-49`

- [ ] **Step 1: Read the current report table and the email table side by side**

Confirm the current PDF section to replace in `report/service_request_report.xml`:

```xml
<!-- Description Table -->
<table class="table table-sm o_main_table mt16">
    <thead>
        <tr style="background-color: #f2f2f2;">
            <th style="width: 70%;">Job Description</th>
            <th class="text-end">Total Amount</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><span t-field="o.description"/></td>
            <td class="text-end">
                <span t-field="o.amount_total" t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
            </td>
        </tr>
    </tbody>
</table>
```

Use the existing email table in `data/email_templates.xml` as the structure reference.

- [ ] **Step 2: Replace the PDF description table with the compact request-lines table**

Update `report/service_request_report.xml` so that the replaced section becomes:

```xml
<!-- Request Lines Table -->
<table class="table table-sm o_main_table mt16">
    <thead>
        <tr style="background-color: #f2f2f2;">
            <th>Loại</th>
            <th>Dịch vụ</th>
            <th class="text-end">SL</th>
            <th class="text-end">Thành tiền</th>
        </tr>
    </thead>
    <tbody>
        <t t-foreach="o.request_line_ids" t-as="line">
            <tr>
                <td><t t-out="line.service_type"/></td>
                <td><t t-out="line.product_id.name"/></td>
                <td class="text-end"><t t-out="line.quantity"/></td>
                <td class="text-end">
                    <span t-field="line.price_subtotal" t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
                </td>
            </tr>
        </t>
    </tbody>
    <tfoot>
        <tr>
            <td colspan="3" class="text-end">Cộng tiền hàng:</td>
            <td class="text-end">
                <span t-field="o.amount_untaxed" t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
            </td>
        </tr>
        <tr>
            <td colspan="3" class="text-end">Thuế Ato (1%):</td>
            <td class="text-end">
                <span t-field="o.amount_tax" t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
            </td>
        </tr>
        <tr>
            <td colspan="3" class="text-end"><strong>Tổng cộng:</strong></td>
            <td class="text-end">
                <strong><span t-field="o.amount_total" t-options='{"widget": "monetary", "display_currency": o.currency_id}'/></strong>
            </td>
        </tr>
    </tfoot>
</table>
```

This intentionally removes the request-level description from the PDF and keeps the Notes section below.

- [ ] **Step 3: Run a targeted diff check**

Run:

```bash
git diff -- report/service_request_report.xml
```

Expected: the old “Job Description / Total Amount” table is gone and replaced by the request-lines table.

- [ ] **Step 4: Commit the report template change**

```bash
git add report/service_request_report.xml
git commit -m "$(cat <<'EOF'
Update service request PDF to show request lines.
EOF
)"
```

### Task 2: Update the TODO entry

**Files:**
- Modify: `TODO.md:67-69`

- [ ] **Step 1: Replace the open TODO item with a fixed note**

Change this block:

```md
13. **Update PDF report to show request lines**
    - `report/service_request_report.xml` only shows description and total.
    - **Fix:** Update the QWeb template to include a detail table of `request_line_ids`, matching the email template layout.
```

To:

```md
13. ~~**Update PDF report to show request lines**~~ ✅ **FIXED**
    - `report/service_request_report.xml` now renders a compact `request_line_ids` table matching the email layout, with totals retained below the lines.
```

- [ ] **Step 2: Run a targeted diff check**

Run:

```bash
git diff -- TODO.md
```

Expected: only item #13 changed from open to fixed.

- [ ] **Step 3: Commit the TODO update**

```bash
git add TODO.md
git commit -m "$(cat <<'EOF'
Mark PDF request-lines report task as fixed.
EOF
)"
```

### Task 3: Final verification

**Files:**
- Verify: `report/service_request_report.xml`
- Verify: `TODO.md`

- [ ] **Step 1: Re-read the updated report template**

Confirm all of the following in `report/service_request_report.xml`:
- there is a `t-foreach="o.request_line_ids"`
- the table headers are `Loại`, `Dịch vụ`, `SL`, `Thành tiền`
- totals still render `o.amount_untaxed`, `o.amount_tax`, and `o.amount_total`
- the Notes section still exists below the table

- [ ] **Step 2: Verify the TODO entry is marked fixed**

Confirm `TODO.md` contains:

```md
13. ~~**Update PDF report to show request lines**~~ ✅ **FIXED**
```

- [ ] **Step 3: Run the final verification commands**

Run:

```bash
grep -n "t-foreach=\"o.request_line_ids\"\|Loại\|Dịch vụ\|Thành tiền\|amount_untaxed\|amount_tax\|amount_total" report/service_request_report.xml
grep -n "Update PDF report to show request lines\|FIXED" TODO.md
```

Expected:
- report grep returns the request-lines loop, headers, and totals references
- TODO grep returns item #13 marked fixed

- [ ] **Step 4: Commit the verification-complete state**

```bash
git status --short report/service_request_report.xml TODO.md
```

Expected: no unexpected unstaged changes for those two files.
