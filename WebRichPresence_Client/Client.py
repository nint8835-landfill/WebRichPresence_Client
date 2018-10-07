import os
import json
import logging
from typing import Dict, Optional, Callable

from socketIO_client import SocketIO
from pypresence import Presence

class Client(object):

    _port: int
    _hostname: str
    _config_path: str
    _config: Dict[str, Optional[str]]
    _socket: SocketIO
    _logger: logging.Logger
    _callbacks: Dict[str, Callable[..., None]]
    _current_app_id: Optional[str]
    _rpc: Presence

    def __init__(self, port: int, hostname: str, config_path: str):
        self._port = port
        self._hostname = hostname
        self._config_path = config_path
        self._current_app_id = None
        self._rpc = None
        self._logger = logging.getLogger("WebRichPresence_Client")
        self._logger.setLevel(logging.INFO)

        self._callbacks = {
            "authenticated": self._on_authenticated,
            "new_token": self._on_new_token,
            "presence": self._on_presence
        }

        if not os.path.isfile(config_path):
            self._config = {
                "token": None
            }

        else:
            with open(config_path) as f:
                self._config = json.load(f)

    def _initialize_rpc(self, app_id: str):
        if self._rpc:
            self._rpc.close()
        self._rpc = Presence(app_id)
        self._rpc.connect()
        self._current_app_id = app_id
    
    def _on_presence(self, app_id: str, presence: dict):
        if app_id != self._current_app_id:
            self._initialize_rpc(app_id)
        self._rpc.update(**presence)
    
    def _on_new_token(self, new_token: str):
        self._config["token"] = new_token

        with open(self._config_path, "w") as f:
            json.dump(self._config, f)
        
        self._logger.info("New token retrieved from server!")
        self._logger.info(f"Your new token is {new_token}")
        self._logger.info("Provide this token to all apps you wish to use with WebRichPresence.")
    
    def _on_authenticated(self, _):
        self._logger.info("Connected and authenticated.")
        
    def run(self):
        self._logger.info("Connecting to WebRichPresence...")
        self._socket = SocketIO(self._hostname, self._port)
        
        for callback in self._callbacks.items():
            self._socket.on(callback[0], callback[1])

        if not self._config["token"]:
            self._logger.info("No token defined, retrieving new one from server...")
            self._socket.emit("new_auth")
        else:
            self._logger.info(f"Authenticating with existing token {self._config['token']}...")
            self._socket.emit("auth", self._config["token"])
        self._socket.wait()
