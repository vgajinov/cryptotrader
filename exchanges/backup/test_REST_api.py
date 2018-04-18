# Import Built-ins
import unittest
import requests

# Import Homebrew
from exchanges.REST.api import APIClient
from exchanges.REST.bitfinex import BitfinexRESTClient


class APITests(unittest.TestCase):
   """
   Tests APIs for connection establishment, authentication, key loading.
   """

   def setUp(self):
      self.api = APIClient('http://google.com/api', api_version='v1',
                           key='12345', secret='abcde')

   def tearDown(self):
      self.api = None

   def test_restapi_load_key(self):
      self.api.load_key("test.key")
      self.assertTrue(self.api.secret, "This_is_a_secret")
      self.assertTrue(self.api.key, "This_is_a_key")

   def test_restapi_nonce(self):
      n = self.api.nonce()
      self.assertTrue(n.strip().isdigit())

   def test_restapi_query(self):
      # Test that the unauthenticated request is built correctly
      r = self.api.query('testing/endpoint/', authenticate=False,
                         request_method=requests.get,
                         params={'test_param': "chimichanga"})
      url = 'http://google.com/api/v1/testing/endpoint/?test_param=chimichanga'
      self.assertTrue(r.request.url == url)

      # Test that authentication requests are built correctly
      r = self.api.query('testing/endpoint/', authenticate=True,
                         request_method=requests.get,
                         params={'test_param': "chimichanga"})
      url = 'http://google.com/api/v1/testing/endpoint/?test_param=authenticated_chimichanga'
      self.assertTrue(r.request.url == url)

   def test_sign_returns_tuple_of_str_and_dict(self):
      r = self.api.sign()
      self.assertIsInstance(r, tuple)
      self.assertIsInstance(r[0], str)
      self.assertIsInstance(r[1], dict)


class BitfinexAPITest(APITests):
   def setUp(self):
      self.api = BitfinexRESTClient()
      self.api.load_key('bitfinex.key')

   def test_public_query(self):
      # query() returns a valid requests.Response object
      r = self.api.query('GET', 'Time')
      self.assertIsInstance(r, requests.Response)
      self.assertEqual(r.status_code, 200)

      # query() is successful (No errors)
      self.assertTrue(r.json()['error'] == [],
                      "Error in Response: %s" % r.json()['error'])

   def test_private_query(self):
      # API Key and secret are loaded?
      self.assertTrue(self.api._key, 'API Key is empty!')
      self.assertTrue(self.api._secret, 'Secret Key is empty!')

      # query() returns a valid request object
      r = self.api.query('POST', 'private/OpenOrders', authenticate=True)
      self.assertIsInstance(r, requests.Response)

      # query() with flag authenticate=True builds valid signature (No errors)
      self.assertTrue(r.json()['error'] == [],
                      "Error in Response: %s" % r.json()['error'])







