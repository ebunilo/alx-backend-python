#!/usr/bin/env python3
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized

from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test the org property of the GithubOrgClient"""
        expected = {"name": org_name, "repos_url": f"https://api.github.com/orgs/{org_name}/repos"}
        mock_get_json.return_value = expected
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected)
        mock_get_json.assert_called_once_with(GithubOrgClient.ORG_URL.format(org=org_name))

    def test_public_repos_url(self):
        org_payload = {"repos_url": "https://api.github.com/orgs/example/repos"}
        with patch.object(GithubOrgClient, 'org', return_value=org_payload):
            client = GithubOrgClient("example")
            self.assertEqual(client._public_repos_url, org_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": {"key": "mit"}},
        ]
        mock_get_json.return_value = repos_payload
        with patch.object(GithubOrgClient, '_public_repos_url', new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = "http://example.com/org/repos"
            client = GithubOrgClient("example")
            self.assertEqual(client.public_repos(), ["repo1", "repo2", "repo3"])
            mock_public_repos_url.assert_called_once()
        mock_get_json.assert_called_once_with("http://example.com/org/repos")


if __name__ == '__main__':
    unittest.main()
