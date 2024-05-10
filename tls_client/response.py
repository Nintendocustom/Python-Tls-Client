import json
import os
import time
from typing import Union

from requests import HTTPError

from .cookies import RequestsCookieJar, cookiejar_from_dict
from .structures import CaseInsensitiveDict


class Response:
    """object, which contains the response to an HTTP request."""

    def __init__(self):

        # Reference of URL the response is coming from (especially useful with redirects)
        self.url = None

        # Integer Code of responded HTTP Status, e.g. 404 or 200.
        self._status_code = None

        # String of responded HTTP Body.
        self.text = None

        # Case-insensitive Dictionary of Response Headers.
        self._headers = CaseInsensitiveDict()

        # A CookieJar of Cookies the server sent back.
        self.cookies = cookiejar_from_dict({})

        self._content = False

        self.writing = True
        self._request_payload = None
        self._file = None
        self._filepath = None

        self.reason = None
        self._http_status_code = {
            100: 'Continue',
            101: 'Switching Protocols',
            102: 'Switching Protocols',
            103: 'Switching Protocols',
            200: 'OK',
            201: 'Created',
            202: 'Accepted',
            203: 'Non-Authoritative Information',
            204: 'No Content',
            205: 'Reset Content',
            206: 'Partial Content',
            207: 'Partial Content',
            208: 'Partial Content',
            226: 'Partial Content',
            300: 'Multiple Choices',
            301: 'Moved Permanently',
            302: 'Found',
            303: 'See Other',
            304: 'Not Modified',
            307: 'Temporary Redirect',
            308: 'Permanent Redirect',
            400: 'Bad Request',
            401: 'Unauthorized',
            402: 'Payment Required',
            403: 'Forbidden',
            404: 'Not Found',
            405: 'Method Not Allowed',
            406: 'Not Acceptable',
            407: 'Proxy Authentication Required',
            408: 'Request Timeout',
            409: 'Conflict',
            410: 'Gone',
            411: 'Length Required',
            412: 'Precondition Failed',
            413: 'Payload Too Large',
            414: 'URI Too Long',
            415: 'Unsupported Media Type',
            416: 'Range Not Satisfiable',
            417: 'Expectation Failed',
            418: 'I\'m a teapot',
            421: 'Misdirected Request',
            422: 'Unprocessable Entity',
            426: 'Upgrade Required',
            428: 'Precondition Required',
            429: 'Too Many Requests',
            431: 'Request Header Fields Too Large',
            451: 'Unavailable For Legal Reasons',
            500: 'Internal Server Error',
            501: 'Not Implemented',
            502: 'Bad Gateway',
            503: 'Service Unavailable',
            504: 'Gateway Timeout',
            505: 'HTTP Version Not Supported',
            506: 'Variant Also Negotiates',
            507: 'Insufficient Storage',
            508: 'Loop Detected',
            510: 'Not Extended',
            511: 'Network Authentication Required'
        }

    def __enter__(self):
        return self

    def __repr__(self):
        return f"<Response [{self.status_code}]>"

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = CaseInsensitiveDict(value)

    @property
    def status_code(self) -> int:
        return self._status_code

    @status_code.setter
    def status_code(self, status_code: int) -> None:
        self._status_code = status_code
        self.reason = self._http_status_code.get(status_code, "UNKNOWN")

    @property
    def ok(self):
        return self.status_code < 400

    def json(self, **kwargs):
        """parse response body to json (dict/list)"""
        return json.loads(self.text, **kwargs)

    @property
    def content(self):
        """Content of the response, in bytes."""

        if self._content is False:
            if self._content_consumed:
                raise RuntimeError("The content for this response was already consumed")

            if self.status_code == 0:
                self._content = None
            else:
                self._content = b"".join(self.iter_content(10 * 1024)) or b""
        self._content_consumed = True
        return self._content

    def raise_for_status(self):
        """Raises :class:`HTTPError`, if one occurred."""
        http_error_msg = ""
        if 400 <= self.status_code < 500:
            http_error_msg = (
                f"{self.status_code} Client Error: {self.reason} for url: {self.url}"
            )

        elif 500 <= self.status_code < 600:
            http_error_msg = (
                f"{self.status_code} Server Error: {self.reason} for url: {self.url}"
            )

        if http_error_msg:
            raise HTTPError(http_error_msg, response=self)

    def __open_file(self):
        start_time = time.time()
        while True:
            try:
                if not self._file:
                    self._file = open(self._filepath, "rb")
                break
            except IOError:
                time.sleep(0.1)
                if time.time() - start_time > 10:
                    raise Exception("Could not open the file within 10 seconds")

    def iter_content(self, chunk_size=1024):
        self.__open_file()
        while True:
            chunk = self._file.read(chunk_size)
            while len(chunk) < chunk_size:
                time.sleep(0.1)
                more_data = self._file.read(chunk_size - len(chunk))
                if more_data:
                    chunk += more_data
                elif not self.writing:
                    break
            if chunk:
                yield chunk
            else:
                break
        self._file.close()
        os.remove(self._filepath)

    def iter_lines(self, chunk_size=512, delimiter=None):
        pending = None

        for chunk in self.iter_content(chunk_size=chunk_size):

            chunk = chunk.decode("utf8")
            if pending is not None:
                chunk = pending + chunk

            if delimiter:
                lines = chunk.split(delimiter)
            else:
                lines = chunk.splitlines()

            if lines and lines[-1] and chunk and lines[-1][-1] == chunk[-1]:
                pending = lines.pop()
            else:
                pending = None

            yield from lines

        if pending is not None:
            yield pending


def build_response(res: Union[dict, list], res_cookies: RequestsCookieJar, filepath=None) -> Response:
    """Builds a Response object """
    response = Response()
    # Add target / url
    response.url = res["target"]
    # Add status code
    response.status_code = res["status"]
    # Add headers
    response_headers = {}
    if res["headers"] is not None:
        for header_key, header_value in res["headers"].items():
            if len(header_value) == 1:
                response_headers[header_key] = header_value[0]
            else:
                response_headers[header_key] = header_value
    response.headers = response_headers
    # Add cookies
    response.cookies = res_cookies
    # Add response body
    response.text = res["body"]
    # Add response content (bytes)
    response._content = res["body"].encode()
    response._filepath = filepath
    return response
