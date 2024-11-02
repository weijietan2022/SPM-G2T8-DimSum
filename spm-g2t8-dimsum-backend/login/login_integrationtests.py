import unittest
from login import app

class UnitTestLogin(unittest.TestCase):
        
        def setUp(self):
            self.app = app.test_client()
            self.app.testing = True
    
        def test_login_success(self):
            response = self.app.post('/api/login', json={
                'email': 'titans.aravind@gmail.com',
                'password': '999998'
            })
            self.assertEqual(response.status_code, 200)
            response_json = response.get_json()
            self.assertEqual(response_json['status'], 'success')
            self.assertEqual(response_json['name'], 'Test Manager')
            self.assertEqual(response_json['position'], 'Testing')

        def test_login_fail(self):
            response = self.app.post('/api/login', json={
                'email': 'aaaa',
                'password': '999998'
            })
            self.assertEqual(response.status_code, 401)
            response_json = response.get_json()
            self.assertEqual(response_json['status'], 'fail')
            self.assertEqual(response_json['message'], 'Invalid email or password.')

if __name__ == '__main__':
    unittest.main()
