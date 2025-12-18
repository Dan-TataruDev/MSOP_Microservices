"""
Script to merge all microservice requirements.txt files into one unified file.
Handles version conflicts by taking the highest compatible version.
"""
import re
from pathlib import Path
from collections import defaultdict
from packaging import version

# Service directories
SERVICES = [
    "booking-reservation-service",
    "inventory-resource-service",
    "payment-billing-service",
    "guest-interaction-service",
    "dynamic-pricing-service",
    "housekeeping-maintenance-service",
    "feedback-sentiment-service",
    "marketing-loyalty-service",
    "favorites-collections-service",
    "bi-analytics-service",
]

# Pattern to match package specifications
PACKAGE_PATTERN = re.compile(r'^([a-zA-Z0-9_-]+(?:\[[^\]]+\])?)([<>=!]+.*)?$')


def parse_requirement(line):
    """Parse a requirement line into package name and version spec."""
    line = line.strip()
    if not line or line.startswith('#'):
        return None
    
    # Remove comments
    if '#' in line:
        line = line.split('#')[0].strip()
    
    # Match package name and version
    match = PACKAGE_PATTERN.match(line)
    if not match:
        return None
    
    package = match.group(1)
    version_spec = match.group(2) if match.group(2) else ""
    
    # Extract base package name (remove extras like [asyncio])
    base_package = package.split('[')[0]
    
    return {
        'package': package,
        'base_package': base_package,
        'version_spec': version_spec.strip(),
        'original': line
    }


def extract_version(version_spec):
    """Extract version number from version spec."""
    if not version_spec:
        return None
    
    # Match version patterns like ==1.2.3, >=1.2.3, etc.
    version_match = re.search(r'([\d.]+(?:\.post\d+)?(?:\.dev\d+)?)', version_spec)
    if version_match:
        v = version_match.group(1).rstrip('.')  # Remove trailing dots
        return v if v else None
    return None


def compare_versions(v1, v2):
    """Compare two version strings, return the higher one."""
    try:
        if v1 and v2:
            return v1 if version.parse(v1) >= version.parse(v2) else v2
        return v1 or v2
    except:
        # If version parsing fails, prefer the one with a version
        return v1 or v2


def merge_requirements():
    """Merge all requirements files."""
    root = Path(__file__).parent
    all_requirements = defaultdict(list)
    comments = []
    
    print("Reading requirements from all services...")
    
    for service in SERVICES:
        req_file = root / service / "requirements.txt"
        if not req_file.exists():
            print(f"  [WARNING] {req_file} not found")
            continue
        
        print(f"  Reading {service}/requirements.txt")
        with open(req_file, 'r', encoding='utf-8') as f:
            for line in f:
                req = parse_requirement(line)
                if req:
                    all_requirements[req['base_package']].append(req)
                elif line.strip().startswith('#'):
                    comments.append(f"# From {service}: {line.strip()}")
    
    print(f"\nFound {len(all_requirements)} unique packages")
    print("Merging and resolving version conflicts...")
    
    # Merge requirements
    merged = {}
    conflicts = []
    
    for base_package, reqs in all_requirements.items():
        # Collect all version specs
        version_specs = [r['version_spec'] for r in reqs]
        packages = [r['package'] for r in reqs]
        
        # Find the highest version
        highest_version = None
        highest_spec = None
        
        for req in reqs:
            v = extract_version(req['version_spec'])
            if v:
                try:
                    if highest_version is None:
                        highest_version = v
                        highest_spec = req['version_spec']
                    elif version.parse(v) > version.parse(highest_version):
                        highest_version = v
                        highest_spec = req['version_spec']
                except:
                    # If version parsing fails, keep the first valid one
                    if highest_version is None:
                        highest_version = v
                        highest_spec = req['version_spec']
        
        # If no version found, use the first requirement
        if not highest_spec:
            # Check for >= specifications
            for req in reqs:
                if '>=' in req['version_spec']:
                    highest_spec = req['version_spec']
                    break
            
            if not highest_spec:
                highest_spec = version_specs[0] if version_specs else ""
        
        # Use the package name with extras if any
        final_package = packages[0]  # Use first package name (may have extras)
        
        # Check for conflicts
        unique_specs = set(vs for vs in version_specs if vs)
        if len(unique_specs) > 1:
            conflicts.append({
                'package': base_package,
                'specs': list(unique_specs),
                'chosen': highest_spec
            })
        
        merged[base_package] = {
            'package': final_package,
            'version_spec': highest_spec
        }
    
    # Generate output
    output_lines = [
        "# Unified Requirements for All Microservices",
        "# Generated by merge-requirements.py",
        "# This file contains all dependencies from all microservices",
        "# Version conflicts resolved by taking the highest version",
        "",
    ]
    
    # Group by category
    categories = {
        'FastAPI and Server': ['fastapi', 'uvicorn', 'python-multipart'],
        'Database': ['sqlalchemy', 'alembic', 'psycopg2-binary', 'asyncpg'],
        'Validation and Serialization': ['pydantic', 'pydantic-settings', 'email-validator'],
        'Authentication and Security': ['python-jose', 'passlib', 'PyJWT'],
        'HTTP Clients': ['httpx', 'aiohttp'],
        'Event Streaming (RabbitMQ)': ['aio-pika', 'pika'],
        'Caching': ['redis', 'aioredis'],
        'AI/ML': ['openai'],
        'Background Tasks': ['celery', 'apscheduler'],
        'Data Processing': ['pandas', 'numpy'],
        'Utilities': ['python-dateutil', 'pytz', 'python-dotenv', 'croniter'],
        'Testing': ['pytest', 'pytest-asyncio', 'pytest-cov'],
        'Logging and Monitoring': ['structlog'],
    }
    
    categorized = defaultdict(list)
    uncategorized = []
    
    for base_pkg, info in merged.items():
        found = False
        for category, packages in categories.items():
            if base_pkg in packages:
                categorized[category].append((base_pkg, info))
                found = True
                break
        if not found:
            uncategorized.append((base_pkg, info))
    
    # Write categorized packages
    for category in categories.keys():
        if category in categorized:
            output_lines.append(f"# {category}")
            for base_pkg, info in sorted(categorized[category], key=lambda x: x[0]):
                pkg_line = info['package']
                if info['version_spec']:
                    pkg_line += info['version_spec']
                output_lines.append(pkg_line)
            output_lines.append("")
    
    # Write uncategorized packages
    if uncategorized:
        output_lines.append("# Other Dependencies")
        for base_pkg, info in sorted(uncategorized, key=lambda x: x[0]):
            pkg_line = info['package']
            if info['version_spec']:
                pkg_line += info['version_spec']
            output_lines.append(pkg_line)
        output_lines.append("")
    
    # Write conflicts report
    if conflicts:
        output_lines.append("# Version Conflicts Resolved:")
        for conflict in conflicts:
            output_lines.append(f"# {conflict['package']}: {', '.join(conflict['specs'])} -> {conflict['chosen']}")
        output_lines.append("")
    
    # Write to file
    output_file = root / "requirements-unified.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
        print(f"\n[OK] Created unified requirements file: {output_file}")
        print(f"  Total packages: {len(merged)}")
        if conflicts:
            print(f"  Version conflicts resolved: {len(conflicts)}")
            print("\nConflicts resolved:")
            for conflict in conflicts[:10]:  # Show first 10
                print(f"  - {conflict['package']}: {conflict['chosen']}")
            if len(conflicts) > 10:
                print(f"  ... and {len(conflicts) - 10} more")
    
    return output_file


if __name__ == "__main__":
    try:
        merge_requirements()
        print("\n[SUCCESS] You can now install all dependencies with:")
        print("  pip install -r requirements-unified.txt")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

