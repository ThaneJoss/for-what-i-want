# For What I Want

## Introduction

**For What I Want** 是一个广义上的 Docker Container Registry Accelerator，用于解决无法连接 [**docker.io**](https://docker.io) 的问题。

  <p align="center">
    <img src="./logo.png">
  </p>

## Features

### 一切从简

- 不再需要任何边缘函数的代理和转发

### 用法从简

- 不再需要任何包管理器
  **For What I Want** 在大多数情况下能够解决以下问题：

1. 被 DNS 解析为 0.0.0.0:

   - This site can't be reached.

2. TCP 协议握手第二段被丢弃：

   - The connection has timed out.

3. DNS 服务器返回解析被替换为空：

   - DNS address could not be found.

4. 收到伪造的 TLS 证书：

   - Your connection is not private.

5. 收到伪造的拒绝服务请求

   - Connection reset by peer.

6. 被 DNS 解析为 127.0.0.1
   - The server refused to connect.

---

**For What I Want** 无法解决以下问题

- There is no internet connection.
- The proxy server isn't responding.
- A firewall or antivirus is blocking the connection.
- The server sent an invalid response.
