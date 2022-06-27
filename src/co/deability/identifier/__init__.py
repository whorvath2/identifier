"""
Copyright © 2021 William L Horvath II

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import subprocess
from typing import List

tag_str: str = str(
    subprocess.run(["git", "tag"], capture_output=True, text=True).stdout
)

if tag_str:
    tags: List[str] = tag_str.split("\n")
    tags.reverse()
    __version__ = tags[0]
else:
    __version__ = os.environ.get("IDENTIFIER_VERSION", "N/A")
