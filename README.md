# Docker Hub Update Notifier
Docker hubのリポジトリをタグ単位で監視し、更新があった場合に通知します。
下記のURLから利用できます。

URL: [Docker Hub Update Checker - https://container-image.live-on.net](https://container-image.live-on.net)

## HOW TO USE

https://container-image.live-on.net へアクセスして利用するか、  
もし、セルフホストしたい場合は下記のコマンドを実行してください。  
If you want to self-host,  

```
> git clone https://github.com/roy-n-roy/DockerHubUpdateNotifier.git
> docker-conpose up -d --build
```

その後、 http://localhost/ へアクセスしてください。  
Access To "http://localhost/"  

## TODO
- [x] ログイン機能
- [x] ユーザー登録機能
- [x] ユーザー情報更新
- [x] 登録リポジトリ一覧表示
- [x] 一覧ページ送り
- [x] 通知機能: slack (Webhook)
- [x] 通知機能: メール
- [ ] 利用方法のページを作成
- [ ] Webhook URLバリデーション
- [ ] テスト
- [x] レスポンシブデザイン対応
- [ ] 全タグ更新チェック対応
- [x] ユーザ単位のタイムゾーン対応
- [ ] タグ一覧のサーバーサイドキャッシュ
- [ ] ドキュメント整備
- [ ] リポジトリ登録画面の初期フォーカス
- [x] 一覧のソート
- [ ] README整備
- [ ] 通知履歴画面
- [ ] 通知機能: IFTTT (Webhook)
- [x] 英語UI
- [ ] 画面フッター
