import qupath.lib.objects.PathObject
import java.io.File

// ---------------------------------------------------------------------
// 环境配置 
// ---------------------------------------------------------------------
def CONFIG = [
    

    //------------------------------------------------------------------
    // Project Path
    //------------------------------------------------------------------

    // 根文件夹
    project_dir = "D:/qupath_cuda_spatial",
    
    // 可执行文件夹
    exe_relpath = "target/release/qupath_gpu_tool.exe",
    
    // 数据csv文件夹
    data_dir_relpath = "data",


    //------------------------------------------------------------------
    // Qupath Object对象种类
    //------------------------------------------------------------------

    // 被测量的细胞种类
    cell_class = "immune_cell",

    // 目标的Annotation种类
    target_annotation_class = "nerve_regions",


    //------------------------------------------------------------------
    // 测量名称
    //------------------------------------------------------------------

    output_measurement = "Distance_to_Nerve_um",

    //------------------------------------------------------------------
    // 像素尺寸转化
    //------------------------------------------------------------------

    // 如果值为null，则脚本自动从Qupath读取
    pixel_to_um = null,
    
    //------------------------------------------------------------------
    // 运行设置
    //------------------------------------------------------------------

    // 是否打印详细运行日志
    verbose = true,

    // 是否重写旧测量值
    overwrite_measurement = true,

    // 是否输出结果后删除原csv
    cleanup_temp_files = false,

    // 警告前的最大细胞批处理数量
    warning_cell_count = 5e+5

]

// ---------------------------------------------------------------------
// Derived Paths
// ---------------------------------------------------------------------

def PROJECT_DIR: new File(CONFIG.project_dir)
def DATA_DIR: new File(PROJECT_DIR, CONFIG.data_dir_relpath)
def EXE_FILE: new File(PROJECT_DIR, CONFIG.exe_relpath)

def CELL_CSV: new File(DATA_DIR, "cells_input.csv")
def BOUNDARY_CSV: new File(DATA_DIR, "boundary_input.csv")
def RESULT_CSV: new File(DATA_DIR, "result.csv")

// ---------------------------------------------------------------------
// 日志
// ---------------------------------------------------------------------

def logInfo = { msg -> 
    if (CONFIG.verbose) {
        println "[Qupath-CUDA-Spatial] ${msg}"
    }
}

def logWarn = { msg ->
    println "[QuPath-CUDA-Spatial][WARNING] ${msg}"
}

def logError = { msg ->
    println "[QuPath-CUDA-Spatial][ERROR] ${msg}"
}


// ---------------------------------------------------------------------
// 检查配置
// ---------------------------------------------------------------------

def validateConfig = {
    if (!PROJECT_DIR.exists()) {
        throw new RuntimeException("Project directory does not exist: ${PROJECT_DIR}")
    }

    if (!EXE_FILE.exists()) {
        throw new RuntimeException(
            "Executable not found: ${EXE_FILE}\n" +
            "Please build the Rust/CUDA executable first:\n" +
            "  cargo build --release"
        )
    }

    if (!DATA_DIR.exists()) {
        DATA_DIR.mkdirs()
        logInfo("Created data directory: ${DATA_DIR}")
    }

    if (CONFIG.cell_class == null || CONFIG.cell_class.trim().isEmpty()) {
        throw new RuntimeException("CONFIG.cell_class is empty.")
    }

    if (CONFIG.target_annotation_class == null || CONFIG.target_annotation_class.trim().isEmpty()) {
        throw new RuntimeException("CONFIG.target_annotation_class is empty.")
    }

    if (CONFIG.output_measurement == null || CONFIG.output_measurement.trim().isEmpty()) {
        throw new RuntimeException("CONFIG.output_measurement is empty.")
    }
}


// ---------------------------------------------------------------------
// 检查config
// ---------------------------------------------------------------------

validateConfig()


// ---------------------------------------------------------------------
// 1. 获取像素尺寸 (单位通常为 µm/pixel)
// ---------------------------------------------------------------------

def imageData = getQuPath().getImageData()
def cal = imageData.getServer().getPixelCalibration()

double pixelSize

if (CONFIG.pixel_to_um != null) {

    pixelSize = CONFIG.pixel_to_um
    logWarn("Using manually configured pixel size: ${pixelSize} um/pixel")

} else {

    def imageData = getCurrentImageData()
    def cal = imageData.getServer().getPixelCalibration()

    pixelSize = cal.getPixelWidthMicrons()

    if (pixelSize == 1.0 && cal.getPixelWidthUnit() == "px") {
        logWarn("Image is not calibrated. Distances remain in pixel units.")
    } else {
        logInfo("Detected pixel size: ${pixelSize} um/pixel")
    }
}


// ---------------------------------------------------------------------
// --- 2. 选择对象 ---
// ---------------------------------------------------------------------

PathObject selected = getSelectedObject()
if (selected == null) {
    print "错误: 请先选中一个 Annotation 父对象。"
    return
}

def children = selected.getChildObjects()
def classNerve = getPathClass(CONFIG.target_annotation_class)
def classCell = getPathClass(CONFIG.cell_class)

// ---------------------------------------------------------------------
// --- 3. 导出数据 ---
// ---------------------------------------------------------------------

def cells = []
new File(CELL_CSV).withWriter { writer ->
    writer.writeLine("x,y")
    children.each { child ->
        if (child.getPathClass() == classCell && child.getROI() != null) {
            double x = child.getROI().getCentroidX()
            double y = child.getROI().getCentroidY()
            writer.writeLine("${x},${y}")
            cells << child 
        }
    }
}

new File(BOUNDARY_CSV).withWriter { writer ->
    writer.writeLine("x,y")
    children.each { child ->
        if (child.getPathClass() == classNerve && child.getROI() != null) {
            def coords = child.getROI().getGeometry().getCoordinates()     
            coords.each { c ->
                writer.writeLine("${c.x},${c.y}")
            }
        }
    }
}

println "数据导出完成，共 ${cells.size()} 个细胞。"

// 检查最大细胞数量报警
if (cells.size() > CONFIG.warning_cell_count) {
    logWarn("Large Cell count detected: ${cells.size()}")
}

// ---------------------------------------------------------------------
// --- 4. 运行 GPU 工具 (修改点在此) ---
// ---------------------------------------------------------------------

println "正在调用 GPU 加速核心..."

// 使用列表形式传递参数，ProcessBuilder 会自动处理路径中的空格
def command = [
    EXE_FILE.getAbsolutePath(), 
    "--cells", CELL_CSV.getAbsolutePath(), 
    "--boundary", BOUNDARY_CSV.getAbsolutePath(), 
    "--output", RESULT_CSV.getAbsolutePath()
]

def pb = new ProcessBuilder(command)
pb.redirectErrorStream(true)
def process = pb.start()

// 实时打印 Rust 的输出到 QuPath 控制台，方便 Debug
process.inputStream.eachLine { println "GPU_LOG: " + it }
process.waitFor()

// 检查退出码（0 表示成功）
if (process.exitValue() != 0) {
    println "错误: Rust 程序执行失败，退出码: ${process.exitValue()}"
    return
}

// ---------------------------------------------------------------------
// --- 5. 读回结果并进行单位转换 ---
// ---------------------------------------------------------------------

def resultFile = RESULT_CSV
if (!resultFile.exists()) {
    print "错误: 未找到结果文件！"
    return
}

def lines = resultFile.readLines()
def distanceValues = lines.tail() // 去掉 header

if (distanceValues.size() != cells.size()) {
    print "错误: 结果数量(${distanceValues.size()})与细胞数量(${cells.size()})不匹配！"
    return
}

cells.eachWithIndex { cell, i ->
    double distPx = distanceValues[i].toDouble()
    double distUm = distPx * pixelSize
    
    cell.getMeasurementList().putMeasurement(
        CONFIG.output_measurement,
        distUm
    )
}

fireHierarchyUpdate()
println "完成！所有细胞已更新 'Distance_to_Nerve_um' 测量值。"

if (CONFIG.cleanup_temp_files) {

    CELL_CSV.delete()
    BOUNDARY_CSV.delete()
    RESULT_CSV.delete()

    logInfo("Temporary CSV files deleted.")
}