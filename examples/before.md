# 示例技术文档 - 转换前 (Sample Technical Document - Before Conversion)

这是一个用于演示文匠 (Wenjiang) 转换效果的示例 Markdown 文档。其中包含行内代码、段落以及不同编程语言的代码块。

---

## 1. 简介与配置

在日常开发中，我们经常需要处理以下形式的配置信息。

### 1.1 YAML 配置示例
如下是一个简单的应用配置文件：

```yaml
server:
  port: 8080
  host: 0.0.0.0
database:
  driver: postgresql
  pool_size: 20
  timeout: 5s
```

在一般转换工具中，上面的缩进（如 `port: 8080`）极易丢失，导致配置文件无法阅读。

---

## 2. 核心代码实现

下面是一个简单的 Python 函数，它演示了行内代码如 `print()` 的用法，以及多行缩进的代码结构。

### 2.1 Python 函数
```python
def calculate_factorial(n):
    """
    计算非负整数的阶乘。
    阶乘计算使用递归方式实现。
    """
    if n < 0:
        raise ValueError("输入值必须为非负整数")
    if n == 0 or n == 1:
        return 1
    else:
        return n * calculate_factorial(n - 1)

# 测试计算
result = calculate_factorial(5)
print(f"5 的阶乘为: {result}")
```

### 2.2 JavaScript 代码块
```javascript
// 异步获取用户数据
async function fetchUserData(userId) {
  try {
    const response = await fetch(`https://api.wojingfang.cn/users/${userId}`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    console.log('User data loaded:', data);
    return data;
  } catch (error) {
    console.error('Failed to fetch user:', error);
  }
}
```

---

## 3. 行内代码排版测试

在正文中，我们会包含一些特殊的术语，例如通过命令 `pip install pypandoc` 来安装依赖，或者通过修改 `sys.path` 变量来添加自定义路径。文匠会将反引号包裹的 `code` 转换为带有玫红底色和 Consolas 字体的高亮样式。

---

## 4. 数据库查询示例 (SQL)

在技术方案中经常需要附带 SQL 语句，例如：

```sql
SELECT 
    user_id, 
    username, 
    email, 
    created_at 
FROM 
    users 
WHERE 
    status = 'active' 
    AND created_at >= '2026-01-01' 
ORDER BY 
    created_at DESC;
```
