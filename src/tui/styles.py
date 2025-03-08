"""CSS styles for the TUI application."""

# Gruvbox Dark Theme Colors
COLORS = {
    "bg": "#282828",
    "fg": "#ebdbb2",
    "gray": "#928374",
    "red": "#cc241d",
    "green": "#98971a",
    "yellow": "#d79921",
    "blue": "#458588",
    "purple": "#b16286",
    "aqua": "#689d6a",
    "orange": "#d65d0e",
}

MAIN_STYLES = f"""
Screen {{
    background: {COLORS["bg"]};
    color: {COLORS["fg"]};
}}

#mode-select {{
    width: 90%;
    height: auto;
    border: solid {COLORS["green"]};
    padding: 1;
}}

RadioButton {{
    background: {COLORS["bg"]};
    color: {COLORS["fg"]};
}}

RadioButton:focus {{
    background: {COLORS["green"]};
    color: {COLORS["bg"]};
}}

.directory-tree-container {{
    width: 90%;
    height: 15;
    margin: 1;
    layout: horizontal;
    border: solid {COLORS["blue"]};
}}

#file-select {{
    width: 100%;
    height: 15;
    margin-left: 1;
    background: {COLORS["bg"]};
    color: {COLORS["fg"]};
}}

DirectoryTree:focus {{
    border: double {COLORS["yellow"]};
}}

#params-form {{
    width: 90%;
    height: auto;
    border: solid {COLORS["red"]};
    margin-top: 1;
    padding: 1;
}}

.form-row {{
    height: 3;
    margin: 1;
    layout: horizontal;
}}

.form-label {{
    width: 20%;
    content-align: right middle;
    padding-right: 1;
    color: {COLORS["yellow"]};
}}

Input {{
    background: {COLORS["bg"]};
    color: {COLORS["fg"]};
}}

Input:focus {{
    border: double {COLORS["yellow"]};
}}

Button {{
    background: {COLORS["green"]};
    color: {COLORS["bg"]};
}}

Button:focus {{
    background: {COLORS["yellow"]};
    color: {COLORS["bg"]};
}}

.results-container {{
    width: 90%;
    height: 80%;
    border: solid {COLORS["blue"]};
    padding: 1;
    background: {COLORS["bg"]};
}}

#results-container {{
    width: 100%;
    height: 80%;
    border: solid {COLORS["green"]};
    margin: 1;
    padding: 1;
    overflow-y: scroll;
    background: {COLORS["bg"]};
}}

.results-header {{
    text-style: bold;
    content-align: center middle;
    width: 100%;
    height: 3;
    margin-bottom: 1;
    color: {COLORS["yellow"]};
}}

.result-item {{
    padding-left: 2;
    width: 100%;
    color: {COLORS["fg"]};
}}

#back-button {{
    margin-top: 1;
    width: 100%;
}}

.stream-container {{
    width: 90%;
    height: 80%;
    border: solid {COLORS["blue"]};
    padding: 1;
    background: {COLORS["bg"]};
}}

#stream-log {{
    width: 100%;
    height: 100%;
    border: solid {COLORS["green"]};
    margin: 1;
    padding: 1;
    overflow-y: scroll;
    background: {COLORS["bg"]};
    color: {COLORS["fg"]};
}}

.stream-header {{
    text-style: bold;
    content-align: center middle;
    width: 100%;
    height: 3;
    margin-bottom: 1;
    color: {COLORS["yellow"]};
}}

Header {{
    background: {COLORS["bg"]};
    color: {COLORS["aqua"]};
}}

Footer {{
    background: {COLORS["bg"]};
    color: {COLORS["gray"]};
}}
"""