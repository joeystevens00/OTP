import otp.reference_db as reference_db
ReferenceDB = reference_db.ReferenceDB
ReferenceDBList = reference_db.ReferenceDBList
import otp.otp as otp
ascii_chars = otp.ascii_chars

import tests.test_otp as test_otp
otp_tests = test_otp.otp_tests
import os
import random
import pytest

@pytest.fixture
def ReferenceDBArgs():
    return {'count':random.randint(1, 1000), 'key_length':random.randint(1, 1000), 'reference_key_length':random.randint(4, 20)}
@pytest.fixture
def ReferenceDBArgsFullCharset():
    return {
        'count':random.randint(1, 1000),
        'key_length':random.randint(1, 1000),
        'reference_key_length':random.randint(4, 20),
        'charset': ascii_chars
    }

def validate_db_against_args(db, args):
    items = db.items
    assert len(items) == args.get('count')
    item_keys = list(items.keys())
    db.pop(item_keys[-1])
    first_item_key = items[item_keys[0]]
    assert len(items) == args.get('count')-1
    db.save()
    db = ReferenceDB.load(db.file)
    items = db.items
    first_item_key_refresh = items[item_keys[0]]
    otp_args = {}
    securegen_args = {}
    if args.get('charset'):
        securegen_args['charset'] = args.get('charset')
        otp_args['charset'] = args.get('charset')
    otp_tests(otp.securegen(400, **securegen_args), first_item_key, **otp_args)
    assert first_item_key == first_item_key_refresh
    assert len(items) == args.get('count')-1
    first_key = item_keys[0]
    assert len(first_key) == args.get('reference_key_length')
    assert len(items.get(first_key)) == args.get('key_length')
    ReferenceDB.delete(db.file)
    assert os.path.exists(db.file) is False


def test_db(ReferenceDBArgs):
    db = ReferenceDB.generate(**ReferenceDBArgs)
    validate_db_against_args(db, ReferenceDBArgs)

def test_db_full_chars(ReferenceDBArgsFullCharset):
    db = ReferenceDB.generate(**ReferenceDBArgsFullCharset)
    validate_db_against_args(db, ReferenceDBArgsFullCharset)

def test_db_list(ReferenceDBArgs):
    num_files = random.randint(1, 10)
    dbs = ReferenceDBList.generate(num_files, **ReferenceDBArgs)
    assert len(dbs) == num_files
    for db in dbs.list:
        validate_db_against_args(db, ReferenceDBArgs)
