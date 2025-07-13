import os
import os.path
from pathlib import Path
import shutil
from bs4 import BeautifulSoup  # Import BeautifulSoup
from bs4.element import Tag  # Import Tag for type checking


def get_content(html_file):

    # Convert Markdown to HTML
    with open(html_file, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    return soup


def process_element_file(
    content_div,
    element_file,
):

    content = get_content(
        html_file=element_file,
    )

    content_div.clear()
    content_div.append(content)


def process_element_folder(
    content_div,
    element_folder,
):

    content_div.clear()

    for file in sorted(element_folder.glob("*.html")):

        content = get_content(html_file=file)
        content_div.append(content)


def add_class(
    element,
    class_name,
):

    if "class" in element.attrs:
        element["class"].append(class_name)
    else:
        element["class"] = [class_name]


def copy_assets(
    assets_dir,
    output_dir,
):

    # Copy static assets (img, css, js) to output directory
    for folder in ["img", "css", "js", "fonts"]:

        source = Path(assets_dir) / folder
        destination = Path(output_dir) / folder

        if source.exists():
            shutil.copytree(source, destination, dirs_exist_ok=True)


def copy_cname(
    output_dir,
):

    # Copy CNAME
    source_file = "CNAME"

    if os.path.exists(source_file):
        output_file = Path(output_dir) / source_file
        shutil.copy(source_file, output_file)


def process_images(
    soup,
    page_name,
):

    for img in soup.find_all("img"):
        if "src" in img.attrs and "{page}" in img["src"]:
            img["src"] = img["src"].replace("{page}", page_name)
        if "alt" in img.attrs and "{page}" in img["alt"]:
            img["alt"] = img["alt"].replace("{page}", page_name)


def load_template(
    template_path,
):
    with open(template_path, "r", encoding="utf-8") as template_file:
        template = template_file.read()
    return BeautifulSoup(template, "html.parser")


def make_title(page_name):
    page_name = page_name.replace("-", " ")
    page_name = page_name.replace("_", " ")
    words = page_name.split(" ")
    return " ".join(word.capitalize() for word in words)


def set_title(
    soup,
    page_name,
):

    title = make_title(page_name)

    # Set the title of the HTML document
    if soup.title:
        soup.title.string = title
    else:
        new_title = soup.new_tag("title")
        new_title.string = title
        soup.head.append(new_title)


def get_output_file(
    page_name,
    output_dir,
):

    # Determine the output HTML file name
    if page_name.lower() == "home":
        return Path(output_dir) / "index.html"  # Special case for home page
    else:
        return Path(output_dir) / f"{page_name}.html"


def generate_element(
    page_folder,
    page_name,
    element_type,
    template_soup,
    lines,
):

    container_id = f"container_{element_type}"
    container_div = template_soup.find(id=container_id)

    if not container_div or type(container_div) is not Tag:
        return

    add_class(
        element=container_div,
        class_name=f"containter_{element_type}_{page_name}",
    )

    # Find the content div within the container
    content_id = f"content_{element_type}"
    content_div = template_soup.find(id=content_id)

    if not content_div:
        container_div.decompose()

    element_file = page_folder / f"{element_type}.html"
    element_folder = page_folder / element_type

    add_class(
        element=container_div,
        class_name=f"content_{element_type}_{page_name}",
    )

    if element_file.exists():

        process_element_file(
            content_div=content_div,
            element_file=element_file,
        )

    elif element_folder.exists():

        process_element_folder(
            content_div=content_div,
            element_folder=element_folder,
        )

    else:
        container_div.decompose()


def get_page_name(
    page_folder,
):
    # Get the page name from the folder name
    return page_folder.stem.lower()


def process_navigation(
    soup,
    page_names,
    lines,
):

    # Find the navigation element
    navItems = soup.find(id="navItems")

    if not navItems:
        print("No navItems element found in the template.")
        return

    # Clear existing navigation items
    navItems.clear()

    number_of_pages = len(page_names)

    # Create navigation links
    for index in range(number_of_pages):

        page_name = page_names[index]

        div_tag = soup.new_tag("div")
        div_tag["class"] = "nav-item mb-2"

        a_tag = soup.new_tag("a", href=f"{page_name}.html")
        a_tag.string = make_title(page_name)

        div_tag.append(a_tag)
        navItems.append(div_tag)

        if index < (number_of_pages - 1):

            line_number = (index % len(lines)) + 1

            img_tag = soup.new_tag(
                "img",
                src=f"img/menu_line{line_number}.svg",
                alt="hand-drawn divider",
            )

            img_tag["class"] = "hand-drawn-line-menu"

            div_tag.append(img_tag)


def generate_page(
    page_folder,
    output_dir,
    template_path,
    page_names,
    white_lines,
    black_lines,
):

    page_name = get_page_name(page_folder)

    template_soup = load_template(template_path)

    set_title(
        soup=template_soup,
        page_name=page_name,
    )

    process_navigation(
        soup=template_soup,
        page_names=page_names,
        lines=white_lines,
    )

    process_images(
        soup=template_soup,
        page_name=page_name,
    )

    for element_type in ["large", "top", "middle", "bottom"]:

        generate_element(
            page_folder=page_folder,
            page_name=page_name,
            element_type=element_type,
            template_soup=template_soup,
            lines=black_lines,
        )

    output_file = get_output_file(
        page_name=page_name,
        output_dir=output_dir,
    )

    # Save the resulting HTML file
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(str(template_soup))

    print(f"Generated: {output_file}")


def get_lines(img_dir, lines_dir):

    lines = []
    search_path = Path(img_dir) / lines_dir

    for line_file in sorted(search_path.glob("*.svg")):

        if line_file.is_file() and line_file.name.startswith("line"):

            image_name = line_file.name
            image_url = f"{lines_dir}/{image_name}"

            lines.append(image_url)

    return lines


def generate_website(
    content_dir,
    output_dir,
    template_path,
    white_lines,
    black_lines,
):

    content_path = Path(content_dir)

    page_names = [get_page_name(f) for f in content_path.iterdir() if f.is_dir()]

    # Process each Markdown file
    for page_folder in content_path.iterdir():
        if page_folder.is_dir():

            generate_page(
                page_folder=page_folder,
                output_dir=output_dir,
                template_path=template_path,
                page_names=page_names,
                white_lines=white_lines,
                black_lines=black_lines,
            )


if __name__ == "__main__":

    # Paths
    output_dir = "html"
    assets_dir = "assets"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    copy_assets(
        assets_dir=assets_dir,
        output_dir=output_dir,
    )

    white_lines = get_lines(
        img_dir=Path(output_dir) / "img",
        lines_dir="white_lines",
    )

    black_lines = get_lines(
        img_dir=Path(output_dir) / "img",
        lines_dir="black_lines",
    )

    copy_cname(
        output_dir=output_dir,
    )

    generate_website(
        content_dir="content",
        output_dir=output_dir,
        template_path="template.html",
        white_lines=white_lines,
        black_lines=black_lines,
    )
