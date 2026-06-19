# EM-uNetPi でのスクリーンショット取得について

## スクリーンショットの取得方法

EM-uNetPiの動作中の画像を撮りたくなる事がある。

そんな時、スマホなどで撮影してもいいが、描画の仕組み自体がFramebufferであるため、実は管理ポートから接続して生の画像を取得可能である。

### 事前準備

FrameBufferから得られるデータは生のRAW画像であるため、一般的な形式に変換する必要がある。

お手軽なコマンドラインツールとしては、ややオーバースペックだがffmpegが小慣れているので、今回はこれを用いることにする。

ビットマップ形式からの変換用には、ImageMagickを使うことにする。

というわけで、おもむろにインストールしておきましょう。

```bash
$ sudo apt-get install ffmpeg
$ sudo apt-get install imagemagick
```

変換時に、フレームバッファの描画情報が必要になるので、

```bash
$ cat /sys/class/graphics/fb0/virtual_size
480,320
$ cat /sys/class/graphics/fb0/bits_per_pixel
16
# -> 32 (RGB8888)
# -> 16 (RGB565)
```

として、サイズとフォーマットを取得しておきましょう。

### 取得手順

任意のタイミングでcatして、リダイレクトで吐いてやれば良い。（fb触るので、管理者権限が必要）

```bash
$ sudo cat /dev/fb0 > capture.raw
```

出力したraw画像をffmpegで変換する。

```bash
$ ffmpeg -vcodec rawvideo -f rawvideo -pix_fmt rgb565 -s 480x320 -i capture.raw -f image2 -vcodec bmp capture.bmp
```

ImageMagickでbitmapをjpegに変換。

```bash
$ convert capture.bmp capture.jpg
```

### スクリーンショットファイルの保存先

デフォルトでは /home/pi/EM-uNetPi/screenshots/ 以下に保存される。

適当に

```bash
$ rsync -avz pi@192.168.31.67:EM-uNetPi/screenshots/ screenshots/
```

などして、同期すると良い。

保存したスクリーンショットは自動では消えないので、定期的に削除すること。

