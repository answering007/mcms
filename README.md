# mcms - minecraft message service

[![PyPI - Version](https://img.shields.io/pypi/v/mcms.svg)](https://pypi.org/project/mcms)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mcms.svg)](https://pypi.org/project/mcms)

-----

**Table of Contents**

- [mcms - minecraft message service](#mcms---minecraft-message-service)
  - [Overview](#overview)
  - [Quick example](#quick-example)
  - [Installation](#installation)
  - [License](#license)

## Overview
This is an example that uses a [MessageServer](https://github.com/answering007/MessageServer) for Spigot to send commands

## Quick example
```python
# Import section
from mcms.connection import Connection

# Setup connection
connection = Connection("localhost", 8000, ("Admin", "123"))

# Say Hello World to server
response = connection.execute_commands("say hello world!")
print("Response code: ", response[0], "Command result: ", response[1])
```

## Installation

1. Download latest release
2. Install from wheel file:
```console
pip install "path_to_the_mcms_wheel_file.whl"
```

## License

`mcms` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
