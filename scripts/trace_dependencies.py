#!/usr/bin/env python3
"""
Trace all Python dependencies used by the project.

Scans all .py files and categorizes imports as:
- Standard library (built-in)
- Third-party (need pip/uv install)
- Local project modules

Usage:
    python scripts/trace_dependencies.py
"""
import ast
import sys
from pathlib import Path
from collections import defaultdict

# Standard library modules (Python 3.10+ and Python 2 variants for Ableton)
STDLIB_MODULES = {
    'abc', 'argparse', 'ast', 'asyncio', 'base64', 'bisect', 'builtins',
    'calendar', 'collections', 'contextlib', 'copy', 'csv', 'dataclasses',
    'datetime', 'decimal', 'difflib', 'email', 'enum', 'errno', 'fnmatch',
    'fractions', 'functools', 'gc', 'getpass', 'glob', 'gzip', 'hashlib',
    'heapq', 'hmac', 'html', 'http', 'importlib', 'inspect', 'io', 'itertools',
    'json', 'keyword', 'linecache', 'locale', 'logging', 'lzma', 'math',
    'mimetypes', 'multiprocessing', 'numbers', 'operator', 'os', 'pathlib',
    'pickle', 'platform', 'pprint', 'queue', 'random', 're', 'reprlib',
    'secrets', 'select', 'shlex', 'shutil', 'signal', 'socket', 'sqlite3',
    'ssl', 'stat', 'statistics', 'string', 'struct', 'subprocess', 'sys',
    'tarfile', 'tempfile', 'textwrap', 'threading', 'time', 'timeit',
    'token', 'tokenize', 'traceback', 'types', 'typing', 'unittest', 'urllib',
    'uuid', 'venv', 'warnings', 'weakref', 'xml', 'zipfile', 'zipimport',
    'winreg', 'winsound', 'msvcrt', 'typing_extensions',
    # Python 2 names (Ableton's internal Python)
    'Queue', 'SocketServer', 'StringIO', 'cStringIO', 'thread', 'cPickle',
}

# Local project modules (including handler submodules)
LOCAL_MODULES = {
    'MCP_Server', 'mcp_tooling', 'AbletonMCP_Remote_Script', 'handlers', 'server',
    # Handler submodules
    'application', 'arrangement', 'base', 'browser', 'chain', 'clip',
    'clip_slot', 'conversion', 'device', 'drum_rack', 'groove', 'mixer',
    'sample', 'scene', 'session', 'simpler', 'song', 'specialized',
    'track', 'track_group', 'interface', 'mcp_socket',
    # mcp_tooling submodules
    'connection', 'util', 'devices', 'generators', 'chords', 'theory',
    'basslines', 'drummer', 'automation', 'conversions', 'macros',
    'recording', 'performance', 'humanization', 'rhythmic_comp',
    'ableton_helpers', 'arrangement', 'constants',
    # orchestration subdirectories
    'brass', 'strings', 'woodwinds', 'rhythm', 'styles', 'voicings',
}

# Ableton internal modules (only available inside Live)
ABLETON_MODULES = {'Live', '_Framework', '_Generic'}


def get_imports(filepath: Path) -> set:
    """Extract top-level import names from a Python file."""
    imports = set()
    try:
        tree = ast.parse(filepath.read_text(encoding='utf-8', errors='ignore'))
    except SyntaxError:
        return imports
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split('.')[0])
    return imports


def categorize(module: str) -> str:
    if module in STDLIB_MODULES:
        return 'stdlib'
    if module in LOCAL_MODULES or module.startswith('_'):
        return 'local'
    if module in ABLETON_MODULES:
        return 'ableton'
    return 'third_party'


def main():
    root = Path(__file__).resolve().parent.parent
    py_files = [f for f in root.rglob('*.py') 
                if '.venv' not in str(f) and '__pycache__' not in str(f)]
    
    all_imports = defaultdict(set)
    locations = defaultdict(list)
    
    for f in py_files:
        for imp in get_imports(f):
            cat = categorize(imp)
            all_imports[cat].add(imp)
            locations[imp].append(f.relative_to(root))
    
    print("=" * 50)
    print("DEPENDENCY TRACE REPORT")
    print("=" * 50)
    
    print("\n[THIRD-PARTY] Packages (pip/uv install required)")
    print("-" * 40)
    for pkg in sorted(all_imports['third_party']):
        locs = locations[pkg][:3]
        print(f"  * {pkg}")
        for loc in locs:
            print(f"      {loc}")
        if len(locations[pkg]) > 3:
            print(f"      ... and {len(locations[pkg]) - 3} more")
    
    print("\n[ABLETON] Internal modules (Live's Python only)")
    print("-" * 40)
    print(f"  {', '.join(sorted(all_imports['ableton']))}")
    
    print("\n[STDLIB] Standard library")
    print("-" * 40)
    print(f"  {', '.join(sorted(all_imports['stdlib']))}")
    
    print("\n[LOCAL] Project modules")
    print("-" * 40)
    print(f"  {', '.join(sorted(all_imports['local']))}")
    
    # pyproject.toml check
    pyproject = root / 'pyproject.toml'
    if pyproject.exists():
        print("\n" + "=" * 50)
        print("DECLARED IN pyproject.toml")
        print("=" * 50)
        in_deps = False
        for line in pyproject.read_text().splitlines():
            if 'dependencies' in line and '=' in line:
                in_deps = True
                continue
            if in_deps:
                if ']' in line:
                    break
                if '"' in line:
                    print(f"  {line.strip().strip(',')}")
    
    print("\nDone.")


if __name__ == '__main__':
    main()
