# Simple Client API for `/bin/sh`

When you're using a simple container like Docker, you don't want to weigh down
your base image with lots of useless cruft, like Perl or Python, unless your
application really needs it.  To this end, the [Simple Client API](../../docs/contract.md)
is also provided in a simple shell script with minimal dependencies.

Each script file is self contained.  You can pick and choose as necessary.  They do,
however, depend upon the contents of the [src](src) directory.


## Package dependencies

To run the provided scripts, the following Linux packages must be installed:

* **openssl >= 1.0.0** - Provides programs for AWS signing (sha256 hashing with possible HMAC mac).
* **curl** - Used to send AWS commands.
* **sh** - Designed to use with Ash or other basic shell programs.  Bash is not required.
* **coreutils** - Some of the GNU coreutils package tools used.  These are listed out to help
    developers of minimalist docker images.
    * `cut`
    * `date`
    * `echo`
    * `mkdir`
    * `rm`
    * `test` (and thus `[`)
    * `touch`
    * `tr`



# References

* http://czak.pl/2015/09/15/s3-rest-api-with-curl.html
* http://tmont.com/blargh/2014/1/uploading-to-s3-in-bash
