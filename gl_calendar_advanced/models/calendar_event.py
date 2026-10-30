from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    gl_kind = fields.Selection(
        [("lesson", "Driving lesson"), ("block", "Instructor blocked"), ("other", "Other")],
        string="Schedule type", default="other", index=True,
    )
    gl_lesson_state = fields.Selection(
        [("scheduled", "Scheduled"), ("completed", "Completed"), ("cancelled", "Cancelled")],
        string="Lesson status", default="scheduled",
    )
    gl_payment_state = fields.Selection(
        [("unknown", "Not specified"), ("unpaid", "Unpaid"), ("paid", "Paid")],
        string="Payment status", default="unknown",
        help="Manual marker only; not linked to accounting.",
    )
    gl_instructor_id = fields.Many2one(
        "res.users", string="Instructor", index=True,
    )
    gl_color = fields.Char(
        string="Instructor HEX color", compute="_compute_gl_color",
        readonly=True,
    )

    @api.depends(
        "gl_instructor_id", "gl_instructor_id.gl_calendar_color",
        "partner_ids", "user_id", "user_id.gl_calendar_color",
    )
    def _compute_gl_color(self):
        """Explicit instructor > unique attendee user > event organizer.

        Legacy lessons often store instructors as attendees instead of using
        gl_instructor_id. Avoid choosing arbitrarily when several attendee
        users match: fall back to the organizer until an instructor is set.
        """
        for event in self:
            instructor = event.gl_instructor_id
            if not instructor and event.partner_ids:
                attendees = self.env["res.users"].search([
                    ("partner_id", "in", event.partner_ids.ids),
                    ("active", "=", True),
                ])
                non_organizers = attendees - event.user_id
                if len(non_organizers) == 1:
                    instructor = non_organizers
                elif len(attendees) == 1:
                    instructor = attendees
            if not instructor:
                instructor = event.user_id
            color = instructor.gl_calendar_color if instructor else False
            event.gl_color = color if color and len(color) == 7 and color.startswith("#") else False
    gl_visual_color = fields.Char(
        string="Status HEX color", compute="_compute_gl_visual_color",
    )

    @api.depends("gl_kind", "gl_lesson_state", "gl_payment_state")
    def _compute_gl_visual_color(self):
        for event in self:
            if event.gl_kind == "block":
                event.gl_visual_color = "#6B7280"
            elif event.gl_lesson_state == "cancelled":
                event.gl_visual_color = "#DC2626"
            elif event.gl_payment_state == "unpaid":
                event.gl_visual_color = "#D97706"
            elif event.gl_payment_state == "paid":
                event.gl_visual_color = "#16A34A"
            else:
                event.gl_visual_color = "#2563EB"

    @api.constrains("gl_kind", "gl_instructor_id", "start", "stop")
    def _check_gl_block_times(self):
        for event in self:
            if event.gl_kind == "block":
                if not event.gl_instructor_id:
                    raise ValidationError(_("Blocked slots need an instructor."))
                if not event.start or not event.stop or event.stop <= event.start:
                    raise ValidationError(_("End time must be after start time."))

    def gl_duplicate_to(self, start_datetime):
        """Copy only schedule fields, never RSVP tokens/attendees/payment settlement."""
        self.ensure_one()
        self.check_access("read")
        self.check_access("create")
        if not isinstance(start_datetime, str):
            raise UserError(_("Invalid target date."))
        try:
            new_start = fields.Datetime.to_datetime(start_datetime)
        except (TypeError, ValueError) as exc:
            raise UserError(_("Invalid target date.")) from exc
        if not new_start:
            raise UserError(_("Target date is required."))
        if not self.start or not self.stop or self.stop <= self.start:
            raise UserError(_("The original event has invalid dates."))
        values = {
            "name": self.name,
            "start": new_start,
            "stop": new_start + (self.stop - self.start),
            "allday": self.allday,
            "user_id": self.user_id.id,
            "gl_kind": self.gl_kind,
            "gl_lesson_state": "scheduled" if self.gl_kind == "lesson" else self.gl_lesson_state,
            "gl_payment_state": "unknown",
            "gl_instructor_id": self.gl_instructor_id.id or False,
            "location": self.location,
            "recurrency": False,
        }
        self._gl_check_instructor_overlap(values)
        return self.create(values)

    @api.model
    def _gl_check_instructor_overlap(self, values):
        instructor = values.get("gl_instructor_id")
        if not instructor:
            return
        start = values["start"]
        stop = values["stop"]
        overlap = self.search([
            ("gl_instructor_id", "=", instructor),
            ("active", "=", True),
            ("gl_kind", "in", ["lesson", "block"]),
            ("gl_lesson_state", "!=", "cancelled"),
            ("start", "<", stop),
            ("stop", ">", start),
        ], limit=1)
        if overlap:
            raise UserError(
                _("Instructor already has an active lesson or block during that time: %s") % overlap.name
            )

    def action_gl_open_copy_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Copy / repeat schedule"),
            "res_model": "gl.calendar.copy.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_source_event_id": self.id},
        }
