#include "catch2/catch.hpp"

#include "sound_enum.h"
#include "ScreenHandler.hpp"
#include "gui_time.hpp" //gui::GetTick
#include "mock_windows.hpp"
#include "mock_display.hpp"
#include <guiconfig/GuiDefaults.hpp>
#include "window_text.hpp"
#include "knob_event.hpp"
#include <memory>
#include "display_helper.h"
#include <str_utils.hpp>

static TMockDisplay<240, 320, 16> MockDispBasic;

static uint32_t hal_tick = 0;
uint32_t gui::GetTick() { return hal_tick; }

// Frame is different than screen (cannot host subwindows)
// also check if frame is notified about visibility changes
TEST_CASE("Visibility notifycation test", "[window]") {
    MockDisplay::Bind(MockDispBasic);
    MockDisplay::Instance().clear(COLOR_BLACK);
    MockFrame_VisibilityNotifycations frame;

    window_t &win = frame.win;
    frame.Draw(); // clears invalidation rect

    // no need to call HideBehindDialog, because frame cannot host dialogs

    REQUIRE(win.IsVisible());
    REQUIRE(win.HasVisibleFlag());
    REQUIRE_FALSE(win.HasEnforcedCapture());
    REQUIRE_FALSE(win.IsHiddenBehindDialog());
    REQUIRE(win.IsCapturable());
    REQUIRE(frame.ChangedCounter == 0);
    REQUIRE(frame.GetInvRect().IsEmpty());

    win.Hide();

    REQUIRE_FALSE(win.IsVisible());
    REQUIRE_FALSE(win.HasVisibleFlag());
    REQUIRE_FALSE(win.HasEnforcedCapture());
    REQUIRE_FALSE(win.IsHiddenBehindDialog());
    REQUIRE_FALSE(win.IsCapturable());
    REQUIRE(frame.ChangedCounter == 1);
    REQUIRE(frame.GetInvRect() == win.GetRect());
    frame.ChangedCounter = 0;
    frame.Draw(); // clears invalidation rect

    // unregistration must invalidate rect
    // mock does not increase counter
    frame.UnregisterSubWin(win);
    REQUIRE(frame.GetInvRect() == win.GetRect());
    frame.Draw(); // clears invalidation rect

    // registration cannot invalidate rect
    // mock does not increase counter
    frame.RegisterSubWin(win);
    REQUIRE_FALSE(win.IsVisible());
    REQUIRE_FALSE(win.HasVisibleFlag());
    REQUIRE_FALSE(win.HasEnforcedCapture());
    REQUIRE_FALSE(win.IsHiddenBehindDialog());
    REQUIRE_FALSE(win.IsCapturable());
    REQUIRE(frame.GetInvRect().IsEmpty());
    frame.Draw(); // clears invalidation rect

    win.Show();

    REQUIRE(win.IsVisible());
    REQUIRE(win.HasVisibleFlag());
    REQUIRE_FALSE(win.HasEnforcedCapture());
    REQUIRE_FALSE(win.IsHiddenBehindDialog());
    REQUIRE(win.IsCapturable());
    REQUIRE(frame.ChangedCounter == 1);
    frame.ChangedCounter = 0;
    frame.Draw(); // clears invalidation rect

    // unregistration must invalidate rect
    // mock does not increase counter
    frame.UnregisterSubWin(win);
    REQUIRE(frame.GetInvRect() == win.GetRect());
    frame.Draw(); // clears invalidation rect
}

TEST_CASE("Visibility notifycation test, hidden win registration", "[window]") {
    MockDisplay::Bind(MockDispBasic);
    MockDisplay::Instance().clear(COLOR_BLACK);
    Rect16 rc = GENERATE(GuiDefaults::RectScreen, Rect16(20, 20, 20, 20));
    MockScreen screen;
    screen.Draw(); // clear invalidation rect

    BasicWindow win(nullptr, rc);
    win.Hide();

    screen.RegisterSubWin(win); // register hidden win
    REQUIRE(screen.GetInvRect().IsEmpty()); // hidden win should not set invalidation rect
}

TEST_CASE("Capturable test window in screen", "[window]") {
    MockDisplay::Bind(MockDispBasic);
    MockDisplay::Instance().clear(COLOR_BLACK);
    MockScreen screen;
    Screens::Access()->Set(&screen); // instead of screen registration
    screen.Draw(); // clears invalidation rect

    // just test one of windows, does not matter which one
    window_t &win = screen.w0;

    REQUIRE(win.IsVisible());
    REQUIRE(win.HasVisibleFlag());
    REQUIRE_FALSE(win.HasEnforcedCapture());
    REQUIRE_FALSE(win.IsHiddenBehindDialog());
    REQUIRE(win.IsCapturable());
    REQUIRE(screen.GetInvRect().IsEmpty());
    screen.Draw();

    win.HideBehindDialog(); // cannot not change rect

    REQUIRE_FALSE(win.IsVisible());
    REQUIRE(win.HasVisibleFlag());
    REQUIRE_FALSE(win.HasEnforcedCapture());
    REQUIRE(win.IsHiddenBehindDialog());
    REQUIRE_FALSE(win.IsCapturable());
    REQUIRE(screen.GetInvRect().IsEmpty()); // hide behind dialog only invalidates dialog
    screen.Draw();

    win.Hide();

    REQUIRE_FALSE(win.IsVisible());
    REQUIRE_FALSE(win.HasVisibleFlag());
    REQUIRE_FALSE(win.HasEnforcedCapture());
    REQUIRE_FALSE(win.IsHiddenBehindDialog()); // screen cleared this flag, because of Hide notifycation
    REQUIRE_FALSE(win.IsCapturable());
    REQUIRE(screen.GetInvRect() == win.GetRect());
    screen.Draw();

    win.SetEnforceCapture();

    REQUIRE_FALSE(win.IsVisible());
    REQUIRE_FALSE(win.HasVisibleFlag());
    REQUIRE(win.HasEnforcedCapture());
    REQUIRE_FALSE(win.IsHiddenBehindDialog());
    REQUIRE(win.IsCapturable());
}

TEST_CASE("Timed dialog tests", "[window]") {
    MockDisplay::Bind(MockDispBasic);
    MockDisplay::Instance().clear(COLOR_BLACK);
    MockScreen screen;
    Screens::Access()->Set(&screen); // instead of screen registration

    // initial screen check
    screen.BasicCheck();
    REQUIRE(screen.GetCapturedWindow() == &screen);

    SECTION("Screen timed dialog test") {
        static constexpr Rect16 RC2(20, 20, 20, 20);
        Rect16 rc = GENERATE(GuiDefaults::RectScreen, RC2);
        screen.Draw();
        screen.BasicCheck();
        REQUIRE(screen.GetCapturedWindow() == &screen);
        REQUIRE(screen.GetInvalidationRect().IsEmpty()); // cleared by draw

        MockDialogTimed dlg_timed(&screen, rc);
        REQUIRE(screen.GetInvRect() == rc);

        dlg_timed.Show(); // win is hidden by default
        REQUIRE(screen.GetInvRect() == rc); // unlike frame, screen invalidates on Show too, (multiple dialog priority, far shorter code)

        dlg_timed.Hide();
        REQUIRE(screen.GetInvRect() == rc);

        screen.Draw();
        REQUIRE(screen.GetInvalidationRect().IsEmpty()); // cleared by draw
    }

    hal_tick = 1000; // set opened on popup
    screen.ScreenEvent(&screen, GUI_event_t::LOOP, 0); // loop will initialize popup timeout
    hal_tick = 10000; // timeout popup
    screen.ScreenEvent(&screen, GUI_event_t::LOOP, 0); // loop event will unregister popup

    // at the end of all sections screen must be returned to its original state
    screen.BasicCheck();
    REQUIRE(screen.GetCapturedWindow() == &screen);
}
