#pragma once

#include "render.hpp"

namespace connect_client::detail {

json::JsonResult render_msg(size_t resume_point, json::JsonOutput &output, RenderState &state, const transfers::Download::InlineRequest &request);
json::JsonResult render_msg(size_t resume_point, json::JsonOutput &output, RenderState &state, const SendTelemetry &telemetry);
json::JsonResult render_msg(size_t resume_point, json::JsonOutput &output, RenderState &state, const Event &event);
json::JsonResult render_msg(size_t resume_point, json::JsonOutput &output, const RenderState &state, const Sleep &);
json::JsonResult render_msg(size_t resume_point, json::JsonOutput &output, const RenderState &state, const ReadCommand &);

} // namespace connect_client::detail
