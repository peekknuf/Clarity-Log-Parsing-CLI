"""Results screen for displaying connection results."""

from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Header, Footer, Button, Static
from textual.screen import Screen

class ResultsScreen(Screen):
    """Screen for displaying connection results."""

    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, results: list[str], host: str):
        super().__init__()
        self.results = results
        self.host = host

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static(f"Hosts connected to {self.host}:", classes="results-header"),
            ScrollableContainer(
                *[Static(host, classes="result-item") for host in sorted(self.results)],
                id="results-container"
            ) if self.results else Static("No hosts connected in the specified time range."),
            Button("Back to Form", variant="primary", id="back-button"),
            classes="results-container"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-button":
            self.app.pop_screen()