#include "probe_analysis.hpp"

using namespace buddy;

int ProbeAnalysisBase::Classify(Features &features) {
    if (features.loadAngleCompressionStart <= 154.68160247802734f) {
        if (features.r2_50ms.compressionEnd <= 0.6531023383140564f) {
            if (features.r2_30ms.compressionEnd <= 0.005205066641792655f) {
                if (features.riseLine.GetY(features.decompressionEndTime) <= -0.18971788883209229f) {
                    return 0; // bad
                } else { /* if features.riseLine.GetY(features.decompressionEndTime) > -0.18971788883209229f */
                    return 0; // bad
                }
            } else { /* if features.r2_30ms.compressionEnd > 0.005205066641792655f */
                if (features.compressionLine.GetY(features.compressionStartTime) <= -51.45247840881348f) {
                    return 0; // bad
                } else { /* if features.compressionLine.GetY(features.compressionStartTime) > -51.45247840881348f */
                    return 1; // good
                }
            }
        } else { /* if features.r2_50ms.compressionEnd > 0.6531023383140564f */
            if (features.loadAngleCompressionEnd <= 51.137014389038086f) {
                if (features.loadMeanBeforeCompression <= -23.7804012298584f) {
                    return 0; // bad
                } else { /* if features.loadMeanBeforeCompression > -23.7804012298584f */
                    return 1; // good
                }
            } else { /* if features.loadAngleCompressionEnd > 51.137014389038086f */
                if (features.loadAngleDecompressionStart <= 135.77788543701172f) {
                    return 1; // good
                } else { /* if features.loadAngleDecompressionStart > 135.77788543701172f */
                    return 1; // good
                }
            }
        }
    } else { /* if features.loadAngleCompressionStart > 154.68160247802734f */
        if (features.decompressionLine.GetY(features.decompressionEndTime) <= -63.84521484375f) {
            if (features.r2_50ms.compressionStart <= 0.6476757228374481f) {
                if (features.r2_60ms.decompressionEnd <= -321.4128608703613f) {
                    return 1; // good
                } else { /* if features.r2_60ms.decompressionEnd > -321.4128608703613f */
                    return 0; // bad
                }
            } else { /* if features.r2_50ms.compressionStart > 0.6476757228374481f */
                if (features.riseLine.GetY(features.decompressionEndTime) <= 0.07457397505640984f) {
                    return 1; // good
                } else { /* if features.riseLine.GetY(features.decompressionEndTime) > 0.07457397505640984f */
                    return 1; // good
                }
            }
        } else { /* if features.decompressionLine.GetY(features.decompressionEndTime) > -63.84521484375f */
            if (features.loadAngleDecompressionStart <= 152.87728118896484f) {
                if (features.loadMeanBeforeCompression <= -36.56223678588867f) {
                    return 0; // bad
                } else { /* if features.loadMeanBeforeCompression > -36.56223678588867f */
                    return 1; // good
                }
            } else { /* if features.loadAngleDecompressionStart > 152.87728118896484f */
                if (features.loadAngleDecompressionStart <= 161.35951232910156f) {
                    return 0; // bad
                } else { /* if features.loadAngleDecompressionStart > 161.35951232910156f */
                    return 0; // bad
                }
            }
        }
    }
}

bool ProbeAnalysisBase::HasOutOfRangeFeature(Features &features, const char **feature, float *value) const {
    if (features.loadMeanBeforeCompression < -154.48058105323756f || features.loadMeanBeforeCompression > 152.44410035911991f) {
        *feature = "load_mean_before_compression";
        *value = features.loadMeanBeforeCompression;
        return true;
    }
    if (features.loadMeanAfterDecompression < -186.40204083948444f || features.loadMeanAfterDecompression > 194.03907144265904f) {
        *feature = "load_mean_after_decompression";
        *value = features.loadMeanAfterDecompression;
        return true;
    }
    if (features.compressionLine.GetY(features.compressionStartTime) < -256.92789509011595f || features.compressionLine.GetY(features.compressionStartTime) > 159.88252116779623f) {
        *feature = "load_compression_start";
        *value = features.compressionLine.GetY(features.compressionStartTime);
        return true;
    }
    if (features.decompressionLine.GetY(features.decompressionEndTime) < -6731.697754324502f || features.decompressionLine.GetY(features.decompressionEndTime) > 470.6857951091628f) {
        *feature = "load_decompression_end";
        *value = features.decompressionLine.GetY(features.decompressionEndTime);
        return true;
    }
    if (features.loadAngleCompressionStart < -52.492364077060884f || features.loadAngleCompressionStart > 233.5051448593478f) {
        *feature = "load_angle_compression_start";
        *value = features.loadAngleCompressionStart;
        return true;
    }
    if (features.loadAngleCompressionEnd < -29.99231606763046f || features.loadAngleCompressionEnd > 213.1064906506039f) {
        *feature = "load_angle_compression_end";
        *value = features.loadAngleCompressionEnd;
        return true;
    }
    if (features.loadAngleDecompressionStart < -46.98080445417618f || features.loadAngleDecompressionStart > 227.04222071853522f) {
        *feature = "load_angle_decompression_start";
        *value = features.loadAngleDecompressionStart;
        return true;
    }
    if (features.loadAngleDecompressionEnd < -93.72798028750367f || features.loadAngleDecompressionEnd > 273.7232224109812f) {
        *feature = "load_angle_decompression_end";
        *value = features.loadAngleDecompressionEnd;
        return true;
    }
    if (features.r2_20ms.compressionStart < -6535.315705859364f || features.r2_20ms.compressionStart > 133.50744526719794f) {
        *feature = "r2_compression_start_20";
        *value = features.r2_20ms.compressionStart;
        return true;
    }
    if (features.r2_20ms.compressionEnd < -1690.1392305507259f || features.r2_20ms.compressionEnd > 46.445990831041414f) {
        *feature = "r2_compression_end_20";
        *value = features.r2_20ms.compressionEnd;
        return true;
    }
    if (features.r2_30ms.decompressionStart < -14399.59142096975f || features.r2_30ms.decompressionStart > 469.83971245187513f) {
        *feature = "r2_decompression_start_30";
        *value = features.r2_30ms.decompressionStart;
        return true;
    }
    if (features.r2_30ms.decompressionEnd < -62922.69516938705f || features.r2_30ms.decompressionEnd > 2911.3834010814626f) {
        *feature = "r2_decompression_end_30";
        *value = features.r2_30ms.decompressionEnd;
        return true;
    }
    if (features.r2_50ms.compressionStart < -525.66164523715f || features.r2_50ms.compressionStart > 15.14786031499957f) {
        *feature = "r2_compression_start_50";
        *value = features.r2_50ms.compressionStart;
        return true;
    }
    if (features.r2_50ms.compressionEnd < -131.39515975957238f || features.r2_50ms.compressionEnd > 5.006255152513094f) {
        *feature = "r2_compression_end_50";
        *value = features.r2_50ms.compressionEnd;
        return true;
    }
    if (features.r2_50ms.decompressionStart < -8376.465287601053f || features.r2_50ms.decompressionStart > 284.4350844023189f) {
        *feature = "r2_decompression_start_50";
        *value = features.r2_50ms.decompressionStart;
        return true;
    }
    if (features.r2_50ms.decompressionEnd < -42356.61891250352f || features.r2_50ms.decompressionEnd > 1919.5961422774267f) {
        *feature = "r2_decompression_end_50";
        *value = features.r2_50ms.decompressionEnd;
        return true;
    }
    if (features.r2_60ms.decompressionStart < -9867.310839170745f || features.r2_60ms.decompressionStart > 257.2049327020503f) {
        *feature = "r2_decompression_start_60";
        *value = features.r2_60ms.decompressionStart;
        return true;
    }
    if (features.r2_60ms.decompressionEnd < -35308.89153040849f || features.r2_60ms.decompressionEnd > 1336.844303073224f) {
        *feature = "r2_decompression_end_60";
        *value = features.r2_60ms.decompressionEnd;
        return true;
    }
    auto compressedvsDecompressedAngleAfter = features.compressedLine.CalculateAngle(features.afterDecompressionLine, false);
    if (std::abs(compressedvsDecompressedAngleAfter) > 40) {
        *feature = "angle_after";
        *value = compressedvsDecompressedAngleAfter;
        return true;
    }
    return false;
}
