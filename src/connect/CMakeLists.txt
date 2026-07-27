target_sources(
  firmware
  PRIVATE background.cpp
          command.cpp
          command_id.cpp
          connect.cpp
          connect_commands.cpp
          connection_cache.cpp
          error_printer.cpp
          hostname.cpp
          json_out.cpp
          marlin_printer.cpp
          marlin_printer_state.cpp
          planner.cpp
          printer.cpp
          printer_common.cpp
          printer_type.cpp
          registrator.cpp
          render.cpp
          render_json.cpp
          render_telemetry.cpp
          run.cpp
          sleep.cpp
          status.cpp
  )

add_subdirectory(tls)
