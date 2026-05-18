import qupath.lib.objects.PathObject
import java.io.File

// ============================================================
// CONFIG
// ============================================================

Map CONFIG = [

    // --------------------------------------------------------
    // Project
    // --------------------------------------------------------

    project_dir: "D:/code/qupath_gpu_tool",

    exe_relpath: "target/release/qupath_gpu_tool.exe",

    data_dir_relpath: "data",

    // --------------------------------------------------------
    // Spatial mode
    // --------------------------------------------------------
    // 你的 Rust/CUDA 端目前语义是：
    // source.csv = 一类点
    // target.csv = 一类点
    //
    // 如果 target 点来自 nerve boundary sampling，
    // 这个模式更准确叫 distance_to_target_points。
    //
    // 这里仍保留你的 CLI mode 名称，避免改 Rust 端。

    mode: "distance_to_polygon",

    // --------------------------------------------------------
    // QuPath classes
    // --------------------------------------------------------

    source_class: "immune_cell",

    target_class: "nerve_regions",

    // source 对象来源：
    // "detections"    -> getDetectionObjects()
    // "annotations"   -> getAnnotationObjects()
    // "both"          -> detections + annotations

    source_object_scope: "detections",

    // target 对象来源：
    // nerve_regions 通常是 annotation，所以默认 annotations

    target_object_scope: "annotations",

    // --------------------------------------------------------
    // Measurement
    // --------------------------------------------------------

    output_measurement: "Distance_to_Nerve_um(GPU)",

    overwrite_measurement: true,

    // --------------------------------------------------------
    // Pixel calibration
    // --------------------------------------------------------
    // null 表示使用图像 calibration；
    // 如果图像无 calibration，可手动写 0.49610156577455383

    pixel_to_um: null,

    // --------------------------------------------------------
    // Runtime
    // --------------------------------------------------------

    verbose: true,

    cleanup_temp_files: false,

    warning_source_count: 500000
]

// ============================================================
// Logging
// ============================================================

def logInfo = { String msg ->
    if (CONFIG.verbose as boolean) {
        println "[QuPath-CUDA-Spatial] ${msg}"
    }
}

def logWarn = { String msg ->
    println "[QuPath-CUDA-Spatial][WARNING] ${msg}"
}

def logError = { String msg ->
    println "[QuPath-CUDA-Spatial][ERROR] ${msg}"
}

// ============================================================
// Paths
// ============================================================

File PROJECT_DIR = new File(CONFIG.project_dir as String)

File DATA_DIR = new File(
    PROJECT_DIR,
    CONFIG.data_dir_relpath as String
)

File EXE_FILE = new File(
    PROJECT_DIR,
    CONFIG.exe_relpath as String
)

File SOURCE_CSV = new File(
    DATA_DIR,
    "source.csv"
)

File TARGET_CSV = new File(
    DATA_DIR,
    "target.csv"
)

File RESULT_CSV = new File(
    DATA_DIR,
    "result.csv"
)

// ============================================================
// Validation
// ============================================================

if (!PROJECT_DIR.exists()) {
    logError("Project directory not found:\n${PROJECT_DIR.getAbsolutePath()}")
    return
}

if (!EXE_FILE.exists()) {
    logError("Executable not found:\n${EXE_FILE.getAbsolutePath()}")
    return
}

if (!DATA_DIR.exists()) {
    boolean created = DATA_DIR.mkdirs()
    if (!created && !DATA_DIR.exists()) {
        logError("Failed to create data directory:\n${DATA_DIR.getAbsolutePath()}")
        return
    }
}

// ============================================================
// Pixel calibration
// ============================================================

double pixelSizeUm

if (CONFIG.pixel_to_um != null) {

    pixelSizeUm = (CONFIG.pixel_to_um as Number).doubleValue()

    logWarn("Using manual pixel size: ${pixelSizeUm} um/pixel")

} else {

    def imageData = getCurrentImageData()

    if (imageData == null) {
        logError("No current image data.")
        return
    }

    def cal = imageData
        .getServer()
        .getPixelCalibration()

    if (cal == null || !cal.hasPixelSizeMicrons()) {
        logError(
            "Image has no valid micron pixel calibration. " +
            "Set CONFIG.pixel_to_um manually."
        )
        return
    }

    pixelSizeUm = cal.getAveragedPixelSizeMicrons()

    logInfo("Pixel size: ${pixelSizeUm} um/pixel")
}

// ============================================================
// Helpers
// ============================================================

Closure<String> classNameOf = { PathObject obj ->
    if (obj == null || obj.getPathClass() == null) {
        return null
    }
    return obj.getPathClass().toString()
}

Closure<List<PathObject>> objectsByScope = { String scope ->

    List<PathObject> objects = []

    if (scope == "detections") {

        objects.addAll(getDetectionObjects())

    } else if (scope == "annotations") {

        objects.addAll(getAnnotationObjects())

    } else if (scope == "both") {

        objects.addAll(getDetectionObjects())
        objects.addAll(getAnnotationObjects())

    } else {

        throw new RuntimeException(
            "Invalid object scope: ${scope}. " +
            "Expected: detections, annotations, or both."
        )
    }

    return objects
}

Closure<List<PathObject>> filterObjectsByClass = {
    List<PathObject> objects,
    String targetClassName ->

    return objects.findAll { PathObject obj ->

        if (obj == null) {
            return false
        }

        if (obj.getROI() == null) {
            return false
        }

        String cls = classNameOf(obj)

        return cls == targetClassName
    }
}

Closure<Void> writePointCsv = {
    File file,
    List<PathObject> objects ->

    file.withWriter("UTF-8") { writer ->

        writer.writeLine("x,y")

        objects.each { PathObject obj ->

            def roi = obj.getROI()

            double x = roi.getCentroidX()
            double y = roi.getCentroidY()

            writer.writeLine("${x},${y}")
        }
    }

    return null
}

// ============================================================
// Collect source / target objects
// ============================================================

List<PathObject> sourceCandidates =
    objectsByScope(CONFIG.source_object_scope as String)

List<PathObject> targetCandidates =
    objectsByScope(CONFIG.target_object_scope as String)

List<PathObject> sourceObjects =
    filterObjectsByClass(
        sourceCandidates,
        CONFIG.source_class as String
    )

List<PathObject> targetObjects =
    filterObjectsByClass(
        targetCandidates,
        CONFIG.target_class as String
    )

logInfo("Source candidates: ${sourceCandidates.size()}")
logInfo("Target candidates: ${targetCandidates.size()}")
logInfo("Matched source objects [${CONFIG.source_class}]: ${sourceObjects.size()}")
logInfo("Matched target objects [${CONFIG.target_class}]: ${targetObjects.size()}")

if (sourceObjects.isEmpty()) {
    logError(
        "No source objects matched class '${CONFIG.source_class}'. " +
        "Check class name and source_object_scope."
    )

    println "Available detection classes:"
    getDetectionObjects()
        .collect { classNameOf(it) }
        .unique()
        .sort()
        .each { println "  - ${it}" }

    println "Available annotation classes:"
    getAnnotationObjects()
        .collect { classNameOf(it) }
        .unique()
        .sort()
        .each { println "  - ${it}" }

    return
}

if (targetObjects.isEmpty()) {
    logError(
        "No target objects matched class '${CONFIG.target_class}'. " +
        "Check class name and target_object_scope."
    )

    println "Available detection classes:"
    getDetectionObjects()
        .collect { classNameOf(it) }
        .unique()
        .sort()
        .each { println "  - ${it}" }

    println "Available annotation classes:"
    getAnnotationObjects()
        .collect { classNameOf(it) }
        .unique()
        .sort()
        .each { println "  - ${it}" }

    return
}

if (sourceObjects.size() > (CONFIG.warning_source_count as Number).intValue()) {
    logWarn("Large source object count detected: ${sourceObjects.size()}")
}

// ============================================================
// Export CSV
// ============================================================

writePointCsv(SOURCE_CSV, sourceObjects)
writePointCsv(TARGET_CSV, targetObjects)

logInfo("Wrote source CSV: ${SOURCE_CSV.getAbsolutePath()}")
logInfo("Wrote target CSV: ${TARGET_CSV.getAbsolutePath()}")

// ============================================================
// Launch external Rust/CUDA tool
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

logInfo("Launching spatial primitive...")

ProcessBuilder pb = new ProcessBuilder(command)

pb.redirectErrorStream(true)

Process process = pb.start()

process.inputStream.eachLine { String line ->
    println "GPU_LOG: ${line}"
}

int exitCode = process.waitFor()

if (exitCode != 0) {
    logError("Rust/CUDA process failed with exit code: ${exitCode}")
    return
}

if (!RESULT_CSV.exists()) {
    logError("Result CSV not found:\n${RESULT_CSV.getAbsolutePath()}")
    return
}

// ============================================================
// Read result.csv
// ============================================================

List<String> resultLines = RESULT_CSV.readLines("UTF-8")

if (resultLines.size() <= 1) {
    logError("Result CSV has no data rows.")
    return
}

List<Double> distancesPx = resultLines
    .tail()
    .collect { String line ->
        String firstCol = line.split(",")[0].trim()
        return Double.parseDouble(firstCol)
    }

if (distancesPx.size() != sourceObjects.size()) {
    logError(
        "Result count mismatch. " +
        "sourceObjects=${sourceObjects.size()}, " +
        "resultRows=${distancesPx.size()}"
    )
    return
}

// ============================================================
// Write measurements
// ============================================================

sourceObjects.eachWithIndex { PathObject obj, int i ->

    def ml = obj.getMeasurementList()

    if (!(CONFIG.overwrite_measurement as boolean)) {

        double oldValue = ml.get(CONFIG.output_measurement as String)

        if (!Double.isNaN(oldValue)) {
            return
        }
    }

    double distPx = distancesPx[i]
    double distUm = distPx * pixelSizeUm

    ml.put(
        CONFIG.output_measurement as String,
        distUm
    )
}

// QuPath 官方脚本 API：通知 hierarchy / GUI 更新
fireHierarchyUpdate()

logInfo("Measurement update complete.")
logInfo("Updated source objects: ${sourceObjects.size()}")
logInfo("Measurement name: ${CONFIG.output_measurement}")