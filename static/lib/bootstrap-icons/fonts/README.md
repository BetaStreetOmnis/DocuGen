# Bootstrap Icons 字体文件

## 📋 需要的字体文件

此目录需要以下Bootstrap Icons字体文件：

1. **bootstrap-icons.woff2** (推荐，现代浏览器支持)
2. **bootstrap-icons.woff** (备用，兼容性更好)

## 🔽 手动下载方法

### 方法1：直接下载
访问以下链接并保存到此目录：

- **WOFF2格式**: https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/fonts/bootstrap-icons.woff2
- **WOFF格式**: https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/fonts/bootstrap-icons.woff

### 方法2：使用命令行下载

#### Windows PowerShell
```powershell
# 下载 woff2 文件
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/fonts/bootstrap-icons.woff2" -OutFile "bootstrap-icons.woff2"

# 下载 woff 文件  
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/fonts/bootstrap-icons.woff" -OutFile "bootstrap-icons.woff"
```

#### Linux/macOS
```bash
# 下载 woff2 文件
curl -L "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/fonts/bootstrap-icons.woff2" -o "bootstrap-icons.woff2"

# 下载 woff 文件
curl -L "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/fonts/bootstrap-icons.woff" -o "bootstrap-icons.woff"
```

## 📁 文件大小参考

- `bootstrap-icons.woff2`: 约 160KB
- `bootstrap-icons.woff`: 约 240KB

## 🔧 验证安装

下载完成后，此目录应包含：
```
fonts/
├── README.md (此文件)
├── bootstrap-icons.woff2
└── bootstrap-icons.woff
```

## 💡 备用方案

如果无法下载字体文件，系统已配置了备用方案：
- 图标将显示为Emoji符号（📄🏠📝💬等）
- 虽然样式可能不同，但功能不受影响

## 🆘 故障排除

1. **404错误**: 确保文件名正确，无额外扩展名
2. **文件损坏**: 重新下载，确保文件大小正确
3. **权限问题**: 确保有写入此目录的权限

完成字体文件下载后，刷新页面即可看到正确的图标显示。 