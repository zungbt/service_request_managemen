# TODO & Improvements for `service_request_managemen`

Generated: 2026-05-05
Updated: 2026-05-07 (sync with actual code state)

## Critical Bugs

1. ~~**Add `product` to `__manifest__.py` dependencies**~~ ✅ **FIXED**
   - `depends` already includes `['base', 'mail', 'product', 'stock']`.

2. ~~**Hardcoded IP URL in email templates**~~ ✅ **FIXED**
   - Replaced all 3 occurrences of `'http://100.81.225.45:8069/web#id=%s&model=%s&view_type=form' % (object.id, object._name)` with `object.get_base_url() + '/web#id=%s&model=%s&view_type=form' % (object.id, object._name)` in `data/email_templates.xml`.

3. ~~**`amount_estimate` inconsistency with computed totals**~~ ✅ **FIXED**
   - Removed `amount_estimate` field entirely from model, form view, and report. Report now uses `amount_total` with `o.currency_id`.

## Quick Wins

4. **Fill the README**
   - `README.md` has placeholder headers but no real content.
   - **Fix:** Document the workflow, security groups, cron job, and key features.

5. **Remove dead controller/wizard code**
   - `controllers/` and `wizard/` folders exist but are empty (only blank `__init__.py` files).
   - **Fix:**
     1. Delete `controllers/__init__.py` and `wizard/__init__.py` (empty files).
     2. In `__init__.py`, remove lines 2-3: `from . import controllers` and `from . import wizard`.
     3. Result: `__init__.py` becomes a single line: `from . import models`.
     4. Remove empty `controllers/` and `wizard/` directories.

6. **Add a Search view for `service.request`**
   - There is no `<search>` view defined.
   - **Fix:** Add filters for `customer_id`, `state`, `assigned_to`, and `deadline` range.

7. **Add a Kanban view**
   - Service requests are a natural fit for a Kanban board grouped by `state`.
   - **Fix:** Add a Kanban view record and include it in the `act_window` `view_mode`.

8. **Add Graph / Pivot reporting**
   - No dashboard or analysis views exist.
   - **Fix:** Add graph/pivot views for revenue by service type, requests by employee, monthly trends.

## Missing Business Logic

9. ~~**Deadline past-date validation**~~ ✅ **FIXED**
   - `_onchange_deadline` in `models/main.py:63-72` warns on past dates.

10. ~~**Header `service_type` vs line `service_type` redundancy**~~ ✅ **FIXED**
    - Removed `service_type` from `service.request` model (header). Only line-level `service_type` remains in `service.request.line`, allowing mixed service types per request.

11. **Reopen logic (`action_reopen`)**
    - Currently just flips state from `done` back to `draft` and posts a message (`models/main.py:112-116`).
    - Unlike `sale.order.action_draft` / `purchase.order.button_draft` (which reset pre-sale negotiation documents and need no reason), reopening a *completed* service request is a business-significant action — Odoo uses wizards for comparable operations (`sale.order.cancel`, `crm.lead.lost`, `applicant.refuse.reason`).
    - **Fix (wizard + groups + activity):**
      1. **Create transient model** `service.request.reopen.wizard` in new file `wizard/service_request_reopen_wizard.py` with:
         - `request_id` (Many2one → service.request, required)
         - `reason` (Text, required — collect reopen reason)
         - `action_confirm_reopen()` — writes `state='draft'`, posts `message_post` with user + reason, schedules a To-Do activity for `assigned_to`
      2. **Create wizard form view** in `wizard/service_request_reopen_wizard.xml` with the `reason` field and Confirm/Cancel buttons.
      3. **Change `action_reopen`** in `models/main.py` to return `ir.actions.act_window` opening the wizard (`target: 'new'`) instead of directly flipping state.
      4. **Add `groups`** to the reopen button in `views/service_request_views.xml`: `groups="service_request_managemen.group_service_request_manager"`.
      5. **Register** wizard model in `models/__init__.py` and wizard view in `__manifest__.py`.
    - **Resolution:** Reason captured via wizard → audit trail via `message_post` (chatter) → permission restricted to managers → activity created so reopened request isn't forgotten. Follows `sale.order.cancel` / `crm.lead.lost` pattern.

12. ~~**Laptop stock concurrency risk**~~ ✅ **FIXED**
    - `action_confirm()` now uses `stock.picking` + `stock.move` with proper Odoo stock atomicity. `action_cancel()` cancels the picking through Odoo stock. See #16.

## Refactor / Architecture Improvements

16. ~~**Migrate `laptop.inventory` to standard Odoo `product.product` + `stock` module**~~ ✅ **DONE**
    - **Bước 1: Dependencies** ✅ `'depends': ['base', 'mail', 'product', 'stock']`
    - **Bước 2: Xóa model `laptop.inventory`** ✅ Class, access rules, views commented out
    - **Bước 3: Sửa `LaptopSaleLine` methods** ✅ `_compute_line_totals` uses `product_id.standard_price`, `_onchange_product_id` uses `product_id.lst_price`
    - **Bước 4: Sửa Views** ✅ `<field name="product_id"/>` in `laptop_view.xml:101`
    - **Bước 5: `action_confirm()` với `stock.picking`** ✅ Creates picking, moves, confirms, assigns, validates
    - **Bước 6: `action_cancel()` với stock** ✅ Searches and cancels the picking by origin

## UX / Polish

13. ~~**Update PDF report to show request lines**~~ ✅ **FIXED**
    - `report/service_request_report.xml` now renders a compact `request_line_ids` table matching the email layout, with totals retained below the lines.

14. **Mixed Vietnamese / English field labels**
    - Some fields are labeled in Vietnamese (`Giá nhập`, `Khách hàng`) while others are in English.
    - **Fix:** Standardize labels to one language. Move translations to the `i18n/` folder using `.pot` / `.po` files.

15. **Chatter tracking for line changes**
    - `amount_untaxed`, `amount_tax`, `amount_total`, `deadline`, and `assigned_to` have `tracking=True`.
    - **Fix:** Consider posting to the chatter when `request_line_ids` are added, removed, or modified.
