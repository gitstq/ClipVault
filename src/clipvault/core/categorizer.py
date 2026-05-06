#!/usr/bin/env python3
"""
Content categorizer - automatically classifies clipboard content.
"""

import re
from typing import Tuple


class ContentCategorizer:
    """Smart content categorization engine."""

    # Category constants
    CATEGORY_TEXT = 'text'
    CATEGORY_CODE = 'code'
    CATEGORY_LINK = 'link'
    CATEGORY_PATH = 'path'
    CATEGORY_IMAGE = 'image'
    CATEGORY_EMAIL = 'email'
    CATEGORY_PHONE = 'phone'
    CATEGORY_JSON = 'json'
    CATEGORY_XML = 'xml'
    CATEGORY_HTML = 'html'
    CATEGORY_SQL = 'sql'
    CATEGORY_NUMBER = 'number'
    CATEGORY_IP = 'ip'
    CATEGORY_HEX = 'hex'
    CATEGORY_BASE64 = 'base64'
    CATEGORY_COMMAND = 'command'

    # Patterns for categorization
    URL_PATTERN = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]+|'
        r'www\.[^\s<>"{}|\\^`\[\]]+|'
        r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?',
        re.IGNORECASE
    )

    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    PHONE_PATTERN = re.compile(
        r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{6,}$'
    )

    PATH_PATTERN = re.compile(
        r'^(/[^/\x00]+)+/?$|'           # Unix absolute path
        r'^[a-zA-Z]:\\[^\\/:*?"<>|]+$',  # Windows absolute path
        re.IGNORECASE
    )

    IP_PATTERN = re.compile(
        r'^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$'
    )

    HEX_PATTERN = re.compile(
        r'^(0x)?[0-9a-fA-F]{8,}$'
    )

    BASE64_PATTERN = re.compile(
        r'^[A-Za-z0-9+/]{20,}={0,2}$'
    )

    COMMAND_PATTERN = re.compile(
        r'^(?:sudo\s+)?(?:apt|yum|dnf|brew|npm|pip|pip3|gem|cargo|go|docker|kubectl|git|ssh|scp|rsync|curl|wget|chmod|chown|mv|cp|rm|mkdir|cat|echo|grep|sed|awk|find|tar|zip|unzip|systemctl|journalctl|python|python3|node|java|gcc|make|cmake)\b',
    )

    CODE_INDICATORS = [
        # Programming language patterns
        (r'(?:def|class|import|from|return|if|else|elif|for|while|try|except|finally|with|async|await|yield|lambda|pass|raise|assert)\b', 'python'),
        (r'(?:function|const|let|var|=>|export|import|require|module\.exports|console\.log)\b', 'javascript'),
        (r'(?:func|package|import|type|struct|interface|chan|go\s|goroutine)\b', 'go'),
        (r'(?:fn |let mut|impl |pub |use |mod |match |enum |struct )\b', 'rust'),
        (r'(?:public|private|protected|static|void|int|String|class|interface|extends|implements|new |this\.|super\.)\b', 'java'),
        (r'(?:\$\w+\s*=|<\?php|->|::|namespace|use\s+\w+\\)\b', 'php'),
        (r'(?:printf|scanf|#include|malloc|free|int\s+main|sizeof)\b', 'c'),
        (r'(?:std::|cout|cin|vector|string|namespace|template|typename)\b', 'cpp'),
    ]

    @classmethod
    def categorize(cls, content: str) -> Tuple[str, str]:
        """Categorize clipboard content.

        Args:
            content: The clipboard content string

        Returns:
            Tuple of (category, detected_language_or_detail)
        """
        if not content or not content.strip():
            return cls.CATEGORY_TEXT, ''

        stripped = content.strip()
        first_line = stripped.split('\n')[0].strip()

        # Check specific patterns first (most specific to least specific)

        # Email
        if cls.EMAIL_PATTERN.match(stripped):
            return cls.CATEGORY_EMAIL, 'email'

        # Phone number
        if cls.PHONE_PATTERN.match(stripped) and len(re.sub(r'\D', '', stripped)) >= 7:
            return cls.CATEGORY_PHONE, 'phone'

        # IP address
        if cls.IP_PATTERN.match(stripped):
            return cls.CATEGORY_IP, 'ip'

        # File path
        if cls.PATH_PATTERN.match(stripped):
            # Check if it looks like an image path
            img_exts = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.ico')
            if any(stripped.lower().endswith(ext) for ext in img_exts):
                return cls.CATEGORY_IMAGE, 'image_path'
            return cls.CATEGORY_PATH, 'file_path'

        # URL / Link
        url_match = cls.URL_PATTERN.search(first_line)
        if url_match and len(url_match.group()) > 5:
            return cls.CATEGORY_LINK, 'url'

        # Hex string
        if cls.HEX_PATTERN.match(stripped):
            return cls.CATEGORY_HEX, 'hex'

        # Base64
        if cls.BASE64_PATTERN.match(stripped) and len(stripped) > 40:
            return cls.CATEGORY_BASE64, 'base64'

        # XML (check before HTML - XML must have proper closing tags and no HTML-specific tags)
        if stripped.startswith('<?xml') or (stripped.startswith('<') and stripped.endswith('>') and '</' in stripped
            and not re.search(r'<(?:div|span|p|a|img|html|body|head|table|form|input|button|h[1-6])\b', stripped, re.IGNORECASE)):
            return cls.CATEGORY_XML, 'xml'

        # HTML (check before JSON since HTML can contain angle brackets)
        if re.search(r'<(?:div|span|p|a|img|html|body|head|table|form|input|button|h[1-6])\b', stripped, re.IGNORECASE):
            return cls.CATEGORY_HTML, 'html'

        # JSON
        if cls._is_json(stripped):
            return cls.CATEGORY_JSON, 'json'

        # SQL
        if re.search(r'\b(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|GRANT|REVOKE)\b', stripped, re.IGNORECASE):
            return cls.CATEGORY_SQL, 'sql'

        # Shell command
        if cls.COMMAND_PATTERN.match(stripped):
            return cls.CATEGORY_COMMAND, 'shell'

        # Code detection
        lang = cls._detect_code_language(stripped)
        if lang:
            return cls.CATEGORY_CODE, lang

        # Number
        if re.match(r'^[\d,.\-+\s]+$', stripped):
            return cls.CATEGORY_NUMBER, 'number'

        # Default: text
        return cls.CATEGORY_TEXT, 'plain_text'

    @classmethod
    def _is_json(cls, content: str) -> bool:
        """Check if content is valid JSON."""
        content = content.strip()
        if not (content.startswith('{') or content.startswith('[')):
            return False
        try:
            import json
            json.loads(content)
            return True
        except (json.JSONDecodeError, ValueError):
            return False

    @classmethod
    def _detect_code_language(cls, content: str) -> str:
        """Detect programming language from content patterns."""
        lines = content.split('\n')
        # Check first 5 lines for language indicators
        check_lines = '\n'.join(lines[:5])

        for pattern, lang in cls.CODE_INDICATORS:
            if re.search(pattern, check_lines):
                return lang

        # Check for common code patterns
        code_signs = [
            r'[{}]\s*$',           # Braces at end of line
            r';\s*$',              # Semicolons at end of line
            r'\(\s*\).*\{',       # Function definition
            r'=\s*function\s',    # Function assignment
            r'->\s*\w+',          # Arrow notation
            r'::\s*\w+',          # Scope resolution
            r'\$\w+\s*=',         # Variable assignment
        ]

        code_score = sum(1 for p in code_signs if re.search(p, content, re.MULTILINE))
        if code_score >= 2:
            return 'code'

        # Multi-line content with indentation is likely code
        if len(lines) > 3:
            indented_lines = sum(1 for l in lines if l.startswith((' ', '\t')) and l.strip())
            if indented_lines > len(lines) * 0.4:
                return 'code'

        return ''

    @classmethod
    def generate_title(cls, content: str, category: str) -> str:
        """Generate a short title for a clip."""
        if not content:
            return ''

        lines = content.strip().split('\n')
        first_line = lines[0].strip()

        # Truncate long titles
        max_len = 60
        if len(first_line) > max_len:
            return first_line[:max_len - 3] + '...'

        # For multi-line content, add line count
        if len(lines) > 1:
            return f"{first_line[:50]} (+{len(lines) - 1} lines)"

        return first_line
