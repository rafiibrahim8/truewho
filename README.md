[![License][License-shield]][License-url]

# truewho

#### Check a phone number for name with Truecaller in command line.

# DISCLAIMER
This program is for educational purpose only. I am not responsible for any misuse of the program.

# DESCRIPTION
[Truecaller](https://www.truecaller.com/) is an app available for android and iOS for viewing caller ID.
However, it is possible to view caller ID without installing the app using API. The progrom does this in a command line.

# INSTALLATION
From a command line enter the command to install truewho
```
pip install git+https://github.com/rafiibrahim8/truewho.git --upgrade
```
You need to have python 3 installed. truewho won't run on python 2.
# USES
Frist you need to make a config file (which contains authentication key) by running:
```sh
$ truewho -k
```
Then you can simply run:

```sh
$ truewho -l +88017XXXXXXXX
```
to view name and country. Use `truewho --help` for full commands list.

# ISSUES

This is very early stage of the program. And I only tested it in my country. It might not work very well in your country. In that case you are always welcome to [create an issue](https://github.com/rafiibrahim8/truewho/issues) or [submit a pull request](https://github.com/rafiibrahim8/truewho/pulls).

[License-shield]: https://img.shields.io/github/license/rafiibrahim8/truewho
[License-url]: https://github.com/rafiibrahim8/truewho/blob/master/LICENSE

