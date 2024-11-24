class Url:
    def __init__(self, scheme: str, authority: str = None, path: str | list[str] = '', query=None, fragment=None):
        self.scheme = scheme
        self.authority = authority
        self._path = path
        self._query = query
        self.fragment = fragment

    @property
    def path(self):
        if isinstance(self._path, list):
            self._path = '/' + '/'.join(self._path)
        return self._path

    @property
    def query(self):
        if isinstance(self._query, dict):
            return '&'.join([f"{key}={value}" for key, value in self._query.items()])
        return self._query

    def __str__(self):
        url = f"{self.scheme}://{self.authority}{self.path}"
        if self.query:
            url += f"?{self.query}"
        if self.fragment:
            url += f"#{self.fragment}"
        return url

    def __eq__(self, other):
        return str(self) == str(other)


class HttpsUrl(Url):
    def __init__(self, authority: str, path="", query=None, fragment=None):
        super().__init__('https', authority, path, query, fragment)


class HttpUrl(Url):
    def __init__(self, authority: str, path="", query=None, fragment=None):
        super().__init__('http', authority, path, query, fragment)


class GoogleUrl(Url):
    def __init__(self, path="", query=None, fragment=None):
        super().__init__('https', 'google.com', path, query, fragment)


class WikiUrl(Url):
    def __init__(self, path="", query=None, fragment=None):
        super().__init__('https', 'wikipedia.org', path, query, fragment)


class UrlCreator:
    def __init__(self, scheme, authority):
        self.scheme = scheme
        self.authority = authority
        self._path_parts = []
        self._query_params = {}

    def __getattr__(self, name):
        new_creator = UrlCreator(self.scheme, self.authority)
        new_creator._path_parts = self._path_parts + [name]
        return new_creator

    def __call__(self, *args, **kwargs):
        new_creator = UrlCreator(self.scheme, self.authority)
        new_creator._path_parts = self._path_parts + list(args)
        new_creator._query_params = {**self._query_params, **kwargs}
        return new_creator

    def _create(self):
        return Url(
            scheme=self.scheme,
            authority=self.authority,
            path=self._path_parts,
            query=self._query_params
        )

    def __eq__(self, other):
        return str(self._create()) == other


assert GoogleUrl() == HttpsUrl(authority='google.com')
assert GoogleUrl() == Url(scheme='https', authority='google.com')
assert GoogleUrl() == 'https://google.com'
assert WikiUrl() == str(Url(scheme='https', authority='wikipedia.org'))
assert WikiUrl(path=['wiki', 'python']) == 'https://wikipedia.org/wiki/python'
assert GoogleUrl(query={'q': 'python', 'result': 'json'}) == 'https://google.com?q=python&result=json'


url_creator = UrlCreator(scheme='https', authority='docs.python.org')
assert url_creator.docs.v1.api.list == 'https://docs.python.org/docs/v1/api/list'
assert url_creator('api', 'v1', 'list') == 'https://docs.python.org/api/v1/list'
assert url_creator('api', 'v1', 'list', q='my_list') == 'https://docs.python.org/api/v1/list?q=my_list'
assert url_creator('3').search(q='getattr', check_keywords='yes', area='default')._create()  == 'https://docs.python.org/3/search?q=getattr&check_keywords=yes&area=default'


