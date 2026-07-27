#include "catch2/catch.hpp"

#include "guiapi/include/Rect16.h"

#include <vector>
#include <tuple>

/// Warning!
/// With yet unknown reason for us the method Catch::getResultCapture() returns nullptr in case the
/// benchmarks in CATCH2 are configured as enable. Please consider this issue when you'll decide to
/// write benchmark tests.
#define COMPARE_ARRAYS(lhs, rhs)                   compareArrays(Catch::getResultCapture().getCurrentTestName(), __LINE__, lhs, rhs)
#define COMPARE_ARRAYS_SIZE_FROM_SMALLER(lhs, rhs) compareArraysGetSizeFromSmaller(Catch::getResultCapture().getCurrentTestName(), __LINE__, lhs, rhs)

template <typename T>
void compareVectors(const std::string &test, unsigned line, const std::vector<T> &lhs, const std::vector<T> &rhs) {
    INFO("Test case [" << test << "] failed at line " << line); // Reported only if REQUIRE fails
    CHECK(lhs == rhs);
}

template <typename T, size_t N>
void compareArrays(const std::string &test, unsigned line, const std::array<T, N> &lhs, const std::array<T, N> &rhs) {
    std::vector<T> lv(lhs.begin(), lhs.end());
    std::vector<T> rv(rhs.begin(), rhs.end());
    compareVectors(test, line, lv, rv);
}

template <typename T, size_t N>
void compareArrays(const std::string &test, unsigned line, const T *lhs, const std::array<T, N> &rhs) {
    std::vector<T> lv(lhs, lhs + N);
    std::vector<T> rv(rhs.begin(), rhs.end());
    compareVectors(test, line, lv, rv);
}

template <typename T, size_t N>
void compareArrays(const std::string &test, unsigned line, const std::vector<T> &lhs, const std::array<T, N> &rhs) {
    std::vector<T> rv(rhs.begin(), rhs.end());
    compareVectors(test, line, lhs, rv);
}

template <typename T>
void compareArraysGetSizeFromSmaller(const std::string &test, unsigned line, const std::vector<T> &lhs, const std::vector<T> &rhs) {
    size_t min_len = std::min(rhs.size(), lhs.size());
    std::vector<T> lv(lhs.begin(), lhs.begin() + min_len);
    std::vector<T> rv(rhs.begin(), rhs.begin() + min_len);
    compareVectors(test, line, lv, rv);
}

template <typename T, size_t N>
void compareArraysGetSizeFromSmaller(const std::string &test, unsigned line, const std::vector<T> &lhs, const std::array<T, N> &rhs) {
    std::vector<T> rv(rhs.begin(), rhs.begin() + std::min(lhs.size(), N));
    compareVectors(test, line, lhs, rv);
}

template <typename T, size_t N>
void compareArraysGetSizeFromSmaller(const std::string &test, unsigned line, const std::array<T, N> &lhs, const std::vector<T> &rhs) {
    compareArraysGetSizeFromSmaller(test, line, rhs, lhs);
}

TEST_CASE("rectangle construc", "[rectangle]") {

    SECTION("topleft corner & width & height") {
        point_i16_t top_left = { 10, 20 };
        Rect16 r { top_left, 20, 40 };
        CHECK(r.Width() == 20);
        CHECK(r.Height() == 40);
    }

    SECTION("topleft corner & size") {
        point_i16_t top_left = { 10, 20 };
        size_ui16_t size = { 20, 40 };
        Rect16 r { top_left, size };
        CHECK(r.EndPoint().x == 30);
        CHECK(r.EndPoint().y == 60);
    }

    SECTION("empty box") {
        Rect16 r;
        CHECK(r.Width() == 0);
        CHECK(r.Height() == 0);
        CHECK(r.BeginPoint().x == 0);
        CHECK(r.BeginPoint().y == 0);
        CHECK(r.EndPoint().x == 0);
        CHECK(r.EndPoint().y == 0);
    }

    SECTION("by coordinates") {
        Rect16 r { 10, 20, 10, 10 };
        CHECK(r.BeginPoint().x == 10);
        CHECK(r.BeginPoint().y == 20);
        CHECK(r.Width() == 10);
        CHECK(r.Height() == 10);
    }

    SECTION("copy construct") {
        Rect16 q { 10, 20, 20, 40 };
        Rect16 r { q };
        CHECK(r.BeginPoint().x == 10);
        CHECK(r.BeginPoint().y == 20);
        CHECK(r.Width() == 20);
        CHECK(r.Height() == 40);
    }

    SECTION("2 points") {
        point_i16_t p0 = { 10, 20 };
        point_i16_t p1 = { 32, 48 };
        point_i16_t p2 = { 2, 48 };

        Rect16 r0 { p0, p1 };
        CHECK(r0.TopLeft().x == 10);
        CHECK(r0.TopLeft().y == 20);
        CHECK(r0.BottomRight().x == 32);
        CHECK(r0.BottomRight().y == 48);

        // same 2 points in different order must create same rect
        Rect16 r1 { p1, p0 };
        CHECK(r0 == r1);

        // p0 top-right
        // p2 bottom-left
        Rect16 r2 { p0, p2 };
        CHECK(r2.Top() == p0.y);
        CHECK(r2.Left() == p2.x);
        CHECK(r2.BottomRight().x == p0.x);
        CHECK(r2.BottomRight().y == p2.y);

        // same 2 points in different order must create same rect
        Rect16 r3 { p2, p0 };
        CHECK(r2 == r3);
    }

    SECTION("Top Left Bottom and Right accessors") {

        point_i16_t top_left, bot_right;

        std::tie(top_left, bot_right) = GENERATE(
            std::make_tuple<point_i16_t, point_i16_t>({ 0, 0 }, { 10, 20 }),
            std::make_tuple<point_i16_t, point_i16_t>({ 2, 4 }, { 10, 20 }),
            std::make_tuple<point_i16_t, point_i16_t>({ -10, -20 }, { 10, 20 }),
            std::make_tuple<point_i16_t, point_i16_t>({ -100, -200 }, { 10, 20 }));

        Rect16 r { top_left, bot_right };
        CHECK(r.Top() == top_left.y);
        CHECK(r.Left() == top_left.x);
        CHECK(r.Bottom() == bot_right.y);
        CHECK(r.Right() == bot_right.x);
    }

    // SECTION("by coordinates & wrong x") {
    //     Rect16 r { 10, 20, 0, 40 };
    //     CHECK(r.Width() == 0);
    //     CHECK(r.Height() != 20);
    // }

    // SECTION("by coordinates & wrong y") {
    //     Rect16 r { 10, 20, 20, 10 };
    //     CHECK(r.Width() != 10);
    //     CHECK(r.Height() != 0);
    // }

    SECTION("copy & shift") {
        Rect16 r, expected;
        ShiftDir_t dir;
        uint16_t offset;

        std::tie(r, dir, offset, expected) = GENERATE(
            std::make_tuple<Rect16, ShiftDir_t, uint16_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Left, 20, { -10, 10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, uint16_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Left, 10, { 0, 10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, uint16_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Left, 0, { 10, 10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, uint16_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Right, 20, { 30, 10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, uint16_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Right, 10, { 20, 10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, uint16_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Right, 0, { 10, 10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, uint16_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Top, 20, { 10, -10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, uint16_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Top, 10, { 10, 0, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, uint16_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Top, 0, { 10, 10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, uint16_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Bottom, 20, { 10, 30, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, uint16_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Bottom, 10, { 10, 20, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, uint16_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Bottom, 0, { 10, 10, 30, 30 }));

        Rect16 res { r, dir, offset };

        CHECK(res.Width() == expected.Width());
        CHECK(res.Height() == expected.Height());
        CHECK(res.BeginPoint().x == expected.BeginPoint().x);
        CHECK(res.BeginPoint().y == expected.BeginPoint().y);
        CHECK(res.EndPoint().x == expected.EndPoint().x);
        CHECK(res.EndPoint().y == expected.EndPoint().y);
    }

    SECTION("copy & shift no offset and CalculateShift") {
        Rect16 r, expected;
        ShiftDir_t dir;

        std::tie(r, dir, expected) = GENERATE(
            std::make_tuple<Rect16, ShiftDir_t, Rect16>({ -10, 10, 30, 30 }, ShiftDir_t::Left, { -40, 10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Left, { -20, 10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, Rect16>({ 40, 10, 30, 30 }, ShiftDir_t::Left, { 10, 10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, Rect16>({ -10, 10, 30, 30 }, ShiftDir_t::Right, { 20, 10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Right, { 40, 10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, Rect16>({ -40, 10, 30, 30 }, ShiftDir_t::Right, { -10, 10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, Rect16>({ 10, -10, 30, 30 }, ShiftDir_t::Top, { 10, -40, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Top, { 10, -20, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, Rect16>({ 10, 40, 30, 30 }, ShiftDir_t::Top, { 10, 10, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, Rect16>({ 10, -10, 30, 30 }, ShiftDir_t::Bottom, { 10, 20, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, Rect16>({ 10, 10, 30, 30 }, ShiftDir_t::Bottom, { 10, 40, 30, 30 }),
            std::make_tuple<Rect16, ShiftDir_t, Rect16>({ 10, -40, 30, 30 }, ShiftDir_t::Bottom, { 10, -10, 30, 30 }));

        // internally use CalculateShift
        Rect16 res { r, dir };

        CHECK(res.Width() == expected.Width());
        CHECK(res.Height() == expected.Height());
        CHECK(res.BeginPoint().x == expected.BeginPoint().x);
        CHECK(res.BeginPoint().y == expected.BeginPoint().y);
        CHECK(res.EndPoint().x == expected.EndPoint().x);
        CHECK(res.EndPoint().y == expected.EndPoint().y);
    }
}

TEST_CASE("Swap") {
    Rect16 unSwapped = GENERATE(
        Rect16({ -10, 10, 30, 40 }),
        Rect16({ 10, 10, 30, 40 }),
        Rect16({ -10, 10, 30, 30 }),
        Rect16({ 0, 10, 30, 40 }),
        Rect16({ -10, 0, 40, 30 }));

    Rect16 swapped = unSwapped;
    swapped.SwapXY();

    CHECK(swapped.Width() == unSwapped.Height());
    CHECK(swapped.Height() == unSwapped.Width());
    CHECK(swapped.BeginPoint().x == unSwapped.BeginPoint().y);
    CHECK(swapped.BeginPoint().y == unSwapped.BeginPoint().x);
    CHECK(swapped.EndPoint().x == unSwapped.EndPoint().y);
    CHECK(swapped.EndPoint().y == unSwapped.EndPoint().x);
}

TEST_CASE("rectangle mirror", "[rectangle]") {
    Rect16 original, mirrored, swapped, swapped_mirrored;
    int16_t mirror_point;
    std::tie(original, mirror_point, mirrored) = GENERATE(
        std::make_tuple<Rect16, int16_t, Rect16>({ 0, 10, 30, 40 }, 0, { -30, 10, 30, 40 }),
        std::make_tuple<Rect16, int16_t, Rect16>({ 0, 10, 30, 40 }, 5, { -20, 10, 30, 40 }),
        std::make_tuple<Rect16, int16_t, Rect16>({ 0, 10, 30, 40 }, -5, { -40, 10, 30, 40 }),

        std::make_tuple<Rect16, int16_t, Rect16>({ 10, 10, 30, 40 }, 0, { -40, 10, 30, 40 }),
        std::make_tuple<Rect16, int16_t, Rect16>({ 10, 10, 30, 40 }, 5, { -30, 10, 30, 40 }),
        std::make_tuple<Rect16, int16_t, Rect16>({ 10, 10, 30, 40 }, -5, { -50, 10, 30, 40 }),

        std::make_tuple<Rect16, int16_t, Rect16>({ -10, 10, 30, 40 }, 0, { -20, 10, 30, 40 }),
        std::make_tuple<Rect16, int16_t, Rect16>({ -10, 10, 30, 40 }, 5, { -10, 10, 30, 40 }),
        std::make_tuple<Rect16, int16_t, Rect16>({ -10, 10, 30, 40 }, -5, { -30, 10, 30, 40 }),

        std::make_tuple<Rect16, int16_t, Rect16>({ 10, 10, 30, 40 }, 40, { 40, 10, 30, 40 }), // mirror at the end of rect
        std::make_tuple<Rect16, int16_t, Rect16>({ 10, 10, 30, 40 }, 100, { 160, 10, 30, 40 }),
        std::make_tuple<Rect16, int16_t, Rect16>({ -10, 10, 30, 40 }, 20, { 20, 10, 30, 40 }), // mirror at the end of rect
        std::make_tuple<Rect16, int16_t, Rect16>({ -10, 10, 30, 40 }, -100, { -190 - 30, 10, 30, 40 }));

    Rect16 res = original;
    res.MirrorX(mirror_point);
    CHECK(res == mirrored);

    Rect16 res_swapped = original;
    res_swapped.SwapXY();
    res_swapped.MirrorY(mirror_point);
    swapped_mirrored = mirrored;
    swapped_mirrored.SwapXY();
    CHECK(res_swapped == swapped_mirrored);
}

TEST_CASE("rectangle Contain point and IsEmpty", "[rectangle]") {
    Rect16 r;
    bool empty;
    std::tie(r, empty) = GENERATE(
        std::make_tuple<Rect16, bool>({ 0, 0, 30, 40 }, false),
        std::make_tuple<Rect16, bool>({ -30, -40, 30, 40 }, false), // ends 0,0
        std::make_tuple<Rect16, bool>({ 10, 10, 30, 40 }, false),
        std::make_tuple<Rect16, bool>({ -100, -100, 30, 40 }, false),
        std::make_tuple<Rect16, bool>({ 0, 0, 0, 0 }, true),
        std::make_tuple<Rect16, bool>({ 10, 10, 0, 10 }, true),
        std::make_tuple<Rect16, bool>({ 10, 10, 10, 0 }, true),
        std::make_tuple<Rect16, bool>({ 10, 10, 0, 0 }, true));

    // first must make sure IsEmptyWorks
    CHECK(r.IsEmpty() == empty);

    // empty does not contain anything
    CHECK_FALSE(r.Contain(r.TopLeft()) == r.IsEmpty());
    CHECK_FALSE(r.Contain(r.BottomRight()) == r.IsEmpty());
    CHECK_FALSE(r.Contain(r.EndPoint()));
    CHECK_FALSE(r.Contain(r.TopEndPoint()));
    CHECK_FALSE(r.Contain(r.LeftEndPoint()));
}

TEST_CASE("rectangle intersection", "[rectangle]") {
    Rect16 l, r, expected;
    std::tie(l, r, expected) = GENERATE(
        std::make_tuple<Rect16, Rect16, Rect16>({ 10, 10, 30, 30 }, { 20, 20, 40, 40 }, { 20, 20, 20, 20 }),
        std::make_tuple<Rect16, Rect16, Rect16>({ 20, 20, 40, 40 }, { 10, 10, 30, 30 }, { 20, 20, 20, 20 }),
        std::make_tuple<Rect16, Rect16, Rect16>({ 10, 10, 30, 30 }, { 20, 0, 40, 40 }, { 20, 10, 20, 30 }),
        std::make_tuple<Rect16, Rect16, Rect16>({ 10, 10, 30, 30 }, { 11, 10, 31, 20 }, { 11, 10, 29, 20 }),
        std::make_tuple<Rect16, Rect16, Rect16>({ 0, 0, 30, 30 }, { 1, 1, 29, 29 }, { 1, 1, 29, 29 }),
        std::make_tuple<Rect16, Rect16, Rect16>({ 0, 20, 30, 30 }, { 10, 0, 40, 22 }, { 10, 20, 20, 2 }),
        std::make_tuple<Rect16, Rect16, Rect16>({ 0, 20, 30, 30 }, { 0, 20, 30, 30 }, { 0, 20, 30, 30 }),
        std::make_tuple<Rect16, Rect16, Rect16>({ 10, 10, 20, 20 }, { 30, 30, 40, 40 }, { 0, 0, 0, 0 }),
        std::make_tuple<Rect16, Rect16, Rect16>({ 10, 10, 20, 20 }, { 15, 15, 0, 0 }, { 0, 0, 0, 0 }),
        std::make_tuple<Rect16, Rect16, Rect16>({ 10, 10, 0, 0 }, { 10, 10, 40, 40 }, { 0, 0, 0, 0 }),
        std::make_tuple<Rect16, Rect16, Rect16>({ 10, 10, 1, 10 }, { 10, 10, 10, 1 }, { 10, 10, 1, 1 }));

    Rect16 res = l.Intersection(r);

    CHECK(res.Width() == expected.Width());
    CHECK(res.Height() == expected.Height());
    CHECK(res.BeginPoint().x == expected.BeginPoint().x);
    CHECK(res.BeginPoint().y == expected.BeginPoint().y);
    CHECK(res.EndPoint().x == expected.EndPoint().x);
    CHECK(res.EndPoint().y == expected.EndPoint().y);
}

TEST_CASE("rectangles has intersection", "[rectangle]") {
    Rect16 l, r;
    bool expected;
    std::tie(l, r, expected) = GENERATE(
        std::make_tuple<Rect16, Rect16, bool>({ 10, 10, 30, 30 }, { 20, 20, 40, 40 }, true),
        std::make_tuple<Rect16, Rect16, bool>({ 20, 20, 40, 40 }, { 10, 10, 30, 30 }, true),
        std::make_tuple<Rect16, Rect16, bool>({ 10, 10, 30, 30 }, { 20, 0, 40, 40 }, true),
        std::make_tuple<Rect16, Rect16, bool>({ 10, 10, 30, 30 }, { 11, 10, 31, 20 }, true),
        std::make_tuple<Rect16, Rect16, bool>({ 0, 0, 30, 30 }, { 1, 1, 29, 29 }, true),
        std::make_tuple<Rect16, Rect16, bool>({ 0, 20, 30, 30 }, { 10, 0, 40, 22 }, true),
        std::make_tuple<Rect16, Rect16, bool>({ 10, 10, 20, 20 }, { 30, 30, 40, 40 }, false));

    CHECK(l.HasIntersection(r) == expected);
}

TEST_CASE("rectangles is subrectangle", "[rectangle]") {
    Rect16 l, r;
    bool expected;
    std::tie(l, r, expected) = GENERATE(
        std::make_tuple<Rect16, Rect16, bool>({ 10, 10, 30, 30 }, { 20, 20, 40, 40 }, false),
        std::make_tuple<Rect16, Rect16, bool>({ 20, 20, 40, 40 }, { 10, 10, 30, 30 }, false),
        std::make_tuple<Rect16, Rect16, bool>({ 10, 10, 30, 30 }, { 0, 0, 40, 40 }, false),
        std::make_tuple<Rect16, Rect16, bool>({ 10, 10, 30, 30 }, { 11, 10, 31, 20 }, false),
        std::make_tuple<Rect16, Rect16, bool>({ 0, 0, 30, 30 }, { 1, 1, 29, 29 }, true),
        std::make_tuple<Rect16, Rect16, bool>({ 0, 20, 30, 30 }, { 10, 0, 40, 22 }, false),
        std::make_tuple<Rect16, Rect16, bool>({ 0, 20, 30, 30 }, { 0, 20, 30, 30 }, true),
        std::make_tuple<Rect16, Rect16, bool>({ 10, 10, 20, 20 }, { 20, 20, 40, 40 }, false));

    CHECK(l.Contain(r) == expected);
}

TEST_CASE("rectangle point arithmetic", "[rectangle]") {
    SECTION("operator=") {
        point_i16_t point = GENERATE(point_i16_t({ 0, 0 }), point_i16_t({ 10, 10 }), point_i16_t({ -2, 8 }), point_i16_t({ -33, 0 }));
        Rect16 r = GENERATE( // this operation does not have meaning on empty rect -  must not be empty
            Rect16({ 0, 0, 1, 1 }),
            Rect16({ 10, 10, 5, 8 }),
            Rect16({ -2, 0, 3, 2 }));
        r = point;
        CHECK(r.TopLeft() == point);
    }

    SECTION("operator+") {
        // it use internally +=
        Rect16 r;
        point_i16_t point, expected;
        std::tie(r, point, expected) = GENERATE(
            std::make_tuple<Rect16, point_i16_t, point_i16_t>({ 0, 0, 30, 30 }, { 0, 2 }, { 0, 2 }),
            std::make_tuple<Rect16, point_i16_t, point_i16_t>({ 0, 20, 30, 30 }, { 6, -5 }, { 6, 15 }),
            std::make_tuple<Rect16, point_i16_t, point_i16_t>({ -5, 20, 30, 30 }, { -3, -30 }, { -8, -10 }),
            std::make_tuple<Rect16, point_i16_t, point_i16_t>({ -6, -1, 30, 30 }, { 20, 20 }, { 14, 19 }));
        CHECK((r + point).TopLeft() == expected);
    }

    SECTION("operator-") {
        // it use internally -=
        Rect16 r;
        point_i16_t point, expected;
        std::tie(r, point, expected) = GENERATE(
            std::make_tuple<Rect16, point_i16_t, point_i16_t>({ 0, 0, 30, 30 }, { 0, 2 }, { 0, -2 }),
            std::make_tuple<Rect16, point_i16_t, point_i16_t>({ 0, 20, 30, 30 }, { 6, -5 }, { -6, 25 }),
            std::make_tuple<Rect16, point_i16_t, point_i16_t>({ -5, 20, 30, 30 }, { -3, -30 }, { -2, 50 }),
            std::make_tuple<Rect16, point_i16_t, point_i16_t>({ -6, -1, 30, 30 }, { 20, 20 }, { -26, -21 }));
        CHECK((r - point).TopLeft() == expected);
    }

    SECTION("operators == and !=") {
        // it use internally -=
        Rect16 r0, r1;
        bool equal;

        std::tie(r0, r1, equal) = GENERATE(
            std::make_tuple<Rect16, Rect16, bool>({ 0, 0, 0, 0 }, { 0, 0, 0, 0 }, true),
            std::make_tuple<Rect16, Rect16, bool>({ 0, 0, 30, 30 }, { 0, 0, 30, 30 }, true),
            std::make_tuple<Rect16, Rect16, bool>({ 0, 20, 30, 30 }, { 0, 20, 30, 30 }, true),
            std::make_tuple<Rect16, Rect16, bool>({ -5, 20, 30, 30 }, { -5, 20, 30, 30 }, true),
            std::make_tuple<Rect16, Rect16, bool>({ -6, -1, 30, 30 }, { -6, -1, 30, 30 }, true),

            // x is wrong
            std::make_tuple<Rect16, Rect16, bool>({ 1, 0, 0, 0 }, { 0, 0, 0, 0 }, true), // all empty rectangles are equal
            std::make_tuple<Rect16, Rect16, bool>({ 22, 0, 30, 30 }, { 0, 0, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ 89, 20, 30, 30 }, { 0, 20, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ 0, 20, 30, 30 }, { -5, 20, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ -4, -1, 30, 30 }, { -6, -1, 30, 30 }, false),

            // y is wrong
            std::make_tuple<Rect16, Rect16, bool>({ 0, -20, 0, 0 }, { 0, 0, 0, 0 }, true), // all empty rectangles are equal
            std::make_tuple<Rect16, Rect16, bool>({ 0, 20, 30, 30 }, { 0, 0, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ 0, 0, 30, 30 }, { 0, 20, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ -5, 0, 30, 30 }, { -5, 20, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ -6, -21, 30, 30 }, { -6, -1, 30, 30 }, false),

            // w is wrong
            std::make_tuple<Rect16, Rect16, bool>({ 0, 0, 10, 0 }, { 0, 0, 0, 0 }, true), // all empty rectangles are equal
            std::make_tuple<Rect16, Rect16, bool>({ 0, 0, 0, 30 }, { 0, 0, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ 0, 20, 10, 30 }, { 0, 20, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ -5, 20, 300, 30 }, { -5, 20, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ -6, -1, 0, 30 }, { -6, -1, 30, 30 }, false),

            // h is wrong
            std::make_tuple<Rect16, Rect16, bool>({ 0, 0, 0, 110 }, { 0, 0, 0, 0 }, true), // all empty rectangles are equal
            std::make_tuple<Rect16, Rect16, bool>({ 0, 0, 30, 0 }, { 0, 0, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ 0, 20, 30, 3 }, { 0, 20, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ -5, 20, 30, 322 }, { -5, 20, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ -6, -1, 30, 1 }, { -6, -1, 30, 30 }, false),

            // multiple wrong values
            std::make_tuple<Rect16, Rect16, bool>({ 0, 0, 3, 0 }, { 0, 0, 0, 1 }, true), // all empty rectangles are equal
            std::make_tuple<Rect16, Rect16, bool>({ 1, 1, 1, 1 }, { 0, 0, 0, 0 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ 0, 0, 3, 6 }, { 0, 0, 0, 0 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ -3, -3, 30, 30 }, { 0, 0, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ 0, 20, 3, 3 }, { 0, 20, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ -5, 2, 3, 3 }, { -5, 20, 30, 30 }, false),
            std::make_tuple<Rect16, Rect16, bool>({ -60, -10, 3, 30 }, { -6, -1, 30, 30 }, false));

        CHECK((r0 == r1) == equal);
        CHECK((r0 != r1) != equal);
    }
}

TEST_CASE("rectangle LimitSize", "[rectangle]") {
    SECTION("not empty") {
        Rect16 r, expected;
        size_ui16_t limit;
        std::tie(r, limit, expected) = GENERATE(
            std::make_tuple<Rect16, size_ui16_t, Rect16>({ 0, 0, 30, 30 }, { 2, 2 }, { 0, 0, 2, 2 }),
            std::make_tuple<Rect16, size_ui16_t, Rect16>({ 0, 20, 80, 40 }, { 6, 1000 }, { 0, 20, 6, 40 }),
            std::make_tuple<Rect16, size_ui16_t, Rect16>({ -5, 20, 20, 1 }, { 20, 1 }, { -5, 20, 20, 1 }),
            std::make_tuple<Rect16, size_ui16_t, Rect16>({ -6, -1, 100, 3 }, { 99, 3 }, { -6, -1, 99, 3 }));

        Rect16 r_sw = r;
        size_ui16_t limit_sw = { limit.h, limit.w };
        Rect16 expected_sw = expected;
        r_sw.SwapXY();
        expected_sw.SwapXY();

        r.LimitSize(limit);
        CHECK(r == expected);

        r_sw.LimitSize(limit_sw);
        CHECK(r_sw == expected_sw);
    }
    SECTION("empty") {
        Rect16 r;
        size_ui16_t limit;
        std::tie(r, limit) = GENERATE(
            std::make_tuple<Rect16, size_ui16_t>({ 0, 0, 0, 0 }, { 0, 0 }),
            std::make_tuple<Rect16, size_ui16_t>({ 0, 0, 0, 30 }, { 2, 2 }),
            std::make_tuple<Rect16, size_ui16_t>({ 0, 20, 80, 40 }, { 6, 0 }),
            std::make_tuple<Rect16, size_ui16_t>({ -5, 20, 0, 0 }, { 20, 1 }),
            std::make_tuple<Rect16, size_ui16_t>({ -6, -1, 100, 3 }, { 0, 0 }));

        r.LimitSize(limit);
        CHECK(r.IsEmpty());
    }
}
