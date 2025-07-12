正如你在 DevTools 里看到的，那条 fetchRoleMappings 请求其实并不是浏览器在用 Cookie 做认证，而是走的 AWS SigV4 签名：

Method 是 GET，并且把分页参数像 maxResults=10000&nextToken=… 放在 URL 里。

Authorization 头是一串 AWS4-HMAC-SHA256 Credential=… SignedHeaders=… Signature=…，也就是说前端是在用 AWS API Gateway（或 CloudFront + Lambda@Edge）配合 SigV4 来做认证，跟 SSO Cookie 是两套机制：

SSO Cookie 只保护了 UI 静态页面和前端 HTML/JS 能下载并运行

前端真正调用的 /api/... 接口，用的是基于浏览器当前 IAM 凭证（amz-sso-token）生成的 SigV4 签名

如何在 Python CLI 里复用这一套 SigV4 认证
方案 A：用 AWS SDK 调相应的 API
如果这条 API 背后实际上对应某个公开的 AWS 服务（如 IAM、STS、…），你可以直接用 boto3：

python
Copy
Edit
import boto3

# 根据你的 API 定义选择正确的 client
client = boto3.client("turtle-admin", region_name="us-west-2")
resp = client.fetch_role_mappings(MaxResults=10000)
items = resp["Items"]
如果它不是标准服务，也可能是公司内部在 API Gateway 后面挂了自定义 Lambda，那么就用…

方案 B：用 requests + SigV4 签名
安装授权库：

bash
Copy
Edit
pip install requests requests-aws4auth
在代码中签名并发 GET：

python
Copy
Edit
import os
import sys
import json
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth

# 1. 从环境或 AWS 配置文件里读你的 IAM 凭证
auth = AWSRequestsAuth(
    aws_access_key=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    aws_token=os.environ.get("AWS_SESSION_TOKEN", None),
    aws_host="corp.management-ui.turtle.aws.dev",
    aws_region="us-west-2",
    aws_service="execute-api",  # API Gateway 通常是这个 service
)

# 2. 发 GET 请求
url = (
  "https://corp.management-ui.turtle.aws.dev"
  "/api/fetchRoleMappings"
  "?maxResults=10000"
)
resp = requests.get(
  url,
  auth=auth,
  headers={
    "Accept": "application/json",
    # 如果前端还带 Origin/Referer，也一起带上
    "Origin":  "https://corp.management-ui.turtle.aws.dev",
    "Referer": "https://corp.management-ui.turtle.aws.dev/role-mappings-view",
  }
)
resp.raise_for_status()
data = resp.json()
print(json.dumps(data, indent=2))
这样你就跟浏览器里一模一样，用 SigV4 把请求签名过去，CloudFront/Lambda 就会校验通过，不会再 307 到 SSO。

为什么方案 1 之前不行
你把所有 cookie 都拼到 Cookie:，但是后端并不看这个 Cookie；

它只信任 SigV4 签名里的 IAM 凭证；

所以即便 Cookie 正确，缺少 Authorization: AWS4-HMAC-SHA256 ...，也会被当作「未认证」返 307 或 401。

下一步
决定用 SDK（boto3）还是 HTTP+SigV4（requests-aws4auth）。

在 CLI 中把这段签名逻辑接入到 fetch 函数里。

拿到 JSON 之后，把它交给你的表格／CSV／JSON 输出模块就大功告成了。

这样，方案 1（“直接调用前端 API”）就真的能跑通了。
