"""GameRouter factory — generates common game endpoints to eliminate route duplication.

Each game (memory, math, iq) has identical patterns for:
- create_session, create_round, submit_attempt, consolidate, get_state, get_history

GameRouter generates these endpoints given a service module and model classes.
Game-specific extras (hints, strategy-log, meta) are added separately.
"""
from collections import defaultdict
from typing import Any, Callable, Optional, Type

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session, select

from core.database import get_session
from core.limiter import get_rate_limit_str, limiter


class GameRouter:
    """Generates common game endpoints.

    Args:
        prefix: URL prefix for the router
        service: Service module with iniciar_sesion, crear_round, enviar_intento, consolidar_sesion
        SessionModel: The game session SQLModel class
        RoundModel: The game round SQLModel class
        AttemptModel: The game attempt SQLModel class
        round_fk_field: Field name on RoundModel that links to session (e.g., "game_session_id" or "session_id")
        session_create_body: Pydantic model for session creation body (must have skill_id field)
        attempt_body: Pydantic model for attempt submission body
        format_session: Callback session → dict for create_session response
        format_round: Callback (round_obj, extra_data) → dict for create_round response
        create_round_extra: Callback (session) → extra data for round creation (e.g., numbers, problem)
        format_state: Callback session → dict for get_state response
        format_history_round: Callback (round, attempts) → dict for history round entry
        error_messages: Dict with optional custom error messages
    """

    def __init__(
        self,
        prefix: str,
        service,
        SessionModel: Type,
        RoundModel: Type,
        AttemptModel: Type,
        round_fk_field: str,
        session_create_body: Type[BaseModel],
        attempt_body: Type[BaseModel],
        format_session: Callable,
        format_round: Callable,
        create_round_extra: Callable,
        format_state: Callable,
        format_history_round: Callable,
        consolidate_error_message: Optional[str] = None,
        round_error_status: int = 404,
        consolidate_error_status: int = 404,
        always_use_error_status: bool = False,
    ):
        self.prefix = prefix
        self.service = service
        self.SessionModel = SessionModel
        self.RoundModel = RoundModel
        self.AttemptModel = AttemptModel
        self.round_fk_field = round_fk_field
        self.session_create_body = session_create_body
        self.attempt_body = attempt_body
        self.format_session = format_session
        self.format_round = format_round
        self.create_round_extra = create_round_extra
        self.format_state = format_state
        self.format_history_round = format_history_round
        self.consolidate_error_message = consolidate_error_message
        self.round_error_status = round_error_status
        self.consolidate_error_status = consolidate_error_status
        self.always_use_error_status = always_use_error_status

        self.router = APIRouter()
        self._register_endpoints()

    def _register_endpoints(self):
        router = self.router
        service = self.service
        SessionModel = self.SessionModel

        @router.post("/sessions")
        @limiter.limit(get_rate_limit_str())
        def create_session(request: Request, body: self.session_create_body, db: Session = Depends(get_session)):
            try:
                session = service.iniciar_sesion(db, body.skill_id)
                return self.format_session(session)
            except ValueError as e:
                raise HTTPException(404, str(e))

        @router.post("/sessions/{session_id}/rounds")
        @limiter.limit(get_rate_limit_str())
        def create_round(request: Request, session_id: int, db: Session = Depends(get_session)):
            try:
                round_obj, extra = service.crear_round(db, session_id)
                return self.format_round(round_obj, extra)
            except ValueError as e:
                if self.always_use_error_status:
                    raise HTTPException(self.round_error_status, str(e))
                status = 404 if "not found" in str(e).lower() else self.round_error_status
                raise HTTPException(status, str(e))

        @router.post("/rounds/{round_id}/attempts")
        @limiter.limit(get_rate_limit_str())
        def submit_attempt(
            request: Request,
            round_id: int,
            body: self.attempt_body,
            db: Session = Depends(get_session),
        ):
            try:
                # Extract the answer field from body — each game has a different field name
                answer = self._extract_attempt_answer(body)
                return service.enviar_intento(db, round_id, answer)
            except ValueError as e:
                raise HTTPException(404, str(e))

        @router.post("/sessions/{session_id}/consolidate")
        @limiter.limit(get_rate_limit_str())
        def consolidate_session(
            request: Request,
            session_id: int,
            payload: Optional[ConsolidatePayload] = Body(default=None),
            db: Session = Depends(get_session),
        ):
            try:
                elapsed_seconds = payload.elapsed_seconds if payload else None
                return service.consolidar_sesion(db, session_id, elapsed_seconds)
            except ValueError as e:
                if self.always_use_error_status:
                    raise HTTPException(self.consolidate_error_status, str(e))
                status = 404 if "not found" in str(e).lower() else self.consolidate_error_status
                raise HTTPException(status, str(e))

        @router.get("/sessions/{session_id}/state")
        def get_state(session_id: int, db: Session = Depends(get_session)):
            game_session = db.get(SessionModel, session_id)
            if not game_session:
                raise HTTPException(404, f"{SessionModel.__name__} not found")
            return self.format_state(game_session)

        @router.get("/sessions/{session_id}/history")
        def get_history(session_id: int, db: Session = Depends(get_session)):
            game_session = db.get(SessionModel, session_id)
            if not game_session:
                raise HTTPException(404, f"{SessionModel.__name__} not found")

            rounds = db.exec(
                select(self.RoundModel)
                .where(getattr(self.RoundModel, self.round_fk_field) == session_id)
                .order_by(self.RoundModel.created_at)
            ).all()

            # Batch fetch all attempts for these rounds in a single query (fixes N+1)
            round_ids = [r.id for r in rounds]
            attempts_by_round: dict[int, list] = defaultdict(list)
            if round_ids:
                all_attempts = db.exec(
                    select(self.AttemptModel)
                    .where(self.AttemptModel.round_id.in_(round_ids))
                    .order_by(self.AttemptModel.created_at)
                ).all()
                for a in all_attempts:
                    attempts_by_round[a.round_id].append(a)

            result = []
            for r in rounds:
                attempts = attempts_by_round.get(r.id, [])
                result.append(self.format_history_round(r, attempts))

            return {"rounds": result, "total": len(result)}

    def _extract_attempt_answer(self, body: BaseModel) -> Any:
        """Extract the answer value from the attempt body.

        Each game has a different field name for the answer:
        - memory: submitted_numbers
        - math: user_answer (float)
        - iq: user_answer (str)
        """
        data = body.model_dump()
        # Remove common non-answer fields
        for key in ("elapsed_seconds",):
            data.pop(key, None)
        # Return the first remaining value (the answer)
        if len(data) == 1:
            return next(iter(data.values()))
        # Fallback: try common field names
        for field in ("submitted_numbers", "user_answer", "answer"):
            if field in data:
                return data[field]
        raise ValueError(f"Cannot extract answer from body: {data}")


class ConsolidatePayload(BaseModel):
    elapsed_seconds: Optional[int] = None
