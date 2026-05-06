#!/usr/bin/env python3
"""
Search engine - supports exact, regex, and fuzzy search.
"""

import re
from typing import List, Dict
from difflib import SequenceMatcher


class SearchEngine:
    """Multi-mode search engine for clipboard history."""

    def __init__(self):
        self._min_fuzzy_ratio = 0.4  # Minimum similarity ratio for fuzzy matching

    def search(self, query: str, items: List[Dict],
               mode: str = 'exact', category: str = None) -> List[Dict]:
        """Search items with specified mode.

        Args:
            query: Search query string
            items: List of clip items to search
            mode: Search mode - 'exact', 'regex', 'fuzzy'
            category: Optional category filter

        Returns:
            List of matching items with relevance score
        """
        if not query:
            # No query but category filter may still apply
            if category:
                return [item for item in items if item.get('category') == category]
            return items

        results = []

        for item in items:
            # Category filter
            if category and item.get('category') != category:
                continue

            content = item.get('content', '')
            title = item.get('title', '')

            if mode == 'exact':
                score = self._exact_search(query, content, title)
            elif mode == 'regex':
                score = self._regex_search(query, content, title)
            elif mode == 'fuzzy':
                score = self._fuzzy_search(query, content, title)
            else:
                score = 0

            if score > 0:
                result = dict(item)
                result['_score'] = score
                results.append(result)

        # Sort by score descending
        results.sort(key=lambda x: x['_score'], reverse=True)
        return results

    def _exact_search(self, query: str, content: str, title: str) -> float:
        """Exact substring match with scoring."""
        query_lower = query.lower()
        content_lower = content.lower()
        title_lower = title.lower()

        score = 0.0

        # Title match (higher weight)
        if query_lower in title_lower:
            score += 10.0
            # Exact title match gets even higher score
            if query_lower == title_lower:
                score += 20.0

        # Content match
        if query_lower in content_lower:
            score += 5.0
            # Count occurrences for relevance
            count = content_lower.count(query_lower)
            score += min(count * 0.5, 5.0)

        return score

    def _regex_search(self, query: str, content: str, title: str) -> float:
        """Regex pattern match with scoring."""
        try:
            pattern = re.compile(query, re.IGNORECASE | re.MULTILINE)
        except re.error:
            # Invalid regex, fall back to exact search
            return self._exact_search(query, content, title)

        score = 0.0

        # Title match
        if pattern.search(title):
            score += 10.0

        # Content match
        matches = pattern.findall(content)
        if matches:
            score += 5.0
            score += min(len(matches) * 0.5, 5.0)

        return score

    def _fuzzy_search(self, query: str, content: str, title: str) -> float:
        """Fuzzy search using sequence matching."""
        score = 0.0
        query_lower = query.lower()

        # Check against title
        title_ratio = SequenceMatcher(None, query_lower, title.lower()).ratio()
        if title_ratio >= self._min_fuzzy_ratio:
            score += title_ratio * 15.0

        # Check against first line of content
        first_line = content.split('\n')[0].strip()
        first_line_ratio = SequenceMatcher(None, query_lower, first_line.lower()).ratio()
        if first_line_ratio >= self._min_fuzzy_ratio:
            score += first_line_ratio * 10.0

        # Check against individual words in query
        query_words = query_lower.split()
        if len(query_words) > 1:
            content_lower = content.lower()
            matched_words = sum(1 for w in query_words if w in content_lower)
            word_ratio = matched_words / len(query_words)
            if word_ratio >= 0.5:
                score += word_ratio * 8.0

        return score

    def highlight_matches(self, text: str, query: str, mode: str = 'exact') -> str:
        """Highlight matching portions of text with ANSI codes.

        Args:
            text: Original text
            query: Search query
            mode: Search mode

        Returns:
            Text with ANSI highlight codes
        """
        if not query:
            return text

        RESET = '\033[0m'
        BOLD_YELLOW = '\033[1;33m'

        if mode == 'regex':
            try:
                pattern = re.compile(f'({query})', re.IGNORECASE)
                return pattern.sub(f'{BOLD_YELLOW}\\1{RESET}', text)
            except re.error:
                pass

        # Exact or fuzzy: highlight exact matches
        if mode == 'fuzzy':
            # For fuzzy, highlight individual words that match
            words = query.split()
            result = text
            for word in words:
                if len(word) >= 2:
                    pattern = re.compile(f'({re.escape(word)})', re.IGNORECASE)
                    result = pattern.sub(f'{BOLD_YELLOW}\\1{RESET}', result)
            return result

        # Exact
        pattern = re.compile(f'({re.escape(query)})', re.IGNORECASE)
        return pattern.sub(f'{BOLD_YELLOW}\\1{RESET}', text)
