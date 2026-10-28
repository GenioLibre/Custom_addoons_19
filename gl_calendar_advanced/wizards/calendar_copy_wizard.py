from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CalendarCopyWizard(models.TransientModel):
    _name = "gl.calendar.copy.wizard"
    _description = "Duplicate or repeat instructor schedule"

    source_event_id = fields.Many2one("calendar.event", string="Source event", required=True)
    target_date = fields.Date(string="First target date", required=True, default=fields.Date.context_today)
    repeat_weekly = fields.Boolean(string="Repeat weekly")
    repeat_count = fields.Integer(string="Occurrences", default=1, required=True,
                                  help="Number of weeks when repeating; one event otherwise.")
    mon = fields.Boolean(string="Monday", default=True)
    tue = fields.Boolean(string="Tuesday", default=True)
    wed = fields.Boolean(string="Wednesday", default=True)
    thu = fields.Boolean(string="Thursday", default=True)
    fri = fields.Boolean(string="Friday", default=True)
    sat = fields.Boolean(string="Saturday")
    sun = fields.Boolean(string="Sunday")

    @api.constrains("repeat_count")
    def _check_repeat_count(self):
        for wizard in self:
            if not 1 <= wizard.repeat_count <= 52:
                raise ValidationError(_("Choose between 1 and 52 occurrences/weeks."))

    def action_duplicate(self):
        self.ensure_one()
        source = self.source_event_id
        if not source.start:
            raise UserError(_("Original event must have a start time."))
        tz = ZoneInfo(self.env.user.tz or "UTC")
        original_local = fields.Datetime.to_datetime(source.start).replace(
            tzinfo=ZoneInfo("UTC")
        ).astimezone(tz)
        days = [self.mon, self.tue, self.wed, self.thu, self.fri, self.sat, self.sun]
        if self.repeat_weekly and not any(days):
            raise UserError(_("Select at least one weekday."))
        target_dates = []
        if self.repeat_weekly:
            week_start = self.target_date - timedelta(days=self.target_date.weekday())
            for week in range(self.repeat_count):
                for day_index, selected in enumerate(days):
                    date = week_start + timedelta(weeks=week, days=day_index)
                    if selected and date >= self.target_date:
                        target_dates.append(date)
        else:
            target_dates = [self.target_date]

        if len(target_dates) > 260:
            raise UserError(_("Too many events requested."))
        created = self.env["calendar.event"]
        for date in target_dates:
            target_local = datetime.combine(date, original_local.timetz().replace(tzinfo=None))
            target_local = target_local.replace(tzinfo=tz)
            utc_start = target_local.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
            created |= source.gl_duplicate_to(fields.Datetime.to_string(utc_start))
        return {
            "type": "ir.actions.act_window",
            "name": _("Created schedules"),
            "res_model": "calendar.event",
            "view_mode": "list,form",
            "domain": [("id", "in", created.ids)],
            "target": "current",
        }
