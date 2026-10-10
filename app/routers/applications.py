from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Application, ApplicationCreate, ApplicationRead, ApplicationUpdate, StageChange, Stage, StageChangeRead, StageChangeCreate, Season 
from typing import Optional
from app.services import change_stage

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("", response_model=ApplicationRead, status_code=201)
def create_application(data: ApplicationCreate, session: Session = Depends(get_session)):
    if not session.get(Season, data.season_id):
        raise HTTPException(status_code=404, detail="Season not found")
    application = Application(**data.model_dump(exclude={"stage"}))
    change_stage(session, application, data.stage)
    session.commit()
    session.refresh(application)
    return application

@router.get("", response_model=list[ApplicationRead])
def list_applications(season_id: Optional[int] = None, session: Session = Depends(get_session)):
    applications_query = select(Application)
    if season_id is not None:
        applications_query = applications_query.where(Application.season_id == season_id)
    return session.exec(applications_query).all()

@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, session: Session = Depends(get_session)):
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application

@router.patch("/{application_id}", response_model=ApplicationRead)
def update_application(application_id: int, data: ApplicationUpdate, session: Session = Depends(get_session)):
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    session.commit()
    session.refresh(application)
    return application

@router.post("/{application_id}/stage", response_model=StageChangeRead, status_code=201)
def change_application_stage(application_id: int, data: StageChangeCreate, session: Session = Depends(get_session)):
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    stage_change = change_stage(session, application, data.stage, data.notes)
    session.commit()
    session.refresh(stage_change)
    return stage_change

@router.get("/{application_id}/history", response_model=list[StageChangeRead])
def get_application_history(application_id: int, session: Session = Depends(get_session)):
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    selected = select(StageChange).where(StageChange.application_id == application_id)
    selected = selected.order_by(StageChange.changed_at.desc())
    return session.exec(selected).all()

@router.delete("/{application_id}", status_code=204)
def delete_application(application_id: int, session: Session = Depends(get_session)):
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    session.delete(application)
    session.commit()