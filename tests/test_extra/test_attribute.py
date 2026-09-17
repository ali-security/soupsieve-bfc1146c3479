"""Test attribute selectors."""
import time
import soupsieve as sv
from .. import util

# Time budget for parsing a malformed selector. The patterns fail in well under a
# millisecond, but the vulnerable, catastrophically backtracking variants run
# effectively forever, so a generous budget keeps this deterministic everywhere.
PARSE_TIMEOUT = 10


class TestAttribute(util.TestCase):
    """Test attribute selectors."""

    MARKUP = """
    <div id="div">
    <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
    <a id="2" href="http://google.com">Link</a>
    <span id="3">Direct child</span>
    <pre id="pre">
    <span id="4">Child 1</span>
    <span id="5">Child 2</span>
    <span id="6">Child 3</span>
    </pre>
    </div>
    """

    def test_attribute_not_equal_no_quotes(self):
        """Test attribute with value that does not equal specified value (no quotes)."""

        # No quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!=\\35]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_quotes(self):
        """Test attribute with value that does not equal specified value (quotes)."""

        # Quotes
        self.assert_selector(
            self.MARKUP,
            "body [id!='5']",
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_double_quotes(self):
        """Test attribute with value that does not equal specified value (double quotes)."""

        # Double quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!="5"]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def assert_fails_fast(self, selector):
        """Assert a malformed selector fails with a syntax error instead of backtracking forever."""

        start = time.perf_counter()
        with self.assertRaises(sv.SelectorSyntaxError):
            sv.compile(selector)
        elapsed = time.perf_counter() - start
        self.assertLess(
            elapsed,
            PARSE_TIMEOUT,
            'Parsing {!r} took {:.3f}s, exceeding the {}s budget'.format(selector[:16], elapsed, PARSE_TIMEOUT)
        )

    def test_bad_attribute_unclused(self):
        """Test bad attribute fails for syntax error, not timeout error."""

        self.assert_fails_fast('[a="' + ('x' * 300))

    def test_bad_attribute_unclosed_single_quote(self):
        """Test bad attribute with an unclosed single quote fails for syntax error, not timeout error."""

        self.assert_fails_fast("[a='" + ('x' * 300))

    def test_bad_value_list_unclosed_quote(self):
        """Test unclosed quotes in a pseudo class value list fail for syntax error, not timeout error."""

        # `:-soup-contains` and `:lang` reuse the same value sub-pattern as attribute selectors.
        self.assert_fails_fast(':-soup-contains("' + ('x' * 300))
        self.assert_fails_fast(":-soup-contains('" + ('x' * 300))
        self.assert_fails_fast(':lang("' + ('x' * 300))
        self.assert_fails_fast(":lang('" + ('x' * 300))
