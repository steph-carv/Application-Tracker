from typing import Optional
from sqlmodel import Session
from app.models import Application, Stage, StageChange

def change_stage(session: Session, application: Application,
                 new_stage: Stage, notes: Optional[str] = None) -> StageChange:
    application.current_stage = new_stage
    session.add(application)
    session.flush()  # Ensure the application has an ID before creating StageChange
    stage_change = StageChange(application_id=application.id, stage=new_stage, notes=notes)
    session.add(stage_change)
    session.flush()
    return stage_change