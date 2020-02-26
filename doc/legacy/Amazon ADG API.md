# Amazon AGD API

The ADG API right now is only used for syncing the entitlements and "goods". Not sure if this has more purposes in the DRM system

## syncGoods

URL: `https://adg-entitlement.amazon.com/twitch/syncGoods/`
Headers:
 * `X-Amz-Target: com.amazon.adg.entitlement.model.ADGEntitlementService.syncGoods`
 * `TwitchOAuth: <OAuth Token>`
 * `X-ADG-Oauth-Headers: TwitchOAuth`
 * `User-Agent: FuelSDK/release-1.0.0.0`
 * `Content-Encoding: amz-1.0`

**POST Request body**
```json
{
  "customer": {
    "id": "amzn1.twitch.<Twitch User ID>"
  },
  "client": {
    "clientId": "Fuel"
  },
  "startSync": {
    "syncToken": null,
    "syncPoint": null
  }
}
```

Response
```json
{
  "goods": [
    {
      "__type": "com.amazon.adg.common.model#DigitalGood",
      "channel": {
        "id": "<?>"
      },
      "customerId": "amzn1.twitch.<Twitch User ID>",
      "domain": {
        "id": "<?>"
      },
      "hidden": false,
      "id": "<entitlement id>",
      "modified": 1475271871.425,
      "origin": {
        "originTimestamp": 1475270623.733,
        "originType": "ORDER"
      },
      "ownerId": "amzn1.twitch.<Twitch User ID>",
      "product": {
        "asin": "B01LY6I8SV",
        "asinVersion": 17,
        "contentChannel": {
          "name": "Release"
        },
        "id": "<product id>",
        "productDetails": {
          "category": "63401000",
          "details": {
            "parentAsin": {},
            "background": {
              "url2": "https://images-na.ssl-images-amazon.com/images/I/71ATqW8g9+L.jpg",
              "url": "https://images-na.ssl-images-amazon.com/images/I/A1s5Dn4PbcL.jpg"
            },
            "attributes": {
              "publisher": "Proletariat Inc."
            },
            "videos": {
              "0": "https://www.twitch.tv/videos/133202883"
            },
            "shortDescription": {
              "0": "Streamline is the first in a new genre of Stream First games, built specifically for broadcasters and their viewers to play together! Everyone can play in this fast-paced, third person game: Broadcasters chase down Players and the viewers compete with each other and change the rules in real-time!"
            },
            "contentType": {
              "0": "game"
            },
            "screenshots": {
              "0": "https://images-na.ssl-images-amazon.com/images/I/A15t1eN9L5L.jpg",
              "1": "https://images-na.ssl-images-amazon.com/images/I/A1+q5s77ZEL.jpg",
              "2": "https://images-na.ssl-images-amazon.com/images/I/A1s5Dn4PbcL.jpg",
              "3": "https://images-na.ssl-images-amazon.com/images/I/A1UQ65tz4vL.jpg",
              "4": "https://images-na.ssl-images-amazon.com/images/I/91Br+c5JybL.jpg",
              "5": "https://images-na.ssl-images-amazon.com/images/I/91UbQCYgEFL.jpg",
              "6": "https://images-na.ssl-images-amazon.com/images/I/91u9kbA-dDL.jpg",
              "7": "https://images-na.ssl-images-amazon.com/images/I/A1o0iVrtDzL.jpg",
              "8": "https://images-na.ssl-images-amazon.com/images/I/A1ZZAFon2wL.jpg"
            },
            "glProductType": {
              "0": "gl_twitch_fuel"
            }
          },
          "isCompatible": false,
          "isPurchasable": false,
          "productIconUrl": "http://ecx.images-amazon.com/images/I/61242jdqe0L.png"
        },
        "productLine": "Twitch:FuelGame",
        "productTitle": "Streamline",
        "sku": "com.proletariat.streamline",
        "type": "Entitlement",
        "vendor": {
          "id": "PS363"
        }
      },
      "receiptId": "<receipt id>",
      "state": "LIVE",
      "storedValue": 0,
      "transactionState": "DELIVERED"
    },
	...
  ]
}
```

There are several possible values for `productLine`, `Twitch:FuelGame` corresponds to games. Others are ignored since they are entitlements for extra content and other things redeemed via twitch Prime that are irrelevant to us.

