#### 第一次使用git

1. git在本地创建一个ssh key
2. 把本地ssh key绑定到github账户中



#### 本地repository首次连接到github

1. 选择账户
2. git config --global user.name “Your Name”
3. git config --global user.email “your@gmail.com”

1. cd到当前文件夹
2. git init
3. git add file_name
4. git status
5. git commit -m “first commit”
6. git branch -M main
7. git remote add origin https://github.com/yexiaopingguo/xxxxxx.git
8. git push -u origin main



#### 后续上传

1. git status
2. git add file_name/ -A
3. git commit -m “first commit”
4. git push -u origin main



#### 通用指令

git add/rm file_name	# 添加/删除文件

git restore…



#### 远程仓库操作

git remote 

git remote -v    # 查看远端仓库地址

git clone

git pull

git push



#### 分支操作

git branch    # 查看分支

git branch <branch>    # 创建分支

git checkout <branch>	# 切换分支

git merge <branch>    # 合并分支（此时必须位于主支下）



#### 解决问题

强制覆盖本地仓库：git push -f    # Push出现错误讯息

遇到分支问题，例如主支和分支都修改了内容，可以手动处理，然后再 git add 特定修改文件