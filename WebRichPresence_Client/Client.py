import json
import logging
import os
import time
from typing import Dict, Optional, Callable, Type

from pypresence import Presence
from socketIO_client import SocketIO, BaseNamespace


class Client(object):
    """
    Main client object for WebRichPresence_Client. Handles all interactions between the API and Discord.
    """

    _port: int
    _hostname: str
    _config_path: str
    _config: Dict[str, Optional[str]]
    _socket: SocketIO
    _logger: logging.Logger
    _presence_callbacks: Dict[str, Callable[..., None]]
    _current_app_id: Optional[str]
    _rpc: Presence
    _presence_namespace: Type[BaseNamespace]

    def __init__(self, port: int, hostname: str, config_path: str):
        """
        Initializes a new Client.
        :param port: The port that the API server runs on
        :param hostname: The hostname (or IP address) the API server runs on
        :param config_path: The path to the config file where the token will be stored
        """
        self._port = port
        self._hostname = hostname
        self._config_path = config_path
        self._current_app_id = None
        self._rpc = None
        self._logger = logging.getLogger("WebRichPresence_Client")
        logging.getLogger("socketIO-client").setLevel(logging.ERROR)
        self._logger.setLevel(logging.INFO)

        # Dynamically create the namespace object
        self._presence_callbacks = {
            "authenticated": self._on_authenticated,
            "new_token": self._on_new_token,
            "presence": self._on_presence,
            "connect": self._on_connected,
            "reconnect": self._on_reconnect,
            "clear": self._on_clear
        }

        self._presence_namespace = type("PresenceNamespace", (BaseNamespace, ), {
            "on_" + k: v for k, v in self._presence_callbacks.items()
        })

        if not os.path.isfile(config_path):
            self._config = {
                "token": None
            }

        else:
            with open(config_path) as f:
                self._config = json.load(f)

    def _initialize_rpc(self, app_id: str):
        """
        Initializes the connection to Discord RPC.
        :param app_id: The app ID that will be used for RPC
        """
        if self._rpc:
            self._rpc.close()
        self._rpc = Presence(app_id)
        self._rpc.connect()
        self._current_app_id = app_id

    def _on_presence(self, app_id: str, presence: dict):
        """
        Handles the presence event from the API server.
        :param app_id: The app ID to use for the presence
        :param presence: The presence details
        """
        if app_id != self._current_app_id or self._rpc is None:
            self._initialize_rpc(app_id)
        try:
            self._rpc.update(**presence)
            self._logger.info(f"App {app_id} updated presence.")
        except TypeError:
            self._logger.warning(f"App {app_id} sent invalid presence object.")
        except IOError:
            time.sleep(15)
            self._on_presence(app_id, presence)

    def _on_new_token(self, new_token: str):
        """
        Handles the new token event from the API server.
        :param new_token: The new token
        """
        self._config["token"] = new_token

        with open(self._config_path, "w") as f:
            json.dump(self._config, f)

        self._logger.info("New token retrieved from server!")
        self._logger.info(f"Your new token is {new_token}")
        self._logger.info("Provide this token to all apps you wish to use with WebRichPresence.")

    def _on_authenticated(self, _):
        """
        Handles the authenticated event from the API server.
        """
        self._logger.info("Authenticated.")

    def _on_connected(self):
        """
        Handles the connect event from the API server.
        """
        self._logger.info("Connected to server. Authenticating...")
        self._authenticate()

    def _on_reconnect(self):
        """
        Handles the reconnect event from the API server.
        """
        self._logger.info("Regained connection to the API server. Re-authenticating...")
        self._authenticate()

    def _on_clear(self, appid):
        """
        Handles the clear event from the API server.
        :param appid: The appid requesting to be cleared
        """
        if appid != self._current_app_id:
            self._logger.warning(f"Non-current app {appid} attempted to clear presence. Ignoring.")
        else:
            self._current_app_id = None
            self._rpc.close()
            self._rpc = None
            self._logger.info(f"App {appid} cleared presence info.")

    def _authenticate(self):
        """
        Handles authenticating with the API server.
        """
        if not self._config["token"]:
            self._logger.info("No token defined, retrieving new one from server...")
            self._socket.emit("new_auth")
        else:
            self._logger.info(f"Authenticating with existing token {self._config['token']}...")
            self._socket.emit("auth", self._config["token"])

    def run(self):
        """
        Runs the client and connects to the API server.
        """
        self._logger.info("Connecting to WebRichPresence...")
        self._socket = SocketIO(self._hostname, self._port)
        self._socket.define(self._presence_namespace, "/presence")

        self._socket.wait()
