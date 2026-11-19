import argparse
from datetime import datetime
import json
import os
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
'''
Brief Note: The idea was created on my own , but I used AI (Gemini) to vibe code it and learn certain commands. This assihelper was created to help students work offline without internet and keep a reminder of what to be done. 



'''

DATA_FILE = "assignments.json"  # The json file where data is to be stored
COMPLETED_FILE = "completed.json"  # The json file for completed assignments
console = Console() #Calling out console

BANNER = r"""
   ___   _____ _____ ____ __ __ ____ __    ___   ____ ___ 
  / _ | / ___// ___//  _// // // __// /   / _ \ / __// _ \
 / __ | \__ \ \__ \ _/ / / _  // _/ / /__ / ___// _/ / , _/
/_/ |_|/___/ /___/ /___//_//_//___//____//_/   /___//_/|_| 
"""  #The banner


def load_data(filename=DATA_FILE):
  if not os.path.exists(filename):  # checks if the json file exists
    return []
  with open(filename, "r") as f: 
    try:
      return json.load(f) #Loads the data
    except json.JSONDecodeError:
      return []


def save_data(assignments, filename=DATA_FILE):
  with open(filename, "w") as f:  # updates the json file
    json.dump(assignments, f, indent=4)  #Dumps the data into the file


def calculate_priority(assignment):
  now = datetime.now() 
  due_str = assignment.get("due_date", now.strftime("%Y-%m-%d %H:%M")) #Getting the due date , default value is system time

  parsed_due = None
  for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"): #Applying both formats of time
    try:
      parsed_due = datetime.strptime(due_str, fmt) #Converting str due_time to datetime object for later comparison
      break
    except ValueError:
      continue

  if not parsed_due:
    parsed_due = now #giving parsed_due value of now datetime object if its still none

  # Precise time difference in days (can be fractional)
  diff = parsed_due - now   #Since now both are datetime objects it can be compared
  days_left = diff.total_seconds() / 86400.0 #Calculating days

  if days_left < 0: #Days left is less than zero , ie due time becomes overdue
    urgency = 50.0  # Overdue boost 
  else:
    urgency = 10.0 / (days_left + 1) #Less urgency with less value if more days are left

  importance = float(assignment.get("importance", 3)) #Importance value 
  hours = float(assignment.get("est_hours", 2))  #Estimated hours value

  score = (
      importance * 3.0   
  ) + (                          #Formula for calculating priority
      urgency * 15.0
  ) + (hours * 0.2)
  return min(round(score, 2),100), days_left, parsed_due #Returning the score , days left and parsed due but making sure score doesn't go beyond 100


def get_importance_stars(imp):
  return "★" * imp + "☆" * (5 - imp) #Adding stars


def get_urgency_bar(score):
  # Creates a visual ASCII bar representing the score intensity.
  filled = min(int(score // 10), 10) #filled bars
  empty = 10 - filled   #unfilled bars
  return "█" * filled + "░" * empty  #Returning the ascii value


def show_header():
  console.print(
      Panel(
          Text(BANNER.strip("\n"), style="bold cyan", justify="center"),
          subtitle="[bold white]Smart CLI Assignment Prioritizer[/bold white]",
          border_style="bright_blue",
          box=box.DOUBLE,
      )
  )


def add_assignment(args):
  assignments = load_data(DATA_FILE)  #Loading data

  # Validate mandatory due date input
  parsed_due = None  
  for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
    try:
      parsed_due = datetime.strptime(args.due_date, fmt)
      break
    except ValueError:
      continue

  if not parsed_due:
    console.print(
        Panel(
            "[bold red]Error:[/bold red] Due date must be in"
            " [cyan]YYYY-MM-DD[/cyan] or [cyan]YYYY-MM-DD HH:MM[/cyan]"
            " format.",
            border_style="red",
        )
    )
    return

  formatted_due = parsed_due.strftime("%Y-%m-%d %H:%M")

  # Generates unique incremental ID
  next_id = max([a["id"] for a in assignments], default=0) + 1

  new_assignment = {
      "id": next_id,
      "title": args.title,
      "description": args.desc,
      "due_date": formatted_due,
      "est_hours": float(args.hours),
      "importance": int(args.importance),
  }

  assignments.append(new_assignment)
  save_data(assignments, DATA_FILE)

  console.print(
      Panel(
          f"[bold green]✓ Added Assignment:[/bold green] [white]{args.title}[/white]\n"
          f"[dim]Due: {formatted_due} | Est. Effort: {args.hours} hrs |"
          f" Importance: {get_importance_stars(args.importance)}[/dim]",
          border_style="green",
          title="Success",
      )
  )


def list_assignments(args):
  show_header()
  assignments = load_data(DATA_FILE) #Loads data

  if not assignments:
    console.print(
        Panel(
            "[yellow]No assignments in your queue![/yellow]\nUse"
            ' [bold cyan]python assihelper.py add "Title" -due YYYY-MM-DD -hrs'
            " 2 -imp 4[/bold cyan] to get started.",
            border_style="yellow",
            title="Queue Empty",
        )
    )
    return

  for a in assignments:
    score, days_left, parsed_due = calculate_priority(a)
    a["score"] = score
    a["days_left"] = days_left
    a["parsed_due"] = parsed_due

  # Sort highest priority first
  assignments.sort(key=lambda x: x["score"], reverse=True) #Sorting based on score

  table = Table(
      title="[bold white]📋 PRIORITIZED ASSIGNMENT QUEUE[/bold white]",
      box=box.ROUNDED,
      show_lines=True,
      header_style="bold magenta",
      border_style="bright_blue",
  ) #Creating table 

  table.add_column("ID", justify="center", style="bold cyan", width=4)
  table.add_column("Assignment & Description", style="bold white", width=34)
  table.add_column("Deadline", justify="center", width=18)
  table.add_column("Effort", justify="center", width=8)
  table.add_column("Importance", justify="center", width=12)
  table.add_column("Priority Score", justify="left", width=20)
  table.add_column("Status", justify="center", width=14)

  for a in assignments:
    days_left = a["days_left"]
    score = a["score"]

    # Color coding logic: Red (Urgent/Overdue), Yellow (Upcoming), Green (On Track)
    if days_left < 0:
      row_color = "bold red"
      status_badge = "[bold white on red] OVERDUE [/bold white on red]"
      due_str = f"{a['due_date']}\n({abs(round(days_left, 1))}d late)"
    elif days_left <= 2 or score > 70: 
      row_color = "red"
      status_badge = "[bold red]● URGENT[/bold red]"
      hours_left = round(days_left * 24, 1)
      time_desc = (
          f"{round(days_left, 1)}d left"
          if days_left >= 1
          else f"{max(0, hours_left)}h left"
      )
      due_str = f"{a['due_date']}\n({time_desc})"
    elif days_left <= 6 or score > 40:
      row_color = "yellow"
      status_badge = "[bold yellow]▲ UPCOMING[/bold yellow]"
      due_str = f"{a['due_date']}\n({round(days_left, 1)}d left)"
    else:
      row_color = "green"
      status_badge = "[bold green]✔ ON TRACK[/bold green]"
      due_str = f"{a['due_date']}\n({round(days_left, 1)}d left)"

    title_and_desc = (
        f"[{row_color}]{a['title']}[/{row_color}]\n[dim]{a['description']}[/dim]"
    )
    stars = f"[{row_color}]{get_importance_stars(a['importance'])}[/{row_color}]"
    score_visual = (
        f"[{row_color}]{score:>5.1f} {get_urgency_bar(score)}[/{row_color}]"
    )

    table.add_row(
        str(a["id"]),
        title_and_desc,
        f"[{row_color}]{due_str}[/{row_color}]",
        f"{a['est_hours']}h",
        stars,
        score_visual,
        status_badge,
    )

  console.print(table)
  console.print(
      "[dim]Legend:[/dim] [bold red]■ Red = Critical/Urgent[/bold red] | "
      "[bold yellow]■ Yellow = Medium/Upcoming[/bold yellow] | "
      "[bold green]■ Green = Low/Safe[/bold green]\n"
  )


def complete_assignment(args):
  assignments = load_data(DATA_FILE)
  completed = load_data(COMPLETED_FILE) #Also loads completed file

  # Find the assignment to complete using args.id
  target = next((a for a in assignments if a["id"] == args.id), None)

  if not target:
    console.print(
        Panel(
            f"[bold red]Assignment ID #{args.id} not found.[/bold red]",
            border_style="red",
        )
    )
    return

  # Remove from active assignments
  assignments = [a for a in assignments if a["id"] != args.id]

  # Set importance to 100% (5 out of 5 stars max importance) when archiving to completed history
  target["importance"] = 5

  # Determine completion time: use argument if provided, otherwise current system time
  if args.due_date:
    parsed_date = None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
      try:
        parsed_date = datetime.strptime(args.due_date, fmt)
        break
      except ValueError:
        continue

    if not parsed_date:
      console.print(
          Panel(
              "[bold red]Error:[/bold red] Completion date must be in"
              " [cyan]YYYY-MM-DD[/cyan] or [cyan]YYYY-MM-DD HH:MM[/cyan]"
              " format.",
              border_style="red",
          )
      )
      return
    target["completed_date"] = parsed_date.strftime("%Y-%m-%d %H:%M")
  else:
    target["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")

  # Generate unique ID for completed log
  next_comp_id = max([c["id"] for c in completed], default=0) + 1
  target["id"] = next_comp_id

  completed.append(target)

  # Save both files
  save_data(assignments, DATA_FILE)
  save_data(completed, COMPLETED_FILE)

  console.print(
      Panel(
          f"[bold green]✓ Assignment #{args.id} marked as complete on"
          f" {target['completed_date']}, set to 100% importance (★★★★★), and"
          " archived![/bold green]",
          border_style="green",
      )
  )


def delete_assignment(args):
  assignments = load_data(DATA_FILE)
  filtered = [a for a in assignments if a["id"] != args.id]

  if len(filtered) == len(assignments):
    console.print(
        Panel(
            f"[bold red]Assignment ID #{args.id} not found.[/bold red]",
            border_style="red",
        )
    )
  else:
    save_data(filtered, DATA_FILE)
    console.print(
        Panel(
            f"[bold red]✗ Assignment #{args.id} permanently deleted from"
            " queue![/bold red]",
            border_style="red",
        )
    )


def list_completed(args):
  completed = load_data(COMPLETED_FILE)

  if not completed:
    console.print(
        Panel(
            "[yellow]No completed assignments archived yet![/yellow]",
            border_style="yellow",
            title="History Empty",
        )
    )
    return

  table = Table(
      title=(
          "[bold white]🏆 COMPLETED ASSIGNMENTS HISTORY (100% Importance)"
          "[/bold white]"
      ),
      box=box.ROUNDED,
      show_lines=True,
      header_style="bold green",
      border_style="green",
  )

  table.add_column("ID", justify="center", style="bold cyan", width=4)
  table.add_column("Assignment & Description", style="bold white", width=34)
  table.add_column("Original Due", justify="center", width=18)
  table.add_column("Effort", justify="center", width=8)
  table.add_column("Importance", justify="center", width=12)
  table.add_column("Completed On", justify="center", width=18)

  for c in completed:
    title_and_desc = f"[green]{c['title']}[/green]\n[dim]{c['description']}[/dim]"
    stars = f"[green]{get_importance_stars(c['importance'])}[/green]"

    table.add_row(
        str(c["id"]),
        title_and_desc,
        c["due_date"],
        f"{c['est_hours']}h",
        stars,
        c.get("completed_date", "N/A"),
    )

  console.print(table)


def main():
  parser = argparse.ArgumentParser(
      description="assihelper: Smart CLI Assignment Tracker"
  )
  subparsers = parser.add_subparsers(dest="command", help="Available commands")

  # Add command (mandatory -due / --due-date argument restored)
  parser_add = subparsers.add_parser("add", help="Add a new assignment")
  parser_add.add_argument("title", type=str, help="Assignment title")
  parser_add.add_argument(
      "-d",
      "--desc",
      type=str,
      default="No description provided",
      help="Short description",
  )
  parser_add.add_argument(
      "-due",
      "--due-date",
      type=str,
      required=True,
      help="Deadline (YYYY-MM-DD or YYYY-MM-DD HH:MM)",
  )
  parser_add.add_argument(
      "-hrs", "--hours", type=float, required=True, help="Estimated hours"
  )
  parser_add.add_argument(
      "-imp",
      "--importance",
      type=int,
      choices=[1, 2, 3, 4, 5],
      required=True,
      help="Importance (1-5)",
  )
  parser_add.set_defaults(func=add_assignment)

  # List command
  parser_list = subparsers.add_parser(
      "list", help="Display sorted priority table"
  )
  parser_list.set_defaults(func=list_assignments)

  # Done command (-id required, optional -due flag for custom completion time)
  parser_done = subparsers.add_parser(
      "done", help="Complete and archive an assignment"
  )
  parser_done.add_argument(
      "-id",
      "--id",
      type=int,
      required=True,
      help="Assignment ID number to complete",
  )
  parser_done.add_argument(
      "-due",
      "--due-date",
      type=str,
      default=None,
      help="Optional completion date/time (YYYY-MM-DD or YYYY-MM-DD HH:MM). Defaults to current system time.",
  )
  parser_done.set_defaults(func=complete_assignment)

  # Delete command
  parser_delete = subparsers.add_parser(
      "delete", help="Permanently delete an assignment"
  )
  parser_delete.add_argument(
      "-id", "--id", type=int, required=True, help="Assignment ID to delete"
  )
  parser_delete.set_defaults(func=delete_assignment)

  # History command
  parser_history = subparsers.add_parser(
      "history", help="Display completed assignments table"
  )
  parser_history.set_defaults(func=list_completed)

  args = parser.parse_args()
  if hasattr(args, "func"):
    args.func(args)
  else:
    list_assignments(args)


if __name__ == "__main__":
  main()