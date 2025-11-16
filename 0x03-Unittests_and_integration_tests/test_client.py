#!/usr/bin/env python3
import unittest
from unittest.mock import patch
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


if __name__ == '__main__':
    unittest.main()
