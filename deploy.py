#!/usr/bin/env python3
"""
Static Site Generator for sauravshah.com.np
Converts markdown content with custom syntax to static HTML
"""

import os
import re
import json
import shutil
import base64
import yaml
from pathlib import Path
from markdown import markdown
from jinja2 import Environment, FileSystemLoader

class SiteGenerator:
    def __init__(self, content_dir='content', output_dir='site', templates_dir='templates'):
        self.content_dir = Path(content_dir)
        self.output_dir = Path(output_dir)
        self.templates_dir = Path(templates_dir)
        self.static_dir = Path('static')
        
        # Site base URL (used for absolute OG image URLs)
        self.site_base_url = 'https://sauravshah.com.np'

        # Setup Jinja2
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
        
    def clean_output(self):
        """Remove existing output directory"""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)
        
    def copy_static_files(self):
        """Copy static assets (CSS, JS, fonts) to output"""
        if self.static_dir.exists():
            shutil.copytree(self.static_dir, self.output_dir / 'static')
            
    def load_meta(self, folder_path):
        """Load _meta.yaml from a folder"""
        meta_file = folder_path / '_meta.yaml'
        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
        
    def load_content(self, content_file):
        """Load markdown file with YAML front matter"""
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse front matter
        front_matter = {}
        body = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                front_matter = yaml.safe_load(parts[1])
                body = parts[2].strip()
                
        return front_matter, body
        
    def is_onedrive_url(self, url):
        """Check if a URL is a OneDrive sharing link"""
        return any(d in url for d in ['1drv.ms', 'onedrive.live.com', 'sharepoint.com'])

    def convert_onedrive_to_direct(self, url):
        """
        Return the OneDrive URL as-is so the browser follows the redirect chain
        at page-load time.

        For embed URLs (https://1drv.ms/i/c/...?width=...&height=...) the
        browser follows a pure HTTP redirect to the image CDN and displays the
        image — no build-time network request or token needed.

        Generic sharing URLs (/u/ path) redirect to an HTML viewer and will
        show a broken image; use the embed URL from OneDrive's Embed dialog.
        """
        return url

    def process_url(self, url):
        """
        Resolve a media URL inside markdown body:
          - OneDrive sharing links  → Graph API direct-content URL
          - Other http/https URLs   → used as-is
          - Local .data/ paths      → mapped to ../assets/
        """
        url = url.strip()
        if self.is_onedrive_url(url):
            return self.convert_onedrive_to_direct(url)
        if url.startswith('http://') or url.startswith('https://'):
            return url
        return url.replace('.data/', '../assets/')

    def resolve_photo_url(self, photo, url_path):
        """
        Resolve a photo value from _meta.yaml / front matter to a URL
        that can be used directly in an <img src="..."> attribute.

          - OneDrive sharing links  → Graph API direct-content URL
          - Other http/https URLs   → used as-is
          - Local paths (.data/x or bare filename)
                                    → depth-correct relative URL
                                      e.g. ../../assets/Treks/EBC/photo.jpg
        """
        photo = photo.strip()
        if self.is_onedrive_url(photo):
            return self.convert_onedrive_to_direct(photo)
        if photo.startswith('http://') or photo.startswith('https://'):
            return photo
        # Local file — build a relative URL from the page back to assets/
        filename = photo.split('/')[-1]
        depth = url_path.count('/') + 1 if url_path else 0
        prefix = '../' * depth
        if url_path:
            return f"{prefix}assets/{url_path}/{filename}"
        return f"assets/{filename}"

    def get_og_image(self, meta):
        """
        Return an absolute URL for the OG image.
        Uses the first entry of 'photos' (slideshow), falling back to 'photo'.
        meta must already be processed by process_meta_photos().
        """
        photo = None
        if meta.get('photos'):
            photo = meta['photos'][0]
        elif meta.get('photo'):
            photo = meta['photo']

        if not photo:
            return None

        # Already an absolute URL (external / OneDrive)
        if photo.startswith('http://') or photo.startswith('https://'):
            return photo

        # Local relative URL like ../../assets/Treks/photo.jpg
        # Strip leading ../ sequences to get the site-root-relative path
        clean = re.sub(r'^(\.\./)+', '', photo)
        return f"{self.site_base_url}/{clean}"

    def get_og_description(self, meta):
        """
        Return a plain-text description for OG tags.
        Takes the first non-empty line of 'intro', truncated to 160 chars.
        """
        intro = meta.get('intro') or ''
        first_line = intro.split('\n')[0].strip()
        if not first_line:
            return None
        return first_line[:157] + '…' if len(first_line) > 160 else first_line

    def process_meta_photos(self, meta, url_path):
        """
        Return a copy of meta with 'photo' and 'photos' values resolved
        to final URLs via resolve_photo_url().
        """
        processed = dict(meta)
        if processed.get('photo'):
            processed['photo'] = self.resolve_photo_url(processed['photo'], url_path)
        if processed.get('photos'):
            processed['photos'] = [
                self.resolve_photo_url(p, url_path) for p in processed['photos']
            ]
        return processed

    def process_custom_syntax(self, content, base_path):
        """Process custom {{...}} syntax in markdown"""

        # YouTube embeds
        def replace_youtube(match):
            video_id = match.group(1)
            # Extract video ID from URL if full URL provided
            if 'youtube.com' in video_id or 'youtu.be' in video_id:
                video_id = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]+)', video_id)
                video_id = video_id.group(1) if video_id else ''
            return f'''<div class="youtube-embed">
                <iframe src="https://www.youtube.com/embed/{video_id}"
                        loading="lazy"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen>
                </iframe>
            </div>'''

        # Local / OneDrive video
        def replace_video(match):
            params = match.group(1).split(',')
            video_url = self.process_url(params[0])
            poster_attr = ''
            for param in params[1:]:
                if 'poster=' in param:
                    poster_url = self.process_url(param.split('=', 1)[1])
                    poster_attr = f'poster="{poster_url}"'

            return f'''<div class="video-container">
                <video controls playsinline preload="metadata" {poster_attr}>
                    <source src="{video_url}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>'''

        # Slideshow (local or OneDrive images)
        def replace_slideshow(match):
            params = match.group(1).split(',')
            images = [p.strip() for p in params if not p.strip().startswith('interval=')]
            interval = 3000  # default 3 seconds

            for param in params:
                if 'interval=' in param:
                    interval = int(param.split('=')[1].strip()) * 1000

            # Store URLs as JSON; JS loads them asynchronously so the browser
            # spinner never spins for slideshow images and no blank <img> is shown.
            urls = [self.process_url(img) for img in images]
            slides_json = json.dumps(urls)

            return (
                f'<div class="slideshow" data-interval="{interval}" '
                f"data-slides='{slides_json}'></div>"
            )

        # Short video – vertical (local or OneDrive)
        def replace_short(match):
            video_url = self.process_url(match.group(1))

            return f'''<div class="short-video">
                <video controls playsinline loop preload="metadata">
                    <source src="{video_url}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>'''

        # Single photo (local or OneDrive)
        def replace_photo(match):
            img_url = self.process_url(match.group(1))
            return (
                f'<div class="photo-embed">'
                f'<img src="{img_url}" alt="Photo" loading="eager" decoding="async">'
                f'</div>'
            )

        # Gallery (local or OneDrive images)
        def replace_gallery(match):
            images = [img.strip() for img in match.group(1).split(',')]
            gallery_html = ''

            for img in images:
                img_url = self.process_url(img)
                gallery_html += (
                    f'<img src="{img_url}" alt="Gallery image" '
                    f'loading="eager" decoding="async">\n'
                )

            return f'<div class="gallery">\n{gallery_html}</div>'
        
        # Quote
        def replace_quote(match):
            params = match.group(1)
            text_match = re.search(r'"([^"]+)"', params)
            author_match = re.search(r'author="([^"]+)"', params)
            
            text = text_match.group(1) if text_match else ''
            author = author_match.group(1) if author_match else ''
            
            author_html = f'<cite>— {author}</cite>' if author else ''
            return f'<blockquote class="styled-quote"><p>{text}</p>{author_html}</blockquote>'
        
        # Apply replacements
        content = re.sub(r'\{\{youtube:\s*([^}]+)\}\}', replace_youtube, content)
        content = re.sub(r'\{\{video:\s*([^}]+)\}\}', replace_video, content)
        content = re.sub(r'\{\{slideshow:\s*([^}]+)\}\}', replace_slideshow, content)
        content = re.sub(r'\{\{short:\s*([^}]+)\}\}', replace_short, content)
        content = re.sub(r'\{\{photo:\s*([^}]+)\}\}', replace_photo, content)
        content = re.sub(r'\{\{gallery:\s*([^}]+)\}\}', replace_gallery, content)
        content = re.sub(r'\{\{quote:\s*([^}]+)\}\}', replace_quote, content)
        
        return content
        
    def copy_data_folder(self, source_folder, dest_folder):
        """Copy .data folder contents to assets"""
        data_folder = source_folder / '.data'
        if data_folder.exists():
            assets_dir = self.output_dir / 'assets' / dest_folder
            assets_dir.mkdir(parents=True, exist_ok=True)
            
            for item in data_folder.iterdir():
                if item.is_file():
                    shutil.copy2(item, assets_dir / item.name)
                    
    def get_folder_structure(self, folder_path, parent_path=''):
        """Recursively get folder structure for navigation"""
        structure = []
        
        for item in sorted(folder_path.iterdir()):
            if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('_'):
                rel_path = os.path.join(parent_path, item.name) if parent_path else item.name
                
                # Check if it's a content page or index page
                has_content = (item / 'content.md').exists()
                meta = self.load_meta(item)
                
                structure.append({
                    'name': item.name,
                    'title': meta.get('title', item.name),
                    'path': rel_path,
                    'has_content': has_content,
                    'meta': meta
                })
                
        return structure
        
    def generate_home_page(self):
        """Generate the home page"""
        meta = self.process_meta_photos(self.load_meta(self.content_dir), '')
        sections = self.get_folder_structure(self.content_dir)

        page_title = meta.get('name', 'Saurav Shah')
        template = self.jinja_env.get_template('home.html')
        html = template.render(
            meta=meta,
            sections=sections,
            current_path='',
            page_title=page_title,
            og_url=self.site_base_url + '/',
            og_image=self.get_og_image(meta),
            og_description=self.get_og_description(meta)
        )
        
        output_file = self.output_dir / 'index.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
            
        print(f"✓ Generated home page: index.html")
        
    def generate_index_page(self, folder_path, url_path):
        """Generate an index/TOC page"""
        meta = self.process_meta_photos(self.load_meta(folder_path), url_path)
        subsections = self.get_folder_structure(folder_path, url_path)

        # Copy .data folder if exists
        self.copy_data_folder(folder_path, url_path)

        page_title = meta.get('title', url_path)
        template = self.jinja_env.get_template('index.html')
        html = template.render(
            meta=meta,
            subsections=subsections,
            current_path=url_path,
            page_title=page_title,
            og_url=self.site_base_url + '/' + url_path + '/',
            og_image=self.get_og_image(meta),
            og_description=self.get_og_description(meta)
        )
        
        # Create output directory
        output_dir = self.output_dir / url_path
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / 'index.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
            
        print(f"✓ Generated index page: {url_path}/index.html")
        
    def generate_content_page(self, folder_path, url_path):
        """Generate a content page"""
        content_file = folder_path / 'content.md'
        meta = self.load_meta(folder_path)
        
        # Load and process content
        front_matter, body = self.load_content(content_file)
        
        # Merge meta and front matter (front matter takes precedence)
        page_meta = self.process_meta_photos({**meta, **front_matter}, url_path)
        
        # Process custom syntax
        body = self.process_custom_syntax(body, url_path)
        
        # Convert markdown to HTML
        html_content = markdown(body, extensions=['extra', 'codehilite', 'fenced_code'])
        
        # Copy .data folder if exists
        self.copy_data_folder(folder_path, url_path)
        
        page_title = page_meta.get('title', url_path)
        template = self.jinja_env.get_template('content.html')
        html = template.render(
            meta=page_meta,
            content=html_content,
            current_path=url_path,
            page_title=page_title,
            og_url=self.site_base_url + '/' + url_path + '/',
            og_image=self.get_og_image(page_meta),
            og_description=self.get_og_description(page_meta)
        )
        
        # Create output directory
        output_dir = self.output_dir / url_path
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / 'index.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
            
        print(f"✓ Generated content page: {url_path}/index.html")
        
    def process_folder(self, folder_path, parent_path=''):
        """Recursively process folders"""
        for item in sorted(folder_path.iterdir()):
            if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('_'):
                rel_path = os.path.join(parent_path, item.name) if parent_path else item.name
                
                # Check if it's a content page or index page
                has_content = (item / 'content.md').exists()
                
                if has_content:
                    self.generate_content_page(item, rel_path)
                else:
                    self.generate_index_page(item, rel_path)
                    
                # Recursively process subfolders
                self.process_folder(item, rel_path)
                
    def generate(self):
        """Main generation process"""
        print("🚀 Starting site generation...")
        
        # Clean and setup
        self.clean_output()
        self.copy_static_files()
        
        # Generate pages
        self.generate_home_page()
        self.process_folder(self.content_dir)
        
        print(f"\n✅ Site generated successfully in '{self.output_dir}/' directory!")
        print(f"📂 Open {self.output_dir}/index.html in your browser to view the site.")

if __name__ == '__main__':
    generator = SiteGenerator()
    generator.generate()
