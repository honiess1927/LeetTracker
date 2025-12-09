# Database Schema Update - Separate Difficulty Storage

## Overview

Updated the `Problem` model to store difficulty as a separate field instead of parsing it from the title at display time. This improves data consistency, query performance, and display uniformity.

---

## Changes Made

### 1. Database Schema

**Before:**
```python
class Problem(BaseModel):
    problem_id = CharField(unique=True)
    title = CharField(null=True)  # Stored as "(E) 1. Two Sum"
    created_at = DateTimeField()
    updated_at = DateTimeField()
```

**After:**
```python
class Problem(BaseModel):
    problem_id = CharField(unique=True)
    title = CharField(null=True)  # Stored as "Two Sum" (clean)
    difficulty = CharField(null=True, max_length=1)  # "E", "M", "H"
    created_at = DateTimeField()
    updated_at = DateTimeField()
```

### 2. Repository Layer

Updated `ProblemRepository.get_or_create()` to:
- Parse input titles to extract difficulty and clean title
- Store difficulty as single letter: "E", "M", or "H"
- Store clean title without difficulty prefix or problem ID

```python
# Parses "(E) 1. Two Sum" into:
# - difficulty: "E"
# - title: "Two Sum"
```

### 3. Display Layer

Updated both `lcr list` and `lcr review` commands:
- Added separate "Diff" column showing difficulty with color
- Display clean titles without redundant information
- No runtime parsing needed (reads directly from database)

**Display Format:**
```
╭─────┬──────┬─────────────────────────┬────────────╮
│ ID  │ Diff │ Title                   │ Scheduled  │
├─────┼──────┼─────────────────────────┼────────────┤
│ 1   │ E    │ Two Sum                 │ 2025-12-10 │
│ 215 │ M    │ Kth Largest Element     │ 2025-12-10 │
│ 4   │ H    │ Median of Two Sorted... │ 2025-12-10 │
╰─────┴──────┴─────────────────────────┴────────────╯
```

### 4. Helper Methods

Added `TitleParser.difficulty_to_letter()`:
```python
def difficulty_to_letter(difficulty: Optional[str]) -> Optional[str]:
    """Convert difficulty name to letter.
    
    "Easy" -> "E"
    "Medium" -> "M"
    "Hard" -> "H"
    """
```

---

## Migration

### Simple Approach (Chosen)

**Clean database reset** - Delete and recreate:

1. Delete existing database:
   ```bash
   rm ~/.lcr/lcr.db
   ```

2. Re-add problems with clean data:
   ```bash
   lcr add "(E) 1. Two Sum"
   lcr add "(M) 215. Kth Largest Element"
   lcr add "(H) 4. Median of Two Sorted Arrays"
   ```

This approach was chosen because:
- Limited test data in database
- User confirmed clean reset was acceptable
- Simplest implementation
- No migration script complexity

---

## Benefits

### 1. **Performance**
- No runtime parsing needed
- Direct database field access
- Faster display rendering

### 2. **Data Consistency**
- Difficulty stored once at creation
- No chance of parsing errors at display time
- Uniform data format

### 3. **Query Capability**
- Can filter by difficulty in database queries
- Future features: "show all hard problems"
- Better analytics possibilities

### 4. **Display Consistency**
- Same format across all commands
- Clear separation of concerns
- Easier maintenance

### 5. **Cleaner UI**
- Separate difficulty column
- No redundant problem ID in title
- Color-coded difficulty for quick recognition

---

## Color Coding

Difficulty is displayed with colors for quick visual identification:

- **E** (Easy): Green
- **M** (Medium): Yellow  
- **H** (Hard): Red
- **-** (Unknown): Dimmed

---

## Input Handling

The system still accepts all input formats:

```bash
# All these work:
lcr add "1"                          # Just ID
lcr add "1. Two Sum"                 # ID + Title
lcr add "(E) 1. Two Sum"             # Full format
lcr add "(E) Two Sum"                # Difficulty + Title

# Difficulty extracted and stored separately:
# - difficulty field: "E"
# - title field: "Two Sum"
```

---

## Code Locations

### Modified Files:

1. **src/lcr/models/problem.py**
   - Added `difficulty` field to schema

2. **src/lcr/database/repository.py**
   - Updated `get_or_create()` to parse and store difficulty

3. **src/lcr/utils/title_parser.py**
   - Added `difficulty_to_letter()` method

4. **src/lcr/cli/commands.py**
   - Updated `list()` command display
   - Updated `review()` command display

---

## Testing

### Test Cases Verified:

✅ Add problem with full format: `(E) 1. Two Sum`  
✅ Add problem with medium difficulty: `(M) 215`  
✅ Add problem with hard difficulty: `(H) 4`  
✅ Display in list command shows separate Diff column  
✅ Display in review command shows separate Diff column  
✅ Clean titles without difficulty prefix  
✅ Color-coded difficulty display  

### Test Results:

```bash
$ lcr review

                           Future Reviews (Scheduled)
╭─────┬──────┬───────────────────────────┬────────────┬────────────┬───────────╮
│ ID  │ Diff │ Title                     │ Scheduled  │ Days Until │ Iteration │
├─────┼──────┼───────────────────────────┼────────────┼────────────┼───────────┤
│ 1   │ E    │ Two Sum                   │ 2025-12-10 │ +0         │ #1        │
│ 215 │ M    │ Kth Largest Element       │ 2025-12-10 │ +0         │ #1        │
│ 4   │ H    │ Median of Two Sorted...   │ 2025-12-10 │ +0         │ #1        │
╰─────┴──────┴───────────────────────────┴────────────┴────────────┴───────────╯
```

**Result:** ✅ Perfect! Clean display with separate difficulty column.

---

## Backward Compatibility

### Breaking Changes:

⚠️ **Database schema change** - Requires clean reset or migration

### Non-Breaking:

✅ Input formats remain the same  
✅ All commands work identically  
✅ Display improvements only  

---

## Future Enhancements

With difficulty stored separately, new features become possible:

1. **Filter by Difficulty**
   ```bash
   lcr list --difficulty hard
   lcr review --only-easy
   ```

2. **Statistics**
   ```bash
   lcr stats
   # Shows: 10 Easy, 5 Medium, 3 Hard
   ```

3. **Smart Scheduling**
   - Adjust intervals based on difficulty
   - Hard problems get more reviews

4. **Progress Tracking**
   - Track mastery by difficulty level
   - "You've mastered 8/10 hard problems"

---

## Notes

- Difficulty field is nullable for backward compatibility
- Problems without difficulty display as "-" (dimmed)
- Parsing happens once at creation time, not at display time
- Clean separation between storage and display logic

---

## Related Documentation

- [INPUT_PARSING_FEATURE.md](INPUT_PARSING_FEATURE.md) - Input parsing details
- [DATABASE_MANAGEMENT.md](DATABASE_MANAGEMENT.md) - Database operations
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration options
