# 一、介绍

webpack主要是打包（根据入口文件的依赖，加载所有模块js，然后合并成一个js;标准且纯粹的模块化打包工具 : 依赖一个文件为入口打包所有依赖为当前浏览器可用的代码），所以其核心存在两个部分，入口和出口，你可以把webpack加工想象成香肠加工厂，就是活猪进去，香肠出来的那种，但是如果每次加工都需要员工亲力亲为，那多麻烦那，所以我们考虑到了自动化配置。webpack存在功能类似的配置文件，让webpack通过配置，全自动的执行我们需要的编译操作。

webpack分成四个部分，期中最核心的就是入口和出口，当然在入口和出口配置的同时我们还需要一些加载器和插件，这就是我们所谓的webpack配置文件。这个配置文件我们习惯把其命名为webpack.config.js ，还有webpackfile.js ，

[优质知乎文章]: https://zhuanlan.zhihu.com/p/269434612
[官网]: https://www.webpackjs.com/



# 二、核心

- 入口：**入口起点(entry point)** 指示 webpack 应该使用哪个模块，来作为构建其内部 [依赖图(dependency graph)](https://webpack.docschina.org/concepts/dependency-graph/) 的开始。进入入口起点后，webpack 会找出有哪些模块和库是入口起点（直接和间接）依赖的。
- 输出：**output** 属性告诉 webpack 在哪里输出它所创建的 *bundle*，以及如何命名这些文件。
- loader：webpack 只能理解 JavaScript 和 JSON 文件，这是 webpack 开箱可用的自带能力。**loader** 让 webpack 能够去处理其他类型的文件，并将它们转换为有效 [模块](https://webpack.docschina.org/concepts/modules)，以供应用程序使用，以及被添加到依赖图中。
- 插件：loader 用于转换某些类型的模块，而插件则可以用于执行范围更广的任务。包括：打包优化，资源管理，注入环境变量。
- 模式：通过选择 `development`, `production` 或 `none` 之中的一个，来设置 `mode` 参数，你可以启用 webpack 内置在相应环境下的优化。其默认值为 `production`。



# 三、简单使用

1、创建项目

2、创建 modules 目录，用于放置 JS 模块等资源文件。

3、在 modules 下创建模块文件，如 hello.js ，用于编写 JS 模块相关代码。

```javascript
// 暴露一个方法
exports.sayHi = function () {
  document.write("<div>Hello WebPack</div>");  
};
```

4、在 modules 下创建一个名为 main.js 的入口文件，用于打包时设置 entry 属性。

```javascript
// require 导入一个模块，就可以调用这个模块的方法了
var hello = require("./hello");
hello.sayHi();
```

5、在项目目录下创建 webpack.config.js 配置文件，使用 webpack 命令打包。

```javascript
module.export = {
	entry: "./modules/main.js",
    output: {
        filename: "./js/bundle.js"
    }
}
```

6、在项目目录下创建 HTML 页面，如 index.html，导入 WebPack 打包后的 JS 文件

```html
<!doctype html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>test</title>
    </head>
    <body>
        <script src="dist/js/bundle.js"></script>
    </body>
</html>
```

7、使用管理员权限运行 webpack 指令

```python
# 参数 --watch 用于监听变化
webpack
```

