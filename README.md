# Article Publisher

A tiny research article website you can publish from the terminal or a Jupyter notebook.

## Preview Locally

From this folder:

```bash
python publish.py build
python -m http.server 8000 --directory public
```

Then open:

```text
http://localhost:8000
```

## Publish From Terminal

Create a new article:

```bash
python publish.py new "My Research Article" --summary "A short one-line summary."
```

Edit the generated Markdown file in `articles/`, then rebuild:

```bash
python publish.py build
```

Your finished website appears in `public/`.

The generated GitHub Pages version appears in `docs/`.

## Add Pages And Navigation

The site now has navigation for:

```text
Home
Articles
About
Project
```

Create a new standalone page:

```bash
python publish.py page "Reading List" --summary "Papers, datasets, and useful references."
```

That creates a Markdown file in `pages/`. Edit it, then rebuild:

```bash
python publish.py build
```

To add a new link to the top navigation, edit `NAV_ITEMS` near the top of `publish.py`:

```python
NAV_ITEMS = [
    ("Home", "index.html"),
    ("Articles", "articles.html"),
    ("About", "about.html"),
    ("Project", "project.html"),
]
```

Then rebuild:

```bash
python publish.py build
```

## Publish From Jupyter

Put this in a notebook cell from the `article-publisher` folder:

```python
from publish import publish_article

publish_article(
    "My Research Article",
    """
# My Research Article

This is the article body.

## Findings

- First finding
- Second finding
""",
    summary="A short one-line summary.",
)
```

That creates `articles/my-research-article.md` and rebuilds the site.

## Put It Online With GitHub Pages

1. Create a new GitHub repository.
2. Upload or commit this `article-publisher` folder as the repository contents.
3. In GitHub, go to Settings -> Pages.
4. Under "Build and deployment", choose "GitHub Actions".
5. Push to the `main` branch.

The included `.github/workflows/pages.yml` workflow rebuilds the site and publishes `public/`.

After that, your everyday workflow is:

```bash
python publish.py new "My Next Article" --summary "One-line summary."
python publish.py build
git add articles pages public docs publish.py README.md
git commit -m "Publish article"
git push
```

## Other Hosting Options

1. Netlify: drag the `public/` folder into Netlify Drop.
2. Cloudflare Pages: connect a repository, set the build command to `python publish.py build`, and set the output directory to `public`.
3. Any static host: upload the contents of `public/`.

## Customize

Edit these constants near the top of `publish.py`:

```python
SITE_TITLE = "Research Notes"
SITE_DESCRIPTION = "Curious by nature. Building with purpose. Learning always."
```

Edit `stylesheet()` in `publish.py` to change the visual style.
