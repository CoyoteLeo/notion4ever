<div align="center">
  <br>
  <img src="https://raw.githubusercontent.com/MerkulovDaniil/notion4ever/assets/cb.svg" width="256" alt="">
  <h1>NOTION4EVER</h1>
</div>

Notion4ever is a small python tool that allows you to free your content and export it as a collection of markdown and HTML files via the official Notion API.

# ✨ Features
* Export ready to deploy static HTML pages from your Notion.so pages.
    ![root_page](https://raw.githubusercontent.com/MerkulovDaniil/notion4ever/assets/root_page.png)
* Supports nice urls.
* Downloads all your Notion content, which is accessible via API to a raw JSON file. 
* Uses official Notion API (via [notion-sdk-py](https://github.com/ramnes/notion-sdk-py), but you can use curls if you want).
* Supports arbitrary page hierarchy.
    ![breadcrumb](https://raw.githubusercontent.com/MerkulovDaniil/notion4ever/assets/breadcrumb.png)
*  Supports galleries and lists
    ![gallery](https://raw.githubusercontent.com/MerkulovDaniil/notion4ever/assets/gallery.png)

    ![list](https://raw.githubusercontent.com/MerkulovDaniil/notion4ever/assets/list.png)

    Note that Notion API does not provide information about the database view yet. That is why notion4ever will render the database as a list if any database entries do not have a cover. Suppose all entries have covers, then it will be displayed as a gallery.
* Lightweight and responsive.
* Downloads all your images and files locally (you can turn this off if you prefer to store images\files somewhere else).

# 💻 How to run it locally
- Start cloning the notion page and build it locally
    ```python
    python -m notion4ever -n NOTION_TOKEN -p NOTION_PAGE_ID
    ```
- Start the local server
    ```
    docker compose up nginx
    ```

# 🛠 How it works
1. Given your notion token and ID of some page, notion4ever downloads all your content from this page and all nested subpages and saves it in a JSON file, `notion_content.json`.
2. Given your raw Notion data, notion4ever structures the page's content and generates file `notion_structured.json` with markdown content of all pages and relations between them. Markdown parsing is done via modification of [notion2md](https://github.com/echo724/notion2md) library.
3. Given structured notion content, notion4ever generates site from [jinja](https://github.com/pallets/jinja/) templates located in `./_templates` directory. All styles are located in `./_sass` directory and compiled with [libsass-python](https://github.com/sass/libsass-python) library. By default, site is located in `./_site` directory

# ToDo
- [x] Use proper package manager instead of pip.
- [x] Add support for `toggle_header`, `synced_block` and `column_list` blocks.
- [x] Add `table_of_contents` block.
- [x] Support `mermaid` diagrams of `code` block.
- [x] Support downloading a single page, db_entry, and workspace. 
- [ ] Add parallel files downloading.
- [ ] Add search field. 
- [ ] Dark model.