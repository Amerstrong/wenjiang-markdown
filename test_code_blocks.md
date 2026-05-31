# 文匠 Word 模板代码块排版对照测试文件

这个文件包含多个具有挑战性的代码块场景，专门用于测试和对比不同 Word 模板下的排版质量。

您可以分别使用：
1. **默认模板 (office_basic.docx)**
2. **精调代码模板 (WenJiangCode.docx)**
进行转换，并对比生成的 Word 文档在字体、缩进、底色、高亮等方面的表现。

---

## 1. Python 多层级缩进与中文注释测试

```python
def outer_function(x):
    # 这是一个包含多层级缩进和中文注释的 Python 代码块
    # 用于测试前导空格保留、行距以及中英文混排时的对齐
    def inner_function(y):
        if y > 0:
            for i in range(y):
                print(f"Loop {i}: x + y = {x + y}")
        else:
            print("y is negative or zero")
    return inner_function

# 执行函数
func = outer_function(10)
func(3)
```

---

## 2. JSON 嵌套与格式化测试

```json
{
  "project": "文匠 Wenjiang",
  "version": "1.61",
  "author": {
    "name": "沃境坊工作室",
    "role": "开发者",
    "contacts": {
      "email": "xiaoyu12657@qq.com",
      "website": "https://wojingfang.cn"
    }
  },
  "features": [
    "Markdown一键转Word",
    "等宽代码块高亮",
    "行内代码底色渲染",
    "本地完全离线"
  ],
  "active": true
}
```

---

## 3. HTML/XML 尖括号与字符转义测试

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>测试 HTML 代码转义</title>
</head>
<body>
  <!-- 容器标签，验证尖括号和属性是否原样保留而不被解析 -->
  <div class="container" id="main-content">
    <h1>测试尖括号转义: &lt;div&gt;</h1>
    <p>测试字符实体: &amp;nbsp; &amp;lt; &amp;gt; &amp;amp;</p>
  </div>
</body>
</html>
```

---

## 4. Java 类定义与大括号对齐测试

```java
package com.wenjiang.test;

/**
 * 这是一个 Java 类测试
 * 验证大括号对齐、关键字高亮和注释样式
 */
public class TestClass {
    private String name;

    public TestClass(String name) {
        this.name = name;
    }

    public void runLoop() {
        for (int i = 0; i < 5; i++) {
            System.out.println("序号: " + i + ", 姓名: " + this.name);
        }
    }
}
```

---

## 5. 行内代码混排测试

这里是普通的中文段落测试。在一句话中，我们穿插了多个行内代码片段，例如使用 Python 语言的 `print("hello")` 打印语句，或者使用 HTML 的 `<div>` 标签，以及命令行的 `cd templates` 指令。
*   **测试要点**：行内代码前后的文字字体、字号以及间距应当不受影响，行内代码本身应当呈现特殊的 Consolas 字体与浅灰色背景。

---

## 6. 连续代码块测试（验证块隔离）

```bash
echo "这是第一个 Bash 代码块，测试连续快输出的排版"
```

```bash
echo "这是第二个 Bash 代码块，验证它们不会粘在一起，而是有合理的段落间隔"
```

---

## 7. 超长单行代码测试（换行与溢出）

```javascript
// 测试超长行代码在 Word 中的自动换行与缩进保留（防溢出）
const veryLongLine = "这是一个超级长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长长的字符串";
```

---

*测试用例由文匠 (Wenjiang) 提供*
