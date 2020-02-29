from cli import main
import cli
import sys
import pytest
import otp.otp as otp
import os
import random
from otp.util import array_to_dict, dict_key_value_swap
import otp.util as util
pkg = 'cli.py'
sys.argv = [pkg]
output_file = 'unittest-{}.json'.format(otp.securegen(8))
test_file = 'unittest-{}.otp'.format(otp.securegen(8))
test_file_key = 'unittest-{}.otp_key'.format(otp.securegen(8))
test_encrypted_file = 'unittest-{}.otp'.format(otp.securegen(8))

DATA_DIR = "{}/../data".format(os.path.dirname(os.path.abspath(__file__)))
@pytest.fixture
def encrypt_string():
    yield sys.argv + ['-m', otp.securegen(100), '-oj', output_file]
    os.remove(output_file)

@pytest.fixture
def cleanup_output_file():
    yield
    os.remove(output_file)
@pytest.fixture
def cleanup_test_file():
    yield
    os.remove(test_file)
@pytest.fixture
def cleanup_test_encrypted_file():
    yield
    os.remove(test_encrypted_file)
@pytest.fixture
def cleanup_test_file_key():
    yield
    os.remove(test_file_key)
@pytest.fixture
def output_file_arg():
    return {'output_json':output_file}

@pytest.fixture
def image_file():
    return "{}/screenshot.png".format(DATA_DIR)
def new_argv(args):
    sys.argv = [pkg] + args
    return sys.argv

def execute(args):
    main(sys.argv[1:], no_exit=True)
    result = cli.CLI(args={**output_file_arg(),**args}).get_message_from_file(file_arg='output_json', mode='r')
    return result
def cli_validate(encrypt_argv=['-m', otp.securegen(100)], decrypt_argv=['-m', '{}'], execute_args={}, include_key=True):
    """
    Calls main() with encrypt and decrypt arguments.
    decrypt_argv supports inserting encrypted_msg by setting -m to {}
    """
    encrypt_args = new_argv([*encrypt_argv, '-oj', output_file])
    result = execute(execute_args)
    encrypted_msg = result['MESSAGE']
    errors = result['ERRORS']
    key = result['KEY']
    e_args = array_to_dict(encrypt_args[1:])
    msg = e_args.get('-m')
    # If no msg and have a message file then load message file
    if not msg and e_args.get('-f'):
        args = {'encoding':execute_args.get('encoding', 'utf-8'), 'file_arg':'message_file', 'message_file': e_args.get('-f')}
        msg = cli.CLI(args).get_message_from_file()
    assert len(key) == len(encrypted_msg)
    assert len(encrypted_msg) == len(msg)
    assert len(errors) == 0
    decrypt_argv = [ i.format(encrypted_msg) if '{}' else i for i in decrypt_argv ]
    key_args = ['-k', key]
    if not include_key:
        key_args = []
    decrypt_args = new_argv(['-d', *decrypt_argv, *key_args, '-oj', output_file])
    decrypt_result = execute(execute_args)
    assert msg == decrypt_result['MESSAGE']
    assert len(decrypt_result['ERRORS']) == 0
    assert decrypt_result['KEY'] == key

def test_encrypt(cleanup_output_file):
    sys.argv = encrypt_string
    cli_validate()
    for option, charset in util.charset_options.items():
        encoding = None
        if option is 'unicode':
            encoding = 'utf-16'
        cli_validate(
            decrypt_argv=['-m', '{}', '--charset', option],
            encrypt_argv=['-m', otp.securegen(100, charset=charset), '--charset', option],
            execute_args = {'encoding':encoding }
        )

def test_nested_operation():
    roll = random.randint(20,1000)
    makenumber = lambda x : roll
    data = {'a':1, 'b':{'c':[1, 2, {'d':{1,2,3}}]}}
    expected_result = {'a':roll, 'b':{'c':[roll, roll, {'d':roll}]}}
    assert util.nested_operation(data, makenumber) == expected_result
    multiply_num = lambda x,y : x*y
    assert util.nested_operation([2,3,[4,5]], multiply_num, 2) == [4,6,[8,10]]


def test_encrypt_output_file(cleanup_test_file, cleanup_test_file_key, cleanup_output_file):
    cli_validate(
        decrypt_argv=['-f', test_file, '--charset', 'unicode', '-kf', test_file_key],
        encrypt_argv=['-m', otp.securegen(100, charset=otp.utf_chars), '--charset', 'unicode', '-o', test_file, '-ok', test_file_key],
        execute_args = {'encoding':'utf-16' },
        include_key = False
    )
def test_file_message_passing(cleanup_test_file):
    messages = [otp.utf_chars[-1], otp.securegen(256, charset=otp.utf_chars)]
    for message in messages:
        args = {'encoding':'utf-16', 'file_arg':'message_file', 'message_file':test_file}
        cli.CLI(args).store_message_file(test_file, message)
        assert message == cli.CLI(args).get_message_from_file()
def test_encrypt_input_file(cleanup_test_file, cleanup_test_file_key, cleanup_test_encrypted_file, cleanup_output_file):
    for charset in util.charset_options.keys():
        args = {'encoding':util.charset_get_encoding(charset), 'file_arg':'message_file', 'message_file':test_file}
        cli.CLI(args).store_message_file(test_file, otp.securegen(100, charset=util.charset_options[charset]))
        cli_validate(
            decrypt_argv=['-f', test_encrypted_file, '-kf', test_file_key, '--charset', charset],
            encrypt_argv=['-f', test_file, '-ok', test_file_key, '-o', test_encrypted_file, '--charset', charset],
            execute_args = {'encoding': util.charset_get_encoding(charset)},
            include_key = False
        )

#
# def test_encrypt_image(image_file):
#     encrypted_image_file = "{}/encrypted_image.otp".format(DATA_DIR)
#     key_file = "{}/encrypted_image.otp_key".format(DATA_DIR)
#     cli_validate(
#         decrypt_argv=['-f', encrypted_image_file, '--charset', 'unicode', '-kf', key_file],
#         encrypt_argv=['-f', image_file, '--charset', 'unicode', '-ok', key_file, '-o', encrypted_image_file],
#         execute_args = {'encoding':'utf-16' },
#         include_key = False
#     )
# TODO
# Test generation
# Test different output options
# Validate STDOUT?

# Test image file with unicode
