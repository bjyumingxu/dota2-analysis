# 🔧 解决Git推送问题

## 问题现象
```
fatal: unable to access 'https://github.com/bjyumingxu/dota2-analysis.git/': Recv failure: Connection was reset
```

这是网络连接问题，常见原因：
1. 网络不稳定
2. GitHub访问受限（需要代理）
3. HTTPS连接问题

---

## ✅ 解决方案（按顺序尝试）

### 方案1：重试（最简单）

有时候只是临时网络问题，多试几次：

```bash
git push -u origin main
```

如果还是失败，继续尝试下面的方案。

---

### 方案2：使用SSH代替HTTPS（推荐）

SSH连接通常更稳定，不受HTTPS代理限制。

#### 2.1 检查是否已有SSH密钥

```bash
ls ~/.ssh
```

如果看到 `id_rsa` 和 `id_rsa.pub`（或 `id_ed25519` 和 `id_ed25519.pub`），说明已有SSH密钥，跳到步骤2.3。

#### 2.2 生成SSH密钥（如果没有）

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

按提示操作：
- 直接按回车使用默认路径
- 可以设置密码，也可以直接回车（不设置密码）

#### 2.3 复制公钥

**Windows PowerShell**：
```powershell
Get-Content ~/.ssh/id_ed25519.pub
```

**或者**：
```powershell
cat ~/.ssh/id_ed25519.pub
```

复制输出的内容（以 `ssh-ed25519` 开头的一长串）

#### 2.4 添加到GitHub

1. 访问：https://github.com/settings/keys
2. 点击 "New SSH key"
3. Title：随便填（例如：My Computer）
4. Key：粘贴刚才复制的公钥
5. 点击 "Add SSH key"

#### 2.5 修改远程仓库地址为SSH

```bash
# 查看当前远程地址
git remote -v

# 修改为SSH地址
git remote set-url origin git@github.com:bjyumingxu/dota2-analysis.git

# 验证修改
git remote -v
```

应该看到：
```
origin  git@github.com:bjyumingxu/dota2-analysis.git (fetch)
origin  git@github.com:bjyumingxu/dota2-analysis.git (push)
```

#### 2.6 测试SSH连接

```bash
ssh -T git@github.com
```

如果看到：
```
Hi bjyumingxu! You've successfully authenticated...
```
说明SSH配置成功！

#### 2.7 重新推送

```bash
git push -u origin main
```

---

### 方案3：配置Git代理（如果使用代理）

如果你使用代理访问GitHub，需要配置Git使用代理：

#### 3.1 设置HTTP代理

```bash
# 设置HTTP代理（替换为你的代理地址和端口）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

#### 3.2 如果使用SOCKS5代理

```bash
git config --global http.proxy socks5://127.0.0.1:7890
git config --global https.proxy socks5://127.0.0.1:7890
```

#### 3.3 重新推送

```bash
git push -u origin main
```

#### 3.4 如果不需要代理了，取消代理

```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

---

### 方案4：增加缓冲区大小

有时候是因为文件太大或网络慢，可以增加缓冲区：

```bash
git config --global http.postBuffer 524288000
git push -u origin main
```

---

### 方案5：使用GitHub Desktop（图形界面）

如果命令行一直有问题，可以使用GitHub Desktop：

1. 下载：https://desktop.github.com
2. 登录GitHub账号
3. 添加仓库
4. 点击推送按钮

---

## 🔍 诊断步骤

### 检查网络连接

```bash
# 测试GitHub连接
ping github.com

# 测试HTTPS连接
curl -I https://github.com
```

### 检查Git配置

```bash
# 查看当前配置
git config --list

# 查看远程仓库地址
git remote -v
```

---

## 💡 推荐方案

**最推荐使用方案2（SSH）**，因为：
- ✅ 更稳定
- ✅ 不需要每次输入密码
- ✅ 不受HTTPS代理限制
- ✅ 更安全

---

## 📝 如果还是不行

请告诉我：
1. 你使用的是什么网络？（家庭网络/公司网络/移动热点）
2. 是否需要代理访问GitHub？
3. 错误信息是什么？（完整的错误信息）

我会根据具体情况提供更针对性的解决方案。

