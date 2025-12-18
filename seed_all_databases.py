"""
Master script to seed all microservice databases.
Runs all individual seed scripts in sequence.
"""
import os
import sys
import subprocess
from pathlib import Path

# List of all microservices with their seed scripts
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


def run_seed_script(service_name: str) -> bool:
    """Run the seed script for a specific service."""
    script_path = Path(__file__).parent / service_name / "seed_data.py"
    
    if not script_path.exists():
        print(f"⚠ Warning: Seed script not found for {service_name}: {script_path}")
        return False
    
    print(f"\n{'=' * 60}")
    print(f"Running seed script for: {service_name}")
    print(f"{'=' * 60}")
    
    try:
        # Change to the service directory
        service_dir = script_path.parent
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(service_dir),
            check=True,
            capture_output=False,
        )
        print(f"✓ Successfully seeded {service_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error seeding {service_name}: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error seeding {service_name}: {e}")
        return False


def main():
    """Main function to seed all databases."""
    print("=" * 60)
    print("MSOP Project - Database Seeding Script")
    print("=" * 60)
    print(f"Seeding {len(SERVICES)} microservices...")
    print("=" * 60)
    
    results = {}
    for service in SERVICES:
        results[service] = run_seed_script(service)
    
    # Summary
    print("\n" + "=" * 60)
    print("SEEDING SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for v in results.values() if v)
    failed = len(results) - successful
    
    for service, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status:12} - {service}")
    
    print("=" * 60)
    print(f"Total: {len(results)} services")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print("=" * 60)
    
    if failed > 0:
        sys.exit(1)
    else:
        print("\n✓ All databases seeded successfully!")


if __name__ == "__main__":
    main()

