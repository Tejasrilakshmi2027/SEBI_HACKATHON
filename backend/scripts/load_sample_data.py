"""
Script to load sample data for demonstration purposes.
Run this script after setting up the database to populate it with sample scans and users.
"""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_maker
from app.models.user import User
from app.models.scan import Scan
from app.core.security import get_password_hash


async def create_demo_user(session: AsyncSession) -> User:
    """Create a demo user account."""
    demo_user = User(
        email="demo@sebisentinel.com",
        username="demo_user",
        full_name="Demo User",
        hashed_password=get_password_hash("demo123"),
        role="investor",
        is_active=True
    )
    session.add(demo_user)
    await session.commit()
    await session.refresh(demo_user)
    return demo_user


async def create_sample_scans(session: AsyncSession, user_id: int):
    """Create sample scan records."""
    sample_scans = [
        {
            "scan_type": "email",
            "file_name": "suspicious_offer.eml",
            "trust_score": 35.0,
            "risk_level": "high",
            "confidence": 0.85,
            "status": "completed",
            "created_at": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "scan_type": "url",
            "file_name": "http://fake-sebi.com",
            "trust_score": 15.0,
            "risk_level": "critical",
            "confidence": 0.92,
            "status": "completed",
            "created_at": datetime.utcnow() - timedelta(hours=5)
        },
        {
            "scan_type": "pdf",
            "file_name": "investment_guide.pdf",
            "trust_score": 92.0,
            "risk_level": "low",
            "confidence": 0.90,
            "status": "completed",
            "created_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "scan_type": "image",
            "file_name": "broker_photo.jpg",
            "trust_score": 65.0,
            "risk_level": "medium",
            "confidence": 0.78,
            "status": "completed",
            "created_at": datetime.utcnow() - timedelta(days=2)
        },
        {
            "scan_type": "video",
            "file_name": "ceo_announcement.mp4",
            "trust_score": 88.0,
            "risk_level": "low",
            "confidence": 0.85,
            "status": "completed",
            "created_at": datetime.utcnow() - timedelta(days=3)
        }
    ]
    
    for scan_data in sample_scans:
        scan = Scan(
            user_id=user_id,
            **scan_data
        )
        session.add(scan)
    
    await session.commit()


async def main():
    """Main function to load sample data."""
    print("Loading sample data...")
    
    async with async_session_maker() as session:
        # Create demo user
        print("Creating demo user...")
        demo_user = await create_demo_user(session)
        print(f"Demo user created: {demo_user.email}")
        
        # Create sample scans
        print("Creating sample scans...")
        await create_sample_scans(session, demo_user.id)
        print("Sample scans created")
        
        print("\nSample data loaded successfully!")
        print("\nDemo credentials:")
        print("  Email: demo@sebisentinel.com")
        print("  Password: demo123")


if __name__ == "__main__":
    asyncio.run(main())
