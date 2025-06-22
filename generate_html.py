import os
import os.path
import markdown
from pathlib import Path
import shutil
from bs4 import BeautifulSoup  # Import BeautifulSoup

# Paths
ASSETS_DIR = "assets"
CONTENT_DIR = "content"
OUTPUT_DIR = "html"
TEMPLATE_FILE = "template.html"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the HTML template
with open(TEMPLATE_FILE, "r") as template_file:
    template = template_file.read()

# Copy static assets (img, css, js) to output directory
for folder in ["img", "css", "js", "fonts"]:
    source = Path(ASSETS_DIR) / folder
    destination = Path(OUTPUT_DIR) / folder
    if source.exists():
        shutil.copytree(source, destination, dirs_exist_ok=True)
        print(f"Copied {folder} from {source} to {destination}")

# Copy CNAME
source_file = "CNAME"
if os.path.exists(source_file):
    output_file = Path(OUTPUT_DIR) / source_file
    shutil.copy(source_file, output_file)

# Process each Markdown file
for md_file in Path(CONTENT_DIR).glob("*.md"):
    # Determine the output HTML file name
    if md_file.stem == "home":
        output_file = Path(OUTPUT_DIR) / "index.html"  # Special case for home page
    else:
        output_file = Path(OUTPUT_DIR) / f"{md_file.stem}.html"

    # Generate a title from the file name
    title = md_file.stem.replace("-", " ").capitalize()

    # Convert Markdown to HTML
    with open(md_file, "r") as file:
        md_content = file.read()
    html_content = markdown.markdown(md_content)

    # Parse the HTML content and add 'img-fluid' class to all <img> tags
    soup = BeautifulSoup(html_content, "html.parser")
    for img in soup.find_all("img"):
        existing_classes = img.get("class", [])
        existing_classes.append("img-fluid")
        img["class"] = existing_classes
    html_content = str(soup)

    # Insert the title and content into the template
    final_html = template.replace("{{ title }}", title).replace(
        "{{ content }}", html_content
    )

    # Save the resulting HTML file
    with open(output_file, "w") as file:
        file.write(final_html)

    print(f"Generated: {output_file}")
