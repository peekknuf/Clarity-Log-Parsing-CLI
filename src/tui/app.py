"""Main TUI application module."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import (
    Header,
    Footer,
    Button,
    RadioSet,
    RadioButton,
    Input,
    Label,
    DirectoryTree,
)
from textual.binding import Binding

from src.processing.batch_processor import process_batch
from src.tui.screens.results_screen import ResultsScreen
from src.tui.screens.stream_screen import StreamScreen
from src.utils.utils import parse_datetime_input
from src.tui.styles import MAIN_STYLES


class LogParserApp(App):
    """Main TUI application for log parsing."""

    CSS = MAIN_STYLES

    BINDINGS = [
        Binding("tab", "focus_next", "Focus Next", show=False),
        Binding("shift+tab", "focus_previous", "Focus Previous", show=False),
        Binding("enter", "submit", "Submit", show=True),
        Binding("ctrl+c", "quit", "Quit", show=True),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)

        yield Container(
            RadioSet(
                RadioButton("Stream Mode", value=True),
                RadioButton("Batch Mode"),
                id="mode-select",
            ),
            Container(
                Label("Log Directory:", classes="form-label"),
                DirectoryTree(".", id="file-select"),
                classes="directory-tree-container",
            ),
            Container(
                Container(
                    Label("Host:", classes="form-label"),
                    Input(
                        placeholder="Enter host to monitor",
                        id="host-input",
                        classes="form-input",
                    ),
                    classes="form-row",
                ),
                Container(
                    Label("Start Time:", classes="form-label"),
                    Input(
                        placeholder="YYYY-MM-DD HH:MM:SS",
                        id="start-time",
                        classes="form-input",
                    ),
                    classes="form-row",
                ),
                Container(
                    Label("End Time:", classes="form-label"),
                    Input(
                        placeholder="YYYY-MM-DD HH:MM:SS",
                        id="end-time",
                        classes="form-input",
                    ),
                    classes="form-row",
                ),
                Button("Submit", variant="primary", id="submit-button"),
                id="params-form",
            ),
        )

        yield Footer()

    def on_mount(self) -> None:
        # Focus the mode select when the app starts
        self.query_one("#mode-select").focus()

    def action_focus_next(self) -> None:
        # Define the focus order
        current = self.focused
        if current is None:
            self.query_one("#mode-select").focus()
        elif isinstance(current.parent, RadioSet):
            self.query_one("#file-select").focus()
        elif isinstance(current, DirectoryTree):
            self.query_one("#host-input").focus()
        elif current.id == "host-input":
            self.query_one("#start-time").focus()
        elif current.id == "start-time":
            self.query_one("#end-time").focus()
        elif current.id == "end-time":
            self.query_one("#submit-button").focus()
        elif current.id == "submit-button":
            self.query_one("#mode-select").focus()

    def action_focus_previous(self) -> None:
        # Define the reverse focus order
        current = self.focused
        if current is None:
            self.query_one("#submit-button").focus()
        elif isinstance(current.parent, RadioSet):
            self.query_one("#submit-button").focus()
        elif isinstance(current, DirectoryTree):
            self.query_one("#mode-select").focus()
        elif current.id == "host-input":
            self.query_one("#file-select").focus()
        elif current.id == "start-time":
            self.query_one("#host-input").focus()
        elif current.id == "end-time":
            self.query_one("#start-time").focus()
        elif current.id == "submit-button":
            self.query_one("#end-time").focus()

    def action_submit(self) -> None:
        """Handle form submission."""
        self.query_one("#submit-button").press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit-button":
            self.process_logs()

    def process_logs(self) -> None:
        """Process logs based on selected mode and parameters."""
        # Get form values
        mode_select = self.query_one("#mode-select")
        file_select = self.query_one("#file-select")
        host_input = self.query_one("#host-input")
        start_time = self.query_one("#start-time")
        end_time = self.query_one("#end-time")

        # Validate inputs
        if not file_select.cursor_node:
            self.notify("Please select a log directory", severity="error")
            return

        if not host_input.value:
            self.notify("Please enter a host to monitor", severity="error")
            return

        directory = str(file_select.cursor_node.data.path)
        host = host_input.value.strip()

        # Stream mode
        if mode_select.pressed_button.label == "Stream Mode":
            self.push_screen(StreamScreen(directory, host))
            return

        # Batch mode
        try:
            # Make time inputs optional
            start = parse_datetime_input(start_time.value) if start_time.value else None
            end = parse_datetime_input(end_time.value) if end_time.value else None

            # Only validate time range if both times are provided
            if start and end and start >= end:
                self.notify("Start time must be before end time", severity="error")
                return

            results = process_batch(directory, host, start, end)
            self.push_screen(ResultsScreen(results, host))

        except ValueError as e:
            self.notify(str(e), severity="error")


def run_tui():
    """Run the TUI application."""
    app = LogParserApp()
    app.run()
