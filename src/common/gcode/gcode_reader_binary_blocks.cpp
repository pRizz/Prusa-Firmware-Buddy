#include "gcode_reader_binary.hpp"

#include "lang/i18n.h"

#include <cassert>
#include <sys/stat.h>

using bgcode::core::BlockHeader;

IGcodeReader::Result_t PrusaPackGcodeReader::read_and_check_header() {
    if (!range_valid(0, sizeof(file_header))) {
        return Result_t::RESULT_OUT_OF_RANGE;
    }

    rewind(file.get());

    if (bgcode::core::read_header(*file, file_header, nullptr) != bgcode::core::EResult::Success) {
        set_error(N_("Invalid BGCODE file header"));
        return Result_t::RESULT_ERROR;
    }

    return Result_t::RESULT_OK;
}

IGcodeReader::Result_t PrusaPackGcodeReader::read_block_header(BlockHeader &block_header, bool check_crc) {
    auto file = this->file.get();
    auto block_start = ftell(file);

    if (!range_valid(block_start, block_start + sizeof(block_header))) {
        return Result_t::RESULT_OUT_OF_RANGE;
    }

    constexpr size_t crc_buffer_size = 128;
    uint8_t crc_buffer[crc_buffer_size];
    auto res = read_next_block_header(*file, file_header, block_header, check_crc ? crc_buffer : nullptr, check_crc ? crc_buffer_size : 0);
    if (res == bgcode::core::EResult::ReadError && feof(file)) {
        return Result_t::RESULT_EOF;
    }

    if (res == bgcode::core::EResult::InvalidChecksum) {
        if (range_valid(block_start, block_start + block_header.get_size() + block_content_size(file_header, block_header))) {
            return Result_t::RESULT_CORRUPT;
        }
        return Result_t::RESULT_OUT_OF_RANGE;
    }

    if (res != bgcode::core::EResult::Success) {
        return Result_t::RESULT_ERROR;
    }

    if (!range_valid(block_start, block_start + block_header.get_size() + block_content_size(file_header, block_header))) {
        return Result_t::RESULT_OUT_OF_RANGE;
    }

    return Result_t::RESULT_OK;
}

std::variant<std::monostate, BlockHeader, PrusaPackGcodeReader::Result_t> PrusaPackGcodeReader::iterate_blocks(bool check_crc, stdext::inplace_function<IterateResult_t(BlockHeader &)> function) {
    if (auto res = read_and_check_header(); res != Result_t::RESULT_OK) {
        return res;
    }

    while (true) {
        BlockHeader block_header;
        auto res = read_block_header(block_header, check_crc);
        if (res != Result_t::RESULT_OK) {
            return res;
        }

        switch (function(block_header)) {
        case IterateResult_t::Return:
            return block_header;
        case IterateResult_t::End:
            return std::monostate {};
        case IterateResult_t::Continue:
            break;
        }

        if (skip_block(*file, file_header, block_header) != bgcode::core::EResult::Success) {
            return Result_t::RESULT_ERROR;
        }
    }
}
