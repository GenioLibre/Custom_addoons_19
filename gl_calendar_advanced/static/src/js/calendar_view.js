/** @odoo-module **/

import { registry } from "@web/core/registry";
import { attendeeCalendarView } from "@calendar/views/attendee_calendar/attendee_calendar_view";
import { AttendeeCalendarController } from "@calendar/views/attendee_calendar/attendee_calendar_controller";
import { browser } from "@web/core/browser/browser";

const KEY = "gl_calendar_advanced.current_date";

class GLCalendarController extends AttendeeCalendarController {
    get modelParams() {
        const params = super.modelParams;
        const saved = browser.sessionStorage.getItem(KEY);
        if (!this.props.state?.date && saved) {
            const restored = luxon.DateTime.fromISO(saved);
            if (restored.isValid) {
                return { ...params, date: restored };
            }
        }
        return params;
    }

    async setDate(move) {
        const result = await super.setDate(move);
        this.rememberDate();
        return result;
    }

    async setScale(scale) {
        const result = await super.setScale(scale);
        this.rememberDate();
        return result;
    }

    rememberDate() {
        if (this.model?.meta?.date) {
            browser.sessionStorage.setItem(KEY, this.model.meta.date.toISO());
        }
    }

    async editRecord(record, context = {}) {
        this.rememberDate();
        return super.editRecord(record, context);
    }
}

registry.category("views").add("gl_advanced_calendar", {
    ...attendeeCalendarView,
    Controller: GLCalendarController,
});
