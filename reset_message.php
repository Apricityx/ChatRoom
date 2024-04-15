<?php

# 此API使用方式：GET请求，参数count，返回最新count条消息
$q = $_GET["__reset__"];
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
# 删除所有数据
$conn->select_db("chatchannel");
$result = $conn->query("delete from storage;");
$conn->query("alter table storage auto_increment=1;");