from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.syntax import Syntax
from rich.layout import Layout
from rich import print as rprint

console = Console()

class JarvisUI:
    @staticmethod
    def print_markdown(text):
        md = Markdown(text)
        console.print(md)

    @staticmethod
    def display_response(role, content):
        title = "[bold cyan]J.A.R.V.I.S.[/bold cyan]" if role == "JARVIS" else "[bold green]USER[/bold green]"
        border_style = "cyan" if role == "JARVIS" else "green"
        
        # Check if content has code blocks
        if "```" in content:
            md = Markdown(content)
            panel = Panel(md, title=title, border_style=border_style, padding=(1, 2))
        else:
            panel = Panel(content, title=title, border_style=border_style, padding=(1, 2))
        
        console.print("\n")
        console.print(panel)

    @staticmethod
    def display_status(status_text, style="yellow"):
        console.print(f"[{style}]▶ {status_text}[/{style}]")

    @staticmethod
    def display_learning_log(topic, summary, code_count):
        table = Table(title="🎓 NEW KNOWLEDGE ACQUIRED", border_style="magenta")
        table.add_column("Topic", style="cyan")
        table.add_column("Insight", style="white")
        table.add_column("Code Blocks", style="green")
        
        table.add_row(topic, summary[:100] + "...", str(code_count))
        console.print(table)

    @staticmethod
    def display_evolution_step(step, detail):
        rprint(f"[bold magenta]🧬 [EVOLUTION][/bold magenta] [italic]{step}[/italic]: {detail}")

    @staticmethod
    def get_input(prompt_text):
        return console.input(prompt_text)

ui = JarvisUI()
