{
    "name": "GL Advanced Calendar",
    "summary": "Instructor scheduling, status colors and copy/block wizard",
    "version": "19.0.1.0.0",
    "category": "Productivity/Calendar",
    "author": "GenioLibre",
    "license": "LGPL-3",
    "depends": ["calendar"],
    "data": [
        "security/ir.model.access.csv",
        "views/calendar_views.xml",
        "wizards/calendar_copy_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "gl_calendar_advanced/static/src/js/calendar_view.js",
            "gl_calendar_advanced/static/src/scss/calendar.scss",
        ],
    },
    "installable": True,
    "application": False,
}