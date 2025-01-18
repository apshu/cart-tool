#Script to generate MONO LCD raster images
import argparse
import sys

from PIL.Image import Dither

try:
    from PIL import Image
except ImportError:
    print('Need PILLOW library for image read/write, use python -m pip install Pillow', file=sys.stderr)
    raise

import pil_lcd_raster

def main():
    parser = argparse.ArgumentParser(description='Generate MONO LCD raster images')
    parser.add_argument('-i', '--infile', type=argparse.FileType('rb'), default='-', help='Input file')
    parser.add_argument('-x', '--defX', type=int, default=0, help='Default image X position. Useful for building skins.')
    parser.add_argument('-y', '--defY', type=int, default=0, help='Default image Y position. Useful for building skins.')
    parser.add_argument('-n', '--varname', type=str, default='RAW_LCD_image', help='Output code variable name')
    parser.add_argument('--inverse', action='store_true', help='Generated output in inverse')
    parser.add_argument('--no_dither', dest='dither', action='store_false', help='Convert non B&W image with 50% luminescence cut')
    parser.add_argument('--no_resize', dest='auto_resize', action='store_false', help='Disable resizing of images to fit OLED display 128×64')
    parser.add_argument('-o', '--outfile', type=argparse.FileType('wb'), default='-', help='Output file')
    args = parser.parse_args()
    # open an image
    im = Image.open(args.infile)
    if args.auto_resize:
        im.thumbnail((128,64))
    if im.mode != '1':
        im = im.convert('1', dither=Dither.FLOYDSTEINBERG if args.dither else Dither.NONE)
    im.info['varname'] = args.varname
    im.info['def_x'] = args.defX
    im.info['def_y'] = args.defY
    im.info['inverse'] = args.inverse
    im.show()
    # save an .lcd image
    im.save(args.outfile, 'rawlcdbin')

if __name__ == '__main__':
    main()
