import otp.otp as otp
import base64
VERSION = 0.01


def charset_get_encoding(charset, default='utf-8'):
    for encoding in encodings_from_charset.keys():
        if charset in encodings_from_charset[encoding]:
            return encoding
    return default


def array_to_dict(arr):
    c = 1
    k = None
    d = {}
    if len(arr) % 2 == 1:
        raise ValueError('Array must be even length')
    for i in arr:
        # Even Rounds are Values
        if c % 2 == 0:
            d[k] = i
        else: # Odd Rounds are Keys
            k = i
        c+=1
    return d


def dict_key_value_swap(d):
    if not isinstance(d, dict):
        raise ValueError("Must be given dict")
    nd = {}
    for k in d.keys():
        nd[d[k]] = k
    return nd


def nested_operation(d, func, *args, **named_args):
    """
    Executes string operation on dict,list,tuple or string
    """
    c = 0
    s = d
    if isinstance(d, str):
        d = func(str, *args, **named_args)
    else:
        for k in d:
            update_key = c
            if isinstance(d, dict):
                update_key = k
            v = d[update_key]
            if isinstance(v, (dict, list, tuple)):
                v = nested_operation(v, func, *args, **named_args)
            else:
                v = func(v, *args, **named_args)
            d[update_key] = v
            c = c+1
    return d


def decodeb64(x, encoding='utf-8', encoding_options=[]):
    return base64.b64decode(x).decode(encoding, *encoding_options)


def encodeb64(x, encoding='utf-8', encoding_options=[]):
    return base64.b64encode(x.encode(encoding, *encoding_options)).decode('utf-8')


charset_options = {
    'ascii': otp.ascii_chars,
    'unicode':otp.utf_chars,
    'alphanumeric':otp.letters+otp.numbers
}

charset_to_option = dict_key_value_swap(charset_options)

charset_option_arg = {
    'ascii': 'ascii_charset',
    'unicode':'utf_charset',
    'alphanumeric':None
}

encodings_from_charset = {
    'utf-16': [otp.utf_chars, 'unicode', 'utf_charset'],
    'utf-8': [otp.ascii_chars, 'ascii', 'ascii_charset']
}
