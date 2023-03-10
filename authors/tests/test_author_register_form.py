from unittest import TestCase

from django.test import TestCase as DjangoTestCase
from django.urls import reverse
from parameterized import parameterized

from authors.forms import RegisterForm


class AuthorRegisterFormUnitTest(TestCase):
    @parameterized.expand([
        ('username', 'Type your username here'),
        ('first_name', 'Type your first name here. Ex.: João'),
        ('last_name', 'Type your last name here. Ex.: Campos'),
        ('email', 'Type your email here'),
        ('password', 'Your password'),
        ('password2', 'Repeat your password'),
    ])
    def test_fields_placeholder(self, field, placeholder):
        form = RegisterForm()
        current = form[field].field.widget.attrs['placeholder']
        self.assertEqual(current, placeholder)

    @parameterized.expand([
        ('username', 'Your password must be between 4 and 150 characters long'),  # noqa:E501
        ('email', 'This email must be valid'),
        ('password', 'Password must have at least one uppercase letter, '
         'one lowercase letter and one number. The length should be '
         'at least 8 characters.'),


    ])
    def test_fields_help_text(self, field, help_text):
        form = RegisterForm()
        current = form[field].field.help_text

        self.assertEqual(current, help_text)

    @parameterized.expand([
        ('username', 'Username'),
        ('first_name', 'First Name'),
        ('last_name', 'Last Name'),
        ('email', 'Email address'),
        ('password', 'Password'),
        ('password2', 'Confirm'),
    ])
    def test_fields_label(self, field, label):
        form = RegisterForm()
        current = form[field].field.label

        self.assertEqual(current, label)


class AuthorRegisterFormIntegrationTest(DjangoTestCase):

    def setUp(self, *args, **kwargs):
        self.form_data = {
            'username': 'user',
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'email@email.com',
            'password': 'P@ssw0rd',
            'password2': 'P@ssw0rd',
        }

        return super().setUp(*args, **kwargs)

    @parameterized.expand([
        ('username', 'This field must not be empty'),
        ('email', 'This field must not be empty'),
        ('first_name', 'Write your first name'),
        ('last_name', 'Write your last name'),
        ('password', 'Password must not be empty'),
        ('password2', 'Please, repeat your password'),



    ])
    def test_fields_cannot_be_empty(self, field, msg):
        self.form_data[field] = ''
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)
        self.assertIn(msg, response.content.decode('utf-8'))
        # self.assertIn(msg, response.context['form'].errors.get(field))

    def test_username_field_min_length_should_be_4(self):
        self.form_data['username'] = 'joa'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)
        msg = 'Username must have at least 4 characters'
        self.assertIn(msg, response.context['form'].errors.get('username'))

    def test_username_field_max_length_should_be_150(self):
        self.form_data['username'] = 'A'*151
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)
        msg = 'Username must have less than 150 characters'
        self.assertIn(msg, response.context['form'].errors.get('username'))

    def test_password_field_have_lower_upper_case_letters_and_numbers(self):
        self.form_data['password'] = 'abc123'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)
        msg = 'Type a strong password'
        self.assertIn(msg, response.context['form'].errors.get('password'))

        self.form_data['password'] = '@A123abc123'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)
        self.assertNotIn(msg, response.content.decode('utf-8'))

    def test_password_and_password_confirmation_are_equal(self):
        self.form_data['password'] = '@A123abc123'
        self.form_data['password2'] = '@A123abc124'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)
        msg = 'Passwords do not match'
        self.assertIn(msg, response.context['form'].errors.get('password'))

        self.form_data['password'] = '@A123abc123'
        self.form_data['password2'] = '@A123abc123'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        self.assertNotIn(msg, response.content.decode('utf-8'))

    def test_send_get_request_to_registration_create_view_returns_404(self):
        url = reverse('authors:register_create')
        response = self.client.get(url, data=self.form_data, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_email_field_must_be_unique(self):
        url = reverse('authors:register_create')

        self.client.post(url, data=self.form_data, follow=True)

        response = self.client.post(url, data=self.form_data, follow=True)
        msg = 'User e-mail is already in use'
        self.assertIn(msg, response.context['form'].errors.get('email'))
        self.assertIn(msg, response.content.decode('utf-8'))

    def test_author_created_can_login(self):
        url = reverse('authors:register_create')
        self.form_data.update({
            'username': 'testuser',
            'password': '@Bc123456',
            'password2': '@Bc123456',
        })

        self.client.post(url, data=self.form_data, follow=True)
        is_authenticated = self.client.login(
            username='testuser', password='@Bc123456')

        self.assertTrue(is_authenticated)
