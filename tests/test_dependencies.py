import unittest
from importlib.metadata import version

class DependencyTests(unittest.TestCase):
    def test_pydantic_version(self):
        self.assertEqual(version('pydantic'), '2.11.7')

    def test_mcp_sdk_import(self):
        from mcp.server.fastmcp import FastMCP
        server = FastMCP('dependency-smoke-test', stateless_http=True, json_response=True)
        self.assertTrue(callable(server.streamable_http_app))
        self.assertIsNotNone(server.streamable_http_app())

if __name__ == '__main__':
    unittest.main()
