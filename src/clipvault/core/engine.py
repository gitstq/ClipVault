#!/usr/bin/env python3
"""
Main engine - orchestrates all ClipVault operations.
"""

import json
import csv
import io
import os
import time
import sys
from typing import Optional

from clipvault.core.clipboard import ClipboardManager
from clipvault.core.storage import StorageManager
from clipvault.core.categorizer import ContentCategorizer
from clipvault.core.search import SearchEngine
from clipvault.utils.helpers import (
    print_success, print_error, print_info, print_warning,
    print_table, format_size, format_time
)


class ClipVaultEngine:
    """Main engine that orchestrates clipboard management operations."""

    def __init__(self):
        self.storage = StorageManager()
        self.clipboard = ClipboardManager()
        self.categorizer = ContentCategorizer()
        self.search_engine = SearchEngine()

    # ─── Clipboard Monitoring ────────────────────────────────────

    def watch_clipboard(self, interval: float = 0.5, silent: bool = False):
        """Monitor clipboard for changes and auto-save."""
        if not self.clipboard.is_available():
            print_error("Clipboard access not available on this system.")
            print_info("Install xclip/xsel (Linux), or use macOS/Windows for native support.")
            return

        tool = self.clipboard.get_tool_name()
        print_info(f"🔍 Monitoring clipboard (tool: {tool}, interval: {interval}s)")
        print_info("Press Ctrl+C to stop...")

        last_content = self.clipboard.get_text()
        last_hash = StorageManager._compute_hash(last_content) if last_content else ''

        try:
            while True:
                time.sleep(interval)
                current = self.clipboard.get_text()
                if not current:
                    continue

                current_hash = StorageManager._compute_hash(current)
                if current_hash != last_hash:
                    category, detail = self.categorizer.categorize(current)
                    title = self.categorizer.generate_title(current, category)
                    clip_id = self.storage.add_clip(
                        content=current,
                        category=category,
                        title=title,
                        meta={'detail': detail, 'source': 'monitor'}
                    )

                    if not silent:
                        icon = self._category_icon(category)
                        print_success(f"  {icon} [{category.upper()}] #{clip_id}: {title}")

                    last_content = current
                    last_hash = current_hash
        except KeyboardInterrupt:
            print_info("\n👋 Clipboard monitoring stopped.")

    # ─── List Operations ─────────────────────────────────────────

    def list_items(self, limit: int = 20, category: str = None,
                   json_output: bool = False):
        """List clipboard history items."""
        items = self.storage.list_clips(limit=limit, category=category)

        if not items:
            print_info("📋 Clipboard history is empty. Start monitoring with: clipvault watch")
            return

        if json_output:
            # Remove internal fields for JSON output
            output = []
            for item in items:
                output.append({
                    'id': item['id'],
                    'content': item['content'],
                    'category': item['category'],
                    'title': item['title'],
                    'pinned': bool(item['pinned']),
                    'copy_count': item['copy_count'],
                    'created_at': item['created_at'],
                })
            print(json.dumps(output, indent=2, ensure_ascii=False))
            return

        # Display as table
        headers = ['ID', '📌', 'Category', 'Title', 'Size', 'Copies', 'Time']
        rows = []
        for item in items:
            icon = '📌' if item['pinned'] else '  '
            cat_icon = self._category_icon(item['category'])
            size = format_size(len(item['content']))
            copies = str(item['copy_count'])
            time_str = format_time(item['created_at'])
            title = item['title'] or item['content'][:40]
            rows.append([
                str(item['id']),
                icon,
                f"{cat_icon} {item['category']}",
                title,
                size,
                copies,
                time_str
            ])

        print_table(headers, rows)
        print_info(f"Showing {len(items)} items (total: {self.storage.get_stats()['total']})")

    # ─── Search Operations ───────────────────────────────────────

    def search_items(self, query: str, fuzzy: bool = False,
                     category: str = None, limit: int = 20):
        """Search clipboard history."""
        all_items = self.storage.list_clips(limit=None, category=category)
        mode = 'fuzzy' if fuzzy else 'exact'

        results = self.search_engine.search(
            query=query,
            items=all_items,
            mode=mode,
            category=category
        )

        results = results[:limit]

        if not results:
            print_info(f"🔎 No results found for: {query}")
            return

        print_success(f"🔎 Found {len(results)} result(s) for: {query}")
        headers = ['ID', 'Score', 'Category', 'Title', 'Preview']
        rows = []
        for item in results:
            cat_icon = self._category_icon(item['category'])
            preview = item['content'][:50].replace('\n', ' ')
            rows.append([
                str(item['id']),
                f"{item['_score']:.1f}",
                f"{cat_icon} {item['category']}",
                item['title'] or '-',
                preview
            ])

        print_table(headers, rows)

    # ─── Copy Operations ─────────────────────────────────────────

    def copy_item(self, clip_id: int, pin: bool = False):
        """Copy a stored item to the system clipboard."""
        item = self.storage.get_clip(clip_id)
        if not item:
            print_error(f"Item #{clip_id} not found.")
            return

        success = self.clipboard.set_text(item['content'])
        if success:
            self.storage.increment_copy_count(clip_id)
            if pin:
                self.storage.toggle_pin(clip_id)
            icon = self._category_icon(item['category'])
            print_success(f"📋 Copied #{clip_id} {icon} [{item['category']}] to clipboard")
            print_info(f"   {item['title'] or item['content'][:60]}")
        else:
            print_error("Failed to copy to clipboard.")

    # ─── Delete Operations ───────────────────────────────────────

    def delete_item(self, clip_id: int):
        """Delete a clipboard item."""
        success = self.storage.delete_clip(clip_id)
        if success:
            print_success(f"🗑️ Deleted item #{clip_id}")
        else:
            print_error(f"Item #{clip_id} not found.")

    def clear_all(self, confirm: bool = False):
        """Clear all clipboard history."""
        if not confirm:
            print_warning("⚠️  This will delete ALL clipboard history!")
            try:
                response = input("   Are you sure? (y/N): ").strip().lower()
                if response != 'y':
                    print_info("Cancelled.")
                    return
            except (EOFError, KeyboardInterrupt):
                print_info("\nCancelled.")
                return

        count = self.storage.clear_all()
        print_success(f"🧹 Cleared {count} items from clipboard history.")

    # ─── Pin Operations ──────────────────────────────────────────

    def toggle_pin(self, clip_id: int):
        """Toggle pin status of a clipboard item."""
        item = self.storage.get_clip(clip_id)
        if not item:
            print_error(f"Item #{clip_id} not found.")
            return

        success = self.storage.toggle_pin(clip_id)
        if success:
            new_status = 'pinned' if not item['pinned'] else 'unpinned'
            print_success(f"📌 Item #{clip_id} {new_status}")

    # ─── Statistics ──────────────────────────────────────────────

    def show_stats(self, json_output: bool = False):
        """Show clipboard statistics."""
        stats = self.storage.get_stats()

        if json_output:
            print(json.dumps(stats, indent=2, ensure_ascii=False))
            return

        print("\n📊 ClipVault Statistics")
        print("─" * 40)
        print(f"  📋 Total Items:     {stats['total']}")
        print(f"  📌 Pinned Items:    {stats['pinned']}")
        print(f"  🕐 Last 24h Items:  {stats['recent_24h']}")
        print()

        if stats['categories']:
            print("  📂 By Category:")
            for cat in stats['categories']:
                icon = self._category_icon(cat['category'])
                print(f"     {icon} {cat['category']:<12} {cat['cnt']:>5} items  ({cat['total_copies']} copies)")
            print()

        if stats['top_items']:
            print("  🔥 Most Copied:")
            for item in stats['top_items'][:5]:
                print(f"     #{item['id']:<5} {item['title'][:35]:<35} ({item['copy_count']} copies)")
            print()

    # ─── Template Operations ─────────────────────────────────────

    def manage_template(self, action: str, name: str = None):
        """Manage clipboard templates."""
        if action == 'list':
            templates = self.storage.list_templates()
            if not templates:
                print_info("📝 No templates saved. Use 'clipvault template add <name>' to create one.")
                return

            print("📝 Saved Templates:")
            for t in templates:
                icon = self._category_icon(t['category'])
                preview = t['content'][:50].replace('\n', ' ')
                print(f"  {icon} {t['name']:<20} [{t['category']}] {preview}")
            return

        if action == 'add':
            if not name:
                print_error("Template name is required. Usage: clipvault template add <name>")
                return

            content = self.clipboard.get_text()
            if not content:
                print_error("Clipboard is empty. Copy some content first.")
                return

            category, detail = self.categorizer.categorize(content)
            self.storage.add_template(name, content, category)
            print_success(f"📝 Template '{name}' saved [{category}]")
            return

        if action == 'use':
            if not name:
                print_error("Template name is required. Usage: clipvault template use <name>")
                return

            template = self.storage.get_template(name)
            if not template:
                print_error(f"Template '{name}' not found.")
                return

            success = self.clipboard.set_text(template['content'])
            if success:
                print_success(f"📝 Template '{name}' copied to clipboard")
            else:
                print_error("Failed to copy to clipboard.")
            return

        if action == 'delete':
            if not name:
                print_error("Template name is required.")
                return

            success = self.storage.delete_template(name)
            if success:
                print_success(f"📝 Template '{name}' deleted")
            else:
                print_error(f"Template '{name}' not found.")

    # ─── Export/Import ───────────────────────────────────────────

    def export_history(self, format: str = 'json', output: str = None):
        """Export clipboard history."""
        items = self.storage.export_all()

        if not items:
            print_info("📋 No items to export.")
            return

        if format == 'json':
            content = json.dumps(items, indent=2, ensure_ascii=False)
            ext = '.json'
        elif format == 'csv':
            output_buf = io.StringIO()
            writer = csv.DictWriter(output_buf, fieldnames=[
                'id', 'content', 'category', 'title', 'pinned', 'copy_count', 'created_at'
            ])
            writer.writeheader()
            for item in items:
                writer.writerow({
                    'id': item['id'],
                    'content': item['content'],
                    'category': item['category'],
                    'title': item['title'],
                    'pinned': item['pinned'],
                    'copy_count': item['copy_count'],
                    'created_at': item['created_at'],
                })
            content = output_buf.getvalue()
            ext = '.csv'
        else:  # txt
            lines = []
            for item in items:
                lines.append(f"--- Item #{item['id']} [{item['category']}] ---")
                lines.append(f"Title: {item['title']}")
                lines.append(f"Pinned: {bool(item['pinned'])}")
                lines.append(f"Copies: {item['copy_count']}")
                lines.append(f"Content:\n{item['content']}")
                lines.append("")
            content = '\n'.join(lines)
            ext = '.txt'

        if output:
            filepath = output
        else:
            filepath = f"clipvault_export_{int(time.time())}{ext}"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print_success(f"💾 Exported {len(items)} items to {filepath}")

    def import_history(self, filepath: str, format: str = 'json'):
        """Import clipboard history from file."""
        if not os.path.exists(filepath):
            print_error(f"File not found: {filepath}")
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                if format == 'json':
                    items = json.load(f)
                elif format == 'csv':
                    reader = csv.DictReader(f)
                    items = list(reader)
                else:
                    print_error(f"Unsupported import format: {format}")
                    return

            count = self.storage.import_clips(items)
            print_success(f"📥 Imported {count} items from {filepath}")
        except Exception as e:
            print_error(f"Import failed: {e}")

    # ─── Config ──────────────────────────────────────────────────

    def manage_config(self, action: str, key: str = None, value: str = None):
        """Manage configuration."""
        if action == 'show':
            config = self.storage.get_all_config()
            if not config:
                print_info("⚙️  No custom configuration set.")
                return

            print("⚙️  ClipVault Configuration:")
            for k, v in config.items():
                print(f"  {k}: {v}")
            return

        if action == 'set':
            if not key or not value:
                print_error("Key and value are required. Usage: clipvault config set <key> <value>")
                return
            self.storage.set_config(key, value)
            print_success(f"⚙️  Set {key} = {value}")
            return

        if action == 'reset':
            if not key:
                print_error("Key is required. Usage: clipvault config reset <key>")
                return
            self.storage.set_config(key, '')
            print_success(f"⚙️  Reset {key}")
            return

    # ─── Helpers ─────────────────────────────────────────────────

    @staticmethod
    def _category_icon(category: str) -> str:
        """Get emoji icon for a category."""
        icons = {
            'text': '📝',
            'code': '💻',
            'link': '🔗',
            'path': '📁',
            'image': '🖼️',
            'email': '📧',
            'phone': '📱',
            'json': '📋',
            'xml': '📄',
            'html': '🌐',
            'sql': '🗃️',
            'number': '🔢',
            'ip': '🌐',
            'hex': '🔢',
            'base64': '🔐',
            'command': '⌨️',
        }
        return icons.get(category, '📝')
