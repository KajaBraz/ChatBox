import src.my_json as my_json


def test_json_to_dict():
    # GIVEN
    json = '{"field1": "value1", "field2": 11}'
    expected_dict = {"field2": 11, "field1": "value1"}

    # WHEN
    result = my_json.from_json(json)

    # THEN
    assert expected_dict == result


def test_wrong_json_to_dict():
    json = '{"fiels"'
    expected_dict = {}
    result = my_json.from_json(json)
    assert expected_dict == result


def test_dict_to_json():
    d = {"nested": {"a": "a", "b": 1}, "field": False}
    as_json = my_json.to_json(d)

    d_result = my_json.from_json(as_json)

    assert d == d_result


def test_is_proper_json():
    j1 = '{"message_type":"user", "message_value":"i am white", "message_receiver":"sheep"}'
    j2 = '{"type":""}'
    expected_res1 = True
    expected_res2 = False
    result1 = my_json.is_proper_json(j1)
    result2 = my_json.is_proper_json(j2)

    assert expected_res1 == result1
    assert expected_res2 == result2
