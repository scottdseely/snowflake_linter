"""
Rule: Keyword Case Detection

Detects SQL keywords that are not uppercase.

This implements a simple heuristic scanner over lines of SQL and flags
occurrences of core SQL keywords that are not fully uppercase in the source.
"""

import re
from typing import List, Dict
try:
    from utils.sql_utils import normalize_sql
except ImportError:
    from ..utils.sql_utils import normalize_sql


class RuleKeywordCase:
    RULE_NAME = "KEYWORD_CASE"
    RULE_DESCRIPTION = "Ensure core SQL keywords are uppercase"
    SEVERITY = "INFO"

    # Core keywords to check (basic list)
    KEYWORDS = [
        "select",
        "from",
        "where",
        "group by",
        "order by",
        "limit",
        "having",
        "join",
        "left join",
        "right join",
        "inner join",
        "outer join",
        "on",
    ]

    @staticmethod
    def _mask_quotes(line: str) -> str:
        """
        Replace contents within single or double quotes with spaces so that
        regex matching does not accidentally match keywords inside string
        literals. Keeps length same so indices remain valid.
        """
        def _replacer(m):
            return ' ' * (len(m.group(0)))

        # Mask single-quoted strings
        line = re.sub(r"'([^']|'')*'", _replacer, line)
        # Mask double-quoted strings
        line = re.sub(r'"([^"]|"")*"', _replacer, line)
        return line

    @staticmethod
    def check(sql: str, file_name: str = "") -> List[Dict]:
        """
        Check SQL source for keywords not in uppercase.

        Returns a list of violation dictionaries.
        """
        violations: List[Dict] = []

        normalized_sql = normalize_sql(sql)
        lines = normalized_sql.split('\n')

        # Precompile patterns for each keyword and sort by length (longer first)
        patterns = []
        for kw in RuleKeywordCase.KEYWORDS:
            parts = kw.split()
            if len(parts) == 1:
                pat = re.compile(r"\b" + re.escape(parts[0]) + r"\b", re.IGNORECASE)
            else:
                pat = re.compile(r"\b" + r"\s+".join(map(re.escape, parts)) + r"\b", re.IGNORECASE)
            patterns.append((kw, pat))

        # Sort patterns by keyword length descending so multi-word patterns take precedence
        patterns.sort(key=lambda x: len(x[0]), reverse=True)

        for line_num, raw_line in enumerate(lines, start=1):
            # Mask quoted content so keywords inside strings are ignored
            line = RuleKeywordCase._mask_quotes(raw_line)

            accepted_spans = []  # list of (start, end) spans already matched

            for kw, pat in patterns:
                for m in pat.finditer(line):
                    s, e = m.start(), m.end()
                    # Skip if this match falls inside an already accepted span
                    in_span = False
                    for (as_, ae) in accepted_spans:
                        if s >= as_ and e <= ae:
                            in_span = True
                            break
                    if in_span:
                        continue

                    matched_text = raw_line[s:e]
                    # If matched text is not all uppercase, flag it
                    if matched_text != matched_text.upper():
                        violations.append({
                            "rule": RuleKeywordCase.RULE_NAME,
                            "severity": RuleKeywordCase.SEVERITY,
                            "line": line_num,
                            "file": file_name,
                            "message": f"Keyword '{matched_text}' should be uppercase.",
                            "description": RuleKeywordCase.RULE_DESCRIPTION,
                        })
                        accepted_spans.append((s, e))

        return violations

    @staticmethod
    def format_report(violations: List[Dict]) -> str:
        if not violations:
            return f"✓ No {RuleKeywordCase.RULE_NAME} violations found\n"

        report = f"\n{'='*60}\n"
        report += f"Rule: {RuleKeywordCase.RULE_NAME}\n"
        report += f"Description: {RuleKeywordCase.RULE_DESCRIPTION}\n"
        report += f"Severity: {RuleKeywordCase.SEVERITY}\n"
        report += f"{'='*60}\n"
        report += f"Found {len(violations)} violation(s):\n\n"
        for v in violations:
            report += f"  File: {v.get('file', 'unknown')}\n"
            report += f"  Line {v['line']}: {v['message']}\n\n"
        return report
