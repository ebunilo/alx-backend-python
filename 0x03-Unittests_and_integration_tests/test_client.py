#!/usr/bin/env python3

"""Unit tests for the GithubOrgClient class.

This module validates that the client correctly retrieves organization
metadata from the GitHub API abstraction without performing real HTTP calls.
"""

import unittest
from unittest.mock import patch, MagicMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


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


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos,
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient using fixture payloads."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up class-wide mocks for external HTTP requests."""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        org_login = cls.org_payload.get("login", "org")
        cls.org_url = f"https://api.github.com/orgs/{org_login}"
        cls.repos_url = cls.org_payload.get("repos_url")

        def side_effect(url):
            """Side effect function to return mock responses based on URL."""
            mock_resp = MagicMock()
            if url == cls.org_url:
                mock_resp.json.return_value = cls.org_payload
            elif url == cls.repos_url:
                mock_resp.json.return_value = cls.repos_payload
            else:
                mock_resp.json.return_value = {}
            return mock_resp

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        """Stop the requests.get patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """Test that public_repos returns all expected repo names (fixtures)."""
        client = GithubOrgClient(self.org_payload.get("login"))
        self.assertEqual(client.public_repos(), self.expected_repos)
        # Ensure external calls were made to org and repos URLs
        self.mock_get.assert_any_call(self.org_url)
        self.mock_get.assert_any_call(self.repos_url)

    def test_public_repos_with_license(self) -> None:
        """Test filtering repos by apache-2.0 license using fixtures."""
        client = GithubOrgClient(self.org_payload.get("login"))
        self.assertEqual(client.public_repos("apache-2.0"), self.apache2_repos)


if __name__ == "__main__":
    unittest.main()
