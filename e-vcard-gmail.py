#!/usr/bin/env python3

import argparse
import base64
import re
import urllib.request
import logging

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--dry-run", help="do not download anything", action="store_true")
parser.add_argument("-p", "--with-photo", help="filter out contacts without photo", action="store_true")
parser.add_argument("filein", help="input vCard file")
parser.add_argument("fileout", help="output vCard file")
args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S"
)

with open(args.filein, 'r') as fin,\
     open(args.fileout, 'w') as fout:

    last_line = fin.readline()
    while True:
        if not last_line:
            break

        lines = [last_line, ]
        last_line = fin.readline()
        while last_line and not re.match('[A-Z]+[:;]', last_line):
            lines.append(last_line)
            last_line = fin.readline()
        line = ''.join(l.strip() for l in lines)

        field, value = line.split(':', 1)
        filed, *prop = field.split(';', 1)

        if field == 'BEGIN' and value == 'VCARD':
            FN = ''
            PHOTO = ''
            vcard = []

        elif field == 'VERSION' and value == '2.1':
            logging.warning('Input file appears to be v2.1. Please, consider converting it to v3.0 via https://github.com/jowave/vcard2to3.')

        elif field == 'FN':
            FN = value

        elif field == 'PHOTO':
            PHOTO = value
            if not args.dry_run:
                with urllib.request.urlopen(PHOTO) as photo:
                    photo64 = base64.b64encode(photo.read())
                lines = ["PHOTO;TYPE=jpeg;ENCODING=b;VALUE=BINARY:\n", ]
                for i in range(0, len(photo64), 74):
                    lines.append(' ' + photo64[i:i+74].decode('ascii') + '\n')
                del photo64

        vcard.extend(lines)

        if field == 'END' and value == 'VCARD':
            if args.with_photo == False or PHOTO:
                with_photo = f" with photo:\n {PHOTO}" if PHOTO else ""
                logging.info(f'Found {FN}{with_photo}')
                for line in vcard:
                    fout.write(line)
