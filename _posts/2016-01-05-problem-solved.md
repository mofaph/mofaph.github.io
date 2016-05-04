---
title: 已解决问题集
layout: post
---

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
$ sudo yum install tmux
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
