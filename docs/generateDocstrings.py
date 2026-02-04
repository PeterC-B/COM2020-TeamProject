import pkgutil
import inspect
import importlib
import os
import html

ROOT_PACKAGE = "server"
OUTPUT_DIR = "docs"

def walk_modules(package):
    """Yield full module names for all modules under a package."""
    package_path = package.replace(".", "/")
    for _, modname, _ in pkgutil.walk_packages([package_path], package + "."):
        yield modname

def safe_import(module_name):
    """Import a module safely, ignoring failures."""
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None

def html_escape(text):
    return html.escape(text or "")

def make_navbar(module_list):
    """Create a navigation bar with links to all modules."""
    nav = ['<div class="navbar">']
    nav.append('<a href="index.html">Home</a>')
    for mod in module_list:
        filename = mod.replace(".", "_") + ".html"
        nav.append(f'<a href="{filename}">{mod}</a>')
    nav.append("</div>")
    return "\n".join(nav)

def generate_html(module_name, module, navbar):
    """Generate HTML content for a single module."""
    lines = []

    lines.append("<html><head>")
    lines.append(f"<title>{module_name}</title>")
    lines.append("<style>")
    lines.append("""
        body { font-family: Arial, sans-serif; padding: 20px; }
        .navbar { background: #333; padding: 10px; }
        .navbar a { color: white; margin-right: 15px; text-decoration: none; }
        .navbar a:hover { text-decoration: underline; }
        h1 { color: #333; }
        pre { background: #f4f4f4; padding: 10px; white-space: pre-wrap; }
    """)
    lines.append("</style>")
    lines.append("</head><body>")

    lines.append(navbar)
    lines.append(f"<h1>Module: {module_name}</h1>")

    # Module docstring
    module_doc = inspect.getdoc(module) or "No module docstring"
    lines.append("<h2>Module Docstring</h2>")
    lines.append(f"<pre>{html_escape(module_doc)}</pre>")

    # Functions
    lines.append("<h2>Functions</h2>")
    functions = inspect.getmembers(module, inspect.isfunction)
    if not functions:
        lines.append("<p>No functions found.</p>")
    else:
        for name, func in functions:
            if func.__module__ != module_name:
                continue
            doc = inspect.getdoc(func) or "No docstring"
            lines.append(f"<h3>{name}</h3>")
            lines.append(f"<pre>{html_escape(doc)}</pre>")

    # Classes (docstring only)
    lines.append("<h2>Classes</h2>")
    classes = inspect.getmembers(module, inspect.isclass)
    if not classes:
        lines.append("<p>No classes found.</p>")
    else:
        for cls_name, cls in classes:
            if cls.__module__ != module_name:
                continue
            cls_doc = inspect.getdoc(cls) or "No docstring"
            lines.append(f"<h3>class {cls_name}</h3>")
            lines.append(f"<pre>{html_escape(cls_doc)}</pre>")

    lines.append("</body></html>")
    return "\n".join(lines)

def generate_homepage(module_list):
    """Create index.html with links to all modules."""
    lines = []

    lines.append("<html><head>")
    lines.append("<title>Server Documentation</title>")
    lines.append("<style>")
    lines.append("""
        body { font-family: Arial, sans-serif; padding: 20px; }
        .navbar { background: #333; padding: 10px; }
        .navbar a { color: white; margin-right: 15px; text-decoration: none; }
        .navbar a:hover { text-decoration: underline; }
        h1 { color: #333; }
        ul { line-height: 1.8; }
    """)
    lines.append("</style>")
    lines.append("</head><body>")

    navbar = make_navbar(module_list)
    lines.append(navbar)

    lines.append("<h1>Server Documentation</h1>")
    lines.append("<p>Select a module to view its documentation.</p>")
    lines.append("<ul>")

    for mod in module_list:
        filename = mod.replace(".", "_") + ".html"
        lines.append(f'<li><a href="{filename}">{mod}</a></li>')

    lines.append("</ul>")
    lines.append("</body></html>")

    return "\n".join(lines)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    module_list = list(walk_modules(ROOT_PACKAGE))
    navbar = make_navbar(module_list)

    # Generate module pages
    for module_name in module_list:
        module = safe_import(module_name)
        if module is None:
            continue

        html_content = generate_html(module_name, module, navbar)
        filename = module_name.replace(".", "_") + ".html"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

    # Generate home page
    homepage = generate_homepage(module_list)
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(homepage)

    print(f"Documentation site generated in '{OUTPUT_DIR}/'")

if __name__ == "__main__":
    main()