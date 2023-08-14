from contextlib import contextmanager
from io import StringIO
import os
from subprocess import check_output
from typing import Iterator, List, Tuple
from tempfile import TemporaryDirectory
from unittest import TestCase, mock
from pseudomyth import automatic_mode


@contextmanager
def temp_cd(target: str) -> Iterator[None]:
    cwd = os.getcwd()
    os.chdir(target)

    try:
        yield
    finally:
        os.chdir(cwd)


class ExampleTest(TestCase):
    maxDiff = None

    def test_readme_example(self) -> None:
        """
        Make sure that the example in the README is representative of functionality.
        """

        documented_call_and_response: List[Tuple[str, List[str]]] = []

        with open(
            os.path.join(os.path.dirname(__file__), '..', 'README.rst'),
            'rt',
        ) as readme_file:
            for prefixed_line in (
                ln.strip('\n') for ln in readme_file if ln.startswith('   ')
            ):
                line = prefixed_line[3:]
                if line.startswith('$ '):
                    documented_call_and_response.append((line[2:], []))
                else:
                    documented_call_and_response[-1][1].append(line)

        self.assertEqual(
            [c for (c, r) in documented_call_and_response],
            ['pip install pseudomyth', 'ls', 'pseudomyth'],
            "if these aren't the commands being run, then the assumptions we're "
            "testing don't make sense",
        )

        installation, directory_listing, invocation = documented_call_and_response

        self.assertEqual(
            installation[1], [], "there should be no response to the installation"
        )
        self.assertNotEqual(directory_listing[1], [], "there should be episodes")

        mock_stdout = StringIO()

        # populate a directory with the listed files:
        with (
            TemporaryDirectory() as td,
            mock.patch('pseudomyth.wait', lambda: print()),
            mock.patch('sys.stdout', mock_stdout),
            temp_cd(td),
            mock.patch('pseudomyth.check_output') as run_stuff,
        ):
            for filename in directory_listing[1]:
                with open(filename, 'wb'):
                    pass

            # quick check to see we've done the right thing:
            self.assertEqual(
                check_output('ls').decode('utf-8'),
                '\n'.join(directory_listing[1]) + '\n',
            )

            automatic_mode()

            printed_output = mock_stdout.getvalue()

            self.assertEqual(
                sorted(run_stuff.mock_calls),
                [
                    # XXX populate this list
                ]
            )

            # make sure stuff (except OPs and EDs) has been moved:
            self.assertEqual(
                check_output('ls').decode('utf-8'),
                '\n'.join(
                    [f for f in directory_listing[1] if 'OP' in f or 'ED' in f]
                ) + '\nconsumed\n',
            )
            self.assertEqual(
                check_output(['ls', 'consumed']).decode('utf-8'),
                '\n'.join(
                    [f for f in directory_listing[1] if not ('OP' in f or 'ED' in f)]
                ) + '\n'
            )

        self.assertEqual(
            '\n'.join(invocation[1]),
            printed_output,
        )
