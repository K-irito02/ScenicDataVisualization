在 GitHub 上获取个人访问令牌（Personal Access Token, PAT）用于访问私有仓库的步骤如下：

---

**1. 创建个人访问令牌（PAT）**
1. 登录 GitHub  
   访问 [GitHub 官网](https://github.com) 并登录你的账号。

2. 进入 Token 设置页面  
   • 点击右上角头像 → Settings（设置）。  

   • 左侧菜单栏 → Developer settings（开发者设置）。  

   • 选择 Personal access tokens（个人访问令牌） → Tokens (classic) 或 Fine-grained tokens（精细权限令牌）。  


   > 注：  
   > - Classic Token：传统令牌，权限范围较广（推荐大多数场景）。  
   > - Fine-grained Token：精细权限令牌（需指定仓库和权限，适合更严格的安全需求）。

3. 生成新令牌  
   • 点击 Generate new token → 选择 Classic 或 Fine-grained。  

   • 填写描述（如 `My Private Repo Access`），设置过期时间（建议选择有效期或自定义）。  


4. 配置权限（Scopes）  
   • Classic Token：勾选以下权限（根据需求调整）：  

     ◦ `repo`：访问所有私有仓库（包括读写）。  

     ◦ `read:packages`：如果需要访问私有包。  

     ◦ `admin:repo_hook`：管理仓库的 Webhook（可选）。  

   • Fine-grained Token：  

     ◦ 指定目标仓库（如你的私有仓库）。  

     ◦ 逐项配置权限（如 `Contents: Read-only` 或 `Read and Write`）。  


5. 生成令牌  
   • 点击 Generate token，生成的令牌会显示一次（务必立即保存，关闭页面后无法再次查看）。  


---

**2. 使用令牌访问私有仓库**
**方式 1：HTTPS 克隆（推荐）**
```bash
git clone https://github.com/用户名/私有仓库名.git
# 输入用户名时，密码栏填写生成的令牌（PAT）。
```

**方式 2：API 调用**
```bash
curl -H "Authorization: token YOUR_PAT" https://api.github.com/user/repos
```

**方式 3：Git 配置免密（可选）**
将令牌写入 Git 凭据存储，避免每次输入：
```bash
git config --global credential.helper store
# 首次克隆时会提示输入用户名和令牌，后续自动记住。
```

---

**3. 安全注意事项**
1. 令牌即密码：  
   • 不要泄露令牌，避免提交到代码或公开文件。  

   • 如果泄露，立即到 GitHub 的 Token 页面撤销（Revoke）。  


2. 最小权限原则：  
   • 仅勾选必要的权限（如私有仓库只需 `repo`）。  


3. 定期轮换：  
   • 设置较短的过期时间（如 30 天），到期后重新生成。  


---

**常见问题**
• Q：令牌和 SSH Key 有什么区别？  

  A：  
  • SSH Key 用于免密克隆（需配置公钥到 GitHub），适合本地开发。  

  • PAT 适用于 HTTPS 操作、API 调用或 CI/CD 工具（如 GitHub Actions）。  


• Q：令牌失效怎么办？  

  A：检查是否过期或被撤销，重新生成并更新使用的地方（如 CI/CD 配置）。

---

通过以上步骤，你可以安全地生成并使用 GitHub 个人访问令牌访问私有仓库！