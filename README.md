# setu-class
Setu classification.

# API

#### 1. Dice from url
> /dice?url=http://random.api.url

1. The classification is returned in headers, which named `Class`.
2. The http content is a webp image.

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