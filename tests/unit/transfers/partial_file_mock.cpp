#include "transfers/partial_file.hpp"

using namespace transfers;

std::variant<const char *, PartialFile::Ptr> PartialFile::open(const char *, PartialFile::State, bool ignore_opened) {
    return "not implemented";
}

bool PartialFile::has_valid_tail(size_t) const {
    return true;
}

PartialFile::State PartialFile::get_state() const {
    return state;
}
