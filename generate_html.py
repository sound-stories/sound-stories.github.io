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
            <div class="modal, pop-up" id="vimeoModal{modal_id}">
                <iframe src="https://player.vimeo.com/video/{video_id}" width="100%" height="100%" frameborder="0" allowfullscreen></iframe>
                <a onclick="document.getElementById('vimeoModal{modal_id}').style.display='none';">X</button>
            </div>
            """
            # Replace the link with a clickable trigger
            a_tag["href"] = "#"
            a_tag["onclick"] = (
                f"document.getElementById('vimeoModal{modal_id}').style.display='block'; return false;"
            )
            # Append the modal HTML at the end
            soup.append(BeautifulSoup(iframe, "html.parser"))


def get_content(md_file, name):

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

    # # Add 'img-fluid' class to all <img> tags
    # for img in soup.find_all("img"):
    #     existing_classes = img.get("class", [])
    #     existing_classes.append("img-fluid")
    #     img["class"] = existing_classes

    add_vimeo_links(soup)

    return soup


# Paths
ASSETS_DIR = "assets"
CONTENT_DIR = "content"
OUTPUT_DIR = "html"
TEMPLATE_FILE = "template.html"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


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

        name = subfolder.stem.lower()

        # Load the HTML template
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as template_file:
            template = template_file.read()

        template_soup = BeautifulSoup(
            template,
            "html.parser",
        )

        # Generate a title from the file name
        title = name.replace("-", " ").capitalize()

        template_soup.title.string = title

        for img in template_soup.find_all("img"):
            if "src" in img.attrs and "{page}" in img["src"]:
                img["src"] = img["src"].replace("{page}", name)
                print(f"Updated image src: {img['src']}")
            if "alt" in img.attrs and "{page}" in img["alt"]:
                img["alt"] = img["alt"].replace("{page}", name)

        # Determine the output HTML file name
        if name == "home":
            output_file = Path(OUTPUT_DIR) / "index.html"  # Special case for home page
        else:
            output_file = Path(OUTPUT_DIR) / f"{name}.html"

        for element_type in ["large", "top", "middle", "bottom"]:

            container_id = f"container_{element_type}"
            container_div = template_soup.find(id=container_id)

            if container_div:

                md_file = subfolder / f"{element_type}.md"

                if not md_file.exists():
                    # delete content_div
                    template_soup.find(id=container_id).decompose()
                else:

                    content_id = f"content_{element_type}"

                    content_div = template_soup.find(id=content_id)

                    print(f"Processing {md_file}")

                    content = get_content(
                        md_file=md_file,
                        name=name,
                    )

                    content_div.clear()
                    content_div.append(content)

                    container_div_class = f"containter_{element_type}_{name}"

                    if "class" in container_div.attrs:
                        container_div["class"].append(container_div_class)
                    else:
                        container_div["class"] = [container_div_class]

                    content_div_class = f"content_{element_type}_{name}"

                    if "class" in content_div.attrs:
                        content_div["class"].append(content_div_class)
                    else:
                        content_div["class"] = [content_div_class]

        # Save the resulting HTML file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(str(template_soup))

        print(f"Generated: {output_file}")
