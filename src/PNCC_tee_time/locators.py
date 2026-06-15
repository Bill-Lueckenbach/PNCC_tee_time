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

########## PNCC Tee Time Booking Page ##########
BOOKING_URL           = "https://www.mcconnellgolf.com/Default.aspx?p=dynamicmodule&pageid=4610568&tt=booking&course=82&ssid=4610888&vnf=1"
BOOKING_DATE          = (By.ID, "txtDate")

# Tee sheet time slot panel (the Ajax-refreshed container)
BOOKING_TIME_SLOT_AJAX_PANEL = (
  By.ID,
  "masterPageUC_MPCA4610563_ctl03_ctrl_Booking_ctl02_TimeSlotPanelPanel",
)
BOOKING_TIME_SLOT_PANEL  = (
  By.ID,
  "masterPageUC_MPCA4610563_ctl03_ctrl_Booking_ctl02_TimeSlotPanel",
)

# Available (bookable) rows are marked with NC_TimeSlotPanelSlotAvailableFull.
# This avoids matching reserved/no-slots rows, which can still appear under
# timeslotJQ containers.
BOOKING_AVAILABLE_SLOTS  = (
  By.CSS_SELECTOR,
  "tr.NC_TimeSlotPanelSlotAvailableFull",
)

# Reserve/Request button inside an available slot's openTee div
BOOKING_RESERVE_BTN      = (
  By.CSS_SELECTOR,
  "div.openTee div[onclick*='LaunchReserver']",
)

# Time label inside a slot row (e.g. "9:30 AM")
BOOKING_SLOT_TIME_TEXT   = (By.CSS_SELECTOR, "span.timeText")

# Reservation blocks showing occupancy (classes like NC_Reserved4, NC_ReservedToday2)
BOOKING_SLOT_RESERVATION   = (By.CSS_SELECTOR, "div.NC_Reserved")

# Individual player entries (member or guest)
BOOKING_SLOT_PLAYER_ENTRY  = (
  By.CSS_SELECTOR,
  "div.NC_MemberPlayer.playerJQ, div.NC_GuestPlayer.playerJQ",
)

# Player name container (parent of the span.fullName)
BOOKING_SLOT_PLAYER_NAME   = (By.CSS_SELECTOR, "div.playerName.noPlayerSelect")

# Individual player full name text
BOOKING_SLOT_FULL_NAME     = (By.CSS_SELECTOR, "span.fullName")

# Make Tee Time popup (rendered after clicking Reserve)
BOOK_TEE_TIME_PARTY_SIZE_INPUT = (
  By.ID,
  "ctl00_ctrl_MakeTeeTime_drpPartySize_tCombo_Input",
)

BOOK_TEE_TIME_PARTY_SIZE_ARROW = (
  By.ID,
  "ctl00_ctrl_MakeTeeTime_drpPartySize_tCombo_Arrow",
)

BOOK_TEE_TIME_PARTY_SIZE_OPTIONS = (
  By.CSS_SELECTOR,
  "#ctl00_ctrl_MakeTeeTime_drpPartySize_tCombo_DropDown li.rcbItem, "
  "#ctl00_ctrl_MakeTeeTime_drpPartySize_tCombo div.rcbSlide li.rcbItem",
)

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

