# Fuel Patch Format

Based on dnSpy's decompiled`Tv.Twitch.Fuel.Patching.Patcher` from `Amazon.Fuel.Patching.dll`.

Patches can be compressed with zstandard or be uncompressed.

The basic idea seems to be that the patch file contains multiple "Instructions" that tell the patcher,
what to do with the following data.

There are four instructions:

* Seek - seek in source file
* Copy - copy from source file to target file
* Insert - copy from patch file to target file
* Merge - Add source and patch bytes, write to target

The "source" is the unpatched game file, the "patch" file is the downloaded patch,
and the "target" file is the (temporary) file that is written to.

This means that for the purpose of patching a game you will need free disk space equivalent to the size of the
largest game file + the patch file's size.

After the target file is written its hash is verified against the `targetHash` from the patch list.
If it matches the source and patch file are deleted and the temporary target file moved to the source file's location.

## Patch encoding

### Patch file header
The header is only a single byte signifying the compression format used for the remainder of the patch file

* 0x0 - no compression
* 0x1 - zstandard compression

If zstandard compression is used then all data after the first byte shall be wrapped in a zstandard decoder.

### Patch instructions

The instruction is mostly encoded in a single byte, though additional ones may be required if patch length exceeds
what can be encoded that way.

* Bits 0-1 are the instruction (enum of Seek, Copy, Insert, Merge)
* If instruction is seek, then bit 2 signifies seek direction (1 = backwards), otherwise it's part of
* Bit 2/3-8 is the encoded length

The encoded length either specifies the length or if it is greater 58 (or 26 if instruction is seek) it tells the
patcher how many bytes need to be read for the length. Example as follows (python pseudocode):

````python
bitcount = 5 if instruction == seek else 6
bitcount_mask = (1 << bitcount) - 1
length = patch_byte & bitcount_mask
if length < (bitcount_mask - 4):
    return length + 1

byte_count = length - bitcount_mask - 5
return int.from_bytes(patch_file.read(byte_count), byteorder='big')
````

The instructions work as follows:
* Seek
    * seeks <length> forwards or backwards (see above) in source file
* Copy
    * copies <length> bytes from source file to target file
* Insert
    * copies <length> bytes from patch file to target file
* Merge
    * reads <length> bytes from source and patch file, adds each byte together and writes it to target file

