#!/usr/bin/env python3
"""
Test script to verify SQLAlchemy 1.4 compatibility
"""

try:
    print("Testing SQLAlchemy 1.4 imports...")
    from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
    from sqlalchemy.orm import sessionmaker, relationship
    from sqlalchemy.ext.declarative import declarative_base
    print("✓ SQLAlchemy imports successful")
    
    print("\nTesting database models...")
    Base = declarative_base()
    
    class TestUser(Base):
        __tablename__ = 'test_users'
        id = Column(Integer, primary_key=True)
        email = Column(String, unique=True, nullable=False)
        
    print("✓ Model definition successful")
    
    print("\nTesting database engine...")
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(bind=engine)
    print("✓ Database creation successful")
    
    print("\nTesting session...")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    # Test adding a user
    test_user = TestUser(email="test@test.com")
    session.add(test_user)
    session.commit()
    
    # Test querying
    user = session.query(TestUser).filter(TestUser.email == "test@test.com").first()
    assert user is not None
    assert user.email == "test@test.com"
    
    session.close()
    print("✓ Session operations successful")
    
    print("\n🎉 All SQLAlchemy 1.4 compatibility tests passed!")
    print("Your deployment should work with Python 3.10.12 and SQLAlchemy 1.4.50")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()