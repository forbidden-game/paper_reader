"""Session state management for resumable operations."""

from __future__ import annotations

import json
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class SessionState:
    """State for a paper_reader session.

    Attributes:
        session_id: Unique session identifier
        created_at: Session creation timestamp
        last_updated: Last update timestamp
        current_operation: Current operation name (if any)
        data: Arbitrary session data
    """

    session_id: str
    created_at: str
    last_updated: str
    current_operation: str | None = None
    data: dict[str, Any] | None = None

    def __post_init__(self: SessionState) -> None:
        """Initialize data dict if None."""
        if self.data is None:
            self.data = {}

    def save(self: SessionState, base_path: Path | None = None) -> None:
        """Save session state to JSON file.

        Args:
            base_path: Base directory for session data (default: .data/paper_reader)
        """
        if base_path is None:
            base_path = Path(".data/paper_reader")

        session_dir = base_path / self.session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        state_file = session_dir / "state.json"
        self.last_updated = datetime.now().isoformat()

        with open(state_file, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls: type[SessionState], session_id: str, base_path: Path | None = None) -> SessionState | None:
        """Load session state from JSON file.

        Args:
            session_id: Session identifier
            base_path: Base directory for session data (default: .data/paper_reader)

        Returns:
            SessionState if found, None otherwise
        """
        if base_path is None:
            base_path = Path(".data/paper_reader")

        state_file = base_path / session_id / "state.json"
        if not state_file.exists():
            return None

        with open(state_file) as f:
            data = json.load(f)
            return cls(**data)

    @staticmethod
    def get_session_dir(session_id: str, base_path: Path | None = None) -> Path:
        """Get directory for session data.

        Args:
            session_id: Session identifier
            base_path: Base directory for session data (default: .data/paper_reader)

        Returns:
            Path to session directory
        """
        if base_path is None:
            base_path = Path(".data/paper_reader")

        return base_path / session_id

    @classmethod
    def create_new(cls: type[SessionState], session_id: str | None = None) -> SessionState:
        """Create new session state.

        Args:
            session_id: Session identifier (default: timestamp-based)

        Returns:
            New SessionState instance
        """
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        now = datetime.now().isoformat()
        return cls(
            session_id=session_id,
            created_at=now,
            last_updated=now,
            current_operation=None,
            data={},
        )
