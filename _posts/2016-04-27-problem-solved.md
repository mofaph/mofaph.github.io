---
layout: post
title: 常见问题解决
---

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
