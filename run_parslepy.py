#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import pprint
import parslepy


def main(args):
    with open(args.parselet) as fp:
        extractor = parslepy.Parselet.from_jsonfile(fp, debug=args.debug)
        output = extractor.parse(args.input)
        pprint.pprint(output)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parselet', help='Path to Parsley script')
    parser.add_argument('input', help='URL or HTML file to scrape from')
    parser.add_argument('--debug', action='store_true', help='Enable DEBUG mode')
    return parser.parse_args()

if __name__ == '__main__':
    main(parse_args())
