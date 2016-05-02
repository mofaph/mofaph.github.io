---
title: 已解决问题集
layout: post
---

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
