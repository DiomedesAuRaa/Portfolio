import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import fetch_feeds

spec = importlib.util.spec_from_file_location('build_public', Path(__file__).resolve().parents[1] / 'scripts/build_public.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class FeedTests(unittest.TestCase):
    def test_failure_retains_original_data_and_timestamp(self):
        old = [{'name': 'Show', 'episodes': [{'title': 'Old', 'audioUrl': 'https://example.com/old.mp3'}], 'generatedAt': 'original'}]
        def fail(url):
            raise OSError('failure')
        actual = fetch_feeds.refresh({'podcasts': [{'name': 'Show', 'feed_url': 'https://example.com/rss'}]}, old, fetch=fail, now='attempt')
        self.assertEqual(actual[0]['episodes'], old[0]['episodes'])
        self.assertEqual(actual[0]['generatedAt'], 'original')
        self.assertEqual(actual[0]['lastAttemptAt'], 'attempt')
        self.assertEqual(actual[0]['fetchStatus'], 'stale')

    def test_success_ignores_non_audio_and_unsafe_enclosures(self):
        xml = b'<rss version="2.0"><channel><title>Feed</title><item><title>Article</title><link>https://example.com/article</link></item><item><title>Bad</title><enclosure url="javascript:alert(1)" /></item><item><title>Episode</title><enclosure url="https://example.com/audio.mp3" type="audio/mpeg" /></item></channel></rss>'
        actual = fetch_feeds.refresh({'podcasts': [{'name': 'Show', 'feed_url': 'https://example.com/rss'}]}, [], fetch=lambda url: xml, now='now')
        self.assertEqual([item['title'] for item in actual[0]['episodes']], ['Episode'])
        self.assertEqual(actual[0]['generatedAt'], 'now')
        self.assertEqual(actual[0]['fetchStatus'], 'ok')

    def test_legacy_retention_does_not_invent_success_time(self):
        def fail(url):
            raise ValueError('invalid response')
        actual = fetch_feeds.refresh({'podcasts': [{'name': 'Show', 'feed_url': 'https://example.com/rss'}]}, [{'name': 'Show', 'episodes': [{'title': 'Old'}]}], fetch=fail, now='now')
        self.assertIsNone(actual[0]['generatedAt'])

    def test_rejects_credentials_or_active_url_schemes(self):
        for url in ['https://user:secret@example.com/rss', 'file:///etc/passwd', 'javascript:alert(1)']:
            with self.assertRaises(ValueError):
                fetch_feeds.public_url(url)

class ArtifactValidationTests(unittest.TestCase):
    def test_rejects_script_audio_and_extra_fields(self):
        spec = importlib.util.spec_from_file_location('validate_podcast', Path(__file__).resolve().parents[1] / 'scripts/validate_podcast.py')
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        show = {'name': 'Show', 'episodes': [{'title': 'Episode', 'date': '', 'dateSort': '', 'audioUrl': 'https://example.com/a.mp3'}], 'generatedAt': '2026-10-08T00:00:00+00:00', 'lastAttemptAt': '2026-10-08T00:00:00+00:00', 'fetchStatus': 'ok'}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'manifest.json'
            path.write_text(json.dumps([show]))
            validator.validate(path)
            show['episodes'][0]['audioUrl'] = 'javascript:alert(1)'
            path.write_text(json.dumps([show]))
            with self.assertRaises(ValueError):
                validator.validate(path)
            show['episodes'][0]['audioUrl'] = 'https://example.com/a.mp3'
            show['private'] = 'unexpected'
            path.write_text(json.dumps([show]))
            with self.assertRaises(ValueError):
                validator.validate(path)

class PublicBoundaryTests(unittest.TestCase):
    def test_only_allowed_runtime_assets_are_published(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'source'
            root.mkdir()
            for name in builder.PAGES + builder.DATA:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{}' if path.suffix == '.json' else '<html></html>')
            (root / 'assets').mkdir()
            (root / 'assets/ui.css').write_text('body{}')
            for name in ['AGENTS.md', '.env', 'sub.yaml', 'fetch_feeds.py', 'backup.zip']:
                (root / name).write_text('private')
            (root / 'assets/private.json').write_text('private')
            out = Path(directory) / 'public'
            builder.build(root, out)
            actual = {str(p.relative_to(out)) for p in out.rglob('*') if p.is_file()}
            self.assertEqual(actual, set(builder.PAGES + builder.DATA) | {'assets/ui.css', '.nojekyll'})

    def test_symlink_and_nonempty_output_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'source'
            root.mkdir()
            for name in builder.PAGES + builder.DATA:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{}' if path.suffix == '.json' else '<html></html>')
            out = Path(directory) / 'public'
            out.mkdir()
            (out / 'retain.txt').write_text('retain')
            with self.assertRaises(ValueError):
                builder.build(root, out)
            self.assertTrue((out / 'retain.txt').exists())
            (root / 'index.html').unlink()
            (root / 'index.html').symlink_to(root / 'home.html')
            with self.assertRaises(ValueError):
                builder.build(root, Path(directory) / 'other')

if __name__ == '__main__':
    unittest.main()
