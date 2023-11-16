"""The following code is used to provide an alternative to students who do not have a Raspberry Pi.
If you have a Raspberry Pi, or a SenseHAT emulator under Debian, you do not need to use this code.

You need to split the classes here into two files, one for the CarParkDisplay and one for the CarDetector.
Attend to the TODOs in each class to complete the implementation."""
from carparkdisplay import CarParkDisplay
from cardetector import CarDetector

# -----------------------------------------#
# TODO: STUDENT IMPLEMENTATION STARTS HERE #
# -----------------------------------------#


if __name__ == '__main__':
    # TODO: Run each of these classes in a separate terminal.
    #  You should see the CarParkDisplay update when you click the buttons in the CarDetector.
    # These classes are not designed to be used in the same module - they are both blocking.
    # If you uncomment one, comment-out the other.

    """It is heavily recommended to run the car park display normally while running the car detector using a
    Git Bash terminal."""



    # CarParkDisplay()
    CarDetector()
