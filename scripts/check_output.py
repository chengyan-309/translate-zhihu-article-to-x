#!/usr/bin/env python3
"""Check copy-ready Post/Comment formatting, not factual or linguistic quality."""

import argparse
import re
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


WORD = re.compile(r"\b[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*\b")
URL = re.compile(r"https?://|www\.", re.IGNORECASE)
HASHTAG = re.compile(r"(?<!\w)#[\w\u3400-\u9fff]+")
EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\u20e3\ufe0f]"
)


def parse_sections(text):
    """Parse copyable prose separately from image attachments and ALT blocks."""
    lines = text.splitlines()
    cursor = 0

    def skip_blank():
        nonlocal cursor
        while cursor < len(lines) and not lines[cursor].strip():
            cursor += 1

    def take_line():
        nonlocal cursor
        skip_blank()
        if cursor >= len(lines):
            raise ValueError("Unexpected end of draft.")
        value = lines[cursor].strip()
        cursor += 1
        return value

    def fenced(language):
        nonlocal cursor
        if take_line() != f"```{language}":
            raise ValueError(f"Expected a {language} code block.")
        start = cursor
        while cursor < len(lines) and lines[cursor].strip() != "```":
            if lines[cursor].lstrip().startswith("```"):
                raise ValueError("Do not nest or use malformed code fences.")
            cursor += 1
        if cursor == len(lines):
            raise ValueError("Unclosed code block.")
        value = "\n".join(lines[start:cursor]).strip()
        cursor += 1
        return value

    sections = []
    while True:
        skip_blank()
        if cursor == len(lines):
            return sections
        label = take_line()
        if not re.fullmatch(r"Post(?: [1-9]\d*)?|Comment", label):
            raise ValueError("Use Post/Comment or consecutive Post 1, Post 2, ... labels.")
        body = fenced("markdown")
        images = []
        while True:
            skip_blank()
            if cursor == len(lines) or not lines[cursor].startswith("Image "):
                break
            image_label = take_line()
            match = re.fullmatch(r"Image ([1-9]\d*)", image_label)
            if not match:
                raise ValueError("Expected Image 1, Image 2, ... in upload order.")
            number = int(match.group(1))
            image = re.fullmatch(r"!\[([^\]\n]+)\]\((<[^>\n]+>|[^\s)]+)\)", take_line())
            if not image:
                raise ValueError(f"{label} {image_label}: embed an actual Markdown image.")
            source_line = take_line()
            prefix = f"Image source {number}: "
            if not source_line.startswith(prefix) or not source_line[len(prefix):].strip():
                raise ValueError(f"{label} {image_label}: provide Image source {number}.")
            if take_line() != f"ALT {number}":
                raise ValueError(f"{label} {image_label}: expected matching ALT {number}.")
            images.append({"number": number, "description": image.group(1),
                           "target": image.group(2).removeprefix("<").removesuffix(">"),
                           "source": source_line[len(prefix):], "alt": fenced("text")})
        sections.append({"label": label, "body": body, "images": images})


def check(text, media_base=None, allow_text_only_thread=False):
    errors = []
    warnings = []
    try:
        sections = parse_sections(text)
    except ValueError as exc:
        return [str(exc)], [], {}
    if len(sections) < 2:
        return ["Use one markdown block per Post and a final Comment block."], [], {}
    labels = [section["label"] for section in sections]
    bodies = [section["body"] for section in sections]
    post_count = len(bodies) - 1
    expected = (["Post"] if post_count == 1 else
                [f"Post {i}" for i in range(1, post_count + 1)]) + ["Comment"]
    if labels != expected:
        errors.append("Use Post/Comment, or consecutive Post 1, Post 2, ... followed by Comment.")
    if any(not body for body in bodies):
        errors.append("Post and Comment blocks must not be empty.")
    if sections[-1]["images"]:
        errors.append("Comment is a source reply; attach images to their Post instead.")
    if post_count == 1 and sections[0]["images"]:
        errors.append("Single-post format is Post/Comment; image bundles use Thread format.")
    if post_count > 1 and allow_text_only_thread:
        warnings.append("Text-only Thread override: use only for an explicit user request.")
    image_counts = []
    for i, section in enumerate(sections[:-1], 1):
        attachments = section["images"]
        image_counts.append(len(attachments))
        if post_count > 1 and not attachments and not allow_text_only_thread:
            errors.append(f"Post {i}: each Thread Post requires an image and English ALT.")
        if len(attachments) > 4:
            errors.append(f"Post {i}: use at most four images per Post.")
        for expected_number, item in enumerate(attachments, 1):
            name = f"Post {i} Image {expected_number}"
            if item["number"] != expected_number:
                errors.append(f"{name}: number images consecutively, restarting at 1 per Post.")
            if not re.search(r"[A-Za-z]", item["alt"]):
                errors.append(f"{name}: provide nonempty English ALT.")
            if URL.search(item["alt"]):
                errors.append(f"{name}: keep source links outside ALT.")
            target = item["target"]
            try:
                parsed = urlsplit(target)
            except ValueError:
                errors.append(f"{name}: malformed image URL.")
                continue
            if parsed.scheme in ("http", "https") and parsed.netloc:
                warnings.append(f"{name}: remote image was not fetched; verify it visually and check availability.")
            elif parsed.scheme:
                errors.append(f"{name}: use a local file path or HTTP(S) image URL.")
            elif media_base is not None:
                path = Path(unquote(target))
                if not path.is_absolute():
                    path = Path(media_base) / path
                try:
                    if not path.is_file() or path.stat().st_size == 0:
                        errors.append(f"{name}: local image is missing or empty: {target}")
                except OSError:
                    errors.append(f"{name}: cannot read local image: {target}")
            else:
                warnings.append(f"{name}: local image existence not checked without media_base.")
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
        "per_post_images": image_counts,
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
    MEDIA = """Image 1
![Synthetic source-based card](card.png)

Image source 1: Editorial graphic based on the synthetic test source.

ALT 1
```text
A source-based card states the test condition and its limitation.
```

"""

    def test_valid(self):
        self.assertEqual(check(SAMPLE)[0], [])

    def test_title_and_question_optional(self):
        text = SAMPLE.replace("# **A Model Test With a Caveat**\n\n", "")
        self.assertEqual(check(text)[0], [])

    def thread(self):
        draft = SAMPLE.replace("Post\n", "Post 1\n", 1).replace(
            "Comment\n", "Post 2\n\n```markdown\nThe test harness also changed.\n```\n\nComment\n", 1)
        return draft.replace("Post 2\n", self.MEDIA + "Post 2\n", 1).replace(
            "Comment\n", self.MEDIA + "Comment\n", 1)

    def test_thread_valid_and_counts(self):
        errors, _, stats = check(self.thread())
        self.assertEqual(errors, [])
        self.assertEqual(stats["mode"], "thread")
        self.assertEqual(stats["post_count"], 2)
        self.assertEqual(stats["post_words"], sum(stats["per_post_words"]))
        self.assertEqual(stats["per_post_images"], [1, 1])

    def test_every_post_requires_media(self):
        text = self.thread().replace(self.MEDIA, "", 1)
        self.assertTrue(any("Post 1" in e and "requires" in e for e in check(text)[0]))

    def test_text_only_requires_explicit_override(self):
        text = self.thread().replace(self.MEDIA, "")
        self.assertTrue(check(text)[0])
        errors, warnings, _ = check(text, allow_text_only_thread=True)
        self.assertEqual(errors, [])
        self.assertTrue(any("explicit user request" in w for w in warnings))

    def test_alt_and_image_source_are_required(self):
        for before, after in [
            ("ALT 1", "ALT 2"),
            ("Image source 1: Editorial graphic based on the synthetic test source.", ""),
            ("A source-based card states the test condition and its limitation.", ""),
            ("A source-based card states the test condition and its limitation.", "这是中文描述。"),
            ("![Synthetic source-based card](card.png)", "Suggested image: card.png"),
        ]:
            with self.subTest(after=after):
                self.assertTrue(check(self.thread().replace(before, after, 1))[0])

    def test_multiple_images_keep_alt_pairing(self):
        second = self.MEDIA.replace("Image 1", "Image 2").replace(
            "Image source 1", "Image source 2").replace("ALT 1", "ALT 2")
        text = self.thread().replace(self.MEDIA, self.MEDIA + second, 1)
        self.assertEqual(check(text)[0], [])
        self.assertEqual(check(text)[2]["per_post_images"], [2, 1])

    def test_numbering_restarts_per_post(self):
        media = self.MEDIA.replace("Image 1", "Image 2").replace(
            "Image source 1", "Image source 2").replace("ALT 1", "ALT 2")
        self.assertTrue(check(self.thread().replace(self.MEDIA, media, 1))[0])

    def test_media_cannot_be_batched_under_comment(self):
        text = self.thread().replace(self.MEDIA, "", 1) + "\n" + self.MEDIA
        self.assertTrue(any("Comment" in e for e in check(text)[0]))

    def test_media_not_counted_as_post_words(self):
        first = check(self.thread())[2]
        changed = self.thread().replace("A source-based card states the test condition and its limitation.",
                                        "An expanded description " + "detail " * 80)
        self.assertEqual(first["per_post_words"], check(changed)[2]["per_post_words"])

    def test_local_image_paths_and_missing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "card.svg"
            path.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            text = self.thread().replace("card.png", "card.svg")
            self.assertEqual(check(text, media_base=directory)[0], [])
            absolute = self.thread().replace("card.png", str(path))
            self.assertEqual(check(absolute, media_base=directory)[0], [])
            path.unlink()
            self.assertTrue(any("missing or empty" in e for e in check(text, media_base=directory)[0]))

    def test_local_path_with_spaces(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "a card.svg"
            path.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            text = self.thread().replace("(card.png)", f"(<{path}>)")
            self.assertEqual(check(text, media_base=directory)[0], [])

    def test_remote_image_warns_without_fetching(self):
        text = self.thread().replace("card.png", "https://example.org/card.png")
        errors, warnings, _ = check(text)
        self.assertEqual(errors, [])
        self.assertTrue(any("not fetched" in w for w in warnings))

    def test_unsupported_image_scheme(self):
        self.assertTrue(check(self.thread().replace("card.png", "javascript:alert"))[0])

    def test_malformed_image_url_reports_error(self):
        self.assertTrue(check(self.thread().replace("card.png", "https://[invalid/image.png"))[0])

    def test_bundled_thread_example(self):
        reference_dir = Path(__file__).resolve().parent.parent / "references"
        text = (reference_dir / "examples.md").read_text(encoding="utf-8")
        section = text.split("## 示例三：", 1)[1].split("## 钩子边界", 1)[0]
        draft = section[section.index("Post 1\n"):].strip()
        errors, _, stats = check(draft, media_base=reference_dir)
        self.assertEqual(errors, [])
        self.assertEqual(stats["per_post_images"], [1, 1, 1])

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
    parser.add_argument("--allow-text-only-thread", action="store_true",
                        help="Only when the user explicitly requested a text-only Thread.")
    args = parser.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner().run(
            unittest.defaultTestLoader.loadTestsFromTestCase(OutputChecks))
        return 0 if result.wasSuccessful() else 1
    if args.draft is None:
        parser.error("provide a draft file or --self-test")
    try:
        errors, warnings, stats = check(
            args.draft.read_text(encoding="utf-8"), media_base=args.draft.resolve().parent,
            allow_text_only_thread=args.allow_text_only_thread)
    except OSError as exc:
        parser.error(str(exc))
    if stats:
        print(f"Mode: {stats['mode']}; {stats['post_count']} Post block(s); "
              f"{stats['post_words']} English words total (excluding Comment).")
        for i, (words, characters) in enumerate(zip(
                stats['per_post_words'], stats['per_post_characters']), 1):
            print(f"Post {i}: {words} English words; {characters} raw characters.")
        print("Counts are editorial diagnostics, not X platform-limit validation.")
        print(f"Images per Post: {stats['per_post_images']}")
    for message in errors:
        print("ERROR:", message)
    for message in warnings:
        print("REVIEW:", message)
    print("FAIL" if errors else "PASS (structure only; facts, image/ALT accuracy, and rendering require review)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
