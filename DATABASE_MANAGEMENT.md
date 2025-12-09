# LCR Database Management Guide

## Database Location

The LCR database is stored at:
```
~/.lcr/lcr.db
```

This is a SQLite database file that contains all your problems, reviews, and session data.

---

## Clearing All Data

### Option 1: Delete Database File (Recommended)

**Simplest and fastest method:**

```bash
rm -f ~/.lcr/lcr.db
```

The database will be automatically recreated fresh on the next LCR command.

**Example:**
```bash
$ rm -f ~/.lcr/lcr.db
$ lcr list
✓ No reviews due today! Great job! 🎉
```

### Option 2: Using SQLite Command Line

If you have `sqlite3` installed:

```bash
sqlite3 ~/.lcr/lcr.db "DROP TABLE IF EXISTS problems; DROP TABLE IF EXISTS reviews; DROP TABLE IF EXISTS sessions;"
```

### Option 3: Backup Then Delete

To keep a backup before clearing:

```bash
# Backup
cp ~/.lcr/lcr.db ~/.lcr/lcr.db.backup.$(date +%Y%m%d)

# Delete
rm ~/.lcr/lcr.db
```

**Restore from backup:**
```bash
cp ~/.lcr/lcr.db.backup.20251209 ~/.lcr/lcr.db
```

---

## Selective Data Deletion

### Clear Only Reviews (Keep Problems)

```bash
sqlite3 ~/.lcr/lcr.db "DELETE FROM reviews;"
```

### Clear Only Sessions

```bash
sqlite3 ~/.lcr/lcr.db "DELETE FROM sessions;"
```

### Clear Specific Problem

```bash
sqlite3 ~/.lcr/lcr.db "DELETE FROM reviews WHERE problem_id IN (SELECT id FROM problems WHERE problem_id='215');"
sqlite3 ~/.lcr/lcr.db "DELETE FROM problems WHERE problem_id='215';"
```

---

## Database Inspection

### View All Problems

```bash
sqlite3 ~/.lcr/lcr.db "SELECT * FROM problems;"
```

### View All Reviews

```bash
sqlite3 ~/.lcr/lcr.db "SELECT r.*, p.problem_id, p.title FROM reviews r JOIN problems p ON r.problem_id = p.id;"
```

### Count Records

```bash
sqlite3 ~/.lcr/lcr.db "SELECT 
  (SELECT COUNT(*) FROM problems) as problems,
  (SELECT COUNT(*) FROM reviews) as reviews,
  (SELECT COUNT(*) FROM sessions) as sessions;"
```

### View Schema

```bash
sqlite3 ~/.lcr/lcr.db ".schema"
```

---

## Export/Import Data

### Export to SQL

```bash
sqlite3 ~/.lcr/lcr.db .dump > lcr_backup.sql
```

### Import from SQL

```bash
sqlite3 ~/.lcr/lcr.db < lcr_backup.sql
```

### Export to CSV

```bash
sqlite3 -header -csv ~/.lcr/lcr.db "SELECT * FROM problems;" > problems.csv
sqlite3 -header -csv ~/.lcr/lcr.db "SELECT * FROM reviews;" > reviews.csv
```

---

## Database Schema

### Problems Table
```sql
CREATE TABLE problems (
    id INTEGER PRIMARY KEY,
    problem_id TEXT UNIQUE NOT NULL,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Reviews Table
```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    problem_id INTEGER NOT NULL,
    chain_id TEXT NOT NULL,
    scheduled_date TIMESTAMP NOT NULL,
    actual_completion_date TIMESTAMP,
    status TEXT DEFAULT 'pending',
    iteration_number INTEGER,
    FOREIGN KEY (problem_id) REFERENCES problems(id)
);
```

### Sessions Table
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    problem_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    FOREIGN KEY (problem_id) REFERENCES problems(id)
);
```

---

## Troubleshooting

### Database Locked Error

If you see "database is locked":

```bash
# Find processes using the database
lsof ~/.lcr/lcr.db

# Kill the process if needed
kill <PID>
```

### Corrupted Database

If database is corrupted:

```bash
# Try to repair
sqlite3 ~/.lcr/lcr.db "PRAGMA integrity_check;"

# If repair fails, delete and start fresh
rm ~/.lcr/lcr.db
```

### Permission Issues

If you can't access the database:

```bash
# Check permissions
ls -la ~/.lcr/

# Fix permissions
chmod 644 ~/.lcr/lcr.db
```

---

## Best Practices

### 1. Regular Backups

Create a backup before major operations:

```bash
# Weekly backup
cp ~/.lcr/lcr.db ~/.lcr/backups/lcr.$(date +%Y%m%d).db
```

### 2. Test Data

Use a separate database for testing:

```bash
# Set custom database location
export LCR_DB_PATH=~/test_lcr.db
lcr add 1
```

### 3. Data Export

Periodically export your data:

```bash
# Export all data
sqlite3 ~/.lcr/lcr.db .dump > ~/Documents/lcr_backup_$(date +%Y%m%d).sql
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Delete all data | `rm -f ~/.lcr/lcr.db` |
| Backup database | `cp ~/.lcr/lcr.db ~/.lcr/lcr.backup` |
| View all problems | `sqlite3 ~/.lcr/lcr.db "SELECT * FROM problems;"` |
| Count reviews | `sqlite3 ~/.lcr/lcr.db "SELECT COUNT(*) FROM reviews;"` |
| Export to SQL | `sqlite3 ~/.lcr/lcr.db .dump > backup.sql` |
| Check integrity | `sqlite3 ~/.lcr/lcr.db "PRAGMA integrity_check;"` |

---

## Notes

- The database is automatically created on first use
- All timestamps are stored in UTC format
- Foreign key constraints are enabled
- The database uses WAL (Write-Ahead Logging) mode for better concurrency

---

## Support

For issues with database management:
1. Check this guide first
2. Verify file permissions: `ls -la ~/.lcr/`
3. Test with fresh database: `rm ~/.lcr/lcr.db && lcr list`
4. Check SQLite version: `sqlite3 --version`
