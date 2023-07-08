# Automated_original_drawing_tracing_for_animation
# リンク
情報処理学会<br>
https://ipsj.ixsq.nii.ac.jp/ej/?action=pages_view_main&active_action=repository_view_main_item_detail&item_id=217855&item_no=1&page_id=13&block_id=8
# ファイル詳細
codes:<br>
　研究に用いたソースコード<br>
　環境はpython,pycharm<br>
input_images:<br>
　評価実験に用いた入力画像<br>
output_imgs.pdf:<br>
　出力画像一覧<br>
recordtime.xlsx:<br>
　各画像の画像処理時間<br>
survey.pdf:<br>
　評価実験に用いたアンケート
# 1．研究の目的と背景
　紙に描いた絵のクリーンアップは手間がかかる．特に，アニメーション制作の原画トレースは大きな負担となる作業である．線画抽出だけでは求めた線画を取得することは容易ではない．したがって，本研究ではアニメーションの原画トレースの自動化を最終目標に掲げ，第一段階として既存のクリーンアップ処理モデルに前処理，後処理を追加して改善を目指した．
# 2．外部状況
　[1]は深層学習を用いてラフスケッチから対話的に線画を作成でき，[2]はラフスケッチのクリーンアップ処理を行っているが，出力が不安定である．また，クリーンアップ処理に関する前処理，後処理の研究は見られない．
# 3．提案手法
　本研究では[2]の研究の出力を安定させるための前処理，後処理手法を提案する．
## 3.1. 前処理
　入力画像に二値フィルタ，メディアンフィルタを用いて前処理を行う．閾値やカーネルサイズは入力画像に対して最適化された値を利用する．<br>
<p align="center">
 <img src="https://github.com/Shio2243/Automated_original_drawing_tracing_for_animation/assets/87845176/8aa55182-7c91-4215-8760-106f822862fb" width=50% height=50% ><br>
図 3.1: 前処理, 黒の割合の求め方
</p>

## 3.2.	後処理
　[2]の出力画像に対して前処理後の画像の線に対応するように線の座標を調整する．<br>
<p align="center">
 <img src="https://github.com/Shio2243/Automated_original_drawing_tracing_for_animation/assets/87845176/d8fa7dbf-95ae-4662-976f-ea7ad9a25e5f" width=50% height=50% ><br>
図 3.2: 後処理, 座標 a から距離 n の求め方
</p>
 
# 4. 実験
## 4.1. 実験手法
　実験素材には3種類の大きさの12種類のイラストを使用して，[2]の出力，前処理を施した[2]の出力，前処理と後処理を施した[2]の出力の3種類の結果を取得した．提案手法の結果から手書きトレースとの類似性を確かめるために差分値を求め，前処理，後処理の有効性を確かめるために13人に対してアンケートを行った．また，前処理，後処理に要した時間も取得した．
## 4.2. 実験結果
　全ての画像で前処理を施した方が負の差分が減少していた．また，アンケートでは， 全ての問で前処理を施した[2]の出力が最も多く選択された．
 処理時間の分散・平均の上昇量について，前処理は小さく，後処理は大きい．<br>
<p align="center">
 <img src="https://github.com/Shio2243/Automated_original_drawing_tracing_for_animation/assets/87845176/d03fb9ac-8ab2-4dd2-9f19-9b3a124e59f9" width=40% height=40% ><br>
 図 4.1: 取得した画像例
</p>
<p align="center">
 <img src="https://github.com/Shio2243/Automated_original_drawing_tracing_for_animation/assets/87845176/0586c99c-fe92-4a7c-a3ad-562961c6959c" width=40% height=40% ><br>
 図 4.2: 出力された画像の比較
</p>
<p align="center">
<img src="https://github.com/Shio2243/Automated_original_drawing_tracing_for_animation/assets/87845176/fea9702c-23b4-4e63-896e-f79960379e43" width=40% height=40% ><br>
図 4.3: 差分の求め方
</p>
<p align="center">
<img src="https://github.com/Shio2243/Automated_original_drawing_tracing_for_animation/assets/87845176/93e6d5af-6902-4d31-a2ee-efcd31bd46ad" width=50% height=50% ><br>
図 4.4: 差分画像出力例
</p>

表 4.1: man.png の差分の割合
|手法|差分割合 [%]|正の差分割合 [%]|負の差分割合 [%]|
| - | - | - | - |
|クリーンアップ処理|5.0471|1.7646|3.2824|
|前処理+クリーンアップ処理|6.0124|4.7612|1.2513|
|前処理+クリーンアップ処理+後処理|6.1289|4.7125|1.4164|

表4.2:処理時間の分散
|画像サイズ|320[s]|720[s]|1000[s]|
| - | - | - | - |
|前処理|0.0550|0.0564|0.0537|
|クリーンアップ処理|1.6241|3.0551|5.9582|
|後処理|0.7103|3.8567|10.2927|

表 4.3: 処理時間の平均
|画像サイズ|320[s]|720[s]|1000[s]|
| - | - | - | - |
|前処理|0.1982|0.2147|0.2294|
|クリーンアップ処理|5.5800|14.4731|25.8553|
|後処理|3.8884|13.4242|26.1521|

<p align="center">
<img src="https://github.com/Shio2243/Automated_original_drawing_tracing_for_animation/assets/87845176/373d2c9a-609d-4478-9e52-08a1b29d09a9" width=60% height=60% ><br>
図 4.5: 処理時間の分散, 平均値
</p>

# 5. 考察
　負の差分の減少から[2]の出力単体よりも線の損失量が減少している．ただし，アンケートの結果から後処理の効果は小さいと見られる．また,処理時間の平均・分散から画像にサイズについて前処理は影響が小さく,後処理は大きいことがわかる.
# 6. まとめと今後の課題
　[2]のモデルに対応した前処理と後処理を提案し，[2]よりも良い結果となった．しかし，出力の不安定さ，精度に関して問題がまだ残っており，今後の課題に前処理の改善,より少ないストロークで画像生成するクリーンアップ処理モデルの作成を挙げる．
# 参考文献
[1] Edgar Simo-Serra, Satoshi Iizuka, Hiroshi Ishikawa: "Real-Time Data-Driven Interactive Rough Sketch Inking" ACM Trans. Graph. 37, 4, Article 98 (2018)
https://esslab.jp/~ess/ja/research/inking/

[2] Mo Haoran, Simo-Serra Edgar, Gao Chengying, Zou Changqing and Wang Ruomei: “General Virtual Sketching Framework for Vector Line” ArtACM Transactions on Graphics 40,4,51:1—51:14 (2021)
https://markmohr.github.io/virtual_sketching/
