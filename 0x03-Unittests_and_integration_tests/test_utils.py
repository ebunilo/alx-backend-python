#!/usr/bin/env python3
"""
Unittest suite for the utils module providing tests for access_nested_map,
get_json HTTP JSON retrieval, and the memoize decorator caching behavior.
"""

import unittest
from typing import Any, Dict, Tuple
from parameterized import parameterized
from utils import access_nested_map
from unittest.mock import patch, Mock


class TestAccessNestedMap(unittest.TestCase):
    """
    Test cases for access_nested_map to ensure correct traversal and
    proper exception handling when keys are missing.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(
        self,
        nested_map: Dict[str, Any],
        path: Tuple[str, ...],
        expected: Any
    ) -> None:
        """
        Test that access_nested_map returns the expected value
        for a valid path.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(
        self,
        nested_map: Dict[str, Any],
        path: Tuple[str, ...]
    ) -> None:
        """
        Test that access_nested_map raises KeyError for an invalid path.
        """
        with self.assertRaises(KeyError):
            access_nested_map(nested_map, path)


class TestGetJson(unittest.TestCase):
    """
    Test cases for get_json to verify HTTP GET invocation and JSON parsing.
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(
        self,
        test_url: str,
        test_payload: Dict[str, Any]
    ) -> None:
        """
        Test that get_json returns expected payload and performs one GET call.
        """
        with patch("utils.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = test_payload
            mock_get.return_value = mock_response

            from utils import get_json
            result: Dict[str, Any] = get_json(test_url)

            mock_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """
    Test cases for the memoize decorator to confirm single underlying call
    and cached return value on repeated property access.
    """

    def test_memoize(self) -> None:
        """
        Test that a_method is called only once while a_property is cached.
        """
        from utils import memoize

        class TestClass:
            """
            Simple test class exposing a_method and a memoized a_property.
            """

            def a_method(self) -> int:
                """
                Return a constant integer to be used for memoization test.
                """
                return 42

            @memoize
            def a_property(self) -> int:
                """
                Return the result of a_method and
                rely on memoization to cache it.
                """
                return self.a_method()

        with patch.object(
            TestClass, "a_method", return_value=42
        ) as mock_method:
            obj = TestClass()
            first: int = obj.a_property
            second: int = obj.a_property
            self.assertEqual(first, 42)
            self.assertEqual(second, 42)
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
