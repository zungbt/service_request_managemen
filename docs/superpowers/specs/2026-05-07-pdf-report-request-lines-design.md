# PDF Report Design: Show Request Lines

## Context
The current PDF report for `service_request_managemen` shows a single-row description table with the request description and total amount. The user wants the PDF to show the actual request lines instead, matching the simpler structure already used in the email templates. The request-level description block should be replaced, while the Notes section should remain.

## Goal
Make the PDF report reflect the actual service lines on the request, using the same compact structure users already see in email notifications.

## Recommended Approach
Replace the current description table in `report/service_request_report.xml` with a compact line-items table that mirrors the email template layout.

### Table structure
Columns:
- `Loại`
- `Dịch vụ`
- `SL`
- `Thành tiền`

Data source:
- Loop over `o.request_line_ids`
- `line.service_type`
- `line.product_id.name`
- `line.quantity`
- `line.price_subtotal`

Footer totals:
- `o.amount_untaxed`
- `o.amount_tax`
- `o.amount_total`

## What stays unchanged
- The top summary block in the PDF remains as-is.
- The Notes section remains below the new table.
- No model changes are needed because the required data already exists on `service.request` and `service.request.line`.

## Alternatives considered
1. Keep the request description and add the table as an extra section.
   - Rejected because the user asked to replace the description block.
2. Expand the PDF beyond the email layout with more columns like unit price or discount.
   - Rejected because the user chose the simpler email-matching layout.

## Files affected
- `report/service_request_report.xml`

## Verification
- Confirm the QWeb template loops over `o.request_line_ids`.
- Confirm the old single-row description table is removed.
- Confirm totals still use `o.amount_untaxed`, `o.amount_tax`, and `o.amount_total`.
- Re-read the updated XML and check that the report structure matches the approved design.
