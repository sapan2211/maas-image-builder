# vi: ts=4 expandtab
# Upstream Author:
#
#     Canonical Ltd.
#
# Copyright:
#
#     (c) 2014-2017 Canonical Ltd.
#
# Licence:
#
# If you have an executed agreement with a Canonical group company which
# includes a licence to this software, your use of this software is governed
# by that agreement.  Otherwise, the following applies:
#
# Canonical Ltd. hereby grants to you a world-wide, non-exclusive,
# non-transferable, revocable, perpetual (unless revoked) licence, to (i) use
# this software in connection with Canonical's MAAS software to install Windows
# in non-production environments and (ii) to make a reasonable number of copies
# of this software for backup and installation purposes.  You may not: use,
# copy, modify, disassemble, decompile, reverse engineer, or distribute the
# software except as expressly permitted in this licence; permit access to the
# software to any third party other than those acting on your behalf; or use
# this software in connection with a production environment.
#
# CANONICAL LTD. MAKES THIS SOFTWARE AVAILABLE "AS-IS".  CANONICAL  LTD. MAKES
# NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, WHETHER ORAL OR WRITTEN,
# WHETHER EXPRESS, IMPLIED, OR ARISING BY STATUTE, CUSTOM, COURSE OF DEALING
# OR TRADE USAGE, WITH RESPECT TO THIS SOFTWARE.  CANONICAL LTD. SPECIFICALLY
# DISCLAIMS ANY AND ALL IMPLIED WARRANTIES OR CONDITIONS OF TITLE, SATISFACTORY
# QUALITY, MERCHANTABILITY, SATISFACTORINESS, FITNESS FOR A PARTICULAR PURPOSE
# AND NON-INFRINGEMENT.
#
# IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING WILL
# CANONICAL LTD. OR ANY OF ITS AFFILIATES, BE LIABLE TO YOU FOR DAMAGES,
# INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING
# OUT OF THE USE OR INABILITY TO USE THIS SOFTWARE (INCLUDING BUT NOT LIMITED
# TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU
# OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER
# PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGES.

"""Main execution of maas-image-builder."""

import logging
import os
import sys
import traceback

from stevedore.extension import ExtensionManager

from mib.parser import load_parser

# Enable basic logging to console.
logging.basicConfig()


def execute():
    """Main execution of the application."""
    # Check that have root privledges
    if os.geteuid() != 0:
        print('Error: must run with root privileges.')
        sys.exit(1)

    # Load all extensions.
    manager = ExtensionManager("mib.builder", invoke_on_load=True)
    builders = {
        extension.obj.name: extension.obj
        for extension in manager
        }

    # Load and parse the arguments.
    parser = load_parser(builders.values())
    args = parser.parse_args()

    # Check that the output directory exists.
    args.output = os.path.abspath(args.output)
    dirpath = os.path.dirname(args.output)
    if not os.path.exists(dirpath):
        print('Error: unable to write to output file in directory: %s' % (
            dirpath))
        sys.exit(1)

    # Build the image.
    builder = builders[args.builder]
    try:
        builder.build_image(args)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception:  # pylint: disable=broad-except
        traceback.print_exc()
        sys.exit(1)

    sys.exit(0)
