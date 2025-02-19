import sass
import markdown
import shutil
import jinja2
from pathlib import Path
import logging
import dateutil.parser as dt_parser
import json

# pip install mdx_truly_sane_lists
# required pip install markdown-captions, pip install markdown-checklist
# pip install pymdown-extensions


def verify_templates(config: dict):
    """Verifies existense and content of sass and templates dirs."""
    if Path(config["sass_dir"]).is_dir() and any(Path(config["sass_dir"]).iterdir()):
        logging.debug("🤖 Sass directory is OK")
    else:
        logging.critical("🤖 Sass directory is not found or empty.")

    if Path(config["templates_dir"]).is_dir() and any(Path(config["templates_dir"]).iterdir()):
        logging.debug("🤖 Templates directory is OK")
    else:
        logging.critical("🤖 Templates directory is not found or empty.")


def generate_css(config: dict):
    """Generates css file (compiling sass files in the output_dir folder)."""
    sass.compile(dirname=(config["sass_dir"], (Path(config["output_dir"]) / "css").as_posix()))


def generate_404(structured_notion: dict, config: dict):
    """Generates 404 html page."""
    with open(Path(config["output_dir"]) / "404.html", "w+", encoding="utf-8") as f:
        tml = (Path(config["templates_dir"]) / "404.html").read_text()
        jinja_loader = jinja2.FileSystemLoader(config["templates_dir"])
        jtml = jinja2.Environment(loader=jinja_loader).from_string(tml)
        html_page = jtml.render(content="", site=structured_notion)
        f.write(html_page)


def generate_archive(structured_notion: dict, config: dict):
    """Generates archive page."""
    archive_link = "Archive.html"
    structured_notion["archive_url"] = str((Path(config["output_dir"]).resolve() / archive_link))

    with open(Path(config["output_dir"]) / archive_link, "w+", encoding="utf-8") as f:
        # Specify template folder
        tml = (Path(config["templates_dir"]) / "archive.html").read_text()
        jinja_loader = jinja2.FileSystemLoader(config["templates_dir"])
        jtemplate = jinja2.Environment(loader=jinja_loader).from_string(tml)
        html_page = jtemplate.render(content="", site=structured_notion)
        f.write(html_page)


def str_to_dt(structured_notion: dict):
    for page_id, page in structured_notion["pages"].items():
        for field in ["date", "date_end", "last_edited_time"]:
            if field in page.keys():
                structured_notion["pages"][page_id][field] = dt_parser.isoparse(page[field])


def generate_page(page_id: str, structured_notion: dict, config: dict):
    page = structured_notion["pages"][page_id]
    page_url = page["url"]

    # Generated file information
    folder = (config["output_dir"] / page_url.lstrip("/")).parent
    md_filename = f"{page_id}.md"
    html_filename = "index.html"

    logging.debug(f"🤖 MD {folder / md_filename}; HTML {folder / html_filename}")
    folder.mkdir(parents=True, exist_ok=True)
    with open((folder / md_filename).resolve(), "w+", encoding="utf-8") as f:
        metadata = (
            "---\n"
            f"title: {page['title']}\n"
            f"cover: {page['cover']}\n"
            f"icon: {page['icon']}\n"
            f"emoji: {page['emoji']}\n"
        )
        if "properties_md" in page.keys():
            for p_title, p_md in page["properties_md"].items():
                metadata += f"{p_title}: {p_md}\n"
        metadata += "---\n\n"
        ### Complex part here
        md_content = page["md_content"]
        md_content = metadata + md_content

        f.write(md_content)

    html_content = markdown.markdown(
        md_content,
        extensions=[
            "meta",
            "tables",
            "mdx_truly_sane_lists",
            "markdown_captions",
            "pymdownx.tilde",
            "pymdownx.tasklist",
            "pymdownx.superfences",
            "pymdownx.blocks.details",
            "markdown_mermaidjs",
            "toc",
        ],
        extension_configs={
            "mdx_truly_sane_lists": {
                "nested_indent": 4,
                "truly_sane": True,
            },
            "pymdownx.tasklist": {
                "clickable_checkbox": True,
            },
        },
    )

    tml = (Path(config["templates_dir"]) / "page.html").read_text()

    with open((folder / html_filename).resolve(), "w+", encoding="utf-8") as f:
        # Specify template folder
        jinja_loader = jinja2.FileSystemLoader(config["templates_dir"])
        jtemplate = jinja2.Environment(loader=jinja_loader).from_string(tml)
        html_page = jtemplate.render(content=html_content, page=page, site=structured_notion)
        f.write(html_page)


def generate_pages(structured_notion: dict, config: dict):
    for page_id, page in structured_notion["pages"].items():
        generate_page(page_id, structured_notion, config)


def generate_search_index(structured_notion: dict, config: dict):
    """Generates search index file if building for server"""
    if structured_notion["search_index"]:
        search_index_path = Path(config["output_dir"]) / "search_index.json"
        with open(search_index_path, "w", encoding="utf-8") as f:
            json.dump(structured_notion["search_index"], f, ensure_ascii=False)
        # Update the search_index to just contain the path
        structured_notion["search_index"] = "search_index.json"


def generate_site(structured_notion: dict, config: dict):
    verify_templates(config)
    logging.debug("🤖 SASS and templates are verified.")

    generate_css(config)
    logging.debug("🤖 SASS translated to CSS folder.")

    generate_search_index(structured_notion, config)
    logging.debug("🤖 Generated search index file.")

    if (Path(config["output_dir"]) / "css" / "fonts").exists():
        shutil.rmtree(Path(config["output_dir"]) / "css" / "fonts")
    shutil.copytree(Path(config["sass_dir"]) / "fonts", Path(config["output_dir"]) / "css" / "fonts")
    logging.debug("🤖 Copied fonts.")

    str_to_dt(structured_notion)
    logging.debug("🤖 Changed string in dates to datetime objects.")

    generate_archive(structured_notion, config)
    logging.info("🤖 Archive page generated.")

    generate_404(structured_notion, config)
    logging.info("🤖 404.html page generated.")

    generate_pages(structured_notion, config)
    logging.info("🤖 All html and md pages generated.")
