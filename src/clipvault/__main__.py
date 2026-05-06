#!/usr/bin/env python3
"""
ClipVault - Lightweight Cross-Platform Clipboard Intelligent Management Engine CLI
轻量级跨平台剪贴板智能管理引擎 CLI

Zero external dependencies, pure Python implementation.
Features: Smart categorization, fuzzy search, template system, statistics, TUI browser.
"""

import sys
import argparse
import os

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from clipvault import __version__
from clipvault.core.engine import ClipVaultEngine
from clipvault.core.clipboard import ClipboardManager
from clipvault.ui.tui import ClipVaultTUI
from clipvault.utils.helpers import print_banner, print_success, print_error, print_info


def create_parser():
    """Create the argument parser for CLI commands."""
    parser = argparse.ArgumentParser(
        prog='clipvault',
        description='📋 ClipVault - Lightweight Clipboard Intelligent Management Engine CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  clipvault watch              Start clipboard monitoring
  clipvault list               List clipboard history
  clipvault search "keyword"   Search in clipboard history
  clipvault copy 5             Copy item #5 to clipboard
  clipvault stats              Show clipboard statistics
  clipvault tui                Launch TUI browser
  clipvault template list      List saved templates
  clipvault template add name  Save current clipboard as template
        """
    )
    parser.add_argument('-v', '--version', action='version', version=f'ClipVault v{__version__}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # watch command
    watch_parser = subparsers.add_parser('watch', help='🔍 Start clipboard monitoring')
    watch_parser.add_argument('-i', '--interval', type=float, default=0.5,
                              help='Polling interval in seconds (default: 0.5)')
    watch_parser.add_argument('--silent', action='store_true',
                              help='Run silently without notifications')

    # list command
    list_parser = subparsers.add_parser('list', help='📋 List clipboard history')
    list_parser.add_argument('-n', '--limit', type=int, default=20,
                             help='Number of items to show (default: 20)')
    list_parser.add_argument('-c', '--category', type=str, default=None,
                             help='Filter by category (text/code/link/path/image)')
    list_parser.add_argument('--all', action='store_true',
                             help='Show all items without limit')
    list_parser.add_argument('--json', action='store_true',
                             help='Output in JSON format')

    # search command
    search_parser = subparsers.add_parser('search', help='🔎 Search clipboard history')
    search_parser.add_argument('query', type=str, help='Search query (supports regex)')
    search_parser.add_argument('-f', '--fuzzy', action='store_true',
                               help='Use fuzzy search')
    search_parser.add_argument('-c', '--category', type=str, default=None,
                               help='Filter by category')
    search_parser.add_argument('-n', '--limit', type=int, default=20,
                               help='Max results (default: 20)')

    # copy command
    copy_parser = subparsers.add_parser('copy', help='📋 Copy item to clipboard')
    copy_parser.add_argument('id', type=int, help='Item ID to copy')
    copy_parser.add_argument('-p', '--pin', action='store_true',
                             help='Pin item after copying')

    # delete command
    delete_parser = subparsers.add_parser('delete', help='🗑️ Delete clipboard item')
    delete_parser.add_argument('id', type=int, help='Item ID to delete')
    delete_parser.add_argument('--all', action='store_true',
                               help='Delete all clipboard history')

    # pin command
    pin_parser = subparsers.add_parser('pin', help='📌 Pin/unpin clipboard item')
    pin_parser.add_argument('id', type=int, help='Item ID to pin/unpin')

    # stats command
    stats_parser = subparsers.add_parser('stats', help='📊 Show clipboard statistics')
    stats_parser.add_argument('--json', action='store_true',
                              help='Output in JSON format')

    # template command
    template_parser = subparsers.add_parser('template', help='📝 Manage templates')
    template_parser.add_argument('action', choices=['list', 'add', 'use', 'delete'],
                                 help='Template action')
    template_parser.add_argument('name', nargs='?', default=None,
                                 help='Template name')

    # export command
    export_parser = subparsers.add_parser('export', help='💾 Export clipboard history')
    export_parser.add_argument('-f', '--format', choices=['json', 'csv', 'txt'],
                               default='json', help='Export format (default: json)')
    export_parser.add_argument('-o', '--output', type=str, default=None,
                               help='Output file path')

    # import command
    import_parser = subparsers.add_parser('import', help='📥 Import clipboard history')
    import_parser.add_argument('file', type=str, help='Input file path')
    import_parser.add_argument('-f', '--format', choices=['json', 'csv'],
                               default='json', help='Import format (default: json)')

    # clear command
    clear_parser = subparsers.add_parser('clear', help='🧹 Clear clipboard history')
    clear_parser.add_argument('--confirm', action='store_true',
                              help='Skip confirmation prompt')

    # tui command
    tui_parser = subparsers.add_parser('tui', help='🖥️ Launch TUI browser')

    # config command
    config_parser = subparsers.add_parser('config', help='⚙️ Manage configuration')
    config_parser.add_argument('action', choices=['show', 'set', 'reset'],
                               help='Config action')
    config_parser.add_argument('key', nargs='?', default=None, help='Config key')
    config_parser.add_argument('value', nargs='?', default=None, help='Config value')

    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        return 0

    engine = ClipVaultEngine()

    try:
        if args.command == 'watch':
            engine.watch_clipboard(interval=args.interval, silent=args.silent)

        elif args.command == 'list':
            engine.list_items(
                limit=args.limit if not args.all else None,
                category=args.category,
                json_output=args.json
            )

        elif args.command == 'search':
            engine.search_items(
                query=args.query,
                fuzzy=args.fuzzy,
                category=args.category,
                limit=args.limit
            )

        elif args.command == 'copy':
            engine.copy_item(args.id, pin=args.pin)

        elif args.command == 'delete':
            if args.all:
                engine.clear_all(confirm=True)
            else:
                engine.delete_item(args.id)

        elif args.command == 'pin':
            engine.toggle_pin(args.id)

        elif args.command == 'stats':
            engine.show_stats(json_output=args.json)

        elif args.command == 'template':
            engine.manage_template(args.action, args.name)

        elif args.command == 'export':
            engine.export_history(format=args.format, output=args.output)

        elif args.command == 'import':
            engine.import_history(filepath=args.file, format=args.format)

        elif args.command == 'clear':
            engine.clear_all(confirm=args.confirm)

        elif args.command == 'tui':
            tui = ClipVaultTUI(engine)
            tui.run()

        elif args.command == 'config':
            engine.manage_config(args.action, args.key, args.value)

    except KeyboardInterrupt:
        print_info("\n👋 ClipVault stopped by user.")
        return 0
    except Exception as e:
        print_error(f"Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
