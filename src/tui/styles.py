"""CSS styles for the TUI application."""

MAIN_STYLES = """
Screen {
    align: center middle;
}

#mode-select {
    width: 90%;
    height: auto;
    border: solid green;
    padding: 1;
}

.directory-tree-container {
    width: 90%;
    height: 15;
    margin: 1;
    layout: horizontal;
    border: solid blue;
}

#file-select {
    width: 100%;
    height: 15;
    margin-left: 1;
}

#params-form {
    width: 90%;
    height: auto;
    border: solid red;
    margin-top: 1;
    padding: 1;
}

DirectoryTree {
    height: 15;
    border: solid green;
    scrollbar-size: 1 1;
}

.form-row {
    height: 3;
    margin: 1;
    layout: horizontal;
}

.form-label {
    width: 20%;
    content-align: right middle;
    padding-right: 1;
}

.form-input {
    width: 80%;
}

#submit-button {
    margin-top: 1;
}

*:focus {
    border: heavy yellow;
}

.results-container {
    width: 90%;
    height: 80%;
    border: solid blue;
    padding: 1;
}

#results-container {
    width: 100%;
    height: 80%;
    border: solid green;
    margin: 1;
    padding: 1;
    overflow-y: scroll;
}

.results-header {
    text-style: bold;
    content-align: center middle;
    width: 100%;
    height: 3;
    margin-bottom: 1;
}

.result-item {
    padding-left: 2;
    width: 100%;
}

#back-button {
    margin-top: 1;
    width: 100%;
}

.stream-container {
    width: 90%;
    height: 80%;
    border: solid blue;
    padding: 1;
}

#stream-log {
    width: 100%;
    height: 100%;
    border: solid green;
    margin: 1;
    padding: 1;
    overflow-y: scroll;
}

.stream-header {
    text-style: bold;
    content-align: center middle;
    width: 100%;
    height: 3;
    margin-bottom: 1;
}
"""