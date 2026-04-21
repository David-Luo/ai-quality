---
id: TC_001
title: 有效登录
module: auth
type: functional
priority: P0
status: draft
tags:
  - login
  - auth
---

## 前提条件

- 用户已注册
- 系统处于登录页面

## 测试步骤

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 打开登录页面 | 页面正常显示登录表单 |
| 2 | 输入用户名 test@example.com | 输入框显示内容 |
| 3 | 输入密码 password123 | 密码显示为掩码 |
| 4 | 点击登录按钮 | 跳转到 Dashboard 页面 |

## 输入数据

| 字段 | 值 |
|------|-----|
| 用户名 | test@example.com |
| 密码 | password123 |

## 备注

这是最基本的登录测试用例