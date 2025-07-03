# Metrics Monitor

## 測定サーバについて

Metrics Monitor 機能は　STUNプロトコルのPadding Attributeを用いて、Padding Attribute を Echo Back する実装を行なった StunServer との通信を行うことで、遅延・パケットロストの測定を行っている。そのため、通信先には対応する実装を行なったStunServerが必須である。

配布イメージのデフォルトの状態では通信先が設定されておらず、この状態のまま起動しても、メニュー画面でMetrics Monitor Mode はグレーアウトされ選択できない。任意の測定サーバを構築の上、設定ファイルにそのアドレス情報を記載すると、メニューが選択可能になるようになっている。

対応するStunServerソフトウェアは後述するので、自身で計測先を用意する場合には参考にすること。（同等の通信が行われるならば、別のソフトウェアを用いても問題ない）

### サーバの構築方法

STUNプロトコルの Padding Attribute は RTC5780 で定義されているが、フローの過程でどの様に扱われるかについては定義が不十分であり、そのため各実装ごとに扱いがまちまちである。

そのため、ここでは Metrics Monitorと適合するOSS公開されているサーバと対応するパッチを使った構築方法を紹介する。

> 前述の通り、Client が送信した Padding Attribute を Echo Back すればいいので、それに従う実装を用意できるのなら、ここで紹介するプログラムを使用しなくても良い。

#### 1. OSSプログラムの用意

「STUNTMAN - An open source STUN server」の version 1.2.13 をベースに構築する。

Github上では、[jselbie/stunserver](https://github.com/jselbie/stunserver/) として公開されている。

対応バージョンのTagを選びリソースをダウンロード・展開する。

#### 2. パッチを適用する

/misc/patch/stunserver_padding_echo.patch

を展開先で適用する

#### 3. 構築

オリジナルソースのビルド・実行手順に従い構築する。