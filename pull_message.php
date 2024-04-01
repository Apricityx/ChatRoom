<?php
# 此API使用方式：GET请求，参数count，返回最新count条消息
$q = $_GET["count"];
$SQL_addr = "localhost:3306";
# 从本地passwd文件读取密码
$PASSWD_FILE = fopen("passwd", "r");
$SQL_passwd = fgets($PASSWD_FILE);
fclose($PASSWD_FILE);
# 连接到SQL
try {
    $conn = new mysqli($SQL_addr, "root", $SQL_passwd);
} catch (Exception $e) {
    echo "数据库连接失败，请检查数据库是否正常运行，或密码是否正确";
    return;
}
# 选择数据库
# 读取数据
$count = (int)$q;
try {
    $conn->select_db("chatchannel");
    # 从末尾查找
    $result = $conn->query("select * from storage order by id desc limit $count;");
    $output = [];
    while ($row = $result->fetch_assoc()) {
        array_push($output, $row);
    }
    echo json_encode($output);
} catch (Exception $e) {
    echo "数据库读取失败，请检查数据库是否正常运行";
    return;
}