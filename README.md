# WebRichPresence_Client

A basic command-line client for the WebRichPresence service

## NOTE: There is currently NO PUBLIC SERVER for WebRichPresence. As a result, this program will not work at the moment

## About WebRichPresence

WebRichPresence is a simple system that provides a web API for sites, apps, and services to use Discord's Rich Presence features without having to build their own app to run on your PC. All they need to do is collect a token from you, and then this client will display the presences they submit to the API.

## Installation

```bash
> git clone https://github.com/nint8835/WebRichPresence_Client.git
> cd WebRichPresence_Client.git
> python setup.py install
```

## Usage

1. Run `webrichpresence`
    * This is the client that will actually handle the interaction with Discord
2. Make note of the token that is logged to the console
    * This token is what will allow services to update your presence
3. Provide this token to all services that you wish to be able to update your status.

## For developers

At the moment, WebRichPresence does not have a publically-available API server. Once a server becomes publicly available, API documentation (or a link to API documentation) will be available here.