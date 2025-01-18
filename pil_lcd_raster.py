import math
import os
import struct
import textwrap

from PIL import Image, ImageFile


def _accept(prefix):
    return False


class LCDRasterImageFile(ImageFile.ImageFile):
    """
    Image plugin for the QOI format (Quite OK Image format)
    """

    format = 'rawlcd'
    format_description = 'RAW format for mono OLED or RGB LCD'


class LCDRasterEncoder(ImageFile.PyEncoder):
    """
    Encoder for RASTER image files
    """

    def __init__(self, mode, *args):
        super().__init__(mode, args)
        self.x = 0
        self.y = 0
        self.eof = False

    def encode(self, bufsize):
        buffer = bytearray(bufsize)
        i = 0
        w = self.im.size[0]
        while not self.eof and i < bufsize * 8:
            pixel = self.im.getpixel((self.x, self.y))
            if self.im.mode in ('1', 'L', 'LAB', 'HSV'):
                if self.im.mode == 'LAB':
                    pixel = pixel[0]  # L
                elif self.im.mode == 'HSV':
                    pixel = pixel[2]  # V
                pxcolor = (3*255) if pixel >= 128 else 0
            elif self.im.mode in ('RGB', 'RGBA'):
                if len(pixel) == 3:
                    pixel = pixel + (255,)
                pxcolor = sum(pixel[0:2]) * pixel[3] / 255
            else:
                raise SyntaxError(f'Unsupported image mode "{self.im.mode}"')
            if pxcolor >= 3 * 128:
                # set pixel
                buffer[self.x + w * (self.y >> 3)] |= 1 << (self.y & 0x07)
            else:
                # clear pixelv
                buffer[self.x + w * (self.y >> 3)] &= ~(1 << (self.y & 0x07))
            self._advance_pixel()
            i += 1
        return math.ceil(i / 8), 1 if self.eof else 0, buffer

    def _advance_pixel(self):
        self.x += 1
        if self.x >= self.im.size[0]:
            self.y += 1
            self.x = 0
        self.eof = self.y >= self.im.size[1]

    def cleanup(self):
        del self.x
        del self.y
        del self.eof


def _save(im, fp, filename, save_all=False):
    varname = im.info['varname'] if 'varname' in im.info else 'LCD_image'
    fp.write(f'#include <stdint.h>{os.linesep}#ifdef __RESOURCE_DATA__{os.linesep}'.encode())
    fp.write(f'const uint8_t {varname}[] = {{{os.linesep}'.encode())
    def_x = im.info['def_x'] * 1 if 'def_x' in im.info else 0
    def_y = im.info['def_y'] * 1 if 'def_y' in im.info else 0
    fp.write(f'{def_x & 0xFF}, {(def_x >> 8) & 0xFF}, //Default X = {def_x}{os.linesep}'.encode())
    fp.write(f'{def_y & 0xFF}, {(def_y >> 8) & 0xFF}, //Default Y = {def_y}{os.linesep}'.encode())
    fp.write(f'{im.size[0] & 0xFF}, {(im.size[0] >> 8) & 0xFF}, //Width = {im.size[0]}{os.linesep}'.encode())
    fp.write(f'{im.size[1] & 0xFF}, {(im.size[1] >> 8) & 0xFF}, //Height = {im.size[1]}{os.linesep}'.encode())
    fp.write(f'{1 if im.mode == "1" else 2}, //GFX_IMAGE_FORMAT_RASTER = 1, GFX_IMAGE_FORMAT_RGB = 2, {os.linesep}'.encode())
    im.load()
    if not hasattr(im, 'encoderconfig'):
        im.encoderconfig = ()
    bufsize = max(ImageFile.MAXBLOCK, im.size[0])
    if hasattr(fp, 'flush'):
        fp.flush()
    encoder = Image._getencoder(im.mode, 'rawlcd', im.mode, im.encoderconfig)
    rsrc_len = 9
    try:
        encoder.setimage(im.im, (0, 0) + im.size)
        wrapper = textwrap.TextWrapper()
        while True:
            l, s, d = encoder.encode(bufsize)
            rsrc_len += l
            vals = [str(by) for by in d[:l]]
            vallist = ', '.join(vals)
            fp.write(wrapper.fill(vallist).encode())
            if s:
                break
        if s < 0:
            raise OSError(f"encoder error {s} when writing image file")
    finally:
        encoder.cleanup()

    fp.write(f'}};{os.linesep}'.encode())
    fp.write(f'#else{os.linesep}'.encode())
    fp.write(f'#ifndef __{varname}_RSRC__{os.linesep}#define __{varname}_RSRC__{os.linesep}'.encode())
    fp.write(f'extern const uint8_t {varname}[{rsrc_len}];{os.linesep}'.encode())
    fp.write(f'#endif{os.linesep}'.encode())
    fp.write(f'#endif{os.linesep}{os.linesep}'.encode())
    if hasattr(fp, 'flush'):
        fp.flush()


def _save_raw_bin(im, fp, filename, save_all=False):
    def_x = im.info['def_x'] * 1 if 'def_x' in im.info else 0
    def_y = im.info['def_y'] * 1 if 'def_y' in im.info else 0
    fp.write(struct.pack('<4HB', def_x, def_y, im.size[0], im.size[1], 1 if im.mode == '1' else 2))
    im.load()
    if not hasattr(im, 'encoderconfig'):
        im.encoderconfig = ()
    bufsize = max(ImageFile.MAXBLOCK, im.size[0])
    if hasattr(fp, 'flush'):
        fp.flush()
    encoder = Image._getencoder(im.mode, 'rawlcd', im.mode, im.encoderconfig)
    try:
        encoder.setimage(im.im, (0, 0) + im.size)
        while True:
            l, s, d = encoder.encode(bufsize)
            fp.write(d[:l])
            if s:
                break
        if s < 0:
            raise OSError(f"encoder error {s} when writing image file")
    finally:
        encoder.cleanup()

    if hasattr(fp, 'flush'):
        fp.flush()


if LCDRasterImageFile.format not in Image.registered_extensions().values():
    Image.register_encoder(LCDRasterImageFile.format, LCDRasterEncoder)

if '.rawlcd.c' not in Image.registered_extensions():
    Image.register_extension(LCDRasterImageFile.format + 'C', '.rawlcd.c')
    Image.register_save(LCDRasterImageFile.format + 'C', _save)

if '.rawlcd.bin' not in Image.registered_extensions():
    Image.register_extension(LCDRasterImageFile.format + 'BIN', '.rawlcd.bin')
    Image.register_save(LCDRasterImageFile.format + 'BIN', _save_raw_bin)
