import qupath.lib.objects.PathObject
import java.io.File

// ============================================================
// CONFIG
// ============================================================

Map CONFIG = [

    // --------------------------------------------------------
    // Project
    // --------------------------------------------------------

    project_dir: "D:/qupath-cuda-spatial",

    exe_relpath: "target/release/qupath_gpu_tool.exe",

    data_dir_relpath: "data",

    // --------------------------------------------------------
    // CSV
    // --------------------------------------------------------

    source_csv_name: "source.csv",

    target_csv_name: "target.csv",

    result_csv_name: "result.csv",

    // --------------------------------------------------------
    // Runtime
    // --------------------------------------------------------

    mode: "distance_to_polygon",

    output_measurement:
        "Distance_to_Nerve_um(GPU)",

    overwrite_measurement: true,

    verbose: true,

    // --------------------------------------------------------
    // Pixel calibration
    // --------------------------------------------------------

    pixel_to_um: null
]

// ============================================================
// Logging
// ============================================================

def logInfo = { String msg ->
    if (CONFIG.verbose as boolean) {
        println "[QuPath-CUDA-Spatial] ${msg}"
    }
}

def logError = { String msg ->
    println "[QuPath-CUDA-Spatial][ERROR] ${msg}"
}

// ============================================================
// Paths
// ============================================================

File PROJECT_DIR =
    new File(CONFIG.project_dir as String)

File DATA_DIR =
    new File(
        PROJECT_DIR,
        CONFIG.data_dir_relpath as String
    )

File EXE_FILE =
    new File(
        PROJECT_DIR,
        CONFIG.exe_relpath as String
    )

File SOURCE_CSV =
    new File(
        DATA_DIR,
        CONFIG.source_csv_name as String
    )

File TARGET_CSV =
    new File(
        DATA_DIR,
        CONFIG.target_csv_name as String
    )

File RESULT_CSV =
    new File(
        DATA_DIR,
        CONFIG.result_csv_name as String
    )

// ============================================================
// Validate files
// ============================================================

if (!PROJECT_DIR.exists()) {

    logError(
        "Project directory not found:\n" +
        PROJECT_DIR.getAbsolutePath()
    )

    return
}

if (!EXE_FILE.exists()) {

    logError(
        "Executable not found:\n" +
        EXE_FILE.getAbsolutePath()
    )

    return
}

if (!SOURCE_CSV.exists()) {

    logError(
        "source.csv not found:\n" +
        SOURCE_CSV.getAbsolutePath()
    )

    return
}

if (!TARGET_CSV.exists()) {

    logError(
        "target.csv not found:\n" +
        TARGET_CSV.getAbsolutePath()
    )

    return
}

// ============================================================
// Pixel calibration
// ============================================================

double pixelSizeUm

if (CONFIG.pixel_to_um != null) {

    pixelSizeUm =
        (CONFIG.pixel_to_um as Number)
            .doubleValue()

    logInfo(
        "Using manual pixel size: " +
        "${pixelSizeUm} um/pixel"
    )

} else {

    def imageData =
        getCurrentImageData()

    if (imageData == null) {

        logError(
            "No current image open."
        )

        return
    }

    def cal =
        imageData
            .getServer()
            .getPixelCalibration()

    if (
        cal == null ||
        !cal.hasPixelSizeMicrons()
    ) {

        logError(
            "Image has no valid pixel calibration."
        )

        return
    }

    pixelSizeUm =
        cal.getAveragedPixelSizeMicrons()

    logInfo(
        "Pixel size: ${pixelSizeUm} um/pixel"
    )
}

// ============================================================
// Get detections
// ============================================================

List<PathObject> detections =
    new ArrayList<>(getDetectionObjects())

logInfo(
    "Detections loaded: ${detections.size()}"
)

// ============================================================
// Count source.csv rows
// ============================================================

List<String> sourceLines =
    SOURCE_CSV.readLines("UTF-8")

if (sourceLines.size() <= 1) {

    logError(
        "source.csv has no data rows."
    )

    return
}

int sourcePointCount =
    sourceLines.size() - 1

logInfo(
    "source.csv points: ${sourcePointCount}"
)

// ============================================================
// IMPORTANT CHECK
// ============================================================

if (sourcePointCount != detections.size()) {

    logError(
        "Mismatch between source.csv rows " +
        "and QuPath detections.\n" +
        "source.csv rows = ${sourcePointCount}\n" +
        "detections = ${detections.size()}\n\n" +
        "CSV row order must match detection order."
    )

    return
}

// ============================================================
// Launch CUDA tool
// ============================================================

List<String> command = [

    EXE_FILE.getAbsolutePath(),

    "--mode",
    CONFIG.mode as String,

    "--source",
    SOURCE_CSV.getAbsolutePath(),

    "--target",
    TARGET_CSV.getAbsolutePath(),

    "--output",
    RESULT_CSV.getAbsolutePath()
]

logInfo(
    "Launching spatial primitive..."
)

ProcessBuilder pb =
    new ProcessBuilder(command)

pb.redirectErrorStream(true)

Process process = pb.start()

process.inputStream.eachLine {
    println "GPU_LOG: ${it}"
}

int exitCode = process.waitFor()

if (exitCode != 0) {

    logError(
        "Rust/CUDA process failed: " +
        "${exitCode}"
    )

    return
}

// ============================================================
// Validate result.csv
// ============================================================

if (!RESULT_CSV.exists()) {

    logError(
        "result.csv not found."
    )

    return
}

List<String> resultLines =
    RESULT_CSV.readLines("UTF-8")

if (resultLines.size() <= 1) {

    logError(
        "result.csv has no data rows."
    )

    return
}

List<Double> distancesPx =
    resultLines
        .tail()
        .collect { String line ->

            String value =
                line
                    .split(",")[0]
                    .trim()

            return Double.parseDouble(value)
        }

if (
    distancesPx.size() !=
    detections.size()
) {

    logError(
        "Result row mismatch.\n" +
        "results = ${distancesPx.size()}\n" +
        "detections = ${detections.size()}"
    )

    return
}

// ============================================================
// Write measurements
// ============================================================

detections.eachWithIndex {
    PathObject obj,
    int i ->

    def ml =
        obj.getMeasurementList()

    if (
        !(CONFIG.overwrite_measurement
            as boolean)
    ) {

        double oldValue =
            ml.get(
                CONFIG.output_measurement
                    as String
            )

        if (!Double.isNaN(oldValue)) {
            return
        }
    }

    double distPx =
        distancesPx[i]

    double distUm =
        distPx * pixelSizeUm

    ml.put(
        CONFIG.output_measurement
            as String,
        distUm
    )
}

// ============================================================
// Refresh QuPath
// ============================================================

fireHierarchyUpdate()

logInfo(
    "Measurement update complete."
)

logInfo(
    "Updated detections: " +
    "${detections.size()}"
)