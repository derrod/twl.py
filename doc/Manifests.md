# Manifests

## Manifest
The simple old Manifest is just a big XML file that contains data for all the game's files (path, hashes, url).

This does not contain some of the data v2 manifests have like file/directory modes, hidden status, creation date, etc. but does include URLs.
Delta patching does not seem to be supported by this manifest version.

**Format (XML):**
```xml
<?xml version="1.0" ?>
<manifest xmlns="http://internal.amazon.com/SoftwareDistributionService/DistributionManifest/1.0">
  <files>
    <file>
      <content length="1571154" type="application/octet-stream"/>
      <verification alg="SHA-256" data="473c0111f5a1efb6791575c5f769431fa2affd76813aaf9d476a571e26cd3fed" method="hash"/>
      <installation>
        <local name="DEC2006_d3dx9_32_x64.cab" path="DirectX"/>
      </installation>
      <download>
        <signed-url expires="2018-07-04T19:07:58.689Z" source="CloudFront" url="https://d3rmjivj4k4f0t.cloudfront.net/..."/>
        <signed-url expires="2018-07-04T19:07:58.689Z" source="S3" url="https://downloads-us-east-1-prod.s3.amazonaws.com/..."/>
      </download>
    </file>
	...
  </files>
</manifest>
```

## Manifest v2
The V2 manifest works in multiple parts, you have the manfiest with information about files, directories and their
hashes (protobuf encoded, see [`data/proto/sds.proto`](../data/proto/sds.proto)).

You then use this to create requests to get the download URLs for the files or patches required to install the game.
This allows comparing a new manifest with the locally stored old version to figure out which files need to be updated.
Delta patching is also supported by the Twitch App.

The mainfest strucutre is:
<4-byte header length> <header> <(compressed) manifest>

Example data taken from [`data/example_manifest`](../data/example_manifest)

**Header Format (protobuf message)**
```
compression {
  algorithm: lzma
}
hash {
  value: "\232\270\306\340\354N\363\363G-\234;]\276s\322\242\352@\367\325\231\324\010\013[p$N\236\0306"
}
signature {
  value: "\350\002x\347\315Yr0D\217\005\000F\236\032P\241\020\251\254\013\375\256hY\213\300\223%Y\344\264\r\344rBW&m\037\\r\360\341,h\376\001\300\0314{\032\316}\320\r\367\205;\022\024\001\022\226\347\220\222\033\245\201\227\264;\002K\302m\r\266B\034?\203d\023w+:P\021\252\253\375\000\014\270\253*\330\014\357`h/\014\t\366\266\346\020U_|\346\216\272\205Q\277\265\205\307\331\026T&\322l\004\335\373\370)\026\345\366\225\221l\236H_\230[\245\311\276\374.v\270L|\337\306\374\370\323\340\346V\003\303CGs5Ty\277?\014\362\216V\232X\252T\302\334L\033;\021m\344g\267A\026x\332Q\234\310\037\370\232r\310g\302uf\252\201Q\344ir99\270B\265\362\277\327*\317\035\203j\006\320\205Be\276\241\272mX\341\002\353\373\302I\265\210\211\033$\224\332\371\0172\250\231\255\206\237"
}
```

The compression value tells you how the main manifest is compressed, it can be lzma or none. Hash is not used in the official twitch app as far as I can tell, but it is likely just the SHA256 of the decompressed manifest.
The signature is a cryptographics signature of the decompressed manifest. The public key can be found in [`data/manifest_pubkey.pem`](../data/manifest_pubkey.pem). See [`src/manifest_v2.py`](../src/models/manifest_v2.py) for how we deal with that.

Usually you can just get the header size, jump to the offset header_size + 4, decompress and read the manifest.

**Manifest Format (protobuf message):**
```
packages {
  name: "required"
  files {
    path: "Adobe AIR\\Versions\\1.0\\Resources/adobecp.vch"
    mode: 511
    hash {
      value: "\343\260\304B\230\374\034\024\232\373\364\310\231o\271$\'\256A\344d\233\223L\244\225\231\033xR\270U"
    }
  }
  ...
  dirs {
    path: "META-INF\\AIR"
    mode: 511
  }
  ...
}
```
