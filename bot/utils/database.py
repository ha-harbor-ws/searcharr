"""
Searcharr
Sonarr & Radarr Telegram Bot
Database Utilities
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
import json
import os
import sqlite3
from threading import Lock

from bot.utils.log import set_up_logger

logger = set_up_logger("database")

DBPATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), "data")
DBFILE = "searcharr.db"
DBLOCK = Lock()


def dict_factory(cursor, row):
    """Factory function for row objects in SQLite.
    
    Creates a dictionary from a database row.
    
    Args:
        cursor: The database cursor
        row: The database row
        
    Returns:
        dict: A dictionary with column names as keys
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_connection():
    """Get a database connection and cursor.
    
    Returns:
        tuple: (connection, cursor)
    """
    # Connect to local DB and return tuple containing connection and cursor
    if not os.path.isdir(DBPATH):
        try:
            logger.debug(
                "The data directory does not exist. Attempting to create it..."
            )
            os.mkdir(DBPATH)
        except Exception as e:
            logger.error(f"Error creating data directory: {e}.")
            raise

    try:
        con = sqlite3.connect(os.path.join(DBPATH, DBFILE), timeout=30)
        con.execute("PRAGMA journal_mode = off;")
        con.row_factory = dict_factory
        cur = con.cursor()
        logger.debug(
            f"Database connection established [{os.path.join(DBPATH, DBFILE)}]."
        )
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise

    return (con, cur)


def _migrate_db_filename():
    """Rename data/db -> data/searcharr.db for anyone who ran PR #100 briefly."""
    old_path = os.path.join(DBPATH, "db")
    new_path = os.path.join(DBPATH, DBFILE)
    if os.path.exists(old_path) and not os.path.exists(new_path):
        os.rename(old_path, new_path)
        logger.info(f"Migrated database file from {old_path} to {new_path}")


def init_db():
    """Initialize the database schema."""
    _migrate_db_filename()
    con, cur = get_connection()
    queries = [
        """CREATE TABLE IF NOT EXISTS conversations (
            id text primary key,
            username text not null,
            type text,
            results text
        );""",
        """CREATE TABLE IF NOT EXISTS users (
            id integer primary key,
            username text not null,
            admin text,
            permissions text
        );""",
        """CREATE TABLE IF NOT EXISTS add_data (
            cid text,
            key text,
            value text,
            primary key (cid, key)
        );""",
        """CREATE TABLE IF NOT EXISTS ai_kv (
            key text primary key,
            value text not null
        );""",
        """CREATE TABLE IF NOT EXISTS ai_chat_prefs (
            chat_id integer primary key,
            group_mode text not null
        );""",
    ]
    for q in queries:
        logger.debug(f"Executing query: [{q}] with no args...")
        try:
            with DBLOCK:
                cur.execute(q)
        except sqlite3.Error as e:
            logger.error(f"Error executing database query [{q}]: {e}")
            raise

    con.commit()
    con.close()


def execute_query(query, args=None):
    """Execute a database query.
    
    Args:
        query (str): The SQL query
        args (tuple, optional): Query parameters. Defaults to None.
        
    Returns:
        list: Query results or None on error
    """
    if args is None:
        args = ()
        
    logger.debug(f"Executing query: [{query}] with args: [{args}]")
    try:
        con, cur = get_connection()
        with DBLOCK:
            r = cur.execute(query, args)
            results = r.fetchall()
            con.commit()
            con.close()
            return results
    except sqlite3.Error as e:
        logger.error(f"Error executing database query [{query}]: {e}")
        return None


def execute_insert(query, args):
    """Execute an insert query.
    
    Args:
        query (str): The SQL query
        args (tuple): Query parameters
        
    Returns:
        bool: True on success, False on error
    """
    logger.debug(f"Executing insert query: [{query}] with args: [{args}]")
    try:
        con, cur = get_connection()
        with DBLOCK:
            cur.execute(query, args)
            con.commit()
            con.close()
            return True
    except sqlite3.Error as e:
        logger.error(f"Error executing database insert query [{query}]: {e}")
        return False