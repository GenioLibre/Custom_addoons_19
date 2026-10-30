from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestGLCalendar(TransactionCase):
    def test_duplicate_resets_payment_state(self):
        start = fields.Datetime.now().replace(microsecond=0)
        instructor = self.env.user
        event = self.env["calendar.event"].create({
            "name": "Driving lesson",
            "start": start,
            "stop": start + timedelta(hours=2),
            "gl_kind": "lesson",
            "gl_instructor_id": instructor.id,
            "gl_payment_state": "paid",
        })
        new_start = start + timedelta(days=7)
        duplicate = event.gl_duplicate_to(fields.Datetime.to_string(new_start))
        self.assertEqual(duplicate.start, new_start)
        self.assertEqual(duplicate.stop - duplicate.start, timedelta(hours=2))
        self.assertEqual(duplicate.gl_payment_state, "unknown")
        self.assertNotEqual(duplicate.id, event.id)

    def test_cannot_duplicate_into_conflicting_slot(self):
        start = fields.Datetime.now().replace(microsecond=0)
        instructor = self.env.user
        event = self.env["calendar.event"].create({
            "name": "Instructor blocked",
            "start": start,
            "stop": start + timedelta(hours=2),
            "gl_kind": "block",
            "gl_instructor_id": instructor.id,
        })
        with self.assertRaises(UserError):
            event.gl_duplicate_to(fields.Datetime.to_string(start + timedelta(minutes=30)))
