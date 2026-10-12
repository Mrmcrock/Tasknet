TaskNet age-gate package

The age prompt is already embedded into each included HTML page; you do not need to add CSS/JS links manually.

To use with Python's built-in web server:
1. Extract this ZIP into your TaskNet website folder (keep a backup of your current files first).
2. Run `python -m http.server 8000` from that folder.
3. Open http://localhost:8000 in your browser.

The gate asks whether the visitor is 13 or above. Yes allows the current browser session; No displays “You have to be 13 or above to use this website.”

This is a client-side prompt only and can be bypassed. It is not secure age verification. The package includes the HTML pages available from the project files; copy any additional images, styles, fonts, and other assets from your original project folder into this same folder to preserve those resources.
