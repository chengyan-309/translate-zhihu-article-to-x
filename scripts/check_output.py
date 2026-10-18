#!/usr/bin/env python3
"""Check copy-ready Post/Comment formatting, not factual or linguistic quality."""

import argparse
import re
import sys
import unittest
from pathlib import Path


BLOCK = re.compile(r"```markdown[ \t]*\n(.*?)\n```", re.DOTALL)
WORD = re.compile(r"\b[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*\b")
URL = re.compile(r"https?://|www\.", re.IGNORECASE)
HASHTAG = re.compile(r"(?<!\w)#[\w\u3400-\u9fff]+")
EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\u20e3\ufe0f]"
)


def check(text):
    errors = []
    warnings = []
    blocks = list(BLOCK.finditer(text))
    if len(blocks) != 2 or len(re.findall(r"^```", text, re.MULTILINE)) != 4:
        return ["Expected exactly two fenced markdown blocks."], [], {}

    post, comment = (match.group(1).strip() for match in blocks)
    outside = [text[:blocks[0].start()].strip(),
               text[blocks[0].end():blocks[1].start()].strip(),
               text[blocks[1].end():].strip()]
    if outside != ["Post", "Comment", ""]:
        errors.append("Outside the blocks, use only Post and Comment labels.")

    lines = post.splitlines()
    if not lines or not re.fullmatch(r"# \*\*[^\n]+\*\*", lines[0]):
        errors.append("The first Post line must be # **Title**.")
    if any(line.startswith("#") for line in lines[1:]):
        errors.append("Use bold subheadings, not additional heading levels.")
    if URL.search(post) or re.search(r"\[[^\]]+\]\([^\)]+\)", post):
        errors.append("Move all Post URLs and Markdown links to Comment.")

    for name, block in (("Post", post), ("Comment", comment)):
        if "\u2014" in block:
            errors.append(f"{name} contains an em dash.")
        if EMOJI.search(block):
            errors.append(f"{name} contains an emoji or emoji presentation marker.")
        # A URL fragment is not a social hashtag.
        without_urls = re.sub(r"https?://\S+", "", block)
        if HASHTAG.search(without_urls):
            errors.append(f"{name} contains a hashtag.")
        if re.search(r"^\s*\|?\s*:?-{3,}:?\s*\|", block, re.MULTILINE):
            errors.append(f"{name} contains a Markdown table.")

    if "Zhihu author" in post:
        errors.append("Use Zhihu contributor, not Zhihu author.")
    if "Zhihu contributor" in post:
        for match in re.finditer(r"Zhihu contributor", post):
            if not re.match(r"Zhihu contributor \*[^*\n]+\*(?!\*)",
                            post[match.start():]):
                errors.append("Contributor nicknames must use single-asterisk italics.")
                break
    else:
        warnings.append("No contributor attribution; check whether this task requires one.")

    for paragraph in re.split(r"\n\s*\n", post):
        words = len(WORD.findall(paragraph))
        if words > 55:
            warnings.append(f"Dense paragraph ({words} English words): review or split.")
    word_count = len(WORD.findall(post))
    if word_count > 400:
        warnings.append("Over 400 words: confirm the source or user request justifies it.")
    if not URL.search(comment):
        warnings.append("No source URL; valid only for a source supplied without a public link.")
    return errors, warnings, {"post_words": word_count, "post_characters": len(post)}


SAMPLE = """Post

```markdown
# **A Model Test With a Caveat**

Zhihu contributor *测试员甲* found more consistent coding.

**Fewer steps, not a measured speedup**

One task used 20% of the previous steps. The harness also changed.
```

Comment

```markdown
Original Zhihu answer:
https://example.org/source
```
"""


class OutputChecks(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(check(SAMPLE)[0], [])

    def test_url_fragment_allowed(self):
        self.assertEqual(check(SAMPLE.replace("/source", "/source#method"))[0], [])

    def test_source_file_warning_not_failure(self):
        text = SAMPLE.replace("https://example.org/source", "Author-provided document.")
        errors, warnings, _ = check(text)
        self.assertEqual(errors, [])
        self.assertTrue(warnings)

    def test_bad_formats(self):
        changes = [
            ("One task", "\U0001f539 One task"),
            ("One task", "1\ufe0f\u20e3 One task"),
            ("One task", "#AI One task"),
            ("also changed", "also\u2014changed"),
            ("One task", "https://example.org One task"),
            ("# **A Model", "## **A Model"),
            ("Zhihu contributor", "Zhihu author"),
            ("*测试员甲*", "**测试员甲**"),
            ("One task", "| A | B |\n|---|---|\nOne task"),
            ("**Fewer steps, not a measured speedup**", "## Fewer steps"),
            ("Post\n", "Here you go!\nPost\n"),
        ]
        for before, after in changes:
            with self.subTest(after=after):
                self.assertTrue(check(SAMPLE.replace(before, after, 1))[0])

    def test_missing_block(self):
        self.assertTrue(check(SAMPLE.split("Comment")[0])[0])

    def test_dense_paragraph_warning(self):
        text = SAMPLE.replace("One task", " ".join(["word"] * 56) + " One task")
        self.assertTrue(any("Dense paragraph" in w for w in check(text)[1]))

    def test_three_blocks(self):
        self.assertTrue(check(SAMPLE + "\n```markdown\nextra\n```\n")[0])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner().run(
            unittest.defaultTestLoader.loadTestsFromTestCase(OutputChecks))
        return 0 if result.wasSuccessful() else 1
    if args.draft is None:
        parser.error("provide a draft file or --self-test")
    try:
        errors, warnings, stats = check(args.draft.read_text(encoding="utf-8"))
    except OSError as exc:
        parser.error(str(exc))
    if stats:
        print(f"Post: {stats['post_words']} English words; "
              f"{stats['post_characters']} characters.")
    for message in errors:
        print("ERROR:", message)
    for message in warnings:
        print("REVIEW:", message)
    print("FAIL" if errors else "PASS (format only; facts require source review)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
