import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    gl_calendar_color = fields.Char(
        string="Instructor calendar color", default="#2563EB",
        help="HEX color used for the instructor border in GL calendar.",
    )

    @api.constrains("gl_calendar_color")
    def _check_gl_calendar_color(self):
        for user in self:
            if user.gl_calendar_color and not re.fullmatch(
                r"#[0-9a-fA-F]{6}", user.gl_calendar_color
            ):
                raise ValidationError("Use a six-digit HEX color, e.g. #2563EB.")
