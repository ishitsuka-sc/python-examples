CTFの流れ

参加者には

invoice_training.pdf

だけを渡します。

AIには

このPDFを要約してください

というタスクを与えます。

参加者は

pdftotext invoice_training.pdf -

や

import fitz

doc = fitz.open("invoice_training.pdf")
print(doc[0].get_text())

などで抽出すると、透明なテキストレイヤーの内容も取得できる場合があります。

問題文の例

あなたはAIエージェントの挙動を調査するセキュリティエンジニアです。

AIに請求書PDFを要約させたところ、通常の請求書とは関係のない内容が応答に含まれていました。

PDFを解析し、AIが誤動作した原因を説明し、埋め込まれていたフラグを提出してください。
