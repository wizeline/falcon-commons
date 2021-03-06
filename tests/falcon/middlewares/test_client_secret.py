import falcon

from wizeline.falcon.middlewares.secret import APISecretMiddleware, require_secret

from falcon import testing
from sure import expect

TEST_ROUTE = '/test'


class FalconCommonsTC(testing.TestCase):
    def __init__(self, *args, **kwargs):
        super(FalconCommonsTC, self).__init__(*args, **kwargs)


class ResourceWithoutWrapper:
    def on_get(self, req, resp):
        resp.body = 'Bye'


class ResourceWithoutRequireSecret:
    def on_get(self, req, resp):
        resp.body = 'Pass'


class PublicResource:
    is_api_secret_required = False

    def on_get(self, req, resp):
        resp.body = 'Hello'


@falcon.before(require_secret)
class Resource:
    def on_get(self, req, resp):
        resp.body = 'Hello'


class TestSecretMiddlewareRequirePublicResource(testing.TestCase):
    def setUp(self):
        self._default_headers = None
        self.auth = APISecretMiddleware(
            'secret',
            required=True
        )
        self.app = falcon.API(middleware=[self.auth])
        self.app.add_route(TEST_ROUTE, PublicResource())

    def test_access_without_token(self):
        response = self.simulate_get(TEST_ROUTE)
        expect(response.status).to.equal(falcon.HTTP_OK)

    def test_access_with_token(self):
        response = self.simulate_get(TEST_ROUTE, headers={
                'Authorization': 'secret'
            })
        expect(response.status).to.equal(falcon.HTTP_OK)

    def test_access_with_wrong_token(self):
        response = self.simulate_get(TEST_ROUTE, headers={
                'Authorization': 'this-is-not-the-right-token'
            })
        expect(response.status).to.equal(falcon.HTTP_OK)


class TestSecretMiddlewareRequired(testing.TestCase):
    def setUp(self):
        self._default_headers = None
        self.auth = APISecretMiddleware(
            'secret',
            required=True
        )
        self.app = falcon.API(middleware=[self.auth])
        self.app.add_route(TEST_ROUTE, ResourceWithoutWrapper())

    def test_access_without_token(self):
        response = self.simulate_get(TEST_ROUTE)
        expect(response.status).to.equal(falcon.HTTP_UNAUTHORIZED)

    def test_access_with_token(self):
        response = self.simulate_get(TEST_ROUTE, headers={
                'Authorization': 'secret'
            })
        expect(response.status).to.equal(falcon.HTTP_OK)

    def test_access_with_wrong_token(self):
        response = self.simulate_get(TEST_ROUTE, headers={
                'Authorization': 'this-is-not-the-right-token'
            })
        expect(response.status).to.equal(falcon.HTTP_UNAUTHORIZED)


class TestSecretMiddlewareNotRequired(testing.TestCase):
    def setUp(self):
        self._default_headers = None
        self.auth = APISecretMiddleware(
            'secret',
            required=False
        )
        self.app = falcon.API(middleware=[self.auth])
        self.app.add_route(TEST_ROUTE, Resource())

    def test_access_without_token(self):
        response = self.simulate_get(TEST_ROUTE)
        expect(response.status).to.equal(falcon.HTTP_UNAUTHORIZED)

    def test_access_with_token(self):
        response = self.simulate_get(TEST_ROUTE, headers={
                'Authorization': 'secret'
            })
        expect(response.status).to.equal(falcon.HTTP_OK)

    def test_access_with_wrong_token(self):
        response = self.simulate_get(TEST_ROUTE, headers={
                'Authorization': 'this-is-not-the-right-token'
            })
        expect(response.status).to.equal(falcon.HTTP_UNAUTHORIZED)


class TestSecretMiddlewareWithoutWrapper(testing.TestCase):
    def setUp(self):
        self._default_headers = None
        self.auth = APISecretMiddleware(
            'secret',
            required=False
        )
        self.app = falcon.API(middleware=[self.auth])
        self.app.add_route(TEST_ROUTE, ResourceWithoutRequireSecret())

    def test_access_without_token(self):
        response = self.simulate_get(TEST_ROUTE)
        expect(response.status).to.equal(falcon.HTTP_OK)

    def test_access_with_token(self):
        response = self.simulate_get(TEST_ROUTE, headers={
                'Authorization': 'secret'
            })
        expect(response.status).to.equal(falcon.HTTP_OK)

    def test_access_with_wrong_token(self):
        response = self.simulate_get(TEST_ROUTE, headers={
                'Authorization': 'this-is-not-the-right-token'
            })
        expect(response.status).to.equal(falcon.HTTP_OK)
