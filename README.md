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
git add articles public
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
SITE_DESCRIPTION = "Articles, research notes, and working papers."
```

Edit `stylesheet()` in `publish.py` to change the visual style.
