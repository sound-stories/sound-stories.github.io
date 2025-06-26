import os
import os.path
import markdown
from pathlib import Path
import shutil
from bs4 import BeautifulSoup  # Import BeautifulSoup


def add_vimeo_links(soup):

    # Process Vimeo links
    modal_id = 0

    for a_tag in soup.find_all("a", href=True):

        href = a_tag["href"]

        if "vimeo.com" in href:
            modal_id += 1
            video_id = href.split("/")[-1]
            iframe = f"""
            <div class="modal" id="vimeoModal{modal_id}" style="display:none; position:fixed; top:10%; left:10%; width:80%; height:80%; background:white; z-index:1000; padding:1rem;">
                <iframe src="https://player.vimeo.com/video/{video_id}" width="100%" height="100%" frameborder="0" allowfullscreen></iframe>
                <button onclick="document.getElementById('vimeoModal{modal_id}').style.display='none';" style="position:absolute; top:10px; right:10px;">Close</button>
            </div>
            """
            # Replace the link with a clickable trigger
            a_tag["href"] = "#"
            a_tag["onclick"] = (
                f"document.getElementById('vimeoModal{modal_id}').style.display='block'; return false;"
            )
            # Append the modal HTML at the end
            soup.append(BeautifulSoup(iframe, "html.parser"))


def get_content(md_file):

    # Convert Markdown to HTML
    with open(md_file, "r") as file:
        md_content = file.read()

    html_content = markdown.markdown(md_content)

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Replace <hr> with alternating hand-drawn lines
    hand_drawn_lines = [
        "img/line1.svg",
        "img/line2.svg",
        "img/line3.svg",
    ]

    for idx, hr_tag in enumerate(soup.find_all("hr")):
        img_tag = soup.new_tag(
            "img",
            src=hand_drawn_lines[idx % len(hand_drawn_lines)],
            alt="hand-drawn divider",
        )
        # Keep your responsive bootstrap style
        img_tag["class"] = ["img-fluid", "hand-drawn-line"]
        hr_tag.replace_with(img_tag)

    # Add 'img-fluid' class to all <img> tags
    for img in soup.find_all("img"):
        existing_classes = img.get("class", [])
        existing_classes.append("img-fluid")
        img["class"] = existing_classes

    add_vimeo_links(soup)

    return soup


# Paths
ASSETS_DIR = "assets"
CONTENT_DIR = "content"
OUTPUT_DIR = "html"
TEMPLATE_FILE = "template.html"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the HTML template
with open(TEMPLATE_FILE, "r", encoding="utf-8") as template_file:
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

content_path = Path(CONTENT_DIR)

# Process each Markdown file
for subfolder in content_path.iterdir():
    if subfolder.is_dir():

        # Determine the output HTML file name
        if subfolder.stem == "home":
            output_file = Path(OUTPUT_DIR) / "index.html"  # Special case for home page
        else:
            output_file = Path(OUTPUT_DIR) / f"{subfolder.stem}.html"

        template_soup = BeautifulSoup(
            template,
            "html.parser",
        )

        # Generate a title from the file name
        title = subfolder.stem.replace("-", " ").capitalize()

        template_soup.title.string = title

        for element_type in ["large", "top", "middle", "bottom"]:

            element_id = f"content_{element_type}"
            md_file = subfolder / f"{element_type}.md"

            content_div = template_soup.find(id=element_id)

            if content_div:

                if not md_file.exists():
                    # delete content_div
                    template_soup.find(id=element_id).decompose()
                else:
                    print(f"Processing {md_file}")

                    content = get_content(md_file)
                    content_div.clear()
                    content_div.append(content)

        # Save the resulting HTML file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(str(template_soup))

        print(f"Generated: {output_file}")
