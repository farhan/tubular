#! /usr/bin/env python3

"""
Script to check the combined test status of a GitHub PR or commit SHA.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import logging
import sys
import click
import yaml

from tubular.github_api import GitHubAPI  # pylint: disable=wrong-import-position

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
LOG = logging.getLogger(__name__)


@click.command()
@click.option(
    '--org',
    help='Org from the GitHub repository URL of https://github.com/<org>/<repo>',
    default='edx'
)
@click.option(
    '--repo',
    help='Repo name from the GitHub repository URL of https://github.com/<org>/<repo>',
    required=True
)
@click.option(
    '--token',
    envvar='GIT_TOKEN',
    help='The github access token, see https://help.github.com/articles/creating-an-access-token-for-command-line-use/'
)
@click.option(
    '--input_file',
    help='YAML file from which to read a PR number to check, with the top-level key "pr_number"'
)
@click.option(
    '--pr_number',
    default=None,
    help='Pull request number to check.',
    type=int,
)
@click.option(
    '--commit_hash',
    help='Commit hash to check.',
)
def check_tests(org,
                repo,
                token,
                input_file,
                pr_number,
                commit_hash):
    """
    Check the current combined status of a GitHub PR/commit in a repo once.

    If tests have passed for the PR/commit, return a success.
    If any other status besides success (such as in-progress/pending), return a failure.

    If an input YAML file is specified, read the PR number from the file to check.
    Else if both PR number -and- commit hash is specified, return a failure.
    Else if either PR number -or- commit hash is specified, check the tests for the specified value.
    """
    gh_utils = GitHubAPI(org, repo, token)

    if pr_number and commit_hash:
        LOG.info("Both PR number and commit hash are specified. Only one of the two should be specified - failing.")
        sys.exit(1)

    status_success = False
    if input_file:
        input_vars = yaml.safe_load(io.open(input_file, 'r'))
        pr_number = input_vars['pr_number']
        status_success = gh_utils.check_pull_request_test_status(pr_number)
        git_obj = 'PR #{}'.format(pr_number)
    elif pr_number:
        status_success = gh_utils.check_pull_request_test_status(pr_number)
        git_obj = 'PR #{}'.format(pr_number)
    elif commit_hash:
        status_success = gh_utils.is_commit_successful(commit_hash)
        git_obj = 'commit hash {}'.format(commit_hash)

    LOG.info("{}: Combined status of {} is {}.".format(
        sys.argv[0], git_obj, "success" if status_success else "failed"
    ))

    # An exit code of 0 means success and non-zero means failure.
    sys.exit(not status_success)


if __name__ == '__main__':
    check_tests()  # pylint: disable=no-value-for-parameter