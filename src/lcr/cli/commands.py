"""CLI commands for LeetCode Repetition (LCR) tool."""

import typer
from typing import Optional
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich import box

from lcr.database import get_db, ProblemRepository, ReviewRepository, SessionRepository
from lcr.utils import default_scheduler, DelayCascade, DateTimeHelper

app = typer.Typer(help="LeetCode Repetition (LCR) - Spaced Repetition for Problem Reviews")
console = Console()


@app.command()
def add(
    problem_id: str = typer.Argument(..., help="LeetCode problem ID"),
    times: int = typer.Option(4, "--times", "-t", help="Number of review intervals (default: 4)"),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Specific review date (yyyy-MM-dd)"),
    title: Optional[str] = typer.Option(None, "--title", help="Problem title (optional)"),
):
    """Register a problem for review with spaced repetition schedule."""
    try:
        # Initialize database
        db = get_db()
        
        # Get or create problem
        problem = ProblemRepository.get_or_create(problem_id, title)
        
        if date:
            # Single review on specific date
            try:
                review_date = DateTimeHelper.parse_date(date)
                scheduled_datetime = DateTimeHelper.combine_date_time(review_date)
            except ValueError as e:
                console.print(f"[red]Error:[/red] Invalid date format. {e}")
                raise typer.Exit(1)
            
            # Create chain ID first
            chain_id = f"{problem_id}-{datetime.now().timestamp()}"
            
            # Check for duplicate
            if ReviewRepository.check_duplicate(problem, scheduled_datetime, chain_id):
                console.print(f"[yellow]Review for problem {problem_id} on {date} already exists.[/yellow]")
                return
            
            # Create single review
            ReviewRepository.create(problem, chain_id, scheduled_datetime, iteration_number=0)
            
            console.print(f"[green]✓[/green] Added review for problem [bold]{problem_id}[/bold] on [bold]{date}[/bold]")
        else:
            # Generate spaced repetition schedule
            now = DateTimeHelper.now_utc()
            chain_id = f"{problem_id}-{now.timestamp()}"
            
            # Generate schedule with randomization
            schedule = default_scheduler.generate_schedule(now, num_reviews=times, apply_randomization=True)
            
            # Create reviews, checking for duplicates
            created_count = 0
            skipped_count = 0
            
            for iteration, scheduled_date in enumerate(schedule):
                if not ReviewRepository.check_duplicate(problem, scheduled_date, chain_id):
                    ReviewRepository.create(problem, chain_id, scheduled_date, iteration_number=iteration + 1)
                    created_count += 1
                else:
                    skipped_count += 1
            
            # Display results
            if created_count > 0:
                console.print(f"[green]✓[/green] Created [bold]{created_count}[/bold] reviews for problem [bold]{problem_id}[/bold]")
                
                # Show schedule
                table = Table(title=f"Review Schedule for {problem_id}", box=box.ROUNDED)
                table.add_column("Iteration", style="cyan")
                table.add_column("Scheduled Date", style="green")
                table.add_column("Days from Now", style="yellow")
                
                for iteration, scheduled_date in enumerate(schedule[:created_count], 1):
                    days_diff = (scheduled_date - now).days
                    date_str = DateTimeHelper.format_date(scheduled_date)
                    table.add_row(str(iteration), date_str, f"+{days_diff}")
                
                console.print(table)
            
            if skipped_count > 0:
                console.print(f"[yellow]⚠[/yellow] Skipped {skipped_count} duplicate reviews")
                
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def checkin(
    problem_id: str = typer.Argument(..., help="LeetCode problem ID"),
):
    """Mark a review as completed and apply delay cascade if needed."""
    try:
        db = get_db()
        
        # Get problem
        problem = ProblemRepository.get_by_id(problem_id)
        if not problem:
            console.print(f"[red]Error:[/red] Problem {problem_id} not found. Use 'lcr add' first.")
            raise typer.Exit(1)
        
        # Get earliest pending review
        review = ReviewRepository.get_earliest_pending_for_problem(problem)
        
        if not review:
            # Orphan check-in - create standalone completed log
            console.print(f"[yellow]⚠[/yellow] No pending review found for {problem_id}.")
            console.print("[yellow]Creating standalone completion log...[/yellow]")
            
            now = DateTimeHelper.now_utc()
            chain_id = f"{problem_id}-orphan-{now.timestamp()}"
            orphan_review = ReviewRepository.create(problem, chain_id, now, iteration_number=0)
            orphan_review.complete(now)
            
            console.print(f"[green]✓[/green] Logged completion for problem [bold]{problem_id}[/bold]")
            return
        
        # Complete the review
        completion_time = DateTimeHelper.now_utc()
        review.complete(completion_time)
        
        # Calculate delay
        delay_days = (completion_time - review.scheduled_date).days
        
        # Apply cascade if delayed
        if delay_days > 0:
            updated_count = DelayCascade.apply_cascade(review, completion_time)
            
            console.print(f"[green]✓[/green] Completed review for [bold]{problem_id}[/bold]")
            console.print(f"[yellow]⚠[/yellow] Review was {delay_days} day(s) late")
            
            if updated_count > 0:
                console.print(f"[blue]ℹ[/blue] Updated {updated_count} future review(s) by +{delay_days} day(s)")
        else:
            console.print(f"[green]✓[/green] Completed review for [bold]{problem_id}[/bold] on time!")
        
        # Show next review if exists
        next_review = ReviewRepository.get_earliest_pending_for_problem(problem)
        if next_review:
            next_date = DateTimeHelper.format_date(next_review.scheduled_date)
            days_until = (next_review.scheduled_date - DateTimeHelper.now_utc()).days
            console.print(f"[blue]→[/blue] Next review: [bold]{next_date}[/bold] (in {days_until} days)")
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def list():
    """Display problems currently due for review."""
    try:
        db = get_db()
        
        # Get due reviews
        now = DateTimeHelper.now_utc()
        due_reviews = ReviewRepository.get_due_reviews(now)
        
        if not due_reviews:
            console.print("[green]✓[/green] No reviews due today! Great job! 🎉")
            return
        
        # Create table
        table = Table(title="Due Reviews", box=box.ROUNDED)
        table.add_column("Problem ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="white")
        table.add_column("Scheduled", style="yellow")
        table.add_column("Delay", style="red")
        table.add_column("Iteration", style="magenta")
        
        for review in due_reviews:
            delay_days = review.delay_days()
            delay_str = f"{delay_days} day(s)" if delay_days > 0 else "On time"
            delay_style = "red" if delay_days > 0 else "green"
            
            scheduled_str = DateTimeHelper.format_date(review.scheduled_date)
            
            table.add_row(
                review.problem.problem_id,
                review.problem.title or "N/A",
                scheduled_str,
                f"[{delay_style}]{delay_str}[/{delay_style}]",
                f"#{review.iteration_number}"
            )
        
        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {len(due_reviews)} review(s) due")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def review(
    days: int = typer.Option(7, "--days", "-d", help="Number of days to show (default: 7)"),
):
    """Show calendar view of past and future review activities."""
    try:
        db = get_db()
        
        now = DateTimeHelper.now_utc()
        start_date = now - timedelta(days=days)
        end_date = now + timedelta(days=days)
        
        # Get completed reviews in range
        completed_reviews = ReviewRepository.get_completed_reviews(start_date, now)
        
        # Get pending reviews in range  
        from lcr.models import Review, Problem
        pending_reviews = [r for r in Review.select()
            .join(Problem)
            .where(
                (Review.scheduled_date >= now) &
                (Review.scheduled_date <= end_date) &
                (Review.status == "pending")
            )
            .order_by(Review.scheduled_date)]
        
        # Past reviews table
        if completed_reviews:
            past_table = Table(title="Past Reviews (Completed)", box=box.ROUNDED)
            past_table.add_column("Problem ID", style="cyan")
            past_table.add_column("Scheduled", style="yellow")
            past_table.add_column("Completed", style="green")
            past_table.add_column("Status", style="white")
            
            for review in completed_reviews:
                scheduled_str = DateTimeHelper.format_date(review.scheduled_date)
                completed_str = DateTimeHelper.format_date(review.actual_completion_date)
                
                delay = review.delay_days()
                if delay == 0:
                    status = "[green]✓ On Time[/green]"
                else:
                    status = f"[red]⚠ Delayed {delay} day(s)[/red]"
                
                past_table.add_row(
                    review.problem.problem_id,
                    scheduled_str,
                    completed_str,
                    status
                )
            
            console.print(past_table)
            console.print()
        
        # Future reviews table
        if pending_reviews:
            future_table = Table(title="Future Reviews (Scheduled)", box=box.ROUNDED)
            future_table.add_column("Problem ID", style="cyan")
            future_table.add_column("Scheduled Date", style="yellow")
            future_table.add_column("Days Until", style="magenta")
            future_table.add_column("Iteration", style="blue")
            
            for review in pending_reviews:
                scheduled_str = DateTimeHelper.format_date(review.scheduled_date)
                days_until = (review.scheduled_date - now).days
                
                future_table.add_row(
                    review.problem.problem_id,
                    scheduled_str,
                    f"+{days_until}",
                    f"#{review.iteration_number}"
                )
            
            console.print(future_table)
        
        if not completed_reviews and not pending_reviews:
            console.print("[yellow]No reviews found in the specified time range.[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def start(
    problem_id: str = typer.Argument(..., help="LeetCode problem ID"),
):
    """Start a timer session for a problem."""
    try:
        db = get_db()
        
        # Get or create problem
        problem = ProblemRepository.get_or_create(problem_id)
        
        # Check for existing active session
        active_session = SessionRepository.get_active_session_for_problem(problem)
        if active_session:
            start_time_str = DateTimeHelper.format_datetime(active_session.start_time, use_local=True)
            console.print(f"[yellow]⚠[/yellow] Session already active for {problem_id}")
            console.print(f"[yellow]Started at:[/yellow] {start_time_str}")
            return
        
        # Create new session
        session = SessionRepository.create(problem)
        start_time_str = DateTimeHelper.format_datetime(session.start_time, use_local=True)
        
        console.print(f"[green]✓[/green] Timer started for problem [bold]{problem_id}[/bold]")
        console.print(f"[blue]Started at:[/blue] {start_time_str}")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def end(
    problem_id: str = typer.Argument(..., help="LeetCode problem ID"),
):
    """End timer session and automatically check in the review."""
    try:
        db = get_db()
        
        # Get problem
        problem = ProblemRepository.get_by_id(problem_id)
        if not problem:
            console.print(f"[red]Error:[/red] Problem {problem_id} not found.")
            raise typer.Exit(1)
        
        # Get active session
        session = SessionRepository.get_active_session_for_problem(problem)
        if not session:
            console.print(f"[yellow]⚠[/yellow] No active session found for {problem_id}")
            return
        
        # End session
        session.end()
        duration_str = session.format_duration()
        
        console.print(f"[green]✓[/green] Timer stopped for problem [bold]{problem_id}[/bold]")
        console.print(f"[blue]Duration:[/blue] {duration_str}")
        
        # Auto check-in
        console.print("\n[blue]→[/blue] Auto-checking in...")
        
        # Trigger checkin logic inline
        review = ReviewRepository.get_earliest_pending_for_problem(problem)
        
        if not review:
            # Orphan check-in
            now = DateTimeHelper.now_utc()
            chain_id = f"{problem_id}-orphan-{now.timestamp()}"
            orphan_review = ReviewRepository.create(problem, chain_id, now, iteration_number=0)
            orphan_review.complete(now)
            console.print(f"[green]✓[/green] Logged completion (no pending review)")
        else:
            completion_time = DateTimeHelper.now_utc()
            review.complete(completion_time)
            
            delay_days = (completion_time - review.scheduled_date).days
            
            if delay_days > 0:
                updated_count = DelayCascade.apply_cascade(review, completion_time)
                console.print(f"[green]✓[/green] Review completed ({delay_days} day(s) late)")
                if updated_count > 0:
                    console.print(f"[blue]ℹ[/blue] Updated {updated_count} future review(s)")
            else:
                console.print(f"[green]✓[/green] Review completed on time!")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
