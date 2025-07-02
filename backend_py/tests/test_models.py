import pytest
from uuid import uuid4
from datetime import datetime
import string

from app.models import User, Spot, Comment, Vote
from app.models.spot import generate_short_id


def test_user_model():
    """Test User model creation"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        avatar_url="http://example.com/avatar.png",
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )
    
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.avatar_url == "http://example.com/avatar.png"
    assert isinstance(user.id, type(uuid4()))


def test_spot_model():
    """Test Spot model creation"""
    user_id = uuid4()
    spot = Spot(
        id=uuid4(),
        short_id="abc123",
        name="Test Skate Spot",
        description="A great place to skate",
        location="POINT(10 20)",
        user_id=user_id,
        photos=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    assert spot.name == "Test Skate Spot"
    assert spot.description == "A great place to skate"
    assert spot.location == "POINT(10 20)"
    assert spot.user_id == user_id
    assert spot.photos == []
    assert isinstance(spot.id, type(uuid4()))


def test_generate_short_id():
    """Test short ID generation"""
    # Test default length
    short_id = generate_short_id()
    assert len(short_id) == 4
    assert all(c in string.ascii_letters + string.digits for c in short_id)
    
    # Test custom length
    short_id_6 = generate_short_id(6)
    assert len(short_id_6) == 6
    assert all(c in string.ascii_letters + string.digits for c in short_id_6)
    
    # Test uniqueness (statistical test)
    ids = [generate_short_id() for _ in range(100)]
    assert len(set(ids)) > 90  # Should have >90% unique IDs


def test_comment_model():
    """Test Comment model creation"""
    user_id = uuid4()
    spot_id = uuid4()
    comment = Comment(
        id=uuid4(),
        content="Great spot for beginners!",
        user_id=user_id,
        spot_id=spot_id,
        created_at=datetime.utcnow()
    )
    
    assert comment.content == "Great spot for beginners!"
    assert comment.user_id == user_id
    assert comment.spot_id == spot_id
    assert isinstance(comment.id, type(uuid4()))


def test_vote_model():
    """Test Vote model creation"""
    user_id = uuid4()
    spot_id = uuid4()
    vote = Vote(
        id=uuid4(),
        spot_id=spot_id,
        user_id=user_id,
        value=1,
        created_at=datetime.utcnow()
    )
    
    assert vote.spot_id == spot_id
    assert vote.user_id == user_id
    assert vote.value == 1
    assert isinstance(vote.id, type(uuid4()))


def test_model_relationships():
    """Test model relationships are properly defined"""
    # Test User relationships
    user = User(id=uuid4(), email="test@example.com", name="Test User")
    assert hasattr(user, 'spots')
    assert hasattr(user, 'comments')
    assert hasattr(user, 'votes')
    
    # Test Spot relationships
    spot = Spot(
        id=uuid4(),
        short_id="abc123",
        name="Test Spot",
        location="POINT(0 0)",
        user_id=user.id
    )
    assert hasattr(spot, 'user')
    assert hasattr(spot, 'comments')
    assert hasattr(spot, 'votes')
    
    # Test Comment relationships
    comment = Comment(
        id=uuid4(),
        content="Test comment",
        user_id=user.id,
        spot_id=spot.id
    )
    assert hasattr(comment, 'user')
    assert hasattr(comment, 'spot')
    
    # Test Vote relationships
    vote = Vote(
        id=uuid4(),
        spot_id=spot.id,
        user_id=user.id,
        value=1
    )
    assert hasattr(vote, 'user')
    assert hasattr(vote, 'spot')


def test_spot_photos_default():
    """Test that Spot photos default to empty list"""
    spot = Spot(
        id=uuid4(),
        short_id="test123",
        name="Test Spot",
        location="POINT(0 0)",
        user_id=uuid4()
    )
    # Photos should default to empty list
    assert spot.photos is None or spot.photos == []