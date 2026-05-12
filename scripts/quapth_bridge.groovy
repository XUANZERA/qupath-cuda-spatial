import qupath.lib.objects.PathObject
import java.io.File

// --- 1. 环境配置 ---
def exePath = "D:/code/qupath_gpu_tool/target/release/qupath_gpu_tool.exe"
// 建议：如果你希望项目更灵活，可以根据当前图片所在文件夹动态生成 CSV 路径
def cellCsv = "D:/code/qupath_gpu_tool/data/cells_input.csv"
def boundaryCsv = "D:/code/qupath_gpu_tool/data/boundary_input.csv"
def resultCsv = "D:/code/qupath_gpu_tool/data/result.csv"

// 获取像素尺寸 (单位通常为 µm/pixel)
def imageData = getQuPath().getImageData()
def cal = imageData.getServer().getPixelCalibration()
double pixelSize = cal.getPixelWidthMicrons() 

if (pixelSize == 1.0 && cal.getUnit() == "pixel") {
    println "警告: 图像未校准（像素尺寸为 1.0）。结果将以像素为单位。"
} else {
    println "检测到像素尺寸: ${pixelSize} µm/pixel"
}

// --- 2. 选择对象 ---
PathObject selected = getSelectedObject()
if (selected == null) {
    print "错误: 请先选中一个 Annotation 父对象。"
    return
}

def children = selected.getChildObjects()
def classNerve = getPathClass("nerve_regions")
def classCell = getPathClass("immune_cell")

// --- 3. 导出数据 ---
def cells = []
new File(cellCsv).withWriter { writer ->
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

new File(boundaryCsv).withWriter { writer ->
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

// --- 4. 运行 GPU 工具 (修改点在此) ---
println "正在调用 GPU 加速核心..."

// 使用列表形式传递参数，ProcessBuilder 会自动处理路径中的空格
def command = [
    exePath, 
    "--cells", cellCsv, 
    "--boundary", boundaryCsv, 
    "--output", resultCsv
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

// --- 5. 读回结果并进行单位转换 ---
def resultFile = new File(resultCsv)
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
    
    cell.getMeasurementList().putMeasurement("Distance_to_Nerve_um", distUm)
}

fireHierarchyUpdate()
println "完成！所有细胞已更新 'Distance_to_Nerve_um' 测量值。"