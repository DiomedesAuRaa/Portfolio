#!/usr/bin/env python3
"""Build only the career portfolio and explicit legacy route stubs."""
import argparse
import json
import shutil
from pathlib import Path

FILES = (
    'index.html', 'contact.html', 'home.html',
    'news.html', 'weather.html', 'standings.html', 'sports-scores.html',
    'bible.html', 'reddit-digest.html', 'podcast-directory.html',
    'games/2048.html', 'games/minesweeper.html', 'games/snake.html',
    'games/tetris.html', 'games/wordle.html', 'assets/landing.css',
    'podcast-manifest.json', 'reddit-digest.json', 'sports-config.json',
)

def build(root: Path, output: Path) -> int:
    root, output = root.resolve(), output.resolve()
    if output == root or output in root.parents or (root in output.parents and output != root / "_site"):
        raise ValueError('Output must be a separate empty directory')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output must be empty')
    for relative in FILES:
        source = root / relative
        if not source.is_file() or root not in source.resolve().parents or any((root.joinpath(*Path(relative).parts[:n])).is_symlink() for n in range(1, len(Path(relative).parts)+1)):
            raise ValueError('Missing or unsafe career file: ' + relative)
        if source.suffix == '.json':
            json.loads(source.read_text())
    output.mkdir(parents=True, exist_ok=True)
    for relative in FILES:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / relative, target)
    (output / '.nojekyll').touch()
    return len(FILES) + 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(f'Career artifact: {build(args.root, args.output)} files')
