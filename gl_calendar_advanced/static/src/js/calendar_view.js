/** @odoo-module **/

import { registry } from "@web/core/registry";
import { attendeeCalendarView } from "@calendar/views/attendee_calendar/attendee_calendar_view";
import { AttendeeCalendarController } from "@calendar/views/attendee_calendar/attendee_calendar_controller";
import { browser } from "@web/core/browser/browser";
import { AttendeeCalendarRenderer } from "@calendar/views/attendee_calendar/attendee_calendar_renderer";
import { AttendeeCalendarCommonRenderer } from "@calendar/views/attendee_calendar/common/attendee_calendar_common_renderer";
import { AttendeeCalendarCommonPopover } from "@calendar/views/attendee_calendar/common/attendee_calendar_common_popover";

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

// Validated HEX only: never interpolate arbitrary record contents into CSS.
function instructorColor(record) {
    const color = record?.rawRecord?.gl_color;
    return typeof color === "string" && /^#[0-9a-fA-F]{6}$/.test(color)
        ? color
        : null;
}

class GLCalendarPopover extends AttendeeCalendarCommonPopover {
    static subTemplates = {
        ...AttendeeCalendarCommonPopover.subTemplates,
        popover: "gl_calendar_advanced.CalendarPopover",
    };

    get instructorColor() {
        return instructorColor(this.props.record);
    }

    get instructorForeground() {
        const color = this.instructorColor;
        if (!color) {
            return null;
        }
        const [r, g, b] = [1, 3, 5].map((i) => parseInt(color.slice(i, i + 2), 16));
        return (r * 299 + g * 587 + b * 114) / 1000 >= 160 ? "#151515" : "#ffffff";
    }
}

class GLCalendarCommonRenderer extends AttendeeCalendarCommonRenderer {
    static components = {
        ...AttendeeCalendarCommonRenderer.components,
        Popover: GLCalendarPopover,
    };

    onEventDidMount(info) {
        super.onEventDidMount(info);
        const record = this.props.model.records[info.event.id];
        const color = instructorColor(record);
        if (color) {
            // Override the background set by Odoo's native palette.
            info.el.style.setProperty("background-color", color, "important");
            info.el.style.setProperty("border-color", color, "important");
            info.el.style.setProperty("--gl-calendar-event-color", color);
        }
    }
}

class GLCalendarRenderer extends AttendeeCalendarRenderer {
    static components = {
        ...AttendeeCalendarRenderer.components,
        day: GLCalendarCommonRenderer,
        week: GLCalendarCommonRenderer,
        month: GLCalendarCommonRenderer,
    };
}

registry.category("views").add("gl_advanced_calendar", {
    ...attendeeCalendarView,
    Controller: GLCalendarController,
    Renderer: GLCalendarRenderer,
});
