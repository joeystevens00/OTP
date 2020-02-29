import otp.otp as otp
ascii_chars = otp.ascii_chars
utf_chars = otp.utf_chars
alphanumeric = otp.letters + otp.numbers
import random
import pytest

def otp_tests(msg, key, **additional_args):
    encrypted_msg, rkey = otp.otp(msg, key, **additional_args)
    assert key == rkey
    decrypted_msg, rkey = otp.otp(encrypted_msg, key, False, **additional_args)
    assert key == rkey
    assert decrypted_msg == msg
    bad_decrypt, _ = otp.otp(encrypted_msg, otp.securegen(len(encrypted_msg)), False, **additional_args)
    assert bad_decrypt != msg
def test_simple():
    otp_tests(otp.securegen(200), otp.securegen(200))

def otp_test_custom_charset(charset):
    test_lengths = [random.randint(1, 200), random.randint(200, 400), random.randint(400,2000)]
    for length in test_lengths:
        otp_tests(otp.securegen(length, charset=charset),
                otp.securegen(length, charset=charset),
                charset=charset
        )
def test_charsets():
    otp_test_custom_charset(otp.letters)
    otp_test_custom_charset(alphanumeric)
    otp_test_custom_charset(ascii_chars)
    otp_test_custom_charset(utf_chars)

@pytest.fixture
def charsets():
    return [otp.numbers, otp.symbols, otp.letters, otp.ascii_chars, otp.utf_chars, alphanumeric]

def test_securegen(charsets):
    assert len(otp.securegen(100)) == 100
    # Test with a random two charsets
    for charset in [ random.choice(charsets) for i in range(2) ]:
        for i in otp.securegen(100, charset=charset):
            assert i in charset


def generate_vc(**charset_args):
    return otp.VigenereCipher(key=otp.securegen(random.randint(100, 300), **charset_args), msg=otp.securegen(random.randint(100,300), **charset_args), mode='encrypt', **charset_args)
def decrypt_vc_from_source_vc(vc):
    return otp.VigenereCipher(key=vc.key, msg=vc.translated, charset=vc.charset, mode='decrypt')
@pytest.fixture
def vcascii():
    return generate_vc(charset=otp.ascii_chars)
@pytest.fixture
def vcutf():
    return generate_vc(charset=otp.utf_chars)

def test_vigenere_cipher(charsets):
    for charset in charsets:
        vc = generate_vc(charset=charset)
        encrypted_msg = vc.translated
        decrypt_vc = decrypt_vc_from_source_vc(vc)
        assert decrypt_vc.translated == vc.msg
        assert decrypt_vc.msg == vc.translated
        assert decrypt_vc.charset == vc.charset
