#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Parslepy shell to help building parselets on the command-line
"""

from __future__ import print_function
import re
import json

import parslepy
import lxml


def get_prop_name(key):
    return re.split('[?]?[(]', key)[0]


class ParslepyShellSession(object):
    def __init__(self, doc_path, outfile):
        self.doc_path = doc_path
        self.outfile = outfile
        self.doc = self.load_document(doc_path)
        self.selector = parslepy.selectors.DefaultSelectorHandler()
        self.parselet_obj = {}

    def load_document(self, doc_path):
        parser = lxml.etree.HTMLParser()
        return lxml.etree.parse(doc_path, parser=parser).getroot()

    def extract_expr(self, expr):
        # TODO: the current output for this may be too terse.
        # In a real-world scenario I'd want to have the option of seeing
        # the actual HTML too, not only the text
        return self.selector.extract(self.doc, self.selector.make(expr))

    def record_simple_property(self, name, expr):
        self.parselet_obj[name] = expr

    def record_aggregating_property(self, name, expr, is_list=False):
        key = '%s(%s)' % (name, expr)
        self.parselet_obj[key] = [{}] if is_list else {}

    def _get_key_for_property(self, name):
        for key in self.parselet_obj:
            if get_prop_name(key) == name:
                return key

    def record_nested_property(self, parent_name, name, expr):
        key = self._get_key_for_property(parent_name)

        if not key:
            valid_keys = [get_prop_name(k) for k in self.parselet_obj]
            raise ValueError('Invalid property: %s (valid properties: %r)' %
                             (parent_name, valid_keys))

        target_obj = self.parselet_obj[key]
        if isinstance(target_obj, list):
            target_obj = target_obj[0]

        target_obj[name] = expr

    def write(self):
        with open(self.outfile, 'w') as fp:
            json.dump(self.parselet_obj, fp, indent=4)
            print('Wrote parselet: %s' % self.outfile)

    def extract(self):
        return parslepy.Parselet(self.parselet_obj).extract(self.doc)


def _run(args):
    """Run IPython shell with a few functions to help create a parselet"""
    from IPython import embed as _embed

    global _session
    _session = ParslepyShellSession(args.input, args.parselet)

    # Here are functions available in the shell:
    def fetch(url, parselet=None):
        global _session
        _session = ParslepyShellSession(url, parselet or args.parselet)

    def test(expr):
        return _session.extract_expr(expr)

    def add(name, expr):
        _session.record_simple_property(name, expr)

    def add_list(name, expr):
        _session.record_aggregating_property(name, expr, is_list=True)

    def add_object(name, expr):
        _session.record_aggregating_property(name, expr, is_list=False)

    def add_nested(parent_name, name, expr):
        _session.record_nested_property(parent_name, name, expr)

    def save():
        _session.write()

    def extract():
        return _session.extract()

    banner = """
    Available functions:

    test(expression)                 - test a CSS or XPath expression
    fetch(url, [parselet])           - fetch a new URL, optionally starts new parselet
    extract()                        - run the extraction using current parselet rules
    add(name, expr)                  - add a simple property to current parselet
    add_list(name, expr)             - add a list property to current parselet
    add_object(name, expr)           - add an object property to current parselet
    add_nested(parent, name, expr)   - add a property to a list or object property
    save()                           - saves current parselet to disk
    \n"""
    _embed(banner1=banner)


if '__main__' == __name__:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parselet', help='Path to Parsley script')
    parser.add_argument('input', help='URL or file')

    args = parser.parse_args()
    _run(args)
