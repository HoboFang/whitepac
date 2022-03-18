# whitepac

本PAC为白名单模式，其中包含了所有特殊IP及CN地区IP；即特殊IP与CN地区直连，其他走代理。

相比使用域名作为白名单，使用IP段不会有遗漏且无需频繁更新。

IP信息提取自以下两个文件：

<https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.txt>
<https://ftp.apnic.net/stats/apnic/delegated-apnic-latest>

SwitchyOmega与Firefox已测试，PAC链接：

<https://raw.githubusercontent.com/HoboFang/whitepac/main/whiteip.pac>

生成指定地区PAC:

`./pacproducer.py CN HK MO TW`

更新IP文件:

`./pacproducer.py -u`

