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

TEST_CASE("rectangle Transform", "[rectangle]") {
    SECTION("not empty") {
        Rect16 r, target, expected;
        std::tie(r, target, expected) = GENERATE(
            std::make_tuple<Rect16, Rect16, Rect16>({ 0, 0, 30, 30 }, { 2, 3, 100, 100 }, { 2, 3, 30, 30 }), // fits
            std::make_tuple<Rect16, Rect16, Rect16>({ 0, 2, 80, 40 }, { 1, 2, 5, 5 }, { 1, 4, 5, 3 }), // does not fit
            std::make_tuple<Rect16, Rect16, Rect16>({ 5, 20, 20, 1 }, { 20, -3, 6, 200 }, { 25, 17, 1, 1 }), // width does not fit
            std::make_tuple<Rect16, Rect16, Rect16>({ 10, 1, 100, 3 }, { -100, 3, 1000, 2 }, { -90, 4, 100, 1 }), // height does not fit
            // rect with negative coords is cut
            // data for X, Y is made by SwapXY
            std::make_tuple<Rect16, Rect16, Rect16>({ -1, 0, 30, 30 }, { 2, 3, 100, 100 }, { 2, 3, 29, 30 }), // negative x
            std::make_tuple<Rect16, Rect16, Rect16>({ -1, 8, 30, 30 }, { 2, 3, 10, 100 }, { 2, 11, 10, 30 }), // negative x, does not fit into target
            std::make_tuple<Rect16, Rect16, Rect16>({ -22, 4, 30, 30 }, { 2, 3, 10, 100 }, { 2, 7, 8, 30 }), // negative x, would not fit into target, but fits after negative coord cut
            std::make_tuple<Rect16, Rect16, Rect16>({ -22, 2, 30, 30 }, { 2, 3, 1, 100 }, { 2, 5, 1, 30 }), // negative x, would not fit into target, and still does not fit even after negative coord cut
            // both X and Y negative
            std::make_tuple<Rect16, Rect16, Rect16>({ -1, -1, 10, 6 }, { 2, 3, 100, 100 }, { 2, 3, 9, 5 }),
            std::make_tuple<Rect16, Rect16, Rect16>({ -1, -4, 20, 7 }, { 2, 3, 10, 100 }, { 2, 3, 10, 3 }), // X does not fit into target
            std::make_tuple<Rect16, Rect16, Rect16>({ -22, -2, 30, 8 }, { 2, 3, 10, 100 }, { 2, 3, 8, 6 }) // X would not fit into target, but fits after negative coord cut
        );

        Rect16 r_sw = r;
        Rect16 target_sw = target;
        Rect16 expected_sw = expected;
        r_sw.SwapXY();
        target_sw.SwapXY();
        expected_sw.SwapXY();

        r.Transform(target);
        CHECK(r == expected);

        r_sw.Transform(target_sw);
        CHECK(r_sw == expected_sw);
    }
}

TEST_CASE("rectangle union", "[rectangle]") {
    SECTION("single rectangle") {
        // it also tests operators + and += since Union use them
        Rect16 l, r, expected;
        std::tie(l, r, expected) = GENERATE(
            std::make_tuple<Rect16, Rect16, Rect16>({ 0, 0, 20, 20 }, { 20, 20, 40, 40 }, { 0, 0, 60, 60 }),
            std::make_tuple<Rect16, Rect16, Rect16>({ 0, 0, 40, 40 }, { 20, 20, 20, 20 }, { 0, 0, 40, 40 }),
            std::make_tuple<Rect16, Rect16, Rect16>({ 10, 10, 30, 30 }, { 20, 20, 10, 10 }, { 10, 10, 30, 30 }),
            std::make_tuple<Rect16, Rect16, Rect16>({ -21, -22, 10, 10 }, { 0, 0, 25, 30 }, { -21, -22, 46, 52 }),
            std::make_tuple<Rect16, Rect16, Rect16>({ -20, -20, 10, 10 }, { -40, -40, 10, 10 }, { -40, -40, 30, 30 }));

        Rect16 res = l.Union(r);

        CHECK(res.Width() == expected.Width());
        CHECK(res.Height() == expected.Height());
        CHECK(res.BeginPoint().x == expected.BeginPoint().x);
        CHECK(res.BeginPoint().y == expected.BeginPoint().y);
        CHECK(res.EndPoint().x == expected.EndPoint().x);
        CHECK(res.EndPoint().y == expected.EndPoint().y);
    }

    SECTION("sequence") {
        using Sequence = std::array<Rect16, 8>;
        Sequence s;
        Rect16 l, expected;

        std::tie(l, s, expected) = GENERATE(
            std::make_tuple<Rect16, Sequence, Rect16>({ 0, 0, 10, 10 }, { {} }, { 0, 0, 10, 10 }),
            std::make_tuple<Rect16, Sequence, Rect16>({ 0, 0, 10, 10 }, { { {} } }, { 0, 0, 10, 10 }),
            std::make_tuple<Rect16, Sequence, Rect16>({ 0, 0, 20, 20 }, { { { 20, 20, 40, 40 } } }, { 0, 0, 60, 60 }),
            std::make_tuple<Rect16, Sequence, Rect16>({ 0, 0, 20, 20 }, { { { 0, 20, 20, 40 }, { 20, 0, 40, 20 } } }, { 0, 0, 60, 60 }),
            std::make_tuple<Rect16, Sequence, Rect16>({ 10, 10, 20, 20 }, { { { 0, 0, 10, 10 }, { 0, 20, 20, 40 }, { 20, 0, 40, 20 } } }, { 0, 0, 60, 60 }),
            std::make_tuple<Rect16, Sequence, Rect16>({ -21, -22, 10, 10 }, { { { 0, 0, 25, 30 } } }, { -21, -22, 46, 52 }),
            std::make_tuple<Rect16, Sequence, Rect16>({ -20, -20, 10, 10 }, { { { -40, -40, 10, 10 } } }, { -40, -40, 30, 30 }));

        Rect16 res = l.Union(s);

        CHECK(res.Width() == expected.Width());
        CHECK(res.Height() == expected.Height());
        CHECK(res.BeginPoint().x == expected.BeginPoint().x);
        CHECK(res.BeginPoint().y == expected.BeginPoint().y);
        CHECK(res.EndPoint().x == expected.EndPoint().x);
        CHECK(res.EndPoint().y == expected.EndPoint().y);
    }
}

TEST_CASE("rectangle Align", "[rectangle]") {
    Rect16 toBeAligned, alignRC;
    Align_t align = Align_t::Center();
    point_i16_t expected_point;
    size_ui16_t sz;
    SECTION("precise fit") {
        sz = { 25, 52 }; // precise fit, all rects has same size

        std::tie(toBeAligned, alignRC, align) = std::make_tuple<Rect16, Rect16, Align_t>(
            Rect16(
                GENERATE(point_i16_t({ 0, 0 }), point_i16_t({ -10, 30 }), point_i16_t({ 110, 0 })) // some X Y coords
                ,
                sz),
            Rect16(
                GENERATE(point_i16_t({ 0, 0 }), point_i16_t({ 10, -30 }), point_i16_t({ 333, 222 })) // some X Y coords
                ,
                sz),
            Align_t(
                GENERATE(Align_t(Align_t::vertical::top), Align_t(Align_t::horizontal::center), Align_t(Align_t::vertical::center, Align_t::horizontal::center))) // precise fit, align should not matter
        );

        toBeAligned.Align(alignRC, align);

        CHECK(toBeAligned == alignRC); // alignRC precisely fits in toBeAligned
    }

    SECTION("normal use") {
        std::tie(toBeAligned, alignRC, align, expected_point) = GENERATE(
            std::make_tuple<Rect16, Rect16, Align_t, point_i16_t>({ 0, 0, 0, 0 }, { 0, 0, 0, 0 }, Align_t(Align_t::vertical::top, Align_t::horizontal::left), { 0, 0 }), // zero aligned via zero aligns to zero
            std::make_tuple<Rect16, Rect16, Align_t, point_i16_t>({ 0, 0, 10, 20 }, { 3, 5, 100, 100 }, Align_t(Align_t::vertical::top, Align_t::horizontal::left), { 3, 5 }),
            std::make_tuple<Rect16, Rect16, Align_t, point_i16_t>({ 666, 0, 10, 20 }, { 0, 0, 100, 100 }, Align_t(Align_t::vertical::top, Align_t::horizontal::left), { 0, 0 }),
            std::make_tuple<Rect16, Rect16, Align_t, point_i16_t>({ 0, 666, 3, 5 }, { 1, -1, 5, 9 }, Align_t(Align_t::vertical::center, Align_t::horizontal::center), { 2, 1 }),
            std::make_tuple<Rect16, Rect16, Align_t, point_i16_t>({ 0, 0, 100, 20 }, { 0, 0, 10, 10 }, Align_t(Align_t::vertical::top, Align_t::horizontal::left), { 0, 0 }), // does not fit .. should not matter for top left
            std::make_tuple<Rect16, Rect16, Align_t, point_i16_t>({ 666, 0, 30, 20 }, { 0, 0, 10, 10 }, Align_t(Align_t::vertical::bottom, Align_t::horizontal::right), { -20, -10 }));

        sz = toBeAligned.Size();
        toBeAligned.Align(alignRC, align);

        CHECK(toBeAligned == Rect16(expected_point, sz));
    }
}

TEST_CASE("rectangle add padding", "[rectangle]") {
    Rect16 l, expected;
    padding_ui8_t p;

    std::tie(l, p, expected) = GENERATE(
        std::make_tuple<Rect16, padding_ui8_t, Rect16>({ 0, 0, 20, 20 }, { 0, 0, 0, 0 }, { 0, 0, 20, 20 }),
        std::make_tuple<Rect16, padding_ui8_t, Rect16>({ 0, 0, 40, 40 }, { 20, 10, 30, 40 }, { -20, -10, 90, 90 }),
        std::make_tuple<Rect16, padding_ui8_t, Rect16>({ 10, 10, 30, 30 }, { 20, 0, 40, 0 }, { -10, 10, 90, 30 }),
        std::make_tuple<Rect16, padding_ui8_t, Rect16>({ 10, 10, 30, 30 }, { 20, 0, 0, 0 }, { -10, 10, 50, 30 }));

    l.AddPadding(p);

    CHECK(l.Width() == expected.Width());
    CHECK(l.Height() == expected.Height());
    CHECK(l.BeginPoint().x == expected.BeginPoint().x);
    CHECK(l.BeginPoint().y == expected.BeginPoint().y);
    CHECK(l.EndPoint().x == expected.EndPoint().x);
    CHECK(l.EndPoint().y == expected.EndPoint().y);
}

TEST_CASE("rectangle cut padding", "[rectangle]") {
    Rect16 l, expected;
    padding_ui8_t p;

    std::tie(l, p, expected) = GENERATE(
        std::make_tuple<Rect16, padding_ui8_t, Rect16>({ 0, 0, 20, 20 }, { 0, 0, 0, 0 }, { 0, 0, 20, 20 }),
        std::make_tuple<Rect16, padding_ui8_t, Rect16>({ 0, 0, 40, 40 }, { 20, 10, 30, 40 }, { 0, 0, 0, 0 }),
        std::make_tuple<Rect16, padding_ui8_t, Rect16>({ 10, 10, 40, 30 }, { 10, 0, 10, 0 }, { 20, 10, 20, 30 }),
        std::make_tuple<Rect16, padding_ui8_t, Rect16>({ 10, 10, 30, 30 }, { 10, 0, 10, 0 }, { 20, 10, 10, 30 }),
        std::make_tuple<Rect16, padding_ui8_t, Rect16>({ 10, 10, 30, 30 }, { 0, 10, 0, 10 }, { 10, 20, 30, 10 }),
        std::make_tuple<Rect16, padding_ui8_t, Rect16>({ 10, 10, 70, 70 }, { 10, 10, 20, 30 }, { 20, 20, 40, 30 }),
        std::make_tuple<Rect16, padding_ui8_t, Rect16>({ 10, 10, 40, 30 }, { 20, 0, 0, 0 }, { 30, 10, 20, 30 }));

    l.CutPadding(p);

    CHECK(l.Width() == expected.Width());
    CHECK(l.Height() == expected.Height());
    CHECK(l.BeginPoint().x == expected.BeginPoint().x);
    CHECK(l.BeginPoint().y == expected.BeginPoint().y);
    CHECK(l.EndPoint().x == expected.EndPoint().x);
    CHECK(l.EndPoint().y == expected.EndPoint().y);
}

TEST_CASE("rectangle Merge", "[rectangle]") {
    SECTION("static impl") {
        using Sequence = std::array<Rect16, 8>;
        Sequence s;
        Rect16 expected;

        std::tie(s, expected) = GENERATE(
            std::make_tuple<Sequence, Rect16>({ {} }, { 0, 0, 0, 0 }),
            std::make_tuple<Sequence, Rect16>({ { { 0, 0, 20, 20 },
                                                  { 20, 20, 40, 40 } } },
                { 0, 0, 60, 60 }),
            std::make_tuple<Sequence, Rect16>({ { { 0, 0, 20, 20 },
                                                  { 0, 20, 20, 40 },
                                                  { 20, 0, 40, 20 } } },
                { 0, 0, 60, 60 }),
            std::make_tuple<Sequence, Rect16>({ { { 10, 10, 20, 20 },
                                                  { 0, 0, 10, 10 },
                                                  { 0, 20, 20, 40 },
                                                  { 20, 0, 40, 20 } } },
                { 0, 0, 60, 60 }),
            std::make_tuple<Sequence, Rect16>({ { { -20, -20, 10, 10 },
                                                  { 0, 0, 20, 20 } } },
                { -20, -20, 40, 40 }));

        Rect16 res = Rect16::Merge(s);

        CHECK(res.Width() == expected.Width());
        CHECK(res.Height() == expected.Height());
        CHECK(res.BeginPoint().x == expected.BeginPoint().x);
        CHECK(res.BeginPoint().y == expected.BeginPoint().y);
        CHECK(res.EndPoint().x == expected.EndPoint().x);
        CHECK(res.EndPoint().y == expected.EndPoint().y);
    }
}

TEST_CASE("rectangle Merge_ParamPack", "[rectangle]") {
    SECTION("static impl") {
        Rect16 res;
        Rect16 expected;

        std::tie(res, expected) = GENERATE(
            std::make_tuple<Rect16, Rect16>(Rect16::Merge_ParamPack(Rect16()), { 0, 0, 0, 0 }),
            std::make_tuple<Rect16, Rect16>(Rect16::Merge_ParamPack(Rect16(0, 0, 20, 20), Rect16(20, 20, 40, 40)), { 0, 0, 60, 60 }),
            std::make_tuple<Rect16, Rect16>(Rect16::Merge_ParamPack(Rect16(0, 0, 20, 20), Rect16(0, 20, 20, 40), Rect16(20, 0, 40, 20)),
                { 0, 0, 60, 60 }));

        CHECK(res.Width() == expected.Width());
        CHECK(res.Height() == expected.Height());
        CHECK(res.BeginPoint().x == expected.BeginPoint().x);
        CHECK(res.BeginPoint().y == expected.BeginPoint().y);
        CHECK(res.EndPoint().x == expected.EndPoint().x);
        CHECK(res.EndPoint().y == expected.EndPoint().y);
    }
}

TEST_CASE("rectangle Contain rectangle", "[rectangle]") {
    Rect16 r;
    bool expected;
    point_i16_t p;

    std::tie(r, p, expected) = GENERATE(
        std::make_tuple<Rect16, point_i16_t, bool>({ 0, 0, 10, 10 }, { 20, 20 }, false),
        std::make_tuple<Rect16, point_i16_t, bool>({ 0, 0, 10, 10 }, { 0, 0 }, true),
        std::make_tuple<Rect16, point_i16_t, bool>({ 0, 0, 10, 10 }, { 5, 5 }, true));

    bool res = r.Contain(p);

    CHECK(res == expected);
}

TEST_CASE("rectangle split", "[rectangle]") {
    using Sequence = std::array<Rect16, 4>;
    using Ratio = std::array<uint8_t, 4>;

    SECTION("horizontal - splits with spaces") {
        Sequence expSplits, expSpaces;
        Rect16 r;
        size_t count;
        uint16_t spacing;
        Ratio ratio;
        Rect16 splits[4];
        Rect16 spaces[4];

        // TESTING
        //  r = Rect16({0, 0}, 120, 100);
        //  count = 4;
        //  spacing = 10;
        //  ratio = {1, 2, 2, 1};
        //
        //  r.HorizontalSplit(splits, spaces, count, spacing, ratio.data());
        //
        //  CHECK(spaces[0].TopLeft().x == 15);
        //  CHECK(spaces[1].TopLeft().x == 55);
        //  CHECK(spaces[2].TopLeft().x == 95);

        std::tie(r, count, spacing, ratio, expSplits, expSpaces) = GENERATE(
            std::make_tuple<Rect16, size_t, uint16_t, Ratio, Sequence, Sequence>(
                { 0, 0, 100, 100 }, 2, 0, { { 20, 20 } }, { { { 0, 0, 50, 100 }, { 50, 0, 50, 100 } } }, { { { 50, 0, 0, 100 } } }),
            std::make_tuple<Rect16, size_t, uint16_t, Ratio, Sequence, Sequence>(
                { 0, 0, 120, 100 }, 4, 10, { { 10, 15, 15, 10 } }, { { { 0, 0, 20, 100 }, { 30, 0, 25, 100 }, { 65, 0, 25, 100 }, { 100, 0, 20, 100 } } }, { { { 20, 0, 10, 100 }, { 55, 0, 10, 100 }, { 90, 0, 10, 100 } } }));

        r.HorizontalSplit(splits, spaces, count, spacing, ratio.data());

        COMPARE_ARRAYS(splits, expSplits);
        COMPARE_ARRAYS(spaces, expSpaces);
    }

    SECTION("horizontal - given widths 'footer style'") {

        Rect16 r;
        static constexpr size_t max_count = 4;
        static constexpr size_t h = 10;

        std::vector<Rect16> expSplits; // expected
        std::array<Rect16, max_count> splits;
        std::vector<Rect16::Width_t> widths;

        std::tie(r, widths, expSplits) = GENERATE(
            std::make_tuple<Rect16, std::vector<Rect16::Width_t>, std::vector<Rect16>>(
                { 0, 0, 100, h }, { 1, 2 }, { { { 0, 0, 1, h }, { 98, 0, 2, h } } }),
            std::make_tuple<Rect16, std::vector<Rect16::Width_t>, std::vector<Rect16>>(
                { 0, 0, 7, h }, { 1, 1, 1, 1 }, { { { 0, 0, 1, h }, { 2, 0, 1, h }, { 4, 0, 1, h }, { 6, 0, 1, h } } }),
            // last does not fit
            std::make_tuple<Rect16, std::vector<Rect16::Width_t>, std::vector<Rect16>>(
                { 0, 0, 12, h }, { 1, 2, 3, 40 }, { { { 0, 0, 1, h }, { 4, 0, 2, h }, { 9, 0, 3, h } } }),
            // not exact space, last is bit further
            std::make_tuple<Rect16, std::vector<Rect16::Width_t>, std::vector<Rect16>>(
                { 0, 0, 8, h }, { 1, 1, 1, 1 }, { { { 0, 0, 1, h }, { 2, 0, 1, h }, { 4, 0, 1, h }, { 7, 0, 1, h } } }),
            // only one fits
            std::make_tuple<Rect16, std::vector<Rect16::Width_t>, std::vector<Rect16>>(
                { 1, 2, 10, h }, { 5, 100, 1, 1 }, { { { 1, 2, 5, h } } }),
            // 2 border empty rects .. any empty rects are equal
            std::make_tuple<Rect16, std::vector<Rect16::Width_t>, std::vector<Rect16>>(
                { 1, 2, 14, h }, { 0, 2, 3, 0 }, { { { 0, 0, 0, 0 }, { 4, 2, 2, h }, { 9, 2, 3, h }, { 0, 0, 0, 0 } } }),
            std::make_tuple<Rect16, std::vector<Rect16::Width_t>, std::vector<Rect16>>(
                { 0, 2, 9, h }, { 0, 5, 0 }, { { { 0, 0, 0, 0 }, { 2, 2, 5, h }, { 0, 0, 0, 0 } } }),
            // empty
            std::make_tuple<Rect16, std::vector<Rect16::Width_t>, std::vector<Rect16>>(
                { 1, 0, 10, h }, { 50, 10, 1, 1 }, std::vector<Rect16>()));

        size_t expCount = expSplits.size();
        size_t do_N_splits = widths.size();
        CHECK(expCount <= max_count);
        CHECK(do_N_splits <= max_count); // unnecessary, next check would find it too, but this will tell me exact reason of failure
        CHECK(expCount <= do_N_splits);

        size_t count = r.HorizontalSplit(&splits[0], &widths[0], do_N_splits);
        CHECK(expCount == count);
        COMPARE_ARRAYS_SIZE_FROM_SMALLER(splits, expSplits);
    }

    SECTION("horizontal - cuts") {
        Sequence expected, result;
        Rect16 r;
        uint16_t span, count;

        std::tie(r, span, count, expected) = GENERATE(
            std::make_tuple<Rect16, uint16_t, uint16_t, Sequence>(
                { 0, 0, 0, 0 }, 10, 0, { { { 0, 0, 0, 0 }, { 0, 0, 0, 0 }, { 0, 0, 0, 0 }, { 0, 0, 0, 0 } } }),
            std::make_tuple<Rect16, uint16_t, uint16_t, Sequence>(
                { 0, 0, 100, 100 }, 10, 4, { { { 0, 0, 10, 100 }, { 10, 0, 10, 100 }, { 20, 0, 10, 100 }, { 30, 0, 10, 100 } } }),
            std::make_tuple<Rect16, uint16_t, uint16_t, Sequence>(
                { 0, 0, 100, 100 }, 30, 3, { { { 0, 0, 30, 100 }, { 30, 0, 30, 100 }, { 60, 0, 30, 100 } } }));

        size_t l = r.HorizontalSplit(result, span);
        CHECK(l == count);
        COMPARE_ARRAYS(expected, result);
    }

    SECTION("vertical - cuts") {
        Sequence expected, result;
        Rect16 r;
        uint16_t span, count;

        std::tie(r, span, count, expected) = GENERATE(
            std::make_tuple<Rect16, uint16_t, uint16_t, Sequence>(
                { 0, 0, 0, 0 }, 10, 0, { { { 0, 0, 0, 0 }, { 0, 0, 0, 0 }, { 0, 0, 0, 0 }, { 0, 0, 0, 0 } } }),
            std::make_tuple<Rect16, uint16_t, uint16_t, Sequence>(
                { 0, 0, 100, 100 }, 10, 4, { { { 0, 0, 100, 10 }, { 0, 10, 100, 10 }, { 0, 20, 100, 10 }, { 0, 30, 100, 10 } } }),
            std::make_tuple<Rect16, uint16_t, uint16_t, Sequence>(
                { 0, 0, 100, 100 }, 30, 3, { { { 0, 0, 100, 30 }, { 0, 30, 100, 30 }, { 0, 60, 100, 30 } } })

        );

        size_t l = r.VerticalSplit(result, span);
        CHECK(l == count);
        COMPARE_ARRAYS(expected, result);
    }
}

TEST_CASE("rectangle LeftSubrect", "[rectangle]") {
    SECTION("empty") {
        // y and h does not matter
        Rect16 minuend { 0, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 0, 1, 8, 1 }; // the rect that is to be subtracted.
        Rect16 expected_result { 0, 1, 0, 1 };

        Rect16 result = minuend.LeftSubrect(subtrahend);

        REQUIRE(expected_result == result);
    }

    SECTION("normal cut") {
        // y and h does not matter
        Rect16 minuend { 0, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 4, 1, 8, 1 }; // the rect that is to be subtracted.
        Rect16 expected_result { 0, 1, 4, 1 };

        Rect16 result = minuend.LeftSubrect(subtrahend);

        REQUIRE(expected_result == result);
    }

    SECTION("cut till end") {
        // y and h does not matter
        Rect16 minuend { 0, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 8, 1, 8, 1 }; // the rect that is to be subtracted.
        Rect16 expected_result { 0, 1, 8, 1 };

        Rect16 result = minuend.LeftSubrect(subtrahend);

        REQUIRE(expected_result == result);
    }

    SECTION("cut behind end") {
        // y and h does not matter
        Rect16 minuend { 0, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 12, 1, 8, 1 }; // the rect that is to be subtracted.
        Rect16 expected_result { 0, 1, 12, 1 };

        Rect16 result = minuend.LeftSubrect(subtrahend);

        REQUIRE(expected_result == result);
    }

    SECTION("empty cut at end") {
        // y and h does not matter
        Rect16 minuend { 0, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 16, 1, 8, 1 }; // the rect that is to be subtracted.
        Rect16 expected_result = minuend;

        Rect16 result = minuend.LeftSubrect(subtrahend);

        REQUIRE(expected_result == result);
    }

    SECTION("empty cut behind end") {
        // y and h does not matter
        Rect16 minuend { 0, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 32, 1, 8, 1 }; // the rect that is to be subtracted.
        Rect16 expected_result = minuend;

        Rect16 result = minuend.LeftSubrect(subtrahend);

        REQUIRE(expected_result == result);
    }

    SECTION("empty cut in front begin") {
        // y and h does not matter
        Rect16 minuend { 8, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 0, 1, 8, 1 }; // the rect that is to be subtracted.

        Rect16 result = minuend.LeftSubrect(subtrahend);

        REQUIRE(result.Width() == 0);
    }
}

TEST_CASE("rectangle RightSubrect", "[rectangle]") {
    SECTION("normal cut from begin") {
        // y and h does not matter
        Rect16 minuend { 0, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 0, 1, 8, 1 }; // the rect that is to be subtracted.
        Rect16 expected_result { 8, 1, 8, 1 };

        Rect16 result = minuend.RightSubrect(subtrahend);

        REQUIRE(expected_result == result);
    }

    SECTION("normal cut middle") {
        // y and h does not matter
        Rect16 minuend { 0, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 4, 1, 8, 1 }; // the rect that is to be subtracted.
        Rect16 expected_result { 12, 1, 4, 1 };

        Rect16 result = minuend.RightSubrect(subtrahend);

        REQUIRE(expected_result == result);
    }

    SECTION("cut till end") {
        // y and h does not matter
        Rect16 minuend { 0, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 8, 1, 8, 1 }; // the rect that is to be subtracted.

        Rect16 result = minuend.RightSubrect(subtrahend);

        REQUIRE(result.Width() == 0);
    }

    SECTION("cut behind end") {
        // y and h does not matter
        Rect16 minuend { 0, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 12, 1, 8, 1 }; // the rect that is to be subtracted.

        Rect16 result = minuend.RightSubrect(subtrahend);

        REQUIRE(result.Width() == 0);
    }

    SECTION("empty cut at end") {
        // y and h does not matter
        Rect16 minuend { 0, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 16, 1, 8, 1 }; // the rect that is to be subtracted.

        Rect16 result = minuend.RightSubrect(subtrahend);

        REQUIRE(result.Width() == 0);
    }

    SECTION("empty cut behind end") {
        // y and h does not matter
        Rect16 minuend { 0, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 32, 1, 8, 1 }; // the rect that is to be subtracted.

        Rect16 result = minuend.RightSubrect(subtrahend);

        REQUIRE(result.Width() == 0);
    }

    SECTION("not intersecting cut in front begin") {
        // y and h does not matter
        Rect16 minuend { 8, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 0, 1, 8, 1 }; // the rect that is to be subtracted.
        Rect16 expected_result = { 8, 1, 16, 1 };

        Rect16 result = minuend.RightSubrect(subtrahend);

        REQUIRE(expected_result == result);
    }

    SECTION("intersecting cut in front begin") {
        // y and h does not matter
        Rect16 minuend { 8, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 0, 1, 16, 1 }; // the rect that is to be subtracted.
        Rect16 expected_result = { 16, 1, 8, 1 };

        Rect16 result = minuend.RightSubrect(subtrahend);

        REQUIRE(expected_result == result);
    }

    SECTION("overlaping cut") {
        // y and h does not matter
        Rect16 minuend { 8, 1, 16, 1 }; // the rect that is to be subtracted from.
        Rect16 subtrahend { 0, 1, 32, 1 }; // the rect that is to be subtracted.

        Rect16 result = minuend.RightSubrect(subtrahend);

        REQUIRE(result.Width() == 0);
    }
}
