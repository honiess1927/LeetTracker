# Software Requirement Specification: LeetCode Repetition (LCR) CLI

## 1. Introduction
**LCR** is a command-line interface (CLI) tool designed to help users track and schedule LeetCode problem reviews based on a spaced repetition algorithm (similar to Ebbinghaus forgetting curve). It manages review schedules, tracks actual execution, and adjusts future plans based on user latency.

## 2. Technology Stack
* **Language:** Python 3.9+
* **Interface:** CLI (Command Line Interface)
* **Storage:** Local SQLite database (preferred) or JSON flat file.
* **Recommended Libraries:** `Typer` (CLI), `Rich` (UI/Formatting), `Peewee` or `SQLAlchemy` (ORM).

## 3. Functional Requirements

### 3.1. Problem Registration (`lcr add`)
The system shall allow users to register a problem ID for review.

* **Parameters:**
    * `problem_input` (Required): A string representing the problem. Supports formats like:
        * Raw ID: `1`
        * Formatted: `(E) 1. Two Sum` or `1. Two Sum`
    * `--times, -t` (Optional): Integer $m$. Default is 4. Specifies the number of review intervals to generate.
    * `--date, -d` (Optional): Date string (`yyyy-MM-dd`). Specifies a one-off, non-recurring review for a specific date.
* **Logic:**
    * **Parsing:** The system must parse `problem_input` to extract a unique numerical `problem_id` (see Section 4.3).
    * **Storage:**
        * Store the extracted `problem_id` as the unique identifier for logic.
        * Store the full `problem_input` as the `display_title` for UI presentation.
    * **Upsert (Update/Insert):**
        * If `problem_id` "1" already exists, update its `display_title` to the new detailed string `(E) 1. Two Sum`.
        * If it doesn't exist, create a new problem entry.
    * **Default Intervals:** The base intervals are $[1, 7, 18, 35]$ days.
    * **Randomization:** Each calculated interval $I$ shall be subject to a randomization factor of $\pm 15\%$. $I_{final} = \text{round}(I \times (1 \pm \text{random}(0, 0.15)))$.
    * **Schedule Generation:**
        * If `--date` is provided: Schedule a single review on the specified date.
        * If `--times` is provided: Generate schedule using the first $m$ intervals from the default list (clamped if $m > 4$, unless extended logic is defined).
        * Base date for calculation is the current system timestamp (Registration Time).
    * **Deduplication:** If a generated review date matches an existing pending review for the same `problem_id`, the new request merges with the existing one (no duplicate entries for the same ID on the same day).

### 3.2. Check-in Mechanism (`lcr checkin`)
The system shall allow users to mark a review as completed.

* **Parameters:**
    * `problem_input` (Required).
* **Logic:**
    * Parse `problem_input` to get `problem_id`.
    * Find the **earliest pending** review for this `problem_id`.
    * **Mark as Completed:** Update the record with the `actual_completion_date`.
    * **Orphan Check-in:** If no pending review exists for this ID, create a standalone "completed" log entry without generating future schedules.
    * **Cascading Delay Trigger:** Upon check-in, if `actual_completion_date` > `scheduled_date`, calculate `delay_days`. All *future* pending reviews for this specific chain of the problem must be shifted forward by `delay_days`.

### 3.3. Task Listing (`lcr list`)
The system shall display problems currently due for review.

* **Logic:**
    * Filter reviews where `scheduled_date` $\le$ `today` AND `status` is `pending`.
    * Display columns: `Problem ID`, `Scheduled Date`, `Delay` (Days overdue), and `Review Iteration` (e.g., 2nd review).
    * Sort by `Scheduled Date` (ascending).

### 3.4. Progress Visualization (`lcr review`)
The system shall provide a calendar or timeline view of past and future activities.

* **Logic:**
    * **Past:** Show completed reviews. Indicate if they were "On Time" (Green) or "Delayed by X days" (Red/Yellow).
    * **Future:** Show upcoming scheduled reviews.
    * **Dynamic Adjustment:** Future dates shown in this view must calculate the projected dates including any accumulated delays from previous steps.
* **UI:** A matrix view or a grouped list by Date headers.

### 3.5. Timer Session (`lcr start` / `lcr end`)
The system shall track the duration of a problem-solving session.

* **Command:** `lcr start <problem_id>`
    * Stores a timestamp and sets the session status to "Active" for this ID.
    * Persists state to handle program exit/interruption.
* **Command:** `lcr end <problem_id>`
    * Retrieves the start timestamp.
    * Calculates `duration`.
    * Automatically triggers the logic of `lcr checkin <problem_id>`.
    * Updates the log with the `duration` data.

## 4. Data Logic & Algorithms

### 4.1. The Delay Cascade Algorithm
Given a sequence of reviews $R_1, R_2, ... R_n$:
If $R_i$ is scheduled for $D_{sched}$ but completed on $D_{actual}$:
1.  Calculate Shift: $\Delta = \max(0, D_{actual} - D_{sched})$.
2.  Update $R_{i+1} ... R_n$:
    $D_{sched}(R_{k}) = D_{sched}(R_{k}) + \Delta$ for all $k > i$.

### 4.2. Randomization Formula
For interval $I$ (e.g., 7 days):
$$I_{randomized} = \text{round}(I \times (1 + \text{uniform}(-0.15, 0.15)))$$
*Constraint:* $I_{randomized} \ge 1$ (Review cannot be same-day unless explicitly requested).

### 4.3. Input Parsing Algorithm
The system shall use Regular Expressions to extract the Problem ID from user input to ensure consistency.

* **Regex Pattern:** `^.*?(\d+)\..*$` (Looks for a number followed by a dot) OR simple integer matching if no dot is present.
* **Examples:**
    * Input: `(E) 1. Two Sum` -> ID: `1`, Title: `(E) 1. Two Sum`
    * Input: `215. Kth Largest Element` -> ID: `215`, Title: `215. Kth Largest Element`
    * Input: `42` -> ID: `42`, Title: `42` (or keep existing title if present in DB)

## 5. Non-Functional Requirements

1.  **Persistence:** Data must survive system restarts. SQLite is required.
2.  **Date Handling:** All dates should be stored in UTC or ISO-8601 format internally, but displayed in the user's local timezone.
3.  **Performance:** `lcr list` should return within 200ms for datasets < 10,000 records.
