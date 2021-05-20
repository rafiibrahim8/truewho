from argparse import ArgumentParser
import requests
import click
import json
import os

from .utils import get_marketplace_version
from .utils import get_token
from . import colors
from . import __version__

__default_endpoint__ = "https://search5-noneu.truecaller.com/v2/search"
__default_config_path__ = "~/.config/truewho-config.json"
__default_tc_version__ = "11.59.8"


def resolve_config_path(config_path):
    if isinstance(config_path, tuple) or config_path == None:
        config_path = __default_config_path__
    return config_path

def mk_config(path):
    path = path if path else __default_config_path__
    exp_path = os.path.expanduser(path)
    dir_path = os.path.dirname(exp_path)

    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    if os.path.exists(exp_path):
        print(f"Config file at {path} already exist.")
        overwite = click.confirm("Do you want to overwrite it?", default=False)
        if not overwite:
            return
    print("Checking current Truecaller version. Please wait...")
    tc_version = get_marketplace_version("com.truecaller")
    tc_version = tc_version if tc_version else __default_tc_version__
    auth_token = get_token(tc_version)
    if auth_token == None:
        print("Authentication failed.")
        return

    auth_token, country_code = auth_token

    confg_json = {
        "auth_token": auth_token,
        "country_code": country_code,
        "tc_version": tc_version,
    }

    with open(exp_path, "w") as f:
        json.dump(confg_json, f)
    print("Authentication successful.")
    print("Config saved at:", path)


def do_search(
    number, auth_token, country_code, tc_version="11.59.8", android_version="5.1"
):
    params = {
        "q": number,
        "countryCode": country_code,
        "type": "2",
        "placement": "CALLERID,AFTERCALL,DETAILS",
        # 'adId':uuid.uuid4(),
        "encoding": "json",
    }

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "User-Agent": f"Truecaller/{tc_version} (Android;{android_version})",
    }
    try:
        res = requests.get(__default_endpoint__, params=params, headers=headers).json()
        name = res["data"][0].get("name", "")
        number_e164 = res["data"][0]["phones"][0]["e164Format"]
        country = res["data"][0]["phones"][0]["countryCode"]
    except:
        if res["status"] == 40101 or res["message"] == "Unauthorized":
            return None
        return number, "error", "error"
    return number_e164, name, country


def read_config(config_path):
    config_path = resolve_config_path(config_path)
    try:
        with open(os.path.expanduser(config_path), "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Unable to find config file at:", config_path)
        print(
            f"Please run {colors.red}truewho -k {config_path}{colors.end} to make the config file."
        )
        exit(11)
    except json.decoder.JSONDecodeError:
        print("The config file at", config_path, "is broken.")
        print(
            f"Please run {colors.red}truewho -k {config_path}{colors.end} to remake the config file."
        )
        exit(12)
    return config


def print_name_or_country(number, config_path, p_type="name"):
    assert p_type in ["name", "country"]
    config = read_config(config_path)
    data = do_search(
        number, config["auth_token"], config["country_code"], config["tc_version"]
    )
    if data == None:
        print("Token expired.")
        print(
            f"Please run {colors.red}truewho -k {resolve_config_path(config_path)}{colors.end} to remake the config file."
        )
        return
    _, name, country = data

    if p_type == "name":
        print(name)
    else:
        print(country)


def print_list(numbers, config_path):
    config = read_config(config_path)

    template_str = "{0: ^18} {1: ^30} {2: ^7}"

    for i, n in enumerate(numbers):
        data = do_search(
            n, config["auth_token"], config["country_code"], config["tc_version"]
        )
        if data == None:
            print("Token expired.")
            print(
                f"Please run {colors.red}truewho -k {resolve_config_path(config_path)}{colors.end} to remake the config file."
            )
            return
        if i == 0:
            print(template_str.format("Number", "Name", "Contry"))
            print(template_str.format("--------", "------", "-------"))
        number, name, country = data
        print(template_str.format(number, name, country))


def main():
    parser = ArgumentParser(description="Query phone number with TrueCaller.")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"v{__version__}",
        help="Show version information.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-n", "--name", metavar="NUMBER", help="Query for the name of the number."
    )
    group.add_argument(
        "-c", "--country", metavar="NUMBER", help="Query for the country of the number."
    )
    group.add_argument(
        "-l",
        "--list",
        metavar="NUMBER",
        nargs="+",
        help="Print a list of number(s) to queried.",
    )
    parser.add_argument(
        "-k",
        "--config",
        metavar="PATH",
        nargs="?",
        default=("not_passed",),
        help="Genarate config OR Select config file when using -l/--list. ",
    )
    args = parser.parse_args()

    if (
        args.config == ("not_passed",)
        and args.list == None
        and args.name == None
        and args.country == None
    ):
        parser.print_usage()
    elif (
        args.config != ("not_passed",)
        and args.list == None
        and args.name == None
        and args.country == None
    ):
        mk_config(args.config)
    elif args.name:
        print_name_or_country(args.name, args.config)
    elif args.country:
        print_name_or_country(args.country, args.config, p_type="country")
    else:
        print_list(args.list, args.config)


if __name__ == "__main__":
    main()
