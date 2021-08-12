---
title: TWCC CLI α
tags: CLI, Test, TW
GA: UA-155999456-1
---

:construction_worker: :point_right: [工作人員專用]( https://man.twcc.ai/XP63CErkQve0tlN0oHxrcA) :warning: 非請勿入。

{%hackmd @docsharedstyle/default %}

# TWCC-CLI α

{%hackmd @tpl/draft_alert_zh %}
{%hackmd @tpl/draft_alert_en %}


本文件為 [TWCC-CLI v0.5](https://github.com/TW-NCHC/TWCC-CLI/tree/v0.5) 之使用手冊，詳細內容操作情境仍在持續更新。TWCC-CLI (Command Line Interface) 是 TWCC 的命令列工具。除了 TWCC 入口網站， TWCC-CLI 提供管理 TWCC 資源的另一種選擇！

以下提供如何安裝 TWCC-CLI、使用開發型容器服務(CCS, Container Computer Service)、虛擬運算服務(VCS, Virtual Computer Service)與雲端物件儲存服務(COS, Cloud Object Storage)的教學指南。

[TOC]

## 1. 部署操作環境 
### 1-1. 於TWCC開啟開發型容器

請自TWCC使用者介面登入後開啟「開發型容器」，並參考 :point_right: [連線使用方式](https://man.twcc.ai/@i_Qvgi7sQMKB7dGyGkWmdA/SJlZnSOaN?type=view#%E9%80%A3%E7%B7%9A%E4%BD%BF%E7%94%A8%E6%96%B9%E5%BC%8F)。
選擇 :point_right: [SSH登入](https://man.twcc.ai/@i_Qvgi7sQMKB7dGyGkWmdA/SJlZnSOaN?type=view#%E4%BD%BF%E7%94%A8-SSH-%E7%99%BB%E5%85%A5%E9%80%A3%E7%B7%9A)、或 :point_right: [Jupyter Notebook Terminal](https://man.twcc.ai/@i_Qvgi7sQMKB7dGyGkWmdA/SJlZnSOaN?type=view#%E4%BD%BF%E7%94%A8-Jupyter-Notebook)，登入。

![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_bd1965899991c86e8ce7eec67e8f6589.png)


:::info
:bulb: 若使用虛擬運算服務操作TWCC-CLI，請參考 :point_right: [於虛擬運算服務中操作TWCC-CLI](#Sup-於虛擬運算-VCS-服務中操作TWCC-CLI)
:bulb: TWCC CCS/VCS Ubuntu 20.04版本內建TWCC-CLI，可略過安裝步驟, 前往[1-3-進入-TWCC_CLI-環境並開始使用服務](/#1-3-進入-TWCC_CLI-環境並開始使用服務)
:::


### 1-2. 安裝TWCC-CLI

- 開啟Terminal，並安裝TWCC-CLI
```bash=https://cos.twcc.ai/SYS-MANUAL/uploads/upload_254250ac703ce730089c80d4a3b12b74.png
pip install TWCC-CLI
```
<!--

![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_254250ac703ce730089c80d4a3b12b74.png)




- 輸入指令確認是否安裝完成

```bash=
twccli
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_a791ca9aaadbaa57b921a60f93bdc3e6.png =60%x)
-->

:::warning
:information_source:  關於`twccli`指令與用途

|指令|用途|
|--|--|
|`-ch`|切換指定TWCC資源，適用於：VCS, VDS等|
|`config`|TWCC-CLI環境配置相關設定|
|`cp`|上傳、下載檔案功能，適用於：COS|
|`ls`|檢視指定TWCC資源資訊，適用於：CCS, COS, VCS, VDS等|
|`mk`|建立(調配)TWCC資源，適用於：CCS, COS, VCS, VDS等|
|`net`|網路設定相關操作，CCS, VCS|
|`rm`|刪除TWCC資源，適用於：CCS, COS, VCS, VDS等|

詳細操作請參考`-h` , `--help`
:::spoiler --help of config 
- `twccli config --help`

![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_9548b4ef631f10523848970cc03a0221.png =55%x)


:::


<!--
- 恭喜！安裝完成！
`--- You Succeed, We Succeed!! ---`
-->


### 1-3. 進入 TWCC_CLI 環境並開始使用服務

- 輸入您的TWCC用戶資訊：包含【TWCC API 金鑰】 與 【計畫編號】 
(請至TWCC使用者頁面 -> API金鑰管理)


```bash=
twccli config init
```
<!--
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_82db84339c641de466d2f25b3ca63d2b.png)


- 依據指示輸入語言、及其他參數設定
-->
- 輸入語言、及其他參數設定
```bash=
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export PYTHONIOENCODING=UTF-8
```

:::info
:bulb:查詢金鑰、計畫編號的方法：


- 登入 TWCC 後，點選右上角的使用者名稱，再點選「API 金鑰管理」

![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_f26e7534913315d3612142ebf3c2a46e.png)



<br>

- 便可檢視、複製您的金鑰、計畫編號
- 請記得==時常更新您的金鑰==，並且==避免使用主金鑰==、==主金鑰切勿外流==

![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_e507610ce46ec17b87b98ffd08df0063.png)


:::


:::info
#### :bulb: 更換使用計畫：

- 執行以下指令刪除金鑰，並再次「[進入 TWCC CLI 環境](https://man.twcc.ai/XP63CErkQve0tlN0oHxrcA?both#Step-3-%E9%80%B2%E5%85%A5-TWCC_CLI-%E7%92%B0%E5%A2%83%E4%B8%A6%E9%96%8B%E5%A7%8B%E4%BD%BF%E7%94%A8%E6%9C%8D%E5%8B%990)」，便可輸入其他計畫之金鑰
```bash=
rm -rf ~/.twcc_data
```

![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_acb61adc3c6c88a39afc53443805c6f6.png =80%x)
:::

- 確認用戶資訊、API金鑰、計畫編號正確

```bash=
twccli config whoami
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_357bb8bf5d9208b9e97187cbc56c58c9.png)

- 確認TWCC-CLI版本資訊（欲確認目前最新版本，請洽 :point_right: [TWCC-CLI github](https://github.com/TW-NCHC/TWCC-CLI/tree/v0.5)）
```bash=
twccli config version
```
### 1-4. TWCC_CLI 版本更新

- 使用以下指令進行CLI版本更新

```bash=
pip install -U TWCC-CLI
```

完成更新後，請重新確認使用者資訊
```
twccli config init
```

<!--
### 1-4. Error solved

- 若出現 credential 檔錯誤
:::warning
:warning: credential檔錯誤，請「[更換使用計畫](https://man.twcc.ai/XP63CErkQve0tlN0oHxrcA?both#-%E6%9B%B4%E6%8F%9B%E4%BD%BF%E7%94%A8%E8%A8%88%E7%95%AB%E7%9A%84%E6%96%B9%E6%B3%95%EF%BC%9A)」，並再次「[進入 TWCC CLI 環境](https://man.twcc.ai/XP63CErkQve0tlN0oHxrcA?both#Step-3-%E9%80%B2%E5%85%A5-TWCC_CLI-%E7%92%B0%E5%A2%83%E4%B8%A6%E9%96%8B%E5%A7%8B%E4%BD%BF%E7%94%A8%E6%9C%8D%E5%8B%990)」
```bash=
rm -rf $HOME/.twcc_data
```
:::


- 若 python 錯誤；ie: 安裝的是 python 3.6, 但環境已經切到 python 2.7 
:::warning
:warning: python版本錯誤，請移除TWCC-CLI、再重新「[安裝TWCC-CLI](https://man.twcc.ai/XP63CErkQve0tlN0oHxrcA?both#Step-2-%E5%AE%89%E8%A3%9DTWCC-CLI)」
```bash=
pip uninstall TWCC-CLI
pip install TWCC-CLI
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_1cd778a90c997944f2ccf2970862d26b.png)

:::

- 若出現語言問題；show `'ascii' codec can't encode characters in position 610-612: ordinal not in range(128)` 
:::warning
:warning: 更新CLI版本、或重新安裝CLI時，容易出現本問題，請輸入
```bash=
export LANG=C.UTF-8
```
:::
-->

## 2. 開發型容器服務(CCS, Container Computer Service)


:::info
:bulb: 注意：以 TWCC CLI 使用開發型容器服務，須先部署 TWCC CLI 的操作環境。參見本文件上方：[1. 部署操作環境](#1.-部署操作環境)
:::



:::warning
:information_source:  關於 CCS 指令與用途

|指令|用於|用途|
|--|--|--|
|`ls`|`ccs`|檢視開發型容器資訊|
|`mk`|`ccs`|建立開發型容器|
|`net`|`ccs`|設定開發型容器網路服務|
|`rm`|`ccs`|刪除開發型容器|

詳細操作請參考`-h` , `--help`

:::spoiler --help of CCS 

- `twccli ls ccs --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_4b48bac10c45dd38d3b5651a20ce1962.png =85%x)


- `twccli mk ccs --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_112dccdb8f5a5022afe92cbcf7c81ffa.png =85%x)

- `twccli net ccs --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_d7126b3e82d6f365c9e11630e705b030.png =80%x)

- `twccli rm ccs --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_71f943929ca40c8815599de9b6b62c4d.png =80%x)

:::



### 2-1. 建立開發型容器

- 以預設建立開發型容器
```bash=
twccli mk ccs
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_773cef50a5209a02cb4a73d2ab299a9a.png)

:::info
:bulb: 預設建立資訊：

| 映像檔類型、映像檔 | 容器名稱 |硬體設定|
| -------- | -------- | -------- |
| TensorFlow (latest environment)    | twcc-cli     | 1 GPU + 04 cores + 090GB memory |
:::

- 建立名為 `clitest` 的預設開發型容器
	
```bash=
twccli mk ccs -n clitest
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_85a289f188891ee3a35b7fa545b4a2a8.png)


:::info
:bulb: 注意：
- 容器名稱命名條件：字母須為小寫字母或數字、首字母為小寫字母、長度6-16個字母
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_095834bd7ee5d99d3a70596a7c462629.png)
- GPU 數量與其他資源的比例與定價請參考 :point_right: [TWCC 價目表](https://www.twcc.ai/doc?page=price#%E5%AE%B9%E5%99%A8%E9%81%8B%E7%AE%97%E6%9C%8D%E5%8B%99-Container-Compute-Service-CCS)
- TWCC 提供的映像檔類型、映像檔，可參考 :point_right: [2-3. 檢視所有容器規格](#2-3-檢視所有容器規格)
:::






### 2-2. 檢視容器資訊

- 檢視容器建立狀況，或可由TWCC使用者介面上確認容器建立完成

```bash=
twccli ls ccs
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_8c56a8a4bafb8fd5ee6b4913dc5d9c86.png)

- 檢視計劃下的所有容器 (僅限租戶管理員使用)
    
```bash=
twccli ls ccs -all
```




### 2-3. 檢視所有容器規格

- 檢視所有映像檔類型
```bash=
twccli ls ccs -itype
```

- 檢視所有映像檔規格
```bash=
twccli ls ccs -img
```

- 檢視所有映像檔gpu規格
```bash=
twccli ls ccs -gpu
```

### 2-4. 建立指定容器環境

- 檢視並確認欲建立之容器規格
- 建立映像檔類型`"Caffe2"`，映像檔規格為`"caffe2-18.08-py3-v1:latest"`、gpu數量 `2` 的容器，並命名 `cusccs`

```bash=
twccli ls ccs -itype
twccli ls ccs -itype "Caffe2" -img
twccli ls ccs -gpu
twccli mk ccs -itype "Caffe2" -img "caffe2-18.08-py3-v1:latest" -gpu 2 -n cusccs
```
:::spoiler 操作範例截圖(點我)
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_753112dc54b2646270806ad6385277ba.png)

:::


### 2-5. 檢視容器連線資訊

- 檢視容器 ID 為 `1249374` 的容器jupiter notebook連線資訊(URL)
- 以瀏覽器開啟URL，連線入jupyter notebook
```bash=
twccli ls ccs -s 1249374 -gjpnb
```
- 檢視容器 ID 為 `1249380` 的容器ssh連線資訊 
- 以ssh 連線
- 確認連線
- 輸入主機帳號密碼


```bash=
twccli ls ccs -s 1249380 -gssh
ssh `連線資訊`
```
- 若要離開連線，輸入`exit`

:::spoiler 操作範例截圖(點我)
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_3df3fc886c7dba630952d7728f69df13.png)

![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_3c381b0a5da433a081b46cbd463701a4.png =65%x)

:::



### 2-6. 容器複本

- TWCC CLI 提供使用者客製化容器，在 TWCC 完成環境部署後，可保存容器複本，再次建立容器便能快速進入熟悉的工作環境。

:::warning
:information_source:  容器複本只能做一次！！
:information_source:  關於 CCS 的容器副本操作指令與用途

|指令|用於| 參數 |用途|
|--|--|--| -- |
|`mk`|`ccs`| `-dup` `-tag` | 建立副本申請 |
|`ls`|`ccs`| `-dup` | 檢視副本申請 |



詳細操作請參考`-h` , `--help`
:::

#### 2-6-1. 提出容器複本的申請

- 提出申請保留容器 ID 為 `934336` 的容器，image tag 自訂為 dup1
```bash=
twccli mk ccs -s 934336 -dup -tag dup1 
```


:::info
:bulb: 使用者需先在 TWCC 建立容器，並自行å°環境部署完成，才能提出此申請。
:::


#### 2-6-2. 檢視已提出的申請狀態

```bash=
twccli ls ccs -dup
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_3b392366c438096c660347681dd81ca7.png)


    
#### 2-6-3. 以複本建立客製化容器

- 檢視並確認欲建立之容器規格
- 建立`"Custom Image"`中，映像檔規格與tag為`"tensorrt-19.08-py3:dup1"`的容器，並命名 `dupcli`

```bash=
twccli ls ccs -img "Custom Image"
twccli mk ccs -itype "Custom Image" -img "tensorrt-19.08-py3:dup1" -n dupcli
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_3310c270ae57370c22704b470cccbe60.png)


![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_6b2071ecdbafd5db2f98fbbf11b3e2ea.png)





### 2-7 開啟與關閉對外服務埠

:::warning
:information_source:  關於 CCS 設定對外服務埠指令與用途

|指令|用於|用途|
|--|--|--|
|`ls`|`ccs`|檢視對外服務埠資訊|
|`net`|`ccs`|設定對外服務埠服務|


詳細操作請參考`-h` , `--help`
:::

- 確認ID為`886330`容器的對外服務埠現有狀態
```bash=
twccli ls ccs -p -s 886330
```
- 為ID`886330`容器，開啟號碼為`5000`的對外服務埠
```bash=
twccli net ccs -p 5000 -open -s 886330
```

- 確認開啟對外服務埠狀態
```bash=
twccli ls ccs -p -s 886330
```

- 為ID`886330`的容器，關閉號碼為`5000`的對外服務埠
```bash=
twccli net ccs -p 5000 -close -s 886330
```

- 確認關閉對外服務埠狀態
```bash=
twccli ls ccs -p -s 886330
```

:::spoiler 操作範例截圖(點我)
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_b507dbb6ae856ecc8b90162ad67683d6.png)
:::

### 2-8. 刪除容器

- 刪除 site_id 為 `934369` 的容器 
- 輸入command以檢視容器狀況，或可由TWCC使用者介面上確認容器刪除成功 

```bash=
twccli rm ccs -s 934369
twccli ls ccs
```

![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_e3796215a4743497651f9775672821d8.png)

## 3. 虛擬運算服務(VCS, Virtual Computer Service)


:::info
:bulb: 注意：以 TWCC CLI 使用虛擬運算服務，須先部署 TWCC CLI 的操作環境。參見本文件上方：[1. 部署操作環境](#1.-部署操作環境)
:::

:::warning
:information_source:  關於 VCS 指令與用途

|指令|用於|用途|
|--|--|--|
|`ls`|`vcs`|檢視虛擬運算個體資訊|
|`mk`|`vcs`|建立虛擬運算個體|
|`net`|`vcs`|設定虛擬運算網路服務|
|`rm`|`vcs`|刪除虛擬運算個體|

詳細操作請參考`-h` , `--help`
:::spoiler --help of VCS
- `twccli ls vcs --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_81afdf28977568cdd0564aeb4edec7c1.png =85%x)

- `twccli mk vcs --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_91ca28b894edd993cef430a95c563545.png =85%x)

- `twccli net vcs --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_f39c1dbbf2dd643c2bae60b03b401a98.png =85%x)

- `twccli rm vcs --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_d0fea3b853232f163db8d34425960ef6.png =85%x)

:::






### 3-1. 鑰匙對
鑰匙對是登入虛擬運算個體的憑證，建立個體之前，必須先取得或建立鑰匙對才能使用個體功能。
#### 3-1-1. 建立鑰匙對
- 輸入command以建立名為`key1`的鑰匙對

```bash=
twccli mk key -n key1
```

:::info
:bulb: 為方便管理，建議為每項鑰匙對命名
:::


#### 3-1-2. 檢視鑰匙對

- 輸入command以確認鑰匙對建立狀況，或可由TWCC使用者介面上確認鑰匙對建立完成

```bash=
twccli ls key
```

![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_752e44d40060a214fa67fba1db2a1ead.png)




### 3-2. 建立虛擬運算個體

- 以`key1`鑰匙對建立預設虛擬運算個體

	
```bash=
twccli mk vcs -key key1
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_da00ae8f99a9be5b6aebcc3256ff4348.png)

:::info
:bulb: 預設建立資訊：

| 映像檔類型、映像檔 | 型號 | 網路資訊 | 硬體設定 |
| ------------ | ------ | ------ | ------ |
| Ubuntu 16.04  | v.2xsuper  | default_network  |0 GPU + 8 CPU + 064GB memory |
:::


- 以`key1`鑰匙對建立名為 `vcscli` 的虛擬運算個體

```bash=
twccli mk vcs -key key1 -n vcscli
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_caf838448cdc6dd7a389125f503a0785.png)


:::info
:bulb: 注意：
- 虛擬運算個體名稱命名條件：
字母須為小寫字母或數字、首字母為小寫字母、長度6-16個字母
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_095834bd7ee5d99d3a70596a7c462629.png)
- GPU 數量與其他資源的比例與定價請參考 :point_right: [TWCC 價目表](https://www.twcc.ai/doc?page=price#%E8%99%9B%E6%93%AC%E9%81%8B%E7%AE%97%E6%9C%8D%E5%8B%99-Virtual-Compute-Service-VCS)
- TWCC 提供的映像檔類型、映像檔，可參考:point_right: [3-4. 檢視所有虛擬運算個體規格](#3-4-檢視所有虛擬運算個體規格)

:::

#### 3-2-1. 為虛擬運算個體建立公用IP

- 為ID`937648`虛擬運算個體，建立公用IP
- 檢視是否建立成功
```bash=
twccli net vcs -s 937648 -fip
twccli ls vcs
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_565a7f89f09a26306182a00123a02929.png)


### 3-3. 檢視虛擬運算個體資訊

- 檢視虛擬運算個體狀況，或可由TWCC使用者介面上確認虛擬運算個體建立完成

```bash=
twccli ls vcs
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_b59214e6a5aa3939d5e679b2b43761eb.png)

:::info
:bulb:使用cli建立的虛擬運算個體將不預設公用IP，欲設定公用IP請參考:point_right: [3-2-1. 為虛擬運算個體建立公用IP](#3-2-1-為虛擬運算個體建立公用IP)
:::

- 檢視計劃下的所有虛擬運算個體 (僅限租戶管理員使用)

```bash=
twccli ls vcs -all
```


### 3-4. 檢視所有虛擬運算個體規格

- 檢視所有映像檔規格
```bash=
twccli ls vcs -img
```

- 檢視所有映像檔產品型號與規格
```bash=
twccli ls vcs -ptype
```


### 3-5. 建立客製化虛擬運算個體 :warning: (TBD..)

- 檢視並確認欲建立之虛擬運算規格
- 以客製規格建立虛擬運算個體
<font color=gray>(後續將持續更新功能與使用範例..)</font>
<!--
- 檢視並確認欲建立之容器規格
- 建立映像檔類型`"Caffe2"`，映像檔規格為`"caffe2-18.08-py3-v1:latest"`、gpu數量 `2` 的容器，並命名 `cusccs`

```bash=
twccli ls ccs -itype
twccli ls ccs -itype "Caffe2" -img
twccli ls ccs -gpu
twccli mk ccs -itype "Caffe2" -img "caffe2-18.08-py3-v1:latest" -gpu 2 -n cusccs
```
:::spoiler 操作範例截圖(點我)
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_753112dc54b2646270806ad6385277ba.png)

:::
-->


### 3-6. 虛擬運算個體快照 :warning: (TBD..)

- TWCC CLI 提供使用者客製化虛擬運算個體，在 TWCC 完成環境部署後，可保存虛擬運算個體快照(建立快照)，再次建立虛擬運算個體便能快速進入熟悉的工作環境。

:::warning
:information_source:  關於 VCS 的個體快照操作指令與用途

|指令|用於| 參數 |用途|
|--|--|--| -- |
|`mk`|`vcs`| `-snap` | 建立快照申請 |
|`ls`|`vcs`| `-snap` | 檢視快照申請 |
|`rm`|`vcs`| `-snap` | 移除快照 |


詳細操作請參考`-h` , `--help`
:::

#### 3-6-1. 提出虛擬運算個體快照的申請

- 為 ID 為 `918628` 的虛擬運算個體建立快照
```bash=
twccli mk vcs -s 918628 -snap
```

:::info
:bulb: 使用者需先在 TWCC 建立虛擬運算個體，並自行將環境部署完成，才能提出此申請。
:::


#### 3-6-2. 檢視已提出的申請狀態
 
- 檢視為 ID 為 `918628` 的虛擬運算個體建立的快照狀態
```bash=
twccli ls vcs -snap -s 918628  
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_19ffc79130c118e2642598005944ffa5.png)

    
#### 3-6-3. 以快照建立虛擬運算個體 :warning: (TBD..)

<font color=gray>(後續將持續更新功能與使用範例..)</font>

<!--
:::spoiler 待更新

- 使用以下指令，以複本直接建立虛擬運算個體

```bash=
# 可使用 list-all-img 查詢所有「映像檔類型」與「映像檔」名稱
pipenv run python gpu_cntr.py create-cntr -img <Custom Image Name> -sol <Image Type Name>
```

- 複本的映像檔類型名稱皆為 「Custom Image」、映像檔名稱為使用者自訂的「image name:image tag」

```bash=
pipenv run python gpu_cntr.py create-cntr -img copyofimg:latest -sol Custom Image
```

:::

-->

#### 3-6-4. 檢視全部快照資訊

- 檢視使用者所有快照資訊
```bash=
twccli ls vcs -snap
```

- 檢視計畫下的所有快照資訊 (僅限租戶管理員使用)
```bash=
twccli ls vcs -snap -all
```

#### 3-6-5. 刪除快照

- 刪除ID為`115453`的快照
```bash=
twccli rm vcs -snap -snap-id 115453
```
<!--
- 刪除ID為`115453`的快照 :warning: 
```bash=
twccli rm vcs -snap -snap-id 115453
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_233792a3772ff18505d8c7163fd46bd0.png)

:::warning
:warning: 目前快照狀況為QUEUED狀況不可刪除 :point_left:  ... solving
:::

-->

#### 3-6-6. 設定定時快照 :warning:

:::warning
:warning: 本項功能目前僅能使用於『虛擬運算服務操作TWCC-CLI』

:bulb: **若需使用虛擬運算服務操作TWCC-CLI**，詳見 :point_right: [於虛擬運算服務中操作TWCC-CLI](#於虛擬運算-VCS-服務中操作TWCC-CLI)
:::

- 使用 `crontab -e` 進行設定，相關使用功能請參照 [CronHowTo](https://help.ubuntu.com/community/CronHowto)。
![](https://i.imgur.com/1zRke01.png)

- 指定任意時間進行快照工作，在此為範例為==午夜 01:01==。
![](https://i.imgur.com/WWwg1ZJ.png)




### 3-7 安全性群組管理

:::warning
:information_source:  關於 VCS 的安全性群組操作指令與用途

|指令|用於| 參數 |用途|
|--|--|--| -- |
|`ls`|`vcs`| `-secg`*必要 / `-s`*必要 | 查詢安全性群組 |
|`net`|`vcs`|`-secg`*必要 / `-s`*必要 | 設定安全性群組 |
|`rm`|`vcs`|`-secg`*必要 / `-s`*必要 | 移除安全性群組 |


詳細操作請參考`-h` , `--help`
:::




針對您所建立的虛擬機可各別進行安全性群組管理，其功能即為 TWCC 提供的免費防火牆，可確保您的計算資源的存取來源或目的網路及服務埠均在控管的範圍。使用方試如下：

#### 3-7-1 列出虛擬機現有安全性群組 (Security Group, *secg*)

- 列出現有虛擬機安全性群組，可透過下列指令進行查詢：
```bash=
twccli ls vcs # 列出現有虛擬機
twccli ls vcs -secg -s 937648 # 列出ID為937648虛擬機的安全性群組
```


#### 3-7-2 設定安全性群組

:::info
若要進行設定網路安全性群組，請使用 `twccli net vcs --help` 進行查詢各細項功能
:::

- 若要設定對安全網路段：==10.10.10.0/24==，開放 ==TCP:81== 埠的連入(ingress)，使用指令如下，
```bash=
twccli net vcs -secg -s 892486 -cidr 10.10.10.0/24 -in -proto tcp -p 81
twccli ls vcs -secg -s 892486
```
:::spoiler 操作範例截圖(點我)
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_c3070ab4f93cd206e3945c68e786abfb.png)
:::

#### 3-7-2 移除安全性群組 :warning: 

若要取消已設定的安全性群組，可使用 :point_right: `twccli rm vcs -secg $SecurityGroupId `

:::info
:bulb: 刪除安全性群組的時候，請使用安全性群組的 UUID 進行刪除。
UUID 最短僅需提供==前8碼==，即可進行刪除。 
:::
參考範例:point_down:：
```bash
twccli rm vcs -secg ff781775
```
<font color=gray>(後續將持續更新功能與使用範例..)</font>
<!--
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_e417d476e63f85c5a17981d261a46df2.png)

再進行查詢

```bash
twccli ls vcs -s 892486
```

![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_d0a392b515b3d778122cebe86b668c8d.png)
-->

### 3-8. 刪除虛擬運算個體與鑰匙對

#### 3-8-1. 刪除虛擬運算個體
- 刪除 site_id 為 `937651` 的虛擬運算個體 
```bash=
twccli rm vcs -s 937651
```

- 輸入command以檢視虛擬運算個體狀況，或可由TWCC使用者介面上確認虛擬運算個體刪除成功 

```bash=
twccli ls vcs
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_024803eddc7136ec4fa25af5fe2ddc84.png)


#### 3-8-2. 刪除鑰匙對
- 刪除名稱為 `key1` 的鑰匙對 
```bash=
twccli rm key -n key1
```
:::info
:bulb: 注意:
刪除後, 請自行刪除本機端鑰匙對
:::spoiler
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_0ebc5f5ed8ea2bff1c5e0d8311873eb5.png)
:::

- 輸入command以檢視鑰匙對狀況，或可由TWCC使用者介面上確認虛擬運算個體刪除成功 

```bash=
twccli ls key
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_d51dddfaf2ad0cb9b2eb6d67f8967824.png)



## 4. 雲端物件儲存服務(COS, Cloud Object Storage)

:::info
:bulb: 注意：

- 若在開發型容器內使用雲端物件儲存、存取資料，需先在容器環境內部署 TWCC CLI 工具。參見本文件上方：1. 部署操作環境 
- 一般檔案管理 (上傳/刪除/搜尋Metadata/設定通知)，亦可於 TWCC 入口網站內操作，參見：[雲端物件儲存](https://www.twcc.ai/doc?page=object&euqinu=true)
:::



:::warning
:information_source:  關於 COS 指令與用途

|指令|用於|用途|
|--|--|--|
|`cp`|`cos`|上傳、下載檔案至雲端儲存體|
|`ls`|`cos`|檢視雲端儲存體資訊|
|`mk`|`cos`|建立雲端儲存體|
|`rm`|`cos`|刪除雲端儲存體|

詳細操作請參考`-h` , `--help`
:::spoiler --help of COS
- `twccli cp cos --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_d8f07b9dbf9217d1ffb6df2b78787953.png =85%x)

- `twccli ls cos --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_623d7615781afa9cfc70734c20663b67.png =85%x)

- `twccli mk cos --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_b26addeb3b5c79b2d7f17284e4ef45fd.png =55%x)

- `twccli rm cos --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_78464b3af8041812c1ddfcb0a96fb2c7.png =85%x)
:::

### 4-1. 建立儲存體

- 建立名為 `bk_cli` 的儲存體

```bash=
twccli mk cos -bkt clibkt
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_50624da8b602a49ae4ed172882d01693.png)




### 4-2. 檢視所有儲存體

```bash=
twccli ls cos
```


### 4-3. 上傳檔案至儲存體

:::info
:bulb: 上傳檔案可藉『相對路徑』、『絕對路徑』擷取資料傳入儲存體
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_66f6bc7fd0b69de7274d2a3251a5a817.png)
 
:::


#### 4-3-1. 上傳單一檔案 `-sync to-cos`

- 自當前路徑上傳單一檔案(檔名：`testfile1`)
- 並利用檢視指令確認檔案是否成功上傳目標儲存體`clibkt`
```bash=
twccli cp cos -bkt clibkt -fn testfile1 -sync to-cos
twccli ls cos -bkt clibkt
```


- 自相對路徑上傳單一檔案(檔名：`test1`)至目標儲存體`testf1/`目錄下

```bash=
twccli cp cos -bkt clibkt -dir testf1/ -fn test1 -sync to-cos
```

- 上傳相對路徑資料夾的所有檔案(資料夾：`testf2`) 至目標儲存體 

```bash=
twccli cp cos -bkt clibkt -dir testf2 -sync to-cos
```

### 4-4. 檢視儲存體的所有檔案

- 檢視儲存體`clibkt` 中所有檔案資訊

```bash=
twccli ls cos -bkt bk_cli
```
    
<!--![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_846285e100fa61b42acb4bcecca3ffc5.png)-->



### 4-5. 下載儲存體檔案 或 整個儲存體 `-sync from-cos` 




- 自儲存體下載單一檔案(檔名:`testfile1`)至當前資料夾
- 並檢視是否下載成功

```bash=
twccli cp cos -bkt clibkt -okey testfile1 -sync from-cos
twccli ls cos -bkt clibkt
```


![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_139476a0ef51c83f649a32e43a8feb3a.png)

<!--


- 自儲存體下載一檔案(檔名:`testfile2`)至指定目錄`download`

```bash=
twccli cp cos -bkt clibkt -dir ./ -fn testfile2 -sync from-cos
```
-->

    

- 下載整包儲存體至指定目錄 
- 並檢視是否下載成功
```bash=
twccli cp cos -bkt clibkt -dir download/ -sync from-cos
twccli ls cos -bkt clibkt
```

![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_a7d7d0ece77cba4025908f4c48453de6.png)






### 4-6. 刪除儲存體資料

:::danger
這個操作會對您的資料完全刪除，請小心使用。
:::


- 刪除儲存體 `clibkt` 的 `testfile2` 檔案
```bash=
twccli rm cos -bkt clibkt -okey testfile2
```   
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_4b80abb6e5602730e663bc44d8a9c751.png)



### 4-7. 刪除儲存體
:::info
:bulb: 刪除儲存體前，請先檢視`ls`目標儲存體是否已清空資料 :point_right: `null`
:::



- 刪除「已清空」的儲存體 `clibkt1` 
```bash=
twccli ls cos -bkt clibkt1
twccli rm cos -bkt clibkt1
```  
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_7ed99a3b7787f3e7ef0355aacc667e9e.png)


- 刪除「未清空」的儲存體 `clibkt`
```bash=
twccli ls cos -bkt clibkt
twccli rm cos -bkt clibkt -r
```  
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_0e3dec4ebaa2a1de12ed047c41396e07.png)


## 5. 虛擬網路 (Virtual Network)

:::warning
:information_source:  關於 VNET 指令與用途

|指令|用於|用途|
|--|--|--|
|`ls`|`vnet`|檢視虛擬網路資訊|
|`mk`|`vnet`|建立虛擬網路|
|`rm`|`vnet`|刪除虛擬網路|

詳細操作請參考`-h` , `--help`
:::spoiler --help of VNET
- `twccli ls vnet --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_ad89f34a5cf690dd6504a4dd69c4b8df.png)


- `twccli mk vnet --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_b9672ae00475ac090489830730f4606f.png)


- `twccli rm vnet --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_2e5f36de8634aae85f98cae62e69e06e.png)

:::

### 5-1. 建立虛擬網路
- 以網段 `172.16.0.0/24` 及閘道 `172.16.0.254` 建立虛擬網路
```bash=
twccli mk vnet -cidr 172.16.0.0/24 -gw 172.16.0.254
```

:::info
:bulb: 注意：
- 192.168.1.0/24 為系統保留的 CIDR，請不要使用。
:::

<!--
- `-cidr` 與 `-gw` 為建立虛擬網路時必要項目。
-->

### 5-2. 檢視虛擬網路
- 檢視所有虛擬網路
```bash=
twccli ls vnet
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_22c4fb8cc6f57701ebd4ea204cf24dd3.png)

- 檢視特定虛擬網路`261894`詳細資訊
```bash=
twccli ls vnet -id 261894
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_e50cd7936738b7be4055b0212adf4d21.png)


### 5-3. 刪除虛擬網路
- 刪除虛擬網路`261894`
```bash=
twccli rm vnet -id 261894
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_0c4cfd1922b2c8d9e112138bd119b29d.png)


![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_f0d90990195ff56580020b195dd744be.png)


## 6. 虛擬磁碟服務(Virtual Disk Service)

:::warning
:information_source:  關於 VDS 指令與用途

|指令|用於|用途|
|--|--|--|
|`ls`|`vds`|檢視虛擬磁碟服務資訊|
|`mk`|`vds`|建立虛擬磁碟服務|
|`rm`|`vds`|刪除虛擬磁碟服務

|

詳細操作請參考`-h` , `--help`
:::spoiler --help of VNET
- `twccli ls vnet --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_485dacba7996fb5101c51b62dc035a29.png)


- `twccli mk vnet --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_7be36cc4baf8e508f0093b19ac336bc8.png)


- `twccli rm vnet --help`
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_8b2007a1e2dc32d617b540ebceff2179.png)

:::

### 6-1 建立虛擬磁碟服務

- 以預設建立虛擬磁碟服務
```bash=
twccli mk vds
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_45a19e410de03a0975d7a88913f7f5f7.png)

:::info
:bulb: 預設建立資訊：

| 虛擬磁碟服務類型 | 虛擬磁碟服務名稱 | 虛擬磁碟服務容量大小  |
| -------- | -------- | -------- |
| HDD | twccli     | 100 GB |
:::

- 建立名為 `clitest` ，且指定儲存容量為`10` GB的虛擬磁碟服務
```bash=
twccli mk vds -n clitest -sz 10
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_3da7383c28c4700cd8429fbbb282a58d.png)

### 6-2 檢視虛擬磁碟服務資訊

- 檢視虛擬磁碟服務建立相關資訊
```bash=
twccli ls vds
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_c976443120fa105196269359143aeb3a.png)

### 6-3 刪除虛擬磁碟服務

- 刪除ID為`376749`的虛擬磁碟服務
```bash=
twccli rm vds -id 376749
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_e2a0873513f1cc8f60be01a78ae3b456.png)

- 強制(無警告視窗)刪除ID為`376716`的虛擬磁碟服務 
```bash=
twccli rm vds -id 376749 -f
```


---

## Sup. 於虛擬運算 VCS 服務中操作TWCC-CLI

### Sup-1. 開啟虛擬運算服務

- 開啟虛擬運算服務
:::info
請參考 :point_right: [虛擬運算服務-建立虛擬運算個體](https://www.twcc.ai/doc?page=vm)
:::

- 連線至虛擬運算服務
:::info
請參考 :point_right: [虛擬運算服務-連線虛擬運算個體](https://www.twcc.ai/doc?page=vm)
:::

### Sup-2. 安裝TWCC-CLI

- 連線成功後，更新與安裝套件工具(視情況選擇安裝python2或python3版本)
```bash=
sudo apt update
sudo apt install python-pip #in python2
sudo apt install python3-pip #in python3
```
<!--
```bash=
wget -q -O - https://bit.ly/2VcPgRE | bash
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_beaec884461605d251737e9e47e9df8a.png)

出現下圖，表示成功安裝

![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_ce36329d30ae65cd29a20828cd8caa24.png)
-->


- 安裝TWCC-CLI(請注意上一步`pip`套件之python版本)
```bash=
pip install TWCC-CLI #in python2
pip3 install TWCC-CLI #in python3
```
- 輸入設定指令，並確認是否安裝完成
```bash=
twccli
```
<!--
```bash=
. .bashrc
twccli
```
:::warning
:information_source: 必須先輸入`. .bashrc`，才算設定完畢
再輸入`twccli` 以確認安裝完成
:::
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_e64396dc8bbdfcc87de7eed0cdd529cb.png)
-->

### Sup-3. 輸入您的TWCC-CLI用戶資訊

:::info

:information_source: 接續本文 :point_right: [#1-3-進入-TWCC_CLI-環境並開始使用服務](#1-3-進入-TWCC_CLI-環境並開始使用服務)
:::
<!--
### Sup-4. Error Solved
- TWCC-CLI安裝路徑問題
:::warning
:warning: install成功後，出現`twccli: command not found`；
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_3bd9eb685a4f792a41dd61b5e067ae5f.png)

- 請確認TWCC-CLI安裝路徑，並設定$PATH路徑環境變數
```bash=
sudo find / -name twccli
export PATH=路徑:$PATH
```
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_55b9287571e87ba62614291ad432d93c.png)
![](https://cos.twcc.ai/SYS-MANUAL/uploads/upload_47e4050c06b225b87e77c370f89bc7f1.png)

::: 
-->
