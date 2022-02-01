#!/usr/bin/env python3

"""Origin client. Manage origins """

import argparse
import configparser
import re
import sys
import traceback
from logging import error
from pathlib import Path
from typing import Optional, Text

import act.api
from act.api.libs import cli


def parseargs() -> argparse.ArgumentParser:
    """Parse arguments"""
    parser = act.api.libs.cli.parseargs("ACT Origin utilities")
    parser.add_argument("--list", action="store_true", help="List origins")
    parser.add_argument("--add", action="store_true", help="Add origin")
    parser.add_argument("--delete", action="store_true", help="Delete origin")
    parser.add_argument(
        "--from-config",
        action="store_true",
        help="Add all origins defined in ~/.config/act/act.ini",
    )

    parser.add_argument("--origin-id", help="Origin ID (UUID)")

    # Trust is converted to float before sending a request to the platform
    # and since this value can come from an ini file (where it will be a string)
    # We keep the value as a string here
    parser.add_argument(
        "--default-trust", type=float, default="0.8", help="Default trust"
    )

    return parser


def float_or_fatal(value: Optional[Text]) -> Optional[float]:
    if value is None or value == "":
        return None

    try:
        return float(value)
    except ValueError:
        cli.fatal(f"Unable to {value} to float")


def add_origin_cli(actapi: act.api.Act, default_trust: float) -> None:
    sys.stdout.write("Origin name: ")
    name = input()
    sys.stdout.write("Origin description: ")
    description = input()
    sys.stdout.write("Origin trust (float 0.0-1.0. Default=0.8): ")
    trust = float_or_fatal(input())
    sys.stdout.write("Origin organization (UUID): ")
    organization = input()

    add_origin(actapi, name, description, default_trust, trust, organization)


def add_origin(
    actapi: act.api.Act,
    name: Text,
    description: Text,
    default_trust: float,
    trust: Optional[float] = None,
    organization: Optional[Text] = None,
) -> None:

    if not trust:
        trust = default_trust

    if not (trust >= 0.0 and trust <= 1.0):
        cli.fatal(f"Trust must be between 0.0 and 1.0: {trust}")

    params = {
        "name": name,
        "description": description,
        "trust": trust,
    }

    if organization:
        if not re.search(act.api.re.UUID_MATCH, organization):
            cli.fatal("Organization must be a valid UUID")

        params["organization"] = organization

    origin = actapi.origin(**params)
    try:
        origin.add()
        print("Origin added:")
        print(origin)
    except act.api.base.ResponseError as e:
        sys.stderr.write(f"Error adding origin: {e}\n")


def add_origin_from_config(actapi: act.api.Act, default_trust: float) -> None:
    """Get all origins from config in ~/.config/act/act.ini and add them to the platform"""

    config = configparser.ConfigParser()
    config.read(Path("~/.config/act/act.ini").expanduser())

    for section in config.sections():
        name = config[section].get("origin-name")
        if not name:
            continue

        organization = config[section].get("origin-organization")

        # Read origin description from config, default to name
        description = config[section].get("origin-description", name)

        # Get trust from config, default to default_trust
        trust = float_or_fatal(config[section].get("origin-trust", default_trust))

        add_origin(actapi, name, description, default_trust, trust, organization)


def origin_handler(actapi: act.api.Act, args: argparse.Namespace) -> None:
    "handle origins"

    try:
        if args.list:
            for origin in actapi.get_origins():
                print(origin)

        if args.from_config:
            add_origin_from_config(actapi, default_trust=args.default_trust)

        if args.add:
            add_origin_cli(actapi, default_trust=args.default_trust)

        if args.delete:
            actapi.api_delete("v1/origin/uuid/{}".format(args.origin_id))

            print("Origin deleted: {}".format(args.origin_id))

    except act.api.base.ResponseError as err:
        error("ResponseError while connecting to platform: %s" % err)


def main() -> None:
    "main function"
    try:
        # Look for default ini file in "/etc/act.ini" and ~/config/act/act.ini
        # (or replace .config with $XDG_CONFIG_DIR if set)
        args = cli.handle_args(parseargs())

        if not (args.act_baseurl):
            cli.fatal("--act-baseurl must be specified")

        if not (args.list or args.add or args.delete or args.from_config):
            cli.fatal("Specify either --list, --add or --delete")

        if (args.delete) and not (args.origin_id):
            cli.fatal("Specify --origin-id to delete an origin")

        actapi = cli.init_act(args)
        origin_handler(actapi, args)
    except Exception:
        error("Unhandled exception: {}".format(traceback.format_exc()))
        raise


if __name__ == "__main__":
    main()
