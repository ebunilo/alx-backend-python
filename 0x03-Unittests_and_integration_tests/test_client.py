#!/usr/bin/env python3

"""Unit tests for the GithubOrgClient class.

This module validates that the client correctly retrieves organization
metadata from the GitHub API abstraction without performing real HTTP calls.
"""

import unittest
from unittest.mock import patch, MagicMock
from parameterized import parameterized

from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test suite for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str, mock_get_json: MagicMock) -> None:
        """Test that GithubOrgClient.org returns expected org payload.

        Ensures:
        - get_json is invoked exactly once with the formatted org URL.
        - Returned value matches mocked JSON.
        """
        expected = {
            "repos_url": f"https://api.github.com/orgs/{org_name}/repos"
        }
        mock_get_json.return_value = expected

        client = GithubOrgClient(org_name)
        result = client.org

        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, expected)

    def test_public_repos_url(self) -> None:
        """Test that _public_repos_url returns
        the correct repos_url from org payload.
        """
        test_payload = {
            "repos_url": "https://api.github.com/orgs/testorg/repos"
        }
        with patch.object(
            GithubOrgClient, "org", new_callable=property
        ) as mock_org:
            mock_org.return_value = test_payload
            client = GithubOrgClient("testorg")
            result = client._public_repos_url
            self.assertEqual(result, test_payload["repos_url"])


if __name__ == "__main__":
    unittest.main()
