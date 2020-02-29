OTP
========================

OTP encryption and decryption with support for ASCII (--ascii_charset) and Unicode (--utf_charset) characters. As well as a reference key system which allows referencing decryption keys by IDs.

---------------

## Simple usage
Encrypt
```
$ python3 cli.py  -m "The quick brown fox jumps over the lazy dog"
MESSAGE:  gIK oyaRO PeirB MGP CFjju XExr cMN sjZd BSt
KEY:  nBGYeSPEONUVoHsstlXUcJjtaJFJhjAFyEnjKMjKbUZ
```

Decrypt
```
$ python3 cli.py -d -m "gIK oyaRO PeirB MGP CFjju XExr cMN sjZd BSt" -k nBGYeSPEONUVoHsstlXUcJjtaJFJhjAFyEnjKMjKbUZ
MESSAGE:  The quick brown fox jumps over the lazy dog
KEY:  nBGYeSPEONUVoHsstlXUcJjtaJFJhjAFyEnjKMjKbUZ
```

## Unicode keys/messages
When working with ASCII/UTF charsets it's easiest to write the message to file on encrypt -o and load it on decrypt with -f

Encrypt
```
$ python3 cli.py  -k "I ❤' unicode 😀🤣" -m "The quick brown fox jumps over the lazy dog 💩"  --utf_charset -o utf.txt
MESSAGE:  ⟉Gê×ÌÎÆ×🙷🦑i⟓@ßãÖÓâ
                                Ô🙥🦕i⟌@áÏãÜÈÔ😠𾷌
KEY:  I ❤' unicode 😀🤣
Wrote message to utf.txt
```

Decrypt
```
$ python3 cli.py  -k "I ❤' unicode 😀🤣"  --utf_charset -f utf.txt -d
MESSAGE:  The quick brown fox jumps over the lazy dog 💩
KEY:  I ❤' unicode 😀🤣
```
## Reference Databases

#### Generate new database with 10k keys (-g -db file -c number_of_keys -l length_of_keys )
```
$ python3 cli.py -g -db "reference_db.json" --count 10000
Generated new reference database: reference_db.json
```
#### Use a random key from it to encrypt a message (default if no -k or -r)
```
$ python3 cli.py -db "reference_db.json" -m "my message"
MESSAGE:  uQ wgVWYFl
KEY:  ZRsK
```
#### Decrypting with reference key (-r reference_key)
```
$ python3 cli.py -db "reference_db.json" -m "uQ wgVWYFl" -d -r ZRsK
MESSAGE:  my message
KEY:  ZRsK
```
## List of databases
In cases where large number of keys must be pre-generated then lists of reference databases can be used.
Generating/using lists is nearly identical to working with a single file except -dbl is used in place of -db and -gl in place of -g. -gl also requires the number of databases to generate.

More in docs/example_usage.txt
