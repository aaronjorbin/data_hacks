#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010 bit.ly
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Generate an ascii bar chart for input data

http://github.com/bitly/data_hacks
"""
import sys
import math
from collections import defaultdict
from optparse import OptionParser
from decimal import Decimal

def load_stream(input_stream):
    for line in input_stream:
        clean_line = line.strip()
        if not clean_line:
            # skip empty lines (ie: newlines)
            continue
        if clean_line[0] in ['"', "'"]:
            clean_line = clean_line.strip('"').strip("'")
        if clean_line:
            yield clean_line

def run(input_stream, options):
    data = defaultdict(lambda:0)
    for row in input_stream:
        if options.agg_values:
            kv = row.split(' ',2);
            data[kv[0]]+= int(kv[1])
        else:
            data[row]+=1
    
    if not data:
        print "Error: no data"
        sys.exit(1)
    
    max_length = max([len(key) for key in data.keys()])
    max_length = min(max_length, 50)
    value_characters = 80 - max_length
    max_value = max(data.values())
    scale = int(math.ceil(float(max_value) / value_characters))
    scale = max(1, scale)
    
    print "# each ∎ represents a count of %d" % scale
    
    if options.sort_values:
        data = [[value, key] for key, value in data.items()]
        data.sort(key=lambda x: x[0], reverse=options.reverse_sort)
    else:
        # sort by keys
        data = [[value, key] for key, value in data.items()]
        if options.numeric_sort:
            # keys could be numeric too
            data.sort(key=lambda x: (Decimal(x[1])), reverse=options.reverse_sort)
        else:
            data.sort(key=lambda x: x[1], reverse=options.reverse_sort)
    
    format = "%" + str(max_length) + "s [%6d] %s"
    for value,key in data:
        print format % (key[:max_length], value, (value / scale) * "∎")

if __name__ == "__main__":
    parser = OptionParser()
    parser.usage = "cat data | %prog [options]"
    parser.add_option("-a", "--agg-values", dest="agg_values", default=False, action="store_true",
                        help="Two column input format, space seperated with key<space>value")
    parser.add_option("-k", "--sort-keys", dest="sort_keys", default=True, action="store_true",
                        help="sort by the key [default]")
    parser.add_option("-v", "--sort-values", dest="sort_values", default=False, action="store_true",
                        help="sort by the frequence")
    parser.add_option("-r", "--reverse-sort", dest="reverse_sort", default=False, action="store_true",
                        help="reverse the sort")
    parser.add_option("-n", "--numeric-sort", dest="numeric_sort", default=False, action="store_true",
                        help="sort keys by numeric sequencing")
    
    (options, args) = parser.parse_args()
    
    if sys.stdin.isatty():
        parser.print_usage()
        print "for more help use --help"
        sys.exit(1)
    run(load_stream(sys.stdin), options)

