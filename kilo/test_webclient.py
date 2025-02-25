import unittest
from unittest.mock import patch, MagicMock
from components.core.webclient import WebClient, open_webclient

class TestWebClient(unittest.TestCase):

    @patch('components.core.webclient.Session')
    def test_start_stop(self, MockSession):
        mock_session = MockSession.return_value
        client = WebClient()

        # Test start
        client.start()
        self.assertTrue(mock_session.called)

        # Test stop
        client.stop()
        self.assertTrue(mock_session.close.called)

    @patch('components.core.webclient.Session.get')
    def test_get_success(self, mock_get):
        client = WebClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'key': 'value'}
        mock_get.return_value = mock_response

        url = 'http://example.com'
        response = client.get(url)

        self.assertEqual(response, {'key': 'value'})
        mock_get.assert_called_with(url, headers={"User-Agent": "Mozilla/5.0"})

    @patch('components.core.webclient.Session.get')
    def test_get_failure(self, mock_get):
        client = WebClient()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        url = 'http://example.com'
        response = client.get(url)

        self.assertIn('errorMessage', response)
        mock_get.assert_called_with(url, headers={"User-Agent": "Mozilla/5.0"})

    def test_context_manager(self):
        with patch.object(WebClient, 'start') as mock_start, \
             patch.object(WebClient, 'stop') as mock_stop:
            with open_webclient() as client:
                self.assertIsInstance(client, WebClient)
                mock_start.assert_called_once()
            mock_stop.assert_called_once()

if __name__ == '__main__':
    unittest.main()
