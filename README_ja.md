# ニューストレンドの相関性

*これは[codecheck](http://app.code-check.io/openchallenges)のチャレンジだよ。 始めてみるには[ドキュを見てね](https://code-check.github.io/docs/ja)*

相関係数とは2つ、もしくはそれ以上のデータ群の関連性を測る指標です。例えば，片方が大きいと，もう片方も大きくなる場合、その2つのデータ群には相関があるといいます。相関係数は無次元量で、−1以上1以下の実数に値をとります。相関係数が正のとき確率変数には正の相関が、負のとき確率変数には負の相関があるといいます。

当チャレンジでは、朝日新聞の記事を収録するデータベースの検索APIを利用して、このような単語の相関性を分析します。

この記事データベースは、朝日新聞の過去の紙面から当チャレンジ用にピックアップした記事を収録したものです。
記事の著作権は朝日新聞社に帰属しますので、当チャレンジ以外での利用はできません。


## ザ・ミッション
朝日新聞アーカイブ記事APIを利用し、入力した文字列の週刊単位での相関係数（ピアソンの積率相関係数）を出力する関数を実装せよ。
また、任意の形態素解析APIを利用し、入力した文字列の品詞が全て等しいことを確認する機能を追加せよ。

## 実装方法

##### CLI
入力値を引数に取り、結果を標準出力に出力するCLIアプリケーションとして解答を実装してください。
CLIの実装方法については[指定言語].mdを参照ください。
使用可能な言語は

- nodejs
- ruby
- java
- go
- python

のいずれかです。

##### 入力形式
`stdin`の入力値の形式は以下の通りです:
```
["keyword1", "keyword2", ...]  startDate  endDate
```
例えば:
```
["うどん", "香川県"]  2010-01-01  2016-01-01
```

すなわち、複数キーワードの動的な長さの配列および掲載日の期間が入力として与えられます。

##### 出力形式
期待する出力は以下の形式の単一の文字列です：
```
{
  coefficients: [ [coefficientOfKeyword1vsKeyword1, coefficientOfKeyword1vsKeyword2],
                  [coefficientOfKeyword2vsKeyword1, coefficientOfKeyword2vsKeyword2] ],
  posChecker: false
}
```

例えば:
```
{ coefficients: [[1,0.275],[0.275,1]], posChecker: true }
```

キーワードが３つであればこのような構造になります：
```
{
  coefficients: [
    [ 1, 0.208, 0.080 ],
    [ 0.208, 1, 0.201 ],
    [ 0.080, 0.201, 1 ]
  ],
  posChecker: true
}
```

##### 相関係数

あなたの関数はまず、APIのレスポンス内の`response.result.numfound`、もしくは`response.result.doc`にある各記事の`Body`を直にクロールして取得した検索件数を、各キーワードごとに週別に分けた配列にします。次に、この複数の配列のピアソンの積率相関係数を計算します。

- 出力の`coefficients`部分は各文字列同士の相関係数を配列の配列として表したものとなります。
- 配列の長さはキーワード数と等しくなります。
- 相関係数自体は小数点以下３桁に四捨五入してください。

##### 形態素解析

追加課題として、公開されている任意の形態素解析APIを利用し、入力した文字列の品詞（動詞、名詞、形容詞等）が全て等しいことを確認してください。
全ての品詞が等しい場合は`posChecker`を`true`とし、等しくない場合は`false`と出力ください。

推奨するAPIは以下の通りです：
- [Yahoo! JAPAN Web API](http://developer.yahoo.co.jp/sample/jlp/sample2.html)
- [goo ラボ API](https://labs.goo.ne.jp/api/jp/morphological-analysis/)
- [Rosette Text Analytics API](https://www.rosette.com/function/morphological-analysis/)

##### 朝日新聞アーカイブ記事API
朝日新聞アーカイブ記事APIの利用方法は`Asahi-News-Archives-API-instructions.md`で確認ください。

## answer.md
`answer.md`を用意してあるので、その中に
- どのように実装したか、工夫した点は何か
- 発生した問題、難しかった箇所
- それをどのようにして対処したのか

等を書いてください。
