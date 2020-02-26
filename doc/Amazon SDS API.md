# Amazon SDS API

Documentation based on `Amazon.Fuel.SoftwareDistributionService` in `Twitch\Bin\Amazon.Fuel.SoftwareDistributionService.dll`

All requests are POST requests with JSON body to `https://sds.amazon.com`.

**Headers:**
* `X-Amz-Target` contains full method name
* `x-auth-twitch` contains Twitch Fuel OAuth token
* `Content-Encoding: amz-1.0`

All method names are prefixed with `com.amazonaws.gearbox.softwaredistribution.service.model.SoftwareDistributionService`

## `GetEntitlements`

Request Body:
```json
{
    "clientId": "Fuel",
    "syncPoint": null
}
```

Response:
```json
{
  "entitlements": [
    // Game entitlement
    {
      "channelId": "<?>",
      "entitlementDateFromEpoch": "1485270623433",
      "id": "<entitlement id>",
      "product": {
        "asin": "B01LY6I8SV",
        "asinVersion": 17,
        "description": "Streamline Product Description",
        "id": "d229a310-2468-4f0c-b49b-4a6dcdd47809",
        "productDetail": {
          "details": {
            "backgroundUrl1": "https://images-na.ssl-images-amazon.com/images/I/A1s5Dn4PbcL.jpg",
            "backgroundUrl2": "https://images-na.ssl-images-amazon.com/images/I/71ATqW8g9+L.jpg",
            "publisher": "Proletariat Inc.",
            "screenshots": [
              "https://images-na.ssl-images-amazon.com/images/I/A15t1eN9L5L.jpg",
              "https://images-na.ssl-images-amazon.com/images/I/A1+q5s77ZEL.jpg",
              "https://images-na.ssl-images-amazon.com/images/I/A1s5Dn4PbcL.jpg",
              "https://images-na.ssl-images-amazon.com/images/I/A1UQ65tz4vL.jpg",
              "https://images-na.ssl-images-amazon.com/images/I/91Br+c5JybL.jpg",
              "https://images-na.ssl-images-amazon.com/images/I/91UbQCYgEFL.jpg",
              "https://images-na.ssl-images-amazon.com/images/I/91u9kbA-dDL.jpg",
              "https://images-na.ssl-images-amazon.com/images/I/A1o0iVrtDzL.jpg",
              "https://images-na.ssl-images-amazon.com/images/I/A1ZZAFon2wL.jpg"
            ],
            "videos": [
              "https://www.twitch.tv/videos/133202883"
            ]
          },
          "iconUrl": "https://images-na.ssl-images-amazon.com/images/I/61242jdqe0L.png"
        },
        "productLine": "Twitch:FuelGame",
        "sku": "com.proletariat.streamline",
        "title": "Streamline",
        "type": "Entitlement",
        "vendorId": "PS363"
      },
      "state": "LIVE"
    },
    // Non-game entitlement
    {
      "channelId": "<?>",
      "entitlementDateFromEpoch": "1485270643825",
      "id": "<entitlement id>",
      "product": {
        "asinVersion": 0,
        "description": "This is a Twitch Prime bundle",
        "id": "c9dae41c-8885-4753-bed0-d21a7b45ae94",
        "productLine": "Twitch:FuelEntitlement",
        "sku": "com.proletariat.streamline.prime_bundle",
        "title": "Streamline Twitch Prime Bundle",
        "type": "Entitlement",
        "vendorId": "PS363"
      },
      "state": "LIVE"
    },
	...
  ]
}
```

Note: the entitlement id is used for getting the manifest


## `GetDownloadManifest`

Request Body:
```json
{
    "entitlementId": "<entitlement Id>"
}
```

Response:
```json
{
    "manifest": "<xml encoded manifest>",
    "versionId": "<manifest version Id>"
}
```

## `GetDownloadManifestV2`

Request Body:
```json
{
  "adgGoodId": "<entitlement Id>",
  "Operation": "GetDownloadManifestV2"
}
```

Response Body:
```json
{
  "downloadUrls": [
    "https://d374f6k4w08fj3.cloudfront.net/139c98bd-680a-4679-9399-5ea6c2c866b7?Expires=1534828868&Signature=...",
    "https://protobuf-manifest-us-east-1-prod.s3.amazonaws.com/139c98bd-680a-4679-9399-5ea6c2c866b7?X-Amz-Algorithm=..."
  ],
  "versionId": "<manifest version Id>"
}
```

## `GetPatches`

This is used in conjunction with V2 Manifests to get Download/Path URLs.
The `sourceHash` can specify the hash of the currently installed file to get a delta patch instead of the full file.
The Twitch App seems to keep manifests of installed titles which can presumably be used to match old files to new files (based on path?) and specify a `sourceHash`.

Request Body
```json
{
  "Operation": "GetPatches",
  "versionId": "<manifest version Id>",
  "fileHashes": [
    {
      "sourceHash": null,
      "targetHash": {
        "value": "<file hash from manifest>",
        "algorithm": "SHA256"
      }
    },
	...
  ],
  "deltaEncodings": [
    "NONE",
    "FUEL_PATCH"
  ],
  "adgGoodId": "<entitlement Id>"
}
```

Response Body:
```json
{
  "patches": [
    {
      "downloadUrls": [
        "https://d3rmjivj4k4f0t.cloudfront.net/10eb3a9b1aab7e9479f3b49f99951060c99dc46c2ebc34ffca808904233ed77c-d7e2194c-adfc-4403-a8ac-83e11db98ad6?Expires=...",
        "https://downloads-us-east-1-prod.s3.amazonaws.com/10eb3a9b1aab7e9479f3b49f99951060c99dc46c2ebc34ffca808904233ed77c-d7e2194c-adfc-4403-a8ac-83e11db98ad6?X-Amz-Algorithm=..."
      ],
      "offset": 0,
      "patchHash": {
        "algorithm": "SHA256",
        "value": "10eb3a9b1aab7e9479f3b49f99951060c99dc46c2ebc34ffca808904233ed77c"
      },
      "size": 118,
      "targetHash": {
        "algorithm": "SHA256",
        "value": "10eb3a9b1aab7e9479f3b49f99951060c99dc46c2ebc34ffca808904233ed77c"
      },
      "type": "NONE"
    },
	...
  ]
}
```

`type` defines the delta encoding (see request), `pathHash` the hash of the file when downloaded, `targetHash` the hash of the file after patching.
`offset` appears to be unused by the Twitch App.

## `GetVersions`

Used to check available versions as well as installed versions vs. latest.

Request body:
```json
{
  "adgProductIds": [
    "<product Id>"
  ],
  "Operation": "GetVersions"
}
```

Response:
```json
{
  "errors": [],
  "versions": [
    {
      "adgProductId": "<product Id>",
      "versionId": "<manifest version Id>"
    }
  ]
}
```
