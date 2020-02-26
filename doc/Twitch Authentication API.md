# Twitch Passport API

Based on Fiddler captures.

## Login

URL: `https://passport.twitch.tv/login`

Body (first try):
```json
{
  "username": "<tw username>",
  "password": "<tw password>",
  "client_id": "jf3xu125ejjjt5cl4osdjci6oz6p93r",
  "undelete_user": false
}
```

Body (2fa + captcha solution):

**Authy:**
```json
{
  "username": "<tw username>",
  "password": "<tw password>",
  "client_id": "jf3xu125ejjjt5cl4osdjci6oz6p93r",
  "undelete_user": false,
  "captcha": {
    "proof": "<captcha_proof>"
  },
  "authy_token": "<authy_token>"
}
```

**TwitchGuard:**
```json
{
  "username": "<tw username>",
  "password": "<tw password>",
  "client_id": "jf3xu125ejjjt5cl4osdjci6oz6p93r",
  "undelete_user": false,
  "captcha": {
    "proof": "<captcha_proof>"
  },
  "twitchguard_code": "<twitchguard_code>"
}
```

#### Possible responses:

Successful:
````json
{
  "access_token": "<access_token>",
  "redirect_path": "https://www.twitch.tv/"
}
````

2FA Token (Authy) required:
````json
{
  "captcha_proof": "<captcha_proof>",
  "error": "Please enter a Login Verification Code.",
  "error_code": 3011,
  "error_description": "missing authy token"
}
````

2FA Token (TwitchGuard) required:
````json
{
  "captcha_proof": "<captcha_proof>",
  "error": "Please enter a Login Verification Code.",
  "error_code": 3022,
  "error_description": "missing twitchguard code"
}
````

Invalid username or password:
````json
{
  "error": "Incorrect username or password.",
  "error_code": 3001,
  "error_description": "user credentials incorrect"
}
````

Manual CAPTCHA solving required
````json
{
  "error": "Please complete the CAPTCHA correctly.",
  "error_code": 1000,
  "error_description": "captcha incorrect"
}
````


