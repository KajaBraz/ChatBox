import unittest
import my_json


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
        expected_json = '{"field": false, "nested": {"a": "a", "b":1}}'

        result = my_json.to_json(d)

        self.assertEqual(expected_json, result)

    def test_is_proper_json(self):
        j1 = '{"message_type":"user", "message_value":"i am white", "message_receiver":"sheep"}'
        j2 = '{"message_type":"message"}'
        expected_res1 = True
        expected_res2 = False
        result1 = my_json.is_proper_json(j1)
        result2 = my_json.is_proper_json(j2)

        self.assertEqual(expected_res1, result1)
        self.assertEqual(expected_res2, result2)

    def test_print_to_json(self):
        print(my_json.to_json({'one': 1, 'two': 2}))

    def test_print_from_jason(self):
        print(my_json.from_json('{"one": 1, "two": 2}'))


if __name__ == '__main__':
    unittest.main()
