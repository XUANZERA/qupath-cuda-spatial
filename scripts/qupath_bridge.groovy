import qupath.lib.objects.PathObject
import java.io.File

// ============================================================
// CONFIG
// ============================================================

def CONFIG = [

    // --------------------------------------------------------
    // Project
    // --------------------------------------------------------

    project_dir: "D:/qupath_cuda_spatial",

    exe_relpath: "target/release/qupath_gpu_tool.exe",

    data_dir_relpath: "data",

    // --------------------------------------------------------
    // Spatial mode
    // --------------------------------------------------------

    mode: "distance_to_polygon",

    // --------------------------------------------------------
    // QuPath classes
    // --------------------------------------------------------

    source_class: "immune_cell",

    target_class: "nerve_regions",

    // --------------------------------------------------------
    // Measurement
    // --------------------------------------------------------

    output_measurement: "Distance_to_Nerve_um",

    // --------------------------------------------------------
    // Pixel calibration
    // --------------------------------------------------------

    pixel_to_um: null,

    // --------------------------------------------------------
    // Runtime
    // --------------------------------------------------------

    verbose: true,

    overwrite_measurement: true,

    cleanup_temp_files: false,

    warning_cell_count: 5e5
]

// ============================================================
// Derived paths
// ============================================================

def PROJECT_DIR = new File(CONFIG.project_dir)

def DATA_DIR = new File(
    PROJECT_DIR,
    CONFIG.data_dir_relpath
)

def EXE_FILE = new File(
    PROJECT_DIR,
    CONFIG.exe_relpath
)

def SOURCE_CSV = new File(
    DATA_DIR,
    "source.csv"
)

def TARGET_CSV = new File(
    DATA_DIR,
    "target.csv"
)

def RESULT_CSV = new File(
    DATA_DIR,
    "result.csv"
)

// ============================================================
// Logging
// ============================================================

def logInfo = { msg ->
    if (CONFIG.verbose) {
        println "[QuPath-CUDA-Spatial] ${msg}"
    }
}

def logWarn = { msg ->
    println "[QuPath-CUDA-Spatial][WARNING] ${msg}"
}

def logError = { msg ->
    println "[QuPath-CUDA-Spatial][ERROR] ${msg}"
}

// ============================================================
// Validate config
// ============================================================

def validateConfig = {

    if (!PROJECT_DIR.exists()) {
        throw new RuntimeException(
            "Project directory not found:\n${PROJECT_DIR}"
        )
    }

    if (!EXE_FILE.exists()) {
        throw new RuntimeException(
            "Executable not found:\n${EXE_FILE}"
        )
    }

    if (!DATA_DIR.exists()) {
        DATA_DIR.mkdirs()
    }
}

validateConfig()

// ============================================================
// Pixel size
// ============================================================

double pixelSize

if (CONFIG.pixel_to_um != null) {

    pixelSize = CONFIG.pixel_to_um

    logWarn(
        "Using manual pixel size: ${pixelSize}"
    )

} else {

    def imageData = getCurrentImageData()

    def cal = imageData
        .getServer()
        .getPixelCalibration()

    pixelSize = cal.getPixelWidthMicrons()

    if (pixelSize == 1.0) {

        logWarn(
            "Image is not calibrated."
        )

    } else {

        logInfo(
            "Pixel size: ${pixelSize} um/pixel"
        )
    }
}

// ============================================================
// Selected annotation
// ============================================================

PathObject selected = getSelectedObject()

if (selected == null) {

    println "ERROR: Select parent annotation first."

    return
}

def children = selected.getChildObjects()

def sourceClass =
    getPathClass(CONFIG.source_class)

def targetClass =
    getPathClass(CONFIG.target_class)

// ============================================================
// Export source points
// ============================================================

def sourceObjects = []

SOURCE_CSV.withWriter { writer ->

    writer.writeLine("x,y")

    children.each { child ->

        if (
            child.getPathClass() == sourceClass &&
            child.getROI() != null
        ) {

            double x =
                child.getROI().getCentroidX()

            double y =
                child.getROI().getCentroidY()

            writer.writeLine("${x},${y}")

            sourceObjects << child
        }
    }
}

// ============================================================
// Export target geometry
// ============================================================

TARGET_CSV.withWriter { writer ->

    writer.writeLine("x,y")

    children.each { child ->

        if (
            child.getPathClass() == targetClass &&
            child.getROI() != null
        ) {

            def coords = child
                .getROI()
                .getGeometry()
                .getCoordinates()

            coords.each { c ->

                writer.writeLine(
                    "${c.x},${c.y}"
                )
            }
        }
    }
}

logInfo(
    "Exported ${sourceObjects.size()} source objects."
)

if (
    sourceObjects.size() >
    CONFIG.warning_cell_count
) {

    logWarn(
        "Large source object count detected."
    )
}

// ============================================================
// Launch Rust/CUDA
// ============================================================

def command = [

    EXE_FILE.getAbsolutePath(),

    "--mode",
    CONFIG.mode,

    "--source",
    SOURCE_CSV.getAbsolutePath(),

    "--target",
    TARGET_CSV.getAbsolutePath(),

    "--output",
    RESULT_CSV.getAbsolutePath()
]

logInfo("Launching spatial primitive...")

def pb = new ProcessBuilder(command)

pb.redirectErrorStream(true)

def process = pb.start()

process.inputStream.eachLine {
    println "GPU_LOG: ${it}"
}

process.waitFor()

if (process.exitValue() != 0) {

    logError(
        "Rust process failed: ${process.exitValue()}"
    )

    return
}

// ============================================================
// Read result
// ============================================================

if (!RESULT_CSV.exists()) {

    logError("Result CSV not found.")

    return
}

def lines = RESULT_CSV.readLines()

def values = lines
    .tail()
    .collect { it.split(",")[0] }

if (values.size() != sourceObjects.size()) {

    logError(
        "Result count mismatch."
    )

    return
}

// ============================================================
// Write measurements
// ============================================================
sourceObjects.eachWithIndex { obj, i ->

    def ml = obj.getMeasurementList()

    if (
        !CONFIG.overwrite_measurement &&
        !Double.isNaN(
            ml.getMeasurementValue(
                CONFIG.output_measurement
            )
        )
    ) {
        return
    }

    double distPx =
        values[i].toDouble()

    double distUm =
        distPx * pixelSize

    ml.putMeasurement(
        CONFIG.output_measurement,
        distUm
    )
}

// 最安全的 measurement refresh
fireObjectMeasurementsChangedEvent(
    this,
    sourceObjects
)

logInfo(
    "Measurement update complete."
)