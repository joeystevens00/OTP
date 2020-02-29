import otp.util as utils

def test_arr_to_dict():
    assert utils.array_to_dict([1,2,3,4]) == {1:2,3:4}
    assert utils.array_to_dict(["a", {1,2,3}, "b", [1,2,3]]) == {"a":{1,2,3}, "b":[1,2,3]}

def test_dict_key_value_swap():
    assert utils.dict_key_value_swap({"a":2, "b":3}) == {2:"a", 3:"b"}
