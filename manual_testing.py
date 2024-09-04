# pylint: skip-file
# ruff: noqa

# python src/plist_helper -h

from plist_helper import *
# from plist_helper import PlistHelper

pl = PlistHelper(INFO_TYPE_FILE, "test.plist")
# pl.insert(['jmlinsert1'], 'foooo')
# pl.get_data()
# pl.insert(['jmlinsert1'], 'should not go in')
# pl.get_data()
# pl.insert(['jmlindict1'], {})
# pl.get_data()
pl.insert(
    ["jmlindict2"],
    {"foo": ["foo"], "bar": ["foo", "bar"], "baz": ["foo", "bar", "baz"]},
)
pl.get_data()
pl.insert(
    ["jmlindict3"],
    {
        "foo": ["foo", 0, 0],
        "bar": ["foo", "bar", 1],
        "baz": ["foo", "bar", "baz", open],
    },
)
pl.get_data()
pl.insert(["jmlinarray1"])

pl = PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><string></string></plist>")
pl.merge(PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><string>foo</string></plist>"), overwrite=False)
pl.print()

pl = PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><string></string></plist>")
pl.merge(PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><string>foo</string></plist>"), overwrite=True)
pl.print()

pl = PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><string></string></plist>")
pl.merge(PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><integer>1000</integer></plist>"), overwrite=False)
pl.print()

pl = PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><string></string></plist>")
pl.merge(PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><integer>1000</integer></plist>"), overwrite=True)
pl.print()

pl = PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><string></string></plist>")
pl.merge(PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><dict></dict></plist>"), overwrite=False)
pl.print()

pl = PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><string></string></plist>")
pl.merge(
    PlistHelper(
        INFO_TYPE_REPRESENTATION,
        b"<plist><dict><key>foo</key><string>bar</string></dict></plist>",
    ),
    overwrite=True,
)
pl.print()

pl = PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><string></string></plist>")
pl.merge(
    PlistHelper(
        INFO_TYPE_REPRESENTATION,
        b"<plist><dict><key>one</key><integer>1</integer></dict></plist>",
    ),
    overwrite=True,
)
pl.print()

pl = PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><string></string></plist>")
pl.merge(PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><dict></dict></plist>"), source_path="foo")
pl.print()

pl = PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><string></string></plist>")
pl.merge(PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><dict></dict></plist>"), target_path="foo")
pl.print()

pl = PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><string></string></plist>")
pl.merge(PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><array></array></plist>"), overwrite=False)
pl.print()

pl = PlistHelper(INFO_TYPE_REPRESENTATION, b"<plist><string></string></plist>")
pl.merge(
    PlistHelper(
        INFO_TYPE_REPRESENTATION,
        b"<plist><array><string>one</string><string>two</string><string>three</string></array></plist>",
    ),
    overwrite=True,
)
pl.print()

pl = PlistHelper(
    INFO_TYPE_REPRESENTATION,
    b"<plist><array><string>one</string><string>two</string><string>three</string></array></plist>",
)
pl.merge(
    PlistHelper(
        INFO_TYPE_REPRESENTATION,
        b"<plist><array><string>cero</string><string>one</string><string>dos</string><string>three</string><string>quatro</string></array></plist>",
    ),
    overwrite=True,
)
pl.print()

pl = PlistHelper(INFO_TYPE_FILE, "test.plist")
pl.merge(PlistHelper(INFO_TYPE_FILE, "test_update.plist"), overwrite=False)
pl.print()

pl = PlistHelper(INFO_TYPE_FILE, "test.plist")
pl.merge(PlistHelper(INFO_TYPE_FILE, "test_update.plist"), overwrite=True)
pl.print()
