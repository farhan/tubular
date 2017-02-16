#! /usr/bin/env python3

"""
Command-line script used to delete AWS Auto-Scaling Groups that are tagged for deletion via Asgard.
"""
# pylint: disable=invalid-name
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import logging
import traceback
import click

from tubular import asgard  # pylint: disable=wrong-import-position
from tubular.ec2 import get_asgs_pending_delete  # pylint: disable=wrong-import-position

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


@click.command()
def delete_asg():
    """
    Method to delete AWS Auto-Scaling Groups via Asgard that are tagged for deletion.
    """
    error = False
    try:
        asgs = get_asgs_pending_delete()
        for asg in asgs:
            try:
                asgard.delete_asg(asg.name)
            except Exception as e:  # pylint: disable=broad-except
                click.secho("Unable to delete ASG: {0} - {1}".format(asg, e), fg='red')
                error = True
    except Exception as e:  # pylint: disable=broad-except
        traceback.print_exc()
        click.secho("An error occured while cleaning up ASGs: {0}".format(e), fg='red')
        error = True

    if error:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    delete_asg()