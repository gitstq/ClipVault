#!/usr/bin/env python3
"""
Tests for ClipVault - Clipboard Intelligent Management Engine.
"""

import unittest
import os
import sys
import tempfile
import json
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from clipvault.core.storage import StorageManager
from clipvault.core.categorizer import ContentCategorizer
from clipvault.core.search import SearchEngine
from clipvault.utils.helpers import format_size, format_time, truncate_text, strip_ansi


class TestStorageManager(unittest.TestCase):
    """Test storage operations."""

    def setUp(self):
        """Create a temporary database for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.storage = StorageManager(self.db_path)

    def tearDown(self):
        """Clean up temporary database."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_add_and_get_clip(self):
        """Test adding and retrieving a clip."""
        clip_id = self.storage.add_clip("Hello World", "text", "Test")
        self.assertIsNotNone(clip_id)

        clip = self.storage.get_clip(clip_id)
        self.assertEqual(clip['content'], "Hello World")
        self.assertEqual(clip['category'], "text")
        self.assertEqual(clip['title'], "Test")

    def test_deduplication(self):
        """Test that duplicate content returns same ID."""
        id1 = self.storage.add_clip("Same content", "text")
        id2 = self.storage.add_clip("Same content", "text")
        self.assertEqual(id1, id2)

    def test_list_clips(self):
        """Test listing clips."""
        self.storage.add_clip("First", "text")
        self.storage.add_clip("Second", "code")
        self.storage.add_clip("Third", "link")

        items = self.storage.list_clips()
        self.assertEqual(len(items), 3)

        # Test category filter
        code_items = self.storage.list_clips(category="code")
        self.assertEqual(len(code_items), 1)

    def test_search_clips(self):
        """Test searching clips."""
        self.storage.add_clip("Python code example", "code")
        self.storage.add_clip("JavaScript code tutorial", "code")
        self.storage.add_clip("Random text", "text")

        results = self.storage.search_clips("Python")
        self.assertEqual(len(results), 1)

        results = self.storage.search_clips("code")
        # "code" appears in content of first two items
        self.assertGreaterEqual(len(results), 2)

    def test_delete_clip(self):
        """Test deleting a clip."""
        clip_id = self.storage.add_clip("To delete", "text")
        self.assertTrue(self.storage.delete_clip(clip_id))
        self.assertIsNone(self.storage.get_clip(clip_id))

    def test_toggle_pin(self):
        """Test pinning/unpinning."""
        clip_id = self.storage.add_clip("Pinned item", "text")
        self.assertTrue(self.storage.toggle_pin(clip_id))
        clip = self.storage.get_clip(clip_id)
        self.assertEqual(clip['pinned'], 1)

        self.assertTrue(self.storage.toggle_pin(clip_id))
        clip = self.storage.get_clip(clip_id)
        self.assertEqual(clip['pinned'], 0)

    def test_clear_all(self):
        """Test clearing all clips."""
        self.storage.add_clip("Item 1", "text")
        self.storage.add_clip("Item 2", "text")
        count = self.storage.clear_all()
        self.assertEqual(count, 2)
        self.assertEqual(len(self.storage.list_clips()), 0)

    def test_template_operations(self):
        """Test template CRUD."""
        self.storage.add_template("greeting", "Hello, World!", "text")
        template = self.storage.get_template("greeting")
        self.assertEqual(template['content'], "Hello, World!")

        templates = self.storage.list_templates()
        self.assertEqual(len(templates), 1)

        self.storage.delete_template("greeting")
        self.assertIsNone(self.storage.get_template("greeting"))

    def test_config_operations(self):
        """Test config get/set."""
        self.storage.set_config("theme", "dark")
        self.assertEqual(self.storage.get_config("theme"), "dark")

        config = self.storage.get_all_config()
        self.assertEqual(config["theme"], "dark")

    def test_export_import(self):
        """Test export and import."""
        self.storage.add_clip("Export test 1", "text")
        self.storage.add_clip("Export test 2", "code")

        exported = self.storage.export_all()
        self.assertEqual(len(exported), 2)

        # Import into new storage
        new_db = os.path.join(self.temp_dir, 'new.db')
        new_storage = StorageManager(new_db)
        count = new_storage.import_clips(exported)
        self.assertEqual(count, 2)

        os.remove(new_db)

    def test_stats(self):
        """Test statistics."""
        self.storage.add_clip("Text item", "text")
        self.storage.add_clip("Code item", "code")
        self.storage.add_clip("Link item", "link")

        stats = self.storage.get_stats()
        self.assertEqual(stats['total'], 3)
        self.assertEqual(len(stats['categories']), 3)

    def test_copy_count(self):
        """Test copy count increment."""
        clip_id = self.storage.add_clip("Counted item", "text")
        self.storage.increment_copy_count(clip_id)
        self.storage.increment_copy_count(clip_id)
        clip = self.storage.get_clip(clip_id)
        self.assertEqual(clip['copy_count'], 2)


class TestContentCategorizer(unittest.TestCase):
    """Test content categorization."""

    def test_text_category(self):
        """Test plain text categorization."""
        cat, detail = ContentCategorizer.categorize("Hello, this is plain text.")
        self.assertEqual(cat, 'text')

    def test_code_python(self):
        """Test Python code detection."""
        code = "def hello():\n    print('world')"
        cat, detail = ContentCategorizer.categorize(code)
        self.assertEqual(cat, 'code')
        self.assertEqual(detail, 'python')

    def test_code_javascript(self):
        """Test JavaScript code detection."""
        code = "const x = () => {\n  console.log('hello');\n};"
        cat, detail = ContentCategorizer.categorize(code)
        self.assertEqual(cat, 'code')
        self.assertEqual(detail, 'javascript')

    def test_link_detection(self):
        """Test URL detection."""
        cat, detail = ContentCategorizer.categorize("https://github.com/clipvault")
        self.assertEqual(cat, 'link')

    def test_email_detection(self):
        """Test email detection."""
        cat, detail = ContentCategorizer.categorize("user@example.com")
        self.assertEqual(cat, 'email')

    def test_path_detection(self):
        """Test file path detection."""
        cat, detail = ContentCategorizer.categorize("/home/user/documents/file.txt")
        self.assertEqual(cat, 'path')

    def test_image_path_detection(self):
        """Test image path detection."""
        cat, detail = ContentCategorizer.categorize("/home/user/photo.png")
        self.assertEqual(cat, 'image')

    def test_json_detection(self):
        """Test JSON detection."""
        cat, detail = ContentCategorizer.categorize('{"key": "value", "num": 42}')
        self.assertEqual(cat, 'json')

    def test_html_detection(self):
        """Test HTML detection."""
        # Use a more specific HTML tag that won't match XML pattern
        cat, detail = ContentCategorizer.categorize("<div class='container'><p>Hello</p></div>")
        self.assertEqual(cat, 'html')

    def test_sql_detection(self):
        """Test SQL detection."""
        cat, detail = ContentCategorizer.categorize("SELECT * FROM users WHERE active = 1")
        self.assertEqual(cat, 'sql')

    def test_command_detection(self):
        """Test shell command detection."""
        cat, detail = ContentCategorizer.categorize("sudo apt install python3")
        self.assertEqual(cat, 'command')

    def test_empty_content(self):
        """Test empty content."""
        cat, detail = ContentCategorizer.categorize("")
        self.assertEqual(cat, 'text')

    def test_generate_title(self):
        """Test title generation."""
        title = ContentCategorizer.generate_title("Short title", "text")
        self.assertEqual(title, "Short title")

        long_text = "A" * 100
        title = ContentCategorizer.generate_title(long_text, "text")
        self.assertTrue(title.endswith("..."))
        self.assertTrue(len(title) <= 63)


class TestSearchEngine(unittest.TestCase):
    """Test search functionality."""

    def setUp(self):
        self.engine = SearchEngine()
        self.items = [
            {'id': 1, 'content': 'Python function example', 'category': 'code', 'title': 'Python'},
            {'id': 2, 'content': 'JavaScript tutorial', 'category': 'code', 'title': 'JavaScript'},
            {'id': 3, 'content': 'https://github.com/repo', 'category': 'link', 'title': 'GitHub'},
            {'id': 4, 'content': 'Random text content', 'category': 'text', 'title': 'Random'},
        ]

    def test_exact_search(self):
        """Test exact search."""
        results = self.engine.search("Python", self.items, mode='exact')
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['id'], 1)

    def test_regex_search(self):
        """Test regex search."""
        results = self.engine.search(r'function|tutorial', self.items, mode='regex')
        self.assertEqual(len(results), 2)

    def test_fuzzy_search(self):
        """Test fuzzy search."""
        results = self.engine.search("pythn", self.items, mode='fuzzy')
        self.assertTrue(len(results) > 0)

    def test_category_filter(self):
        """Test category filtering."""
        # Empty query with category filter returns all items in that category
        results = self.engine.search("", self.items, mode='exact', category='code')
        self.assertEqual(len(results), 2)

    def test_highlight_matches(self):
        """Test match highlighting."""
        text = "Python is great"
        highlighted = self.engine.highlight_matches(text, "Python", mode='exact')
        self.assertIn("Python", highlighted)
        self.assertNotEqual(highlighted, text)  # Should have ANSI codes


class TestHelpers(unittest.TestCase):
    """Test utility helper functions."""

    def test_format_size(self):
        """Test size formatting."""
        self.assertEqual(format_size(100), "100B")
        self.assertEqual(format_size(2048), "2.0KB")
        self.assertEqual(format_size(1048576), "1.0MB")

    def test_format_time(self):
        """Test time formatting."""
        now = time.time()
        result = format_time(now)
        self.assertIn("ago", result)

    def test_truncate_text(self):
        """Test text truncation."""
        self.assertEqual(truncate_text("Hello", 10), "Hello")
        self.assertTrue(truncate_text("A" * 100, 10).endswith("..."))

    def test_strip_ansi(self):
        """Test ANSI code stripping."""
        text = "\033[32mHello\033[0m"
        self.assertEqual(strip_ansi(text), "Hello")


if __name__ == '__main__':
    unittest.main(verbosity=2)
