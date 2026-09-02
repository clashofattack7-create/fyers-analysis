//===== fyers_apiv3/__init__.py=====//name = "FyersApi"
//===== fyers_apiv3/fyersModel.py=====//import logging
import urllib.parse
import hashlib
import json
import subprocess
import sys
import requests
import json
import urllib
import aiohttp
import json
from fyers_apiv3.fyers_logger import FyersLogger


class Config:

    #URL's
    API = 'https://api-t1.fyers.in/api/v3'
    DATA_API = "https://api-t1.fyers.in/data"

    # Endpoint
    get_profile = "/profile"
    tradebook = "/tradebook"
    positions = "/positions"
    holdings = "/holdings"
    convert_position = "/positions"
    funds = "/funds"
    orders_endpoint = "/orders/sync"
    gtt_orders_sync = "/gtt/orders/sync"
    orderbook = "/orders"
    gtt_orders = "/gtt/orders"
    market_status = "/marketStatus"
    auth = "/generate-authcode"
    generate_access_token = "/validate-authcode"
    generate_data_token = "/data-token"
    data_vendor_td = "/truedata-ws"
    multi_orders = "/multi-order/sync"
    history = "/history"
    quotes = "/quotes"
    market_depth = "/depth"
    option_chain = "/options-chain-v3"
    multileg_orders = "/multileg/orders/sync"
    logout = "/logout"
    price_alert ="/price-alert"
    toggle_alert = "/toggle-alert"
    create_smartorder_step ="/smart-order/step"
    create_smartorder_limit ="/smart-order/limit"
    create_smartorder_trail ="/smart-order/trail"
    create_smartorder_sip ="/smart-order/sip"
    modify_smartorder="/smart-order/modify"
    cancel_smartorder="/smart-order/cancel"
    pause_smartorder="/smart-order/pause"
    resume_smartorder="/smart-order/resume"
    smartorder_orderbook="/smart-order/orderbook"
    smartexit_trigger="/flows/tc/se"
    activate_smartexit_trigger="/flows/tc/se/activate"
    orderhistory = "/order-history"
    tradeHistory = "/trade-history"
    charges_history = "/charges-history"
    realised_profit_history = "/realised-pnl-history"
    tax_pnl_history = "/tax-pnl-history"
    ledger_history = "/ledger-history"
    screeners_config = "/screeners/config"
    screeners_query = "/screeners/query"
    screeners_candlestick = "/screeners/candlestick"
    screeners_technical = "/screeners/technical"


class FyersServiceSync:
    def __init__(self, logger,request_logger):
        """
        Initializes an instance of FyersServiceSync.

        Args:
            logger: The logger object used for logging errors.
            request_logger: The logger object used for logging requests.
        """
        self.api_logger = logger
        self.request_logger = request_logger
        self.content = "application/json"
        self.error_resp = {"s":"error", "code": 0 , "message":"Bad request"}
        self.error_message = "invalid input please check your input"
        self.session = requests.Session()


    def post_call(self, api: str, header: str, data=None) -> dict:
        """
        Makes a POST request to the specified API.

        Args:
            api: The API endpoint to make the request to.
            header: The authorization header for the request.
            data: The data to send in the request payload.

        Returns:
            The response JSON as a dictionary, or the response object if an error occurs.
        """
        try:
            URL = Config.API + api 
            response = self.session.post(
                URL,
                data=json.dumps(data),
                headers={"Authorization": header, "Content-Type": self.content ,"version": "3"},
            )
            self.request_logger.debug({"Status Code":response.status_code, "API":api  })
            self.api_logger.debug({"URL": URL, "post data": json.dumps(data), \
                                   "Response Status Code": response.status_code, \
                                    "Response": response.json()})
            response.raise_for_status()
            return response.json()
        
        except requests.HTTPError as e:
            self.api_logger.error({"API":api, "Error": response.json()})
            return response.json()
            
        except TypeError as e:
            if "response" in locals():
                self.error_resp["code"] = response.status_code
            else:
                self.error_resp["code"] = -99
                self.error_resp["message"]=self.error_message
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": URL,"data": json.dumps(data),"message": self.error_resp})
            return self.error_resp 
                 
        except Exception as e:
            if "response" in locals():
                self.error_resp["code"] = response.status_code
            else:
                self.error_resp["code"] = -99
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": URL,"data": json.dumps(data),"message": e})
            return self.error_resp

    def get_call(self, api: str, header: str, data=None, data_flag=False) -> dict:
        """
        Makes a GET request to the specified API.

        Args:
            api: The API endpoint to make the request to.
            header: The authorization header for the request.
            data: The data to send in the request query parameters.
            data_flag: A flag indicating whether to use custom data URLs.

        Returns:
            The response JSON as a dictionary, or the response object if an error occurs.
        """
        try:
            if data_flag:
                URL = Config.DATA_API + api
            else:
                URL = Config.API + api  
            if data is not None:
                url_params = urllib.parse.urlencode(data)
                URL = URL + "?" + url_params   
            response = self.session.get(
                url=URL,
                headers={
                    "Authorization": header,
                    "Content-Type": self.content,
                    "version": "3"
                },
            )
            self.request_logger.debug({"Status Code":response.status_code, "API":api  })
            self.api_logger.debug({"URL": URL, "Status Code": response.status_code, "Response": response.json()})
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            self.api_logger.error({"API":api, "Error": response.json()})
            return response.json()
   
        except TypeError as e:
            if "response" in locals():
                self.error_resp["code"] = response.status_code
            else:
                self.error_resp["code"] = -99
                self.error_resp["message"]=self.error_message
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": URL,"message": self.error_resp})
            return self.error_resp 
                 
        except Exception as e:
            if "response" in locals():
                self.error_resp["code"] = response.status_code
            else:
                self.error_resp["code"] = -99
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": URL,"message": e})
            return self.error_resp
        
    def delete_call(self, api: str, header: str, data) -> dict:
        """
        Makes a DELETE request to the specified API.

        Args:
            api: The API endpoint to make the request to.
            header: The authorization header for the request.
            data: The data to send in the request payload.

        Returns:
            The response JSON as a dictionary, or the response object if an error occurs.
        """
        try:
            URL = Config.API + api
            response = self.session.delete(
                URL,
                data=json.dumps(data),
                headers={"Authorization": header, "Content-Type": self.content ,"version": "3"},
            )
            self.request_logger.debug({"Status Code":response.status_code, "API":api  })
            self.api_logger.debug({"URL": URL, "data": json.dumps(data), \
                                   "Response Status Code": response.status_code,\
                                   "Response": response.json()})
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            self.api_logger.error({"API":api, "Error": response.json()})
            return response.json()
        
        except TypeError as e:
            if "response" in locals():
                self.error_resp["code"] = response.status_code
            else:
                self.error_resp["code"] = -99
                self.error_resp["message"]=self.error_message
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": URL,"data": json.dumps(data),"message": self.error_resp})
            return self.error_resp 
                 
        except Exception as e:
            if "response" in locals():
                self.error_resp["code"] = response.status_code
            else:
                self.error_resp["code"] = -99
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": URL,"data": json.dumps(data),"message": e})
            return self.error_resp
        

    def patch_call(self, api: str, header: str, data) -> dict:
        """
        Makes a PATCH request to the specified API.

        Args:
            api: The API endpoint to make the request to.
            header: The authorization header for the request.
            data: The data to send in the request payload.

        Returns:
            The response JSON as a dictionary, or the response object if an error occurs.
        """
        try:
            URL = Config.API + api
            response = self.session.patch(
                URL,
                data=json.dumps(data),
                headers={"Authorization": header, "Content-Type": self.content ,"version": "3"},
            )
            self.request_logger.debug({"Status Code":response.status_code, "API":api  })
            self.api_logger.debug({"URL": URL, "data": json.dumps(data), \
                                   "Response Status Code": response.status_code, \
                                   "Response": response.json()})
            response.raise_for_status()            
            return response.json()

        except requests.HTTPError as e:
            self.api_logger.error({"API":api, "Error": response.json()})
            return response.json()
        
        except TypeError as e:
            if "response" in locals():
                self.error_resp["code"] = response.status_code
            else:
                self.error_resp["code"] = -99
                self.error_resp["message"]=self.error_message
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": URL,"data": json.dumps(data),"message": self.error_resp})
            return self.error_resp 
                 
        except Exception as e:
            if "response" in locals():
                self.error_resp["code"] = response.status_code
            else:
                self.error_resp["code"] = -99
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": URL,"data": json.dumps(data),"message": e})
            return self.error_resp

    def put_call(self, api: str, header: str, data) -> dict:
        """
        Makes a PUT request to the specified API.

        Args:
            api: The API endpoint to make the request to.
            header: The authorization header for the request.
            data: The data to send in the request payload.

        Returns:
            The response JSON as a dictionary, or the response object if an error occurs.
        """
        try:
            URL = Config.API + api
            response = self.session.put(
                URL,
                data=json.dumps(data),
                headers={"Authorization": header, "Content-Type": self.content ,"version": "3"},
            )
            self.request_logger.debug({"Status Code":response.status_code, "API":api  })
            self.api_logger.debug({"URL": URL, "data": json.dumps(data), \
                                   "Response Status Code": response.status_code, \
                                   "Response": response.json()})
            response.raise_for_status()            
            return response.json()

        except requests.HTTPError as e:
            self.api_logger.error({"API":api, "Error": response.json()})
            return response.json()
        
        except TypeError as e:
            if "response" in locals():
                self.error_resp["code"] = response.status_code
            else:
                self.error_resp["code"] = -99
                self.error_resp["message"]=self.error_message
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": URL,"data": json.dumps(data),"message": self.error_resp})
            return self.error_resp 
                 
        except Exception as e:
            if "response" in locals():
                self.error_resp["code"] = response.status_code
            else:
                self.error_resp["code"] = -99
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": URL,"data": json.dumps(data),"message": e})
            return self.error_resp

class FyersServiceAsync:
    def __init__(self, logger, request_logger):
        """
        Initializes an instance of FyersServiceAsync.

        Args:
            logger: The logger object used for logging errors.
            request_logger: The logger object used for logging requests.
        """
        self.api_logger = logger
        self.request_logger = request_logger
        self.content = "application/json"
        self.error_resp = {"s":"error", "code": 0 , "message":"Bad request"}
        self.error_message = "invalid input please check your input"
        self.session = None
        self._session_created_here = True


    async def post_async_call(self, api: str, header: str, data=None) -> dict:
        """
        Makes an asynchronous POST request to the specified API.

        Args:
            api: The API endpoint to make the request to.
            header: The authorization header for the request.
            data: The data to send in the request payload.

        Returns:
            The response JSON as a dictionary, or the response object if an error occurs.
        """
        try:
            url = Config.API + api
            # Create session on first use if not provided
            if self.session is None:
                self.session = aiohttp.ClientSession()
            
            headers = {"Authorization": header, "Content-Type": self.content, "version": "3"}
            async with self.session.post(url, data=json.dumps(data), headers=headers) as response:
                self.request_logger.debug({"Status Code":response.status, "API":api  })
                content = await response.read()
                self.api_logger.debug({"URL": url,"Post Data": json.dumps(data), \
                                       "Response Status Code": response.status, \
                                        "Response": json.loads(content)})
                response.raise_for_status()
                response = await response.json()
                return response

        except aiohttp.ClientResponseError as e:
            self.api_logger.error({"Api": api, "Response": json.loads(content)})
            return await response.json()
                
        except TypeError as e:
            if "response" in locals():
                self.error_resp["code"] = response.status
            else:
                self.error_resp["code"] = -99
                self.error_resp["message"]=self.error_message
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": url,"Post Data": json.dumps(data),"message": self.error_resp})
            return self.error_resp 
                 
        except Exception as e:
            if "response" in locals():
                self.error_resp["code"] = response.status
            else:
                self.error_resp["code"] = -99
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": url,"Post Data": json.dumps(data),"message": e})
            return self.error_resp

    async def get_async_call(
        self, api: str, header: str, params=None, data_flag=False
    ) -> dict:
        """
        Makes an asynchronous GET request to the specified API.

        Args:
            api: The API endpoint to make the request to.
            header: The authorization header for the request.
            params: The query parameters to send with the request.
            data_flag: A flag indicating whether to use custom data URLs.

        Returns:
            The response JSON as a dictionary, or the response object if an error occurs.
        """
        try:
            if data_flag:
                URL = Config.DATA_API + api
            else:
                URL = Config.API + api
            # Create session on first use if not provided
            if self.session is None:
                self.session = aiohttp.ClientSession()
            
            headers = {
                "Authorization": header,
                "Content-Type": self.content,
                "version": "3",
            }
            async with self.session.get(URL, params=params, headers=headers) as response:
                self.request_logger.debug({"Status Code": response.status, "API":api })
                content = await response.read()
                self.api_logger.debug({"URL": URL, "Status Code": response.status, "Response": json.loads(content)})
                response.raise_for_status()
                response = await response.json()
                return response               

        except aiohttp.ClientResponseError as e:
            self.api_logger.error({"Api": api, "Response": json.loads(content)})
            return await response.json() 

        except TypeError as e:
            if "response" in locals():
                self.error_resp["code"] = response.status
            else:
                self.error_resp["code"] = -99
                self.error_resp["message"]= self.error_message
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": URL,"message": self.error_resp})
            return self.error_resp

        except Exception as e:
            if "response" in locals():
                self.error_resp["code"] = response.status
            else:
                self.error_resp["code"] = -99
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": URL,"message": e})
            return self.error_resp

    async def delete_async_call(self, api: str, header: str, data) -> dict:
        """
        Makes an asynchronous DELETE request to the specified API.

        Args:
            api: The API endpoint to make the request to.
            header: The authorization header for the request.
            data: The data to send in the request payload.

        Returns:
            The response JSON as a dictionary, or the response object if an error occurs.
        """
        try:
            url = Config.API + api
            # Create session on first use if not provided
            if self.session is None:
                self.session = aiohttp.ClientSession()
            
            headers = {"Authorization": header, "Content-Type": self.content, "version": "3"}
            async with self.session.delete(url, data=json.dumps(data), headers=headers) as response:
                self.request_logger.debug({"Status Code": response.status, "API":api })
                content = await response.read()
                self.api_logger.debug({"URL": url, "data": json.dumps(data), \
                                        "Response Status Code": response.status, \
                                        "Response": json.loads(content)})
                response.raise_for_status()
                response = await response.json()          
                return response

        except aiohttp.ClientResponseError as e:
            self.api_logger.error({"Api": api, "Response": json.loads(content)})
            return await response.json()

        except TypeError as e:
            if "response" in locals():
                self.error_resp["code"] = response.status
            else:
                self.error_resp["code"] = -99
                self.error_resp["message"]=self.error_message
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": url,"data": json.dumps(data),"message": self.error_resp})
            return self.error_resp 
                 
        except Exception as e:
            if "response" in locals():
                self.error_resp["code"] = response.status
            else:
                self.error_resp["code"] = -99
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": url,"data": json.dumps(data),"message": e})
            return self.error_resp

    async def patch_async_call(self, api: str, header: str, data) -> dict:
        """
        Makes an asynchronous PATCH request to the specified API.

        Args:
            api: The API endpoint to make the request to.
            header: The authorization header for the request.
            data: The data to send in the request payload.

        Returns:
            The response JSON as a dictionary, or the response object if an error occurs.
        """
        try:
            url = Config.API + api
            # Create session on first use if not provided
            if self.session is None:
                self.session = aiohttp.ClientSession()
            
            json_data = json.dumps(data).encode("utf-8")
            headers = {"Authorization": header, "Content-Type": self.content, "version": "3"}
            async with self.session.patch(url, data=json_data, headers=headers) as response:
                self.request_logger.debug({"Status Code": response.status, "API":api })
                content = await response.read()
                self.api_logger.debug({"URL": url, "data": json.dumps(data), \
                                      "Status Code": response.status, \
                                      "Response": json.loads(content)})
                response.raise_for_status()
                response = await response.json()           
                return response 
                
        except aiohttp.ClientResponseError as e:
            self.api_logger.error({"Api": api, "Response": json.loads(content)})
            return await response.json()
        
        except TypeError as e:
            if "response" in locals():
                self.error_resp["code"] = response.status
            else:
                self.error_resp["code"] = -99
                self.error_resp["message"]=self.error_message
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": url,"data": json.dumps(data),"message": self.error_resp})
            return self.error_resp 
                 
        except Exception as e:
            if "response" in locals():
                self.error_resp["code"] = response.status
            else:
                self.error_resp["code"] = -99
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": url,"data": json.dumps(data),"message": e})
            return self.error_resp

    async def put_async_call(self, api: str, header: str, data) -> dict:
        """
        Makes an asynchronous PUT request to the specified API.

        Args:
            api: The API endpoint to make the request to.
            header: The authorization header for the request.
            data: The data to send in the request payload.

        Returns:
            The response JSON as a dictionary, or the response object if an error occurs.
        """
        try:
            url = Config.API + api
            # Create session on first use if not provided
            if self.session is None:
                self.session = aiohttp.ClientSession()
            
            json_data = json.dumps(data).encode("utf-8")
            headers = {"Authorization": header, "Content-Type": self.content, "version": "3"}
            async with self.session.put(url, data=json_data, headers=headers) as response:
                self.request_logger.debug({"Status Code": response.status, "API":api })
                content = await response.read()
                self.api_logger.debug({"URL": url, "data": json.dumps(data), \
                                      "Status Code": response.status, \
                                      "Response": json.loads(content)})
                response.raise_for_status()
                response = await response.json()           
                return response 
                
        except aiohttp.ClientResponseError as e:
            self.api_logger.error({"Api": api, "Response": json.loads(content)})
            return await response.json()
        
        except TypeError as e:
            if "response" in locals():
                self.error_resp["code"] = response.status
            else:
                self.error_resp["code"] = -99
                self.error_resp["message"]=self.error_message
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": url,"data": json.dumps(data),"message": self.error_resp})
            return self.error_resp 
                 
        except Exception as e:
            if "response" in locals():
                self.error_resp["code"] = response.status
            else:
                self.error_resp["code"] = -99
            self.api_logger.error({"API": api, "error": e})
            self.api_logger.debug({"URL": url,"data": json.dumps(data),"message": e})
            return self.error_resp

    async def close(self):
        """
        Closes the aiohttp session if it was created by this instance.
        Should be called when done with the service to properly clean up resources.
        """
        if self.session is not None and self._session_created_here:
            await self.session.close()
            self.session = None



class SessionModel:
    def __init__(
        self,
        client_id=None,
        redirect_uri=None,
        response_type=None,
        scope=None,
        state=None,
        nonce=None,
        secret_key=None,
        grant_type=None,
    ):
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.response_type = response_type
        self.scope = scope
        self.state = state
        self.nonce = nonce
        self.secret_key = secret_key
        self.grant_type = grant_type

    def generate_authcode(self):
        data = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": self.response_type,
            "state": self.state,
        }
        if self.scope is not None:
            data["scope"] = self.scope
        if self.nonce is not None:
            data["nonce"] = self.nonce

        url_params = urllib.parse.urlencode(data)
        return f"{Config.API}{Config.auth}?{url_params}"

    def get_hash(self):
        hash_val = hashlib.sha256(f"{self.client_id}:{self.secret_key}".encode())
        return hash_val

    def set_token(self, token):
        self.auth_token = token

    def generate_token(self):
        data = {
            "grant_type": self.grant_type,
            "appIdHash": self.get_hash().hexdigest(),
            "code": self.auth_token,
        }
        response = requests.post(
            Config.API + Config.generate_access_token, headers="", json=data
        )
        return response.json()


class FyersModel:
    def __init__(
        self,
        is_async: bool = False,
        log_path=None,
        client_id: str = "",
        token: str = "",
        log_level: str = "ERROR"
    ):
        """
        Initializes an instance of FyersModelv3.

        Args:
            is_async: A boolean indicating whether API calls should be made asynchronously.
            client_id: The client ID for API authentication.
            token: The token for API authentication.
        """
        self.client_id = client_id
        self.token = token
        self.is_async = is_async
        self.log_path = log_path
        self.header = "{}:{}".format(self.client_id, self.token)
        self.log_level = log_level
        if log_path:
            self.log_path = log_path + "/"
        else:
            self.log_path = ""

        self.api_logger = FyersLogger(
            "FyersAPI",
            log_level,
            stack_level=2,
            logger_handler=logging.FileHandler(self.log_path + "fyersApi.log"),
        )

        self.request_logger = FyersLogger(
            "FyersAPIRequest",
            "DEBUG",
            stack_level=2,
            logger_handler=logging.FileHandler(self.log_path + "fyersRequests.log"),
        )
        if is_async:
            self.service = FyersServiceAsync(self.api_logger, self.request_logger)
        else:
            self.service = FyersServiceSync(self.api_logger, self.request_logger)

    def get_profile(self) -> dict:
        """
        Retrieves the user profile information.

        """
        if self.is_async:
            response = self.service.get_async_call(Config.get_profile, self.header)
            
        else:
            response = self.service.get_call(Config.get_profile, self.header)
        return response

    def tradebook(self) -> dict:
        """
        Retrieves daily trade details of the day.

        """
        if self.is_async:
            response = self.service.get_async_call(Config.tradebook, self.header)
            
        else:
            response = self.service.get_call(Config.tradebook, self.header)
        return response

    def funds(self) -> dict:
        """
        Retrieves funds details.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.funds, self.header)
            
        else:
            response = self.service.get_call(Config.funds, self.header)
        return response

    def positions(self) -> dict:
        """
        Retrieves information about current open positions.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.positions, self.header)
            
        else:
            response = self.service.get_call(Config.positions, self.header)
        return response

    def holdings(self) -> dict:
        """
        Retrieves information about current holdings.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.holdings, self.header)
            
        else:
            response = self.service.get_call(Config.holdings, self.header)
        return response

    def logout(self) -> dict:
        """
        Invalidates the access token.

        """
        if self.is_async:
            response = self.service.post_async_call(Config.logout, self.header)
            
        else:
            response = self.service.post_call(Config.logout, self.header)
        return response

    def get_orders(self, data) -> dict:
        """
        Retrieves order details by ID.

        Args:
            data: The data containing the order ID.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.orderbook, self.header)
            
        else:
            response = self.service.get_call(Config.orderbook, self.header)
        id_list = data['id'].split(",")
        response["orderBook"]= [order for order in response["orderBook"] if order["id"] in id_list]

        return response

    def orderbook(self, data = None) -> dict:
        """
        Retrieves the order information.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.orderbook, self.header, data)
            
        else:
            response = self.service.get_call(Config.orderbook, self.header, data)
        return response
    
    def gtt_orderbook(self, data = None) -> dict:
        """
        Retrieves the gtt order information.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.gtt_orders, self.header, data)
            
        else:
            response = self.service.get_call(Config.gtt_orders, self.header, data)
        return response
    
    def market_status(self) -> dict:
        """
        Retrieves market status.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(
                    Config.market_status, self.header, data_flag=True
                )
            
        else:
            response = self.service.get_call(
                Config.market_status, self.header, data_flag=True
            )
        return response

    def convert_position(self, data) -> dict:
        """
        Converts positions from one product type to another based on the provided details.

        Args:
            symbol (str): Symbol of the positions. Eg: "MCX:SILVERMIC20NOVFUT".
            positionSide (int): Side of the positions. 1 for open long positions, -1 for open short positions.
            convertQty (int): Quantity to be converted. Should be in multiples of lot size for derivatives.
            convertFrom (str): Existing product type of the positions. (CNC positions cannot be converted)
            convertTo (str): The new product type to convert the positions to.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.post_async_call(
                    Config.convert_position, self.header, data
                )
            
        else:
            response = self.service.post_call(
                Config.convert_position, self.header, data
            )
        return response

    def cancel_order(self, data) -> dict:
        """
        Cancel order.

        Args:
            id (str, optional): ID of the position to close. If not provided, all open positions will be closed.


        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.delete_async_call(Config.orders_endpoint, self.header, data)
            
        else:
            response = self.service.delete_call(Config.orders_endpoint, self.header, data)
        return response
    
    def cancel_gtt_order(self,data) -> dict:
        """
        Cancel order.

        Args:
            id (str): Unique identifier for the order to be cancelled, e.g., "25010700000001".

        Returns:
            The response JSON as a dictionary.
        """

        if self.is_async:
            response = self.service.delete_async_call(Config.gtt_orders_sync, self.header, data)
        else:
            response = self.service.delete_call(Config.gtt_orders_sync, self.header, data)
        return response

    def place_order(self, data) -> dict:
        """
        Places an order based on the provided data.

        Args:
        data (dict): A dictionary containing the order details.
            - 'productType' (str): Type of the product. Possible values: 'CNC', 'INTRADAY', 'MARGIN', 'MTF'.
            - 'side' (int): Side of the order. 1 for Buy, -1 for Sell.
            - 'symbol' (str): Symbol of the product. Eg: 'NSE:SBIN-EQ'.
            - 'qty' (int): Quantity of the product. Should be in multiples of lot size for derivatives.
            - 'disclosedQty' (int): Disclosed quantity. Allowed only for equity. Default: 0.
            - 'type' (int): Type of the order. 1 for Limit Order, 2 for Market Order,
                            3 for Stop Order (SL-M), 4 for Stoplimit Order (SL-L).
            - 'validity' (str): Validity of the order. Possible values: 'IOC' (Immediate or Cancel), 'DAY' (Valid till the end of the day).
            - 'filledQty' (int): Filled quantity. Default: 0.
            - 'limitPrice' (float): Valid price for Limit and Stoplimit orders. Default: 0.
            - 'stopPrice' (float): Valid price for Stop and Stoplimit orders. Default: 0.
            - 'offlineOrder' (bool): Specifies if the order is placed when the market is open (False) or as an AMO order (True).
            - 'isSliceOrder' (bool): Specifies if the order is a slice order. Default: False.
            - 'takeProfit' (float, optional): Profit target offset relative to entry. Omit if not used.
            - 'stopLoss' (float, optional): Stop loss offset relative to entry. Omit if not used.
            - 'legType' (int, optional): Offset type when TP/SL is used. 1 = Points (default), 2 = Percentage of entry price. Omit if not using TP/SL.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.post_async_call(Config.orders_endpoint, self.header, data)
        else:
            response = self.service.post_call(Config.orders_endpoint, self.header, data)
        return response
    
    def place_gtt_order(self,data) -> dict:
        """
        Places an order based on the provided data.

        Args:
        data (dict): A dictionary containing the order details.
            - 'id*' (str): Unique identifier for the order to be modified, e.g., "25010700000001".
            - 'side' (int): Indicates the side of the order: 1 for buy, -1 for sell.
            - 'symbol' (str): The instrument's unique identifier, e.g., "NSE:CHOLAFIN-EQ"
            - 'productType*' (str): The product type for the order. Valid values: "CNC", "MARGIN", "MTF".
            - 'orderInfo*' (object): Contains information about the GTT/OCO order legs.
            - 'orderInfo.leg1*' (object): Details for GTT order leg. Mandatory for all orders.
            - 'orderInfo.leg1.price*' (number): Price at which the order.
            - 'orderInfo.leg1.triggerPrice' (number): 	Trigger price for the GTT order. NOTE: for OCO order this leg trigger price should be always above LTP
            - 'orderInfo.leg1.qty*' (int): Quantity for the GTT order leg.
            - 'orderInfo.leg2*' (object): Details for OCO order leg. Optional and included only for OCO orders.
            - 'orderInfo.leg2.price*' (number): Price at which the second leg of the OCO order should be placed.
            - 'orderInfo.leg2.triggerPrice*' (number): Trigger price for the second leg of the OCO order.NOTE: for OCO order this leg trigger price should be always below LTP
            - 'orderInfo.leg2.qty*' (integer): Quantity for the second leg of the OCO order.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.post_async_call(Config.gtt_orders_sync, self.header, data)
        else:
            response = self.service.post_call(Config.gtt_orders_sync, self.header, data)
        return response

    def modify_order(self, data) -> dict:
        """
        Modifies the parameters of a pending order based on the provided details.

        Parameters:
            id (str): ID of the pending order to be modified.
            limitPrice (float, optional): New limit price for the order. Mandatory for Limit/Stoplimit orders.
            stopPrice (float, optional): New stop price for the order. Mandatory for Stop/Stoplimit orders.
            qty (int, optional): New quantity for the order.
            type (int, optional): New order type for the order.
            takeProfit (float | None, optional): Omit to keep existing. Value > 0 updates/creates TP; 0 or null removes TP.
            stopLoss (float | None, optional): Omit to keep existing. Value > 0 updates/creates SL; 0 or null removes SL.
            legType (int, optional): Only relevant when setting TP/SL. Read-only once legs exist.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.patch_async_call(Config.orders_endpoint, self.header, data)
            
        else:
            response = self.service.patch_call(Config.orders_endpoint, self.header, data)
        return response
    
    def modify_gtt_order(self,data) -> dict:
        """
        Modifies the parameters of a pending order based on the provided details.

        Parameters:
            id (str): 	Unique identifier for the order to be modified, e.g., "25010700000001"
            orderInfo* (object): Contains updated information about the GTT/OCO order legs.
            orderInfo.leg1* (object): Details for GTT order leg. Mandatory for all modifications.
            orderInfo.leg1.price* (number): Updated price at which the order should be placed.
            orderInfo.leg1.triggerPrice* (number): Updated trigger price for the GTT order. NOTE: for OCO order this leg trigger price should be always above LTP.
            orderInfo.leg1.qty** (integer): Updated quantity for the GTT order leg.
            orderInfo.leg2* (object): Details for OCO order leg. Required if the order is an OCO type.
            orderInfo.leg2.triggerPrice* (number): Updated trigger price for the second leg of the OCO order.NOTE: for OCO order this leg trigger price should be always below LTP.
            orderInfo.leg2.qty* (integer): Updated quantity for the second leg of the OCO order.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.patch_async_call(Config.gtt_orders_sync, self.header, data)
        else:
            response = self.service.patch_call(Config.gtt_orders_sync, self.header, data)
        return response

    def exit_positions(self, data={}) -> dict:
        """
        Closes open positions based on the provided ID or closes all open positions if ID is not passed.

        Args:
            id (str, optional): ID of the position to close. If not provided, all open positions will be closed.


        Returns:
            The response JSON as a dictionary.
        """
        if len(data) == 0 :
            data = {"exit_all": 1}

        if self.is_async:
            response = self.service.delete_async_call(Config.positions, self.header, data)
            
        else:
            response = self.service.delete_call(Config.positions, self.header, data)
        return response

    def attach_position_legs(self, data) -> dict:
        """
        Attach or update TP/SL legs on an existing open position (PATCH /positions).

        Args:
        data (dict): A dictionary containing the attachment details.
            - 'positionId' (str): Position identifier. Eg: 'NSE:SBIN-EQ-INTRADAY'. Required.
            - 'takeProfit' (float | None, optional): Target offset, or null/0 to delete. Omit if unchanged.
            - 'stopLoss' (float | None, optional): Stop loss offset, or null/0 to delete. Omit if unchanged.
            - 'legType' (int, optional): 1 = Points (default), 2 = Percentage. Only needed when setting TP/SL.
            - 'qty' (int, optional): Quantity to protect. Defaults to the position's net quantity.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.patch_async_call(Config.positions, self.header, data)
        else:
            response = self.service.patch_call(Config.positions, self.header, data)
        return response
    
    
    def place_multileg_order(self, data) -> dict:
        """
        Places an multileg order based on the provided data.

        Args:
        data (dict): A dictionary containing the order details.
            - 'productType' (str): Type of the product. Possible values: 'INTRADAY', 'MARGIN'.
            - 'offlineOrder' (bool): Specifies if the order is placed when the market is open (False) or as an AMO order (True).
            - 'orderType' (str): Type of multileg. Possible values: '3L' for 3 legs and '2L' for 2 legs .
            - 'validity' (str): Validity of the order. Possible values: 'IOC' (Immediate or Cancel).
            legs (dict): A dictionary containing multiple legs order details.
                - 'symbol' (str): Symbol of the product. Eg: 'NSE:SBIN-EQ'.
                - 'qty' (int): Quantity of the product. Should be in multiples of lot size for derivatives.
                - 'side' (int): Side of the order. 1 for Buy, -1 for Sell.
                - 'type' (int): Type of the order. Possible values: 1 for Limit Order.
                - 'limitPrice' (float): Valid price for Limit and Stoplimit orders.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.post_async_call(Config.multileg_orders, self.header, data)
        else:
            response = self.service.post_call(Config.multileg_orders, self.header, data)
        return response

    def generate_data_token(self, data):
        allPackages = subprocess.check_output([sys.executable, "-m", "pip", "freeze"])
        installed_packages = [r.decode().split("==")[0] for r in allPackages.split()]
        if Config.data_vendor_td not in installed_packages:
            print("Please install truedata package | pip install truedata-ws")
        response = self.service.post_call(Config.generate_data_token, self.header, data)
        return response

    def cancel_basket_orders(self, data):
        """
        Cancels the orders with the provided IDs.

        Parameters:
            order_ids (list): A list of order IDs to be cancelled.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.delete_async_call(
                    Config.multi_orders, self.header, data
                )
            
        else:
            response = self.service.delete_call(
                Config.multi_orders, self.header, data
            )
        return response

    def place_basket_orders(self, data):
        """
        Places multiple orders based on the provided details.

        Parameters:
        orders (list): A list of dictionaries containing the order details.
            Each dictionary should have the following keys:
            - 'symbol' (str): Symbol of the product. Eg: 'MCX:SILVERM20NOVFUT'.
            - 'qty' (int): Quantity of the product.
            - 'type' (int): Type of the order. 1 for Limit Order, 2 for Market Order, and so on.
            - 'side' (int): Side of the order. 1 for Buy, -1 for Sell.
            - 'productType' (str): Type of the product. Eg: 'INTRADAY', 'CNC', 'MARGIN', 'MTF'.
            - 'limitPrice' (float): Valid price for Limit and Stoplimit orders.
            - 'stopPrice' (float): Valid price for Stop and Stoplimit orders.
            - 'disclosedQty' (int): Disclosed quantity. Allowed only for equity.
            - 'validity' (str): Validity of the order. Eg: 'DAY', 'IOC', etc.
            - 'offlineOrder' (bool): Specifies if the order is placed when the market is open (False) or as an AMO order (True).
            - 'takeProfit' (float, optional): Profit target offset. Omit if not using TP/SL.
            - 'stopLoss' (float, optional): Stop loss offset. Omit if not using TP/SL.
            - 'legType' (int, optional): Offset type when TP/SL is used. 1 = Points (default), 2 = Percentage.


        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.post_async_call(Config.multi_orders, self.header, data)
            
        else:
            response = self.service.post_call(
                Config.multi_orders, self.header, data
            )
        return response

    def modify_basket_orders(self, data):
        """
        Modifies multiple pending orders based on the provided details.

        Parameters:
        orders (list): A list of dictionaries containing the order details to be modified.
            Each dictionary should have the following keys:
            - 'id' (str): ID of the pending order to be modified.
            - 'limitPrice' (float): New limit price for the order. Mandatory for Limit/Stoplimit orders.
            - 'stopPrice' (float): New stop price for the order. Mandatory for Stop/Stoplimit orders.
            - 'qty' (int): New quantity for the order.
            - 'type' (int): New order type for the order.
            - 'takeProfit' (float | None, optional): Omit to keep. Value > 0 updates/creates; 0 or null removes.
            - 'stopLoss' (float | None, optional): Omit to keep. Value > 0 updates/creates; 0 or null removes.
            - 'legType' (int, optional): Only relevant when setting TP/SL. Read-only once legs exist.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.patch_async_call(
                    Config.multi_orders, self.header, data
                )
            
        else:
            response = self.service.patch_call(
                Config.multi_orders, self.header, data
            )
        return response

    def history(self, data=None):
        """
        Fetches candle data based on the provided parameters.

        Parameters:
        symbol (str): Symbol of the product. Eg: 'NSE:SBIN-EQ'.
        resolution (str): The candle resolution. Possible values are:
            'Day' or '1D', '1', '2', '3', '5', '10', '15', '20', '30', '60', '120', '240'.
        date_format (int): Date format flag. 0 to enter the epoch value, 1 to enter the date format as 'yyyy-mm-dd'.
        range_from (str): Start date of the records. Accepts epoch value if date_format flag is set to 0,
            or 'yyyy-mm-dd' format if date_format flag is set to 1.
        range_to (str): End date of the records. Accepts epoch value if date_format flag is set to 0,
            or 'yyyy-mm-dd' format if date_format flag is set to 1.
        cont_flag (int): Flag indicating continuous data and future options. Set to 1 for continuous data.


        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(
                    Config.history, self.header, data, data_flag=True
                )
            
        else:
            response = self.service.get_call(
                Config.history, self.header, data, data_flag=True
            )
        return response

    def quotes(self, data=None):
        """
        Fetches quotes data for multiple symbols.

        Parameters:
            symbols (str): Comma-separated symbols of the products. Maximum symbol limit is 50. Eg: 'NSE:SBIN-EQ,NSE:HDFC-EQ'.


        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            
            response =   self.service.get_async_call(
                    Config.quotes, self.header, data, data_flag=True
                )
            
        else:
            response = self.service.get_call(
                Config.quotes, self.header, data, data_flag=True
            )
        return response

    def depth(self, data=None):
        """
        Fetches market depth data for a symbol.

        Parameters:
            symbol (str): Symbol of the product. Eg: 'NSE:SBIN-EQ'.
            ohlcv_flag (int): Flag to indicate whether to retrieve open, high, low, closing, and volume quantity. Set to 1 for yes.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
                response = self.service.get_async_call(
                    Config.market_depth, self.header, data, data_flag=True
                )
            
        else:
            response = self.service.get_call(
                Config.market_depth, self.header, data, data_flag=True
            )
        return response


    def optionchain(self, data=None):
        """
        Fetches option chain data for a given symbol.

        Parameters:
            symbol (str): The symbol of the product. For example, 'NSE:NIFTY50-INDEX'.
            timestamp (int): Expiry timestamp of the stock. Use empty for current expiry. Example: 1813831200.
            strikecount (int): Number of strike price data points desired. 
                For instance, setting it to 7 provides: 1 INDEX + 7 ITM + 1 ATM + 7 OTM = 1 INDEX and 15 STRIKE (15 CE + 15 PE).
            greeks (string): Set greeks to 1 for greeks data which includes delta, gamma, theta, vega and iv.
    

        Returns:
            dict: The response JSON containing the option chain data.
        """
        if self.is_async:
                response = self.service.get_async_call(
                    Config.option_chain, self.header, data, data_flag=True
                )
            
        else:
            response = self.service.get_call(
                Config.option_chain, self.header, data, data_flag=True
            )
        return response
    
    def create_alert(self, data) -> dict:
        """
        Creates a new price alert for a user.

        Args:
            data (dict): A dictionary containing the alert details.
                Required:
                    - alert-type (int): Type of alert. 1 usually means price-based alert.
                    - name (str): User-provided name/label for the alert.
                    - symbol (str): Trading symbol in full format.
                        Eg: "NSE:SBIN-EQ", "NSE:SILVERMIC25DECFUT"
                    - comparisonType (str): Price parameter used for comparison.
                        Allowed: "OPEN", "HIGH", "LOW", "CLOSE", "LTP"
                    - condition (str): Price comparison operator.
                        Allowed: "GT" (greater), "LT" (lesser), "EQ" (equal)
                    - value (float/int/str): Target price against which comparison is performed.
                Optional:
                    - agent (str): Source of alert creation. Eg: "fyers-api"
                    - notes (str): Additional notes for the alert.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.post_async_call(Config.price_alert, self.header, data)
        else:
            response = self.service.post_call(Config.price_alert, self.header, data)
        return response
       
    def get_alert(self, data=None) -> dict:
        """
        Retrieves alert details. If data with 'id' is provided, filters alerts by ID(s).
        Otherwise, returns all alerts. Supports fetching archived alerts via 'archive' parameter.

        Args:
            data (dict, optional): Optional dictionary containing query parameters.
                - 'archive' (int, optional): Set to 1 to retrieve archived alerts instead of active alerts.
                    Default: 0 (active alerts)

        Returns:
            The response JSON as a dictionary :
        """
        if data is None:
            data = {}
        
        if self.is_async:
            response = self.service.get_async_call(Config.price_alert, self.header, data)
        else:
            response = self.service.get_call(Config.price_alert, self.header, data)
        return response

    def delete_alert(self, data) -> dict:
        """
        Deletes a price alert.

        Args:
            data (dict): A dictionary containing the alert deletion details.
                Required Attributes:
                    - alertId (str): Alert ID from creation
                Optional Attributes:
                    - agent (str): Client calling the API (e.g., "fyers-api")

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.delete_async_call(Config.price_alert, self.header, data)
        else:
            response = self.service.delete_call(Config.price_alert, self.header, data)
        return response     

    def update_alert(self, data) -> dict:
        """
        Modifies the parameters of an existing alert based on the provided details.

        Args:
            data (dict): A dictionary containing the alert modification details.
                Required Attributes:
                    - alertId (str): ID of the alert to be modified. Eg: "3870991"
                    - alert-type (int): Type of alert. 1 usually means price-based alert.
                    - symbol (str): Trading symbol in full format.
                        Eg: "NSE:SBIN-EQ", "NSE:SILVERMIC25DECFUT"
                    - comparisonType (str): Price parameter used for comparison.
                        Allowed: "OPEN", "HIGH", "LOW", "CLOSE", "LTP"
                    - condition (str): Price comparison operator.
                        Allowed: "GT" (greater), "LT" (lesser), "E" (equal)
                    - value (float/int/str): Target price against which comparison is performed.
                    - name (str): User-provided name/label for the alert.
                Optional Attributes:
                    - agent (str): Source of alert creation. Eg: "fyers-api"
                    

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.put_async_call(Config.price_alert, self.header, data)
        else:
            response = self.service.put_call(Config.price_alert, self.header, data)
        return response

    def toggle_alert(self, data) -> dict:
        """
        Toggles the status of an existing alert between enabled (1) and disabled (2).
        If the alert is currently disabled, it will be enabled. If enabled, it will be disabled.

        Args:
            data (dict): A dictionary containing the alert toggle details.
                - 'alertId' (str, mandatory): ID of the alert to be toggled. Eg: "3870991"

        Returns:
            The response JSON as a dictionary with success message indicating the alert status has been modified.
        """
        if self.is_async:
            response = self.service.put_async_call(Config.toggle_alert, self.header, data)
        else:
            response = self.service.put_call(Config.toggle_alert, self.header, data)
        return response
    
    def create_smart_order_step(self, data: dict) -> dict:
        """
        Creates a step smart order based on the provided data.

        Args:
            data (dict): A dictionary containing the smart order creation details.
               Required Attributes:
                - symbol (str): Symbol of the product. Eg: "NSE:SBIN-EQ"
                - side (int): Side of the order. 1 for Buy, -1 for Sell
                - qty (int): Total quantity of the product
                - productType (str): Type of the product. Possible values: 'CNC', 'INTRADAY', 'MARGIN'
                - avgqty (int): Average quantity per step
                - avgdiff (int): Average difference between steps
                - direction (int): Direction of the order
                - orderType (int): Type of the order
                - startTime (int): Start time in epoch format
                - endTime (int): End time in epoch format
                
               Conditional Attributes:  
                - limitPrice (float): Limit price for the order
                
               Optional Attributes:   
                - initQty (int): Initial quantity to be placed
                - hpr (float): Higher price range
                - lpr (float): Lower price range
                - mpp (int): Maximum price per order

        Returns:
            dict: The response JSON as a dictionary.
        """

       
        
        if self.is_async:
            response = self.service.post_async_call(Config.create_smartorder_step, self.header, data)
        else:
            response = self.service.post_call(Config.create_smartorder_step, self.header, data) 
        return response
    
    async def close(self):
        """
        Closes the HTTP session(s) to properly clean up resources.
        Should be called when done with the FyersModel instance, especially for async mode.
        """
        if self.is_async:
            if hasattr(self, 'async_session') and self.async_session:
                await self.async_session.close()
                self.async_session = None
            if hasattr(self, 'service') and hasattr(self.service, 'close'):
                await self.service.close()
        else:
            if hasattr(self, 'session') and self.session:
                self.session.close()
                self.session = None
    

    def create_smart_order_limit(self,data: dict) -> dict:
        """
        Creates a Smart Limit Order based on the provided data.
        
        Smart Limit Orders allow you to place limit orders that remain active until the specified end time.
        Once the end time is reached, the order can be converted to an MPP order or cancelled.

        Args:
            data (dict): A dictionary containing the smart order creation details.
                Required Attributes:
                    - symbol (str): The instrument's unique identifier, e.g., "NSE:SBIN-EQ"
                    - side (int): Order side: 1 for Buy, -1 for Sell (enum: 1, -1)
                    - qty (int): Order quantity (Min: 1, Max: 999999; must be a multiple of lot size)
                    - productType (str): Must be one of: "CNC", "MARGIN", "INTRADAY", "MTF"
                    - limitPrice (number): The price at which the order should be placed (Min: 0.01)
                    - endTime (int): Order expiry time as a Unix timestamp (epoch)
                    - orderType (int): Order type: 1 for Limit, 4 for Stop-Limit (enum: 1, 4)
                    - onExp (int): Action on expiry: 1 = Cancel, 2 = Market (enum: 1, 2)
                
                Optional Attributes:
                    - stopPrice (number): Default: 0. Required when orderType is 4 (Stop-Limit)
                    - hpr (number): Default: 0. 0 = no upper price limit. If provided, order executes only below this price
                    - lpr (number): Default: 0. 0 = no lower price limit. If provided, order executes only above this price
                    - mpp (number): Default: 0. 0 = no market protection. Valid values: 0–3 or -1 (disabled)

        Returns:
            dict: The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.post_async_call(Config.create_smartorder_limit, self.header, data)
        else:
            response = self.service.post_call(Config.create_smartorder_limit, self.header, data) 
        return response
    
    def create_smart_order_trail(self, data: dict) -> dict:
        """
        Creates a Smart Trail Order (Trailing Stop Loss) based on the provided data.
        
        A Smart Trail Order is a trailing stop-loss that automatically adjusts the stop price as the market moves 
        in your favour. The stop price trails the market by a specified jump price.

        Args:
            data (dict): A dictionary containing the smart order creation details.
                Required Attributes:
                    - symbol (str): The instrument's unique identifier, e.g., "NSE:SBIN-EQ"
                    - side (int): Order side: 1 for Buy, -1 for Sell (enum: 1, -1)
                    - qty (int): Order quantity (Min: 1, Max: 999999; must be a multiple of lot size)
                    - productType (str): Must be one of: "CNC", "MARGIN", "INTRADAY", "MTF"
                    - orderType (int): Order type: 1 for Limit Order, 2 for Market Order (enum: 1, 2)
                    - stopPrice (number): Initial stop/trigger price (must be greater than 0)
                    - jump_diff (number): Jump price — the value by which the stop price trails (Min: 0.2)
                
                Optional Attributes:
                    - limitPrice (number): Default: 0. If not provided, executes at market price. Required if orderType = 1
                    - target_price (number): Default: 0 (no target). If provided, must be greater than current LTP
                    - mpp (number): Default: 0 (no market protection). Valid values: 0–3 or -1 (disabled)

        Returns:
            dict: The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.post_async_call(Config.create_smartorder_trail, self.header, data)
        else:
            response = self.service.post_call(Config.create_smartorder_trail, self.header, data) 
        return response
    
    def create_smart_order_sip(self, data: dict) -> dict:
        """
        Creates a Smart SIP (Systematic Investment Plan) order based on the provided data.
        
        Smart SIP allows you to automate recurring investments in equity stocks, ETFs, with orders placed automatically 
        at your selected frequency—daily, weekly, monthly, or on custom dates.

        Args:
            data (dict): A dictionary containing the smart order creation details.
                Required Attributes:
                    - symbol (str): The instrument's unique identifier (Equity only), e.g., "NSE:SBIN-EQ"
                    - productType (str): Must be one of: "CNC", "MTF"
                    - freq (int): SIP frequency (enum: 1, 2, 3, 6)
                    - sip_day (int): Day of the month for SIP execution (Min: 1, Max: 28)
                    - qty OR amount (int/number): At least one required - Quantity or amount per SIP instalment (Max: 999999)
                
                Conditional Attributes:
                    - sip_time (int): Required if freq = 1 (Daily). Unix timestamp for SIP execution time (must be within market hours)
                
                Optional Attributes:
                    - imd_start (bool): Whether to start SIP immediately. true = start now, false = wait for schedule
                    - endTime (int): Default: 0 (no end date). Unix timestamp when the SIP should end
                    - hpr (number): Default: 0. Skips SIP if price is above this upper limit
                    - lpr (number): Default: 0. Skips SIP if price is below this lower limit
                    - step_up_freq (int): Frequency of step-up increase (enum: 3, 5). Default: 0 (no step-up)
                    - step_up_qty (int): Quantity to increase at each step-up (Default: 0; Max: 999999)
                    - step_up_amount (number): Amount to increase at each step-up (Default: 0; Max: 999999)
                    - exp_qty (int): Quantity for expiry/final SIP order (Default: 0; Max: 999999)

        Returns:
            dict: The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.post_async_call(Config.create_smartorder_sip, self.header, data)
        else:
            response = self.service.post_call(Config.create_smartorder_sip, self.header, data) 
        return response
    
    
        
    
    def modify_smart_order(self, data) -> dict:
        """
        Modifies a smart order based on the provided data.

        Args:
            data (dict): A dictionary containing the smart order modification details.

                Required:
                    - flowId (str): Unique identifier of the Smart Order to be modified

                Optional (by order type/flowtype):

                    Limit Order (flowtype: 4):
                        - qty (int): To update order quantity
                        - limitPrice (number): To update limit price
                        - stopPrice (number): To update stop/trigger price
                        - endTime (int): To update expiry time (Unix timestamp)
                        - hpr (number): To update upper price limit (High Price Range)
                        - lpr (number): To update lower price limit (Low Price Range)
                        - mpp (number): To update market protection percentage
                        - onExp (int): To update expiry action (1 = Cancel, 2 = Market Order)

                    Trail Order (flowtype: 6):
                        - qty (int): To update order quantity
                        - limitPrice (number): To update limit price (required if orderType = 1; must be 0 if orderType = 2)
                        - stopPrice (number): To update stop/trigger price
                        - jump_diff (number): To update jump value for trailing stop
                        - target_price (number): To update target price (optional profit booking)
                        - mpp (number): To update market protection percentage

                    Step Order (flowtype: 3):
                        - qty (int): To update total order quantity
                        - startTime (int): To update order start time
                        - endTime (int): To update order end time
                        - hpr (number): To update upper price limit (High Price Range)
                        - lpr (number): To update lower price limit (Low Price Range)
                        - mpp (number): To update market protection percentage
                        - avgqty (int): To update quantity per averaging step
                        - avgdiff (number): To update price gap between steps
                        - initQty (int): To update initial quantity (only before order starts)
                        - limitPrice (number): To update limit price (only before order starts)
                        - direction (int): To update direction for averaging (1 = price drop, -1 = price rise)

                    SIP Order (flowtype: 7):
                        - qty (int): To update investment quantity per instalment
                        - amount (number): To update investment amount per instalment
                        - hpr (number): To update upper price limit (skip if price is above this)
                        - lpr (number): To update lower price limit (skip if price is below this)
                        - sip_day (int): To update SIP day (applicable for monthly/custom frequency)
                        - sip_time (int): To update SIP time (required for daily/custom frequency)
                        - step_up_amount (number): To update step-up amount (amount-based SIP only)
                        - step_up_qty (int): To update step-up quantity (qty-based SIP only)
                        - exp_qty (int): To update expiry quantity
                        - exp_amount (number): To update expiry amount

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.patch_async_call(Config.modify_smartorder, self.header, data)
        else:
            response = self.service.patch_call(Config.modify_smartorder, self.header, data)
        return response

    def cancel_smart_order(self, data) -> dict:
        """
        Cancels a smart order based on the provided data.

        Args:
            data (dict): A dictionary containing the smart order cancellation details.
                Required:
                    - flowId (str): Unique identifier of the smart order flow to cancel

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.delete_async_call(Config.cancel_smartorder, self.header, data)
        else:
            response = self.service.delete_call(Config.cancel_smartorder, self.header, data)
        return response

    def pause_smart_order(self, data) -> dict:
        """
        Pauses a smart order based on the provided data.

        Args:
            data (dict): A dictionary containing the smart order pause details.
                Required:
                    - flowId (str): Unique identifier of the smart order flow to pause

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.patch_async_call(Config.pause_smartorder, self.header, data)
        else:
            response = self.service.patch_call(Config.pause_smartorder, self.header, data)
        return response

    def resume_smart_order(self, data) -> dict:
        """
        Resumes a paused smart order based on the provided data.

        Args:
            data (dict): A dictionary containing the smart order resume details.
                Required:
                    - flowId (str): Unique identifier of the smart order flow to resume

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.patch_async_call(Config.resume_smartorder, self.header, data)
        else:
            response = self.service.patch_call(Config.resume_smartorder, self.header, data)
        return response

    def smart_orderbook_with_filter(self, data=None) -> dict:
        """
        Retrieves smart order book information with optional filters.

        Optional Query Parameters (pass as keys in data dict for GET query params):
            - flowtype (int[]): Filter by order type (repeatable). 3 = Step, 4 = Limit, 5 = Peg, 6 = Trail, 7 = SIP. Default: all types
            - messageType (int[]): Filter by order status/message type (repeatable). Default: all
            - page_no (int): Page number for pagination. Default: 1
            - page_size (int): Number of records per page. Default: 15
            - sort_by (str): Sort by field: "CreatedTime", "UpdatedTime", "Alphabet". Default: "UpdatedTime"
            - ord_by (int): Sort order: 1 for ascending, -1 for descending. Default: -1
            - side (int[]): Filter by side (repeatable). 1 for buy, -1 for sell. Default: all
            - exchange (str[]): Filter by exchange (repeatable). "NSE", "BSE", "MCX". Default: all
            - product (str[]): Filter by product type (repeatable). "CNC", "MARGIN", "INTRADAY", "MTF". Default: all
            - search (str): Search by symbol name. Default: none

        Args:
            data (dict, optional): A dictionary containing the optional query parameters above.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.smartorder_orderbook, self.header, data)
        else:
            response = self.service.get_call(Config.smartorder_orderbook, self.header, data)
        return response


    def create_smartexit_trigger(self, data) -> dict:
        """
        Creates a new smart exit trigger based on the provided data.
        
        Smart exit triggers support three types of strategies:
        
        Type 1: Only Alert (notification only, no auto-exit)
            - Sends notification when profit/loss thresholds are reached
            - Does not automatically exit positions
            - Example:
                {
                    "name": "Alert Only Strategy",
                    "type": 1,
                    "profitRate": 5000,
                    "lossRate": -2000
                }
        
        Type 2: Exit with Alert (notification + immediate exit)
            - Sends notification and immediately exits positions when thresholds are reached
            - Example:
                {
                    "name": "Auto Exit Strategy",
                    "type": 2,
                    "profitRate": 5000,
                    "lossRate": -2000
                }
        
        Type 3: Exit with Alert + Wait for Recovery (notification + delayed exit)
            - Sends notification and waits for recovery before exiting
            - Requires waitTime parameter (in minutes)
            - Example:
                {
                    "name": "Recovery Exit Strategy",
                    "type": 3,
                    "profitRate": 10000,
                    "lossRate": -3000,
                    "waitTime": 5
                }

        Args:
            data (dict): A dictionary containing the smart exit trigger creation details.
                - name (str): Name of the smart exit trigger strategy
                - type (int): Type of the trigger (1: Alert only, 2: Exit with alert, 3: Exit with alert + wait for recovery)
                - profitRate (float): Profit rate threshold (positive value, e.g., 5000)
                - lossRate (float): Loss rate threshold (negative value, e.g., -2000)
                - waitTime (int, optional): Wait time in minutes (required for type 3, default: 0)

        """
        if self.is_async:
            response = self.service.post_async_call(Config.smartexit_trigger, self.header, data)
        else:
            response = self.service.post_call(Config.smartexit_trigger, self.header, data)
        return response

    def get_smartexit_triggers(self, data=None) -> dict:
        """
        Retrieves smart exit trigger information.

        Args:
            data (dict, optional): A dictionary containing parameters for filtering smart exit triggers.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.smartexit_trigger, self.header, data)
        else:
            response = self.service.get_call(Config.smartexit_trigger, self.header, data)
        return response

    def update_smartexit_trigger(self, data) -> dict:
        """
        Updates an existing smart exit trigger based on the provided data.
        
        Use this endpoint to modify a Smart Exit trigger. You can update the target values, exit type, or wait time.
        If the trigger is active, updates are validated against the current P&L.
        Either a profit target or a loss limit must be provided.
        
        Exit Types (type field):
            - Value 1: Only Alert - Notification Only
                Sends a notification when target is hit. Does NOT exit positions automatically.
            - Value 2: Exit with Alert - Notification + Immediate Exit
                Sends notification AND exits all intraday positions immediately.
            - Value 3: Exit with Alert (Wait for Recovery) - Notification + Delayed Exit
                Sends notification, waits for waitTime minutes, then exits positions.

        Args:
            data (dict): A dictionary containing the smart exit trigger update details.
                Required Attributes:
                    - flowId (str): The unique identifier of the smart exit to update
                
                Optional Attributes:
                    - name (str): Unique name for your Smart Exit trigger
                    - profitRate (number): Book profit value (positive) or Minimize loss value (negative). 
                                         (Min: -1,00,00,000, Max: 1,00,00,000)
                    - lossRate (number): Max loss value (negative) or Min profit value (positive). 
                                       (Min: -1,00,00,000, Max: 1,00,00,000)
                    - type (int): Exit type (enum: 1, 2, 3). Default is 1 if not provided.
                    - waitTime (int): Wait time in minutes (required if type=3). Default: 0 (Min: 0, Max: 60)
                
                Note: Either profitRate or lossRate must be provided.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.put_async_call(Config.smartexit_trigger, self.header, data)
        else:
            response = self.service.put_call(Config.smartexit_trigger, self.header, data)
        return response

    def activate_deactivate_smartexit_trigger(self, data) -> dict:
        """
        Activates a smart exit trigger based on the provided data.

        Args:
            data (dict): A dictionary containing the smart exit trigger activation details.
                - flowId (str): Unique identifier of the smart exit trigger flow to activate

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.post_async_call(Config.activate_smartexit_trigger, self.header, data)
        else:
            response = self.service.post_call(Config.activate_smartexit_trigger, self.header, data)
        return response
    
    def orderhistory(self, data) -> dict:
        """
        Retrieves order history based on the provided data.
        Args:
        data (dict): A dictionary containing the order history details.
            - 'symbol' (str): Symbol of the product. Eg: 'NSE:SBIN-EQ'.
            - 'from_date' (str): Start date of the records in YYYY-MM-DD format.
            - 'to_date' (str): End date of the records in YYYY-MM-DD format.
            - 'page_no' (int): Page number for pagination. Default: 1
            - 'page_size' (int): Number of records per page. Default: 100
            - 'segment_type' (str): 0 => Includes all segments, 1 => Includes only Equity, 2 => Includes only Equity Derivatives, 3 => Includes Currency Derivatives, 4 => Includes only Commodity Derivatives
            - 'exchange_type' (str): 0 => Includes all exchanges, 1 => Includes only NSE, 2 => Includes only BSE, 3 => Includes only MCX
            - 'status' (str): 0 => All Status, 1 => Executed, 2 => Cancelled, 3 => Rejected

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.orderhistory, self.header, data)
        else:
            response = self.service.get_call(Config.orderhistory, self.header, data)
        return response
    
    def tradehistory(self, data) -> dict:
        """
        Retrieves trade history based on the provided data.

        Args:
        data (dict): A dictionary containing the trade history details.
            - 'symbol' (str): Symbol of the product. Eg: 'NSE:SBIN-EQ'.
            - 'from_date' (str): Start date of the records in YYYY-MM-DD format.
            - 'to_date' (str): End date of the records in YYYY-MM-DD format.
            - 'page_no' (int): Page number for pagination. Default: 1
            - 'page_size' (int): Number of records per page. Default: 100
            - 'segment_type' (str): 0 => Includes all segments, 1 => Includes only Equity, 2 => Includes only Equity Derivatives, 3 => Includes Currency Derivatives, 4 => Includes only Commodity Derivatives
            - 'exchange_type' (str): 0 => Includes all exchanges, 1 => Includes only NSE, 2 => Includes only BSE, 3 => Includes only MCX

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.tradeHistory, self.header, data)
        else:
            response = self.service.get_call(Config.tradeHistory, self.header, data)
        return response

    def charges_history(self, data) -> dict:
        """
        Retrieves charges history based on the provided data.

        Args:
            data (dict): A dictionary containing the charges history details.
            page_size (int):	The number of records to be fetched in one page (default is 100)
            page_no (int):	The page number to fetch (default is 1)
            from_date (str):	The start date for fetching orders in “YYYY-MM-DD” format (default is the start of the current financial year)
            to_date (str):	The end date for fetching orders in “YYYY-MM-DD” format (default is the current date)
            segment_type (str):	
            0 → Includes all segments
            1 → Includes only Equity
            2 → Includes only Equity Derivatives
            3 → Includes Mutal Funds
            4 → Includes only Currency Derivatives
            5 → Includes only Commodity Derivatives
            exchange_type (str):	
            0 → Includes all exchanges
            1 → Includes only NSE
            2 → Includes only BSE
            3 → Includes only MCX
            report_type (str):	
            1 → Includes only date wise
            2 → Includes summarized data (segment wise)

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.charges_history, self.header, data)
        else:
            response = self.service.get_call(Config.charges_history, self.header, data)
        return response
    
    def realised_profit_history(self, data) -> dict:
        """
        Retrieves realised profit history based on the provided data.

        Args:
            data (dict): A dictionary containing the realised profit history details.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.realised_profit_history, self.header, data)
        else:
            response = self.service.get_call(Config.realised_profit_history, self.header, data)
        return response
    
    def tax_pnl_history(self, data) -> dict:
        """
        Retrieves tax pnl history based on the provided data.

        Args:
            data (dict): A dictionary containing the tax pnl history details.
        
        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.tax_pnl_history, self.header, data)
        else:
            response = self.service.get_call(Config.tax_pnl_history, self.header, data)
        return response
    
    def ledger_history(self, data) -> dict:
        """
        Retrieves ledger history based on the provided data.

        Args:
            data (dict): A dictionary containing the ledger history details.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.ledger_history, self.header, data)
        else:
            response = self.service.get_call(Config.ledger_history, self.header, data)
        return response

    def screeners_config(self) -> dict:
        """
        Retrieves screeners config required for the screeners API.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.screeners_config, self.header)
        else:
            response = self.service.get_call(Config.screeners_config, self.header)
        return response

    def screeners_query(self, data) -> dict:
        """
        Retrieves screeners query based on the provided data.

        Args:
            data (dict): A dictionary containing the screeners query details.
            - screener (str): The screener to use.
            - universe (str): The universe to use.
            - fields (str): The fields to use.
            - order_by (str): The field to order by.
            - order (str): The order to use.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.screeners_query, self.header, data)
        else:
            response = self.service.get_call(Config.screeners_query, self.header, data)
        return response

    def screeners_candlestick(self, data) -> dict:
        """
        Retrieves screeners query based on the provided data.

        Args:
            data (dict): A dictionary containing the screeners query details.
            - screener (str): The screener to use.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.screeners_candlestick, self.header, data)
        else:
            response = self.service.get_call(Config.screeners_candlestick, self.header, data)
        return response

    def screeners_technical(self, data) -> dict:
        """
        Retrieves screeners query based on the provided data.

        Args:
            data (dict): A dictionary containing the screeners query details.
            - screener (str): The screener to use.

        Returns:
            The response JSON as a dictionary.
        """
        if self.is_async:
            response = self.service.get_async_call(Config.screeners_technical, self.header, data)
        else:
            response = self.service.get_call(Config.screeners_technical, self.header, data)
        return response//===== fyers_apiv3/fyers_logger.py=====//from typing import Any, Dict, Union
from aws_lambda_powertools import Logger


class FyersLogger(Logger):
    def __init__(
        self, service: str, level: str, stack_level: int = 4, **kwargs
    ) -> None:
        """Create FyersLogger object

        Args:
            service (str): Service name. This should be the same across the code wherever the logger is initialized
            level (str): Logger level. Possible values are [INFO, DEBUG, CRITICAL, WARNING]

        Kwargs:
            stack_level (int): Stack level. This decides how many levels the stack should go up to get the line number
                            to be printed in the logging statement
        """
        super().__init__(
            service=service,
            level=level,
            location="[%(funcName)s:%(lineno)s] %(module)s",
            **kwargs
        )
        self.__stacklevel = stack_level

    def __populate_request_data(self, stack_level, **kwargs) -> Dict[str, Any]:
        """Adds additional log data to log statement

        Returns:
            Dict[str, Any]: all the keyword arguments along with extra data
        """
        kwargs["stacklevel"] = stack_level
        if "extra" not in kwargs:
            kwargs["extra"] = {}

        if "message" in kwargs["extra"]:
            kwargs["extra"]["passed_message"] = kwargs["extra"].pop("message")
        return kwargs

    def error(self, msg: Union[str, Dict[Any, Any]], *args, **kwargs) -> None:
        """Logs error statement

        Args:
            msg (Union[str, Dict[Any, Any]]): Can be str or dict object

        Kwargs:
            extra (Dict[Any, Any]): Adds this data to the log statement
        """
        stacklevel = self.__stacklevel
        while stacklevel > 0:
            try:
                kwargs = self.__populate_request_data(stacklevel, **kwargs)
                super().error(msg, *args, **kwargs)
                break
            except:
                stacklevel -= 1

    def info(self, msg: Union[str, Dict[Any, Any]], *args, **kwargs) -> None:
        """Logs info statement

        Args:
            msg (Union[str, Dict[Any, Any]]): Can be str or dict object

        Kwargs:
            extra (Dict[Any, Any]): Adds this data to the log statement
        """
        stacklevel = self.__stacklevel
        while stacklevel > 0:
            try:
                kwargs = self.__populate_request_data(stacklevel, **kwargs)
                super().info(msg, *args, **kwargs)
                break
            except:
                stacklevel -= 1

    def debug(self, msg: Union[str, Dict[Any, Any]], *args, **kwargs) -> None:
        """Logs debug statement

        Args:
            msg (Union[str, Dict[Any, Any]]): Can be str or dict object

        Kwargs:
            extra (Dict[Any, Any]): Adds this data to the log statement
        """
        stacklevel = self.__stacklevel
        while stacklevel > 0:
            try:
                kwargs = self.__populate_request_data(stacklevel, **kwargs)
                super().debug(msg, *args, **kwargs)
                break
            except:
                stacklevel -= 1

    def exception(self, msg: Union[str, Dict[Any, Any]], *args, **kwargs) -> None:
        """Logs exception statement. Should be called only from exception block

        Args:
            msg (Union[str, Dict[Any, Any]]): Can be str or dict object

        Kwargs:
            extra (Dict[Any, Any]): Adds this data to the log statement
        """
        stacklevel = self.__stacklevel
        while stacklevel > 0:
            try:
                kwargs = self.__populate_request_data(stacklevel, **kwargs)
                super().exception(msg, *args, **kwargs)
                break
            except:
                stacklevel -= 1
//===== fyers_apiv3/FyersWebsocket/__init__.py=====////===== fyers_apiv3/FyersWebsocket/data_ws.py=====//import base64
import logging
import threading
import time
from typing import Optional, Callable

from pkg_resources import resource_filename
import requests
import urllib.parse
import websocket
from threading import Thread
import struct
import json

from fyers_apiv3.FyersWebsocket import defines
from fyers_apiv3.fyers_logger import FyersLogger


class SymbolConversion:
    def __init__(self, access_token: str, data_type: str, log_path: str):
        """
        Initializes a SymbolConversion instance.

        Args:
            access_token (str): The access token used for authentication.
            data_type (str): The data_type associated with the symbol conversion. 
                            Valid values are 'Symbolupdate' or 'DepthUpdate'.

        """
        self.data_type = data_type
        if ":" in access_token:
            access_token = access_token.split(":")[1]
        self.access_token = access_token
        self.log_path = log_path
        self.symbols_token_api = "https://api-t1.fyers.in/data/symbol-token"

        if log_path:
            self.log_path = log_path + "/"
        else:
            self.log_path = ""
        self.data_logger = FyersLogger(
            "FyersDataSocket",
            "DEBUG",
            stack_level=3,
            logger_handler=logging.FileHandler(log_path + "fyersDataSocket.log"),
        )

    def symbol_to_hsmtoken(self, symbols: list):
        """
        Converts symbols to HSM tokens.

        Args:
            symbols (list): A list of symbols to be converted.

        Returns:
            tuple: A tuple containing dictionary and list.
                - The first dictionary represents the mapping of symbols to HSM tokens.
                - The second list represents any symbols that could not be converted.

        """
        try:
            data = {"symbols": symbols}
            response = requests.post(
                url=self.symbols_token_api ,
                headers={
                    "Authorization": self.access_token,
                    "Content-Type": "application/json",
                },json=data
            )
            response_data =response.json()
            datadict = {}
            file_path = resource_filename('fyers_apiv3.FyersWebsocket', 'map.json')
            with open(file_path, "r") as file:
                mapper = json.load(file)
            index_dict = mapper["index_dict"]
            exch_seg_dict = mapper["exch_seg_dict"]
            wrong_symbol = []
            dp_index_flag = False


            if response_data['s'] == "ok":
                for symbol, fytoken in response_data["validSymbol"].items():
                    ex_sg = fytoken[:4]
                    if ex_sg not in exch_seg_dict:
                        continue
                    segment = exch_seg_dict[ex_sg]
                    symbol_split = symbol.split("-")
                    update_dict = True
                    if len(symbol_split) > 1 and symbol_split[-1] == "INDEX" and self.data_type != "DepthUpdate":
                        if symbol in index_dict:
                                exch_token = index_dict[symbol]
                        else:
                            exch_token = (
                                symbol.split(":")[1].split("-")[0]
                            )
                        hsm_symbol = (
                                "if" + "|" + segment + "|" + exch_token
                            )                
                    elif self.data_type == "DepthUpdate" and symbol_split[-1] != "INDEX":
                        
                        exch_token = fytoken[10:]
                        hsm_symbol = (
                            "dp" + "|" + segment + "|" + exch_token
                        )
                    elif self.data_type == "SymbolUpdate":
                        exch_token = fytoken[10:]
                        hsm_symbol = (
                            "sf" + "|" + segment + "|" + exch_token
                        )                        
                    elif self.data_type == "DepthUpdate" and symbol_split[-1] == "INDEX":
                        update_dict = False
                        dp_index_flag =True

                    if update_dict:
                        datadict[hsm_symbol] = symbol
                if response_data["invalidSymbol"]:
                    wrong_symbol = response_data["invalidSymbol"]
                return (datadict, wrong_symbol, dp_index_flag,"")

            elif response_data['s'] == "error":
                
                return ({}, [],dp_index_flag, response_data["message"])


        except Exception as e:
            self.data_logger.exception(e)


class FyersDataSocket:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        access_token: str,
        write_to_file: bool = False,
        log_path: Optional[str] = None,
        litemode: bool = False,
        reconnect: bool = True,
        on_message: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_connect: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        reconnect_retry: int = 5
    ):

        """
        Initialize YourClass instance.

        Args:
            access_token (str): The access token used for authentication.
            write_to_file (bool, optional): Specifies if the class should run in the background.
                Defaults to False.
            log_path (str, optional): The path to the log file. Defaults to None.
            litemode (bool, optional): Specifies if the class should run in litemode.
                Defaults to False.
            reconnect (bool, optional): Specifies if the class should attempt to reconnect on failure.
                Defaults to True.
            on_message (callable, optional): Callback function to be executed when a message is received.
                Defaults to None.
            on_error (callable, optional): Callback function to be executed when an error occurs.
                Defaults to None.
            on_connect (callable, optional): Callback function to be executed when a connection is established.
                Defaults to None.
            on_close (callable, optional): Callback function to be executed when a connection is closed.
                Defaults to None.
        """
        
        self.__url = "wss://socket.fyers.in/hsm/v1-5/prod"
        self.__access_token = access_token
        self.__hsm_token = ""
        self.log_path = log_path
        self.lite = litemode
        self.max_retry = reconnect_retry
        self.source = "PythonSDK-3.0.9"
        self.channel_num = 11
        self.channels = []
        self.running_channels = set()
        self.data_type = None
        self.OnMessage = on_message
        self.OnError = on_error
        self.OnOpen = on_connect
        self.OnClose = on_close
        self.UpdateTick = False
        self.ack_count = 0
        self.__ws_run = None
        self.write_to_file = write_to_file
        self.background_flag = False
        self.update_count = 0
        self.literesp = {}
        self.channel_symbol = []
        self.symbol_dict = {}
        self.scrips_count = {}
        self.scrips_per_channel = {}
        self.restart_flag = reconnect
        self.websocket_lock = threading.Lock()
        self.message_lock = threading.Lock()
        self.message_condition = threading.Condition(lock=self.message_lock)
        self.unsub_symbol = []
        for i in range(1, 31):
            self.scrips_per_channel[i] = []
        self.active_channel = None
        self.message = []
        self.resp = {}
        self.__ws_object = None
        self.__valid_token = False
        self.dp_sym = {}
        self.ping_thread = None
        self.message_thread = None
        self.message_thread_stop_event = None
        self.ws_thread = None
        self.infy_loop = None
        self.symbol_limit = 5000
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 50
        if reconnect_retry < self.max_reconnect_attempts:
            self.max_reconnect_attempts = reconnect_retry
       
        self.mode = "P"
        self.reconnect_delay = 0
        self.index_sym = {}
        self.scrips_sym = {}
        self.symbol_token = {}
        self.ack_bool = False     
        if log_path:
            self.log_path = log_path + "/"
        else:
            self.log_path = ""
        self.data_logger = FyersLogger(
            "FyersDataSocket",
            "DEBUG",
            stack_level=3,
            logger_handler=logging.FileHandler(self.log_path + "fyersDataSocket.log"),
        )
        file_path = resource_filename('fyers_apiv3.FyersWebsocket', 'map.json')

        with open(file_path, "r") as file:
            # Imported json file
            mapper = json.load(file)

        self.data_val = mapper["data_val"]
        self.index_val = mapper["index_val"]
        self.lite_val = mapper["lite_val"]
        self.depthvalue = mapper["depthvalue"]

    def access_token_to_hsmtoken(self) -> bool :
        """
        Decode APIv2 token to extract 'hsm_key' and check for validity.

        This function decodes the APIv2 access token and extracts the 'hsm_key' from it.
        It also verifies if the token is expired by comparing the 'exp' (expiration) claim in the
        token's payload with the current timestamp. If the token is valid and not expired, it sets
        the 'hsm_token' attribute and returns True. Otherwise, it raises an error and returns False.

        Returns:
            bool: True if the token is valid and not expired, False otherwise.
        """
        try:
            header_token , payload_b64, _ = self.__access_token.split(".")
            # Decode the base64 encoded payload
            decoded_header = base64.urlsafe_b64decode(header_token + "===")
            decoded_payload = base64.urlsafe_b64decode(payload_b64 + "===")
            # Convert the decoded payload to a string (assuming it's in JSON format)
            decode_token = json.loads(decoded_payload.decode())
            today = int(time.time())
            if decode_token["exp"] - today  < 0:
                self.On_error(
                    {   
                        "type": defines.AUTH_TYPE,
                        "code": defines.TOKEN_EXPIRED,
                        "message": defines.TOKEN_EXPIRED_MSG,
                        "s": defines.ERROR,
                    }
                )
                return False
            self.__valid_token = True

            self.__hsm_token = decode_token["hsm_key"]
            return True
        
        except:
            self.On_error(
                {   "type": defines.AUTH_TYPE,
                    "code": defines.INVALID_CODE,
                    "message": defines.INVALID_TOKEN,
                    "s": defines.ERROR,
                }
            )
            # self.data_logger.error(e)
            return False



    def __access_token_msg(self) -> bytearray:
        """
        Create a message in bytearray for token.

        Returns:
            bytearray: The token message in bytearray format.
        """
        try:
            buffer_size = 18 + len(self.__hsm_token) + len(self.source)

            # Create the byte buffer
            byte_buffer = bytearray()

            # Pack data length into the byte buffer
            byte_buffer.extend(struct.pack("!H", buffer_size - 2))

            # Set ReqType
            byte_buffer.extend(bytes([1]))

            # Set FieldCount
            byte_buffer.extend(bytes([4]))

            # Field-1: AuthToken
            field1_id = 1
            field1_size = len(self.__hsm_token)
            byte_buffer.extend(bytes([field1_id]))
            byte_buffer.extend(struct.pack("!H", field1_size))
            byte_buffer.extend(self.__hsm_token.encode())

            # Field-2
            field2_id = 2
            field2_size = 1
            byte_buffer.extend(bytes([field2_id]))
            byte_buffer.extend(struct.pack("!H", field2_size))
            byte_buffer.extend(self.mode.encode('utf-8'))

            # Field-3
            field3_id = 3
            field3_size = 1
            byte_buffer.extend(bytes([field3_id]))
            byte_buffer.extend(struct.pack("!H", field3_size))
            byte_buffer.extend(bytes([1]))

            # Field-4: self.source
            field4_id = 4
            field4_size = len(self.source)
            byte_buffer.extend(bytes([field4_id]))
            byte_buffer.extend(struct.pack("!H", field4_size))
            byte_buffer.extend(self.source.encode())

            return byte_buffer

        except Exception as e:
            self.data_logger.exception(e)

    def __lite_mode_msg(self) -> bytearray:
        """
        Create a message in bytearray for lite mode connection.

        Returns:
            bytearray: The lite mode message in bytearray format.
        """

        try:
            self.channels = [self.channel_num]
            data = bytearray()

            data.extend(struct.pack(">H", 0))

            data.extend(struct.pack("B", 12))

            data.extend(struct.pack("B", 2))

            channel_bits = 0
            for channel_num in self.channels:
                if channel_num < 64 and channel_num > 0:
                    channel_bits |= 1 << channel_num
            # Field-1
            field_1 = bytearray()
            field_1.extend(struct.pack("B", 1))
            field_1.extend(struct.pack(">H", 8))
            field_1.extend(struct.pack(">Q", channel_bits))
            data.extend(field_1)

            # Field-2
            field_2 = bytearray()
            field_2.extend(struct.pack("B", 2))
            field_2.extend(struct.pack(">H", 1))
            field_2.extend(struct.pack("B", 76))
            data.extend(field_2)

            return data

        except Exception as e:
            self.data_logger.exception(e)

    def __full_mode_msg(self) -> bytearray:

        """
        Create a message in bytearray for full mode connection.

        Returns:
            bytearray: The full mode message in bytearray format.
        """
        try:
            self.channels = [self.channel_num]
            data = bytearray()

            data.extend(struct.pack(">H", 0))

            data.extend(struct.pack("B", 12))

            data.extend(struct.pack("B", 2))

            channel_bits = 0
            for channel_num in self.channels:
                if channel_num < 64 and channel_num > 0:
                    channel_bits |= 1 << channel_num
            # Field-1
            field_1 = bytearray()
            field_1.extend(struct.pack("B", 1))
            field_1.extend(struct.pack(">H", 8))
            field_1.extend(struct.pack(">Q", channel_bits))
            data.extend(field_1)

            # Field-2
            field_2 = bytearray()
            field_2.extend(struct.pack("B", 2))
            field_2.extend(struct.pack(">H", 1))
            field_2.extend(struct.pack("B", 70))
            data.extend(field_2)

            return data

        except Exception as e:
            self.data_logger.exception(e)

    def __subscription_msg(self, symbols: list) -> bytearray:

        """
        Create a message in bytearray for symbol subscription.

        Args:
            symbols (list): A list of symbols to subscribe to.

        Returns:
            bytearray: The subscription message in bytearray format.
        """

        try:
            self.scrips_per_channel[self.channel_num] += symbols
            self.scrips = symbols
            self.scrips_data = bytearray()
            self.scrips_data.append(len(self.scrips) >> 8 & 0xFF)
            self.scrips_data.append(len(self.scrips) & 0xFF)
            for scrip in self.scrips:
                scrip_bytes = str(scrip).encode("ascii")
                self.scrips_data.append(len(scrip_bytes))
                self.scrips_data.extend(scrip_bytes)

            data_len = (
                18 + len(self.scrips_data) + len(self.__access_token) + len(self.source)
            )
            request_type = 4
            field_count = 2
            buffer_msg = bytearray()
            buffer_msg.extend(struct.pack(">H", data_len))
            buffer_msg.append(request_type)
            buffer_msg.append(field_count)

            # Field-1
            buffer_msg.append(1)
            buffer_msg.extend(struct.pack(">H", len(self.scrips_data)))
            buffer_msg.extend(self.scrips_data)

            # Field-2
            buffer_msg.append(2)
            buffer_msg.extend(struct.pack(">H", 1))
            buffer_msg.append(self.channel_num)
            return buffer_msg

        except Exception as e:
            self.data_logger.exception(e)

    def __unsubscription_msg(self, symbols: list) -> bytearray:
        """
        Create a message in bytearray for unsubscription message.

        Args:
            symbols (list): A list of symbols to unsubscribe from.

        Returns:
            bytearray: The unsubscription message in bytearray format.
        """
        try:
            scrips_data = bytearray()
            scrips_data.append(len(symbols) >> 8 & 0xFF)
            scrips_data.append(len(symbols) & 0xFF)
            for scrip in symbols:
                scrip_bytes = str(scrip).encode("ascii")
                scrips_data.append(len(scrip_bytes))
                scrips_data.extend(scrip_bytes)

            data_len = (
                18 + len(scrips_data) + len(self.__access_token) + len(self.source)
            )
            request_type = 5
            field_count = 2
            buffer_msg = bytearray()
            buffer_msg.extend(struct.pack(">H", data_len))
            buffer_msg.append(request_type)
            buffer_msg.append(field_count)

            # Field-1
            buffer_msg.append(1)
            buffer_msg.extend(struct.pack(">H", len(scrips_data)))
            buffer_msg.extend(scrips_data)

            # Field-2
            buffer_msg.append(2)
            buffer_msg.extend(struct.pack(">H", 1))
            buffer_msg.append(self.channel_num)

            return buffer_msg
        except Exception as e:
            self.data_logger.exception(e)

    def __channel_resume_msg(self, channel: int) -> bytearray:

        """
        Create a message in bytearray for channel resume.

        Args:
            channel (int): The channel to resume.

        Returns:
            bytearray: The channel resume message in bytearray format.
        """
        try:

            self.channels = [channel]

            data = bytearray()

            data.extend(struct.pack(">H", 0))

            data.extend(struct.pack("B", 8))

            data.extend(struct.pack("B", 1))

            channel_bits = 0
            for channel_num in self.channels:
                if channel_num < 64 and channel_num > 0:
                    channel_bits |= 1 << channel_num
            # Field-1
            field_1 = bytearray()
            field_1.extend(struct.pack("B", 1))
            field_1.extend(struct.pack(">H", 8))
            field_1.extend(struct.pack(">Q", channel_bits))
            data.extend(field_1)

            return data

        except Exception as e:
            self.data_logger.exception(e)

    def __channel_pause_msg(self, channel: int) -> bytearray:

        """
        Create a message in bytearray for channel pause.

        Args:
            channel (int): The channel to pause.

        Returns:
            bytearray: The channel pause message in bytearray format.
        """

        try:
            self.channels = [channel]

            data = bytearray()

            data.extend(struct.pack(">H", 0))

            data.extend(struct.pack("B", 7))

            data.extend(struct.pack("B", 1))

            channel_bits = 0
            for channel_num in self.channels:
                if channel_num < 64 and channel_num > 0:
                    channel_bits |= 1 << channel_num
            # Field-1
            field_1 = bytearray()
            field_1.extend(struct.pack("B", 1))
            field_1.extend(struct.pack(">H", 8))
            field_1.extend(struct.pack(">Q", channel_bits))
            data.extend(field_1)

            return data

        except Exception as e:
            self.data_logger.exception(e)

    def __ackowledgement_msg(self, message_number: int) -> bytearray:

        """
        Create a message in bytearray for acknowledgement.

        Args:
            message_number (int): The message number to acknowledge.

        Returns:
            bytearray: The acknowledgement message in bytearray format.
        """
        try:
            total_size = 11
            req_type = 3
            field_count = 1
            field_id = 1
            field_size = 4
            field_value = message_number
            buffer_msg = bytearray()
            # Pack the data into the byte array
            buffer_msg.extend(struct.pack(">H", total_size - 2))
            buffer_msg.extend(struct.pack("B", req_type))
            buffer_msg.extend(struct.pack("B", field_count))
            buffer_msg.extend(struct.pack("B", field_id))
            buffer_msg.extend(struct.pack(">H", field_size))
            buffer_msg.extend(struct.pack(">I", field_value))

            return buffer_msg

        except Exception as e:
            self.data_logger.exception(e)

    def __auth_resp(self, data: bytearray) -> dict:
        """
        Unpacks the authentication response from a bytearray.

        Args:
            data (bytearray): The authentication response message.

        Returns:
            dict: The authentication response as a dictionary with keys 'code', 'message', and 's'.
        """

        try:
            offset = 4
            offset += 1
            field_length = struct.unpack("!H", data[offset : offset + 2])[0]
            offset += 2
            string_val = data[offset : offset + field_length].decode("utf-8")
            offset += field_length

            if string_val == "K":

                self.On_message(
                    {   "type": defines.AUTH_TYPE,
                        "code": defines.SUCCESS_CODE,
                        "message": defines.AUTH_SUCCESS,
                        "s": defines.SUCCESS,
                    }
                )
            else:
                self.On_error(
                    {   "type": defines.AUTH_TYPE,
                        "code": defines.AUTH_ERROR_CODE,
                        "message": defines.AUTH_FAIL,
                        "s": defines.ERROR,
                    }
                )

            offset += 1
            field_length = struct.unpack("!H", data[offset : offset + 2])[0]
            offset += 2
            self.ack_count = struct.unpack(">I", data[offset : offset + 4])[0]
            offset += 4

        except Exception as e:
            self.data_logger.exception(e)

    def __subscribe_resp(self, data: bytearray) -> dict:
        """
        Unpacks the subscription response from a bytearray.

        Args:
            data (bytearray): The subscription response message.

        Returns:
            dict: The subscription response as a dictionary with keys 'code', 'message', and 's'.
        """

        try:

            offset = 5
            field_length = struct.unpack("H", data[offset : offset + 2])[0]
            offset += 2
            string_val = data[offset : offset + 1].decode("latin-1")
            offset += field_length
            if string_val == "K":

                self.On_message(
                    {   
                        "type": defines.SUBS_TYPE,
                        "code": defines.SUCCESS_CODE,
                        "message": defines.SUBSCRIBE_SUCCESS,
                        "s": defines.SUCCESS,
                    }
                )
            else:
                self.On_error(
                    {
                        "type": defines.SUBS_TYPE,
                        "code": defines.SUBS_ERROR_CODE,
                        "message": defines.SUBSCRIBE_FAIL,
                        "s": defines.ERROR,
                    }
                )

        except Exception as e:
            self.data_logger.exception(e)

    def __unsubscribe_resp(self, data: bytearray) -> dict:

        """
        Unpacks the unsubscription response from a bytearray.

        Args:
            data (bytearray): The unsubscription response message.

        Returns:
            dict: The unsubscription response as a dictionary with keys 'code', 'message', and 's'.
        """

        try:

            offset = 5
            field_length = struct.unpack("H", data[offset : offset + 2])[0]
            offset += 2
            string_val = data[offset : offset + 1].decode("latin-1")
            offset += field_length
            if string_val == "K":

                self.On_message(
                    {
                        "type": defines.UNSUBS_TYPE,
                        "code": defines.SUCCESS_CODE,
                        "message": defines.UNSUBSCRIBE_SUCCESS,
                        "s": defines.SUCCESS,
                    }
                )
                for symbol in self.unsub_symbol:
                    count = 0
                    for channel in self.running_channels:
                        if symbol in self.scrips_per_channel[channel]:
                            count +=1 
                        if count > 1:
                            break
                    if symbol in self.scrips_per_channel[self.active_channel]:
                        self.scrips_per_channel[self.active_channel].remove(symbol)
                    if count == 1:
                        self.symbol_token.pop(symbol)
                            
            else:
                self.On_error(
                    {
                        "type": defines.UNSUBS_TYPE,
                        "code": defines.UNSUBS_ERROR_CODE,
                        "message": defines.UNSUBSCRIBE_FAIL,
                        "s": defines.ERROR,
                    }
                )

        except Exception as e:
            self.data_logger.exception(e)

    def __lite_full_mode_resp(self, data: bytearray) -> dict:

        """
        Unpacks the lite/full mode response from a bytearray.

        Args:
            data (bytearray): The lite/full mode response message.

        Returns:
            dict: The lite/full mode response as a dictionary with keys 'code', 'message', and 's'.
        """

        try:
            offset = 3

            # Unpack the field count
            field_count = struct.unpack("!B", data[offset : offset + 1])[0]
            offset += 1

            if field_count >= 1:
                # Unpack the field ID
                offset += 1

                # Unpack the field length
                field_length = struct.unpack("!H", data[offset : offset + 2])[0]
                offset += 2

                # Extract the string value and decode it
                string_val = data[offset : offset + field_length].decode("utf-8")
                offset += field_length

                if string_val == "K":
                    if self.lite:
                        self.On_message(
                            {
                                "type": defines.LITE_MODE_TYPE,
                                "code": defines.SUCCESS_CODE,
                                "message": defines.LITE_MODE,
                                "s": defines.SUCCESS,
                            }
                        )
                    else:
                        self.On_message(
                            {
                                "type": defines.FULL_MODE_TYPE,
                                "code": defines.SUCCESS_CODE,
                                "message": defines.FULL_MODE,
                                "s": defines.SUCCESS,
                            }
                        )
                else:
                    self.On_error(
                        {
                            "code": defines.MODE_ERROR_CODE,
                            "message": defines.MODE_CHANGE_ERROR,
                            "s": defines.ERROR,
                        }
                    )

        except Exception as e:
            self.data_logger.exception(e)
        
    def __resume_pause_resp(self, data: bytearray, channeltype: int) -> dict:
        """
        Unpacks and processes the resume/pause response data based on the channel type.

        Args:
            data (bytearray): The response data.
            channeltype (int): The channel type. 7 for pause and 8 for resume.

        Returns:
            dict: The resume/pause response as a dictionary with keys 'code', 'message', and 's'.
        """
        try:
            offset = 5

            # Unpack the field length
            field_length = struct.unpack("!H", data[offset : offset + 2])[0]
            offset += 2

            # Extract the string value and decode it
            string_val = data[offset : offset + field_length].decode("utf-8")
            offset += field_length

            if string_val == "K":
                if channeltype == 7:
                    self.On_message(
                        {
                            "type": defines.CH_PAUSE_TYPE,
                            "code": defines.SUCCESS_CODE,
                            "message": defines.CHANNEL_PAUSED,
                            "s": defines.SUCCESS,
                        }
                    )
                else:
                    self.On_message(
                        {
                            "type": defines.CH_RESUME_TYPE,
                            "code": defines.SUCCESS_CODE,
                            "message": defines.CHANNEL_RESUMED,
                            "s": defines.SUCCESS,
                        }
                    )
            else:
                if channeltype == 7:
                    self.On_error(
                        {
                            "type": defines.CH_PAUSE_TYPE,
                            "code": defines.PAUSE_ERROR_CODE,
                            "message": defines.CHANNEL_CHANGE_FAIL,
                            "s": defines.ERROR,
                        }
                    )
                else:
                    self.On_error(
                        {
                            "type": defines.CH_RESUME_TYPE,
                            "code": defines.RESUME_ERROR_CODE,
                            "message": defines.CHANNEL_CHANGE_FAIL,
                            "s": defines.ERROR,
                        }
                    )

        except Exception as e:
            self.data_logger.exception(e)

    def __response_output(self, data: str, data_type: str) -> object:

        """
        Processes the response data and returns the output based on the specified data_type.

        Args:
            data (bytearray): The response data.
            data_type (str): The type of data to be processed.

        Returns:
            object: The processed output based on the specified data_type.
        """
        try:
            data_resp = data
            precision_calcu_value = [
                                    "ltp",
                                    "bid_price",
                                    "ask_price",
                                    "avg_trade_price",
                                    "low_price",
                                    "high_price",
                                    "open_price",
                                    "prev_close_price",
                                ]
            response = {}
            if (
                "bidPrice1" not in data_resp
                # and "vol_traded_today" in data_resp
                and self.lite
            ):
                for i, val in enumerate(self.lite_val):
                    if val in data_resp and val == "ltp":
                        response[val] = data_resp[val] / (
                                (10 ** data_resp["precision"] ) * data_resp["multiplier"]
                            )
                    else:
                        response[val] = data_resp[val]
                if "prev_close_price" in response and "ltp" in response:
                    response["ch"] = round((response['ltp']  - response['prev_close_price']),2) 
                    response["chp"] = round((response["ch"]  / response['prev_close_price'] * 100) , 2)
            else:
                if data_type == "depth":

                    for i, val in enumerate(self.depthvalue):
                        if val in data_resp and i < 10:
                            response[val] = data_resp[val] / ((
                                10 ** data_resp["precision"] ) * data_resp["multiplier"])

                        elif val in data_resp:
                            response[val] = data_resp[val]
                elif data_type == "scrips":
                    for i, val in enumerate(self.data_val):
                        if val in data_resp and val in precision_calcu_value and val not in ["upper_ckt", "lower_ckt"]:
                            response[val] = data_resp[val] / (
                                (10 ** data_resp["precision"] )* data_resp["multiplier"]
                            )
                            # response[val] = data_resp[val] / (

                        elif val in data_resp:
                            response[val] = data_resp[val]

                    response["lower_ckt"] = 0
                    response["upper_ckt"] = 0
                    if "prev_close_price" in response and "ltp" in response and response["prev_close_price"] != 0:
                        response["ch"] = round((response['ltp']  - response['prev_close_price']),4) 
                        response["chp"] = round((response["ch"]  / response['prev_close_price'] * 100) , 4)
                    if "OI" in response:
                        response.pop("OI")
                    if "Yhigh" in response:
                        response.pop("Yhigh")
                    if "Ylow" in response:
                        response.pop("Ylow")
                else:
                    for i, val in enumerate(self.index_val):
                        if val in data_resp and i in [0, 1, 3, 4, 5]:
                            response[val] = data_resp[val] / (
                                (10 ** data_resp["precision"] ) * data_resp["multiplier"]
                            )
                        elif val in data_resp:
                            response[val] = data_resp[val]
                        if "prev_close_price" in response and "ltp" in response:
                            response["ch"] = round((response['ltp']  - response['prev_close_price']),2) 
                            response["chp"] = round((response["ch"]  / response['prev_close_price'] * 100) , 2)
            
            self.On_message(response)

        except Exception as e:
            self.data_logger.exception(e)

    def __datafeed_resp(self, data: bytearray):

        """
        Unpacks and processes the data based on data_type and sends it to the __response_output function.

        Args:
            data (bytearray): The response data.

        Returns:
            None
        """
        try:

            if self.ack_count > 0:
                self.update_count += 1
                message_num = struct.unpack(">I", data[3:7])[0]
                if self.update_count == self.ack_count:
                    self.ack_msg = self.__ackowledgement_msg(message_num)
                    # self.message.append(self.ack_msg)
                    self.add_message(self.ack_msg)

                    
                    self.update_count = 0
            scrip_count = struct.unpack("!H", data[7:9])[0]
            offset = 9

            for _ in range(scrip_count):
                data_type = struct.unpack("B", data[offset : offset + 1])[0]
                if data_type == 83:  # Snapshot datafeed

                    offset += 1
                    topic_id = struct.unpack("H", data[offset : offset + 2])[0]
                    offset += 2
                    topic_name_len = struct.unpack("B", data[offset : offset + 1])[0]
                    offset += 1

                    topic_name = data[offset : offset + topic_name_len].decode("utf-8")
                    offset += topic_name_len

                    # Maintaining dict - topic_id : topic_name
                    if topic_name[:2] == "dp":
                        self.dp_sym[topic_id] = topic_name

                        self.resp[self.dp_sym[topic_id]] = {}

                        field_count = struct.unpack("B", data[offset : offset + 1])[0]
                        offset += 1

                        for index in range(field_count):
                            value = struct.unpack(">i", data[offset : offset + 4])[0]
                            offset += 4

                            if value != -2147483648:
                                self.resp[self.dp_sym[topic_id]][
                                    self.depthvalue[index]
                                ] = value

                        offset += 2

                        multiplier = struct.unpack(">H", data[offset : offset + 2])[0]
                        self.resp[self.dp_sym[topic_id]]["multiplier"] = multiplier
                        offset += 2
                        precision = struct.unpack("B", data[offset : offset + 1])[0]
                        self.resp[self.dp_sym[topic_id]]["precision"] = precision
                        offset += 1

                        val = ["exchange", "exchange_token", "symbol"]
                        for i in range(3):
                            string_len = struct.unpack("B", data[offset : offset + 1])[
                                0
                            ]
                            offset += 1
                            string_data = data[offset : offset + string_len].decode(
                                "utf-8",errors='ignore'
                            )
                            self.resp[self.dp_sym[topic_id]][val[i]] = string_data
                            offset += string_len
                        self.resp[self.dp_sym[topic_id]]["type"] = "dp"
                        self.resp[topic_name]["symbol"] = self.symbol_token[topic_name]
                        self.__response_output(
                            self.resp[self.dp_sym[topic_id]], "depth"
                        )

                    elif topic_name[:2] == "if":

                        self.index_sym[topic_id] = topic_name
                        self.resp[self.index_sym[topic_id]] = {}

                        # field_count - 21 in scrips , 25 in depth , 6 in index
                        field_count = struct.unpack("B", data[offset : offset + 1])[0]
                        offset += 1

                        for index in range(field_count):

                            value = struct.unpack(">i", data[offset : offset + 4])[0]
                            offset += 4

                            if value != -2147483648:
                                self.resp[self.index_sym[topic_id]][
                                    self.index_val[index]
                                ] = value

                        offset += 2

                        multiplier = struct.unpack(">H", data[offset : offset + 2])[0]
                        self.resp[self.index_sym[topic_id]]["multiplier"] = multiplier
                        offset += 2

                        precision = struct.unpack("B", data[offset : offset + 1])[0]
                        self.resp[self.index_sym[topic_id]]["precision"] = precision
                        offset += 1

                        val = ["exchange", "exchange_token", "symbol"]
                        for i in range(3):
                            string_len = struct.unpack("B", data[offset : offset + 1])[
                                0
                            ]
                            offset += 1
                            string_data = data[offset : offset + string_len].decode(
                                "utf-8",errors='ignore'
                            )
                            self.resp[self.index_sym[topic_id]][val[i]] = string_data
                            offset += string_len
                        self.resp[topic_name]["symbol"] = self.symbol_token[topic_name]
                        self.resp[self.index_sym[topic_id]]["type"] = "if"
                        self.__response_output(
                            self.resp[self.index_sym[topic_id]], "index"
                        )

                    elif topic_name[:2] == "sf":
                        self.scrips_sym[topic_id] = topic_name
                        self.resp[self.scrips_sym[topic_id]] = {}

                        # field_count - 21 in scrips , 25 in depth , 6 in index
                        field_count = struct.unpack("B", data[offset : offset + 1])[0]
                        offset += 1

                        for index in range(field_count):
                            value = struct.unpack(">i", data[offset : offset + 4])[0]
                            offset += 4
                            if value != -2147483648:
                                self.resp[self.scrips_sym[topic_id]][
                                    self.data_val[index]
                                ] = value

                        offset += 2

                        multiplier = struct.unpack(">H", data[offset : offset + 2])[0]
                        self.resp[self.scrips_sym[topic_id]]["multiplier"] = multiplier
                        offset += 2

                        precision = struct.unpack("B", data[offset : offset + 1])[0]
                        self.resp[self.scrips_sym[topic_id]]["precision"] = precision
                        offset += 1
                        val = ["exchange", "exchange_token", "symbol"]
                        for i in range(3):
                            string_len = struct.unpack("B", data[offset : offset + 1])[
                                0
                            ]
                            offset += 1
                            string_data = bytes(data[offset : offset + string_len]).decode(
                                "utf-8" ,errors='ignore'
                            )
                            self.resp[self.scrips_sym[topic_id]][val[i]] = string_data
                            offset += string_len
                        self.resp[topic_name]["symbol"] = self.symbol_token[topic_name]
                        self.resp[self.scrips_sym[topic_id]]["type"] = "sf"
                        self.__response_output(
                            self.resp[self.scrips_sym[topic_id]], "scrips"
                        )

                elif data_type == 85:  # Full mode datafeed
                    offset += 1
                    topic_id = struct.unpack("H", data[offset : offset + 2])[0]
                    offset += 2

                    field_count = struct.unpack("B", data[offset : offset + 1])[0]
                    offset += 1
                    sf_flag, idx_flag, dp_flag = False, False, False
                    self.UpdateTick = False
                    for index in range(field_count):
                        value = struct.unpack(">i", data[offset : offset + 4])[0]
                        offset += 4
                        # if field_count == 20 or field_count == 21:
                        if topic_id in self.scrips_sym:
                            if self.data_val[index] in self.resp[self.scrips_sym[topic_id]] and self.resp[self.scrips_sym[topic_id]][
                                self.data_val[index]] != value and value != -2147483648:
                                self.resp[self.scrips_sym[topic_id]][
                                    self.data_val[index]
                                ] = value
                                self.UpdateTick = True
                            elif self.data_val[index] not in self.resp[self.scrips_sym[topic_id]] and value != -2147483648:
                                self.resp[self.scrips_sym[topic_id]][
                                    self.data_val[index]
                                ] = value
                                self.UpdateTick = True

                            sf_flag = True
                        elif topic_id in self.index_sym:
                            if self.index_val[index] in self.resp[self.index_sym[topic_id]] and  self.resp[self.index_sym[topic_id]][self.index_val[index]] != value and value != "-2147483648":

                                self.resp[self.index_sym[topic_id]][
                                    self.index_val[index]
                                ] = value
                                self.UpdateTick = True
                            elif self.index_val[index] not in self.resp[self.index_sym[topic_id]] and value != -2147483648:
                                self.resp[self.index_sym[topic_id]][
                                    self.index_val[index]
                                ] = value
                                self.UpdateTick = True
                            idx_flag = True
                        elif topic_id in self.dp_sym:
                            if self.depthvalue[index] in self.resp[self.dp_sym[topic_id]] and self.resp[self.dp_sym[topic_id]][
                                self.depthvalue[index]] != value and value != -2147483648:
                                self.resp[self.dp_sym[topic_id]][
                                    self.depthvalue[index]
                                ] = value
                                self.UpdateTick = True
                            elif self.depthvalue[index] not in self.resp[self.dp_sym[topic_id]] and  value != -2147483648:
                                self.resp[self.dp_sym[topic_id]][
                                    self.depthvalue[index]
                                ] = value
                                self.UpdateTick = True                                
                            dp_flag = True
                    if self.UpdateTick:
                        if sf_flag:
                            self.__response_output(
                                self.resp[self.scrips_sym[topic_id]], "scrips"
                            )
                        elif idx_flag:
                            self.__response_output(
                                self.resp[self.index_sym[topic_id]], "index"
                            )
                        elif dp_flag:
                            self.__response_output(
                                self.resp[self.dp_sym[topic_id]], "depth"
                            )

                elif data_type == 76:  # lite mode datafeed

                    offset += 1
                    topic_id = struct.unpack("H", data[offset : offset + 2])[0]
                    offset += 2
                    sf_flag, idx_flag = False, False
                    if topic_id in self.scrips_sym:

                        # for index in range(3):
                        value = struct.unpack(">i", data[offset : offset + 4])[0]
                        offset += 4
                        if value != self.resp[self.scrips_sym[topic_id]][self.data_val[0]] and value != -2147483648:
                            self.resp[self.scrips_sym[topic_id]][self.data_val[0]] = value
                            sf_flag = True
                            self.resp[self.scrips_sym[topic_id]]["type"] = "sf"
                            self.__response_output(
                                self.resp[self.scrips_sym[topic_id]], "scrips"
                            )
                    elif topic_id in self.index_sym:
                        value = struct.unpack(">i", data[offset : offset + 4])[0]
                        offset += 4
                        if value != self.resp[self.index_sym[topic_id]][self.index_val[0]] and value != -2147483648:
                            self.resp[self.index_sym[topic_id]][self.index_val[0]] = value
                            idx_flag = True
                            self.resp[self.index_sym[topic_id]]["type"] = "if"
                        
                            self.__response_output(
                                self.resp[self.index_sym[topic_id]], "index"
                            )
                        
        except Exception as e:
            self.data_logger.exception(e)


    def __response_msg(self, data: bytearray):
        """
        Processes the response message based on the response type and calls the corresponding function.

        Args:
            data (bytearray): The response data.

        """
        try:

            _, resp_type = struct.unpack("!HB", data[:3])
            if resp_type == 1:  # Authentication response
                self.__auth_resp(data)

            elif resp_type == 4:  # subsciption response
                self.__subscribe_resp(data)

            elif resp_type == 5:  # Unsubsciption response
                self.__unsubscribe_resp(data)

            elif resp_type == 6:  # Data Feed Response
                self.__datafeed_resp(data)

            elif resp_type == 7 or resp_type == 8:
                self.__resume_pause_resp(data, resp_type)

            elif resp_type == 12:  # Full Mode Data Response
                self.__lite_full_mode_resp(data)

        except Exception as e:
            self.data_logger.exception(e)

    def __symbol_conversion(self, symbolslst: list) -> dict:
        """
        Converts symbols to HSM symbol tokens and returns a dictionary of {hsmtoken: symbol}.

        Args:
            symbolslst (list): A list of symbols to convert.

        Returns:
            dict: A dictionary mapping HSM symbol tokens to symbols.
        """
        try:

            wrong_symbols = []
            symb_flag = False
            idx_dp_flag = False
            symbol_dict = {}
            total_symbols = len(symbolslst)
            if (
                len(self.scrips_per_channel[self.channel_num]) > self.symbol_limit
                or total_symbols > self.symbol_limit
                and len(self.scrips_per_channel[self.channel_num]) + total_symbols > self.symbol_limit
            ):
                self.On_error(
                    {
                        "code": defines.LIMIT_EXCEED_CODE,
                        "message": defines.LIMIT_EXCEED_MSG_5000,
                        "s": defines.ERROR,
                    }
                )
                return 

            symbol_chunks = [
                symbolslst[i : i + 500] for i in range(0, total_symbols, 500)
            ]
            conv = SymbolConversion(self.__access_token, self.data_type, self.log_path)
            for symbols in symbol_chunks:
                symbol_value = conv.symbol_to_hsmtoken(symbols)
                if symbol_value[3] != "":
                    self.On_error(
                    {
                        "code": defines.INVALID_CODE,
                        "message": symbol_value[3],
                        "s": defines.ERROR,
                        "type": defines.SUBS_TYPE
                    })
                    return
                symbol_dict.update(symbol_dict, **symbol_value[0])
                if type(symbol_value[1]) == list and len(symbol_value[1]) > 0:

                    wrong_symbols += symbol_value[1]
                    symb_flag = True
                if symbol_value[2] == True:
                    idx_dp_flag = True
            
                
            if symb_flag:
                self.On_error(
                    {
                        "code": defines.INVALID_CODE,
                        "message": defines.INVALID_SYMBOLS,
                        "s": defines.ERROR,
                        "type": defines.SUBS_TYPE,
                        "invalid_symbols": wrong_symbols,
                    }
                )
            if idx_dp_flag:
                self.On_error(
                    {
                        "code": defines.INVALID_CODE,
                        "message": defines.INDEX_DEPTH_ERROR_MESSAGE,
                        "s": defines.ERROR,
                        "type": defines.SUBS_TYPE,
                    }
                )

            return symbol_dict

        except Exception as e:
            self.data_logger.exception(e)

    def __channel_resume_pause(self):
        """
        Pauses the active channel and resumes the specified channel if necessary.

        If the WebSocket object (__ws_object) is not None and there is an active channel (active_channel)
        that is different from the specified channel (channelNum), the function creates and appends a pause message
        for the active channel to the message list. If the specified channel is already in the running_channels set,
        the function creates and appends a resume message for the specified channel to the message list.

        Finally, it updates the running_channels set and sets the active_channel to the specified channel (channelNum).

        """
        try:
            if (
                self.__ws_object is not None
                and self.active_channel is not None
                and self.active_channel != self.channel_num
            ):
                message = self.__channel_pause_msg(self.active_channel)
                # self.message.append(message)
                self.add_message(message)


                if self.channel_num in self.running_channels:
                    message = self.__channel_resume_msg(self.channel_num)
                    # self.message.append(message)
                    self.add_message(message)

            self.running_channels.add(self.channel_num)
            self.active_channel = self.channel_num

        except Exception as e:
            self.data_logger.exception(e)

    def channel_resume(self, channel: int) -> None:
        """
        Resumes the specified channel.

        Args:
            channel (int): The channel number to resume.
        """
        try:
            self.channel_num = channel
            self.__channel_resume_pause()

        except Exception as e:
            self.data_logger.exception(e)

    def On_message(self, message: dict) -> None:
        """
        Handles the received message.

        Args:
            message (str): The received message.
        """
        try:
            if self.OnMessage is not None:
                self.OnMessage(message)
            else:
                if self.write_to_file:
                    self.data_logger.debug(f"Response:{message}")
                else:
                    print(f"Response:{message}")

        except KeyError as e:
            key_name = str(e)
            self.data_logger.exception(e)
            self.On_error(f"KeyError: The key {key_name} is missing in the response.")

        except Exception as e:
            self.data_logger.exception(e)
            self.On_error(e)

    def __send_message(self, message: str) -> None:
        """
        Sends a message through the WebSocket connection.

        Args:
            message (str): The message to send.
        """
        with self.websocket_lock:
            if self.__ws_object is not None:

                self.__ws_object.send(message, opcode=websocket.ABNF.OPCODE_BINARY)


    def add_message(self, message):
        """
        Add a message to the list of messages and notify waiting threads.

        Args:
            message (str): The message to add to the list.
        """
        with self.message_lock:
            self.message.append(message)
            self.message_condition.notify()


    def __process_message_queue(self) -> None:
        """
        Processes the message queue by sending messages sequentially.
        """

        while not self.message_thread_stop_event.is_set():
                    with self.message_lock:
                        while not self.message_thread_stop_event.is_set() and  not self.message:  # Use a loop to handle spurious wake-ups
                            self.message_condition.wait()
                        if self.message_thread_stop_event.is_set():
                            break
                        # Once a message is available, pop it from the queue
                        message = self.message.pop(0)

                    # Send the message outside the lock to avoid blocking other threads
                    self.__send_message(message)


    def On_error(self, message: dict) -> None:
        """
        Handles the error message.

        Args:
            message (str): The error message.
        """
        if self.OnError is not None:
            self.OnError(message)
            self.data_logger.error(message)
        else:
            if self.write_to_file:
                self.data_logger.debug(f"ERROR Response:{message}")
            else:
                print(f"Error: {message}")




    def on_open(self) -> None:
        """
        Handles the open action.
        """
        try:
            if self.OnOpen:
                self.OnOpen()
        except Exception as e:
            self.data_logger.exception(e)
            self.On_error(e)


    def connect(self) -> None:
        """
        Establishes a connection to the WebSocket.

        If the WebSocket object is not already initialized, this method will create the
        WebSocket connection.

        """
        try:
            if self.__ws_object is None:
                self.__init_connection()
                time.sleep(2)
            self.on_open()

        except Exception as e:
            self.data_logger.exception(e)
            self.On_error(e)
            

    def on_close(self, message: dict) -> None:
        """
        Handles the close event.

        Args:
            message (dict): The close message .
        """
        try:
            if self.OnClose:
                self.OnClose(message)
            else:
                print(f"Response: {message}")
        except Exception as e:
            self.data_logger.exception(e)
            self.On_error(e)


    def __on_open(self, ws) -> None:
        """
        Handles the WebSocket connection open event.

        Args:
            ws (websocket.WebSocketApp): The WebSocket object.
        """
        if self.__ws_object is None:
            self.message = []
            self.__ws_object = ws
            self.message_thread = Thread(target=self.__process_message_queue)
            self.ping_thread = Thread(target=self.__ping)
            self.message_thread_stop_event = threading.Event()  # Event to signal stopping
            self.message_thread.start()
            self.ping_thread.start()
            message = self.__access_token_msg()
            # self.message.append(message)
            self.add_message(message)
            self.reconnect_attempts = 0
            self.reconnect_delay = 0
            if self.lite:
                message = self.__lite_mode_msg()
                # self.message.append(message)
                self.add_message(message)
            else:
                message = self.__full_mode_msg()
                # self.message.append(message)
                self.add_message(message)


    def __on_close(self, ws, close_code, close_reason):
        """
        Handle the WebSocket connection close event.

        Args:
            ws (WebSocket): The WebSocket object.
            close_code (int): The code indicating the reason for closure.
            close_reason (str): The reason for closure.

        Returns:
            dict: A dictionary containing the response code, message, and s.
        """
        if self.restart_flag:
            if self.reconnect_attempts < self.max_reconnect_attempts:

                if self.write_to_file:
                    self.data_logger.debug(
                        f"Response:{f'Attempting reconnect {self.reconnect_attempts+1} of {self.max_reconnect_attempts}...'}"
                    )
                else:
                    print(
                        f"Attempting reconnect {self.reconnect_attempts+1} of {self.max_reconnect_attempts}..."
                    )

                if (self.reconnect_attempts) % 5 == 0:
                    self.reconnect_delay += 5
                time.sleep(self.reconnect_delay)
                self.reconnect_attempts += 1

                self.__ws_object = None
                self.scrips_per_channel[self.channel_num] = []
                self.symbol_token = {}
                self.scrips_sym = {}
                self.index_sym = {}
                self.dp_sym = {}
                self.resp = {}

                self.connect()
            else:
                if self.write_to_file:
                    self.data_logger.debug(
                        f"Response:{'Max reconnect attempts reached. Connection abandoned.'}"
                    )
                else:
                    print("Max reconnect attempts reached. Connection abandoned.")
        else:

            self.on_close(
                {
                    "code": defines.SUCCESS_CODE,
                    "message": defines.CONNECTION_CLOSED,
                    "s": defines.SUCCESS,
                }
            )

    def __ping(self):
        while (
            self.__ws_object is not None
            and self.__ws_object.sock
            and self.__ws_object.sock.connected
        ):
            self.__ws_object.send(bytes([0, 1, 11]), opcode=websocket.ABNF.OPCODE_BINARY)
            time.sleep(10)

    def __init_connection(self):
        """
        Initializes the WebSocket connection and starts the WebSocketApp.

        The method creates a WebSocketApp object with the specified URL and sets the appropriate event handlers.
        It then starts the WebSocketApp in a separate thread.
        """
        try:
            if  self.access_token_to_hsmtoken() and self.__valid_token :
                if self.write_to_file:
                    self.background_flag = True  
                ws = websocket.WebSocketApp(
                    self.__url,
                    on_message=lambda ws, msg: self.__response_msg(msg),
                    on_error=lambda ws, msg: self.On_error(msg),
                    on_close=lambda ws, close_code, close_reason: self.__on_close(
                        ws, close_code, close_reason
                    ),
                    on_open=lambda ws: self.__on_open(ws),
                )

                self.ws_thread = Thread(target=ws.run_forever)
                self.ws_thread.daemon = self.background_flag
                self.ws_thread.start()

        except Exception as e:
            self.data_logger.exception(e)

    def close_connection(self) -> None:
        """
        Closes the WebSocket connection 

        """

        if self.__ws_object:
            self.restart_flag = False
            self.__ws_object.close()
            self.__ws_object = None
            self.ws_thread.join()
            self.message_thread_stop_event.set()
            with self.message_lock:
                self.message_condition.notify()  # Notify the thread to wake up
            self.message_thread.join()
            self.ping_thread.join()
            self.__ws_run = False
            self.scrips_per_channel[self.channel_num] = []
            self.scrips_sym = {}
            self.index_sym = {}
            self.dp_sym = {}
            self.resp = {}


    def keep_running(self):
        """
        Starts an infinite loop to keep the program running.

        """
        self.__ws_run = True
        self.infy_loop = Thread(target=self.infinite_loop)
        self.infy_loop.start()

    def infinite_loop(self):
        while self.__ws_run:
            time.sleep(0.5)


    def is_connected(self):
        """
        Check if the websocket is connected.

        Returns:
            bool: True if the websocket is connected, False otherwise.
        """
        if self.__ws_object:
            return True
        else:
            return False

    def unsubscribe(
        self, symbols: list, data_type: str = "SymbolUpdate", channel: int = 11
    ):
        """
        Unsubscribes from real-time data updates for the specified symbols.

        Args:
            symbols (list): A list of symbols to unsubscribe from.
            data_type (str, optional): The type of data to unsubscribe from. Defaults to "SymbolUpdate".
            channel (int, optional): The channel to use for unsubscription. Defaults to 1.
        """
        try:
            if self.__valid_token:
                self.data_type = data_type
                self.symbols = symbols
                self.channel_num = channel
                self.__channel_resume_pause()
                self.channel_symbol = self.__symbol_conversion(symbols)
                self.unsub_symbol = list(self.channel_symbol.keys())
                for symb in self.unsub_symbol:
                    if symb not in self.scrips_count[self.channel_num]:
                        self.unsub_symbol.remove(symb)

                if len(self.unsub_symbol) != 0:
                    total_symbols = len(self.unsub_symbol)
                    symbol_chunks = [
                        self.unsub_symbol[i : i + 1500] for i in range(0, total_symbols, 1500)
                    ]
                    for symbols in symbol_chunks:
                        message = self.__unsubscription_msg(symbols)
                        # self.message.append(message)
                        self.add_message(message)

                else:
                    self.On_error(
                        {
                            "code": defines.INVALID_CODE,
                            "message": defines.INVALID_SYMBOLS,
                            "s": defines.ERROR,
                        }
                    )

        except Exception as e:
            self.data_logger.exception(e)

    def subscribe(
        self, symbols: list, data_type: str = "SymbolUpdate", channel: int = 11
    ):
        """
        Subscribes to real-time data updates for the specified symbols.

        Args:
            symbols (list): A list of symbols to subscribe to.
            data_type (str, optional): The type of data to subscribe to. Defaults to "SymbolUpdate".
            channel (int, optional): The channel to use for subscription. Defaults to 1.
        """
        try:
            if self.__valid_token:
                self.data_type = data_type
                self.symbols = symbols
                self.channel_num = channel
                self.__channel_resume_pause()
                self.channel_symbol = self.__symbol_conversion(symbols)
                if self.channel_symbol is None:
                    return
                if len(self.symbol_token) + len(self.channel_symbol) > 5000:
                    self.On_error(
                        {
                            "code": defines.LIMIT_EXCEED_CODE,
                            "message": defines.LIMIT_EXCEED_MSG_5000,
                            "s": defines.ERROR,
                        }
                    )
                    return
                self.symbol_token.update(self.symbol_token, **self.channel_symbol)
                self.scrips_count[self.channel_num] = list(self.channel_symbol.keys())
                total_symbols = len(self.scrips_count[self.channel_num])
                symbol_chunks = [
                    self.scrips_count[self.channel_num][i : i + 1500]
                    for i in range(0, total_symbols, 1500)
                ]
                for symbols in symbol_chunks:
                    message = self.__subscription_msg(symbols)
                    # self.message.append(message)
                    time.sleep(0.5)
                    self.add_message(message)


        except Exception as e:
            self.data_logger.exception(e)
//===== fyers_apiv3/FyersWebsocket/defines.py=====//AUTH_ERROR_CODE = 11001
SUBS_ERROR_CODE = 11011
UNSUBS_ERROR_CODE = 11012
RESUME_ERROR_CODE = 11031
RESUME_ERROR_CODE = 11032
MODE_ERROR_CODE = 12001
SUCCESS_CODE = 200
INVALID_CODE = -300
TOKEN_EXPIRED = -99
LIMIT_EXCEED_CODE = -99
LIMIT_EXCEED_MSG_5000 = "Please provide less than 5000 symbols"
TOKEN_EXPIRED_MSG = "Token is expired"
INVALID_TOKEN = "Please provide valid token"
SUCCESS = "ok"
ERROR = "error"
AUTH_SUCCESS = "Authentication done"
AUTH_FAIL = "Authentication failed"
SUBSCRIBE_SUCCESS = "Subscribed"
SUBSCRIBE_FAIL = "subscription failed"
UNSUBSCRIBE_SUCCESS = "Unsubscribed"
UNSUBSCRIBE_FAIL = "unsubscription failed"
LITE_MODE = "Lite Mode On"
FULL_MODE = "Full Mode On"
MODE_CHANGE_ERROR = "Mode change failed"
CHANNEL_PAUSED = "Channel Paused"
CHANNEL_RESUMED = "Channel Resumed"
CHANNEL_CHANGE_FAIL = "Mode change failed"
INVALID_SYMBOLS = "Please provide a valid symbol"
CONNECTION_CLOSED = "Connection Closed"
INDEX_DEPTH_ERROR_MESSAGE = "Index does not have market depth"
AUTH_TYPE = "cn"
SUBS_TYPE = "sub"
UNSUBS_TYPE = "unsub"
LITE_MODE_TYPE = "lit"
FULL_MODE_TYPE = "ful"
CH_PAUSE_TYPE = "cp"
CH_RESUME_TYPE = "cr"//===== fyers_apiv3/FyersWebsocket/msg_pb2.py=====//# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: msg.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tmsg.proto\x1a\x1egoogle/protobuf/wrappers.proto\"\xbb\x01\n\x0bMarketLevel\x12*\n\x05price\x18\x01 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12)\n\x03qty\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\x12*\n\x04nord\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\x12)\n\x03num\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\"\x95\x01\n\x05\x44\x65pth\x12)\n\x03tbq\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12)\n\x03tsq\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x1a\n\x04\x61sks\x18\x03 \x03(\x0b\x32\x0c.MarketLevel\x12\x1a\n\x04\x62ids\x18\x04 \x03(\x0b\x32\x0c.MarketLevel\"\xb7\x02\n\x05Quote\x12(\n\x03ltp\x18\x01 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12)\n\x03ltt\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\x12)\n\x03ltq\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\x12)\n\x03vtt\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12.\n\x08vtt_diff\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12(\n\x02oi\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12)\n\x04ltpc\x18\x07 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\"\x88\x03\n\rExtendedQuote\x12(\n\x03\x61tp\x18\x01 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12\'\n\x02\x63p\x18\x02 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12(\n\x02lc\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\x12(\n\x02uc\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\x12\'\n\x02yh\x18\x05 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12\'\n\x02yl\x18\x06 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12)\n\x03poi\x18\x07 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12)\n\x04oich\x18\x08 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12(\n\x02pc\x18\t \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\"\x88\x02\n\nDailyQuote\x12\'\n\x02\x64o\x18\x01 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12\'\n\x02\x64h\x18\x02 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12\'\n\x02\x64l\x18\x03 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12\'\n\x02\x64\x63\x18\x04 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12*\n\x04\x64hoi\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12*\n\x04\x64loi\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\"\x8e\x02\n\x05OHLCV\x12)\n\x04open\x18\x01 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12)\n\x04high\x18\x02 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12(\n\x03low\x18\x03 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12*\n\x05\x63lose\x18\x04 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12,\n\x06volume\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\x12+\n\x05\x65poch\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\"\x1d\n\tSymDetail\x12\x10\n\x08ticksize\x18\x01 \x01(\t\"\xcd\x02\n\nMarketFeed\x12\x15\n\x05quote\x18\x01 \x01(\x0b\x32\x06.Quote\x12\x1a\n\x02\x65q\x18\x02 \x01(\x0b\x32\x0e.ExtendedQuote\x12\x17\n\x02\x64q\x18\x03 \x01(\x0b\x32\x0b.DailyQuote\x12\x15\n\x05ohlcv\x18\x04 \x01(\x0b\x32\x06.OHLCV\x12\x15\n\x05\x64\x65pth\x18\x05 \x01(\x0b\x32\x06.Depth\x12/\n\tfeed_time\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12/\n\tsend_time\x18\x07 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\r\n\x05token\x18\x08 \x01(\t\x12\x13\n\x0bsequence_no\x18\t \x01(\x04\x12\x10\n\x08snapshot\x18\n \x01(\x08\x12\x0e\n\x06ticker\x18\x0b \x01(\t\x12\x1d\n\tsymdetail\x18\x0c \x01(\x0b\x32\n.SymDetail\"\xbe\x01\n\rSocketMessage\x12\x1a\n\x04type\x18\x01 \x01(\x0e\x32\x0c.MessageType\x12(\n\x05\x66\x65\x65\x64s\x18\x02 \x03(\x0b\x32\x19.SocketMessage.FeedsEntry\x12\x10\n\x08snapshot\x18\x03 \x01(\x08\x12\x0b\n\x03msg\x18\x04 \x01(\t\x12\r\n\x05\x65rror\x18\x05 \x01(\x08\x1a\x39\n\nFeedsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x1a\n\x05value\x18\x02 \x01(\x0b\x32\x0b.MarketFeed:\x02\x38\x01*\x86\x01\n\x0bMessageType\x12\x08\n\x04ping\x10\x00\x12\t\n\x05quote\x10\x01\x12\x12\n\x0e\x65xtended_quote\x10\x02\x12\x0f\n\x0b\x64\x61ily_quote\x10\x03\x12\x10\n\x0cmarket_level\x10\x04\x12\t\n\x05ohlcv\x10\x05\x12\t\n\x05\x64\x65pth\x10\x06\x12\x07\n\x03\x61ll\x10\x07\x12\x0c\n\x08response\x10\x08\x42\nZ\x08/gencodeb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'msg_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z\010/gencode'
  _globals['_SOCKETMESSAGE_FEEDSENTRY']._loaded_options = None
  _globals['_SOCKETMESSAGE_FEEDSENTRY']._serialized_options = b'8\001'
  _globals['_MESSAGETYPE']._serialized_start=2197
  _globals['_MESSAGETYPE']._serialized_end=2331
  _globals['_MARKETLEVEL']._serialized_start=46
  _globals['_MARKETLEVEL']._serialized_end=233
  _globals['_DEPTH']._serialized_start=236
  _globals['_DEPTH']._serialized_end=385
  _globals['_QUOTE']._serialized_start=388
  _globals['_QUOTE']._serialized_end=699
  _globals['_EXTENDEDQUOTE']._serialized_start=702
  _globals['_EXTENDEDQUOTE']._serialized_end=1094
  _globals['_DAILYQUOTE']._serialized_start=1097
  _globals['_DAILYQUOTE']._serialized_end=1361
  _globals['_OHLCV']._serialized_start=1364
  _globals['_OHLCV']._serialized_end=1634
  _globals['_SYMDETAIL']._serialized_start=1636
  _globals['_SYMDETAIL']._serialized_end=1665
  _globals['_MARKETFEED']._serialized_start=1668
  _globals['_MARKETFEED']._serialized_end=2001
  _globals['_SOCKETMESSAGE']._serialized_start=2004
  _globals['_SOCKETMESSAGE']._serialized_end=2194
  _globals['_SOCKETMESSAGE_FEEDSENTRY']._serialized_start=2137
  _globals['_SOCKETMESSAGE_FEEDSENTRY']._serialized_end=2194
# @@protoc_insertion_point(module_scope)
//===== fyers_apiv3/FyersWebsocket/order_ws.py=====//from typing import Any, Callable, Dict, Optional
from pkg_resources import resource_filename
import websocket
from threading import Thread
import logging
import threading
import time
import json
from fyers_apiv3.FyersWebsocket import defines
from fyers_apiv3.fyers_logger import FyersLogger


class FyersOrderSocket:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        access_token: str,
        write_to_file: Optional[bool] = False,
        log_path: Optional[str] = None,
        on_trades : Optional[Callable] = None,
        on_positions: Optional[Callable] = None,
        on_orders: Optional[Callable] = None,
        on_general: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_connect: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        reconnect : Optional[Callable] = True,
        reconnect_retry: int = 5 
    ) -> None:
        """
        Initializes the class instance.

        Args:
            access_token (str): The access token to authenticate with.
            write_to_file (bool, optional): Flag indicating whether to save data to a file. Defaults to False.
            log_path (str, optional): The path to the log file. Defaults to None.
            on_trades (callable, optional): Callback function for trade events. Defaults to None.
            on_positions (callable, optional): Callback function for position events. Defaults to None.
            on_orders (callable, optional): Callback function for order events. Defaults to None.
            on_general (callable, optional): Callback function for general events. Defaults to None.
            on_error (callable, optional): Callback function for error events. Defaults to None.
            on_connect (callable, optional): Callback function for connect events. Defaults to None.
            on_close (callable, optional): Callback function for close events. Defaults to None.
            reconnect (bool, optional): Flag indicating whether to attempt reconnection on disconnection. Defaults to True.
        """
        self.__access_token = access_token
        self.log_path = log_path
        self.__ws_object = None
        self.__ws_run = False
        self.ping_thread = None
        self.write_to_file = write_to_file
        self.background_flag = False
        self.reconnect_delay = 0
        self.ontrades = on_trades
        self.onposition = on_positions
        self.restart_flag = reconnect
        self.onorder = on_orders
        self.ongeneral = on_general
        self.onerror = on_error
        self.onopen = on_connect
        self.max_reconnect_attempts = 50
        self.reconnect_attempts = 0
        if reconnect_retry < self.max_reconnect_attempts:
            self.max_reconnect_attempts = reconnect_retry

        self.onclose = on_close
        self.__ws_object = None
        self.running_thread=None
        self.__url = "wss://socket.fyers.in/trade/v3"
        file_path = resource_filename('fyers_apiv3.FyersWebsocket', 'map.json')
        with open(file_path, "r") as file:
            # Imported json file
            mapper = json.load(file)
        self.position_mapper = mapper["position_mapper"]
        self.order_mapper = mapper["order_mapper"]
        self.trade_mapper = mapper["trade_mapper"]


        if log_path:
            self.order_logger = FyersLogger(
                "FyersDataSocket",
                "DEBUG",
                stack_level=2,
                logger_handler=logging.FileHandler(log_path + "/fyersOrderSocket.log"),
            )
        else:
            self.order_logger = FyersLogger(
                "FyersDataSocket",
                "DEBUG",
                stack_level=2,
                logger_handler=logging.FileHandler("fyersOrderSocket.log"),
            )
        self.websocket_task = None

        self.write_to_file = write_to_file
        self.background_flag = False
        self.socket_type = {
            "OnOrders": "orders",
            "OnTrades": "trades",
            "OnPositions": "positions",
            "OnGeneral": ["edis", "pricealerts", "login"],
        }

    def __parse_position_data(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses position data from a message and returns it in a specific format.

        Args:
            msg (str): The message containing position data.

        Returns:
            Dict[str, Any] : The parsed position data in a specific format.

        """
        try:
            position_data = {}
            for key , value in self.position_mapper.items():
                if key in msg["positions"]:
                    position_data[value] = msg["positions"][key]
            
            # Add id_fyers only if the key is present
            if "id_fyers" in msg["positions"]:
                position_data["id_fyers"] = msg["positions"]["id_fyers"]

            return { "s": msg["s"], "positions": position_data}

        except Exception as e:
            self.order_logger.error(e)

    def __parse_trade_data(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses trade data from a message and returns it in a specific format.

        Args:
            msg (str): The message containing trade data.

        Returns:
            Dict[str, Any] : The parsed trade data in a specific format.

        """
        try:
            trade_data = {}
            for key , value in self.trade_mapper.items():
                if key in msg["trades"]:
                    trade_data[value] = msg["trades"][key]
            
            # Add id_fyers only if the key is present
            if "id_fyers" in msg["trades"]:
                trade_data["id_fyers"] = msg["trades"]["id_fyers"]

            return { "s": msg["s"], "trades": trade_data}

        except Exception as e:
            self.order_logger.error(e)

    def __parse_order_data(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses order update data from a dictionary and returns it in a specific format.

        Args:
            msg (Dict[str, Any]): The dictionary containing order update data.

        Returns:
            Dict[str, Any]: The parsed order update data in a specific format.
        """
        try:
            order_data = {}
            for key , value in self.order_mapper.items():
                if key in msg["orders"]:
                    order_data[value] = msg["orders"][key]
                    
            # Add id_fyers only if the key is present
            if "id_fyers" in msg["orders"]:
                order_data["id_fyers"] = msg["orders"]["id_fyers"]
            
            return { "s": msg["s"], "orders": order_data}

        except Exception as e:
            self.order_logger.error(e)

    def on_trades(self, message):
        try:
            if self.ontrades is not None:
                self.ontrades(message)
            else:
                print(f"Trade : {message}")
        except Exception as e:
            self.order_logger.error(e)
            self.On_error(e)

    def on_positions(self, message):
        try:
            if self.onposition is not None:
                self.onposition(message)
            else:
                print(f"Position : {message}")
        except Exception as e:
            self.order_logger.error(e)
            self.On_error(e)

    def on_order(self, message):
        try:
            if self.onorder is not None:
                self.onorder(message)
            else:
                print(f"Order : {message}")
        except Exception as e:
            self.order_logger.error(e)
            self.On_error(e)

    def on_general(self, message):
        try:
            if self.ongeneral is not None:
                self.ongeneral(message)
            else:
                print(f"General : {message}")
        except Exception as e:
            self.order_logger.error(e)
            self.On_error(e)

    def __on_message(self, message: Dict[str, Any]):
        """
        Parses the response data based on its content.

        Args:
            message (str): The response message to be parsed.

        Returns:
            Any: The parsed response data.
        """
        try:
            if message != "pong":
                response = json.loads(message)
                if "orders" in response:
                    response = self.__parse_order_data(response)
                    self.on_order(response)
                elif "positions" in response:
                    response = self.__parse_position_data(response)
                    self.on_positions(response)
                elif "trades" in response:
                    response = self.__parse_trade_data(response)
                    self.on_trades(response)
                else:
                    self.on_general(response)
                
                if self.write_to_file:
                    self.order_logger.debug(f"Response:{response}")


        except Exception as e:
            self.order_logger.error(e)
            self.On_error(e)

    def On_error(self, message: str) -> None:
        """
        Callback function for handling error events.

        Args:
            message (str): The error message.

        """
        if self.onerror is not None:
            self.onerror(message)
            self.order_logger.error(message)
        else:
            if self.write_to_file:
                self.order_logger.debug(f"Response:{message}")
            else:
                print(f"Error Response : {message}")

    def __on_open(self, ws):
        try:
            if self.__ws_object is None:
                self.__ws_object = ws
                self.ping_thread = threading.Thread(target=self.__ping)
                self.ping_thread.start()
                self.reconnect_attempts = 0
                self.reconnect_delay = 0

        except Exception as e:
            self.order_logger.error(e)
            self.On_error(e)

    def __on_close(self, ws, close_code=None, close_reason=None):
        """
        Handle the WebSocket connection close event.

        Args:
            ws (WebSocket): The WebSocket object.
            close_code (int): The code indicating the reason for closure.
            close_reason (str): The reason for closure.

        Returns:
            dict: A dictionary containing the response code, message, and s.
        """
        try:
            if self.restart_flag:
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    if self.write_to_file:
                        self.order_logger.debug(
                            f"Response:{f'Attempting reconnect {self.reconnect_attempts} of {self.max_reconnect_attempts}...'}"
                        )
                    else:
                        print(
                            f"Attempting reconnect {self.reconnect_attempts+1} of {self.max_reconnect_attempts}..."
                        )
                    if (self.reconnect_attempts) % 5 == 0:
                        self.reconnect_delay += 5
                    time.sleep(self.reconnect_delay)
                    self.reconnect_attempts += 1

                    self.__ws_object = None
                    self.connect()
                else:
                    if self.write_to_file:
                        self.order_logger.debug(
                            f"Response:{'Max reconnect attempts reached. Connection abandoned.'}"
                        )
                    else:
                        print("Max reconnect attempts reached. Connection abandoned.")
            else:

                self.on_close(
                    {
                        "code": defines.SUCCESS_CODE,
                        "message": defines.CONNECTION_CLOSED,
                        "s": defines.SUCCESS,
                    }
                )
        except Exception as e:
            self.order_logger.error(e)
            self.On_error(e)

    def __ping(self) -> None:
        """
        Sends periodic ping messages to the server to maintain the WebSocket connection.

        The method continuously sends "__ping" messages to the server at a regular interval
        as long as the WebSocket connection is active.

        """

        while (
            self.__ws_object is not None
            and self.__ws_object.sock
            and self.__ws_object.sock.connected
        ):
            self.__ws_object.send("ping")
            time.sleep(10)

    def on_close(self, message: dict) -> None:
        """
        Handles the close event.

        Args:
            message (dict): The close message .
        """

        if self.onclose:
            self.onclose(message)
        else:
            print(f"Response: {message}")

    def on_open(self) -> None:
        """
        Performs initialization and waits before executing further actions.
        """
        try:
            if self.onopen:
                self.onopen()
        except Exception as e:
            self.On_error(e)

    def is_connected(self):
        """
        Check if the websocket is connected.

        Returns:
            bool: True if the websocket is connected, False otherwise.
        """
        if self.__ws_object:
            return True
        else:
            return False
        

    def __init_connection(self):
        """
        Initializes the WebSocket connection and starts the WebSocketApp.

        The method creates a WebSocketApp object with the specified URL and sets the appropriate event handlers.
        It then starts the WebSocketApp in a separate thread.
        """
        try:
            if self.__ws_object is None:
                if self.write_to_file:
                    self.background_flag = True
                header = {"authorization": self.__access_token}
                ws = websocket.WebSocketApp(
                    self.__url,
                    header=header,
                    on_message=lambda ws, msg: self.__on_message(msg),
                    on_error=lambda ws, msg: self.On_error(msg),
                    on_close=lambda ws, close_code, close_reason: self.__on_close(
                        ws, close_code, close_reason
                    ),
                    on_open=lambda ws: self.__on_open(ws),
                )
                self.t = Thread(target=ws.run_forever) 
                self.t.daemon = self.background_flag
                self.t.start()

        except Exception as e:
            self.order_logger.error(e)

    def keep_running(self):
        """
        Starts an infinite loop to keep the program running.

        """
        self.__ws_run = True
        self.running_thread = Thread(target=self.infinite_loop)
        self.running_thread.start()

    def stop_running(self):
        self.__ws_run = False

    def infinite_loop(self):
        while self.__ws_run:
            time.sleep(0.5)

    def connect(self) -> None:
        """
        Establishes a connection to the WebSocket.

        If the WebSocket object is not already initialized, this method will create the
        WebSocket connection.

        """
        if self.__ws_object is None:
            self.__init_connection()
            time.sleep(2)
        self.on_open()

            
    def close_connection(self):
        """
        Closes the WebSocket connection 

        """
        if self.__ws_object is not None:
            self.restart_flag = False
            self.__ws_object.close()
            self.__ws_object = None
            self.__ws_run = None
            self.running_thread.join()
            self.t.join()
            self.ping_thread.join()

    def subscribe(self, data_type: str) -> None:
        """
        Subscribes to real-time updates of a specific data type.

        Args:
            data_type (str): The type of data to subscribe to, such as orders, position, or holdings.


        """

        try:
            if self.__ws_object is not None:
                self.data_type = []
                for elem in data_type.split(","):
                    if isinstance(self.socket_type[elem], list):
                        self.data_type.extend(self.socket_type[elem])
                    else:
                        self.data_type.append(self.socket_type[elem])
                                
                message = json.dumps(
                    {"T": "SUB_ORD", "SLIST": self.data_type, "SUB_T": 1}
                )
                self.__ws_object.send(message)

        except Exception as e:
            self.order_logger.error(e)

    def unsubscribe(self, data_type: str) -> None:
        """
        Unsubscribes from real-time updates of a specific data type.

        Args:
            data_type (str): The type of data to unsubscribe from, such as orders, position, holdings or general.

        """

        try:
            if self.__ws_object is not None:
                self.data_type = [
                    self.socket_type[(type)] for type in data_type.split(",")
                ]
                message = json.dumps(
                    {"T": "SUB_ORD", "SLIST": self.data_type, "SUB_T": -1}
                )
                self.__ws_object.send(message)

        except Exception as e:
            self.order_logger.error(e)
//===== fyers_apiv3/FyersWebsocket/tbt_ws.py=====//from typing import Any, Callable, Dict, Optional
from pkg_resources import resource_filename
import websocket
from threading import Thread
import logging
import threading
import time
import json
from fyers_apiv3.FyersWebsocket import defines
from fyers_apiv3.fyers_logger import FyersLogger
from typing import Set, List
import fyers_apiv3.FyersWebsocket.msg_pb2 as protomsg
from enum import Enum
import requests

## Models and definitions

def getUrl(access_token: str):
    """
    Get the URL for the WebSocket connection.

    Args:
        access_token (str): The access token to authenticate with. Format: APPID:SECRET_KEY

    Returns:
        str: The URL for the WebSocket connection.
    """
    data = requests.get('https://api-t1.fyers.in/indus/home/tbtws', headers={'Authorization': f'{access_token}'})
    if data.status_code == 200:
        return data.json()['data']['socket_url']
    return "wss://rtsocket-api.fyers.in/versova"

class SubscriptionModes(Enum):
    DEPTH = "depth"

class Depth:
    def __init__(self):
        self.tbq: int = 0
        self.tsq: int = 0
        self.bidprice: List[float] = [0.0] * 50
        self.askprice: List[float] = [0.0] * 50
        self.bidqty: List[float] = [0] * 50
        self.askqty: List[float] = [0] * 50
        self.bidordn: List[float] = [0] * 50
        self.askordn: List[float] = [0] * 50
        self.snapshot: bool = False
        self.timestamp: int = 0
        self.sendtime: int = 0
        self.seqNo: int = 0

    def __str__(self):
        return (f"Depth{{ts: {self.timestamp}, "
                f"send_ts: {self.sendtime}, "
                f"tbq: {self.tbq}, tsq: {self.tsq}, "
                f"bidprice: {self.bidprice}, askprice: {self.askprice}, "
                f"bidqty: {self.bidqty}, askqty: {self.askqty}, "
                f"bidordn: {self.bidordn}, askordn: {self.askordn}, "
                f"snapshot: {self.snapshot}, sNo: {self.seqNo} }}")
    
    def _addDepth(self, currdata: protomsg.MarketFeed, isSnapshot: bool):
        if currdata.HasField('depth'):
            self.snapshot = isSnapshot
            if currdata.depth.HasField('tbq'):
                self.tbq = currdata.depth.tbq.value

            if currdata.depth.HasField('tsq'):
                self.tsq = currdata.depth.tsq.value

            if currdata.depth.asks is not None:
                for i in range(len(currdata.depth.asks)):
                    if currdata.depth.asks[i].HasField('price'):
                        self.askprice[i] = currdata.depth.asks[i].price.value / 100

                    if currdata.depth.asks[i].HasField('qty'):
                        self.askqty[i] = currdata.depth.asks[i].qty.value

                    if currdata.depth.asks[i].HasField('nord'):
                        self.askordn[i] = currdata.depth.asks[i].nord.value
                        
            if currdata.depth.bids is not None:
                for i in range(len(currdata.depth.bids)):
                    if currdata.depth.bids[i].HasField('price'):
                        self.bidprice[i] = currdata.depth.bids[i].price.value / 100

                    if currdata.depth.bids[i].HasField('qty'):
                        self.bidqty[i] = currdata.depth.bids[i].qty.value

                    if currdata.depth.bids[i].HasField('nord'):
                        self.bidordn[i] = currdata.depth.bids[i].nord.value
            
            self.timestamp = currdata.feed_time.value
            self.sendtime = currdata.send_time.value
            self.seqNo = currdata.sequence_no

class SubscriptionInfo:
    def __init__(self) -> None:
        self._symbols: Dict[str, Set[str]] = {}
        self._modeInfo: Dict[str, SubscriptionModes] = {}
        self._activeChannels: Set[str] = set()

    def subscribe(self, symbols: Set[str], channelNo: str, mode: SubscriptionModes) -> None:
        if channelNo in self._symbols:
            self._symbols[channelNo].update(symbols)
        else:
            self._symbols[channelNo] = set(symbols)
        self._modeInfo[channelNo] = mode

    def unsubscribe(self, symbols: Set[str], channelNo: str) -> None:
        if channelNo in self._symbols:
            self._symbols[channelNo].difference_update(symbols)
            if not self._symbols[channelNo]:
                del self._symbols[channelNo]

    def updateChannels(self, pauseChannels: Set[str], resumeChannels: Set[str]) -> None:
        self._activeChannels.difference_update(pauseChannels)
        self._activeChannels.update(resumeChannels)

    def updateMode(self, modeConfig: Dict[str, SubscriptionModes]) -> None:
        for channelNo, mode in modeConfig.items():
            self._modeInfo[channelNo] = mode

    def getSymbolsInfo(self, chanNo: str) -> Set[str]:
        return self._symbols[chanNo]

    def getModeInfo(self, chanNo: str) -> SubscriptionModes:
        return self._modeInfo[chanNo]

    def getChannelInfo(self) -> Set[str]:
        return self._activeChannels
    

class DataStore:
  depth: Dict[str, Depth] = {}

  def updateDepth(self, packet: protomsg.SocketMessage, cb: Optional[Callable], diffOnly: bool):
    if packet.feeds is not None:
        for _, value in packet.feeds.items():
            symbol = value.ticker
            if symbol not in self.depth:
                self.depth[symbol] = Depth()
            if not diffOnly:
                self.depth[symbol]._addDepth(value, packet.snapshot)
                cb(symbol, self.depth[symbol])     
            else:
                depth = Depth() 
                depth._addDepth(value, packet.snapshot)
                cb(symbol, depth)     


class FyersTbtSocket:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        access_token: str,
        write_to_file: Optional[bool] = False,
        log_path: Optional[str] = None,
        on_depth_update: Optional[Callable] = None,
        on_error_message:   Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_connect: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        on_open: Optional[Callable] = None,
        reconnect : Optional[Callable] = True,
        diff_only: bool = False,
        reconnect_retry: int = 5 
    ) -> None:
        """
        Initializes the class instance.

        Args:
            access_token (str): The access token to authenticate with.
            write_to_file (bool, optional): Flag indicating whether to save data to a file. Defaults to False.
            log_path (str, optional): The path to the log file. Defaults to None.
            on_depth_update (callable, optional): Callback function for 50 depth events. Defaults to None.
            on_error_message (callable, optional): Callback function for error msg received from server. Defaults to None.
            on_error (callable, optional): Callback function for error events. Defaults to None.
            on_connect (callable, optional): Callback function for connect events. Defaults to None.
            on_close (callable, optional): Callback function for close events. Defaults to None.
            on_open (callable, optional): Callback function for open events. Defaults to None.
            reconnect (bool, optional): Flag indicating whether to attempt reconnection on disconnection. Defaults to True.
        """
        self._datastore = DataStore()
        self._subsinfo = SubscriptionInfo()
        self.__access_token = access_token
        self.log_path = log_path
        self.__ws_object = None
        self.__ws_run = False
        self.ping_thread = None
        self.write_to_file = write_to_file
        self.background_flag = False
        self.reconnect_delay = 0
        self.onDepthUpdate = on_depth_update
        self.onErrorMsg = on_error_message
        self.restart_flag = reconnect
        self.onerror = on_error
        self.onopen = on_connect
        self.max_reconnect_attempts = 50
        self.reconnect_attempts = 0
        self.diff_only = diff_only
        if reconnect_retry < self.max_reconnect_attempts:
            self.max_reconnect_attempts = reconnect_retry

        self.onclose = on_close
        self.onopen = on_open
        self.__ws_object = None
        self.running_thread=None
        self.__url = getUrl(access_token)

        if log_path:
            self.tbtlogger = FyersLogger(
                "FyersTbtSocket",
                "DEBUG",
                stack_level=2,
                logger_handler=logging.FileHandler(log_path + "/fyersTBTSocket.log"),
            )
        else:
            self.tbtlogger = FyersLogger(
                "FyersTbtSocket",
                "DEBUG",
                stack_level=2,
                logger_handler=logging.FileHandler("fyersTBTSocket.log"),
            )
        self.websocket_task = None

        self.write_to_file = write_to_file
        self.background_flag = False
        
    def subscribe(self, symbol_tickers: Set[str], channelNo: str, mode: SubscriptionModes) -> None:
        """
        Subscribe to a specific channel with the given symbols and mode.

        Args:
            symbol_tickers (Set[str]): The set of symbol tickers to subscribe to.
            channelNo (str): The channel number to subscribe to. Should be between 1 and 50
            mode (SubscriptionModes): The mode of subscription.
        """
        if (
            self.__ws_object is not None
            and self.__ws_object.sock
            and self.__ws_object.sock.connected
        ):
            self._subsinfo.subscribe(symbol_tickers, channelNo, mode)
            self.__ws_object.send(
                json.dumps(
                    {
                        "type": 1,
                        "data": {
                            "subs": 1,
                            "symbols": list(symbol_tickers),
                            "mode": mode.value,
                            "channel": channelNo,
                        },
                    }
                )
            )

    def unsubscribe(self, symbol_tickers: Set[str], channelNo: str, mode: SubscriptionModes) -> None:
        """
        Unsubscribe from a specific channel with the given symbols and mode.

        Args:
            symbol_tickers (Set[str]): The set of symbol tickers to unsubscribe from.
            channelNo (str): The channel number to unsubscribe from. Should be between 1 and 50
            mode (SubscriptionModes): The mode of subscription.
        """
        if (
            self.__ws_object is not None
            and self.__ws_object.sock
            and self.__ws_object.sock.connected
        ):  
            self._subsinfo.unsubscribe(symbol_tickers, channelNo)
            self.__ws_object.send(
                json.dumps(
                    {
                        "type": 1,
                        "data": {
                            "subs": -1,
                            "symbols": list(symbol_tickers),
                            "mode": mode.value,
                            "channel": channelNo,
                        },
                    }
                )
            )
    
    def switchChannel(self, resume_channels: Set[str], pause_channels: Set[str]) -> None:
        """
        Resume and pause channels to receive data from the server.

        Args:
            resume_channels (Set[str]): The set of channels to resume. Data will be received for symbols on these channels.
            pause_channels (Set[str]): The set of channels to pause. Data will be paused for symbols on these channels.
        """
        if (
            self.__ws_object is not None
            and self.__ws_object.sock
            and self.__ws_object.sock.connected
        ):
            self._subsinfo.updateChannels(pause_channels, resume_channels)
            self.__ws_object.send(
                json.dumps(
                    {
                        "type": 2,
                        "data": {
                            "resumeChannels": list(resume_channels),
                            "pauseChannels": list(pause_channels)
                        }
                    }
                )
            )

    def on_depth_update(self, ticker: str, message: Depth):
        """
        Callback function for depth update events.

        Args:
            ticker (str): The ticker symbol.
            message (Depth): The depth message.
        """
        try:
            if self.onDepthUpdate is not None:
                self.onDepthUpdate(ticker, message)
            else:
                if self.write_to_file:
                    self.tbtlogger.debug(f"{ticker}: {message}")
                else:
                    print(f"{ticker}: {message}")
                
        except Exception as e:
            self.tbtlogger.error(e)
            self.On_error(e)

    def on_error_message(self, message: str):
        """
        Callback function for error message events from the server

        Args:
            message (str): The error message.
        """
        try:
            if self.onErrorMsg is not None:
                self.onErrorMsg(message)
            else:
                print(f"error received from server: {message}")
        except Exception as e:
            self.tbtlogger.error(e)
            self.On_error(e)
    
    def __on_message(self, message: Dict[str, Any]):
        """
        Parses the response data based on its content.

        Args:
            message (str): The response message to be parsed.

        Returns:
            Any: The parsed response data.
        """
        try:
            if message != "pong":
                d = protomsg.SocketMessage()
                d.ParseFromString(message)
                if d.error:
                    self.on_error_message(d.msg)
                else:
                    self._datastore.updateDepth(d, self.on_depth_update, self.diff_only)
            

        except Exception as e:
            self.tbtlogger.error(e)
            self.On_error(e)

    def On_error(self, message: str) -> None:
        """
        Callback function for handling error events.

        Args:
            message (str): The error message.

        """
        if self.onerror is not None:
            self.onerror(message)
            self.tbtlogger.error(message)
        else:
            if self.write_to_file:
                self.tbtlogger.debug(f"Response:{message}")
            else:
                print(f"Error Response : {message}")

    def __on_open(self, ws):
        """
        Callback function for open events from the server

        Args:
            ws (WebSocket): The WebSocket object.
        """
        try:
            if self.__ws_object is None:
                self.__ws_object = ws
                self.ping_thread = threading.Thread(target=self.__ping)
                self.ping_thread.start()
                self.reconnect_attempts = 0
                self.reconnect_delay = 0
                self.on_open()

        except Exception as e:
            self.tbtlogger.error(e)
            self.On_error(e)

    def __on_close(self, ws, close_code=None, close_reason=None):
        """
        Handle the WebSocket connection close event.

        Args:
            ws (WebSocket): The WebSocket object.
            close_code (int): The code indicating the reason for closure.
            close_reason (str): The reason for closure.

        Returns:
            dict: A dictionary containing the response code, message, and s.
        """
        try:
            if self.restart_flag:
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    if self.write_to_file:
                        self.tbtlogger.debug(
                            f"Response:{f'Attempting reconnect {self.reconnect_attempts} of {self.max_reconnect_attempts}...'}"
                        )
                    else:
                        print(
                            f"Attempting reconnect {self.reconnect_attempts+1} of {self.max_reconnect_attempts}..."
                        )
                    if (self.reconnect_attempts) % 5 == 0:
                        self.reconnect_delay += 5
                    time.sleep(self.reconnect_delay)
                    self.reconnect_attempts += 1

                    self.__ws_object = None
                    self.connect()
                else:
                    if self.write_to_file:
                        self.tbtlogger.debug(
                            f"Response:{'Max reconnect attempts reached. Connection abandoned.'}"
                        )
                    else:
                        print("Max reconnect attempts reached. Connection abandoned.")
            else:

                self.on_close(
                    {
                        "code": defines.SUCCESS_CODE,
                        "message": defines.CONNECTION_CLOSED,
                        "s": defines.SUCCESS,
                    }
                )
        except Exception as e:
            self.tbtlogger.error(e)
            self.On_error(e)

    def __ping(self) -> None:
        """
        Sends periodic ping messages to the server to maintain the WebSocket connection.

        The method continuously sends "__ping" messages to the server at a regular interval
        as long as the WebSocket connection is active.

        """

        while (
            self.__ws_object is not None
            and self.__ws_object.sock
            and self.__ws_object.sock.connected
        ):
            self.__ws_object.send("ping")
            time.sleep(10)

    def on_close(self, message: dict) -> None:
        """
        Handles the close event.

        Args:
            message (dict): The close message .
        """

        if self.onclose:
            self.onclose(message)
        else:
            print(f"Response: {message}")

    def on_open(self) -> None:
        """
        Performs initialization and waits before executing further actions.
        """
        try:
            if self.onopen:
                self.onopen()
                open_chans = self._subsinfo.getChannelInfo()
                self.switchChannel(self._subsinfo.getChannelInfo(), set())
                for channel in open_chans:
                    self.subscribe(self._subsinfo.getSymbolsInfo(channel), channel, self._subsinfo.getModeInfo(channel))
        except Exception as e:
            self.On_error(e)

    def is_connected(self):
        """
        Check if the websocket is connected.

        Returns:
            bool: True if the websocket is connected, False otherwise.
        """
        if self.__ws_object:
            return True
        else:
            return False
        

    def __init_connection(self):
        """
        Initializes the WebSocket connection and starts the WebSocketApp.

        The method creates a WebSocketApp object with the specified URL and sets the appropriate event handlers.
        It then starts the WebSocketApp in a separate thread.
        """
        try:
            if self.__ws_object is None:
                if self.write_to_file:
                    self.background_flag = False
                header = {"authorization": self.__access_token}
                ws = websocket.WebSocketApp(
                    self.__url,
                    header=header,
                    on_message=lambda ws, msg: self.__on_message(msg),
                    on_error=lambda ws, msg: self.On_error(msg),
                    on_close=lambda ws, close_code, close_reason: self.__on_close(
                        ws, close_code, close_reason
                    ),
                    on_open=lambda ws: self.__on_open(ws),
                )
                self.t = Thread(target=ws.run_forever) 
                self.t.daemon = self.background_flag
                self.t.start()

        except Exception as e:
            self.tbtlogger.error(e)

    def keep_running(self):
        """
        Starts an infinite loop to keep the program running.

        """
        self.__ws_run = True
        self.running_thread = Thread(target=self.infinite_loop)
        self.running_thread.start()

    def stop_running(self):
        self.__ws_run = False

    def infinite_loop(self):
        while self.__ws_run:
            time.sleep(0.5)

    def connect(self) -> None:
        """
        Establishes a connection to the WebSocket.

        If the WebSocket object is not already initialized, this method will create the
        WebSocket connection.

        """
        if self.__ws_object is None:
            self.__init_connection()
            time.sleep(2)

            
    def close_connection(self):
        """
        Closes the WebSocket connection 

        """
        if self.__ws_object is not None:
            self.restart_flag = False
            self.__ws_object.close()
            self.__ws_object = None
            self.__ws_run = None
            self.running_thread.join()
            self.t.join()
            self.ping_thread.join()
