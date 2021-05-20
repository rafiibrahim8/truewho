from phone_iso3166.country import phone_country_prefix
from phone_iso3166.network import country_networks
import requests
import datetime
import random
import string
import os
import re

onboarding_json_tmpl = {
    "countryCode": "bd",
    "dialingCode": 880,
    "installationDetails": {
        "app": {
            "buildVersion": 8,
            "majorVersion": 11,
            "minorVersion": 59,
            "store": "GOOGLE_PLAY",
        },
        "device": {
            "deviceId": "76931fac9dab2b36",
            "language": "en",
            "manufacturer": "unknown",
            "mobileServices": ["GMS"],
            "model": "Google",
            "osName": "Android",
            "osVersion": "5.1",
            "simSerials": ["8931027000000000007"],
        },
        "language": "en",
        "sims": [
            {
                "imsi": "310270000000000",
                "mcc": "310",
                "mnc": "270",
                "operator": "Android",
            }
        ],
    },
    "phoneNumber": "15XXXXXXXX",
    "region": "region-2",
    "sequenceNo": 2,
}


def get_marketplace_version(appId):
    try:
        res = requests.get(
            "https://play.google.com/store/apps/details",
            params={"id": appId, "hl": "en", "gl": "US"},
        )
        return re.findall("Current\\ Version[^.]+[^<]+", res.text)[0].split(">")[-1]
    except:
        pass


def calculate_luhn(sequence: str):
    sequence_rev = sequence[::-1]
    summ = 0
    for i, n in enumerate(sequence_rev, start=1):
        if i % 2 == 1:
            summ += int(n)
            continue
        n_x_2 = int(n) * 2
        n_x_2 = n_x_2 if n_x_2 < 10 else n_x_2 - 9
        summ += n_x_2
    return summ % 10


def genarate_luhn_checksum(sequence):
    luhn_digit = calculate_luhn(str(sequence) + "0")
    return luhn_digit if luhn_digit == 0 else 10 - luhn_digit


def genarate_iccid(imsi):
    iccid = f"89{imsi}0"
    return f"{iccid}{genarate_luhn_checksum(iccid)}"


def genarate_imsi(mcc, mnc):
    random_seq = "".join([random.choice(string.digits) for _ in range(9)])
    return f"{mcc:0>3}{mnc:0>3}{random_seq}"


def mk_onboarding_json(tc_version="8.12.59"):
    phone = input("Enter your phone with country code: ")
    prefix, country = phone_country_prefix(phone)
    networks = country_networks(country)
    v_build, v_major, v_minor = tuple(map(int, tc_version.split(".")))

    for i, network in enumerate(networks, start=1):
        print(f"{i}. {network[2]}")

    while True:
        try:
            option = int(input("\nChoose your oparator: "))
            network = networks[option - 1]
            break
        except (IndexError, ValueError):
            print(f"Please enter a number between 1 and {len(networks)}")

    onboarding_json_tmpl["countryCode"] = country.lower()
    onboarding_json_tmpl["dialingCode"] = prefix
    onboarding_json_tmpl["phoneNumber"] = phone.strip("+").replace(str(prefix), "", 1)
    onboarding_json_tmpl["installationDetails"]["sims"][0]["mcc"] = f"{network[0]:0>3}"
    onboarding_json_tmpl["installationDetails"]["sims"][0]["mnc"] = f"{network[1]:0>3}"
    onboarding_json_tmpl["installationDetails"]["sims"][0]["operator"] = network[
        2
    ].split(" ")[0]
    onboarding_json_tmpl["installationDetails"]["sims"][0]["imsi"] = genarate_imsi(
        network[0], network[1]
    )
    onboarding_json_tmpl["installationDetails"]["device"]["deviceId"] = "7" + "".join(
        [random.choice(string.hexdigits[:16]) for _ in range(15)]
    )
    onboarding_json_tmpl["installationDetails"]["device"]["simSerials"] = [
        genarate_iccid(onboarding_json_tmpl["installationDetails"]["sims"][0]["imsi"])
    ]
    onboarding_json_tmpl["installationDetails"]["app"]["buildVersion"] = v_build
    onboarding_json_tmpl["installationDetails"]["app"]["majorVersion"] = v_major
    onboarding_json_tmpl["installationDetails"]["app"]["minorVersion"] = v_minor

    return onboarding_json_tmpl


def format_timedelta(td):
    td = str(td)
    if "," not in td:
        td = "0 days, " + td
    days = int(td.split(",")[0].replace(" days", ""))
    hours = int(td.split(",")[1].strip().split(":")[0])
    mins = int(td.split(",")[1].strip().split(":")[1])
    secs = int(td.split(",")[1].strip().split(":")[2])

    tdp = {"day": days, "hour": hours, "minute": mins, "second": secs}
    tdp_str = ""
    for k, v in tdp.items():
        if v == 0:
            continue
        tdp_str += f"{v} {k}"
        if v > 1:
            tdp_str += "s "
        else:
            tdp_str += " "
    return tdp_str.strip()


def format_secs(secs):
    return format_timedelta(datetime.timedelta(seconds=secs))


def get_token(tc_version):
    headers = {
        "User-Agent": f"Truecaller/{tc_version} (Android;5.1)",
        "clientSecret": "lvc22mp3l1sfv6ujg83rd17btt",
    }
    jdata = mk_onboarding_json(tc_version)

    res = requests.post(
        "https://account-asia-south1.truecaller.com/v2/sendOnboardingOtp",
        headers=headers,
        json=jdata,
    ).json()

    if res["status"] != 1:
        print("Sending OTP failed. Reason:", res["message"])
        try_again_time = format_secs(res["tokenTtl"])
        print(f"Please try again after {try_again_time}.")
        return
    if res["method"] == "call":
        print("TrueCaller called your phone for verification.")
        print(
            "Unfortunately TrueWho does not support that method for verification now."
        )
        print("Please try again.")
        return

    print("SMS sent to", res["parsedPhoneNumber"])
    otp = input("Enter OTP: ").strip()

    jdata = {
        "countryCode": jdata["countryCode"],
        "dialingCode": jdata["dialingCode"],
        "phoneNumber": jdata["phoneNumber"],
        "requestId": res["requestId"],
        "token": otp,
    }

    res = requests.post(
        "https://account-asia-south1.truecaller.com/v1/verifyOnboardingOtp",
        headers=headers,
        json=jdata,
    ).json()

    if res["status"] != 2:
        print("Verifiction failed. Reason:", res["message"])
        return

    return res["installationId"], jdata["countryCode"].upper()
