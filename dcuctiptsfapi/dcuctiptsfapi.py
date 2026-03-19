"""
Compatibility wrapper for the TSF endpoint.

The shared implementation now lives in dcuctipapi.py.
This file is intentionally small to avoid duplicate logic.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
from argparse import RawTextHelpFormatter
from datetime import datetime, timezone
import logging
import os
import sys
import traceback

try:
    from .dcuctipapi import (
        BASE_DIRECTORY,
        BUILD_VERSION,
        CTIP_API_FRAUD_TSF,
        CTIP_DATA_DIRECTORY,
        CtipApi,
        Config,
        ConfigureLogging,
        FormatDateTimeYMDHMS,
        LOG_FILENAME,
        log,
    )
except ImportError:
    from dcuctipapi import (
        BASE_DIRECTORY,
        BUILD_VERSION,
        CTIP_API_FRAUD_TSF,
        CTIP_DATA_DIRECTORY,
        CtipApi,
        Config,
        ConfigureLogging,
        FormatDateTimeYMDHMS,
        LOG_FILENAME,
        log,
    )


def main():
    logPath = os.path.dirname(LOG_FILENAME)
    if not os.path.exists(logPath):
        os.makedirs(logPath)

    ConfigureLogging()

    parser = argparse.ArgumentParser(
        description='dcuctiptsfapi - DCU CTIP API Download Utility\n\nConnects to the CTIP API to download and process DCU CTIP TSF data.',
        prog='dcuctiptsfapi.py',
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument('--subscription-key', '-key', required=True, help='The CTIP API access key issued by DCU [required]')
    parser.add_argument('--subscription-name', '-sn', default='dcuctiptsfapi', help='Used to name downloaded data files')
    parser.add_argument('--days-ago', '-da', type=int, default=14, help='Timespan in days. Valid values are 1..180')
    parser.add_argument('--save-ctip-data', '-save', action='store_true', help='Save downloaded data to local files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.INFO)
    if args.debug:
        log.setLevel(logging.DEBUG)

    saveCtipDataFiles = bool(args.save_ctip_data)

    # Initialize to keep finally block safe even if setup fails.
    startTimestampUtc = datetime.now(timezone.utc)
    startTimestampLocal = datetime.now()

    try:
        if not os.path.exists(BASE_DIRECTORY):
            os.makedirs(BASE_DIRECTORY)
        if saveCtipDataFiles and not os.path.exists(CTIP_DATA_DIRECTORY):
            os.makedirs(CTIP_DATA_DIRECTORY)

        config = Config(
            ctipApi=CTIP_API_FRAUD_TSF,
            subscriptionName=args.subscription_name,
            subscriptionKey=args.subscription_key,
            daysAgo=args.days_ago,
            saveCtipDataFiles=saveCtipDataFiles,
        )

        log.critical(f'Build {BUILD_VERSION}')
        ctipTsfDataItems = CtipApi(config=config)
        log.critical(f'Total CTIP TSF Dataset Objects: {len(ctipTsfDataItems)}')

    except KeyboardInterrupt:
        log.error('dcuctiptsfapi.py aborted by user.')
        sys.exit(0)
    except Exception as error:
        log.error('General Error during dcuctiptsfapi.py processing.')
        log.error(f'Error: {error}')
        log.error(f'Call Stack:\n{traceback.format_exc()}')
    finally:
        endTimestampUtc = datetime.now(timezone.utc)
        endTimestampLocal = datetime.now()
        executionTime = endTimestampLocal - startTimestampLocal
        log.critical(
            f'dcuctiptsfapi started processing at:   {FormatDateTimeYMDHMS(startTimestampLocal)}L / {FormatDateTimeYMDHMS(startTimestampUtc)}Z'
        )
        log.critical(
            f'dcuctiptsfapi completed processing at: {FormatDateTimeYMDHMS(endTimestampLocal)}L / {FormatDateTimeYMDHMS(endTimestampUtc)}Z'
        )
        log.critical(f'dcuctiptsfapi total processing time:   {executionTime}')
        if saveCtipDataFiles:
            log.critical(f'CTIP data files: {CTIP_DATA_DIRECTORY}')
        log.critical(f'Log file: {os.path.join(os.getcwd(), LOG_FILENAME)}')


if __name__ == '__main__':
    main()
