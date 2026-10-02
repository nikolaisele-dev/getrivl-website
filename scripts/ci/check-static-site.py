#!/usr/bin/env python3
"""Check the publishable HTML structure and local links without network or npm."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

STRUCTURE = ['+html', '+head', '+title', '-title', '-head', '+body', '-body', '-html']


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.doctype = False
        self.structure = []
        self.references = []

    def handle_decl(self, declaration):
        if declaration.lower() == 'doctype html':
            self.doctype = True

    def handle_starttag(self, tag, attrs):
        if tag in ('html', 'head', 'title', 'body'):
            self.structure.append('+' + tag)
        for name, value in attrs:
            if name in ('href', 'src') and value:
                self.references.append(value)

    def handle_endtag(self, tag):
        if tag in ('html', 'head', 'title', 'body'):
            self.structure.append('-' + tag)


def local_target(root, page, reference):
    if reference.startswith('//'):
        return None
    parts = urlsplit(reference)
    if parts.scheme or not parts.path:
        return None
    path = unquote(parts.path)
    target = root / path.lstrip('/') if path.startswith('/') else page.parent / path
    target = target.resolve()
    try:
        target.relative_to(root)
    except ValueError:
        raise ValueError('path escapes site root') from None
    if target.is_dir() or path.endswith('/'):
        target /= 'index.html'
    return target


def check(root):
    root = root.resolve()
    errors = []
    pages = sorted(root.rglob('*.html'))
    if not pages or root / 'index.html' not in pages:
        return ['index.html: site entry point is missing']
    for path in pages:
        parser = Page()
        try:
            parser.feed(path.read_text(encoding='utf-8'))
            parser.close()
        except (UnicodeError, ValueError) as error:
            errors.append(f'{path.relative_to(root)}: invalid HTML input: {error}')
            continue
        if not parser.doctype or parser.structure != STRUCTURE:
            errors.append(f'{path.relative_to(root)}: missing or invalid basic HTML structure')
        for reference in parser.references:
            try:
                target = local_target(root, path, reference)
            except ValueError as error:
                errors.append(f'{path.relative_to(root)}: {reference}: {error}')
                continue
            if target is not None and not target.is_file():
                errors.append(f'{path.relative_to(root)}: {reference}: local target missing')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    errors = check(args.root)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print('Static HTML structure and local references passed')


if __name__ == '__main__':
    main()
