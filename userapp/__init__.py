""" Base class for making API calls to the UserApp API. """

import sys
import re
import json
import base64
import logging
import requests

class IterableObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.source

class IterableObject(object):
    """
    Wraps a dictionary and makes it feel and
    look like an object but with the power of being iterable.
    """
    def __init__(self, source):
        object.__setattr__(self, 'source', source)

    def __iter__(self):
        return self.source.items()

    def __getattr__(self, key):
        if not key in self.source:
            raise AttributeError("Object has not attribute '{k}'".format(k=key))

        return self.source[key]

    def __setattr__(self, key, value):
        if isinstance(value, dict) or isinstance(value, list):
            value=DictionaryUtility.to_object(value)
        
        self.source[key]=value

    def __getitem__(self, key):
        return self.source[key]

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __contains__(self, key):
        return key in self.source
    
    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.source)

    def to_json(self):
        return json.dumps(self, cls=IterableObjectEncoder)

    def to_dict(self):
        return DictionaryUtility.to_dict(self)

class DictionaryUtility:
    """
    Utility methods for dealing with dictionaries.
    """
    @staticmethod
    def to_object(item):
        """
        Convert a dictionary to an object (recursive).
        """
        def convert(item): 
            if isinstance(item, dict):
                return IterableObject({k: convert(v) for k, v in item.items()})
            if isinstance(item, list):
                def yield_convert(item):
                    for index, value in enumerate(item):
                        yield convert(value)
                return list(yield_convert(item))
            else:
                return item

        return convert(item)

    @staticmethod
    def to_dict(item):
        """
        Convert an object to a dictionary (recursive).
        """
        def convert(item):
            if isinstance(item, IterableObject):
                if isinstance(item.source, dict):
                    return {k: convert(v.source) if hasattr(v, 'source') else convert(v) for k, v in item}
                else:
                    return convert(item.source)
            elif isinstance(item, dict):
                return {k: convert(v) for k, v in item.items()}
            elif isinstance(item, list):
                def yield_convert(item):
                    for index, value in enumerate(item):
                        yield convert(value)
                return list(yield_convert(item))
            else:
                return item

        return convert(item)

class UserAppException(Exception):
    """
    Base class for all UserApp exceptions.
    """
    pass

class UserAppTransportException(UserAppException):
    """
    An error occurred in the transport.
    """
    pass

class UserAppInvalidOptionException(Exception):
    """
    Option does not exist.
    """
    pass

class UserAppInvalidServiceException(UserAppException):
    """
    Service called does not exist.
    """
    def __init__(self, message, service_name=None):
        UserAppException.__init__(self, message)
        self.service_name = service_name

class UserAppInvalidMethodException(UserAppException):
    """
    Method called does not exist.
    """
    def __init__(self, message, service_name=None, method_name=None):
        UserAppException.__init__(self, message)
        self.service_name = service_name
        self.method_name = method_name

class UserAppServiceException(UserAppException):
    """
    Error response from the API.
    """
    def __init__(self, message, error_code):
        UserAppException.__init__(self, message)
        self.error_code = error_code

class NativeTransport(object):
    def __init__(self, logger):
        self._logger = logger

    def call(self, method, url, headers=None, body=None):
        if headers is None:
            headers={}

        if 'Content-Type' in headers:
            if headers['Content-Type'] == 'application/json':

                body=json.dumps(body)

        if method != 'post':
            raise UserAppTransportException("Method {m} not supported.".format(m=method))

        self._logger.debug("Calling {m} {u} with headers {h} and body {b}".format(
            m=method,
            u=url,
            h=headers,
            b=body
        ))

        response=requests.post(
            url=url,
            data=body,
            headers=headers,
            verify=True
        )

        return response

class Client(object):
    """
    Handles communication with the UserApp API.
    """
    def __init__(self, app_id, token="", base_address='api.userapp.io', throw_errors=True, secure=True, debug=False, logger=None, transport=None):
        self._app_id=app_id
        self._token=token
        self._base_address=base_address
        self._throw_errors=throw_errors
        self._secure=secure
        self._debug=debug

        # Setup logging, add handler if debug mode
        self._logger=logging.getLogger(__name__) if logger is None else logger
        if debug:
            self._logger.setLevel(logging.DEBUG)
            if len(self._logger.handlers) == 0:
                log_handler = logging.StreamHandler()
                log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                log_handler.setFormatter(log_format)
                self._logger.addHandler(log_handler)
                log_handler.setLevel(logging.DEBUG)

        self._transport=transport if not transport is None else NativeTransport(self._logger)

    def call(self, version, service, method, arguments):
        protocol = 'https' if self._secure else 'http'

        if not service:
            raise UserAppInvalidServiceException("No service specified.")

        if not service:
            raise UserAppInvalidMethodException("No method on service '{s}' specified.".format(s=service))

        target_url = "{p}://{a}/v{v}/{s}.{m}".format(
            p=protocol,
            a=self._base_address,
            v=version,
            s=service,
            m=method
        )

        encoded_credentials=None

        # Python 2/3 compatibility
        if sys.version_info[0] < 3:
            encoded_credentials=base64.b64encode('{u}:{p}'.format(u=self._app_id, p=self._token)).encode('ascii')
        else:
            encoded_credentials=base64.b64encode(byte('{u}:{p}'.format(u=self._app_id, p=self._token), 'ascii')).decode('ascii')

        response = self._transport.call(
            'post',
            url=target_url,
            headers={
                'Content-Type':'application/json',
                'Authorization':'Basic '+encoded_credentials
            },
            body=arguments
        )

        if response is None and response.status_code != 200:
            raise UserAppTransportException("Recieved HTTP status {s}, expected 200.".format(s=response.status_code))

        self._logger.debug("Recieved response={r}".format(r=response.text))
        result = DictionaryUtility.to_object(response.json())
        is_error_result=hasattr(result, 'error_code')

        # If we got an error back in the response result, or if the
        # HTTP response code was bad, raise the appropriate exception.
        if self._throw_errors and is_error_result:
            if result.error_code == 'INVALID_SERVICE':
                raise UserAppInvalidServiceException("Service '{s}' does not exist.".format(s=service), service)
            elif result.error_code == 'INVALID_METHOD':
                raise UserAppInvalidMethodException("Method '{m}' on service '{s}' does not exist.".format(m=method,s=service), service, method)
            else:
                raise UserAppServiceException(result.message, result.error_code)

        # For ease of use. Automatically set/unset the token during login/logout
        if service == 'user':
            if not is_error_result and method == 'login':
                self._token = result.token
            elif method == 'logout':
                self._token = ""

        return result

    def set_option(self, name, value):
        if not self._is_valid_option(name):
            raise UserAppInvalidOptionException("Option {s} does not exist.".format(s=name))

        return setattr(self, '_'+name, value)

    def get_option(self, name):
        if not self._is_valid_option(name):
            raise UserAppInvalidOptionException("Option {s} does not exist.".format(s=name))

        return getattr(self, '_'+name)

    def _is_valid_option(self, name):
        return name in ['app_id','token','base_address','secure','debug']

    def get_logger(self):
        return self._logger

    def set_logger(self, logger):
        self._logger = logger

class ClientProxy(object):
    """
    Proxies Python attribute/function calls into UserApp client calls.
    """
    def __init__(self, **kwargs):
        self._client=None
        self._parent=None
        self._version=1
        self._service_name=""
        self._method_name=""
        self._services={}

        if 'parent' in kwargs:
            self._parent=kwargs['parent']
            del kwargs['parent']

        if 'version' in kwargs:
            self._version=kwargs['version']
            del kwargs['version']

        if 'service_name' in kwargs:
            self._service_name=kwargs['service_name']
            del kwargs['service_name']

        if 'method_name' in kwargs:
            self._method_name=kwargs['method_name']
            del kwargs['method_name']

        if self._parent is None:
            self._client=Client(**kwargs)
        else:
            self._client=self._parent._client

    def __call__(self, *args, **kwargs):
        if self._parent is None:
            raise UserAppInvalidMethodException("Service does not exist.")

        return self._client.call(self._version, self._parent._service_name, self._method_name, kwargs)

    def __getattr__(self, name):
        name = self._apply_naming_convention(name)

        if not name in self._services:
            if self._parent is None and self._is_version(name):
                self._services[name] = ClientProxy(
                    parent=self,
                    version=name[1:]
                )
            else:
                self._services[name] = ClientProxy(
                    parent=self,
                    version=self._version,
                    service_name=name if not self._service_name else "{s}.{m}".format(s=self._service_name, m=name),
                    method_name=name
                )

        return self._services[name]

    def get_client(self):
        return self._client

    def get_option(self, name):
        return self._client.get_option(name)

    def set_option(self, name, value):
        self._client.set_option(name, value)

    def get_logger(self):
        return self._client.get_logger()

    def set_logger(self, logger):
        return self._client.set_logger(logger)

    def _is_version(self, s):
        if s.startswith('v'):
            try:
                float(s[1:])
                return True
            except ValueError:
                return False

        return False

    def _apply_naming_convention(self, value):
        return re.sub(r'(?!^)_([a-zA-Z])', lambda m: m.group(1).upper(), value)

class API(ClientProxy):
    """
    Wraps the UserApp API for ease of access.
    """
    instance=None

    def __init__(self, *args, **kwargs):
        ClientProxy.__init__(self, *args, **kwargs)

    @staticmethod
    def get_instance(**kwargs):
        if API.instance is None:
            API.instance=API(**kwargs)

        return API.instance