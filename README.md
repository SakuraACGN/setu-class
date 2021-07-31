# setu-class
Setu classification.

# Command line
```bash
python3 server_flask.py <host> <port> <valid_img_save_dir> <invalid_img_save_dir>
```

- **valid_img_save_dir**: the image got from valid api list.
- **invalid_img_save_dir**: the image got beyond valid api list.

# API

#### 1. Dice from url
> /dice?url=http://random.api.url

> optional: noimg=true loli=true class=9


1. The classification is returned in headers, which named `Class`.
2. The http content is a webp image.
3. There are also a `DHash` value returned in headers and being encoded by `base16384`.
4. If noimg=true is set, the server will only return json in API 2.
5. If loli=true is set, the server will use lolicon api and ignore url parameter.
6. If class=9 is set, the server will return class from 0 to 8.

#### 2. Classify posted data
> /classdat

1. Post an image to this url.
2. Returns json with its `dhash` & `class`.

```json
{"img": "dhash", "class": 0}
```

#### 3. Classify posted form
> /classform

1. Post multiple images in a form to this url.
2. Returns json array with its `dhash` & `class`.

```json
{"result": [{"name": "name1", "img": "dhash1", "class": 0}, ...]}
```

# Thanks
- [露娜](https://github.com/cherry-luna)