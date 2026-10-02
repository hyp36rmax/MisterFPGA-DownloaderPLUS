"""Report encoding corruption in changed public documentation; never rewrite it."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = {'.md', '.rst', '.txt', '.html'}


def corruption_signatures():
    # Known UTF-8 characters decoded incorrectly as a Western legacy encoding.
    originals = ''.join(chr(n) for n in range(0x80, 0x100))
    originals += ''.join(chr(n) for n in range(0x2010, 0x2028))
    originals += ''.join(chr(n) for n in range(0x2190, 0x2200))
    originals += ''.join(chr(n) for n in range(0x2500, 0x2580)) + '\ufeff'
    signatures = {'\ufffd'}
    for character in originals:
        for encoding in ('cp1252', 'latin1'):
            try:
                wrong = character.encode('utf-8').decode(encoding)
            except UnicodeDecodeError:
                continue
            if wrong != character:
                signatures.add(wrong)
    return tuple(sorted(signatures, key=lambda s: (-len(s), s)))


SIGNATURES = corruption_signatures()


def problems(data):
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError as exc:
        prefix = data[:exc.start]
        line = prefix.count(b'\n') + 1
        column = len(prefix.rsplit(b'\n', 1)[-1]) + 1
        return [(line, column, 'invalid UTF-8 byte 0x%02x' % data[exc.start])]
    found = []
    for number, line in enumerate(text.splitlines(), 1):
        for signature in SIGNATURES:
            column = line.find(signature)
            if column >= 0:
                found.append((number, column + 1, 'known mojibake ' + ascii(signature)))
    return found


def git(*arguments):
    return subprocess.check_output(['git', *arguments], cwd=ROOT)


def documentation_paths(base=None, all_files=False):
    if all_files:
        raw = git('ls-files', '-z')
    else:
        base = base or 'HEAD^'
        raw = git('diff', '--name-only', '--diff-filter=ACMR', '-z', base, 'HEAD')
        raw += git('diff', '--name-only', '--diff-filter=ACMR', '-z', 'HEAD')
        raw += git('ls-files', '--others', '--exclude-standard', '-z')
    paths = {name.decode('utf-8') for name in raw.split(b'\0') if name}
    return sorted(name for name in paths if Path(name).suffix.lower() in SUFFIXES
                  and not name.startswith('dist/') and (ROOT / name).is_file())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', help='Git revision before the documentation changes')
    parser.add_argument('--all', action='store_true', help='Review all tracked documentation')
    args = parser.parse_args()
    paths = documentation_paths(args.base, args.all)
    failures = 0
    for name in paths:
        for line, column, description in problems((ROOT / name).read_bytes()):
            print(f'{name}:{line}:{column}: {description}')
            failures += 1
    if failures:
        return 1
    print(f'Documentation encoding passed: {len(paths)} files checked.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
