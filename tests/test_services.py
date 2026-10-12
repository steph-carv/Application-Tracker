from app.models import User, Season, Application, Stage, StageChange
from app.services import change_stage
from sqlmodel import select 


def test_change_stage_keeps_current_stage_in_sync(session):
    user = User(email="test@example.com" , hashed_password="fakehashedpassword")
    session.add(user)
    session.flush()
    season = Season(name="Test Season 20XX", user_id=user.id)
    session.add(season)
    session.flush()
    application = Application(season_id=season.id, company="Fake Company Inc.", position="Software Dev")
    change_stage(session, application, Stage.to_apply)
    change_stage(session, application, Stage.applied)
    change_stage(session, application, Stage.interview)
    session.add(application)
    session.flush()
    session.commit()

    rows = session.exec(
        select(StageChange).where(StageChange.application_id == application.id).order_by(StageChange.changed_at.desc(), StageChange.id.desc()) 
    ).all()
    assert len(rows) == 3
    assert rows[0].stage == application.current_stage
    assert application.current_stage == Stage.interview
