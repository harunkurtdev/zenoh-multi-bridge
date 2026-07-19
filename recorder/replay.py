#!/usr/bin/env python3
"""
Replay / inspect the recorded archive.

Reads the JSONL files written by recorder.py and prints matching records.
Use this AFTER a shutdown to review exactly what the brokers saw.

Usage:
  python3 replay.py [--dir DIR] [--day YYYY-MM-DD] [--topic SUBSTR]
                    [--since ISO] [--until ISO] [--tail N]

Examples:
  # everything recorded today
  python3 replay.py --day 2026-07-19
  # only bot1 pose messages
  python3 replay.py --topic robots/bot1/telemetry/pose
  # last 20 records overall
  python3 replay.py --tail 20

Default DIR is ./records (or $RECORD_DIR). When running against the Docker
volume, point --dir at the mounted path.
"""
import argparse
import glob
import json
import os


def parse_args():
    p = argparse.ArgumentParser(description="Replay recorded broker archive")
    p.add_argument("--dir", default=os.getenv("RECORD_DIR", "./records"))
    p.add_argument("--day", default="*", help="YYYY-MM-DD or * for all days")
    p.add_argument("--topic", default=None, help="substring match on topic")
    p.add_argument("--since", default=None, help="ISO timestamp lower bound")
    p.add_argument("--until", default=None, help="ISO timestamp upper bound")
    p.add_argument("--tail", type=int, default=None, help="show only last N")
    return p.parse_args()


def main():
    args = parse_args()
    pattern = os.path.join(args.dir, args.day, "*.jsonl")
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"no records found under {pattern}")
        return 1

    records = []
    for path in files:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if args.topic and args.topic not in rec.get("topic", ""):
                    continue
                if args.since and rec.get("ts", "") < args.since:
                    continue
                if args.until and rec.get("ts", "") > args.until:
                    continue
                records.append(rec)

    records.sort(key=lambda r: r.get("ts", ""))
    if args.tail:
        records = records[-args.tail:]

    for rec in records:
        print(f"{rec.get('ts'):26s} {rec.get('topic'):45s} {json.dumps(rec.get('payload'), ensure_ascii=False)}")
    print(f"\n-- {len(records)} record(s) --")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
