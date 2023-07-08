# SearchReference

## 概要
OpenAIのAPIをワードファイルから呼び出すためのアドインです。以下の二つの機能があります。

1.**ワードファイルの選択した部分の文章を論文らしい文章に言い換え（英語→英語）、もしくは翻訳（日本語→英語）**: 

ChatGPT のAPIを呼び出して実行します。1ページ程度の文章までrephrase可能です。GPT3.5モードとGPT4モードが選択できますが、GPT3.5モードの方が安く、
そこまで言い換えレベルではGPT4との差がないので、GPT3.5の方を選んだ方がよいケースが多いですが、GPT4の方がより重厚な文を生成しやすく、ここぞというときには
こちらを選択しても良いかと思います。


2.**選択した文章に近いことを主張している論文上位をPubMedへのリンク付きで表示**：

事前に取得した（主に小林がEndNoteに保存していた造血関連・幹細胞関連の論文）1300個程度のリファレンスのAbstractを、ada-embedding-002のAPIを用いてtext embedding（文章データの意味情報を数値ベクトルに変換する）を行いデータベース化したファイルに対して、同じくWordファイル上の該当箇所をtext embeddingをリアルタイムで実施し、両者の間で類似度を計算し、上位50個程度を表示します。

OpenAI APIを使用するため、使用量に応じて課金されますが、１．については全文を言い換え、ないし翻訳して20円程度、2については全文を検索しても（ないと思いますが）1円以下です。

3.**文章の補完機能**：

選択した部分の文章の続きをChatGPTによって補完またはリライトします。この機能は、GPT-4モードを使用して選択したテキストの意味や文脈を理解し、それに基づいた新しい文章を生成します。この機能は英語のテキストに対して使用できます。

4.**PubMedAPIの呼び出し機能**：

選択した文章と関連性の高い論文をPubMedから探し出し、その情報を表示します。この機能は、選択したテキストをテキストエンベッディングし、そのエンベッディングベクトルを元に1300個程度のリファレンスとの類似度を計算します。最も関連性の高い上位50件の文献を表示します。

5.**DeepLの呼び出し機能**：

選択した文章をDeepLを用いて翻訳します。この機能は主に日本語から英語への翻訳に使用します。

これらの機能は、JavaScriptで実装されたWordのアドインを通じて提供され、Pythonで実行されるローカルサーバーを介してOpenAIのAPIにアクセスします。このため、使用にはNode.jsおよびPythonの環境設定が必要です。

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

https://nodejs.org/ja
からインストール

次に、Node.jsのプロジェクトのテンプレートを作成します。
```
cd your-project-directory
npm install -g yo generator-office
yo office
```
プロジェクトのタイプ、使用するOfficeのプログラム、名前、ID、言語などを指定するプロンプトが表示されます。

プロジェクトのタイプとして"Office Add-in Task Pane project React"を選択します。言語はJavaScriptです。

プロジェクトが作成されたら
```
# your-project-name/src/taskpane/components/ ディレクトリの下に、App.js、Header.js、HeroList.jsを上書き保存します。
# your-project-name/src/taskpane/　ディレクトリの下に taskpane.cssを上書き保存します。
```

## 実行
### Node.jsおよびPython Flaskによるローカルサーバーの起動
コマンドプロンプトを二つ立ち上げて、片方はPython、もう片方はNode.jsのローカルサーバーの起動に使います。

#### Python Flask
```
cd your-project-directory
python Rephrase_ChatGPT.py 
```

#### Node.js
```
cd your-project-directory/your-project-name
npm start
```

このあと、何か聞かれるので n を入力するとWordが起動します。この状態で既存のワードファイルを開くとAdd-inが利用可能です。

