#!/usr/bin/env python3
"""
Tech-Int CLI — Technology Intelligence Scanner
Usage: python3 cli.py [command] [options]
"""

import argparse
import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.scanner import Scanner
from db.database import Database
from cve.cve_db import CVEdb


def cmd_scan(args):
    """Scan target(s) for technology intelligence"""
    try:
        db = Database(args.db or "tech_int.db")
        scanner = Scanner(db, threads=args.threads, stealth=args.stealth, browser=args.browser)
        
        if args.file:
            try:
                with open(args.file) as f:
                    targets = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            except FileNotFoundError:
                logger.error(f"Target file not found: {args.file}")
                return
            except IOError as e:
                logger.error(f"Failed to read target file: {e}")
                return
                
            for target in targets:
                try:
                    scanner.scan_single(target)
                except Exception as e:
                    logger.error(f"Scan failed for {target}: {e}")
                    continue
        elif args.targets:
            targets = [t.strip() for t in args.targets.split(",") if t.strip()]
            for target in targets:
                try:
                    scanner.scan_single(target)
                except Exception as e:
                    logger.error(f"Scan failed for {target}: {e}")
                    continue
        else:
            try:
                scanner.scan_single(args.target)
            except Exception as e:
                logger.error(f"Scan failed for {args.target}: {e}")
                return
        
        db.close()
        logger.info(f"Scan complete. Results in {args.db or 'tech_int.db'}")
    except Exception as e:
        logger.error(f"Scan command failed: {e}")
        sys.exit(1)


def cmd_search(args):
    """Search database for targets"""
    db = Database(args.db or "tech_int.db")
    
    if args.cve:
        results = db.search_cve(args.cve)
    elif args.query:
        results = db.search(args.query)
    else:
        results = db.get_all()
    
    for r in results[:args.limit]:
        print(f"{r['domain']} | {r['tech_stack'] or 'N/A'} | CVSS: {r['cvss'] or 'N/A'}")
    
    db.close()


def cmd_update_cve(args):
    """Update local CVE database"""
    cve_db = CVEdb(args.cve_db or "cve.db")
    cve_db.update_from_nvd()
    print(f"[+] CVE database updated: {cve_db.count()} entries")


def cmd_export(args):
    """Export results"""
    db = Database(args.db or "tech_int.db")
    results = db.get_all()
    
    if args.format == "json":
        import json
        data = [r.to_dict() for r in results]
        with open(args.output, "w") as f:
            json.dump(data, f, indent=2)
    elif args.format == "csv":
        import csv
        with open(args.output, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["domain", "tech_stack", "versions", "cves", "cvss"])
            for r in results:
                writer.writerow([r.domain, r.tech_stack, r.versions, r.cves, r.cvss])
    
    print(f"[+] Exported to {args.output}")
    db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Tech-Int: Technology Intelligence Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Scan single target:
    python3 cli.py scan example.com
    
  Mass scan from file:
    python3 cli.py scan -f domains.txt --threads 5
    
  Scan with browser (JS rendering):
    python3 cli.py scan example.com --browser
    
  Search for CVEs:
    python3 cli.py search --cve "2025"
    
  Update CVE database:
    python3 cli.py update-cve
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Scan command
    scan_p = subparsers.add_parser("scan", help="Scan target(s)")
    scan_p.add_argument("target", nargs="?", help="Single target domain")
    scan_p.add_argument("-f", "--file", help="File with targets (one per line)")
    scan_p.add_argument("-t", "--targets", help="Comma-separated targets")
    scan_p.add_argument("--threads", type=int, default=1, help="Thread count")
    scan_p.add_argument("--db", help="Database file")
    scan_p.add_argument("--stealth", action="store_true", help="Use stealth mode (random UA, delays)")
    scan_p.add_argument("--browser", action="store_true", help="Use browser tool for JS rendering")
    
    # Search command
    search_p = subparsers.add_parser("search", help="Search database")
    search_p.add_argument("-q", "--query", help="SQL query or keyword")
    search_p.add_argument("--cve", help="Search by CVE ID or year")
    search_p.add_argument("--db", help="Database file")
    search_p.add_argument("-l", "--limit", type=int, default=50)
    
    # Update CVE command
    update_p = subparsers.add_parser("update-cve", help="Update CVE database")
    update_p.add_argument("--cve-db", help="CVE database file")
    
    # Export command
    export_p = subparsers.add_parser("export", help="Export results")
    export_p.add_argument("--db", help="Database file")
    export_p.add_argument("--format", choices=["json", "csv"], default="json")
    export_p.add_argument("-o", "--output", default="results.json")
    
    args = parser.parse_args()
    
    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "update-cve":
        cmd_update_cve(args)
    elif args.command == "export":
        cmd_export(args)


if __name__ == "__main__":
    main()
