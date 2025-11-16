#!/usr/bin/env python3
"""Unit tests for GithubOrgClient.

Covers:
- org property retrieval (memoized)
- _public_repos_url property derivation
- public_repos list extraction and filtering logic
"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized

from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test suite for GithubOrgClient focusing on repo/org metadata."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Verify org property returns expected payload and calls get_json once."""
        expected = {
            "name": org_name,
            "repos_url": (
                f"https://api.github.com/orgs/{org_name}/repos"
            ),
        }
        mock_get_json.return_value = expected
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected)
        mock_get_json.assert_called_once_with(
            GithubOrgClient.ORG_URL.format(org=org_name)
        )

    def test_public_repos_url(self):
        """Ensure _public_repos_url pulls repos_url from mocked org payload."""
        org_payload = {
            "repos_url": "https://api.github.com/orgs/example/repos"
        }
        with patch.object(GithubOrgClient, 'org', return_value=org_payload):
            client = GithubOrgClient("example")
            self.assertEqual(
                client._public_repos_url,
                org_payload["repos_url"],
            )

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Validate public_repos returns repo names and mocks are called once."""
        repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": {"key": "mit"}},
        ]
        mock_get_json.return_value = repos_payload
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock
        ) as mock_public_repos_url:
            mock_public_repos_url.return_value = "http://example.com/org/repos"
            client = GithubOrgClient("example")
            self.assertEqual(
                client.public_repos(),
                ["repo1", "repo2", "repo3"],
            )
            mock_public_repos_url.assert_called_once()
        mock_get_json.assert_called_once_with("http://example.com/org/repos")


if __name__ == '__main__':
    unittest.main()
