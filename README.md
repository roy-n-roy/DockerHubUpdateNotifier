# Docker Hub Update Notifier
Docker hubのリポジトリをタグ単位で監視し、更新があった場合に通知します。

<img src="https://github.com/roy-n-roy/DockerHubUpdateNotifier/raw/master/django/repos/static/images/top_jp.png" width="70%" />  
<img src="https://github.com/roy-n-roy/DockerHubUpdateNotifier/raw/master/django/repos/static/images/repo_add_jp.png" width="70%%" />  

下記のURLから利用できます。  
You can use it by going to the following URL.  

URL: [Docker Hub Update Checker - https://container-image.live-on.net](https://container-image.live-on.net)

## HOW TO SELF HOST

もし、セルフホストしたい場合は下記のコマンドを実行してください。  
If you want to self-host,  

```
> git clone https://github.com/roy-n-roy/DockerHubUpdateNotifier.git
> docker-conpose up -d --build
```

その後、 http://localhost/ へアクセスしてください。  
Access To "http://localhost/"  

## TODO
- [ ] Webhook URLバリデーション
- [ ] 全タグ更新チェック対応
- [ ] 通知機能: IFTTT (Webhook)
