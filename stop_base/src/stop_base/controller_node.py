# Software License Agreement (BSD License)
#
# Copyright (C) 2015, Jack O'Quin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of the author nor of other contributors may be
#    used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
.. module:: controller_node

This Python module implements a controller interface for interrupting
the flow of `geometry_msgs/Twist`_ commands to the robot base.

.. include:: weblinks.rst

"""
# enable some python3 compatibility options:
from __future__ import absolute_import, print_function, unicode_literals

import rospy
import threading

from bwi_msgs.msg import StopBaseStatus
from bwi_msgs.srv import StopBase
from geometry_msgs.msg import Twist

from .transitions import StopBaseState


class ControllerNode(object):
    """ Stop base controller node.
    """
    def __init__(self):
        """ Constructor. """
        rospy.init_node('stop_base_controller')
        self.lock = threading.RLock()
        """ Big Controller Lock. """
        self.state = StopBaseState()
        """ Controller state. """
        self.last_command = None
        """ Last velocity command received. """
        self.zero_vel = Twist()
        self.pub_vel = rospy.Publisher('cmd_vel_safe', Twist, 1)
        self.pub_status = rospy.Publisher('stop_base_status',
                                          StopBaseStatus, 1, latch=True)
        rospy.Subscriber('cmd_vel', Twist, self.cmd_vel_callback)

        # Handle service requests until canceled.
        rospy.spin()

    def cmd_vel_callback(self, msg):
        """ Velocity command request callback.

        :param msg: newest ``cmd_vel`` message.
        :type msg: `geometry_msgs/Twist`_
        """
        rospy.logdebug('cmd_vel callback:')
        self.last_command = msg
        if self.state.status == StopBaseStatus.RUNNING:
            self.pub_vel.publish(msg)
        else:
            self.stop_robot()

    def stop_robot(self):
        """ Send stop commands to a robot not in the RUNNING state.

        This implementation sends zero velocities at once.  Some
        robots might benefit from more gradual stop velocities.
        """
        self.pub_vel.publish(self.zero_vel)


def main():
    """ Controller node main entry point. """
    node = ControllerNode()
