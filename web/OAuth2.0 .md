#OAuth2.0

1. 请求授权
    response_type:code
    client_id:
    state:
    scope:
    redirect_uri:
2. 同意授权
    code:
    state:
3. 请求令牌
    grant_type:
    client_id:
    client_secret:
    code:
    redirect_uri:
4. 响应令牌
    access_token:
    token_type:"Bearer"
    expires_in:3600
5. 使用令牌
    Authorization:OAuth "access_token"
    
    
## 授权
1. 请求授权
    GET https://api.weibo.com/oauth2/authorize?client_id=123050457758183&redirect_uri=http://jianshu.com/callback
    client_id:
    redirect_uri：http://jianshu.com/callback
2. 响应跳转redirect_uri
    GET http://jianshu.com/callback?code=2559200ecd7ea433f067a2cf67d6ce6c
    code:
3. 请求access_token
    POST https://api.weibo.com/oauth2/access_token
    client_id：在微博开放平台申请的应用 ID
    client_secret：在微博开放平台申请时提供的APP Secret
    grant_type：需要填写authorization_code
    code：上一步获得的 code
    redirect_uri：回调地址，需要与注册应用里的回调地址以及第一步的redirect_uri 参数一致
4. 响应数据
    {
     "access_token": "ACCESS_TOKEN",//Token 的值
     "expires_in": 1234,//过期时间
     "uid":"12341234"//当前授权用户的UID。
    }
5. 获取用户资源
    GET https://api.weibo.com/2/users/show.json
    access_token：上一步获取的access_token
    uid：用户的账号 id，上一步的接口有返回

## App端
1. 注册
    grant_type:
    username:
    password:
    scope:
2. 响应
    { 
        "access_token"  : "...",
        "token_type"    : "...",
        "expires_in"    : "...",
        "refresh_token" : "...",
    }
access_type属性是授权服务器分配的访问令牌。
token_type是被授权服务器分配的令牌类型。
expires_in属性是指访问令牌过多少秒后，就不再有效。访问令牌过期值是可选的。
refresh_token属性包含令牌过期后刷新的令牌。刷新的令牌用于，一旦响应返回的不再有效时，包含一个新的访问令牌。

