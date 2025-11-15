#!/usr/bin/env python3
"""
Unit and integration tests for the GithubOrgClient class.

This module contains:
- Pure unit tests that mock all external interactions.
- Integration-style tests that only mock network I/O (requests.get),
  exercising the interaction between methods and fixture data.
Fixtures imported from fixtures.py provide deterministic payloads:
org_payload, repos_payload, expected_repos, apache2_repos.
"""

import unittest
from unittest.mock import patch, MagicMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """
    Unit tests for individual behaviors of GithubOrgClient.

    All HTTP-layer functionality is mocked to isolate logic within the client.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str, mock_get_json: MagicMock) -> None:
        """
        Test that GithubOrgClient.org returns expected organization data.

        Args:
            org_name: Organization name to initialize the client.
            mock_get_json: Mock for client.get_json.
        Ensures:
            - get_json called once with the correct URL.
            - Returned value matches the mocked payload.
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
        """
        Test that _public_repos_url returns the repos_url from the org payload.

        Uses patching of the org property to supply a synthetic payload.
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
        """
        Test that public_repos returns the expected list of repository names.

        Mocks:
            - _public_repos_url property.
            - get_json call to return a synthetic repo list.
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
        """
        Test has_license returns correct boolean based on license key match.

        Args:
            repo: Repository metadata dict containing license info.
            license_key: License key to match.
            expected: Expected boolean result.
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
    """
    Integration tests for GithubOrgClient.

    Only the outgoing HTTP calls (requests.get) are mocked. The client
    methods interact with real fixture data to validate end-to-end behavior
    (minus network).
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Start patching requests.get and configure side effects.

        Creates:
            cls.get_patcher: Active patcher for requests.get.
            cls.mock_get: The started mock object.
            cls.org_url / cls.repos_url: Derived URLs used in side effects.
        Side effects:
            - org URL returns org_payload.
            - repos URL returns repos_payload.
            - Any other URL returns {}.
        """
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        org_login = cls.org_payload.get("login", "org")
        cls.org_url = f"https://api.github.com/orgs/{org_login}"
        cls.repos_url = cls.org_payload.get("repos_url")

        def side_effect(url: str):
            """
            Side effect dispatcher for requests.get.

            Args:
                url: URL passed to requests.get.
            Returns:
                Mock response whose json() yields a payload based on URL.
            """
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
        """
        Stop the requests.get patcher started in setUpClass.
        """
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """
        Test that public_repos returns all expected repository names.

        Verifies:
            - Returned list matches expected_repos fixture.
            - requests.get invoked for both org and repos URLs.
        """
        client = GithubOrgClient(self.org_payload.get("login"))
        self.assertEqual(client.public_repos(), self.expected_repos)
        self.mock_get.assert_any_call(self.org_url)
        self.mock_get.assert_any_call(self.repos_url)

    def test_public_repos_with_license(self) -> None:
        """
        Test filtering repositories by the apache-2.0 license.

        Verifies:
            - Returned list matches apache2_repos fixture.
        """
        client = GithubOrgClient(self.org_payload.get("login"))
        self.assertEqual(client.public_repos("apache-2.0"), self.apache2_repos)


if __name__ == "__main__":
    unittest.main()
