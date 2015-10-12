# checkthru

This program copies stdin to stdout if the content on stdin matches the given
checksum.

## Examples

### Sending files without SSH:

On the sender:

checkthru prints the checksum to stderr, for easy-copy & paste...

    $ tar --bzip2 -cf - . | checkthru -p | nc -l 127.0.0.1 4567
    896c4a28446c10dc48046f4bf65aefe4b8ab6f15beb6baa3c9c2b00356001826

On the receiver:

Verify you got the right data before you pass it to tar

    $ nc 127.0.0.1 4567 | checkthru 896c4a28446c10dc48046f4bf65aefe4b8ab6f15beb6baa3c9c2b00356001826 | tar --bzip2 -xvf -
    x ./
    x ./.gitignore
    x ./checkthru.py
    x ./LICENSE.txt
    x ./README.md

### Running commands from a site

Sometimes a website will have you do something like this:

    curl -s 'http://www.example.com/setup.sh' | sh -

This is really dangerous without TLS (and even with it, but for other reasons).
If the publisher somehow securely provides a checksum of their setup script, you
can use checkthru to verify you are getting the right script, without errors and
without MITM attacks.

On the web server, the publisher could use `shasum` or `checkthru` to calculate
the checksum:

    $ checkthru -p <setup.sh
    echo "this is dumb. don't run untrusted commands from the internet"
    hostname
    f39893bc56941ade5b6671980826e5a3c5ad984a7e972c81cb99926d40475f7b

Then clients can do:

    $ curl -s "http://www.example.com/setup.sh" | checkthru f39893bc56941ade5b6671980826e5a3c5ad984a7e972c81cb99926d40475f7b | sh -
    this is dumb. don't run untrusted commands from the internet
    myfancycomputer.local

### Verified downloads:

Here's an example of downloading a copy of virtualbox with a known signature. In this case using checkthru is probably not better than wget + shasum

    URL="http://download.virtualbox.org/virtualbox/5.0.6/VirtualBox-5.0.6-103037-OSX.dmg"
    SUM="612e73aafa3dcdcf99e69e8831fb526512a4e4f8d02a0f4ac9d05baee09bb452"    
    curl -s $URL | checkthru $SUM > virtualbox.dmg

##  Usage

    usage: checkthru [-h] [-a ALGORITHM] [-b BUFFERSIZE] [-p] [-d] [checksum]

    copy stdin to stdout -- if it matches the given sha checksum

    positional arguments:
      checksum              the checksum to compare the standard input to
                            (default: None)

    optional arguments:
      -h, --help            show this help message and exit
      -a ALGORITHM, --algorithm ALGORITHM
                            the checksum algorithm to use, for example md5, sha1,
                            sha224, sha256, sha384, sha512, DSA, DSA-SHA, MD4,
                            MDC2, RIPEMD160, SHA, dsaEncryption, dsaWithSHA,
                            ecdsa-with-SHA1, md4, mdc2, ripemd160, sha (default:
                            sha256)
      -b BUFFERSIZE, --buffersize BUFFERSIZE
                            the buffer size to use when reading from stdin
                            (default: 1048576)
      -p, --passthru        do no checking - instead pass the contents of stdin
                            through to stdoutand print the checksum of that
                            content to stderr (default: False)
      -d, --debug           enable debugging output (default: False)


## Example



## Support Information

This program is provided without technical support.

## License

This program is distributed WITHOUT ANY WARRANTY under terms described in the file LICENSE.txt.
