from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Season, SeasonCreate, SeasonRead, SeasonUpdate

router = APIRouter(prefix="/seasons", tags=["seasons"])

@router.post("", response_model=SeasonRead, status_code=201)
def create_season(data: SeasonCreate, session: Session = Depends(get_session)):
    season = Season.model_validate(data)
    session.add(season)
    session.commit()
    session.refresh(season)
    return season

@router.get("/{season_id}", response_model=SeasonRead)
def get_season(season_id: int, session: Session = Depends(get_session)):
    season = session.get(Season, season_id)   
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    return season

@router.get("", response_model=list[SeasonRead])
def get_all_seasons(session: Session = Depends(get_session)):
    seasons = session.exec(select(Season)).all()
    return seasons


@router.patch("/{season_id}", response_model=SeasonRead)
def update_season(season_id: int, data: SeasonUpdate, session: Session = Depends(get_session)):
    season = session.get(Season, season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    season.sqlmodel_update(data.model_dump(exclude_unset=True))
    session.add(season)
    session.commit()
    session.refresh(season)
    return season