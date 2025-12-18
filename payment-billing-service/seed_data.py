"""
Seed script for payment-billing-service.
Generates payments, invoices, refunds, and billing records.
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import random
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.invoice import Invoice, InvoiceStatus
from app.models.refund import Refund, RefundStatus
from app.models.billing import BillingRecord

Base.metadata.create_all(bind=engine)

GUEST_IDS = [str(uuid.uuid4()) for _ in range(200)]
BOOKING_IDS = [str(uuid.uuid4()) for _ in range(1000)]
PAYMENT_METHODS = list(PaymentMethod)
PAYMENT_STATUSES = list(PaymentStatus)


def generate_payment_reference(used_refs: set):
    """Generate a unique payment reference."""
    while True:
        ref = f"PAY{random.randint(100000, 999999)}"
        if ref not in used_refs:
            used_refs.add(ref)
            return ref


def generate_invoice_number(used_refs: set):
    """Generate a unique invoice number."""
    while True:
        ref = f"INV{random.randint(100000, 999999)}"
        if ref not in used_refs:
            used_refs.add(ref)
            return ref


def generate_refund_reference(used_refs: set):
    """Generate a unique refund reference."""
    while True:
        ref = f"REF{random.randint(100000, 999999)}"
        if ref not in used_refs:
            used_refs.add(ref)
            return ref


def generate_payments(db: Session, num_payments: int = 1500):
    """Generate payment records."""
    print(f"Generating {num_payments} payments...")
    
    # Check existing references to avoid duplicates
    from app.models.payment import Payment
    existing_refs = {ref[0] for ref in db.query(Payment.payment_reference).all()}
    used_payment_refs = set(existing_refs)
    
    payments = []
    for i in range(num_payments):
        booking_id = random.choice(BOOKING_IDS)
        guest_id = random.choice(GUEST_IDS)
        amount = Decimal(random.uniform(50.0, 1000.0))
        status = random.choice(PAYMENT_STATUSES)
        method = random.choice(PAYMENT_METHODS)
        
        created_at = datetime.utcnow() - timedelta(days=random.randint(0, 180))
        processed_at = created_at + timedelta(minutes=random.randint(1, 30)) if status in [PaymentStatus.COMPLETED, PaymentStatus.FAILED] else None
        completed_at = processed_at if status == PaymentStatus.COMPLETED else None
        failed_at = processed_at if status == PaymentStatus.FAILED else None
        
        payment = Payment(
            payment_reference=generate_payment_reference(used_payment_refs),
            booking_id=uuid.UUID(booking_id),
            booking_reference=f"BK{random.randint(100000, 999999)}",
            guest_id=uuid.UUID(guest_id),
            amount=amount,
            currency="USD",
            payment_method=method,
            status=status,
            provider=random.choice(["stripe", "paypal", "square", "cash"]),
            provider_payment_id=f"provider_{random.randint(100000, 999999)}" if status == PaymentStatus.COMPLETED else None,
            card_last4=str(random.randint(1000, 9999)) if method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD] else None,
            card_brand=random.choice(["visa", "mastercard", "amex"]) if method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD] else None,
            description=f"Payment for booking {booking_id[:8]}",
            failure_reason=random.choice([None, "Insufficient funds", "Card declined", "Network error"]) if status == PaymentStatus.FAILED else None,
            created_at=created_at,
            processed_at=processed_at,
            completed_at=completed_at,
            failed_at=failed_at,
        )
        payments.append(payment)
    
    db.bulk_save_objects(payments)
    db.commit()
    print(f"✓ Created {len(payments)} payments")
    return payments


def generate_invoices(db: Session, payments: list, num_invoices: int = 1200):
    """Generate invoice records."""
    print(f"Generating {num_invoices} invoices...")
    
    # Check existing references to avoid duplicates
    from app.models.invoice import Invoice
    existing_refs = {ref[0] for ref in db.query(Invoice.invoice_number).all()}
    used_invoice_refs = set(existing_refs)
    
    invoices = []
    for i in range(num_invoices):
        payment = random.choice(payments) if payments else None
        booking_id = random.choice(BOOKING_IDS)
        guest_id = random.choice(GUEST_IDS)
        
        base_amount = Decimal(random.uniform(50.0, 1000.0))
        tax_amount = base_amount * Decimal("0.10")
        fee_amount = Decimal(random.uniform(0, 50.0))
        discount_amount = Decimal(random.uniform(0, 100.0)) if random.random() > 0.7 else Decimal(0)
        amount = base_amount + tax_amount + fee_amount - discount_amount
        
        status = random.choice(list(InvoiceStatus))
        invoice_date = datetime.utcnow() - timedelta(days=random.randint(0, 180))
        due_date = invoice_date + timedelta(days=random.randint(7, 30))
        paid_date = invoice_date + timedelta(days=random.randint(1, 7)) if status == InvoiceStatus.PAID else None
        
        invoice = Invoice(
            invoice_number=generate_invoice_number(used_invoice_refs),
            booking_id=uuid.UUID(booking_id),
            booking_reference=f"BK{random.randint(100000, 999999)}",
            payment_id=payment.id if payment else None,
            guest_id=uuid.UUID(guest_id),
            amount=amount,
            currency="USD",
            status=status,
            base_amount=base_amount,
            tax_amount=tax_amount,
            fee_amount=fee_amount,
            discount_amount=discount_amount,
            invoice_date=invoice_date.date(),
            due_date=due_date.date(),
            paid_date=paid_date,
            billing_name=f"Guest {random.randint(1, 1000)}",
            billing_email=f"guest{random.randint(1, 1000)}@example.com",
            billing_address=f"{random.randint(100, 9999)} Main St, City, State {random.randint(10000, 99999)}",
            description=f"Invoice for booking services",
            line_items=[
                {"item": "Room/Table Booking", "quantity": 1, "price": float(base_amount)},
                {"item": "Tax", "quantity": 1, "price": float(tax_amount)},
            ],
            created_at=invoice_date,
            sent_at=invoice_date + timedelta(hours=1) if status in [InvoiceStatus.SENT, InvoiceStatus.PAID] else None,
        )
        invoices.append(invoice)
    
    db.bulk_save_objects(invoices)
    db.commit()
    print(f"✓ Created {len(invoices)} invoices")
    return invoices


def generate_refunds(db: Session, payments: list, num_refunds: int = 100):
    """Generate refund records."""
    print(f"Generating {num_refunds} refunds...")
    
    # Check existing references to avoid duplicates
    from app.models.refund import Refund
    existing_refs = {ref[0] for ref in db.query(Refund.refund_reference).all()}
    used_refund_refs = set(existing_refs)
    
    # Only refund completed payments
    completed_payments = [p for p in payments if p.status == PaymentStatus.COMPLETED]
    
    refunds = []
    for i in range(min(num_refunds, len(completed_payments))):
        payment = random.choice(completed_payments)
        amount = payment.amount if random.random() > 0.3 else payment.amount * Decimal("0.5")  # Full or partial
        
        status = random.choice(list(RefundStatus))
        created_at = payment.completed_at + timedelta(days=random.randint(1, 30))
        processed_at = created_at + timedelta(hours=random.randint(1, 48)) if status in [RefundStatus.COMPLETED, RefundStatus.FAILED] else None
        completed_at = processed_at if status == RefundStatus.COMPLETED else None
        failed_at = processed_at if status == RefundStatus.FAILED else None
        
        refund = Refund(
            refund_reference=generate_refund_reference(used_refund_refs),
            payment_id=payment.id,
            booking_id=payment.booking_id,
            booking_reference=payment.booking_reference,
            guest_id=payment.guest_id,
            amount=amount,
            currency="USD",
            status=status,
            reason=random.choice(["Cancellation", "Guest request", "Service issue", "Double charge"]),
            refund_type=random.choice(["full", "partial", "cancellation"]),
            provider=payment.provider,
            provider_refund_id=f"refund_{random.randint(100000, 999999)}" if status == RefundStatus.COMPLETED else None,
            created_at=created_at,
            processed_at=processed_at,
            completed_at=completed_at,
            failed_at=failed_at,
        )
        refunds.append(refund)
    
    db.bulk_save_objects(refunds)
    db.commit()
    print(f"✓ Created {len(refunds)} refunds")
    return refunds


def generate_billing_records(db: Session, payments: list, num_records: int = 1500):
    """Generate billing records."""
    print(f"Generating {num_records} billing records...")
    
    records = []
    for i in range(num_records):
        payment = random.choice(payments) if payments else None
        
        base_amount = payment.amount * Decimal("0.9") if payment else Decimal(random.uniform(50.0, 1000.0))
        tax_amount = base_amount * Decimal("0.10")
        fee_amount = Decimal(random.uniform(0, 50.0))
        discount_amount = Decimal(0)
        amount = base_amount + tax_amount + fee_amount
        
        record = BillingRecord(
            payment_id=payment.id if payment else uuid.uuid4(),
            booking_id=payment.booking_id if payment else uuid.UUID(random.choice(BOOKING_IDS)),
            booking_reference=f"BK{random.randint(100000, 999999)}",
            guest_id=payment.guest_id if payment else uuid.UUID(random.choice(GUEST_IDS)),
            amount=amount,
            currency="USD",
            billing_type=random.choice(["payment", "refund", "adjustment", "fee"]),
            base_amount=base_amount,
            tax_amount=tax_amount,
            fee_amount=fee_amount,
            discount_amount=discount_amount,
            description=f"Billing record for transaction",
            billed_at=datetime.utcnow() - timedelta(days=random.randint(0, 180)),
        )
        records.append(record)
    
    db.bulk_save_objects(records)
    db.commit()
    print(f"✓ Created {len(records)} billing records")


def main():
    """Main function to seed the database."""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Seeding payment-billing-service database...")
        print("=" * 60)
        
        payments = generate_payments(db, num_payments=1500)
        invoices = generate_invoices(db, payments, num_invoices=1200)
        refunds = generate_refunds(db, payments, num_refunds=100)
        generate_billing_records(db, payments, num_records=1500)
        
        print("=" * 60)
        print("✓ Database seeding completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

