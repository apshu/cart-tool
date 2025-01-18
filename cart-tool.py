import argparse
import json
import pathlib
import sys

import a8_cart
import filesize
from a8_cart import A8CARFile, ATCartridgeInfo

def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    has_trace = hasattr(sys, 'gettrace') and sys.gettrace() is not None
    has_breakpoint = sys.breakpointhook.__module__ != "sys"
    is_debug = has_trace or has_breakpoint
    if is_debug:
        debug_hook(exception_type, exception, traceback)
    else:
        # No debug
        print (f'{pathlib.Path(traceback.tb_frame.f_code.co_filename).name}@{traceback.tb_lineno}: {exception_type.__name__}: {exception}')

sys.excepthook = exception_handler


def cmd_info(cart_file, **kwargs):
    cart = a8_cart.A8CARFile(cart_file)
    print(f'''Validity check: {'✓ OK' if cart.is_valid else '✗ fail'}
Cart type: {cart.header._cart_mode} → {cart.header._cart_mode.mCartDescription}
Cart max ROM size: {cart.header._cart_mode.mCartSize:_} (0x{cart.header._cart_mode.mCartSize:04X}) <{filesize.naturalsize(cart.header._cart_mode.mCartSize, binary=True)}>
ROM actual size: {len(cart.rom_data):_} (0x{len(cart.rom_data):04X}) <{filesize.naturalsize(len(cart.rom_data), binary=True)}>
BLOB: {f'✓ {len(cart.blob):_} (0x{len(cart.blob):04X}) <{filesize.naturalsize(len(cart.blob), binary=True)}>' if len(cart.blob) else '✗ No BLOB'}''')


def save_cart(cart: A8CARFile, cart_file_name):
    with open(cart_file_name, 'wb') as cart_file:
        cart_file.write(bytes(cart))


def cmd_set_blob(cart_file, blob_file, **kwargs):
    cart = a8_cart.A8CARFile(cart_file)
    cart.blob = blob_file.read() if blob_file else []
    save_cart(cart, cart_file)


def cmd_delete_blob(cart_file, **kwargs):
    cmd_set_blob(cart_file, [])


def cmd_get_blob(cart_file, blob_file, **kwargs):
    cart = a8_cart.A8CARFile(cart_file)
    if cart.blob:
        with open(blob_file, 'wb') as f_out:
            f_out.write(cart.blob)


def cmd_get_rom(cart_file, rom_file, **kwargs):
    cart = a8_cart.A8CARFile(cart_file)
    if cart.rom_data:
        with open(rom_file, 'wb') as f_out:
            f_out.write(cart.rom_data)


def cmd_set_type(cart_file, cart_type: int, adjust_size: bool, **kwargs):
    cart = a8_cart.A8CARFile(cart_file)
    cart.header.cart_mode = cart_type
    if adjust_size:
        cart_max_size = cart.header.cart_mode.mCartSize
        if len(cart.rom_data) > cart_max_size:
            # truncate
            cart.rom_data = cart.rom_data[:cart_max_size]
        elif len(cart.rom_data) < cart_max_size:
            # extend
            cart.rom_data += b'\xff' * (cart_max_size - len(cart.rom_data))
    if cart.header.cart_mode != cart.header.cart_mode.Mode_Unknown or cart.header.cart_mode != cart.header.cart_mode.Mode_None:
        save_cart(cart, cart_file)
    else:
        ValueError(f'Cannot set caty type to {cart_type} - {cart.header.cart_mode.mCartDescription}')


def cmd_rom2car(rom_file, cart_file, cart_type: ATCartridgeInfo, **kwargs):
    cart = A8CARFile()
    cart.rom_data = rom_file.read()
    rom_length = len(cart.rom_data)
    if rom_length:
        if cart_type.is_virtual:
            # Autodetect needed
            print(f'Autodetecting:\n ROM size {filesize.naturalsize(rom_length, True)},\n all matching options: {', '.join(map(lambda x: x.name, filter(lambda x: x.mCartSize == rom_length, ATCartridgeInfo)))}')
            preferred_cart_modes = [1,2,12,13,14,23,24,25]
            if not (cart_type := tuple(filter(lambda x: ATCartridgeInfo(x).mCartSize == rom_length, preferred_cart_modes))):
                cart_type = tuple(filter(lambda x: x.mCartSize == rom_length, ATCartridgeInfo))
                if not cart_type:
                    raise RuntimeError('Couldn\'t identify CART type based on ROM file')
            cart_type = ATCartridgeInfo(cart_type[0])
        cart.header.cart_mode = cart_type
        save_cart(cart, cart_file)
        print(f'Created CART with mode: "{cart.header.cart_mode.name}"')
        if cart.header.cart_mode.mCartSize != rom_length:
            print(f'ROM size mismatch for type "{cart.header.cart_mode.name}"! (ROM file size={rom_length:_}, Cart mode ROM size={cart.header.cart_mode.mCartSize:_})')
    else:
        raise ValueError('ROM file length is 0')


def cmd_opt_list(output_format: str = 'default', **kwargs):
    real_cartlist: ATCartridgeInfo = sorted(filter(lambda x: not x.is_virtual, ATCartridgeInfo))
    if output_format == 'json':
        print(json.dumps(separators=(',', ':'), obj={item.name: {'mode': item.value, 'size': item.mCartSize, 'description': item.mCartDescription} for item in real_cartlist}))
    else:
        for carttype in real_cartlist:
            print(f'{carttype}={carttype.name} <{filesize.naturalsize(carttype.mCartSize, binary=True)}> "{carttype.mCartDescription}"')


command_map = {
    'info': cmd_info,
    # setblob
    'setblob': cmd_set_blob,
    'set': cmd_set_blob,
    'addblob': cmd_set_blob,
    'add': cmd_set_blob,
    # delblob
    'delblob': cmd_delete_blob,
    'del': cmd_delete_blob,
    'rm': cmd_delete_blob,
    'erase': cmd_delete_blob,
    # getblob
    'getblob': cmd_get_blob,
    'get': cmd_get_blob,
    'extract': cmd_get_blob,
    # getrom
    'getrom': cmd_get_rom,
    'rom': cmd_get_rom,
    # settype
    'settype': cmd_set_type,
    # rom2car
    'rom2car': cmd_rom2car,
    'convert': cmd_rom2car,
    'convertrom': cmd_rom2car
}


def param_to_cart_type(val):
    ret_val: ATCartridgeInfo = ATCartridgeInfo(ATCartridgeInfo.Mode_Unknown)
    try:
        ret_val = ATCartridgeInfo(val)
    except KeyError as e:
        raise ValueError(e)
    else:
        if ret_val.is_virtual:
            raise ValueError('Virtual cart type')
    return ret_val


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', required=True)

    sub_cmd = subparsers.add_parser('info', help='Get <CAR file> information based on header')
    sub_cmd.add_argument('cart_file', type=argparse.FileType('rb'), metavar='<CAR file>', help='Input file. The file is not modified.')

    sub_cmd = subparsers.add_parser('setblob', aliases=('set', 'addblob', 'add'), help='Set  <CAR file> blob to bytes from <BLOB file>')
    sub_cmd.add_argument('cart_file', type=pathlib.Path, metavar='<CAR file>', help='Input/output file. File content rewritten. No backups created.')
    sub_cmd.add_argument('blob_file', type=argparse.FileType('rb'), metavar='<BLOB file>', help='Input file. The file is not modified.')

    sub_cmd = subparsers.add_parser('delblob', aliases=('del', 'rm', 'erase'), help='Eliminate BLOB from <CAR file>')
    sub_cmd.add_argument('cart_file', type=pathlib.Path, metavar='<CAR file>', help='Input/output file. File content rewritten. No backups created.')

    sub_cmd = subparsers.add_parser('getblob', aliases=('get', 'extract'), help='Extract BLOB from <CAR file> to <BLOB file>')
    sub_cmd.add_argument('cart_file', type=argparse.FileType('rb'), metavar='<CAR file>', help='Input file. The file is not modified.')
    sub_cmd.add_argument('blob_file', type=pathlib.Path, metavar='<BLOB file>', help='Generated file. If file exists, it will be overwritten without backup.')

    sub_cmd = subparsers.add_parser('getrom', aliases=('rom',), help='Extract RAW ROM content from <CAR file> to <ROM file>')
    sub_cmd.add_argument('cart_file', type=argparse.FileType('rb'), metavar='<CAR file>', help='Input file. The file is not modified.')
    sub_cmd.add_argument('rom_file', type=pathlib.Path, metavar='<ROM file>', help='Generated file. If file exists, it will be overwritten without backup.')

    sub_cmd = subparsers.add_parser('settype', help='Override cart type in <CAR file>')
    sub_cmd.add_argument('cart_file', type=pathlib.Path, metavar='<CAR file>', help='Input/output file. File content rewritten. No backups created.')
    sub_cmd.add_argument('cart_type', type=param_to_cart_type, help='New type identifier. To list all known types, run the command with --list')
    sub_cmd.add_argument('-a', '--adjust-size', action='store_true', help='If the new CART type is bigger or smaller, the ROM content will be extended (0xFF) or truncated.')
    sub_cmd.add_argument('-l', '--list', type=str, action='store', nargs='?', const='default', default=argparse.SUPPRESS, help='List available CART type identifiers and exit. Specify -l JSON for JSON format.')

    sub_cmd = subparsers.add_parser('rom2car', aliases=('convert', 'convertrom'), help='Convert RAW <ROM file> to <CAR file>')
    sub_cmd.add_argument('rom_file', type=argparse.FileType('rb'), metavar='<ROM file>', help='Source (cart-type guess is based only on the size)')
    sub_cmd.add_argument('cart_file', type=pathlib.Path, metavar='<CAR file>', help='Generated file. If file exists, it will be overwritten without backup.')
    sub_cmd.add_argument('-t', '--cart-type', default=ATCartridgeInfo.Mode_Unknown, type=param_to_cart_type, help='If omitted, the cart-type will be guessed')
    sub_cmd.add_argument('-l', '--list', type=str, action='store', nargs='?', const='default', default=argparse.SUPPRESS, help='List available CART type identifiers and exit. Specify -l JSON for JSON format.')

    args = parser.parse_args()
    if 'list' in args:
        cmd_opt_list(args.list.casefold())
    else:
        if args.command in command_map:
            command_map[args.command](**vars(args))
        else:
            raise RuntimeError(f'Unable to execute command "{args.command}". Internal error.')


if __name__ == '__main__':
    main()
