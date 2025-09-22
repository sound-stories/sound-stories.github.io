import os
import os.path
from pathlib import Path
import shutil
from bs4 import BeautifulSoup  # Import BeautifulSoup
from bs4.element import Tag  # Import Tag for type checking


ORDER = [
    "commissions",
    "songs",
    "podcasts",
    "studio_facilities",
    "experiments",
    "contact",
    "about",
]


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


def process_popups(
    template_soup,
    popup_folder,
):

    for file in sorted(popup_folder.glob("*.html")):

        name = file.stem

        print(f"  Adding popup: {name}")

        popup_div = template_soup.new_tag("div")

        popup_div["class"] = "modal fade"
        popup_div["id"] = f"{name}PopUp"

        template_soup.body.append(popup_div)

        dialog_div = template_soup.new_tag("div")
        dialog_div["class"] = "modal-dialog"
        popup_div.append(dialog_div)

        content_div = template_soup.new_tag("div")
        content_div["class"] = "modal-content"
        dialog_div.append(content_div)

        header_div = template_soup.new_tag("div")
        header_div["class"] = "modal-header"
        content_div.append(header_div)

        # title_h5 = template_soup.new_tag("h5")
        # title_h5["class"] = "modal-title"
        # title_h5.string = make_title(name)
        # header_div.append(title_h5)

        close_a = template_soup.new_tag("a")
        close_a["href"] = "#"
        close_a["data-bs-dismiss"] = "modal"
        close_a["aria-label"] = "Close"
        close_a["class"] = "modal-close"
        close_a.string = "X"
        content_div.append(close_a)

        body_div = template_soup.new_tag("div")
        body_div["class"] = "modal-body"
        content_div.append(body_div)

        process_element_file(
            body_div,
            element_file=popup_folder / f"{name}.html",
        )


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


def copy_robots(
    robots_dir,
    output_dir,
):

    files = [
        "robots.txt",
        "sitemap.xml",
    ]

    for file in files:
        source = Path(robots_dir) / file
        destination = Path(output_dir) / file
        if source.exists():
            shutil.copy(source, destination)
        else:
            print(f"Warning: Robots file {file} not found in {robots_dir}.")


def copy_favicon(
    favicon_dir,
    output_dir,
):

    # Copy favicon files to output directory
    favicon_files = [
        "favicon-16x16.png",
        "favicon-32x32.png",
        "favicon.ico",
        "favicon.svg",
        "apple-touch-icon.png",
        "site.webmanifest",
        "android-chrome-192x192.png",
        "android-chrome-512x512.png",
    ]

    for favicon in favicon_files:
        source = Path(favicon_dir) / favicon
        destination = Path(output_dir) / favicon

        if source.exists():
            shutil.copy(source, destination)
        else:
            print(f"Warning: Favicon file {favicon} not found in {favicon_dir}.")


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


def process_body(
    soup,
    page_name,
):

    for body in soup.find_all("body"):
        # replace {page} in body class attribute
        if "class" in body.attrs:
            body["class"] = [cls.replace("{page}", page_name) for cls in body["class"]]


def process_spans(
    soup,
    page_name,
):

    for span in soup.find_all("span"):
        # check if span text contain {page}
        if span.string and "{page}" in span.string:

            title = make_title(page_name)

            span.string = span.string.replace("{page}", title)


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

    # Set the title of the HTML document
    if soup.title:

        template_title = str(soup.title.string)

        if page_name.lower() == "home":

            new_title = template_title.replace("{page}", "").strip()

            if new_title.endswith("|"):
                new_title = new_title[:-1].strip()

            new_title = new_title.strip()

        else:

            title = make_title(page_name)

            new_title = template_title.replace("{page}", title)

        soup.title.string.replace_with(new_title)

    else:

        title = make_title(page_name)

        new_title = soup.new_tag("title")
        new_title.string = title
        soup.head.append(new_title)


def get_output_file(
    page_name,
    output_dir,
):

    return Path(output_dir) / get_url_from_page_name(
        page_name=page_name,
    )


def get_url_from_page_name(
    page_name,
):
    if page_name.lower() == "home":
        return "index.html"  # Special case for home page
    else:
        return f"{page_name}.html"


def generate_element(
    page_folder,
    page_name,
    element_type,
    template_soup,
):

    container_id = f"container_{element_type}"
    container_div = template_soup.find(id=container_id)

    if not container_div or type(container_div) is not Tag:
        return

    add_class(
        element=container_div,
        class_name=f"container_{element_type}_{page_name}",
    )

    # Find the content div within the container
    content_id = f"content_{element_type}"
    content_div = template_soup.find(id=content_id)

    if not content_div:
        container_div.decompose()

    element_file = page_folder / f"{element_type}.html"

    add_class(
        element=content_div,
        class_name=f"content_{element_type}_{page_name}",
    )

    if element_file.exists():

        process_element_file(
            content_div=content_div,
            element_file=element_file,
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

    page_names = sorted(
        page_names,
        key=lambda x: ORDER.index(x) if x in ORDER else len(ORDER),
    )

    # remove home
    if "home" in page_names:
        page_names.remove("home")

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

        url = get_url_from_page_name(page_name)
        a_tag = soup.new_tag("a", href=url)
        a_tag.string = make_title(page_name)
        a_tag["class"] = page_name.replace("_", "-")

        div_tag.append(a_tag)
        navItems.append(div_tag)

        if index < (number_of_pages - 1):

            line_index = index % len(lines)

            img_tag = soup.new_tag(
                "img",
                src=f"img/{lines[line_index]}",
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

    process_spans(
        soup=template_soup,
        page_name=page_name,
    )

    process_body(
        soup=template_soup,
        page_name=page_name,
    )

    for element_type in ["large", "split", "top", "middle"]:

        generate_element(
            page_folder=page_folder,
            page_name=page_name,
            element_type=element_type,
            template_soup=template_soup,
        )

    popup_folder = page_folder / "popups"

    if popup_folder.exists() and popup_folder.is_dir():
        process_popups(
            template_soup=template_soup,
            popup_folder=popup_folder,
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
            )


if __name__ == "__main__":

    # Paths
    output_dir = "html"
    assets_dir = "assets"
    favicon_dir = "favicon"
    robots_dir = "robots"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    copy_robots(
        robots_dir=robots_dir,
        output_dir=output_dir,
    )

    copy_favicon(
        favicon_dir=favicon_dir,
        output_dir=output_dir,
    )

    copy_assets(
        assets_dir=assets_dir,
        output_dir=output_dir,
    )

    white_lines = get_lines(
        img_dir=Path(output_dir) / "img",
        lines_dir="white_lines",
    )

    copy_cname(
        output_dir=output_dir,
    )

    generate_website(
        content_dir="content",
        output_dir=output_dir,
        template_path="template.html",
        white_lines=white_lines,
    )
