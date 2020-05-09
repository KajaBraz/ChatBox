import unittest

import src.my_json as my_json
from enums import MessageTypes, JsonFields


class MyTestCase(unittest.TestCase):
    def test_json_to_dict(self):
        # GIVEN
        json = b'{"field1": "value1", "field2": 11}'
        expected_dict = {"field2": 11, "field1": "value1"}

        # WHEN
        result = my_json.from_json(json)

        # THEN
        self.assertEqual(expected_dict, result)

    def test_wrong_json_to_dict(self):
        json = b'{"fiels"'
        expected_dict = {}
        result = my_json.from_json(json)
        self.assertEqual(expected_dict, result)

    def test_dict_to_json(self):
        d = {"nested": {"a": "a", "b": 1}, "field": False}
        as_json = my_json.to_json(d)

        d_result = my_json.from_json(as_json)

        self.assertEqual(d, d_result)

    def test_is_proper_json(self):
        j1 = '{"message_type":"user", "message_value":"i am white", "message_receiver":"sheep"}'
        j2 = '{"type":""}'
        expected_res1 = True
        expected_res2 = False
        result1 = my_json.is_proper_json(j1)
        result2 = my_json.is_proper_json(j2)

        self.assertEqual(expected_res1, result1)
        self.assertEqual(expected_res2, result2)

    def test_join_json_len(self):
        j = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE, JsonFields.MESSAGE_VALUE: 'abcdef'}
        j_b = my_json.to_json(j)
        j_with_len = my_json.join_json_len(j_b)
        j_len = int.from_bytes(j_with_len[:2], 'big')
        exp_res = len(j_b)

        self.assertEqual(j_len, exp_res)

    def test_count_jsons(self):
        j1 = my_json.to_json({'a': 1})
        j2 = my_json.to_json({'b': 2})

        j1_len = len(j1).to_bytes(2, 'big')
        j2_len = len(j2).to_bytes(2, 'big')
        jj = j1_len + j1 + j2_len + j2

        exp_res = [j1, j2]
        res = my_json.count_jsons(jj)

        self.assertEqual(res, exp_res)


if __name__ == '__main__':
    unittest.main()
