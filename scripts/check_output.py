#!/usr/bin/env python3
"""Check copy-ready Post/Comment formatting, not factual or linguistic quality."""

import argparse
import re
import sys
import unittest
from pathlib import Path


BLOCK = re.compile(r"^```markdown[ \t]*\n(.*?)\n```[ \t]*$", re.DOTALL | re.MULTILINE)
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
    if len(blocks) < 2 or len(re.findall(r"^\s*```", text, re.MULTILINE)) != 2 * len(blocks):
        return ["Use one markdown block per Post and a final Comment block."], [], {}

    labels, bodies = [], []
    previous_end = 0
    for match in blocks:
        labels.append(text[previous_end:match.start()].strip())
        bodies.append(match.group(1).strip())
        previous_end = match.end()
    if text[previous_end:].strip():
        errors.append("Do not add text after the final Comment block.")
    post_count = len(bodies) - 1
    expected = (["Post"] if post_count == 1 else
                [f"Post {i}" for i in range(1, post_count + 1)]) + ["Comment"]
    if labels != expected:
        errors.append("Use Post/Comment, or consecutive Post 1, Post 2, ... followed by Comment.")
    if any(not body for body in bodies):
        errors.append("Post and Comment blocks must not be empty.")
    posts, comment = bodies[:-1], bodies[-1]
    post = "\n\n".join(posts)
    for i, body in enumerate(posts, 1):
        for line_index, line in enumerate(body.splitlines()):
            if re.match(r"^\s*#", line) and not (
                line_index == 0 and re.fullmatch(r"# \*\*[^\n]+\*\*", line)
            ):
                errors.append(f"Post {i}: optional title must be # **Title**; use bold subheadings.")
        if URL.search(body) or re.search(r"\[[^\]]+\]\([^\)]+\)", body):
            errors.append(f"Post {i}: move URLs and Markdown links to Comment.")

    for name, block in zip(expected, bodies):
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

    per_post_words = []
    for i, body in enumerate(posts, 1):
        per_post_words.append(len(WORD.findall(body)))
        for paragraph in re.split(r"\n\s*\n", body):
            words = len(WORD.findall(paragraph))
            if words > 55:
                warnings.append(f"Post {i}: Dense paragraph ({words} English words): review or split.")
        if per_post_words[-1] > 400:
            warnings.append(f"Post {i}: over 400 words; confirm the source or user request justifies it.")
    if post_count > 1 and per_post_words[0] > 90:
        warnings.append("Thread opening exceeds 90 words: review entry cost without dropping necessary scope.")
    word_count = sum(per_post_words)
    if not URL.search(comment):
        warnings.append("No source URL; valid only for a source supplied without a public link.")
    return errors, warnings, {
        "mode": "single" if post_count == 1 else "thread",
        "post_count": post_count,
        "post_words": word_count,
        "post_characters": sum(len(body) for body in posts),
        "per_post_words": per_post_words,
        "per_post_characters": [len(body) for body in posts],
        "opening_post_words": per_post_words[0],
    }


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

    def test_title_and_question_optional(self):
        text = SAMPLE.replace("# **A Model Test With a Caveat**\n\n", "")
        self.assertEqual(check(text)[0], [])

    def thread(self):
        return SAMPLE.replace("Post\n", "Post 1\n", 1).replace(
            "Comment\n", "Post 2\n\n```markdown\nThe test harness also changed.\n```\n\nComment\n", 1)

    def test_thread_valid_and_counts(self):
        errors, _, stats = check(self.thread())
        self.assertEqual(errors, [])
        self.assertEqual(stats["mode"], "thread")
        self.assertEqual(stats["post_count"], 2)
        self.assertEqual(stats["post_words"], sum(stats["per_post_words"]))

    def test_thread_rejects_bad_numbering(self):
        for label in ("Post 1", "Post 3", "Post"):
            with self.subTest(label=label):
                self.assertTrue(check(self.thread().replace("Post 2\n", label + "\n"))[0])

    def test_links_checked_in_every_post(self):
        self.assertTrue(check(self.thread().replace(
            "The test harness", "https://example.org/source The test harness"))[0])

    def test_thread_requires_final_comment(self):
        self.assertTrue(check(self.thread().replace("Comment\n", "Post 3\n"))[0])

    def test_empty_body_rejected(self):
        self.assertTrue(check(SAMPLE.replace(
            "Original Zhihu answer:\nhttps://example.org/source", ""))[0])

    def test_long_opening_is_warning_not_failure(self):
        text = self.thread().replace("One task", " ".join(["word"] * 100) + " One task")
        errors, warnings, _ = check(text)
        self.assertEqual(errors, [])
        self.assertTrue(any("opening exceeds" in warning for warning in warnings))

    def test_trailing_prose_rejected(self):
        self.assertTrue(check(SAMPLE + "Extra explanation")[0])

    def test_malformed_fence_rejected(self):
        self.assertTrue(check(SAMPLE.replace("```markdown", "```text", 1))[0])

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
        print(f"Mode: {stats['mode']}; {stats['post_count']} Post block(s); "
              f"{stats['post_words']} English words total (excluding Comment).")
        for i, (words, characters) in enumerate(zip(
                stats['per_post_words'], stats['per_post_characters']), 1):
            print(f"Post {i}: {words} English words; {characters} raw characters.")
        print("Counts are editorial diagnostics, not X platform-limit validation.")
    for message in errors:
        print("ERROR:", message)
    for message in warnings:
        print("REVIEW:", message)
    print("FAIL" if errors else "PASS (format only; facts require source review)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
