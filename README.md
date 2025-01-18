# Atari 8-bit Cartridge Tools

This project provides tools and utilities for working with Atari 8-bit cartridge files.

## Table of Contents

- [Installation](#installation)
- [cart-tool.py](#usage-of-cart-toolpy) command-line tool for manipulating Atari 8-bit cartridge files.
- [image2oled.py](#usage-of-image2oledpy) command-line tool to generate MONO LCD raster images
- [License](#license)

## Installation

To use the tools provided in this project, you must have Python 3.10 or later installed.

For [`image2oled.py`](#usage-of-image2oledpy), the Pillow library is needed. You can install it using pip:
```sh
python -m pip install Pillow
```

## Usage of [`cart-tool.py`](cart-tool.py)

```
python cart-tool.py [-h] {info,list,setblob,set,addblob,add,delblob,del,rm,erase,getblob,get,extract,getrom,rom,settype,rom2car,convert,convertrom} ...
```
&emsp;[`info`](#subcommand-info-parameters): Get `<CAR file>` information based on header.  
&emsp;[`list`](#subcommand-list-parameters): List available CART mode identifiers.  
&emsp;[`setblob`](#subcommand-setblob-parameters) (aliases: `set`, `addblob`, `add`): Set `<CAR file>` blob to bytes from `<BLOB file>`.  
&emsp;[`delblob`](#subcommand-delblob-parameters) (aliases: `del`, `rm`, `erase`): Eliminate BLOB from `<CAR file>`.  
&emsp;[`getblob`](#subcommand-getblob-parameters) (aliases: `get`, `extract`): Extract BLOB from `<CAR file>` to `<BLOB file>`.  
&emsp;[`getrom`](#subcommand-getrom-parameters) (alias: `rom`): Extract RAW ROM content from `<CAR file>` to `<ROM file>`.  
&emsp;[`settype`](#subcommand-settype-parameters): Override cart type in `<CAR file>`.  
&emsp;[`rom2car`](#subcommand-rom2car-parameters) (aliases: `convert`, `convertrom`): Convert RAW `<ROM file>` to `<CAR file>`.    

### List of commands with parameters
#### Subcommand *info* Parameters
```
python cart-tool.py info [-h] <CAR file>
```
- `info`: Get information about a cartridge file.
    - `<CAR file>`: Input file. The file is not modified.

#### Subcommand *list* Parameters
```
python cart-tool.py list [-h] [-f FORMAT]
```
- `list`: List available CART mode identifiers.
    - `-f, --format`: Define output format. Default is human readable format. Specify -f JSON for JSON format.

#### Subcommand *setblob* Parameters
```
python cart-tool.py setblob [-h] <CAR file> <BLOB file>
```
- `setblob`: Set the blob data in a cartridge file.
    - `<CAR file>`: Input/output file. File content rewritten. No backups created.
    - `<BLOB file>`: Input file. The file is not modified.

#### Subcommand *delblob* Parameters
```
python cart-tool.py delblob [-h] <CAR file>
```
- `delblob`: Remove the blob data from a cartridge file.
    - `<CAR file>`: Input/output file. File content rewritten. No backups created.

#### Subcommand *getblob* Parameters
```
python cart-tool.py getblob [-h] <CAR file> <BLOB file>
```
- `getblob`: Extract the blob data from a cartridge file.
    - `<CAR file>`: Input file. The file is not modified.
    - `<BLOB file>`: Generated file. If file exists, it will be overwritten without backup.

#### Subcommand *getrom* Parameters
```
python cart-tool.py getrom [-h] <CAR file> <ROM file>
```
- `getrom`: Extract the ROM data from a cartridge file.
    - `<CAR file>`: Input file. The file is not modified.
    - `<ROM file>`: Generated file. If file exists, it will be overwritten without backup.

#### Subcommand *settype* Parameters
```
python cart-tool.py settype [-h] <CAR file> <cart_type> [-a]
```
- `settype`: Set the cartridge type in a cartridge file.
    - `<CAR file>`: Input/output file. File content rewritten. No backups created.
    - `<cart_type>`: New type identifier. To list all known types, run the command with --list.
    - `-a, --adjust-size`: If the new CART type is bigger or smaller, the ROM content will be extended (0xFF) or truncated.

#### Subcommand *rom2car* Parameters
```
python cart-tool.py rom2car [-h] <ROM file> <CAR file> [-t cart_type]
```
- `rom2car`: Convert a raw ROM file to a cartridge file.
    - `<ROM file>`: Source (cart-type guess is based only on the size).
    - `<CAR file>`: Generated file. If file exists, it will be overwritten without backup.
    - `-t, --cart-type`: If omitted, the cart-type will be guessed.

### Command invocation examples

- [`info`](#subcommand-info-parameters) example:

    Get information about a cartridge file.
    ```sh
    python cart-tool.py info mycartridge.car
    ```
- [`list`](#subcommand-list-parameters) example:

    List available CART mode identifiers.
    ```sh
    python cart-tool.py list
    ```
    List available CART mode identifiers in JSON format.
    ```sh
    python cart-tool.py list -f JSON
    ```
- [`setblob`](#subcommand-setblob-parameters) example:

    Set the blob data in a cartridge file.
    ```sh
    python cart-tool.py setblob mycartridge.car myblob.bin
    ```
- [`delblob`](#subcommand-delblob-parameters) example:

    Remove the blob data from a cartridge file.
    ```sh
    python cart-tool.py delblob mycartridge.car
    ```
- [`getblob`](#subcommand-getblob-parameters) example:

    Extract the blob data from a cartridge file.
    ```sh
    python cart-tool.py getblob mycartridge.car extractedblob.bin
    ```
- [`getrom`](#subcommand-getrom-parameters) example:

    Extract the ROM data from a cartridge file.
    ```sh
    python cart-tool.py getrom mycartridge.car extractedrom.bin
    ```
- [`settype`](#subcommand-settype-parameters) examples:

    Set the cartridge type in a cartridge file.
    ```sh
    python cart-tool.py settype mycartridge.car 12 --adjust-size
    ```
    Invoke command with hexa number (other Python recognized number formats also accepted)
    ```sh
    python cart-tool.py settype mycartridge.car 0x0C --adjust-size
    ```
    Command invocation with text based cart mode
    ```sh
    python cart-tool.py settype mycartridge.car Mode_XEGS_32K --adjust-size
    ```
- [`rom2car`](#subcommand-rom2car-parameters) examples:

    Convert a raw ROM file to a type 12 cartridge file.
    ```sh
    python cart-tool.py rom2car myrom.bin mycartridge.car --cart-type 12
    ```
    Command invocation with text based cart mode
    ```sh
    python cart-tool.py rom2car myrom.bin newXEGScart.car -t Mode_XEGS_64K
    ```

## Usage of [`image2oled.py`](image2oled.py)

```
python image2oled.py [-h] [-i INFILE] [-x DEFX] [-y DEFY] [-n VARNAME] [--inverse] [--no_dither] [--no_resize] [-o OUTFILE]
```
- `-i, --infile`: Input file (default: `-` = stdin).
- `-x, --defX`: Default image X position (default: `0`).
- `-y, --defY`: Default image Y position (default: `0`).
- `-n, --varname`: Output C code variable name (default: `RAW_LCD_image`). Omitted for BINARY format.
- `--inverse`: Generate output in inverse.
- `--no_dither`: Convert non B&W image with 50% luminescence cut.
- `--no_resize`: Disable resizing of images to fit OLED display 128×64.
- `-o, --outfile`: Output file (default: `-` = stdout).

### Command invocation examples

- Convert an image to MONO LCD raster format and save it.
  ```sh
  python image2oled.py -i input.png -o output.lcd
  ```
- Convert an image with default X and Y positions.
  ```sh
  python image2oled.py -i input.bmp -x 10 -y 20 -o output.lcd
  ```
- Convert an image without dithering and resizing.
  ```sh
  python image2oled.py -i input.jpg --no_dither --no_resize -o output.lcd
  ```

## License

This project is licensed under the MIT License.


