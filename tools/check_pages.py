#!/usr/bin/env python3
"""check_pages.py — check the built Pages site before it is published.

Fails if a page links to another page or anchor in the site that doesn't exist,
or if a page has no <title> or no language. External links are not fetched.

Usage:
    python3 tools/check_pages.py [_site]
"""
import html.parser
import pathlib
import sys
import urllib.parse


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.title, self.lang = set(), [], False, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'a' and a.get('name'):
            self.ids.add(a['name'])
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'title':
            self.title = True
        if tag == 'html' and a.get('lang'):
            self.lang = True


def main(site):
    site = pathlib.Path(site)
    pages = {}
    for f in sorted(site.glob('*.html')):
        p = Page()
        p.feed(f.read_text(encoding='utf-8'))
        pages[f.name] = p
    if 'index.html' not in pages:
        sys.exit(f'{site}/index.html is missing')
    errors = []
    for name, p in pages.items():
        if not p.title:
            errors.append(f'{name}: no <title>')
        if not p.lang:
            errors.append(f'{name}: no lang on <html>')
        for href in p.links:
            u = urllib.parse.urlsplit(href)
            if u.scheme or u.netloc or href.startswith(('mailto:', 'javascript:')):
                continue
            target = u.path or name
            if target not in pages:
                errors.append(f'{name}: link to missing page {href}')
            elif u.fragment and u.fragment not in pages[target].ids and u.fragment != 'top':
                errors.append(f'{name}: link to missing anchor {href}')
    for e in errors:
        print(e)
    print(f'{len(pages)} pages checked, {len(errors)} problems')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '_site'))
