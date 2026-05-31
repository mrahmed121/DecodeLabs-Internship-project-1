#!/usr/bin/env python3
"""
================================================================================
  DECODELABS INDUSTRIAL TRAINING KIT — ARTIFICIAL INTELLIGENCE
  Project 4: Enterprise Conversational AI Agent (DecodeBot Personal)
  Rule-Based NLP Pipeline with Contextual Memory & Profile Management

  VVIP Professional Edition | Industry-Grade Refactor
  Batch: 2026 | Powered by DecodeLabs
================================================================================

Upgrades Applied:
  1. Secure Configuration Management (python-dotenv + os.environ)
  2. Advanced Error Handling & Custom Exception Hierarchy
  3. Interactive Terminal UI with Box-Drawing & Safe ANSI Colors
  4. Dual-Channel Auto-Logging (Console + app.log with session audit)
  5. Performance Optimization, Type Hints & Comprehensive Documentation
"""

from __future__ import annotations

import os
import re
import json
import random
import argparse
import logging
import logging.handlers
import sys
import textwrap
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List, Set, Final

from dotenv import load_dotenv

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 0 — SECURE CONFIGURATION MANAGEMENT (dotenv + Environment Variables)
# ═══════════════════════════════════════════════════════════════════════════════

load_dotenv(override=True)


class Config:
    """
    Centralized, secure configuration manager.

    All tunable parameters are injected via environment variables (/.env file)
    so that no hardcoded secrets, paths, or identity data ever touch version control.

    Usage:
        Create a `.env` file in the project root:
            LOG_LEVEL=INFO
            LOG_FILE=app.log
            MAX_HISTORY=20
            ROTATING_MAX_BYTES=2000000
            ROTATING_BACKUP_COUNT=3
            PROFILE_FILE=user_profile.json
    """
    LOG_LEVEL: Final[str]              = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE: Final[str]               = os.getenv("LOG_FILE", "app.log")
    LOG_DIR: Final[str]                = os.getenv("LOG_DIR", "logs")
    MAX_HISTORY: Final[int]            = int(os.getenv("MAX_HISTORY", "20"))
    ROTATING_MAX_BYTES: Final[int]     = int(os.getenv("ROTATING_MAX_BYTES", "2000000"))
    ROTATING_BACKUP_COUNT: Final[int]  = int(os.getenv("ROTATING_BACKUP_COUNT", "3"))
    PROFILE_FILE: Final[str]           = os.getenv("PROFILE_FILE", "user_profile.json")
    WEB_HOST: Final[str]               = os.getenv("WEB_HOST", "127.0.0.1")
    WEB_PORT: Final[int]               = int(os.getenv("WEB_PORT", "5000"))
    WEB_DEBUG: Final[bool]             = os.getenv("WEB_DEBUG", "False").lower() == "true"

    # Identity block — loaded from env for flexibility, with safe fallback
    IDENTITY_NAME: Final[str]            = os.getenv("IDENTITY_NAME", "Ahmed")
    IDENTITY_SPOUSE: Final[str]         = os.getenv("IDENTITY_SPOUSE", "Mariyum")
    IDENTITY_DISPLAY_NAME: Final[str]    = os.getenv("IDENTITY_DISPLAY_NAME", "MARIYUM KA AHMED")

    @classmethod
    def validate(cls) -> None:
        """Runtime validation of critical environment parameters."""
        if cls.MAX_HISTORY < 1:
            raise ValueError("MAX_HISTORY must be >= 1")
        if cls.ROTATING_MAX_BYTES < 1024:
            raise ValueError("ROTATING_MAX_BYTES must be >= 1024")
        if cls.WEB_PORT < 1 or cls.WEB_PORT > 65535:
            raise ValueError("WEB_PORT must be in [1, 65535]")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — CUSTOM EXCEPTION HIERARCHY (Advanced Error Handling)
# ═══════════════════════════════════════════════════════════════════════════════

class DecodeBotError(Exception):
    """Base exception for all DecodeBot domain errors."""
    pass


class ProfileIOError(DecodeBotError):
    """Raised when profile read/write operations fail (disk, permissions, JSON)."""
    pass


class IntentEngineError(DecodeBotError):
    """Raised when intent matching or regex compilation fails unexpectedly."""
    pass


class SessionStateError(DecodeBotError):
    """Raised when session history corruption or memory overflow is detected."""
    pass


class WebServerError(DecodeBotError):
    """Raised when Flask web UI initialization or runtime fails."""
    pass


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — AUTO-LOGGING SYSTEM (Dual-Channel: Console + File with Audit)
# ═══════════════════════════════════════════════════════════════════════════════

def initialize_logging() -> logging.Logger:
    """
    Initialize a production-grade logger with dual handlers and session audit.

    - StreamHandler   → Console (colored, human-readable, INFO+)
    - RotatingFileHandler → app.log (persistent, timestamped, DEBUG+)

    The file handler captures full session traces: user inputs, bot outputs,
    intent classifications, confidence scores, and timestamps for compliance debugging.

    Returns:
        logging.Logger: The root logger instance for the application.
    """
    logger = logging.getLogger("DecodeBot_VVIP")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers on re-import or reload
    if logger.handlers:
        return logger

    # ── Console Handler ───────────────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, Config.LOG_LEVEL, logging.INFO))
    console_fmt = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # ── Rotating File Handler (Persistent Audit Trail) ─────────────────────────
    log_dir = Path(Config.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / Config.LOG_FILE

    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=Config.ROTATING_MAX_BYTES,
        backupCount=Config.ROTATING_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    logger.info(
        "Logging infrastructure initialized | Dir: %s | File: %s | Level: %s | MaxHistory: %d",
        log_dir, log_path, Config.LOG_LEVEL, Config.MAX_HISTORY
    )
    return logger


LOGGER: Final[logging.Logger] = initialize_logging()


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — INTERACTIVE TERMINAL UI (Box-Drawing & Safe ANSI Colors)
# ═══════════════════════════════════════════════════════════════════════════════

class TerminalUI:
    """
    Production-grade terminal UI renderer using Unicode box-drawing characters.

    All ANSI color codes are wrapped in a safe toggle so the UI degrades gracefully
    on terminals that do not support color (e.g., Windows CMD without ANSI, CI logs).

    Attributes:
        _color (bool): Runtime flag indicating whether ANSI sequences are emitted.
    """

    # Unicode box-drawing glyphs for professional framing
    HORIZONTAL: Final[str] = "═"
    VERTICAL:   Final[str] = "║"
    TOP_LEFT:   Final[str] = "╔"
    TOP_RIGHT:  Final[str] = "╗"
    BOT_LEFT:   Final[str] = "╚"
    BOT_RIGHT:  Final[str] = "╝"
    T_LEFT:     Final[str] = "╠"
    T_RIGHT:    Final[str] = "╣"
    BULLET:     Final[str] = "▸"
    STAR:       Final[str] = "★"
    ARROW:      Final[str] = "➤"

    def __init__(self, use_color: bool = True) -> None:
        """
        Args:
            use_color: If False, all ANSI escape sequences are suppressed.
        """
        self._color = use_color and self._supports_ansi()

    @staticmethod
    def _supports_ansi() -> bool:
        """
        Heuristic to detect ANSI support.

        Disables colors on Windows legacy terminals unless ANSICON, WT_SESSION,
        or FORCE_COLOR=1 is present. Prevents garbage characters in CMD.
        """
        if os.getenv("FORCE_COLOR", "0") == "1":
            return True
        if os.name == "nt" and not os.getenv("ANSICON") and not os.getenv("WT_SESSION"):
            return False
        return sys.stdout.isatty()

    def _c(self, code: str, text: str) -> str:
        """Wrap text in an ANSI color code if colors are enabled."""
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def bold(self, text: str) -> str:
        return self._c("1", text)

    def green(self, text: str) -> str:
        return self._c("92", text)

    def yellow(self, text: str) -> str:
        return self._c("93", text)

    def red(self, text: str) -> str:
        return self._c("91", text)

    def cyan(self, text: str) -> str:
        return self._c("36", text)

    def magenta(self, text: str) -> str:
        return self._c("35", text)

    def blue(self, text: str) -> str:
        return self._c("94", text)

    def header(self, title: str, width: int = 78) -> str:
        """Render a framed header banner with centered title."""
        inner_width = width - 2
        pad_total = inner_width - len(title)
        pad_left = pad_total // 2
        pad_right = pad_total - pad_left
        line = f"{self.TOP_LEFT}{self.HORIZONTAL * inner_width}{self.TOP_RIGHT}"
        text_line = f"{self.VERTICAL}{' ' * pad_left}{self.bold(title)}{' ' * pad_right}{self.VERTICAL}"
        return f"\n{line}\n{text_line}\n{self.T_LEFT}{self.HORIZONTAL * inner_width}{self.T_RIGHT}"

    def footer(self, width: int = 78) -> str:
        """Render a closing footer banner."""
        inner_width = width - 2
        return f"{self.BOT_LEFT}{self.HORIZONTAL * inner_width}{self.BOT_RIGHT}\n"

    def info_line(self, label: str, value: str, width: int = 78) -> str:
        """Render a key-value pair inside the frame."""
        content = f"  {self.BULLET} {label}: {value}"
        padding = width - 2 - len(content)
        return f"{self.VERTICAL}{content}{' ' * max(padding, 0)}{self.VERTICAL}"

    def divider(self, width: int = 78) -> str:
        """Render a horizontal divider line."""
        inner_width = width - 2
        return f"{self.T_LEFT}{self.HORIZONTAL * inner_width}{self.T_RIGHT}"

    def status_badge(self, status: str, ok: bool = True) -> str:
        """Render a colored status badge."""
        if ok:
            return self.green(f"[ {status} ]")
        return self.red(f"[ {status} ]")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — DATA MODELS (Type-Safe Immutable Structures)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MatchResult:
    """
    Immutable data transfer object for a single intent match.

    Attributes:
        response: The final rendered response string sent to the user.
        intent_id: The classified intent identifier (e.g., 'greeting', 'fallback').
        confidence: Float in [0.0, 1.0] representing match certainty.
        slots: Extracted regex group dictionary (empty if no capture groups).
    """
    response: str
    intent_id: str
    confidence: float
    slots: Dict[str, str]


@dataclass
class SessionEntry:
    """Single turn in the conversation history with full audit metadata."""
    timestamp: str
    user_input: str
    bot_response: str
    intent_id: str
    confidence: float


@dataclass
class BotProfile:
    """Structured profile container with safe defaults from environment."""
    user_name: str = field(default_factory=lambda: Config.IDENTITY_NAME)
    spouse_name: str = field(default_factory=lambda: Config.IDENTITY_SPOUSE)
    display_name_response: str = field(default_factory=lambda: Config.IDENTITY_DISPLAY_NAME)
    notes: str = "Wife is loving and a bit stubborn; user loves her back."

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BotProfile":
        """Hydrate from dictionary with safe fallback for missing keys."""
        return cls(
            user_name=data.get("user_name", Config.IDENTITY_NAME),
            spouse_name=data.get("spouse_name", Config.IDENTITY_SPOUSE),
            display_name_response=data.get("display_name_response", Config.IDENTITY_DISPLAY_NAME),
            notes=data.get("notes", "")
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 — PROFILE MANAGEMENT (Secure I/O with Error Shielding)
# ═══════════════════════════════════════════════════════════════════════════════

class ProfileManager:
    """
    Handles persistent storage and retrieval of user/bot profiles.

    All disk I/O is wrapped in try-except shields to prevent crashes from
    permission errors, disk-full conditions, or JSON corruption.
    """

    def __init__(self, profile_path: Optional[Path] = None) -> None:
        self.path: Path = profile_path or Path(Config.PROFILE_FILE)
        LOGGER.debug("ProfileManager initialized | Target: %s", self.path.resolve())

    def load(self) -> BotProfile:
        """
        Load profile from JSON disk storage.

        Returns:
            BotProfile: Hydrated profile object.

        Raises:
            ProfileIOError: If the file exists but is unreadable or corrupt.
        """
        if not self.path.exists():
            LOGGER.info("No existing profile found at '%s'. Creating default.", self.path)
            default = BotProfile()
            self.save(default)
            return default

        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                raw_data: Dict[str, Any] = json.load(fh)
            LOGGER.info("Profile loaded successfully | Keys: %s", list(raw_data.keys()))
            return BotProfile.from_dict(raw_data)
        except json.JSONDecodeError as exc:
            LOGGER.error("Profile JSON corruption detected: %s", exc)
            raise ProfileIOError(f"Profile JSON is corrupt: {exc}") from exc
        except OSError as exc:
            LOGGER.error("OS error reading profile: %s", exc)
            raise ProfileIOError(f"Cannot read profile file: {exc}") from exc
        except Exception as exc:
            LOGGER.exception("Unexpected profile load failure")
            raise ProfileIOError(f"Unexpected profile load error: {exc}") from exc

    def save(self, profile: BotProfile, alternate_path: Optional[Path] = None) -> None:
        """
        Persist profile to JSON disk storage with atomic write pattern.

        Args:
            profile: The profile object to serialize.
            alternate_path: Optional override destination (for export commands).

        Raises:
            ProfileIOError: If write fails due to permissions, disk space, etc.
        """
        target = alternate_path or self.path
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            # Atomic write: write to temp file, then rename to avoid corruption on crash
            temp_path = target.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as fh:
                json.dump(profile.to_dict(), fh, indent=2, ensure_ascii=False)
            temp_path.replace(target)
            LOGGER.info("Profile saved | Destination: %s", target.resolve())
        except OSError as exc:
            LOGGER.error("OS error writing profile: %s", exc)
            raise ProfileIOError(f"Cannot write profile file: {exc}") from exc
        except Exception as exc:
            LOGGER.exception("Unexpected profile save failure")
            raise ProfileIOError(f"Unexpected profile save error: {exc}") from exc


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — INTENT ENGINE (Rule-Based NLP with Confidence Scoring)
# ═══════════════════════════════════════════════════════════════════════════════

class IntentEngine:
    """
    Production-grade rule-based intent classification engine.

    Matching Strategy (priority order):
        1. Exact normalized phrase match (confidence = 1.0)
        2. Regex pattern match with named capture groups (confidence = 0.85)
        3. Token-level contains match (confidence = 0.70)
        4. Fallback response (confidence = 0.35)

    The engine is stateless; all mutable state (profile) is injected at match time.
    """

    # Embedded baseline intent corpus — can be overridden via external JSON
    DEFAULT_INTENTS: Final[Dict[str, Any]] = {
        "intents": [
            {
                "id": "greeting",
                "examples": ["hi", "hello", "hey", "hola", "yo"],
                "regex": r"^(hi+|hello+|hey+|hola|yo)$",
                "responses": [
                    "Hello! How can I help you today?",
                    "Hey there! What can I do for you?",
                    "Hi! Ready to assist."
                ],
                "priority": 10
            },
            {
                "id": "goodbye",
                "examples": ["bye", "goodbye", "exit", "quit", "see you"],
                "regex": r"\b(bye|goodbye|exit|quit|see you)\b",
                "responses": [
                    "Goodbye! Have a great day.",
                    "See you later! Take care.",
                    "Bye! Come back anytime."
                ],
                "priority": 100
            },
            {
                "id": "thanks",
                "examples": ["thanks", "thank you", "ty", "appreciate it"],
                "regex": r"\b(thanks?|thank you|ty|appreciate)\b",
                "responses": [
                    "You're welcome!",
                    "Happy to help!",
                    "Anytime!"
                ],
                "priority": 5
            },
            {
                "id": "identity",
                "examples": [
                    "what is your name",
                    "who are you",
                    "your name",
                    "tell me your details",
                    "introduce yourself"
                ],
                "regex": r"(who\s+are\s+you|what('?s| is)\s+your\s+name|tell\s+me\s+your\s+details|introduce\s+yourself)",
                "responses": ["__PERSONAL_NAME__"],
                "priority": 8
            },
            {
                "id": "status",
                "examples": ["how are you", "how are you doing", "hows it going"],
                "regex": r"(how\s+are\s+you|how\s+are\s+u|how('?s| is)\s+it\s+going)",
                "responses": [
                    "I'm a program, running smoothly — thanks for asking!",
                    "All systems operational. How about you?"
                ],
                "priority": 5
            },
            {
                "id": "help",
                "examples": ["help", "what can you do", "commands", "menu"],
                "regex": r"\b(help|what\s+can\s+you\s+do|commands?|menu)\b",
                "responses": [
                    "I can respond to greetings, answer questions, and manage your profile.\n"
                    "Admin commands: /profile-show, /profile-set key=value, /profile-export file.json, /profile-import file.json"
                ],
                "priority": 6
            },
            {
                "id": "tell_me_about_user",
                "examples": ["tell me about me", "who am i", "my details", "about me"],
                "regex": r"(tell\s+me\s+about\s+me|who\s+am\s+i|my\s+details|about\s+me)",
                "responses": ["__USER_PROFILE__"],
                "priority": 4
            }
        ],
        "fallback": {
            "responses": [
                "Sorry, I didn't understand that. Can you rephrase?",
                "I don't have an answer for that yet. Try 'help' for options.",
                "Hmm, I'm not sure about that. Could you ask differently?"
            ]
        }
    }

    def __init__(self, intents: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the intent engine with an optional custom intent corpus.

        Args:
            intents: External intent dictionary. If None, DEFAULT_INTENTS is used.
        """
        self._intents_raw: Dict[str, Any] = intents or self.DEFAULT_INTENTS.copy()
        self._intents: List[Dict[str, Any]] = self._intents_raw.get("intents", [])
        self._fallbacks: List[str] = self._intents_raw.get("fallback", {}).get("responses", ["I do not understand."])

        # Pre-build normalized phrase map for O(1) exact lookups
        self._phrase_map: Dict[str, Dict[str, Any]] = {}
        for intent in self._intents:
            for ex in intent.get("examples", []):
                self._phrase_map[self._normalize(ex)] = intent

        # Pre-compile all regex patterns for performance
        self._regex_cache: Dict[str, re.Pattern] = {}
        for intent in self._intents:
            pattern = intent.get("regex", "")
            if pattern:
                try:
                    self._regex_cache[intent["id"]] = re.compile(pattern, re.IGNORECASE)
                except re.error as exc:
                    LOGGER.error("Regex compile failure for intent '%s': %s", intent.get("id"), exc)
                    raise IntentEngineError(f"Invalid regex for intent {intent.get('id')}: {exc}") from exc

        LOGGER.info("IntentEngine initialized | Intents: %d | Regex cached: %d", len(self._intents), len(self._regex_cache))

    @staticmethod
    def _normalize(text: Optional[str]) -> str:
        """
        Normalize raw user input for consistent matching.

        Pipeline:
            1. Lowercase
            2. Strip whitespace
            3. Remove non-alphanumeric characters (except spaces, apostrophes, ?!)
            4. Collapse multiple spaces to single space

        Args:
            text: Raw user input string.

        Returns:
            str: Normalized, match-ready string.
        """
        if text is None:
            return ""
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s'?!]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _render_response(self, template: str, profile: BotProfile) -> str:
        """
        Replace magic template tokens with dynamic profile data.

        Supported tokens:
            __PERSONAL_NAME__  → Identity story block
            __USER_PROFILE__   → User profile summary

        Args:
            template: Raw response template from intent definition.
            profile: Current active profile for personalization.

        Returns:
            str: Fully rendered response string.
        """
        if template == "__PERSONAL_NAME__":
            identity = (
                f"My name is {profile.user_name}, but my absolute identity is '{profile.display_name_response}'. "
                f"If you want to know my details: My wifey's name is {profile.spouse_name}. "
                f"She is incredibly stubborn (bhot ziddi hai) but she is extremely beautiful and cute (bhoot pyari hai). "
                f"She loves me deeply, and I love her immensely in return."
            )
            return identity

        if template == "__USER_PROFILE__":
            return (
                f"My user is {profile.user_name}. "
                f"Their spouse is {profile.spouse_name}. "
                f"Notes: {profile.notes}"
            )

        return template

    def match(self, user_input: str, profile: BotProfile) -> MatchResult:
        """
        Classify user input against the intent corpus and return a MatchResult.

        The matching pipeline follows strict priority order:
            1. Exact normalized phrase map lookup (confidence 1.0)
            2. Regex pattern match (confidence 0.85)
            3. Token-level contains/substring match (confidence 0.70)
            4. Fallback (confidence 0.35)

        CRITICAL TRIGGER OVERRIDE:
            If the matched intent is 'greeting', 'identity', or 'tell_me_about_user',
            the identity story block is force-injected regardless of the template.

        Args:
            user_input: Raw string from the user.
            profile: Active BotProfile for personalization rendering.

        Returns:
            MatchResult: Immutable match result with response, intent, confidence, slots.
        """
        norm = self._normalize(user_input)
        matched_intent: Optional[Dict[str, Any]] = None
        slots: Dict[str, str] = {}
        confidence = 0.0

        # ── 1) Exact phrase matching (O(1) lookup) ────────────────────────────────
        if norm in self._phrase_map:
            matched_intent = self._phrase_map[norm]
            confidence = 1.0
            LOGGER.debug("Exact match | Intent: %s | Input: %s", matched_intent.get("id"), user_input)

        # ── 2) Priority-based regex matching ────────────────────────────────────
        if not matched_intent:
            for intent in sorted(self._intents, key=lambda i: -i.get("priority", 0)):
                intent_id = intent.get("id", "")
                compiled = self._regex_cache.get(intent_id)
                if not compiled:
                    continue

                m = compiled.search(norm)
                if m:
                    slots = m.groupdict() if m.groupdict() else {}
                    matched_intent = intent
                    confidence = 0.85
                    LOGGER.debug("Regex match | Intent: %s | Pattern matched: %s", intent_id, m.group(0))
                    break

        # ── 3) Token-level contains / substring matching ──────────────────────────
        if not matched_intent:
            for intent in sorted(self._intents, key=lambda i: -i.get("priority", 0)):
                found = False
                for ex in intent.get("examples", []):
                    ex_norm = self._normalize(ex)
                    if " " in ex_norm:
                        if ex_norm in norm:
                            found = True
                            break
                    else:
                        if ex_norm in set(norm.split()):
                            found = True
                            break
                if found:
                    matched_intent = intent
                    confidence = 0.70
                    LOGGER.debug("Contains match | Intent: %s", intent.get("id"))
                    break

        # ── Response Rendering ────────────────────────────────────────────────────
        if matched_intent:
            intent_id = matched_intent.get("id", "unknown")
            resp_template = random.choice(matched_intent.get("responses", [""]))
            base_response = self._render_response(resp_template, profile)

            # CRITICAL TRIGGER OVERRIDE: Force identity injection on key intents
            if intent_id in ("greeting", "identity", "tell_me_about_user"):
                identity = self._render_response("__PERSONAL_NAME__", profile)
                final_response = f"{identity}\n\nHow can I help you today?"
                LOGGER.info("Identity override triggered | Intent: %s", intent_id)
                return MatchResult(
                    response=final_response,
                    intent_id=intent_id,
                    confidence=confidence,
                    slots=slots
                )

            return MatchResult(
                response=base_response,
                intent_id=intent_id,
                confidence=confidence,
                slots=slots
            )

        # ── 4) Fallback ───────────────────────────────────────────────────────
        fallback_resp = random.choice(self._fallbacks)
        LOGGER.debug("Fallback triggered | Input: %s", user_input)
        return MatchResult(
            response=fallback_resp,
            intent_id="fallback",
            confidence=0.35,
            slots={}
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 7 — SESSION MANAGER (Contextual Memory with Audit Logging)
# ═══════════════════════════════════════════════════════════════════════════════

class SessionManager:
    """
    Manages conversational state with bounded history and full audit logging.

    Each turn (user input + bot response) is logged to the file handler
    with timestamp, intent, and confidence for post-session debugging.
    """

    def __init__(self, session_id: str, max_history: int = 20) -> None:
        self.session_id: str = session_id
        self.max_history: int = max_history
        self._history: List[SessionEntry] = []
        self._start_time: str = datetime.now().isoformat()
        LOGGER.info("Session initialized | ID: %s | MaxHistory: %d", session_id, max_history)

    def push(self, user_input: str, match_result: MatchResult) -> None:
        """
        Record a conversation turn and rotate history if capacity exceeded.

        Args:
            user_input: Raw user message.
            match_result: The engine's classification result.

        Raises:
            SessionStateError: If history corruption is detected (should never occur).
        """
        entry = SessionEntry(
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            bot_response=match_result.response,
            intent_id=match_result.intent_id,
            confidence=match_result.confidence
        )
        self._history.append(entry)

        # Audit log every turn to file (debug level)
        LOGGER.debug(
            "SESSION_TURN | id=%s | intent=%s | conf=%.2f | user=%s | bot=%s",
            self.session_id,
            entry.intent_id,
            entry.confidence,
            entry.user_input[:60],
            entry.bot_response[:60]
        )

        # Bounded FIFO rotation
        if len(self._history) > self.max_history:
            removed = self._history.pop(0)
            LOGGER.debug("History rotated | Dropped oldest turn: %s", removed.intent_id)

    def get_history(self) -> List[SessionEntry]:
        """Return a shallow copy of the current history list."""
        return self._history.copy()

    def summary(self) -> str:
        """Generate a human-readable session summary."""
        lines = [
            f"Session ID: {self.session_id}",
            f"Started: {self._start_time}",
            f"Total Turns: {len(self._history)}",
            f"Avg Confidence: {sum(e.confidence for e in self._history) / max(len(self._history), 1):.2f}"
        ]
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 8 — ADMIN COMMAND PROCESSOR (Profile CRUD Operations)
# ═══════════════════════════════════════════════════════════════════════════════

class AdminProcessor:
    """
    Handles slash-prefixed administrative commands with validation and logging.

    Supported commands:
        /profile-show              → Display current profile as JSON
        /profile-set key=value     → Update a single profile field
        /profile-export path.json  → Export profile to alternate path
        /profile-import path.json  → Import profile from external JSON
        /session-summary           → Display current session statistics
        /help                      → Show available admin commands
    """

    def __init__(self, profile_manager: ProfileManager, session_manager: SessionManager) -> None:
        self._pm = profile_manager
        self._sm = session_manager
        self._ui = TerminalUI()

    def process(self, cmd: str, current_profile: BotProfile) -> Tuple[str, Optional[BotProfile]]:
        """
        Parse and execute an admin command.

        Args:
            cmd: Raw command string starting with '/'.
            current_profile: The currently loaded profile (may be mutated on set/import).

        Returns:
            Tuple[str, Optional[BotProfile]]: (response_message, updated_profile_or_None)
        """
        parts = cmd.strip().split(maxsplit=1)
        action = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        LOGGER.info("Admin command received | Action: %s | Args: %s", action, arg)

        try:
            if action == "/help":
                return self._cmd_help(), None

            if action == "/profile-show":
                return self._cmd_profile_show(current_profile), None

            if action == "/profile-set":
                return self._cmd_profile_set(arg, current_profile)

            if action == "/profile-export":
                return self._cmd_profile_export(arg, current_profile), None

            if action == "/profile-import":
                return self._cmd_profile_import(arg)

            if action == "/session-summary":
                return self._cmd_session_summary(), None

            return f"Unknown admin command: {action}. Type /help for available commands.", None

        except ProfileIOError as exc:
            LOGGER.error("Admin command failed | Action: %s | Error: %s", action, exc)
            return f"{self._ui.red('[Profile Error]')} {exc}", None
        except Exception as exc:
            LOGGER.exception("Unexpected admin command failure | Action: %s", action)
            return f"{self._ui.red('[System Error]')} Command failed: {exc}", None

    def _cmd_help(self) -> str:
        commands = [
            ("/help", "Show this help message"),
            ("/profile-show", "Display current profile as formatted JSON"),
            ("/profile-set key=value", "Update a profile field (e.g., notes=New note)"),
            ("/profile-export path.json", "Export profile to a JSON file"),
            ("/profile-import path.json", "Import profile from a JSON file"),
            ("/session-summary", "Show session turn count and average confidence")
        ]
        lines = [f"  {self._ui.cyan(cmd):<28} {desc}" for cmd, desc in commands]
        return "Available Admin Commands:\n" + "\n".join(lines)

    def _cmd_profile_show(self, profile: BotProfile) -> str:
        data = profile.to_dict()
        pretty = json.dumps(data, indent=2, ensure_ascii=False)
        return f"Current Profile:\n{self._ui.green(pretty)}"

    def _cmd_profile_set(self, arg: str, profile: BotProfile) -> Tuple[str, Optional[BotProfile]]:
        if "=" not in arg:
            return "Usage: /profile-set key=value", None
        key, value = arg.split("=", 1)
        key, value = key.strip(), value.strip()

        if key not in ("user_name", "spouse_name", "display_name_response", "notes"):
            return f"Invalid key '{key}'. Valid keys: user_name, spouse_name, display_name_response, notes", None

        setattr(profile, key, value)
        self._pm.save(profile)
        LOGGER.info("Profile field updated | Key: %s | Value: %s", key, value)
        return f"Profile updated: {self._ui.bold(key)} = {self._ui.green(value)}", profile

    def _cmd_profile_export(self, arg: str, profile: BotProfile) -> str:
        if not arg:
            return "Usage: /profile-export path.json"
        path = Path(arg)
        self._pm.save(profile, alternate_path=path)
        return f"Profile exported to {self._ui.green(str(path.resolve()))}"

    def _cmd_profile_import(self, arg: str) -> Tuple[str, Optional[BotProfile]]:
        if not arg:
            return "Usage: /profile-import path.json", None
        path = Path(arg)
        if not path.exists():
            return f"{self._ui.red('File not found:')} {path}", None
        new_profile = self._pm.load()  # This loads default path; need to load from arg
        # Actually we need to load from the specified path
        temp_pm = ProfileManager(profile_path=path)
        imported = temp_pm.load()
        self._pm.save(imported)
        LOGGER.info("Profile imported from %s", path.resolve())
        return f"Profile imported from {self._ui.green(str(path.resolve()))}", imported

    def _cmd_session_summary(self) -> str:
        return self._sm.summary()


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 9 — CLI INTERFACE (Interactive Loop with Graceful Shutdown)
# ═══════════════════════════════════════════════════════════════════════════════

class CLIInterface:
    """
    Production-grade command-line interface for DecodeBot.

    Features:
        - Framed banners and colored prompts
        - Graceful KeyboardInterrupt / EOFError handling
        - Admin command routing
        - Full session audit logging
        - Exit detection via intent or explicit keywords
    """

    def __init__(self, engine: IntentEngine, profile_manager: ProfileManager) -> None:
        self._engine = engine
        self._pm = profile_manager
        self._ui = TerminalUI()
        self._profile: BotProfile = self._pm.load()
        self._session = SessionManager(session_id=f"cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self._admin = AdminProcessor(profile_manager, self._session)

    def run(self) -> None:
        """Main interactive event loop."""
        print(self._ui.header("DECODEBOT PERSONAL — VVIP EDITION"))
        print(f"{self._ui.VERTICAL}  {self._ui.cyan('Type your message and press Enter.')}{' ' * 48}{self._ui.VERTICAL}")
        print(f"{self._ui.VERTICAL}  {self._ui.yellow('Admin commands start with /  |  Type "bye" or "exit" to quit.')}{' ' * 15}{self._ui.VERTICAL}")
        print(self._ui.divider())

        while True:
            try:
                user_input = input(f"{self._ui.ARROW} You: ").strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n{self._ui.yellow('\nSession interrupted by user. Goodbye!')}")
                LOGGER.info("Session terminated via KeyboardInterrupt/EOF")
                break

            if not user_input:
                print(f"{self._ui.ARROW} Bot: {self._ui.yellow('Please type something so I can respond.')}")
                continue

            # ── Admin Command Routing ───────────────────────────────────────────
            if user_input.startswith("/"):
                response, updated_profile = self._admin.process(user_input, self._profile)
                if updated_profile:
                    self._profile = updated_profile
                print(f"{self._ui.ARROW} Bot: {response}")
                LOGGER.info("Admin response | Cmd: %s", user_input)
                continue

            # ── Intent Classification ───────────────────────────────────────────
            try:
                result = self._engine.match(user_input, self._profile)
            except IntentEngineError as exc:
                LOGGER.error("Intent engine failure: %s", exc)
                print(f"{self._ui.ARROW} Bot: {self._ui.red('Internal error processing your message. Please try again.')}")
                continue

            # ── Response & Session Recording ──────────────────────────────────────
            print(f"{self._ui.ARROW} Bot: {result.response}")
            self._session.push(user_input, result)

            LOGGER.info(
                "chat_turn | intent=%s | conf=%.2f | user=%s",
                result.intent_id, result.confidence, user_input[:80]
            )

            # ── Exit Detection ──────────────────────────────────────────────────
            if result.intent_id == "goodbye" or re.search(r"\b(exit|quit|bye|goodbye|stop)\b", self._engine._normalize(user_input)):
                print(f"\n{self._ui.green('Session ended gracefully. See you soon!')}")
                LOGGER.info("Session ended via goodbye intent or exit keyword")
                break

        # Session close summary
        print(self._ui.divider())
        print(self._session.summary())
        print(self._ui.footer())


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 10 — OPTIONAL WEB UI (Flask Backend with JSON API)
# ═══════════════════════════════════════════════════════════════════════════════

def run_web_ui(host: str, port: int, debug: bool, engine: IntentEngine, profile_manager: ProfileManager) -> None:
    """
    Launch an optional Flask-based web UI for browser-based interaction.

    Endpoints:
        GET  /          → Serves the embedded HTML chat interface
        POST /api/chat  → JSON API: {msg: string} → {reply, intent, confidence, slots}

    Args:
        host: Bind address (default 127.0.0.1).
        port: Bind port (default 5000).
        debug: Flask debug mode flag.
        engine: Initialized IntentEngine instance.
        profile_manager: Initialized ProfileManager instance.

    Raises:
        WebServerError: If Flask is not installed or initialization fails.
    """
    try:
        from flask import Flask, request, jsonify, render_template_string
    except ImportError as exc:
        LOGGER.error("Flask not installed. Install with: pip install Flask")
        raise WebServerError("Flask dependency missing. Run: pip install Flask") from exc

    profile = profile_manager.load()
    app = Flask(__name__)

    # Embedded single-page chat interface
    HTML_TEMPLATE = """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>DecodeBot Personal — VVIP Edition</title>
        <style>
            :root { --bg:#0f1117; --card:#1a1d27; --text:#e8eaf6; --user:#4caf50; --bot:#7986cb; --accent:#ff8a65; }
            * { box-sizing:border-box; margin:0; padding:0; }
            body { font-family:'Segoe UI',Arial,sans-serif; background:var(--bg); color:var(--text); height:100vh; display:flex; flex-direction:column; }
            header { padding:1rem; background:var(--card); border-bottom:2px solid var(--accent); text-align:center; }
            #chat { flex:1; padding:1rem; overflow:auto; display:flex; flex-direction:column; gap:0.75rem; }
            .msg { max-width:80%; padding:0.75rem 1rem; border-radius:12px; line-height:1.4; white-space:pre-wrap; }
            .user { align-self:flex-end; background:var(--user); color:#fff; }
            .bot { align-self:flex-start; background:var(--bot); color:#fff; }
            .meta { font-size:0.7rem; opacity:0.7; margin-top:0.25rem; }
            #controls { display:flex; padding:1rem; gap:0.5rem; background:var(--card); border-top:1px solid #333; }
            #msg { flex:1; padding:0.75rem; border:none; border-radius:8px; background:#2e3250; color:var(--text); font-size:1rem; }
            button { padding:0.75rem 1.5rem; border:none; border-radius:8px; background:var(--accent); color:#fff; font-weight:bold; cursor:pointer; }
            button:hover { filter:brightness(1.1); }
        </style>
    </head>
    <body>
        <header><h2>DecodeBot Personal — VVIP Edition</h2><p>Powered by DecodeLabs | Batch 2026</p></header>
        <div id="chat"></div>
        <div id="controls">
            <input id="msg" placeholder="Type your message..." autofocus autocomplete="off">
            <button onclick="send()">Send</button>
        </div>
        <script>
            function append(role, text, meta='') {
                const d = document.createElement('div');
                d.className = 'msg ' + role;
                d.innerHTML = text.replace(/\n/g,'<br>') + (meta ? `<div class="meta">${meta}</div>` : '');
                document.getElementById('chat').appendChild(d);
                document.getElementById('chat').scrollTop = document.getElementById('chat').scrollHeight;
            }
            async function send() {
                const m = document.getElementById('msg');
                if (!m.value.trim()) return;
                append('user', m.value);
                try {
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {'Content-Type':'application/json'},
                        body: JSON.stringify({msg: m.value})
                    });
                    const j = await res.json();
                    append('bot', j.reply, `intent: ${j.intent} | confidence: ${(j.confidence*100).toFixed(0)}%`);
                } catch(e) {
                    append('bot', 'Error: Could not reach server.');
                }
                m.value = '';
            }
            document.getElementById('msg').addEventListener('keypress', e => { if(e.key==='Enter') send(); });
        </script>
    </body>
    </html>
    """

    @app.route("/")
    def index() -> str:
        return render_template_string(HTML_TEMPLATE)

    @app.route("/api/chat", methods=["POST"])
    def chat() -> Any:
        data = request.get_json() or {}
        msg = data.get("msg", "").strip()
        if not msg:
            return jsonify({"error": "Empty message"}), 400
        result = engine.match(msg, profile)
        return jsonify({
            "reply": result.response,
            "intent": result.intent_id,
            "confidence": result.confidence,
            "slots": result.slots
        })

    LOGGER.info("Starting web UI | Host: %s | Port: %d | Debug: %s", host, port, debug)
    print(f"\n{TerminalUI().green(f'Starting web server at http://{host}:{port}')}\n")
    try:
        app.run(host=host, port=port, debug=debug)
    except Exception as exc:
        LOGGER.exception("Web server runtime failure")
        raise WebServerError(f"Flask runtime error: {exc}") from exc


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 11 — SELF-TEST SUITE (Automated Regression Testing)
# ═══════════════════════════════════════════════════════════════════════════════

def run_self_test(engine: IntentEngine, profile: BotProfile) -> bool:
    """
    Execute a built-in regression test suite against the intent engine.

    Tests cover exact matches, regex matches, contains matches, and fallback
    behavior to ensure no regressions after code changes.

    Args:
        engine: Initialized IntentEngine.
        profile: BotProfile for rendering magic templates.

    Returns:
        bool: True if all tests pass, False otherwise.
    """
    ui = TerminalUI()
    tests: List[Tuple[str, str]] = [
        ("Hi", "greeting"),
        ("bye", "goodbye"),
        ("What's your name?", "identity"),
        ("How are you?", "status"),
        ("Tell me about me", "tell_me_about_user"),
        ("qwertyuiop12345", "fallback"),
        ("help", "help"),
        ("thanks a lot", "thanks"),
    ]

    print(ui.header("SELF-TEST REGRESSION SUITE"))
    passed = 0
    failed = 0

    for inp, expected in tests:
        try:
            result = engine.match(inp, profile)
            ok = (result.intent_id == expected)
            status = ui.green("PASS") if ok else ui.red("FAIL")
            intent_label = ui.cyan(result.intent_id) if ok else ui.red(result.intent_id)
            print(f"{ui.VERTICAL}  {status} | Input: {inp!r:<25} | Expected: {ui.cyan(expected):<20} | Got: {intent_label}{' ' * 10}{ui.VERTICAL}")
            if ok:
                passed += 1
            else:
                failed += 1
                LOGGER.warning("Self-test failure | Input: %s | Expected: %s | Got: %s", inp, expected, result.intent_id)
        except Exception as exc:
            print(f"{ui.VERTICAL}  {ui.red('ERROR')} | Input: {inp!r:<25} | Exception: {exc}{' ' * 20}{ui.VERTICAL}")
            failed += 1
            LOGGER.exception("Self-test exception | Input: %s", inp)

    print(ui.divider())
    total = len(tests)
    pct = (passed / total) * 100 if total else 0
    color = ui.green if failed == 0 else ui.yellow if failed <= 2 else ui.red
    print(f"{ui.VERTICAL}  {color(f'Results: {passed}/{total} passed ({pct:.0f}%)')} {' ' * 50}{ui.VERTICAL}")
    print(ui.footer())

    LOGGER.info("Self-test completed | Passed: %d | Failed: %d | Total: %d", passed, failed, total)
    return failed == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 12 — MAIN ORCHESTRATOR (Graceful Entry Point with Top-Level Shield)
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    """
    Application entry point with top-level exception shielding.

    Parses CLI arguments, validates configuration, initializes subsystems,
    and dispatches to CLI or Web UI mode.

    Any unhandled exception is caught, logged to app.log, and presented
    to the user as a clean error message without exposing stack traces.
    """
    parser = argparse.ArgumentParser(
        description="DecodeBot Personal — VVIP Edition | Enterprise Conversational AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python decodebot_vvip.py              # Run interactive CLI
  python decodebot_vvip.py --web        # Run web UI (requires Flask)
  python decodebot_vvip.py --selftest   # Run regression tests
  python decodebot_vvip.py --debug       # Enable debug logging
        """
    )
    parser.add_argument("--log", action="store_true", help="Enable persistent file logging (already default)")
    parser.add_argument("--web", action="store_true", help="Run web UI server (requires Flask)")
    parser.add_argument("--selftest", action="store_true", help="Run built-in regression test suite")
    parser.add_argument("--debug", action="store_true", help="Enable DEBUG level logging to console")
    args = parser.parse_args()

    # Override log level if --debug is passed
    if args.debug:
        logging.getLogger("DecodeBot_VVIP").setLevel(logging.DEBUG)
        for handler in logging.getLogger("DecodeBot_VVIP").handlers:
            handler.setLevel(logging.DEBUG)

    # Configuration validation
    try:
        Config.validate()
    except ValueError as exc:
        LOGGER.error("Configuration validation failed: %s", exc)
        print(f"\n{TerminalUI(use_color=True).red(f'[CONFIG ERROR] {exc}')}\n")
        sys.exit(1)

    # Initialize core subsystems
    try:
        profile_manager = ProfileManager()
        profile = profile_manager.load()
        engine = IntentEngine()
    except (ProfileIOError, IntentEngineError) as exc:
        LOGGER.error("Subsystem initialization failure: %s", exc)
        print(f"\n{TerminalUI(use_color=True).red(f'[INIT ERROR] {exc}')}\n")
        sys.exit(1)

    # Dispatch to mode
    try:
        if args.selftest:
            ok = run_self_test(engine, profile)
            sys.exit(0 if ok else 2)

        if args.web:
            run_web_ui(
                host=Config.WEB_HOST,
                port=Config.WEB_PORT,
                debug=Config.WEB_DEBUG,
                engine=engine,
                profile_manager=profile_manager
            )
        else:
            cli = CLIInterface(engine, profile_manager)
            cli.run()

    except DecodeBotError as exc:
        LOGGER.error("DecodeBot domain error: %s", exc)
        print(f"\n{TerminalUI(use_color=True).red(f'[APPLICATION ERROR] {exc}')}\n")
        sys.exit(1)
    except Exception as exc:
        LOGGER.exception("Unhandled runtime exception")
        print(f"\n{TerminalUI(use_color=True).red(f'[CRITICAL FAILURE] An unexpected error occurred. Check {Config.LOG_FILE} for details.')}")
        sys.exit(1)


if __name__ == "__main__":
    main()