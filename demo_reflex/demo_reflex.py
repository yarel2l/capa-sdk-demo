"""
CAPA Demo Application
A comprehensive demo showcasing all features of the CAPA using Reflex.
"""

import reflex as rx
from rxconfig import config
from .pages import (
    home_page,
    docs_page,
    demo_page,
)


# Create the app with dark theme (fixed, no toggle)
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        radius="large",
        accent_color="orange",
        gray_color="slate",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap",
    ],
    style={
        "font_family": "'Courier Prime', monospace",
    },
)

# Add all pages
app.add_page(home_page, route="/", title="CAPA - Home")
app.add_page(docs_page, route="/docs", title="Documentation - CAPA")
app.add_page(demo_page, route="/demo", title="Demo - CAPA")
