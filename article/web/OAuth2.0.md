#OAuth2.0

## 授权码模式（authorization code）
第三方登录模式

1. 请求授权
    API:    URI:https://api.fixedbug.com/oauth2/authorize
            method:GET
            params:
                grant_type:"authorization_code"//必选
                response_type:"code"//必选
                client_id:客户端 ID//必选
                redirect_uri:http://xxx.com/callback//必选
                scope:申请权限范围//可选
                state:客户端当前状态，原样返回//可选
2. 服务端响应跳转至redirect_uri
    API:    URI:http://xxx.com/callback
            method:GET
            params:
                code:
                state:
3. 请求 token
    API:    URI:https://api.fixedbug.com/oauth2/access_token
            method:POST
            params:
                client_id:客户端 ID//必选
                client_secret:客户端密钥//必选
                grant_type:"authorization_code"//必选
                code:上一步获得的 code//必选
                redirect_uri:http://xxx.com/callback//必选
4. 响应 token
    {
     "access_token": "access_token",//访问令牌
     "token_type":"bearer"//令牌类型，一般为bearer
     "expires_in": 3600,//过期时间，单位为秒
     "refresh_token":"refresh_token"//更新令牌
    }
## 简化模式（implicit）
浏览器中脚本语言
1. 请求 token
    API:    URI:https://api.fixedbug.com/oauth2/authorize
            method:GET
            params:
                response_type:token//该模式固定为token//必选
                client_id://必选
                redirect_uri:http://xxx.com/callback//http://xxx.com/callback
                scope:申请权限范围//可选
                state:客户端当前状态，原样返回//可选
2. 响应
    API:    URI:http://xxx.com/callback
            method:GET
            params:
                 access_token: "access_token",//Token 的值//必选
                 token_type:"bearer"或者"mac"//必选
                 expires_in: 3600,//过期时间//必选
                 scope:权限范围//可选
                 state:客户端当前状态//可选
    
## 密码模式（resource owner password credentials）
注册或者登录获取 token
1. 请求 token
    API:    URI:https://api.fixedbug.com/oauth2/authorize
            method:POST
            params:
                grant_type:password//该模式固定为password//必选
                username://必选
                password://必选
                scope:申请权限范围//可选
2. 响应 token
    {
     "access_token": "access_token",//Token 的值
     "token_type":"bearer"或者"mac"
     "expires_in": 3600,//过期时间
     "refresh_token":
    }
## 客户端模式（client credentials）
开放API，只验证客户端
1. 请求 token
    API:    URI:https://api.fixedbug.com/oauth2/authorize
            method:POST
            params:
                grant_type:client_credentials//该模式固定//必选
                scope:申请权限范围//可选
2. 响应 token
    {
     "access_token": "access_token",//Token 的值
     "token_type":"bearer"或者"mac"
     "expires_in": 3600,//过期时间
    }
## 更新令牌
使用refresh_token获取access_token
1. 请求 token
    API:    URI:https://api.fixedbug.com/oauth2/authorize
            header:Basic <refresh_token>//必选
            method:POST
            params:
                grant_type:refresh_token//该模式固定//必选
                scope:申请权限范围//可选
2. 响应 token
    {
     "access_token": "access_token",//Token 的值
     "token_type":"bearer"或者"mac"
     "expires_in": 3600,//过期时间
    }
## grant_type

授权类型：五个值

- authorization_code ：授权码模式(即先登录获取code,再获取token)
- password ：密码模式(将用户名,密码传过去,直接获取token)
- client_credentials ：客户端模式(无用户,用户向客户端注册,然后客户端以自己的名义向’服务端’获取资源)
- implicit ：简化模式(在redirect_uri 的Hash传递token; Auth客户端运行在浏览器中,如JS,Flash)
- refresh_token ：刷新access_token



