from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.dependencies import get_current_user
from app.models import Season, SeasonCreate, SeasonRead, SeasonUpdate, User

router = APIRouter(prefix="/seasons", tags=["seasons"])

def get_owned_season(session: Session, season_id: int, user: User) -> Season:
    season = session.get(Season, season_id)
    if not season or season.user_id != user.id: 
        raise HTTPException(status_code=404, detail="Season not found")
    return season

@router.post("", response_model=SeasonRead, status_code=201)
def create_season(data: SeasonCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    season = Season(name=data.name, user_id=current_user.id)
    session.add(season)
    session.commit()
    session.refresh(season)
    return season

@router.get("/{season_id}", response_model=SeasonRead)
def get_season(season_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    season = get_owned_season(session, season_id, current_user)  
    return season

@router.get("", response_model=list[SeasonRead])
def get_all_seasons(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    seasons = session.exec(select(Season).where(Season.user_id == current_user.id)).all()
    return seasons


@router.patch("/{season_id}", response_model=SeasonRead)
def update_season(season_id: int, data: SeasonUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    season = get_owned_season(session, season_id, current_user)
    season.sqlmodel_update(data.model_dump(exclude_unset=True))
    session.add(season)
    session.commit()
    session.refresh(season)
    return season