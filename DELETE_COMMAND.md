# LCR Delete Command Documentation

## Overview

The `lcr delete` command removes pending reviews for a specific problem, allowing you to clean up your review schedule or cancel future reviews you no longer need.

---

## Basic Usage

```bash
lcr delete <problem_id>
```

### Examples

```bash
# Delete pending reviews for problem 100
lcr delete 100

# Delete with formatted input
lcr delete "215. Kth Largest Element"

# Delete with difficulty tag
lcr delete "(M) 787"
```

---

## Options

### `--all` / `-a` Flag

Delete ALL reviews (both pending and completed) for a problem.

```bash
# Delete only pending reviews (default)
lcr delete 100

# Delete ALL reviews including completed ones
lcr delete 100 --all
lcr delete 100 -a
```

---

## How It Works

### 1. Shows Preview
The command displays all reviews that will be deleted:

```bash
$ lcr delete 100

Found 4 pending review(s) for problem 100:
╭────────────┬─────────┬───────────╮
│ Scheduled  │ Status  │ Iteration │
├────────────┼─────────┼───────────┤
│ 2025-12-10 │ Pending │ #1        │
│ 2025-12-17 │ Pending │ #2        │
│ 2026-01-06 │ Pending │ #3        │
│ 2026-02-09 │ Pending │ #4        │
╰────────────┴─────────┴───────────╯
```

### 2. Asks for Confirmation
You must confirm the deletion:

```
Delete 4 review(s)? [y/N]:
```

- Press `y` or `Y` to confirm
- Press `n`, `N`, or Enter to cancel

### 3. Deletes Reviews
Upon confirmation:

```
✓ Deleted 4 review(s) for problem 100
ℹ Problem 100 has no remaining reviews.
```

---

## Use Cases

### 1. Cancel Future Reviews

**Scenario**: You've mastered a problem and don't need more reviews

```bash
$ lcr delete 215
# Removes all pending reviews, keeps completion history
```

### 2. Clean Up Mistakes

**Scenario**: Added wrong problem or too many reviews

```bash
$ lcr delete 999
# Remove the incorrect problem's reviews
```

### 3. Reset Problem Completely

**Scenario**: Want to start fresh with a problem

```bash
$ lcr delete 42 --all
# Removes everything, then can re-add:
$ lcr add 42
```

### 4. Manage Overload

**Scenario**: Too many reviews scheduled

```bash
# Check your schedule
$ lcr review

# Delete problems you don't need
$ lcr delete 100
$ lcr delete 200
$ lcr delete 300
```

---

## Behavior Details

### Pending vs Completed Reviews

**Default (no `--all` flag):**
- Deletes ONLY pending (future) reviews
- Keeps completed reviews for history
- Preserves your learning record

**With `--all` flag:**
- Deletes ALL reviews (pending AND completed)
- Removes entire review history
- Problem entry remains in database

### Confirmation Required

The command ALWAYS asks for confirmation before deleting. This prevents accidental data loss.

To cancel:
- Press `n` or `N`
- Press Enter without input
- Press Ctrl+C

### Empty Results

If no reviews exist:

```bash
$ lcr delete 999
No pending reviews found for problem 999.
Tip: Use --all flag to delete completed reviews too.
```

With `--all` flag:
```bash
$ lcr delete 999 --all
No reviews found for problem 999.
```

---

## Examples

### Example 1: Standard Deletion

```bash
$ lcr add 215
✓ Created 4 reviews for problem 215

$ lcr delete 215
Found 4 pending review(s) for problem 215:
╭────────────┬─────────┬───────────╮
│ Scheduled  │ Status  │ Iteration │
├────────────┼─────────┼───────────┤
│ 2025-12-10 │ Pending │ #1        │
│ 2025-12-17 │ Pending │ #2        │
│ 2026-01-06 │ Pending │ #3        │
│ 2026-02-09 │ Pending │ #4        │
╰────────────┴─────────┴───────────╯

Delete 4 review(s)? [y/N]: y
✓ Deleted 4 review(s) for problem 215
ℹ Problem 215 has no remaining reviews.
```

### Example 2: Delete After Completion

```bash
# Add and complete first review
$ lcr add 100
$ lcr checkin 100

# Now has 1 completed, 3 pending
$ lcr delete 100

Found 3 pending review(s) for problem 100:
╭────────────┬─────────┬───────────╮
│ Scheduled  │ Status  │ Iteration │
├────────────┼─────────┼───────────┤
│ 2025-12-17 │ Pending │ #2        │
│ 2026-01-06 │ Pending │ #3        │
│ 2026-02-09 │ Pending │ #4        │
╰────────────┴─────────┴───────────╯

Delete 3 review(s)? [y/N]: y
✓ Deleted 3 review(s) for problem 100
# Completed review remains in history
```

### Example 3: Delete All Reviews

```bash
$ lcr delete 100 --all

Found 4 all review(s) for problem 100:
╭────────────┬───────────┬───────────╮
│ Scheduled  │ Status    │ Iteration │
├────────────┼───────────┼───────────┤
│ 2025-12-09 │ Completed │ #1        │
│ 2025-12-17 │ Pending   │ #2        │
│ 2026-01-06 │ Pending   │ #3        │
│ 2026-02-09 │ Pending   │ #4        │
╰────────────┴───────────┴───────────╯

Delete 4 review(s)? [y/N]: y
✓ Deleted 4 review(s) for problem 100
ℹ Problem 100 has no remaining reviews.
```

### Example 4: Cancel Deletion

```bash
$ lcr delete 215

Found 4 pending review(s) for problem 215:
[table shown]

Delete 4 review(s)? [y/N]: n
Deletion cancelled.

# Reviews remain intact
$ lcr list
[215 still has pending reviews]
```

---

## Comparison with Other Commands

### vs `lcr checkin`
- **checkin**: Marks review as completed (normal workflow)
- **delete**: Removes review without completing (cancel/cleanup)

### vs Database Reset
- **delete**: Removes reviews for ONE problem
- **rm ~/.lcr/lcr.db**: Removes EVERYTHING (see DATABASE_MANAGEMENT.md)

---

## Tips & Best Practices

### 1. Review Before Deleting
Always check `lcr review` or `lcr list` first to see what you're deleting.

### 2. Keep Completed Reviews
Use default (no `--all`) to preserve your learning history while removing future reviews.

### 3. Confirmation is Your Friend
The confirmation prompt prevents accidents - don't rush through it.

### 4. Problem Still Exists
Deleting reviews doesn't delete the problem entry. You can re-add reviews later:
```bash
$ lcr delete 215
$ lcr add 215  # Creates new review schedule
```

### 5. Batch Deletion
For multiple problems, delete one at a time:
```bash
lcr delete 100
lcr delete 200
lcr delete 300
```

---

## Error Handling

### Problem Not Found

```bash
$ lcr delete 999
Error: Problem 999 not found.
```

**Solution**: Problem was never added. Use `lcr add` first.

### No Reviews to Delete

```bash
$ lcr delete 100
No pending reviews found for problem 100.
Tip: Use --all flag to delete completed reviews too.
```

**Solution**: All reviews already completed or deleted.

---

## Related Commands

- `lcr add` - Add new reviews for a problem
- `lcr checkin` - Complete a review (normal workflow)
- `lcr list` - See pending reviews
- `lcr review` - See all reviews (past and future)

---

## Command Reference

```bash
# Basic syntax
lcr delete <problem_id>

# With options
lcr delete <problem_id> [--all]

# Examples
lcr delete 215
lcr delete "215. Kth Largest Element"
lcr delete "(M) 787"
lcr delete 100 --all
lcr delete 100 -a
```

---

## Safety Features

✅ **Preview Before Delete**: Shows exactly what will be deleted  
✅ **Confirmation Required**: Cannot accidentally delete  
✅ **Clear Feedback**: Reports what was deleted  
✅ **Cancel Anytime**: Easy to abort operation  
✅ **Preserves History**: Default keeps completed reviews  

---

## Notes

- The command is designed to be safe with confirmation prompts
- Deletion is immediate and cannot be undone
- Consider using `lcr review` before deleting to see full context
- The `--all` flag is rarely needed unless you want to completely reset a problem
