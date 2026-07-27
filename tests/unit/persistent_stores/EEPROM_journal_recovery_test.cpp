#include <catch2/catch.hpp>
#include "crc32.h"
#include "dummy_eeprom_chip.h"
#include <journal/backend.hpp>
#include <journal/store.hpp>
#include <storage_drivers/eeprom_storage.hpp>

static constexpr const char *key = "data";
static constexpr size_t header_size = 6;

inline constexpr int32_t default_int32_t { 0 };

constexpr size_t chip_journal_start_address = 100;
constexpr size_t chip_journal_size = 8096 - chip_journal_start_address;

using namespace journal;

inline journal::Backend &Test_EEPROM_journal() {
    return journal::backend_instance<chip_journal_start_address, chip_journal_size, EEPROMInstance>();
}
inline void reinit_journal() {
    new (&Test_EEPROM_journal()) Backend(chip_journal_start_address, chip_journal_size, EEPROMInstance());
}
struct TestStruct {
    int32_t int32 = 0;
    std::array<uint8_t, 10> data = {};
    bool operator==(const TestStruct &rhs) const {
        return int32 == rhs.int32 && data == rhs.data;
    }
    bool operator!=(const TestStruct &rhs) const {
        return !(rhs == *this);
    }
};
struct NestedStruct {
    bool operator==(const NestedStruct &rhs) const {
        return test_struct == rhs.test_struct && is_valid == rhs.is_valid;
    }
    bool operator!=(const NestedStruct &rhs) const {
        return !(rhs == *this);
    }
    TestStruct test_struct;
    bool is_valid = false;
};

inline constexpr TestStruct default_test_struct {};
inline constexpr NestedStruct default_nested_struct {};

struct TestEEPROMJournalConfigV0 : public CurrentStoreConfig<Backend, Test_EEPROM_journal> {
    StoreItem<int32_t, default_int32_t, ItemFlags {}, 0xAA> int_item;
    StoreItem<TestStruct, default_test_struct, ItemFlags {}, 0x1000> struct_item;
    StoreItem<NestedStruct, default_nested_struct, ItemFlags {}, 0x2000> nested_struct_item;
};
struct TestDeprecatedEEPROMJournalItemsV0 : public DeprecatedStoreConfig<Backend> {
};

static_assert(journal::has_unique_items<TestEEPROMJournalConfigV0>(), "Just added items are causing collisions");

inline constexpr std::array<journal::Backend::MigrationFunction, 0> test_migration_functions_v0 {};
inline constexpr std::span<const journal::Backend::MigrationFunction> test_migration_functions_span_v0 { test_migration_functions_v0 };

constexpr std::array<int32_t, 64> default_array = { 1, 2, 3, 4, 5, 6, 7, 8, 9 };

inline journal::Backend &Small_Test_EEPROM_journal() {
    return journal::backend_instance<100, 768, EEPROMInstance>();
}
struct TestEEPROMJournalConfigBigItem : public CurrentStoreConfig<Backend, Small_Test_EEPROM_journal> {
    StoreItem<std::array<int32_t, 64>, default_array, ItemFlags {}, 1> random_data;
};

TEST_CASE("journal::EEPROM::Bank migration during transaction") {
    eeprom_chip.clear();
    new (&Small_Test_EEPROM_journal()) Backend(100, 768, EEPROMInstance());

    auto local_store = std::make_unique<Store<TestEEPROMJournalConfigBigItem, TestDeprecatedEEPROMJournalItemsV0, test_migration_functions_span_v0>>();
    auto data = default_array;
    data[1] = 10;
    local_store->init();
    local_store->load_all();
    REQUIRE(Small_Test_EEPROM_journal().current_address == 110);
    local_store->random_data.set(data);
    REQUIRE(Small_Test_EEPROM_journal().current_address == 373);

    data[1] = 20;
    Small_Test_EEPROM_journal().transaction_start();
    local_store->random_data.set(data);
    REQUIRE(Small_Test_EEPROM_journal().current_address == 757);
    Small_Test_EEPROM_journal().transaction_end();
    REQUIRE(Small_Test_EEPROM_journal().current_address == 757);

    new (&Small_Test_EEPROM_journal()) Backend(100, 768, EEPROMInstance());
    local_store = std::make_unique<Store<TestEEPROMJournalConfigBigItem, TestDeprecatedEEPROMJournalItemsV0, test_migration_functions_span_v0>>();
    local_store->init();
    local_store->load_all();
    REQUIRE(Small_Test_EEPROM_journal().current_address == 757);
    REQUIRE(local_store->random_data.get() == data);
}

struct TestEEPROMJournalConfigV1 : public CurrentStoreConfig<Backend, Test_EEPROM_journal> {
    StoreItem<int32_t, default_int32_t, ItemFlags {}, 0x11> int_item;
    StoreItem<TestStruct, default_test_struct, ItemFlags {}, 0x1000> struct_item;
    StoreItem<NestedStruct, default_nested_struct, ItemFlags {}, 0x2000> nested_struct_item;
};

struct TestDeprecatedEEPROMJournalItemsV1 : public DeprecatedStoreConfig<Backend> {
    StoreItem<int32_t, default_int32_t, 0xAA> int_item_v0;
};

struct TestEEPROMJournalConfigV2 : public CurrentStoreConfig<Backend, Test_EEPROM_journal> {
    StoreItem<int32_t, default_int32_t, ItemFlags {}, 0x22> int_item;
    StoreItem<TestStruct, default_test_struct, ItemFlags {}, 0x1000> struct_item;
    StoreItem<NestedStruct, default_nested_struct, ItemFlags {}, 0x2000> nested_struct_item;
};

struct TestDeprecatedEEPROMJournalItemsV2 : public DeprecatedStoreConfig<Backend> {
    StoreItem<int32_t, default_int32_t, 0x11> int_item_v1;
    StoreItem<int32_t, default_int32_t, 0xAA> int_item_v0;
};

struct TestEEPROMJournalConfigV3 : public CurrentStoreConfig<Backend, Test_EEPROM_journal> {
    StoreItem<int32_t, default_int32_t, ItemFlags {}, 0x33> int_item;
    StoreItem<TestStruct, default_test_struct, ItemFlags {}, 0x1000> struct_item;
    StoreItem<NestedStruct, default_nested_struct, ItemFlags {}, 0x2000> nested_struct_item;
};

struct TestDeprecatedEEPROMJournalItemsV3 : public DeprecatedStoreConfig<Backend> {
    StoreItem<int32_t, default_int32_t, 0x22> int_item_v2;
    StoreItem<int32_t, default_int32_t, 0x11> int_item_v1;
    StoreItem<int32_t, default_int32_t, 0xAA> int_item_v0;
};

template <typename IntItemT>
void int_item_migration(journal::Backend &backend, uint16_t new_id) {
    typename IntItemT::value_type old_int_item { IntItemT::default_val };

    static_assert(sizeof(typename IntItemT::value_type) == 4, "");

    auto callback = [&](journal::Backend::ItemHeader header, std::array<uint8_t, journal::Backend::MAX_ITEM_SIZE> &buffer) -> void {
        if (header.id == IntItemT::hashed_id) {
            memcpy(&old_int_item, buffer.data(), header.len);
        }
    };
    backend.read_items_for_migrations(callback);

    typename IntItemT::value_type new_int_item { old_int_item };

    backend.save_migration_item<typename IntItemT::value_type>(new_id, new_int_item);
}

namespace V1_deprecated_ids {
inline constexpr uint16_t int_item[] {
    0xAA,
};
}

namespace V1_migrations {
void int_item(journal::Backend &backend) {
    int_item_migration<decltype(TestDeprecatedEEPROMJournalItemsV1::int_item_v0)>(backend, 0x11);
}
} // namespace V1_migrations

static_assert(journal::has_unique_items<TestEEPROMJournalConfigV1>(), "Just added items are causing collisions");

inline constexpr journal::Backend::MigrationFunction test_migration_functions_v1[] {
    { V1_migrations::int_item, V1_deprecated_ids::int_item },
};
inline constexpr std::span<const journal::Backend::MigrationFunction> test_migration_functions_span_v1 { test_migration_functions_v1 };

namespace V2_deprecated_ids {
inline constexpr uint16_t int_item[] {
    0x11,
};
}

namespace V2_migrations {
void int_item(journal::Backend &backend) {
    int_item_migration<decltype(TestDeprecatedEEPROMJournalItemsV2::int_item_v1)>(backend, 0x22);
}
} // namespace V2_migrations

static_assert(journal::has_unique_items<TestEEPROMJournalConfigV2>(), "Just added items are causing collisions");

inline constexpr journal::Backend::MigrationFunction test_migration_functions_v2[] {
    { V1_migrations::int_item, V1_deprecated_ids::int_item },
    { V2_migrations::int_item, V2_deprecated_ids::int_item },
};
inline constexpr std::span<const journal::Backend::MigrationFunction> test_migration_functions_span_v2 { test_migration_functions_v2 };

namespace V3_deprecated_ids {
inline constexpr uint16_t int_item[] {
    0x22,
};
}

namespace V3_migrations {
void int_item(journal::Backend &backend) {
    int_item_migration<decltype(TestDeprecatedEEPROMJournalItemsV3::int_item_v2)>(backend, 0x33);
}
} // namespace V3_migrations

static_assert(journal::has_unique_items<TestEEPROMJournalConfigV3>(), "Just added items are causing collisions");

inline constexpr journal::Backend::MigrationFunction test_migration_functions_v3[] {
    { V1_migrations::int_item, V1_deprecated_ids::int_item },
    { V2_migrations::int_item, V2_deprecated_ids::int_item },
    { V3_migrations::int_item, V3_deprecated_ids::int_item },
};
inline constexpr std::span<const journal::Backend::MigrationFunction> test_migration_functions_span_v3 { test_migration_functions_v3 };

// USE INFO(print_chip); to print the current state of chip
std::string print_chip() {
    std::array<uint8_t, 32> buffer; // adjust number to print more
    eeprom_chip.read_bytes(chip_journal_start_address, buffer);

    std::string str { "" };
    str += "CHIP:\n";
    int counter = 0;

    for (const auto &el : buffer) {
        str += " ";
        char buffer[10];
        snprintf(buffer, sizeof(buffer), "%02X", static_cast<int>(el));
        str += buffer;
        if (++counter >= 5) {
            counter = 0;
            str += "\n";
        }
    }

    // eeprom_chip.read_bytes(chip_journal_start_address + chip_journal_size / 2, buffer);
    // counter = 0;
    // str += "\nCHIP Next bank:\n";
    // for (const auto &el : buffer) {
    //     str += " ";
    //     char buffer[10];
    //     snprintf(buffer, sizeof(buffer), "%02X", static_cast<int>(el));
    //     str += buffer;
    //     if (++counter >= 5) {
    //         counter = 0;
    //         str += "\n";
    //     }
    // }
    return str;
}

TEST_CASE("journal::EEPROM::Item migration") {
    eeprom_chip.clear();
    reinit_journal();
    auto old_store = std::make_unique<Store<TestEEPROMJournalConfigV0, TestDeprecatedEEPROMJournalItemsV0, test_migration_functions_span_v0>>();
    old_store->init();
    old_store->load_all();
    REQUIRE(Test_EEPROM_journal().journal_state == Backend::JournalState::ColdStart);
    REQUIRE(Test_EEPROM_journal().current_address == Test_EEPROM_journal().start_address + 10);

    old_store->int_item.set(10);
    REQUIRE(old_store->int_item.get() == 10);
    REQUIRE(Test_EEPROM_journal().current_address == Test_EEPROM_journal().start_address + 21);

    reinit_journal();

    SECTION("First migration") {
        auto v1_store = std::make_unique<Store<TestEEPROMJournalConfigV1, TestDeprecatedEEPROMJournalItemsV1, test_migration_functions_span_v1>>();
        v1_store->init();
        REQUIRE(Test_EEPROM_journal().journal_state != Backend::JournalState::ColdStart);
        v1_store->load_all();

        REQUIRE(Test_EEPROM_journal().journal_state == Backend::JournalState::ValidStart);
        REQUIRE(Test_EEPROM_journal().current_address == Test_EEPROM_journal().start_address + Test_EEPROM_journal().bank_size + 21);
        REQUIRE(v1_store->int_item.get() == 10);

        SECTION("Second migration") {
            auto v2_store = std::make_unique<Store<TestEEPROMJournalConfigV2, TestDeprecatedEEPROMJournalItemsV2, test_migration_functions_span_v2>>();
            v2_store->init();
            v2_store->load_all();

            REQUIRE(Test_EEPROM_journal().journal_state == Backend::JournalState::ValidStart);
            REQUIRE(Test_EEPROM_journal().current_address == Test_EEPROM_journal().start_address + 21);
            REQUIRE(v2_store->int_item.get() == 10);

            SECTION("Third migration") {
                auto v3_store = std::make_unique<Store<TestEEPROMJournalConfigV3, TestDeprecatedEEPROMJournalItemsV3, test_migration_functions_span_v3>>();
                v3_store->init();
                v3_store->load_all();

                REQUIRE(Test_EEPROM_journal().journal_state == Backend::JournalState::ValidStart);
                REQUIRE(Test_EEPROM_journal().current_address == Test_EEPROM_journal().start_address + Test_EEPROM_journal().bank_size + 21);
                REQUIRE(v3_store->int_item.get() == 10);
            }
        }
    }
}

struct StoreConfig_BFW3553 : public CurrentStoreConfig<Backend, Test_EEPROM_journal> {
    StoreItem<int32_t, default_int32_t, ItemFlags {}, 0> int_item;
};

TEST_CASE("journal::EEPROM::Regression BFW-3553") {
    eeprom_chip.clear();
    reinit_journal();
    auto &backend = Test_EEPROM_journal();

    auto store = std::make_unique<Store<StoreConfig_BFW3553, TestDeprecatedEEPROMJournalItemsV0, test_migration_functions_span_v0>>();
    store->init();
    store->load_all();

    // At start, we should be at bank 1
    const auto start_bank = backend.get_next_bank();
    REQUIRE(start_bank == Backend::BankSelector::Second);

    // Write items into the store until the bank is almost full
    int i = 0;
    {
        // Make it a single transaction, to prevent bank migration on next reinit
        auto transaction = backend.transaction_guard();

        constexpr auto single_write_size = Backend::ITEM_HEADER_SIZE + sizeof(int32_t);
        while (backend.fits_in_current_bank(single_write_size + Backend::CRC_SIZE + Backend::END_ITEM_SIZE_WITH_CRC)) {
            const auto start_free_space = backend.get_free_space_in_current_bank();
            REQUIRE(start_free_space > single_write_size);

            store->int_item.set(++i);

            // Check for unexpected bank migration
            REQUIRE(backend.get_next_bank() == start_bank);

            // Check that we've journalled exactly the amount of bytes we expected
            REQUIRE(backend.get_free_space_in_current_bank() == start_free_space - single_write_size);
        }
    }

    // Check for unexpected bank migration
    REQUIRE(backend.get_next_bank() == start_bank);

    const auto reinit_store = [&] {
        store.reset();
        reinit_journal();
        store = std::make_unique<Store<StoreConfig_BFW3553, TestDeprecatedEEPROMJournalItemsV0, test_migration_functions_span_v0>>();
        store->init();
        store->load_all();
    };

    reinit_store();

    // Check that no migration and such happened
    REQUIRE(backend.get_next_bank() == start_bank);
    REQUIRE(store->int_item.get() == i);

    // Write an item that just fits the rest of the bank - without the end item
    // This is however artificially constructed and in practice probably never happens in the real code
    {
        std::vector<unsigned char> data(backend.get_free_space_in_current_bank() - Backend::ITEM_HEADER_SIZE - Backend::CRC_SIZE);
        Backend::ItemHeader header { .last_item = true, .id = 8631, .len = static_cast<uint16_t>(data.size()) };
        const auto crc = backend.calculate_crc(header, data);
        backend.current_address += backend.write_item(backend.current_address, header, data, crc);
        REQUIRE(backend.get_free_space_in_current_bank() == 0);
    }

    reinit_store();

    // Check that we still have data
    REQUIRE(store->int_item.get() == i);
    REQUIRE(backend.journal_state == Backend::JournalState::MissingEndItem);
}
