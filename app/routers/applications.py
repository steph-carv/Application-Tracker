from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import Application, ApplicationCreate, ApplicationRead, ApplicationUpdate, StageChange, StageChangeRead, StageChangeCreate, Season, User 
from typing import Optional
from app.services import change_stage, get_owned_application, get_owned_season
from app.dependencies import get_current_user


router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("", response_model=ApplicationRead, status_code=201)
def create_application(data: ApplicationCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    get_owned_season(session, data.season_id, current_user)
    application = Application(**data.model_dump(exclude={"stage"}))
    change_stage(session, application, data.stage)
    session.commit()
    session.refresh(application)
    return application

@router.get("", response_model=list[ApplicationRead])
def list_applications(season_id: Optional[int] = None, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    applications_query = select(Application).join(Season).where(Season.user_id == current_user.id)
    if season_id is not None:
        applications_query = applications_query.where(Application.season_id == season_id)
    return session.exec(applications_query).all()

@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    application = get_owned_application(session, application_id, current_user)
    return application

@router.patch("/{application_id}", response_model=ApplicationRead)
def update_application(application_id: int, data: ApplicationUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    application = get_owned_application(session, application_id, current_user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    session.commit()
    session.refresh(application)
    return application

@router.post("/{application_id}/stage", response_model=StageChangeRead, status_code=201)
def change_application_stage(application_id: int, data: StageChangeCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    application = get_owned_application(session, application_id, current_user)
    stage_change = change_stage(session, application, data.stage, data.notes)
    session.commit()
    session.refresh(stage_change)
    return stage_change

@router.get("/{application_id}/history", response_model=list[StageChangeRead])
def get_application_history(application_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    application = get_owned_application(session, application_id, current_user)
    selected = select(StageChange).where(StageChange.application_id == application_id)
    selected = selected.order_by(StageChange.changed_at.desc())
    return session.exec(selected).all()

@router.delete("/{application_id}", status_code=204)
def delete_application(application_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    application = get_owned_application(session, application_id, current_user)
    session.delete(application)
    session.commit()