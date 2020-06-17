# Docker Hub Update Notifier [![Release build status](https://github.com/roy-n-roy/DockerHubUpdateNotifier/workflows/Release%20build/badge.svg)](https://github.com/roy-n-roy/DockerHubUpdateNotifier/actions) [![Nightly build status](https://img.shields.io/docker/cloud/build/roynroy/docker-hub-update-notifier?label=Nightly%20build)](https://hub.docker.com/r/roynroy/docker-hub-update-notifier/builds)
Docker hubのリポジトリをタグ単位で監視し、更新があった場合に通知します。

下記のURLから利用できます。(You can use it by going to the following URL.)  

[![Website](https://img.shields.io/website?label=https%3A%2F%2Fcontainer-image.live-on.net&url=https%3A%2F%2Fcontainer-image.live-on.net)](https://container-image.live-on.net)  
https://container-image.live-on.net

<img src="https://github.com/roy-n-roy/DockerHubUpdateNotifier/raw/master/django/repos/static/images/top_jp.png" width="70%" />  
<img src="https://github.com/roy-n-roy/DockerHubUpdateNotifier/raw/master/django/repos/static/images/repo_add_jp.png" width="70%%" />  

## HOW TO SELF HOST

もし、セルフホストしたい場合は下記のコマンドを実行してください。 (If you want to self-host,)  

```
> git clone https://github.com/roy-n-roy/DockerHubUpdateNotifier.git
> docker-conpose up -d --build
```

その後、 http://localhost/ へアクセスしてください。 (Access To "http://localhost/")  
