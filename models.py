from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any


# ============================================
# 1. player_seasons(player_id) Response Models
# ============================================

class Sport(BaseModel):
    name: str
    slug: str
    id: int


class NameTranslation(BaseModel):
    ar: Optional[str] = None
    hi: Optional[str] = None
    bn: Optional[str] = None
    ru: Optional[str] = None


class FieldTranslations(BaseModel):
    nameTranslation: Optional[NameTranslation] = None
    shortNameTranslation: Optional[NameTranslation] = None


class Category(BaseModel):
    name: str
    slug: str
    sport: Sport
    id: int
    flag: Optional[str] = None
    alpha2: Optional[str] = None
    fieldTranslations: Optional[FieldTranslations] = None


class UniqueTournament(BaseModel):
    name: str
    slug: str
    primaryColorHex: Optional[str] = None
    secondaryColorHex: Optional[str] = None
    category: Category
    userCount: Optional[int] = None
    id: int
    displayInverseHomeAwayTeams: Optional[bool] = None
    fieldTranslations: Optional[FieldTranslations] = None


class Season(BaseModel):
    name: str
    year: str
    editor: bool
    id: int


class UniqueTournamentSeason(BaseModel):
    uniqueTournament: UniqueTournament
    seasons: List[Season]


class PlayerSeasonsResponse(BaseModel):
    """Response from player.player_seasons(player_id)"""
    uniqueTournamentSeasons: List[UniqueTournamentSeason]
    typesMap: Optional[Dict[str, Dict[str, List[str]]]] = None


# ============================================
# 2. league_stats(league_id, season_id) Response Models
# ============================================

class Statistics(BaseModel):
    # Rating
    rating: Optional[float] = None
    totalRating: Optional[float] = None
    countRating: Optional[int] = None
    
    # Goals & Assists
    goals: Optional[int] = None
    assists: Optional[int] = None
    goalsAssistsSum: Optional[int] = None
    expectedGoals: Optional[float] = None
    expectedAssists: Optional[float] = None
    
    # Chances
    bigChancesCreated: Optional[int] = None
    bigChancesMissed: Optional[int] = None
    
    # Passing
    accuratePasses: Optional[int] = None
    inaccuratePasses: Optional[int] = None
    totalPasses: Optional[int] = None
    accuratePassesPercentage: Optional[float] = None
    accurateOwnHalfPasses: Optional[int] = None
    accurateOppositionHalfPasses: Optional[int] = None
    accurateFinalThirdPasses: Optional[int] = None
    keyPasses: Optional[int] = None
    totalOwnHalfPasses: Optional[int] = None
    totalOppositionHalfPasses: Optional[int] = None
    accurateLongBalls: Optional[int] = None
    accurateLongBallsPercentage: Optional[float] = None
    totalLongBalls: Optional[int] = None
    totalChippedPasses: Optional[int] = None
    accurateChippedPasses: Optional[int] = None
    passToAssist: Optional[int] = None
    
    # Dribbling
    successfulDribbles: Optional[int] = None
    successfulDribblesPercentage: Optional[float] = None
    
    # Defending
    tackles: Optional[int] = None
    tacklesWon: Optional[int] = None
    tacklesWonPercentage: Optional[float] = None
    interceptions: Optional[int] = None
    clearances: Optional[int] = None
    blockedShots: Optional[int] = None
    ballRecovery: Optional[int] = None
    
    # Cards
    yellowCards: Optional[int] = None
    redCards: Optional[int] = None
    directRedCards: Optional[int] = None
    yellowRedCards: Optional[int] = None
    
    # Crosses
    accurateCrosses: Optional[int] = None
    accurateCrossesPercentage: Optional[float] = None
    totalCross: Optional[int] = None
    
    # Shooting
    totalShots: Optional[int] = None
    shotsOnTarget: Optional[int] = None
    shotsOffTarget: Optional[int] = None
    shotsFromInsideTheBox: Optional[int] = None
    shotsFromOutsideTheBox: Optional[int] = None
    hitWoodwork: Optional[int] = None
    
    # Duels
    groundDuelsWon: Optional[int] = None
    groundDuelsWonPercentage: Optional[float] = None
    aerialDuelsWon: Optional[int] = None
    aerialDuelsWonPercentage: Optional[float] = None
    totalDuelsWon: Optional[int] = None
    totalDuelsWonPercentage: Optional[float] = None
    duelLost: Optional[int] = None
    aerialLost: Optional[int] = None
    totalContest: Optional[int] = None
    
    # Playing Time
    minutesPlayed: Optional[int] = None
    matchesStarted: Optional[int] = None
    appearances: Optional[int] = None
    
    # Goals Detail
    goalConversionPercentage: Optional[float] = None
    goalsFromInsideTheBox: Optional[int] = None
    goalsFromOutsideTheBox: Optional[int] = None
    headedGoals: Optional[int] = None
    leftFootGoals: Optional[int] = None
    rightFootGoals: Optional[int] = None
    scoringFrequency: Optional[float] = None
    
    # Penalties
    penaltiesTaken: Optional[int] = None
    penaltyGoals: Optional[int] = None
    penaltyWon: Optional[int] = None
    penaltyConceded: Optional[int] = None
    penaltyConversion: Optional[float] = None
    attemptPenaltyMiss: Optional[int] = None
    attemptPenaltyPost: Optional[int] = None
    attemptPenaltyTarget: Optional[int] = None
    
    # Set Pieces
    shotFromSetPiece: Optional[int] = None
    freeKickGoal: Optional[int] = None
    setPieceConversion: Optional[float] = None
    
    # Errors
    errorLeadToGoal: Optional[int] = None
    errorLeadToShot: Optional[int] = None
    
    # Possession
    dispossessed: Optional[int] = None
    possessionLost: Optional[int] = None
    possessionWonAttThird: Optional[int] = None
    dribbledPast: Optional[int] = None
    
    # Misc
    touches: Optional[int] = None
    wasFouled: Optional[int] = None
    fouls: Optional[int] = None
    ownGoals: Optional[int] = None
    offsides: Optional[int] = None
    totalAttemptAssist: Optional[int] = None
    totwAppearances: Optional[int] = None
    
    # Goalkeeper Stats
    saves: Optional[int] = None
    cleanSheet: Optional[int] = None
    penaltyFaced: Optional[int] = None
    penaltySave: Optional[int] = None
    savedShotsFromInsideTheBox: Optional[int] = None
    savedShotsFromOutsideTheBox: Optional[int] = None
    goalsConcededInsideTheBox: Optional[int] = None
    goalsConcededOutsideTheBox: Optional[int] = None
    goalsConceded: Optional[int] = None
    punches: Optional[int] = None
    runsOut: Optional[int] = None
    successfulRunsOut: Optional[int] = None
    highClaims: Optional[int] = None
    crossesNotClaimed: Optional[int] = None
    savesCaught: Optional[int] = None
    savesParried: Optional[int] = None
    goalKicks: Optional[int] = None
    
    # Meta
    id: Optional[int] = None
    type: Optional[str] = None


class TeamColors(BaseModel):
    primary: str
    secondary: str
    text: str


class Team(BaseModel):
    name: str
    slug: str
    shortName: str
    gender: Optional[str] = None
    sport: Optional[Sport] = None
    userCount: Optional[int] = None
    nameCode: Optional[str] = None
    disabled: Optional[bool] = None
    national: Optional[bool] = None
    type: Optional[int] = None
    id: int
    entityType: Optional[str] = None
    teamColors: Optional[TeamColors] = None
    fieldTranslations: Optional[FieldTranslations] = None


class LeagueStatsResponse(BaseModel):
    """Response from player.league_stats(league_id, season_id)"""
    statistics: Statistics
    team: Team