from abc import abstractmethod

import requests
from requests import HTTPError

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.types.EventHandler import EventHandler


class ClientRequest(object):

    def __init__(self, context):
        """
        Abstract request client

        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        """
        self._context = context
        self._queries = []
        self._current_query = None
        self.beforeExecute = EventHandler()
        self.afterExecute = EventHandler()

    @property
    def context(self):
        return self._context

    @property
    def current_query(self):
        """
        :rtype: office365.runtime.queries.client_query.ClientQuery
        """
        return self._current_query

    def add_query(self, query, execute_first=False, set_as_current=True, reset_queue=False):
        """
        :type query: office365.runtime.queries.client_query.ClientQuery
        :type execute_first: bool
        :type set_as_current: bool
        :type reset_queue: bool
        """
        if reset_queue:
            self._queries = []
        if set_as_current:
            self._current_query = query
        if execute_first:
            self._queries.insert(0, query)
        else:
            self._queries.append(query)

    def clear(self):
        self._current_query = None
        self._queries = []

    @abstractmethod
    def build_request(self, query):
        """
        :type query: office365.runtime.queries.client_query.ClientQuery
        :rtype: office365.runtime.http.request_options.RequestOptions
        """
        pass

    @abstractmethod
    def process_response(self, response):
        """
        :type response: requests.Response
        """
        pass

    def execute_query(self):
        """
        Submit a pending request to the server
        """
        for qry in self:
            try:
                request = self.build_request(qry)
                self.beforeExecute.notify(request)
                response = self.execute_request_direct(request)
                response.raise_for_status()
                self.process_response(response)
                self.afterExecute.notify(response)
            except HTTPError as e:
                raise ClientRequestException(*e.args, response=e.response)

    def execute_request_direct(self, request):
        """Execute client request

        :type request: office365.runtime.http.request_options.RequestOptions
        """
        self.context.authenticate_request(request)
        if request.method == HttpMethod.Post:
            if request.is_bytes or request.is_file:
                response = requests.post(url=request.url,
                                         headers=request.headers,
                                         data=request.data,
                                         auth=request.auth,
                                         verify=request.verify,
                                         proxies=request.proxies)
            else:
                response = requests.post(url=request.url,
                                         headers=request.headers,
                                         json=request.data,
                                         auth=request.auth,
                                         verify=request.verify,
                                         proxies=request.proxies)
        elif request.method == HttpMethod.Patch:
            response = requests.patch(url=request.url,
                                      headers=request.headers,
                                      json=request.data,
                                      auth=request.auth,
                                      verify=request.verify,
                                      proxies=request.proxies)
        elif request.method == HttpMethod.Delete:
            response = requests.delete(url=request.url,
                                       headers=request.headers,
                                       auth=request.auth,
                                       verify=request.verify,
                                       proxies=request.proxies)
        elif request.method == HttpMethod.Put:
            response = requests.put(url=request.url,
                                    data=request.data,
                                    headers=request.headers,
                                    auth=request.auth,
                                    verify=request.verify,
                                    proxies=request.proxies)
        else:
            response = requests.get(url=request.url,
                                    headers=request.headers,
                                    auth=request.auth,
                                    verify=request.verify,
                                    stream=request.stream,
                                    proxies=request.proxies)
        return response

    def __iter__(self):
        while len(self._queries) > 0:
            qry = self._queries.pop(0)
            self._current_query = qry
            yield qry
