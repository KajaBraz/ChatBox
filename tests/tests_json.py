import unittest

import src.my_json as my_json


class MyTestCase(unittest.TestCase):
    def test_json_to_dict(self):
        json = '{"field1": "value1", "field2": 11}'
        expected_dict = {"field2": 11, "field1": "value1"}

        result = my_json.from_json(json)

        self.assertEqual(expected_dict, result)

    def test_wrong_json_to_dict(self):
        json = '{"fiels"'
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
        j2 = '{"message_type":"message"}'
        expected_res1 = True
        expected_res2 = False
        result1 = my_json.is_proper_json(j1)
        result2 = my_json.is_proper_json(j2)

        self.assertEqual(expected_res1, result1)
        self.assertEqual(expected_res2, result2)


if __name__ == '__main__':
    unittest.main()
