# Curse API

## Twitch Auth API

After getting redirected from Twitch oauth portal get the "code" parameter and send the following JSON body to `https://logins-v1.curseapp.net/login/twitch-oauth`

Request:
````json
{
  "ClientID": "jf3xu125ejjjt5cl4osdjci6oz6p93r",
  "Code": "<code from redirect URL>",
  "State": "<randomly generated state>",
  "RedirectUri": "https://web.curseapp.net/laguna/passport-callback.html",
}
````

Response:
````json
{
  "Status": 0,
  "Session": {
    "UserID": <curse userid>,
    "Username": "<twitch/curse username>",
    "DisplayName": "<twitch/curse displayname>",
    "SessionID": "",
    "Token": "<auth header token>",
    "EmailAddress": "<user email>",
    "EffectivePremiumStatus": false,
    "ActualPremiumStatus": false,
    "SubscriptionToken": <dunno (int)>,
    "Expires": <token expiry>,
    "RenewAfter": <when to renew>,
    "IsTemporaryAccount": false,
    "IsMerged": true,
    "Bans": 0
  },
  "Timestamp": <request timestamp>,
  "MergeToken": null,
  "TwitchUsername": "<twitch username>",
  "TwitchDisplayName": "<twitch displayname>",
  "TwitchAvatar": "<avatar URL>",
  "TwitchUserID": "<twitch user id>"
}
````

## Session API
This API starts the session I guess


## Twitch Fuel API
This has to be used in order to get the Twitch OAuth token that works with the SDS/ADG API.

