#!/usr/bin/env python3
"""
Lagopus Release Nomenclature Resolver & Validator.
Pairs Semantic Versioning with the Ptarmigan (Lagopus) biological taxonomy.
"""

import argparse
import json
import re
import subprocess
import sys

SPECIES_MAP = {
    1: ("Lagopus", "Lagopus lagopus (Willow ptarmigan)"),
    2: ("LagopusMuta", "Lagopus muta (Rock ptarmigan)"),
    3: ("LagopusLeucura", "Lagopus leucura (White-tailed ptarmigan)"),
    4: ("LagopusScotica", "Lagopus scotica (Red grouse)"),
}

PRIORITY_SUBSPECIES = [
    "Helvetica", "Hyperborea", "Islandorum", "Japonica", "Millaisi",
    "Nivalis", "Pyrenaica", "Rupestris", "Saxatilis", "Welchi"
]

EXTENDED_SUBSPECIES = [
    "Alascensis", "Alleni", "Altai", "Atkhensis", "Birulai", "Cabrerai",
    "Captus", "Chamberlaini", "Dixoni", "Evermanni", "Gabrielsoni",
    "Kelloggae", "Kurilensis", "Leucoptera", "Macruros", "Muriei",
    "Nadezdae", "Nelsoni", "Peninsularis", "Rainierensis", "Sanfordi",
    "Saturata", "Townsendi", "Ungavus", "Xenoura"
]

TAG_REGEX = re.compile(
    r"^(Lagopus(?:Muta|Leucura|Scotica)?)([A-Z][a-z]+)?_v(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.]+))?(?:\+([a-zA-Z0-9.]+))?$"
)

def get_existing_git_tags() -> list:
    try:
        res = subprocess.run(
            ["git", "tag", "-l", "Lagopus*"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return [line.strip() for line in res.stdout.splitlines() if line.strip()]
    except Exception:
        return []

def validate_tag(tag: str) -> bool:
    match = TAG_REGEX.match(tag)
    if not match:
        return False
    species, subspecies, major, minor, patch, stage, build = match.groups()
    major = int(major)
    expected_species = SPECIES_MAP.get(major, ("Lagopus", ""))[0]
    if species != expected_species:
        return False
    return True

def resolve_next_release(bump_type: str = "patch", stage: str = None) -> dict:
    tags = get_existing_git_tags()
    latest_major = 1
    latest_minor = 0
    latest_patch = 0
    used_subspecies = set()
    current_species = "Lagopus"
    current_subspecies = ""

    for tag in tags:
        m = TAG_REGEX.match(tag)
        if m:
            sp, sub, maj, min_, pat, stg, bld = m.groups()
            maj, min_, pat = int(maj), int(min_), int(pat)
            if (maj, min_, pat) >= (latest_major, latest_minor, latest_patch):
                latest_major, latest_minor, latest_patch = maj, min_, pat
                current_species = sp
                current_subspecies = sub or ""
            if sub:
                used_subspecies.add(sub)

    new_major = latest_major
    new_minor = latest_minor
    new_patch = latest_patch
    new_subspecies = current_subspecies

    if bump_type == "major":
        new_major += 1
        new_minor = 0
        new_patch = 0
        new_subspecies = ""
    elif bump_type == "minor":
        new_minor += 1
        new_patch = 0
        pool = [s for s in (PRIORITY_SUBSPECIES + EXTENDED_SUBSPECIES) if s not in used_subspecies]
        new_subspecies = pool[0] if pool else "Helvetica"
    elif bump_type == "patch":
        new_patch += 1

    species_token = SPECIES_MAP.get(new_major, (f"LagopusSpecies{new_major}", ""))[0]
    taxonomic_token = f"{species_token}{new_subspecies}"

    version_str = f"v{new_major}.{new_minor}.{new_patch}"
    if stage:
        version_str += f"-{stage}"

    full_tag = f"{taxonomic_token}_{version_str}"

    human_lineage = species_token
    if new_subspecies:
        human_lineage += f" {new_subspecies}"

    return {
        "full_tag": full_tag,
        "semver": version_str,
        "species": species_token,
        "subspecies": new_subspecies,
        "human_title": f"Platform {version_str} - {human_lineage}",
        "binary_suffix": f"{taxonomic_token}_{version_str}-<os>-<arch>"
    }

def main():
    parser = argparse.ArgumentParser(description="Lagopus Release Nomenclature Helper")
    parser.add_argument("--bump", choices=["major", "minor", "patch"], default="patch")
    parser.add_argument("--stage", choices=["alpha.1", "beta.1", "beta.2", "rc.1"], default=None)
    parser.add_argument("--validate", type=str, help="Validate a candidate tag string")
    parser.add_argument("--json", action="store_true", help="Output full resolution object in JSON")
    args = parser.parse_args()

    if args.validate:
        is_valid = validate_tag(args.validate)
        if is_valid:
            print(f"[VALID] Tag '{args.validate}' strictly conforms to Ptarmigan (Lagopus) taxonomy.")
            sys.exit(0)
        else:
            print(f"[INVALID] Tag '{args.validate}' does NOT conform to Ptarmigan (Lagopus) taxonomy.")
            sys.exit(1)

    result = resolve_next_release(args.bump, args.stage)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Tag:         {result['full_tag']}")
        print(f"Title:       {result['human_title']}")
        print(f"Binary:      {result['binary_suffix']}")

if __name__ == "__main__":
    main()
