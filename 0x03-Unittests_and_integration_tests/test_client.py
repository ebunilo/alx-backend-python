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

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json: MagicMock) -> None:
        """Test that public_repos returns the expected list of repo names.

        Ensures:
        - get_json is called once with the mocked _public_repos_url.
        - _public_repos_url property is accessed once.
        - Returned repo list matches expected names.
        """
        repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": {"key": "mit"}},
        ]
        mock_get_json.return_value = repos_payload

        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=property
        ) as mock_repos_url:
            mock_repos_url.return_value = "mocked_url"
            client = GithubOrgClient("testorg")
            result = client.public_repos()
            self.assertEqual(result, ["repo1", "repo2", "repo3"])
            mock_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with("mocked_url")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected) -> None:
        """Test has_license returns correct boolean
        based on license key match.
        """
        client = GithubOrgClient("testorg")
        self.assertEqual(client.has_license(repo, license_key), expected)


if __name__ == "__main__":
    unittest.main()
