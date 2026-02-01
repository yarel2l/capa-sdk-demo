import reflex as rx

config = rx.Config(
    app_name="demo_reflex",
    state_auto_setters=True,  # Enable auto setters for state vars
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)