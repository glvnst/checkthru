#!/usr/bin/env python
"""
checkthru: copy stdin to stdout -- if it matches the given sha checksum
"""
import argparse
import sys
import shutil
import tempfile
import hashlib


def main():
    """
    direct program entry point
    return an exit status integer suitable for use with sys.exit
    """
    algorithm_choices = ", ".join(
        sorted(hashlib.algorithms) +
        sorted(hashlib.algorithms_available -
               set(hashlib.algorithms) -
               set([a.upper() for a in hashlib.algorithms]))
    )

    argp = argparse.ArgumentParser(
        description=(
            "copy stdin to stdout -- if it matches the given sha checksum"),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argp.add_argument('checksum', nargs="?", help=(
        "the checksum to compare the standard input to"))
    argp.add_argument('-a', '--algorithm', default="sha256", help=(
        "the checksum algorithm to use, for example "
        "{}").format(algorithm_choices))
    argp.add_argument('-b', '--buffersize', type=int, default=1048576, help=(
        "the buffer size to use when reading from stdin"))
    argp.add_argument('-p', '--passthru', action="store_true", help=(
        "do no checking - instead pass the contents of stdin through to stdout"
        "and print the checksum of that content to stderr"))
    argp.add_argument('-d', '--debug', action="store_true", help=(
        "enable debugging output"))
    args = argp.parse_args()

    # sanity checking
    if args.algorithm not in hashlib.algorithms_available:
        warn("Unsupported algorithm {}", args.algorithm)
        return 1
    if int(bool(args.checksum)) + int(bool(args.passthru)) != 1:
        warn("Invalid mode, you must use either a checksum or passthru mode")
        return 1

    # sum checking
    tmp_fh = tempfile.SpooledTemporaryFile(prefix="checkthru",
                                           max_size=args.buffersize)
    with tmp_fh:
        shutil.copyfileobj(sys.stdin, tmp_fh)
        tmp_fh.seek(0)
        input_checksum = filehandle_checksum(tmp_fh,
                                             buffersize=args.buffersize,
                                             algorithm=args.algorithm)

        if args.passthru or input_checksum == args.checksum:
            tmp_fh.seek(0)
            shutil.copyfileobj(tmp_fh, sys.stdout)
            if args.passthru:
                warn(input_checksum)
            return 0

        # if we're still here the checksums didn't match
        if args.debug:
            warn('stdin checksum "{}" does NOT match given checksum "{}"',
                 input_checksum, args.checksum)

    return 1


def filehandle_checksum(filehandle, buffersize=1048576, algorithm="sha256"):
    """
    use the given algorithm to get a checksum of the data in the given
    filehandle. return the computed hexdigest
    """
    hasher = (hashlib.__dict__[algorithm] if
              algorithm in hashlib.algorithms else
              hashlib.new(algorithm))()
    while True:
        buf = filehandle.read(buffersize)
        if not buf:
            break
        hasher.update(buf)
    return hasher.hexdigest()


def warn(message, *args, **kwargs):
    """
    Print the given message to stderr, with timestamp prepended and newline
    appended, return the message unchanged
    """
    formatted_message = message.format(*args, **kwargs)
    sys.stderr.write(formatted_message + "\n")
    return formatted_message


if __name__ == '__main__':
    try:
        RESULT = main()
    except KeyboardInterrupt:
        sys.stderr.write("\n")
        RESULT = 1
    sys.exit(RESULT)
