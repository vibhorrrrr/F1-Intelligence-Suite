import os
import shutil

print("Setting up the F1 Strategy Suite for Netlify...")

# Create necessary directories
os.makedirs('build', exist_ok=True)

# Create a simple index.html that will redirect to the Dash app
with open('build/index.html', 'w') as f:
    f.write("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>F1 Strategy Suite</title>
        <meta http-equiv="refresh" content="0; url=/app" />
    </head>
    <body>
        <p>Redirecting to F1 Strategy Suite...</p>
    </body>
    </html>
    """)

print("Setup complete!")
