'''Create a forgery-proof timestamp for your data, secured by the bitcoin network.'''

__copyright__ = '''\
Copyright (C) 2013 Volker Grabsch <v@njh.eu>

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
'''

import hashlib

b58digits = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
b58values = {d: v for v, d in enumerate(b58digits)}

def b58encode(s):
    value = 0L
    for c in s:
        value = (value * 256) + ord(c)
    r = ''
    while value > 0:
        value, c = divmod(value, 58)
        r = b58digits[c] + r
    for c in s:
        if c == chr(0):
            r = b58digits[0] + r
        else:
            break
    return r

def b58decode(s):
    value = 0L
    for c in s:
        value = (value * 58) + b58values[c]
    r = ''
    while value > 0:
        value, c = divmod(value, 256)
        r = chr(c) + r
    for c in s:
        if c == b58digits[0]:
            r = chr(0) + r
        else:
            break
    return r

def convert_base_reversed(input, base, new_base):
    '''Convert input digits to another base. Input is big endian, but output is little endian!'''
    # initialize result = 0, which may be represented equally well as [] or [0]
    result = []
    for d in input:
        # calculate result = (result * base) + d, perform calculation in new base
        carry = d
        for i in xrange(len(result)):
            carry, result[i] = divmod((result[i] * base) + carry, new_base)
        while carry > 0:
            carry, carry_digit = divmod(carry, new_base)
            result.append(carry_digit)
    return result

def convert_base(input, base, new_base):
    '''Convert input digits to another base. Input and output are big endian.'''
    result = convert_base_reversed(input, base, new_base)
    # convert result from little endian to big endian
    result.reverse()
    return result

def convert_base_fast(input, (base, base_group_size), (new_base, new_base_group_size)):
    '''Same as convert_base, but calculates multiple input and output digits at once.'''
    padding = [0] * ((-len(input)) % base_group_size)
    padded_input = padding + input
    grouped_input = []
    for i in xrange(0, len(padded_input), base_group_size):
        d = 0
        for j in xrange(base_group_size):
            d = (d * base) + padded_input[i + j]
        grouped_input.append(d)
    result = []
    for group_digit in convert_base_reversed(grouped_input, base**base_group_size, new_base**new_base_group_size):
        for i in xrange(new_base_group_size):
            group_digit, d = divmod(group_digit, new_base)
            result.append(d)
    result.reverse()
    result_padding = next((i for i, d in enumerate(result) if d != 0), len(result))
    return result[result_padding:]

def b58encode_nolong(s):
    '''Same as b58encode, but with plain "int"s (no "long").'''
    padding = next((i for i, c in enumerate(s) if c != chr(0)), len(s))
    result = convert_base_fast([ord(c) for c in s], (256, 3), (58, 4))
    return (b58digits[0] * padding) + ''.join(b58digits[d] for d in result)

def b58decode_nolong(s):
    '''Same as b58decode, but with plain "int"s (no "long").'''
    padding = next((i for i, c in enumerate(s) if c != b58digits[0]), len(s))
    result = convert_base_fast([b58values[c] for c in s], (58, 4), (256, 3))
    return (chr(0) * padding) + ''.join(chr(d) for d in result)

def ripemd160_to_address(ripemd160_digest):
    '''Convert a RIPEMD-160 hash (or any other 160-bit string) to a bitcoin address'''
    assert len(ripemd160_digest) == 160 / 8
    versioned_digest = '\x00' + ripemd160_digest
    checksum = hashlib.sha256(hashlib.sha256(versioned_digest).digest()).digest()[:4]
    return versioned_digest + checksum

def sha256_to_address(sha256_digest):
    '''Convert a SHA-256 hash of a public key (or of any other binary data) to a bitcoin address'''
    assert len(sha256_digest) == 256 / 8
    return ripemd160_to_address(hashlib.new('ripemd160', sha256_digest).digest())

def publickey_to_address(publickey):
    '''Convert a bitcoin public key (or any other binary data) to a bitcoin address'''
    return sha256_to_address(hashlib.sha256(publickey).digest())

def hr_address(prefix):
    '''Generate human-readable pseudo-addresses'''
    # 'W11111' in b58 is the mean value ('W' = 29 = 58/2),
    # to avoid a carry into the prefix during the implicit
    # addition/subtraction that happens while exchanging the checksum
    address_bin = b58decode(prefix + 'W11111')
    assert len(address_bin) == 25
    assert address_bin[0] == '\x00'
    address = b58encode(ripemd160_to_address(address_bin[1:-4]))
    assert address.startswith(prefix)
    return address

def hash_to_hr_addresses(algorithm, hexdigest):
    assert len(algorithm) == 6
    size = 16
    return [
        hr_address('1%sx%xx%sx' % (algorithm, i + 1, hexdigest[i*size:(i+1)*size].replace('0', 'o')))
        for i in xrange(0, len(hexdigest)/size)
    ]

def sha256_to_hr_addresses(sha256_hexdigest):
    assert len(sha256_hexdigest) == 256/4
    return hash_to_hr_addresses('SHA256', sha256_hexdigest)
