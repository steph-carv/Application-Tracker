from typing import Optional
from fastapi import HTTPException
from sqlmodel import Session
from app.models import Application, Season, Stage, StageChange, User

def change_stage(session: Session, application: Application,
                new_stage: Stage, notes: Optional[str] = None) -> StageChange:
    application.current_stage = new_stage
    session.add(application)
    session.flush()  
    stage_change = StageChange(application_id=application.id, stage=new_stage, notes=notes)
    session.add(stage_change)
    session.flush()
    return stage_change

def get_owned_season(session: Session, season_id: int, user: User) -> Season:
    season = session.get(Season, season_id)
    if not season or season.user_id != user.id: 
        raise HTTPException(status_code=404, detail="Season not found")
    return season

def get_owned_application(session: Session, application_id: int, user: User) -> Application:
    application = session.get(Application, application_id)
    if not application: 
         raise HTTPException(status_code=404, detail="Application not found")
    season = session.get(Season, application.season_id)
    if season.user_id != user.id:
        raise HTTPException(status_code=404, detail="Application not found")
    return application 
