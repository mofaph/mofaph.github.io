---
title: 已解决问题集
layout: post
---

# 问题：如何自动部署静态博客文章到 Nginx？

解决方法：

{% highlight bash %}
\# adduser git
\# su - git
git$ git init --bare blog.git
git$ cat > blog.git/hooks/post-receive << EOF
#!/bin/sh

PATH=$HOME/bin:$PATH

BLOG_BARE_REPO=$HOME/blog.git
BLOG_BUILD_REPO=$HOME/buildblog
PUBLIC_WWW=/var/www

git clone $BLOG_BARE_REPO $BLOG_BUILD_REPO
jekyll build -s $BLOG_BUILD_REPO -d $PUBLIC_WWW

exit
EOF
git$ exit
\# mkdir /var/www
\# chown git:nginx /var/www
\# chmod 0755 /var/www
{% endhighlight %}

设置完了 Git 之后，开始设置 Nginx：

{% highlight Lua %}
server {
    listen 16328;
    index index.html index.htm;
    location / {
        root /var/www;
    }
}
{% endhighlight %}

{% highlight bash %}
user$ git remote add deploy git@localhost:~/blog.git
user$ git push deploy master
{% endhighlight %}

问题分析：

由于使用 Git 管理博客文章，那么需要在推送到服务端后，执行生成静态页面，然后将生
成的静态页面放到 Nginx 能够访问的目录中。

# 问题：如何在 CentOS-7 系统中，搭建一个本地的 Github 博客？

解决方法：

{% highlight bash %}
$ gem install bundler
$ mkdir newsite && cd newsite && git init
$ cat > Gemfile << EOF
source 'https://ruby.taobao.org/'
gem 'github-pages', group: :jekyll_plugins
EOF
$ bundle install
$ bundle exec jekyll serve
{% endhighlight %}

问题分析：

由于 Github Page 使用 Jekyll 搭建静态博客，而 Jekyll 依赖 Ruby 的开发包。由于需
要在本地搭建一个博客，那么也需要将 Github 的主题下来回来。

# 问题：在 CentOS-7 系统中，运行 gem install jekyll 失败

详细描述：

ERROR: Could not find a valid gem 'jekyll' (>= 0), here is why:

Unable to download data from https://rubygems.org/ - Errno::ECONNRESET:
Connection reset by peer - SSL_connect
(https://rubygems.org/latest_specs.4.8.gz)

解决方法：

{% highlight bash %}
$ gem sources -r https://rubygems.org/
$ gem sources -a https://ruby.taobao.org/
{% endhighlight %}

问题分析：

由于防火墙屏蔽了 rubygems.org。

# 问题：在 CentOS-7 系统中，官方源没法安装 nodejs

解决方法：

{% highlight bash %}
$ sudo yum install epel-release
$ sudo yum install nodejs
$ node --version
$ sudo yum install npm
{% endhighlight %}

# 问题：在 CentOS-7 系统中，安装后时间不一致

解决方法：

{% highlight bash %}
$ sudo yum install -y ntpdate
$ sudo ntpdate pool.ntp.org
$ sudo crobtab -e
30 * * * * ntpdate pool.ntp.org
$ sudo hwclock -w
{% endhighlight %}

# 问题：docker pull centos:7 无法完成

详细描述：

在 CentOS-7 中，安装官网的教程安装完了 docker 之后，使用 docker pull centos-7 不
能完成。安装和运行的命令如下：

{% highlight bash %}
$ curl -fsSL https://get.docker.com/ | sh
$ docker pull centos:7
{% endhighlight %}

解决方法：

{% highlight bash %}
$ sudo service docker start #1
{% endhighlight %}

# 问题：编译 zeromq-4.1. 时，不能找到 libsodium，但它已安装

问题详细描述：

在编译 zeromq-4.1.4 之前，已经手动编译安装了 libsodium-1.0.10

{% highlight bash %}
libsodium-1.0.10$ ./configure && make
libsodium-1.0.10$ sudo make install
libsodium-1.0.10$ ls /usr/local/lib
libsodium.a  libsodium.la*  libsodium.so@  libsodium.so.18@
libsodium.so.18.1.0*  pkgconfig/
libsodium-1.0.10$ ls /usr/local/lib/pkgconfig
libsodium.pc
{% endhighlight %}

解决方法：

{% highlight bash %}
zeromq-4.1.4$ PKG_CONFIG_PATH=/usr/local/lib/pkgconfig ./configure
{% endhighlight %}

原因分析：

在编译 zeromq 时，编译系统使用 pkg-config 来查找需要的库。但是 pkg-config 默认的
搜索路径不包括 /usr/local/lib/pkgconfig。

# 问题：CentOS-7 安装完了之后，不能进行开发工作

解决方法：安装开发包

使用 yum 安装的软件包：

{% highlight bash %}
$ sudo yum groupinstall "Development Tools"
$ sudo yum install zlib-devel bzip2-devel openssl-devel ncurses-devel \
    readline-devel tk-devel libpcap-devel xz-devel libxslt-devel libxml2-devel \
    libjpeg-devel libcurl-devel
$ sudo yum install tmux cmake cmake-doc
{% endhighlight %}

手动编译的软件包：

emacs
global
nginx
zeromq

# VMWare Workstation 8 安装 CentOS-7 没找到网卡

问题：在 VMWare Workstation 8 中，使用 minimal 镜像安装完 CentOS-7 之后，系统启
动后没有找到网卡。

解决方法：

在网络上找到这个解决方法：
[问题：Vmware无法识别网卡，导致虚拟机无法上网][vmware_nat]

[vmware_nat]: https://segmentfault.com/a/1190000004438657

打开虚拟机配置文件（.vmx），在配置文件中加入一行：

ethernet0.virtualDev = "e1000"

值为"e1000"指定网卡类型为Intel(R) PRO/1000
值为"vlance"指定网卡类型为AMD PCNet AM79C970A（默认为此项不兼容）
值为"vmxnet"指定网卡类型为VMware PCI Ethernet Adapter

原因分析：

Vmware虚拟网卡和linux兼容问题导致驱动无法正常安装，默认的网卡类型不兼容

# Python InsecurePlatformWarning

问题：在 CentOS-6.5 中，运行 pip install 时，出现如下的警告：

/usr/lib/python2.6/site-packages/pip/_vendor/requests/packages/urllib3/util/ssl_.py:90:
InsecurePlatformWarning: A true SSLContext object is not available. This
prevents urllib3 from configuring SSL appropriately and may cause certain SSL
connections to fail. For more information, see
https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning.

解决方法：

1. 升级到 Python 2.7.9
2. pip install --upgrade requests[security]

# 问题：`aptitude update`出现“无法重建软件包缓存”

问题描述：

见标题

解决方案：

* 换一个服务器
* 等待一段时间（几个小时或者几天），故障服务器可能会被修复

# 问题：wireshark启动后不能看到设备列表

问题详细描述：

在 ubuntu-14.04 系统中，使用 `sudo aptitude install wireshark` 安装之后，启动
wireshark，不能看到可以捕获的设备列表。

解决方案：

{% highlight bash %}
$ sudo dpkg-reconfigure wireshark-common # 允许普通用户捕获设备
$ sudo usermod -a -G wireshark $USER
$ sudo reboot
{% endhighlight %}
