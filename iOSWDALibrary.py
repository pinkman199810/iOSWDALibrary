# -*- coding: utf-8 -*-
import time
import wda
import sys
import os.path
from RPA.recognition import templates
from wda.exceptions import WDAElementNotFoundError
from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
sys.setrecursionlimit(2000)


class iOSWDALibrary(object):
    """Robot framework library for iOS UI test automation."""
    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.client = None
        self.session = None
        self.bundle_id = None
        self._strategies = {
            'id': self._find_by_id,
            'name': self._find_by_name,
            'xpath': self._find_by_xpath,
            'label': self._find_by_label,
            'value': self._find_by_value,
            'text': self._find_by_label
        }

    def open_application(self, wda_url='http://127.0.0.1:8100', bundle_id='com.daimler.ris.mercedesme.cn.ios.stage'):
        """Opens a new application to given wda server.

        Examples:
        | Open Application | wda_url=http://internalserver:port | bundle_id=com.daimler.ris.mercedesme.cn.ios.stage
        """
        self.client = wda.Client(wda_url)
        self.client.wait_ready(timeout=10, noprint=False)
        self.bundle_id = bundle_id
        self.session = self.client.session(bundle_id)

    def close_application(self):
        """Closes the current application and also close wda session."""
        self.session.close()

    def launch_application(self):
        """ Launch application. Application can be launched while wda session running.
        This keyword can be used to launch application during test case or between test cases.

        This keyword works while `Open Application` has a test running. This is good practice to `Launch Application`
        and `Quit Application` between test cases. As Suite Setup is `Open Application`, `Test Setup` can be used to `Launch Application`

        Example (syntax is just a representation, refer to RF Guide for usage of Setup/Teardown):
        | [Setup Suite] |
        |  | Open Application | com.daimler.ris.mercedesme.cn.ios.stage
        | [Test Setup] |
        |  | Launch Application |
        |  |  | <<<test execution>>> |
        |  |  | <<<test execution>>> |
        | [Test Teardown] |
        |  | Quit Application |
        | [Suite Teardown] |
        |  | Close Application |

        See `Quit Application` for quiting application but keeping wda sesion running.
        """
        self.session.app_activate(self.bundle_id)

    def quit_application(self):
        """ Quit application. Application can be quit while wda session is kept alive.
        This keyword can be used to close application during test case or between test cases.

        See `Launch Application` for an explanation.
        """
        self.session.app_terminate(self.bundle_id)
    
    def swtich_application(self, bundle_id):
        self.session.app_terminate(bundle_id)
        
    def capture_page_screenshot(self, filepath):
        self.session.screenshot().save(filepath)

    @keyword(tags=['expand', ])
    def capture_screenshot(self, filepath):
        """Takes a screenshot of the current page and embeds it into the log.

        `filename` argument specifies the name of the file to write the
        screenshot into. If no `filename` is given, the screenshot is saved into file
        `wda-screenshot-<counter>.png` under the directory where
        the Robot Framework log file is written into. The `filename` is
        also considered relative to the same directory, if it is not
        given in absolute format.

        `css` can be used to modify how the screenshot is taken. By default
        the background color is changed to avoid possible problems with
        background leaking when the page layout is somehow broken.
        """
        logfile = BuiltIn().get_variable_value('${LOG FILE}')
        logdir = os.path.split(logfile)[0]
        filedir = os.path.split(os.path.abspath(filepath))[0]
        filename = os.path.split(filepath)[1]
        logger.info('screenshot is saved in: %s' % filedir)
        relative_path = os.path.relpath(filedir, logdir)

        self.session.screenshot().save(filepath)
        logger.info('<div><img src="%s\%s" Width="288" height="512"/></div>' % (relative_path, filename), True)

    def press_home_button(self):
        self.client.home()

    def get_text(self, locator):
        """Get element text (for hybrid and mobile browser use `xpath` locator, others might cause problem)

        Example:

        | ${text} | Get Text | //*[contains(@text,'foo')] |
        """
        text = self.__get_text(locator)
        logger.info("Element '%s' text is '%s' " % (locator, text))
        return text

    def clear_text(self, locator):
        """Clears the text field identified by `locator`.

        See `introduction` for details about locating elements.
        """
        element = self._find_element(locator).get(timeout=0)
        element.clear_text()

    def input_text(self, locator, text):
        """Types the given `text` into text field identified by `locator`.

        See `introduction` for details about locating elements.
        """
        element = self._find_element(locator).get(timeout=0)
        element.set_text(text)
    
    def click_a_point(self, x, y, duration=100):
        """ Click on a point"""
        __duration = int(duration)/1000
        if duration:
            return self.client.click(int(float(x)), int(float(y)), __duration)
        return self.client.click(x, y)

    def click_element(self, locator):
        """Click element identified by `locator`.

        Key attributes for arbitrary elements are `index` and `name`. See
        `introduction` for details about locating elements.
        """
        if self._find_element(locator).exists:
            self._find_element(locator).click()
        else:
            logger.info(f"Locator:{locator} not disppear!", also_console=True)
            raise WDAElementNotFoundError(f"Locator:{locator} not disppear!")

    def click_text(self, text, exact_match=False):
        """Click text identified by ``text``.

        By default tries to click first text involves given ``text``, if you would
        like to click exactly matching text, then set ``exact_match`` to `True`.

        If there are multiple use  of ``text`` and you do not want first one,
        use `locator` with `Get Web Elements` instead.
        """
        if exact_match:
            _xpath = u'//*[@value="{}" or @label="{}"]'.format(text, text)
        else:
            _xpath = u'//*[contains(@label,"{}") or contains(@value, "{}")]'.format(text, text)
        if self._find_by_xpath(_xpath).exists:
            self._find_by_xpath(_xpath).click()
        else:
            logger.info(f"Text:{text} not disppear!", also_console=True)
            raise WDAElementNotFoundError(f"Text:{text} not disppear!")

    def swipe(self, start_x, start_y, offset_x, offset_y ,duration=1000):
        """
        Swipe from one point to another point, for an optional duration.

        Args:
         - start_x - x-coordinate at which to start
         - start_y - y-coordinate at which to start
         - offset_x - x-coordinate distance from start_x at which to stop
         - offset_y - y-coordinate distance from start_y at which to stop
         - duration - (optional) time to take the swipe, in ms.
        
        Usage:
        | Swipe | 500 | 100 | 100 | 0 | 1000 |
        """
        _duration = int(duration)/1000
        self.client.swipe(int(float(start_x)), int(float(start_y)), int(float(offset_x)), int(float(offset_y)), _duration)

    def element_attribute_should_match(self, locator, attr_name, match_pattern):
        """Verify that an attribute of an element matches the expected criteria.

        The element is identified by _locator_. See `introduction` for details
        about locating elements. If more than one element matches, the first element is selected.

        The _attr_name_ is the name of the attribute within the selected element.

        The _match_pattern_ is used for the matching, if the match_pattern is
        - boolean or 'True'/'true'/'False'/'false' String then a boolean match is applied
        - any other string is cause a string match

        Examples:

        | Element Attribute Should Match | xpath = //*[contains(@text,'foo')] | text | *foobar |
        | Element Attribute Should Match | xpath = //*[contains(@text,'foo')] | text | f.*ar |
        | Element Attribute Should Match | xpath = //*[contains(@text,'foo')] | enabled | True |

        | 1. is a string pattern match i.e. the 'text' attribute should end with the string 'foobar'
        | 2. is a boolead match i.e. the 'enabled' attribute should be True
        """
        elements = self._find_element(locator).get(timeout=0)
        # if len(elements) > 1:
        #     raise IndexError("CAUTION: '%s' matched %s elements - using the first element only" % (locator, len(elements)))
        if attr_name == "value":
            elements.value == match_pattern
            return True
        elif attr_name == "enabled":
            elements.enabled == match_pattern
            return True
        elif attr_name == "visible":
            elements.visible == match_pattern
            return True
        elif attr_name == "accessible":
            elements.accessible == match_pattern
            return True
        else:
            raise IndexError("CAUTION: '%s' not found" % locator)

    def element_should_be_visible(self, locator):
        """Verifies that element identified with locator is visible.

        Key attributes for arbitrary elements are `id` and `name`. See
        `introduction` for details about locating elements.
        """
        element = self._find_element(locator).get(timeout=0)
        if element.visible:
            logger.info("Element '%s' is visible " % locator)
            return
        logger.info("Element '%s' should be visible but did not" % locator, also_console=True)
        raise AssertionError("Element '%s' should be visible but did not" % locator)

    def element_should_contain_text(self, locator, expected, message=''):
        """Verifies element identified by ``locator`` contains text ``expected``.

        If you wish to assert an exact (not a substring) match on the text
        of the element, use `Element Text Should Be`.

        Key attributes for arbitrary elements are ``id`` and ``xpath``. ``message`` can be used to override the default error message.
        """
        logger.info("Verifying element '%s' contains text '%s'."
                    % (locator, expected))
        actual = self.__get_text(locator)
        if not expected in actual:
            if not message:
                message = "Element '%s' should have contained text '%s' but "\
                          "its text was '%s'." % (locator, expected, actual)
            raise AssertionError(message)

    def element_should_not_contain_text(self, locator, expected, message=''):
        """Verifies element identified by ``locator`` does not contain text ``expected``.

        ``message`` can be used to override the default error message.
        See `Element Should Contain Text` for more details.
        """
        logger.info("Verifying element '%s' does not contain text '%s'."
                   % (locator, expected))
        actual = self.__get_text(locator)
        if expected in actual:
            if not message:
                message = "Element '%s' should not contain text '%s' but " \
                          "it did." % (locator, expected)
            raise AssertionError(message)

    def element_text_should_be(self, locator, expected, message=''):
        """Verifies element identified by ``locator`` exactly contains text ``expected``.

        In contrast to `Element Should Contain Text`, this keyword does not try
        a substring match but an exact match on the element identified by ``locator``.

        ``message`` can be used to override the default error message.
        """
        element = self._find_element(locator).get(timeout=0)
        actual = element.label
        if expected != actual:
            if not message:
                message = "The text of element '%s' should have been '%s' but "\
                          "in fact it was '%s'." % (locator, expected, actual)
            raise AssertionError(message)
        logger.info("Element '%s' text is '%s' " % (locator, expected))

    def element_value_should_be(self, locator, expected):
        element = self._find_element(locator).get(timeout=0)
        if str(expected) != str(element.value):
            raise AssertionError("Element '%s' value should be '%s' "
                                 "but it is '%s'." % (locator, expected, element.value))
        logger.info("Element '%s' value is '%s' " % (locator, expected))

    def get_element_attribute(self,locator,attribute):
        """Get element attribute using given attribute: name, value,...

        Examples:

        | Get Element Attribute | locator | name |
        | Get Element Attribute | locator | value |
        """
        element = self._find_element(locator).get(timeout=0)
        if element is not None:
            if attribute == "value":
                logger.info("Element '%s' value: %s" %(locator,element.value))
                return element.value
            if attribute == "name":
                logger.info("Element '%s' name: %s" %(locator,element.name))
                return element.name
            else:
                 raise AssertionError("Attribute: '%s' error!,Attribute should be value or name" % attribute)
        else:
           logger.info("Element '%s' does not exist" % element) 

    def get_element_location(self, locator):
        """Get element location

        Key attributes for arbitrary elements are `id` and `name`. See
        `introduction` for details about locating elements.
        """
        location={'x':'','y':'','width':'','height':''}
        element = self._find_element(locator).get(timeout=0)
        element_bounds = element.bounds
        location['x'] = element_bounds.x
        location['y'] = element_bounds.y
        location['width'] = element_bounds.width
        location['height'] = element_bounds.height
        logger.info("Element '%s' location: %s " % (locator, element_bounds))
        return location

    def get_window_height(self):
        """Get current device height.

        Example:
        | ${width}       | Get Window Width |
        | ${height}      | Get Window Height |
        | Click A Point  | ${width}         | ${height} |
        """
        return self.client.window_size().height

    def get_window_width(self):
        """Get current device width.

        Example:
        | ${width}       | Get Window Width |
        | ${height}      | Get Window Height |
        | Click A Point  | ${width}          | ${height} |
        """
        return self.client.window_size().width

    def page_should_contain_text(self, text):
        """Verifies that current page contains `text`., if you would not
        like to assert exactly matching text, then set ``exact_match`` to `False`.

        Args:
         - exact_match - default:True
        """
        if self.__is_text_present(text):
            logger.info("Current page contains text '%s'." % text)
        else:
            raise AssertionError("Page should have contained text '%s' but did not" % text)

    def page_should_not_contain_text(self, text):
        """Verifies that current page not contains `text`.

        """
        if self.__is_text_present(text) is False:
            logger.info("Current page not contains text '%s'." % text)
        else:
            raise AssertionError("Page should not have contained text '%s'" % text)

    def page_should_contain_element(self, locator):
        """Verifies that current page contains `locator` element.

        """
        if self.__is_element_present(locator):
            logger.info("Current page contains element '%s'." % locator)
        else:
            raise AssertionError("Page should have contained element '%s' but did not" % locator)

    def page_should_not_contain_element(self, locator):
        """Verifies that current page not contains `locator` element.

        """
        if self.__is_element_present(locator) is False:
            logger.info("Current page not contains element '%s'." % locator)
        else:
            raise AssertionError("Page should not have contained element '%s'" % locator)

    def wait_until_page_contains(self, text, timeout='10s'):
        """Waits until `text` appears on current page.

        Fails if `timeout` expires before the text appears. See
        `introduction` for more information about `timeout` and its
        default value.

        See also `Wait Until Page Does Not Contain`,
        `Wait Until Page Contains Element`,
        `Wait Until Page Does Not Contain Element` and
        BuiltIn keyword `Wait Until Keyword Succeeds`.
        """
        __timeout = int(timeout.lower().replace('s', ''))
        maxtime = time.time() + __timeout
        while True:
            if self.__is_text_present(str(text)):
                return
            if time.time() > maxtime:
                raise AssertionError("Text '%s' did not appear in %ss" % (text, __timeout))
            time.sleep(0.2)

    def wait_until_page_contains_element(self, locator, timeout='10s'):
        """Waits until element specified with `locator` appears on current page.

        Fails if `timeout` expires before the element appears. See
        `introduction` for more information about `timeout` and its
        default value.

        See also `Wait Until Page Contains`,
        `Wait Until Page Does Not Contain`
        `Wait Until Page Does Not Contain Element`
        and BuiltIn keyword `Wait Until Keyword Succeeds`.
        """
        __timeout = int(timeout.lower().replace('s', ''))
        maxtime = time.time() + __timeout
        while True:
            if self.__is_element_present(locator):
                return
            if time.time() > maxtime:
                raise AssertionError("Element '%s' did not appear in %ss" % (locator, __timeout))
            time.sleep(0.2)

    def wait_until_page_does_not_contain_element(self, locator, timeout='10s'):
        """Waits until element specified with `locator` disappears from current page.

        Fails if `timeout` expires before the element disappears. See
        `introduction` for more information about `timeout` and its
        default value.

        `error` can be used to override the default error message.

        See also `Wait Until Page Contains`,
        `Wait Until Page Does Not Contain`,
        `Wait Until Page Contains Element` and
        BuiltIn keyword `Wait Until Keyword Succeeds`.
        """
        __timeout = int(timeout.lower().replace('s', ''))
        maxtime = time.time() + __timeout
        while True:
            if self.__is_element_present(locator) is False:
                return
            if time.time() > maxtime:
                raise AssertionError("Element '%s' still in %ss" % (locator, __timeout))
            time.sleep(0.2)

    def wait_until_page_does_not_contain(self, text, timeout='10s'):
        """Waits until element specified with `locator` disappears from current page.

        Fails if `timeout` expires before the element disappears. See
        `introduction` for more information about `timeout` and its
        default value.

        `error` can be used to override the default error message.

        See also `Wait Until Page Contains`,
        `Wait Until Page Does Not Contain`,
        `Wait Until Page Contains Element` and
        BuiltIn keyword `Wait Until Keyword Succeeds`.
        """
        __timeout = int(timeout.lower().replace('s', ''))
        maxtime = time.time() + __timeout
        while True:
            if self.__is_text_present(text) is False:
                return
            if time.time() > maxtime:
                raise AssertionError("text '%s' still in %ss" % (text, __timeout))
            time.sleep(0.2)

    def hide_keyboard(self,key_name=None):
        """Hides the software keyboard on the device. (optional) In iOS, use `key_name` to press
        a particular key, ex. `Done`. In Android, no parameters are used.
        """
        self.click_text(key_name, exact_match=True)

    def narrow(self, locator):
        """This function is used to replace the "zoom" method of appiumlibrary.
        
        Args:
        - _locator_
        """
        element = self._find_element(locator)
        element.pinch(0.5, -1)

    def enlarge(self, locator):
        """This function is used to replace the "pinch" method of appiumlibrary.

        Args:
        - _locator_
        """
        element = self._find_element(locator)
        element.pinch(2.0, 1)

    def find_image(self, screenshot, template, confidence=90, number=1):
        info = templates.find(screenshot, template, confidence=confidence)
        info.sort()
        print(info)
        left = info[number-1].left
        right = info[number-1].right
        top = info[number-1].top
        bottom = info[number-1].bottom
        x = int((left+right)/2)
        y = int((top+bottom)/2)
        return {'x': x, 'y': y}

    def drag_and_drop_by_element(self, ele1, ele2):
        """ Drag from one element location to another element, default duration:5s.

        Args:
         - ele1 - origin element at which to start
         - ele2 - destination element at which to stop

        Example:
        | Drag And Drop By Element | name=ic_shortcut_findmycar | name=ic_shortcut_caralarm |
        """
        ele1 = self._find_element(ele1).get(timeout=0)
        ele1_x = int(ele1.bounds.x + ele1.bounds.width/2)
        ele1_y = int(ele1.bounds.y + ele1.bounds.height/2)
        ele2 = self._find_element(ele2).get(timeout=0)
        ele2_x = int(ele2.bounds.x + ele2.bounds.width/2)
        ele2_y = int(ele2.bounds.y + ele2.bounds.height/2)
        data = {"actions": [{"action": "press","options": {"x": ele1_x,"y": ele1_y}},
                    {"action": "wait","options": {"ms": 5000}},
                    {"action": "moveTo","options": {"x": ele2_x,"y": ele2_y}},
                    {"action": "wait","options": {"ms": 2000}},
                    {"action": "release"}]}
        r = self.client._session_http.post('/wda/touch/perform', data=data)
        if not r["value"]:
            raise AssertionError(r["value"]['message'])

    def drag_and_drop_by_coordinate(self, start_x, start_y, stop_x, stop_y):
        """ Drag from one point to another point, default duration:5s.

        Args:
         - start_x - x-coordinate at which to start
         - start_y - y-coordinate at which to start
         - stop_x - x-coordinate distance from start_x at which to stop
         - stop_y - y-coordinate distance from start_y at which to stop

        Example:
        | Drag And Drop By Coordinate | start_x=200 | start_y=200 | stop_x=300 | stop_y=300 |
        """
        data = {"actions": [{"action": "press","options": {"x": int(start_x),"y": int(start_y)}},
                    {"action": "wait","options": {"ms": 5000}},
                    {"action": "moveTo","options": {"x": int(stop_x),"y": int(stop_y)}},
                    {"action": "wait","options": {"ms": 2000}},
                    {"action": "release"}]}
        r = self.client._session_http.post('/wda/touch/perform', data=data)
        if not r["value"]:
            raise AssertionError(r["value"]['message'])

    def narrow_by_coordinate(self, x1, y1, x2, y2):
        """ narrow screen by coordinate.

        Args:
         - x1 - X coordinate value of finger 1
         - y1 - Y coordinate value of finger 1
         - x2 - X coordinate value of finger 2
         - y2 - Y coordinate value of finger 2

        Example:
        | Narrow By Coordinate | x1=200 | y1=200 | x2=300 | y2=300 |
        """
        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)
        data = {"actions": 
                    [
                        {
                        "type": "pointer",
                        "id": "finger1",
                        "parameters": {"pointerType": "touch"},
                        "actions": [
                            {"type": "pointerMove", "duration": 1000, "x": x1, "y": y1},
                            {"type": "pointerDown"},
                            {"type": "pointerMove", "duration": 1000, "x": x1*1.25, "y": y1*1.25},
                            {"type": "pointerUp"},
                            ],
                        },
                        {
                        "type": "pointer",
                        "id": "finger2",
                        "parameters": {"pointerType": "touch"},
                        "actions": [
                            {"type": "pointerMove", "duration": 1000, "x": x2, "y": y2},
                            {"type": "pointerDown"},
                            {"type": "pointerMove", "duration": 1000, "x": x2*0.8, "y": y2*0.8},
                            {"type": "pointerUp"},
                            ],
                        },
                    ],
                }
        r = self.client._session_http.post('/actions', data=data)
        if r["value"] != None:
            raise AssertionError(r["value"]['message'])

    def enlarge_by_coordinate(self, x1, y1, x2, y2):
        """ enlarge screen by coordinate.

        Args:
         - x1 - X coordinate value of finger 1
         - y1 - Y coordinate value of finger 1
         - x2 - X coordinate value of finger 2
         - y2 - Y coordinate value of finger 2

        Example:
        | Enlarge By Coordinate | x1=200 | y1=200 | x2=300 | y2=300 |
        """
        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)
        data = {"actions": 
                    [
                        {
                        "type": "pointer",
                        "id": "finger1",
                        "parameters": {"pointerType": "touch"},
                        "actions": [
                            {"type": "pointerMove", "duration": 1000, "x": x1, "y": y1},
                            {"type": "pointerDown"},
                            {"type": "pointerMove", "duration": 1000, "x": x1*0.8, "y": y1*0.8},
                            {"type": "pointerUp"},
                            ],
                        },
                        {
                        "type": "pointer",
                        "id": "finger2",
                        "parameters": {"pointerType": "touch"},
                        "actions": [
                            {"type": "pointerMove", "duration": 1000, "x": x2, "y": y2},
                            {"type": "pointerDown"},
                            {"type": "pointerMove", "duration": 1000, "x": x2*1.25, "y": y2*1.25},
                            {"type": "pointerUp"},
                            ],
                        },
                    ],
                }
        r = self.client._session_http.post('/actions', data=data)
        if r["value"] != None:
            raise AssertionError(r["value"]['message'])

    def temp_wda_session(self, wda_url='http://127.0.0.1:8100', bundle_ID='com.daimler.ris.mercedesme.cn.ios.stage'):
        """Running iOS wda session without using stf api locally

        Args:
         - wda_url(STF) - WebDriverAgentUrl of iOS device control page,Example:http://internalserver:port
         - wda_url(Local) - http://127.0.0.1:8100
         - boundle_ID - Unique identification of iOS software,use: 'ideviceinstaller -l' to view app list in iPhone

        Example:
        | Temp WDA Session | wda_url=http://internalserver:port | boundle_ID=com.daimler.ris.mercedesme.cn.ios.stage |
        | Click Element    | name=更多 |
        """
        self.client = wda.Client(wda_url)
        self.client.wait_ready(timeout=10, noprint=False)
        self.bundle_id = bundle_ID
        self.session = self.client.session(bundle_ID)
        time.sleep(3)
        self.wait_until_page_contains_element('name=ic_home_more')
        time.sleep(2)
        self.click_element('name=id_map_tab')
        time.sleep(2)
        self.narrow_by_coordinate("80", "150", "300", "600")

    # private
    def __get_text(self, locator):
        element = self._find_element(locator).get(timeout=0)
        if element is not None:
            if element.label is not None:
                return element.label
            if element.value is not None:
                return element.value
        return None

    def __is_text_present(self, text):
        _xpath = u'//*[contains(@label,"{}") or contains(@value, "{}")]'.format(text, text)
        try:
            elements = self.session(xpath=_xpath).find_elements()
            for i in elements:
                if i.displayed:
                    return True
            return False
        except wda.exceptions.WDAElementNotFoundError:
            return False

    def __is_element_present(self, locator):
        try:
            elements = self._find_elements(locator)
            for i in elements:
                if i.displayed:
                    return True
            return False
        except wda.exceptions.WDAElementNotFoundError:
            return False

    def _find_element(self, locator):
        (prefix, criteria) = self._parse_locator(locator)
        prefix = 'default' if prefix is None else prefix
        strategy = self._strategies.get(prefix)
        if strategy is None:
            raise ValueError("Element locator with prefix '" + prefix + "' is not supported")
        return strategy(criteria)

    def _find_elements(self, locator):
        (prefix, criteria) = self._parse_locator(locator)
        prefix = 'default' if prefix is None else prefix
        strategy = self._strategies.get(prefix)
        if strategy is None:
            raise ValueError("Element locator with prefix '" + prefix + "' is not supported")
        return strategy(criteria).find_elements()

    def _parse_locator(self, locator: str):
        try:
            if '=' not in locator:
                raise IndexError(f'"=" not in locator: {e}')
            else:
                using = locator.split('=')[0].strip('=').lower()
                value = locator.split('=', 1)[1].strip()
                return using, value
        except Exception as e:
            raise IndexError(f'Locator:[{locator}] Parameter error:{e}')

    # Strategy routines
    def _find_by_id(self, _value):
        return self.session(id=_value)

    def _find_by_name(self, _value):
        return self.session(name=_value)

    def _find_by_xpath(self, _value):
        return self.session(xpath=_value)

    def _find_by_label(self, _value):
        return self.session(label=_value)

    def _find_by_value(self, _value):
        return self.session(value=_value)

if __name__ == "__main__":
    try:
        test_lib = iOSWDALibrary()
        # test_lib.open_application('com.daimler.ris.mercedesme.cn.ios.stage')
        test_lib.temp_wda_session(wda_url='http://serverurl:prot')
    except Exception:
        raise
