# sauravshah.com.np

A minimalist, book-like static blog site generator with support for markdown, custom media embeds, and beautiful typography.

## Features

✨ **Minimalist Design** — Clean, book-like aesthetic with beautiful typography  
🌙 **Night Mode** — Automatically follows system theme, with manual override  
🎨 **Custom Markdown** — Extended syntax for videos, slideshows, galleries, and more  
🌏 **Multilingual** — Full support for English and Nepali (Devanagari) text  
📱 **Responsive** — Works beautifully on all devices  
⚡ **Fast** — Pure static HTML, no JavaScript frameworks  
🎯 **Simple** — Edit markdown files, run deploy.py, done!

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Your Content

Edit files in the `content/` directory:

```
content/
├── _meta.yaml              # Home page metadata
├── Treks/
│   ├── _meta.yaml          # Section metadata
│   └── Everest Base Camp/
│       ├── content.md      # Your blog post
│       └── .data/          # Photos, videos, etc.
└── About/
    └── content.md
```

### 3. Generate the Site

```bash
python deploy.py
```

### 4. View Your Site

Open `site/index.html` in your browser, or deploy the `site/` folder to any static hosting service.

## Content Structure

### Home Page (`content/_meta.yaml`)

```yaml
name: "Your Name"
intro: |
  Your introduction
  Multiple lines supported
photo: "profile.jpg"
social_links:
  - type: instagram
    url: "https://instagram.com/yourhandle"
  - type: github
    url: "https://github.com/yourusername"
```

### Section/Index Page (`content/SectionName/_meta.yaml`)

```yaml
title: "Section Title"
intro: "Section description"
photos:
  - .data/photo1.jpg
  - .data/photo2.jpg
social_links:
  - type: instagram
    url: "https://instagram.com/yourhandle"
```

### Content Page (`content/SectionName/PageName/content.md`)

```markdown
---
title: "Page Title"
intro: "Page description"
photos:
  - .data/photo1.jpg
  - .data/photo2.jpg
---

# Your Content Here

Write your blog post in markdown...
```

## Custom Markdown Syntax

### YouTube Videos

```markdown
{{youtube: VIDEO_ID}}
{{youtube: https://youtube.com/watch?v=VIDEO_ID}}
```

### Local Videos

```markdown
{{video: .data/video.mp4}}
{{video: .data/video.mp4, poster=.data/poster.jpg}}
```

### Slideshows

```markdown
{{slideshow: .data/img1.jpg, .data/img2.jpg, .data/img3.jpg}}
{{slideshow: .data/img1.jpg, .data/img2.jpg, interval=5}}
```

### Short Videos (Vertical)

```markdown
{{short: .data/reel.mp4}}
```

### Image Galleries

```markdown
{{gallery: .data/photo1.jpg, .data/photo2.jpg, .data/photo3.jpg}}
```

### Styled Quotes

```markdown
{{quote: "Your quote here", author="Author Name"}}
```

### Standard Markdown

All standard markdown is supported:

```markdown
# Heading 1
## Heading 2
### Heading 3

**Bold text**
*Italic text*

> Blockquote

- List item 1
- List item 2

1. Numbered item 1
2. Numbered item 2

[Link text](https://example.com)

![Image alt text](.data/image.jpg)

`inline code`

\`\`\`
code block
\`\`\`
```

## Folder Structure

```
.
├── content/                 # Your content (edit this!)
│   ├── _meta.yaml          # Home page config
│   ├── Section1/
│   │   ├── _meta.yaml      # Section config
│   │   └── Post1/
│   │       ├── content.md  # Blog post
│   │       └── .data/      # Media files
│   └── Section2/
├── templates/               # HTML templates (Jinja2)
│   ├── base.html
│   ├── home.html
│   ├── index.html
│   └── content.html
├── static/                  # CSS, JS, fonts
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── site/                    # Generated site (deploy this!)
├── deploy.py               # Build script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Theme Controls

### In the Browser

- **Night Mode Button** (🌙) — Toggle dark theme
  - By default, follows your system theme preference
  - Click to manually override system setting

### Keyboard Shortcuts

- `N` — Toggle night mode
- `Esc` — Go back to previous page

### Theme Behavior

- **Night Mode**: Automatically follows your system's dark/light mode preference. If you manually toggle it, your preference is saved and will override the system setting.
- **Theme Persistence**: Your manual preferences are saved in browser localStorage and persist across visits.
- **System Theme Changes**: If you haven't manually set a preference, the site will automatically update when your system theme changes.

## Deployment

### GitHub Pages

1. Generate your site: `python deploy.py`
2. Push the `site/` folder to your repository
3. Enable GitHub Pages in repository settings
4. Point to the `site/` folder

### Netlify / Vercel

1. Generate your site: `python deploy.py`
2. Deploy the `site/` folder
3. Done!

### Custom Server

1. Generate your site: `python deploy.py`
2. Upload the `site/` folder to your web server
3. Point your domain to the folder

## Customization

### Fonts

Edit `templates/base.html` to change Google Fonts:

```html
<link href="https://fonts.googleapis.com/css2?family=Your+Font&display=swap" rel="stylesheet">
```

Then update CSS variables in `static/css/style.css`:

```css
:root {
    --font-body: 'Your Font', serif;
    --font-heading: 'Your Heading Font', serif;
}
```

### Colors

Edit CSS variables in `static/css/style.css`:

```css
:root {
    --bg-color: #faf8f3;
    --text-color: #2c2c2c;
    --accent-color: #8b7355;
    /* ... */
}
```

### Layout

Edit templates in `templates/` directory using Jinja2 syntax.

## Tips

1. **Keep it simple** — The beauty is in the simplicity
2. **Use high-quality images** — They make a huge difference
3. **Write in markdown** — It's intuitive and portable
4. **Test locally** — Always preview before deploying
5. **Backup your content** — Keep your `content/` folder in version control

## Troubleshooting

### Site not generating?

- Check Python version (3.7+)
- Install dependencies: `pip install -r requirements.txt`
- Check for YAML syntax errors in `_meta.yaml` files

### Images not showing?

- Ensure images are in `.data/` folders
- Use relative paths: `.data/image.jpg`
- Check file extensions match (case-sensitive on Linux)

### Nepali text not displaying?

- Ensure UTF-8 encoding in your markdown files
- The Noto Serif Devanagari font is loaded automatically

## License

MIT License — Feel free to use and modify for your own blog!

## Credits

Built with:
- [Python](https://python.org)
- [Markdown](https://python-markdown.github.io/)
- [Jinja2](https://jinja.palletsprojects.com/)
- [PyYAML](https://pyyaml.org/)
- [Google Fonts](https://fonts.google.com/)
- [Font Awesome](https://fontawesome.com/)

---

Made with ❤️ for simple, beautiful blogging.
