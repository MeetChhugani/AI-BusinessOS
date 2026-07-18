import pytest
from uuid import uuid4
from httpx import AsyncClient
from app.auth.security import hash_password
from app.models.user import User
from app.models.notifications import NotificationPreference, NotificationLog
from app.models.settings import FeatureFlag
from app.models.search import SearchIndex
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@pytest.mark.asyncio
async def test_notification_preference_blocks_delivery(client: AsyncClient, db_session: AsyncSession) -> None:
    # 1. Create user and disabled email preference
    user = User(
        email="prefuser@businessos.com",
        full_name="Preferences User",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="EMPLOYEE",
    )
    db_session.add(user)
    await db_session.flush()

    pref = NotificationPreference(
        user_id=user.id,
        category="GENERAL",
        email_enabled=False, # email disabled!
        in_app_enabled=True
    )
    db_session.add(pref)
    await db_session.commit()

    # Authenticate admin
    admin = User(
        email="testplatadmin@businessos.com",
        full_name="Platform Admin",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="ADMIN",
    )
    db_session.add(admin)
    await db_session.commit()

    login_res = await client.post("/api/v1/auth/login", json={"email": admin.email, "password": "SuperSecurePassword123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Try posting an email notification log (will raise validation exception)
    from app.services.platform_service import NotificationService
    with pytest.raises(Exception) as excinfo:
        await NotificationService.log_notification(
            db_session,
            user_id=user.id,
            title="Warning alert",
            message="This is a test notification message",
            channel="EMAIL"
        )
    assert "disabled by preference" in str(excinfo.value)

@pytest.mark.asyncio
async def test_feature_flags_toggle(client: AsyncClient, db_session: AsyncSession) -> None:
    # 1. Seed feature flag config
    flag = FeatureFlag(
        name="test.beta_view",
        enabled=False,
        description="Beta page flag"
    )
    db_session.add(flag)
    await db_session.commit()

    # Authenticate admin
    admin = User(
        email="testflagadmin@businessos.com",
        full_name="Flags Admin",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="ADMIN",
    )
    db_session.add(admin)
    await db_session.commit()

    login_res = await client.post("/api/v1/auth/login", json={"email": admin.email, "password": "SuperSecurePassword123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Toggle active state from false to true
    res = await client.post(f"/api/v1/features/{flag.id}/toggle?enabled=true", headers=headers)
    assert res.status_code == 200
    assert res.json()["enabled"] is True

@pytest.mark.asyncio
async def test_global_search_indexing(client: AsyncClient, db_session: AsyncSession) -> None:
    # 1. Index mock customer entity record
    from app.services.platform_service import SearchService
    ent_id = uuid4()
    await SearchService.index_entity(
        db_session,
        entity_type="Customer",
        entity_id=ent_id,
        title="Initech Consulting Group",
        description="Premium enterprise consulting accounts",
        keywords="initech,consulting,billing"
    )

    # 2. Query search endpoint
    response = await client.get("/api/v1/search?q=initech")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Initech Consulting Group"
