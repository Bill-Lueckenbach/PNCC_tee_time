"""Centralised element locator constants for all PNCC pages.

Storing locators here (rather than inside page or element functions) keeps
selectors in one place so that a single site change only requires one edit.

Conventions:
    - Constants are grouped by page/section using plain module-level names
      or simple namespacing objects (e.g. a plain dict or namedtuple).
    - Each locator is a tuple of (By.<strategy>, "selector") so it can be
      passed directly to Selenium's find_element / find_elements.

Example::

    LOGIN_USERNAME = (By.ID, "masterPageUC_MPCA342028_ctl00_txtUsernam
    LOGIN_PASSWORD = (By.ID, "masterPageUC_MPCA342028_ctl00_txtCookiePassword")
    LOGIN_SUBMIT   = (By.CSS_SELECTOR, "button[type='submit']")
"""

from selenium.webdriver.common.by import By

########## PNCC Main Page ##########
PNCC_MAIN_PAGE_URL  = "https://www.portersneckcountryclub.com/"
LOGIN_MENU_ITEM     = (By.ID, "ulMenuItem_327855")  # nav link to login page

########## PNCC Tee Time Booking Page ##########
BOOKING_URL           = "https://www.mcconnellgolf.com/Default.aspx?p=dynamicmodule&pageid=4610568&tt=booking&course=82&ssid=4610888&vnf=1"
BOOKING_DATE          = (By.ID, "txtDate")
# Date input container and calendar trigger from the dateBox widget.
BOOKING_DATE_BOX      = (By.CSS_SELECTOR, "span.dateBox")
BOOKING_DATE_PICKER_BUTTON = (By.CSS_SELECTOR, "a[onclick*='displayDatePicker']")
BOOKING_DATE_PICKER_IMAGE  = (By.CSS_SELECTOR, 
                              "span.dateBox a img[alt='Show Calendar']")
BOOKING_PREV_DAY_LINK      = (By.CSS_SELECTOR, "#prevDates a[onclick*='changeDate']")
BOOKING_NEXT_DAY_LINK      = (By.CSS_SELECTOR, "#nextDates a[onclick*='changeDate']")

# Tee sheet time slot panel (the Ajax-refreshed container)
BOOKING_TIME_SLOT_AJAX_PANEL = (
  By.ID,
  "masterPageUC_MPCA4610563_ctl03_ctrl_Booking_ctl02_TimeSlotPanelPanel",
)
BOOKING_TIME_SLOT_PANEL  = (
  By.ID,
  "masterPageUC_MPCA4610563_ctl03_ctrl_Booking_ctl02_TimeSlotPanel",
)
BOOKING_COURSE_DATE_HEADER = (By.CSS_SELECTOR, "div.NC_TimeSlotPanelSlotDate")
BOOKING_NEXT_OPEN_MESSAGE  = (By.CSS_SELECTOR, "div.ncDateOpen")
BOOKING_COUNTDOWN          = (By.ID, "cdownBox")

# All rendered time slot rows (one per 10-minute interval)
# Slot IDs follow the pattern: {H}_{MM}_{AM|PM}82_  e.g. "9_30_AM82_"
BOOKING_ALL_SLOTS        = (By.CSS_SELECTOR, "div.tsSection.timeslotJQ")
BOOKING_SLOT_BY_TIME_ID_PREFIX = (By.CSS_SELECTOR, "div.tsSection[id$='82_']")
BOOKING_SLOT_TABLE_ROWS        = (By.CSS_SELECTOR, "div.tsSection table tr")
BOOKING_SLOT_CONTAINER         = (By.CSS_SELECTOR, "div.block.Slot")
BOOKING_SLOT_TIME_ROW          = (
  By.CSS_SELECTOR,
  "tr.NC_TimeSlotPanelSlotAvailableFull, tr.NC_TimeSlotPanelNoSlotsFull",
)

# Available (bookable) rows are marked with NC_TimeSlotPanelSlotAvailableFull.
# This avoids matching reserved/no-slots rows, which can still appear under
# timeslotJQ containers.
BOOKING_AVAILABLE_SLOTS  = (
  By.CSS_SELECTOR,
  "tr.NC_TimeSlotPanelSlotAvailableFull",
)
BOOKING_UNAVAILABLE_SLOTS = (By.CSS_SELECTOR, "tr.NC_TimeSlotPanelNoSlotsFull")

# Reserve/Request button inside an available slot's openTee div
BOOKING_RESERVE_BTN      = (
  By.CSS_SELECTOR,
  "div.openTee div[onclick*='LaunchReserver']",
)
BOOKING_SLOT_OPEN_TEE      = (By.CSS_SELECTOR, "div.openTee")

# Time label inside a slot row (e.g. "9:30 AM")
BOOKING_SLOT_TIME_TEXT   = (By.CSS_SELECTOR, "span.timeText")
BOOKING_SLOT_START_TEE    = (By.CSS_SELECTOR, "span.startTee")
BOOKING_SLOT_TIME_CELL    = (By.CSS_SELECTOR, "td.TimeText")

# Reservation / player details inside the party holder area.
BOOKING_SLOT_PARTY_HOLDER = (By.CSS_SELECTOR, "td.partyHolder")
BOOKING_SLOT_RES_SECTION  = (
  By.CSS_SELECTOR,
  "div.resSection, div.resSectionBlocked567, div.resSectionBlocked",
)
# Reservation blocks showing occupancy (classes like NC_Reserved4, NC_ReservedToday2)
BOOKING_SLOT_RESERVATION   = (By.CSS_SELECTOR, "div.NC_Reserved")
BOOKING_SLOT_BLOCK_BORDER  = (By.CSS_SELECTOR, "span.blockBorder")

# Party info container with player entries
BOOKING_SLOT_PARTY_INFO    = (By.CSS_SELECTOR, "div.partyinfo")
# Individual player entries (member or guest)
BOOKING_SLOT_PLAYER_ENTRY  = (
  By.CSS_SELECTOR,
  "div.NC_MemberPlayer.playerJQ, div.NC_GuestPlayer.playerJQ",
)
# All player names within a slot (spans within player entries)
BOOKING_SLOT_PLAYER_NAMES_LIST = (By.CSS_SELECTOR, 
                                  "div.playerName.noPlayerSelect span.fullName"
                                )
# Player name container (parent of the span.fullName)
BOOKING_SLOT_PLAYER_NAME   = (By.CSS_SELECTOR, "div.playerName.noPlayerSelect")
# Individual player full name text
BOOKING_SLOT_FULL_NAME     = (By.CSS_SELECTOR, "span.fullName")
BOOKING_SLOT_CANCEL_TRASH  = (By.CSS_SELECTOR, "span.cancelTrashButton")
BOOKING_SLOT_NEED_PLAYER   = (By.CSS_SELECTOR, "div.needPlayerName")
BOOKING_SLOT_VIEW_REG_ICON = (By.CSS_SELECTOR, "span.ncIcon.ncViewRegistrantsIcon")

# Round length selector (booking form)
# Example selected value in input: "Eighteen Holes"
BOOKING_ROUND_LENGTH_SECTION = (By.ID, "ncRoundLength")
BOOKING_ROUND_LENGTH_INPUT = (
  By.ID,
  "ctl00_ctrl_MakeTeeTime_drpRoundLength_tCombo_Input",
)
BOOKING_ROUND_LENGTH_ARROW = (
  By.ID,
  "ctl00_ctrl_MakeTeeTime_drpRoundLength_tCombo_Arrow",
)
# Option items are rendered by Telerik RadComboBox in popup list containers.
BOOKING_ROUND_LENGTH_OPTION_ITEMS = (
  By.CSS_SELECTOR,
  "div.rcbSlide li.rcbItem, div.rcbSlide li.rcbHovered",
)
########## Booking form selectors ##########




# PNCC Login Page
LOGIN_URL      = (
  "https://www.mcconnellgolf.com/default.aspx?p=dynamicmodule"
  "&pageid=4610552&ssid=4610870&vnf=1"
)
LOGIN_USERNAME    = (By.ID, "masterPageUC_MPCA342028_ctl00_txtUsername")
LOGIN_PASSWORD    = (
  By.CSS_SELECTOR,
  "#masterPageUC_MPCA342028_ctl00_txtPassword,"
  " #masterPageUC_MPCA342028_ctl00_txtCookiePassword",
)
LOGIN_REMEMBER_ME = (By.ID, "masterPageUC_MPCA342028_ctl00_chkRM")
LOGIN_SUBMIT      = (By.ID, "btnSecureLogin")

# Post login landing page (used to verify successful login)
MEMBER_HOME_URL = (
  "https://www.mcconnellgolf.com/default.aspx?p=dynamicmodule"
  "&ssid=4610871&vnf=1&navRefresh=1&pageid=4610553")

