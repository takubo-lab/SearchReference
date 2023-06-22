# SearchReference

## 概要
OpenAIのAPIをワードファイルから呼び出すためのアドインです。以下の二つの機能があります。

１．ワードファイルの選択した部分の文章を論文らしい文章に言い換える（英語→英語）、もしくは翻訳（日本語→英語）
ChatGPT のAPIを呼び出して実行します。1ページ程度の文章までrephrase可能です。


２．選択した文章に近いことを主張している論文上位をPubMedへのリンク付きで表示する。

事前に取得した（主に小林がEndNoteに保存していた造血関連・幹細胞関連の論文）1300個程度のリファレンスのAbstractを、ada-embedding-002のAPIを用いてtext embedding（文章データの意味情報を数値ベクトルに変換する）を行いデータベース化したファイルに対して、同じくWordファイル上の該当箇所をtext embeddingをリアルタイムで実施し、両者の間で類似度を計算し、上位50個程度を表示します。

OpenAI APIを使用するため、使用量に応じて課金されますが、１．については全文を言い換え、ないし翻訳して20円程度、2については1円以下です。

## 事前準備
Node.jsのプロジェクトを利用してWordのAdd-inを呼び出し、それをPythonで立ち上げたローカルサーバーを介して、OpenAIのAPIを使用するため、Node.jsおよびPythonの環境を
セットアップする必要があります。

### 1. OpenAIのAPIキーを取得し、OPENAI_API_KEYを環境変数に設定する

### 2. Python環境の設定

まずどこかのフォルダを作ってそこにcdで移動してその下にプロジェクトを展開します。
そしてPythonをインストールします。ウェブページからインストールできますが、Windowsの場合このあとの過程でマイクロソフトストアから自動でダウンロードし、バージョンの競合のためエラーの原因になるので、最初からマイクロソフトストアで検索してダウンロードしたほうが良いです。

このディレクトリの下に、RIS_library　ディレクトリおよび、
Rephrase_ChatGPT.py をおいてください。
必要なPython libraryのインストール
```
pip install openai
pip install numpy
pip install flask
pip install flask_cors
pip install openai.embeddings_utils
pip install scikit-learn
pip install plotly
pip install pandas
```

### 3. Node.js環境の設定

https://nodejs.org/ja　　からインストール

次に、Node.jsのプロジェクトのテンプレートを作成します。
```
cd your-project-directory
npm install -g yo generator-office
yo office
```
プロジェクトのタイプ、使用するOfficeのプログラム、名前、ID、言語などを指定するプロンプトが表示されます。
プロジェクトのタイプとして"Office Add-in Task Pane project React"を選択します。言語はJavaScriptです。

プロジェクトが作成されたら
your-project-name/src/taskpane/components/ ディレクトリの下に、App.js、Header.js、HeroList.jsを上書き保存します。

### 4. Node.jsおよびPython Flaskによるローカルサーバーの起動
コマンドプロンプトを二つ立ち上げて、片方はPython、もう片方はNode.jsのローカルサーバーの起動に使います。
Python Flask
```
cd your-project-directory
python Rephrase_ChatGPT.py 
```


Node.js
```
cd your-project-directory/your-project-name
npm start
```

このあと、何か聞かれるので n を入力するとWordが起動します。この状態で既存のワードファイルを開くとAdd-inが利用可能です。





