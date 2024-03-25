import unittest
from app import app, db, User

class TestApp(unittest.TestCase):

    def setUp(self):
        # Set up a test client
        self.app = app.test_client()
        # Set up an application context
        self.app_context = app.app_context()
        self.app_context.push()
        # Set up a temporary database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.create_all()

    def tearDown(self):
        # Remove the session and drop the database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_signup(self):
        # Test the signup route        
        response = self.app.post('/signup', data=dict(username='testuser', password='testpassword'))
        print(response.status_code)  # Print the status code
        print(response.data)  # Print the response data
        self.assertEqual(response.status_code, 302)  # Check for redirect status code


    def test_signin(self):
        # Create a user for testing signin
        user = User(username='testuser')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()

        # Test the signin route
        response = self.app.post('/signin', data=dict(username='testuser', password='testpassword'))

        # Check for redirect status code
        self.assertEqual(response.status_code, 302)

        # Follow the redirect and check the response of the redirected page
        response = self.app.get(response.headers['Location'], follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Chat', response.data)


    def test_reset_password(self):
        # Create a user for testing reset password
        user = User(username='testuser')
        user.set_password('oldpassword')
        db.session.add(user)
        db.session.commit()

        # Test the reset password route
        response = self.app.post('/forgotPassword', data=dict(username='testuser', new_password='newpassword', confirm_password='newpassword'))
        
        # Check if the password was updated successfully
        user = User.query.filter_by(username='testuser').first()
        self.assertTrue(user.check_password('newpassword'))

        # Check the response status code
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password has been updated successfully', response.data)


    def test_bucc_7b_bot(self):
        # Sample query
        query = "What is the course code for Data Structures?"

        # Send POST request to /bucc-7b-bot/ route
        response = self.app.post('/bucc-7b-bot/', json={'question': query})

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check if the response contains a valid answer
        # You might need to adjust this check based on the expected response format and content
        self.assertIn(b"course code", response.data)
    
        
    # Add more tests as needed...

if __name__ == '__main__':
    unittest.main()
