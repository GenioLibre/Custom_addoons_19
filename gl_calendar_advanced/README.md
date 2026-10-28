# GL Advanced Calendar for Odoo 19

Initial test release for `calendar.event` on Odoo 19 Community/Enterprise.

## Available in v1

- Adds instructor, schedule type, lesson state and a **manual** payment marker.
- Allows individual instructor HEX colors in the Users form (administrator only).
- Adds **Copy / Repeat** wizard in the event form. Preserves wall-clock start time in the operator's timezone and copies a bounded selection of weekdays.
- Prevents creating overlapping duplicates for the same instructor, within events tagged as lesson/block.
- Restores the last navigated date when reopening the Calendar view in the same browser tab.

## Limitations

- This initial build targets Odoo's standard `calendar.event`. Custom driving-school lesson models require an adapter.
- No right-click contextual menu in v1.
- Precise per-status HEX rendering not activated; fields are prepared for v2.
- The wizard does not copy attendees: that is intentional to avoid creating accidental invitations or marking new reservations paid.
- Overlap checks are applied to **wizard-created duplicates**, not all other event creation paths. They are not an atomic DB lock.
- The week-selection wizard creates events for selected days starting on the first date and can create up to 260; use a test database.
- Staff manual color is only metadata in v1; do not expect borders to change before v2.

## Install

1. Clone this repository into the Odoo addons path (or configure `addons_path`).
2. Restart the Odoo service.
3. In Apps, update the Apps List; search for *GL Advanced Calendar* and install.
4. Test first in a database copy. Open Calendar > event form, fill instructor / schedule type, save and reopen, then Copy / Repeat.
5. Run Odoo tests with `--test-enable -i gl_calendar_advanced --stop-after-init` on a fresh test DB.

## Validation

This code has static source checks only until it is installed on a test Odoo 19 database. The client's installed Odoo apps and original driving-school calendar model have not yet been inspected.
