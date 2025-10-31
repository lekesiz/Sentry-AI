"""
Database module for Sentry-AI.

This module handles all database operations using SQLAlchemy,
including action logging, statistics, and configuration persistence.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from .config import settings

# Create base class for models
Base = declarative_base()


class ActionLogDB(Base):
    """Database model for action logs."""
    
    __tablename__ = "action_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    app_name = Column(String(255), nullable=False, index=True)
    window_title = Column(String(255), nullable=True)
    dialog_type = Column(String(50), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # JSON string
    chosen_option = Column(String(255), nullable=False)
    ai_confidence = Column(Float, nullable=True)
    ai_reasoning = Column(Text, nullable=True)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"<ActionLog(id={self.id}, app={self.app_name}, option={self.chosen_option})>"


class UserPreferenceDB(Base):
    """Database model for user preferences learned over time."""
    
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    app_name = Column(String(255), nullable=False, index=True)
    dialog_pattern = Column(String(500), nullable=False)
    preferred_option = Column(String(255), nullable=False)
    confidence = Column(Float, default=1.0)
    usage_count = Column(Integer, default=1)
    last_used = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<UserPreference(app={self.app_name}, option={self.preferred_option})>"


class SystemStatDB(Base):
    """Database model for system statistics."""
    
    __tablename__ = "system_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.now, nullable=False, index=True)
    total_actions = Column(Integer, default=0)
    successful_actions = Column(Integer, default=0)
    failed_actions = Column(Integer, default=0)
    avg_execution_time_ms = Column(Float, default=0.0)
    most_active_app = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<SystemStat(date={self.date}, actions={self.total_actions})>"


class DatabaseManager:
    """Manager class for database operations."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the database manager.
        
        Args:
            database_url: Database connection URL (defaults to settings)
        """
        self.database_url = database_url or settings.database_url
        self.engine = create_engine(self.database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        logger.info(f"Database initialized: {self.database_url}")
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def log_action(
        self,
        app_name: str,
        dialog_type: str,
        question: str,
        options: List[str],
        chosen_option: str,
        success: bool,
        execution_time_ms: float,
        window_title: Optional[str] = None,
        ai_confidence: Optional[float] = None,
        ai_reasoning: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Optional[int]:
        """
        Log an action to the database.
        
        Returns:
            The ID of the created log entry, or None if failed
        """
        session = self.get_session()
        try:
            import json
            
            log_entry = ActionLogDB(
                app_name=app_name,
                window_title=window_title,
                dialog_type=dialog_type,
                question=question,
                options=json.dumps(options),
                chosen_option=chosen_option,
                ai_confidence=ai_confidence,
                ai_reasoning=ai_reasoning,
                success=success,
                error_message=error_message,
                execution_time_ms=execution_time_ms
            )
            
            session.add(log_entry)
            session.commit()
            
            log_id = log_entry.id
            logger.debug(f"Action logged to database (ID: {log_id})")
            
            return log_id
        
        except Exception as e:
            logger.error(f"Error logging action to database: {e}")
            session.rollback()
            return None
        
        finally:
            session.close()
    
    def get_recent_actions(self, limit: int = 50) -> List[ActionLogDB]:
        """Get the most recent actions."""
        session = self.get_session()
        try:
            return session.query(ActionLogDB)\
                .order_by(ActionLogDB.timestamp.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()
    
    def get_actions_by_app(self, app_name: str, limit: int = 50) -> List[ActionLogDB]:
        """Get actions for a specific application."""
        session = self.get_session()
        try:
            return session.query(ActionLogDB)\
                .filter(ActionLogDB.app_name == app_name)\
                .order_by(ActionLogDB.timestamp.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get statistics for the last N days.
        
        Args:
            days: Number of days to include in statistics
            
        Returns:
            Dictionary with statistics
        """
        session = self.get_session()
        try:
            since = datetime.now() - timedelta(days=days)
            
            actions = session.query(ActionLogDB)\
                .filter(ActionLogDB.timestamp >= since)\
                .all()
            
            if not actions:
                return {
                    "total_actions": 0,
                    "successful_actions": 0,
                    "failed_actions": 0,
                    "success_rate": 0.0,
                    "avg_execution_time_ms": 0.0,
                    "most_active_app": None,
                    "actions_by_app": {}
                }
            
            total = len(actions)
            successful = sum(1 for a in actions if a.success)
            failed = total - successful
            avg_time = sum(a.execution_time_ms for a in actions) / total
            
            # Count actions by app
            app_counts = {}
            for action in actions:
                app_counts[action.app_name] = app_counts.get(action.app_name, 0) + 1
            
            most_active = max(app_counts.items(), key=lambda x: x[1])[0] if app_counts else None
            
            return {
                "total_actions": total,
                "successful_actions": successful,
                "failed_actions": failed,
                "success_rate": (successful / total * 100) if total > 0 else 0.0,
                "avg_execution_time_ms": avg_time,
                "most_active_app": most_active,
                "actions_by_app": app_counts
            }
        
        finally:
            session.close()
    
    def cleanup_old_logs(self, days: int = 30) -> int:
        """
        Delete logs older than N days.
        
        Args:
            days: Keep logs from the last N days
            
        Returns:
            Number of deleted entries
        """
        session = self.get_session()
        try:
            cutoff = datetime.now() - timedelta(days=days)
            
            deleted = session.query(ActionLogDB)\
                .filter(ActionLogDB.timestamp < cutoff)\
                .delete()
            
            session.commit()
            logger.info(f"Deleted {deleted} old log entries")
            
            return deleted
        
        except Exception as e:
            logger.error(f"Error cleaning up old logs: {e}")
            session.rollback()
            return 0
        
        finally:
            session.close()


# Global database manager instance
db_manager = DatabaseManager()
