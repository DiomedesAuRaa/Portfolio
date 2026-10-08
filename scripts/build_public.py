#!/usr/bin/env python3
"""Copy only explicitly approved public files into a clean Pages artifact."""
import argparse
import json
import shutil
from pathlib import Path

PAGES = ('index.html', 'home.html', 'contact.html', 'news.html', 'weather.html', 'standings.html', 'sports-scores.html', 'bible.html', 'podcast-directory.html', 'reddit-digest.html', 'games/2048.html', 'games/minesweeper.html', 'games/snake.html', 'games/tetris.html', 'games/wordle.html')
DATA = ('sports-config.json', 'podcast-manifest.json', 'reddit-digest.json')

def build(root, output):
    root, output = root.resolve(), output.resolve()
    if output == root or root in output.parents and output.name != '_site':
        raise ValueError('Use _site in the repository or an external output directory')
    if output in root.parents:
        raise ValueError('Output cannot contain source directory')
    files = list(PAGES + DATA)
    assets = root / 'assets'
    if assets.exists():
        files.extend(str(path.relative_to(root)) for path in sorted(assets.glob('*')) if path.suffix in ('.css', '.js'))
    for relative in files:
        source = root / relative
        if not source.is_file() or source.is_symlink() or root not in source.resolve().parents:
            raise ValueError('Missing or unsafe public asset: ' + relative)
        if source.suffix == '.json':
            json.loads(source.read_text())
    # Never recursively delete a caller-selected directory. Clear only dedicated output.
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output must be empty; choose a fresh directory')
    output.mkdir(parents=True, exist_ok=True)
    for relative in files:
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / relative, destination)
    (output / '.nojekyll').touch()
    print('Public artifact: %d files' % (len(files) + 1))
    return files

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.root, args.output)
