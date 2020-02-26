# Amazon SDS API

Documentation based on `Amazon.Fuel.SoftwareDistributionService` in `Twitch\Bin\Amazon.Fuel.SoftwareDistributionService.dll`

All requests are POST requests with JSON body to `https://sds.amazon.com`.

**Headers:**
* `X-Amz-Target` contains full method name
* `x-auth-twitch` contains Twitch Fuel OAuth token
* `Content-Encoding: amz-1.0`

All method names are prefixed with `com.amazonaws.gearbox.softwaredistribution.service.model.SoftwareDistributionService`

## `GetDownloadManifest`

Request Body:
```json
{
    "entitlementId": "<product Id>"
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
  "adgGoodId": "<product Id>",
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
  "adgGoodId": "<product Id>"
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
