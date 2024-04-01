<?php
# 此API使用方式：POST请求，来向数据库中写入数据，参数nickname，message，返回写入的数据
$q = file_get_contents("php://input");
# 验证格式是否正确，必须包含nickname，message
if (strpos($q, "nickname") === false || strpos($q, "message") === false) {
    echo "错误，检查你的数据格式";
    return;
}
$nickname = json_decode($q, true)["nickname"];
$message = json_decode($q, true)["message"];
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
# 插入数据
try {
    echo '尝试写入：insert into storage(nickname,message) values(' . $nickname . ',' . $message . ')';
    $conn->select_db("chatchannel");
    $conn->query("insert into storage(nickname,message) values('$nickname' , '$message');");
} catch (Exception $e) {
    echo "数据库写入失败，请检查数据库是否正常运行";
    echo $e;
    return;
}

echo $q;
?>