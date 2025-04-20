from .run import create_app

# Create and expose both the Dash app and its underlying Flask server
app = create_app()
server = app.server